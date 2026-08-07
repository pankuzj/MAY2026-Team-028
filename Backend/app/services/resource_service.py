"""Resource service for worker/vehicle/equipment status updates."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.equipment import Equipment, EquipmentStatus
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.worker import Worker, WorkerStatus
from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.worker_repository import WorkerRepository

__all__ = ["ResourceService"]


class ResourceService:
    @staticmethod
    def get_worker(db: Session, worker_id: int) -> Worker:
        worker = WorkerRepository.get_by_id(db, worker_id)
        if not worker:
            raise NotFoundError("Worker not found.")
        return worker

    @staticmethod
    def check_worker_available(db: Session, worker_id: int) -> Worker:
        worker = ResourceService.get_worker(db, worker_id)
        if not worker.is_active or worker.status != WorkerStatus.AVAILABLE.value:
            raise ConflictError(f"Worker {worker_id} is not available.")
        return worker

    @staticmethod
    def get_vehicle(db: Session, vehicle_id: int) -> Vehicle:
        vehicle = VehicleRepository.get_by_id(db, vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found.")
        return vehicle

    @staticmethod
    def check_vehicle_available(db: Session, vehicle_id: int) -> Vehicle:
        vehicle = ResourceService.get_vehicle(db, vehicle_id)
        if not vehicle.is_active or vehicle.status != VehicleStatus.AVAILABLE.value:
            raise ConflictError(f"Vehicle {vehicle_id} is not available.")
        return vehicle

    @staticmethod
    def get_equipment(db: Session, equipment_id: int) -> Equipment:
        equipment = EquipmentRepository.get_by_id(db, equipment_id)
        if not equipment:
            raise NotFoundError("Equipment not found.")
        return equipment

    @staticmethod
    def check_equipment_available(db: Session, equipment_id: int) -> Equipment:
        equipment = ResourceService.get_equipment(db, equipment_id)
        if not equipment.is_active or equipment.status != EquipmentStatus.AVAILABLE.value:
            raise ConflictError(f"Equipment {equipment_id} is not available.")
        return equipment

    @staticmethod
    def update_worker_status(
        db: Session, worker_id: int, *, status: str | None = None, **updates
    ) -> Worker:
        worker = ResourceService.get_worker(db, worker_id)
        payload = dict(updates)
        if status is not None:
            payload["status"] = status
        return WorkerRepository.update(db, worker, payload)

    @staticmethod
    def update_vehicle_status(
        db: Session, vehicle_id: int, *, status: str | None = None, **updates
    ) -> Vehicle:
        vehicle = ResourceService.get_vehicle(db, vehicle_id)
        payload = dict(updates)
        if status is not None:
            payload["status"] = status
        return VehicleRepository.update(db, vehicle, payload)

    @staticmethod
    def update_equipment_status(
        db: Session, equipment_id: int, *, status: str | None = None, **updates
    ) -> Equipment:
        equipment = ResourceService.get_equipment(db, equipment_id)
        payload = dict(updates)
        if status is not None:
            payload["status"] = status
        return EquipmentRepository.update(db, equipment, payload)
