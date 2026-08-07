"""Task service for assignment orchestration."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidStateTransitionError, NotFoundError
from app.models.equipment import EquipmentStatus
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.models.vehicle import VehicleStatus
from app.models.worker import WorkerStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.complaint_service import ComplaintService
from app.services.resource_service import ResourceService

__all__ = ["TaskService"]


class TaskService:
    _ALLOWED_STATUS_TRANSITIONS = {
        TaskStatus.ASSIGNED.value: {TaskStatus.IN_PROGRESS.value, TaskStatus.CANCELLED.value},
        TaskStatus.IN_PROGRESS.value: {TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value},
        TaskStatus.COMPLETED.value: set(),
        TaskStatus.CANCELLED.value: set(),
    }

    @staticmethod
    def create_task(db: Session, current_user: User, task_in: TaskCreate) -> Task:
        if task_in.vehicle_id:
            ResourceService.check_vehicle_available(db, task_in.vehicle_id)
        if task_in.worker_ids:
            for w_id in task_in.worker_ids:
                ResourceService.check_worker_available(db, w_id)
        if task_in.equipment_ids:
            for e_id in task_in.equipment_ids:
                ResourceService.check_equipment_available(db, e_id)

        task = Task(
            title=task_in.title,
            description=task_in.description,
            complaint_id=task_in.complaint_id,
            ward_id=task_in.ward_id,
            vehicle_id=task_in.vehicle_id,
            status=(
                task_in.status.value if hasattr(task_in.status, "value") else str(task_in.status)
            ),
            assigned_by_user_id=task_in.assigned_by_user_id or current_user.id,
            assigned_at=datetime.now(UTC),
        )
        created = TaskRepository.create(db, task)

        if task_in.worker_ids:
            TaskRepository.set_worker_ids(db, created.id, task_in.worker_ids)
            for w_id in task_in.worker_ids:
                ResourceService.update_worker_status(db, w_id, status=WorkerStatus.ASSIGNED.value)
        if task_in.equipment_ids:
            TaskRepository.set_equipment_ids(db, created.id, task_in.equipment_ids)
            for e_id in task_in.equipment_ids:
                ResourceService.update_equipment_status(
                    db, e_id, status=EquipmentStatus.IN_USE.value
                )
        if task_in.vehicle_id:
            ResourceService.update_vehicle_status(
                db, task_in.vehicle_id, status=VehicleStatus.EN_ROUTE.value
            )

        if created.complaint_id:
            ComplaintService.change_status(
                db, created.complaint_id, "in_progress", changed_by_user_id=current_user.id
            )
        return created

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task:
        task = TaskRepository.get_by_id(db, task_id)
        if not task:
            raise NotFoundError("Task not found.")
        return task

    @staticmethod
    def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Task:
        task = TaskService.get_task(db, task_id)
        update_data = task_in.model_dump(exclude_unset=True)
        worker_ids = update_data.pop("worker_ids", None)
        equipment_ids = update_data.pop("equipment_ids", None)
        vehicle_id = update_data.get("vehicle_id")

        if vehicle_id is not None and vehicle_id != task.vehicle_id:
            ResourceService.check_vehicle_available(db, vehicle_id)

        if worker_ids is not None:
            old_w_ids = set(TaskRepository.get_worker_ids(db, task_id))
            new_w_ids = set(worker_ids)
            added_w_ids = new_w_ids - old_w_ids
            for w_id in added_w_ids:
                ResourceService.check_worker_available(db, w_id)

        if equipment_ids is not None:
            old_e_ids = set(TaskRepository.get_equipment_ids(db, task_id))
            new_e_ids = set(equipment_ids)
            added_e_ids = new_e_ids - old_e_ids
            for e_id in added_e_ids:
                ResourceService.check_equipment_available(db, e_id)

        status = update_data.get("status")
        if status is not None:
            update_data["status"] = status.value if hasattr(status, "value") else str(status)

        updated = TaskRepository.update(db, task, update_data)

        if vehicle_id is not None and vehicle_id != task.vehicle_id:
            if task.vehicle_id:
                ResourceService.update_vehicle_status(
                    db, task.vehicle_id, status=VehicleStatus.AVAILABLE.value
                )
            ResourceService.update_vehicle_status(
                db, vehicle_id, status=VehicleStatus.EN_ROUTE.value
            )

        if worker_ids is not None:
            old_w_ids = set(TaskRepository.get_worker_ids(db, task_id))
            new_w_ids = set(worker_ids)
            removed_w_ids = old_w_ids - new_w_ids
            added_w_ids = new_w_ids - old_w_ids
            TaskRepository.set_worker_ids(db, updated.id, worker_ids)
            for w_id in removed_w_ids:
                ResourceService.update_worker_status(
                    db, w_id, status=WorkerStatus.AVAILABLE.value
                )
            for w_id in added_w_ids:
                ResourceService.update_worker_status(
                    db, w_id, status=WorkerStatus.ASSIGNED.value
                )

        if equipment_ids is not None:
            old_e_ids = set(TaskRepository.get_equipment_ids(db, task_id))
            new_e_ids = set(equipment_ids)
            removed_e_ids = old_e_ids - new_e_ids
            added_e_ids = new_e_ids - old_e_ids
            TaskRepository.set_equipment_ids(db, updated.id, equipment_ids)
            for e_id in removed_e_ids:
                ResourceService.update_equipment_status(
                    db, e_id, status=EquipmentStatus.AVAILABLE.value
                )
            for e_id in added_e_ids:
                ResourceService.update_equipment_status(
                    db, e_id, status=EquipmentStatus.IN_USE.value
                )

        return updated

    @staticmethod
    def complete_task(
        db: Session, task_id: int, *, completed_by_user_id: int | None = None
    ) -> Task:
        task = TaskService.get_task(db, task_id)
        if task.status in {TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value}:
            return task
        updated = TaskRepository.update(
            db,
            task,
            {"status": TaskStatus.COMPLETED.value, "completed_at": datetime.now(UTC)},
        )
        if updated.vehicle_id:
            ResourceService.update_vehicle_status(
                db, updated.vehicle_id, status=VehicleStatus.AVAILABLE.value
            )
        worker_ids = TaskRepository.get_worker_ids(db, updated.id)
        for w_id in worker_ids:
            ResourceService.update_worker_status(db, w_id, status=WorkerStatus.AVAILABLE.value)
        equipment_ids = TaskRepository.get_equipment_ids(db, updated.id)
        for e_id in equipment_ids:
            ResourceService.update_equipment_status(
                db, e_id, status=EquipmentStatus.AVAILABLE.value
            )

        if updated.complaint_id:
            ComplaintService.change_status(
                db, updated.complaint_id, "resolved", changed_by_user_id=completed_by_user_id
            )
        return updated

    @staticmethod
    def update_status(db: Session, task_id: int, status: TaskStatus, *, user_id: int) -> Task:
        """Advance a task through its lifecycle without bypassing state rules."""
        task = TaskService.get_task(db, task_id)
        target = status.value
        if target == task.status:
            return task
        if target not in TaskService._ALLOWED_STATUS_TRANSITIONS.get(task.status, set()):
            raise InvalidStateTransitionError(
                f"Cannot move task from '{task.status}' to '{target}'."
            )
        if target == TaskStatus.COMPLETED.value:
            return TaskService.complete_task(db, task_id, completed_by_user_id=user_id)
        updates = {"status": target}
        if target == TaskStatus.IN_PROGRESS.value:
            updates["started_at"] = datetime.now(UTC)
        return TaskRepository.update(db, task, updates)

    @staticmethod
    def request_assistance(db: Session, task_id: int, notes: str) -> Task:
        """Persist the latest assistance request for an assignment."""
        task = TaskService.get_task(db, task_id)
        if task.status in {TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value}:
            raise InvalidStateTransitionError("Closed tasks cannot request assistance.")
        return TaskRepository.update(
            db,
            task,
            {"assistance_requested": True, "assistance_notes": notes},
        )

    @staticmethod
    def cancel_task(db: Session, task_id: int) -> Task:
        task = TaskService.get_task(db, task_id)
        if task.vehicle_id:
            ResourceService.update_vehicle_status(
                db, task.vehicle_id, status=VehicleStatus.AVAILABLE.value
            )
        worker_ids = TaskRepository.get_worker_ids(db, task.id)
        for w_id in worker_ids:
            ResourceService.update_worker_status(db, w_id, status=WorkerStatus.AVAILABLE.value)
        equipment_ids = TaskRepository.get_equipment_ids(db, task.id)
        for e_id in equipment_ids:
            ResourceService.update_equipment_status(
                db, e_id, status=EquipmentStatus.AVAILABLE.value
            )

        return TaskRepository.update(db, task, {"status": TaskStatus.CANCELLED.value})
