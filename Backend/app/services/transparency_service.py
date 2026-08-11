"""Transparency feed service (S2-F03, US-25).

Posts are published manually by crew/admin for a resolved complaint (RBAC is
enforced at the route layer via ``require_role``); auto-generating a post when
a complaint closes is separate follow-up work (S2-A04), not implemented here.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, InvalidStateTransitionError, NotFoundError
from app.models.complaint import ComplaintStatus
from app.models.transparency import PostComment, TransparencyPost
from app.models.user import User
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.transparency_repository import PostCommentRepository, TransparencyRepository
from app.schemas.transparency import PostCommentCreate, TransparencyPostCreate

__all__ = ["TransparencyService"]


class TransparencyService:
    @staticmethod
    def create_post(
        db: Session, current_user: User, post_in: TransparencyPostCreate
    ) -> TransparencyPost:
        complaint = ComplaintRepository.get_by_id(db, post_in.complaint_id)
        if not complaint:
            raise NotFoundError("Complaint not found.")
        if complaint.status != ComplaintStatus.RESOLVED.value:
            raise InvalidStateTransitionError(
                "A transparency post can only be published for a resolved complaint."
            )
        if TransparencyRepository.get_by_complaint_id(db, complaint.id):
            raise ConflictError("A transparency post already exists for this complaint.")

        post = TransparencyPost(
            complaint_id=complaint.id,
            ward_id=complaint.ward_id,
            title=post_in.title,
            description=post_in.description,
            before_photo_url=post_in.before_photo_url,
            after_photo_url=post_in.after_photo_url,
            posted_by_user_id=current_user.id,
        )
        return TransparencyRepository.create(db, post)

    @staticmethod
    def get_post(db: Session, post_id: int) -> TransparencyPost:
        post = TransparencyRepository.get_by_id(db, post_id)
        if not post:
            raise NotFoundError("Transparency post not found.")
        return post

    @staticmethod
    def list_posts(
        db: Session, *, ward_id: int | None = None, page: int = 1, page_size: int = 20
    ) -> tuple[list[TransparencyPost], int]:
        return TransparencyRepository.list(
            db, filters={"ward_id": ward_id}, page=page, page_size=page_size
        )

    @staticmethod
    def applaud(db: Session, post_id: int) -> TransparencyPost:
        post = TransparencyService.get_post(db, post_id)
        return TransparencyRepository.increment_applause(db, post)

    @staticmethod
    def add_comment(
        db: Session, post_id: int, current_user: User, comment_in: PostCommentCreate
    ) -> PostComment:
        TransparencyService.get_post(db, post_id)
        comment = PostComment(post_id=post_id, user_id=current_user.id, comment=comment_in.comment)
        return PostCommentRepository.create(db, comment)

    @staticmethod
    def list_comments(db: Session, post_id: int) -> list[PostComment]:
        TransparencyService.get_post(db, post_id)
        return PostCommentRepository.list_by_post(db, post_id)
