"""Task service for assignment orchestration."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.complaint_service import ComplaintService

__all__ = ["TaskService"]


class TaskService:
    @staticmethod
    def create_task(db: Session, current_user: User, task_in: TaskCreate) -> Task:
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
        if task_in.equipment_ids:
            TaskRepository.set_equipment_ids(db, created.id, task_in.equipment_ids)
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
        status = update_data.get("status")
        if status is not None:
            update_data["status"] = status.value if hasattr(status, "value") else str(status)
        updated = TaskRepository.update(db, task, update_data)
        if worker_ids is not None:
            TaskRepository.set_worker_ids(db, updated.id, worker_ids)
        if equipment_ids is not None:
            TaskRepository.set_equipment_ids(db, updated.id, equipment_ids)
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
        if updated.complaint_id:
            ComplaintService.change_status(
                db, updated.complaint_id, "resolved", changed_by_user_id=completed_by_user_id
            )
        return updated

    @staticmethod
    def cancel_task(db: Session, task_id: int) -> Task:
        task = TaskService.get_task(db, task_id)
        return TaskRepository.update(db, task, {"status": TaskStatus.CANCELLED.value})
