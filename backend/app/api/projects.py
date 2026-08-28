import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, require_role
from app.core.database import get_db
from app.models.organization import Membership, Role
from app.models.project import ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailOut,
    ProjectOut,
    ProjectUpdate,
    TaskCreate,
    TaskOut,
    TaskUpdate,
    TaskWithProjectOut,
)
from app.services import project_service
from app.services.project_service import ClientNotInOrganizationError, ProjectNotFoundError, TaskNotFoundError

router = APIRouter(tags=["projects"])


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    status_filter: ProjectStatus | None = None,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return project_service.list_projects(db, membership.organization_id, status_filter)


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return project_service.create_project(db, membership.organization_id, payload)
    except ClientNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client introuvable")


@router.get("/projects/{project_id}", response_model=ProjectDetailOut)
def get_project(
    project_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return project_service.get_project(db, membership.organization_id, project_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return project_service.update_project(db, membership.organization_id, project_id, payload)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    membership: Membership = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    try:
        project_service.delete_project(db, membership.organization_id, project_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    return None


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: uuid.UUID,
    payload: TaskCreate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return project_service.create_task(db, membership.organization_id, project_id, payload)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return project_service.update_task(db, membership.organization_id, task_id, payload)
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche introuvable")


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        project_service.delete_task(db, membership.organization_id, task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche introuvable")
    return None


@router.get("/tasks", response_model=list[TaskWithProjectOut])
def list_incomplete_tasks(
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    # Construit à la main plutôt que via from_attributes : project_name vient
    # de la relation Task.project, pas d'une colonne directe sur Task.
    tasks = project_service.list_incomplete_tasks(db, membership.organization_id)
    return [
        TaskWithProjectOut(
            id=t.id,
            title=t.title,
            is_done=t.is_done,
            due_date=t.due_date,
            created_at=t.created_at,
            project_id=t.project_id,
            project_name=t.project.name,
        )
        for t in tasks
    ]
