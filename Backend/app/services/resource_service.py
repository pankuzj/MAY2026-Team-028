"""Resource service for worker/vehicle/equipment status updates."""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.equipment import Equipment
from app.models.vehicle import Vehicle
from app.models.worker import Worker
from app.repositories.equipment_repository import EquipmentRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.worker_repository import WorkerRepository

__all__ = ["ResourceService"]


class ResourceService:
    @staticmethod
    def update_worker_status(
        db: Session, worker_id: int, *, status: str | None = None, **updates
    ) -> Worker:
        worker = WorkerRepository.get_by_id(db, worker_id)
        if not worker:
            raise NotFoundError("Worker not found.")
        payload = dict(updates)
        if status is not None:
            payload["status"] = status
        return WorkerRepository.update(db, worker, payload)

    @staticmethod
    def update_vehicle_status(
        db: Session, vehicle_id: int, *, status: str | None = None, **updates
    ) -> Vehicle:
        vehicle = VehicleRepository.get_by_id(db, vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found.")
        payload = dict(updates)
        if status is not None:
            payload["status"] = status
        return VehicleRepository.update(db, vehicle, payload)

    @staticmethod
    def update_equipment_status(
        db: Session, equipment_id: int, *, status: str | None = None, **updates
    ) -> Equipment:
        equipment = EquipmentRepository.get_by_id(db, equipment_id)
        if not equipment:
            raise NotFoundError("Equipment not found.")
        payload = dict(updates)
        if status is not None:
            payload["status"] = status
        return EquipmentRepository.update(db, equipment, payload)
