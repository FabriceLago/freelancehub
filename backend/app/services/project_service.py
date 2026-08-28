import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.project import Project, ProjectStatus, Task
from app.repositories import client_repository, project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


class ProjectNotFoundError(AppError):
    pass


class TaskNotFoundError(AppError):
    pass


class ClientNotInOrganizationError(AppError):
    pass


def list_projects(db: Session, organization_id: uuid.UUID, status: ProjectStatus | None) -> list[Project]:
    return project_repository.list_for_organization(db, organization_id, status)


def get_project(db: Session, organization_id: uuid.UUID, project_id: uuid.UUID) -> Project:
    project = project_repository.get_for_organization(db, organization_id, project_id)
    if project is None:
        raise ProjectNotFoundError()
    return project


def create_project(db: Session, organization_id: uuid.UUID, data: ProjectCreate) -> Project:
    # Sans cette vérification, rien n'empêcherait (bug ou requête forgée) de
    # créer un projet pointant vers le client_id d'une AUTRE organisation —
    # le schéma Pydantic ne valide qu'un UUID, pas son appartenance tenant.
    if client_repository.get_for_organization(db, organization_id, data.client_id) is None:
        raise ClientNotInOrganizationError()

    project = Project(organization_id=organization_id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, organization_id: uuid.UUID, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
    project = get_project(db, organization_id, project_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, organization_id: uuid.UUID, project_id: uuid.UUID) -> None:
    project = get_project(db, organization_id, project_id)
    db.delete(project)
    db.commit()


def create_task(db: Session, organization_id: uuid.UUID, project_id: uuid.UUID, data: TaskCreate) -> Task:
    get_project(db, organization_id, project_id)  # 404 si le projet n'appartient pas à l'organisation
    task = Task(project_id=project_id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, organization_id: uuid.UUID, task_id: uuid.UUID, data: TaskUpdate) -> Task:
    task = project_repository.get_task_for_organization(db, organization_id, task_id)
    if task is None:
        raise TaskNotFoundError()
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, organization_id: uuid.UUID, task_id: uuid.UUID) -> None:
    task = project_repository.get_task_for_organization(db, organization_id, task_id)
    if task is None:
        raise TaskNotFoundError()
    db.delete(task)
    db.commit()


def list_incomplete_tasks(db: Session, organization_id: uuid.UUID, limit: int = 10) -> list[Task]:
    return project_repository.list_incomplete_tasks_for_organization(db, organization_id, limit)
