import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.project import Project, ProjectStatus, Task


def list_for_organization(
    db: Session, organization_id: uuid.UUID, status: ProjectStatus | None = None
) -> list[Project]:
    stmt = select(Project).where(Project.organization_id == organization_id)
    if status is not None:
        stmt = stmt.where(Project.status == status)
    stmt = stmt.order_by(Project.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_for_organization(db: Session, organization_id: uuid.UUID, project_id: uuid.UUID) -> Project | None:
    return db.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.id == project_id, Project.organization_id == organization_id)
    ).scalar_one_or_none()


def get_task_for_organization(db: Session, organization_id: uuid.UUID, task_id: uuid.UUID) -> Task | None:
    # Un Task n'a pas organization_id en propre : on passe par son Project
    # pour vérifier qu'il appartient bien à l'organisation courante — même
    # principe d'isolation tenant que partout ailleurs, juste via une jointure.
    return db.execute(
        select(Task).join(Project).where(Task.id == task_id, Project.organization_id == organization_id)
    ).scalar_one_or_none()


def list_incomplete_tasks_for_organization(db: Session, organization_id: uuid.UUID, limit: int = 10) -> list[Task]:
    stmt = (
        select(Task)
        .join(Project)
        .options(joinedload(Task.project))
        .where(Project.organization_id == organization_id, Task.is_done.is_(False))
        .order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
