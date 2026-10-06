from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.category import Category
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.auth import AdminProfile
from app.services.cloudinary_service import upload_project_image

router = APIRouter(prefix="/projects", tags=["Projects"])


def format_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        image_url=project.image_url,
        github_url=project.github_url,
        category_id=project.category_id,
        category_name=project.category.name if project.category else None,
        category_slug=project.category.slug if project.category else None,
        tech_stack=project.tech_stack or [],
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=List[ProjectResponse])
def get_projects(
    category_id: Optional[int] = None,
    category_slug: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Public: Retrieve all portfolio projects, with optional category filtering."""
    query = db.query(Project).join(Category)

    if category_id:
        query = query.filter(Project.category_id == category_id)
    elif category_slug and category_slug != "all":
        query = query.filter(Category.slug == category_slug)

    projects = query.order_by(Project.created_at.desc()).all()
    return [format_project_response(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Public: Fetch detailed information for a single project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return format_project_response(project)


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Upload a project image to Cloudinary and retrieve its secure URL."""
    contents = await file.read()
    secure_url = upload_project_image(
        file_bytes=contents,
        filename=file.filename or "upload.jpg",
        content_type=file.content_type or "image/jpeg",
    )
    return {"url": secure_url}


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Create a new project and assign it to a category."""
    category = db.query(Category).filter(Category.id == project_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with ID {project_in.category_id} does not exist.",
        )

    project = Project(
        title=project_in.title,
        description=project_in.description,
        image_url=project_in.image_url,
        github_url=project_in.github_url,
        category_id=project_in.category_id,
        tech_stack=project_in.tech_stack,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return format_project_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Update an existing project's metadata or image."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if project_in.category_id is not None:
        category = db.query(Category).filter(Category.id == project_in.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {project_in.category_id} does not exist.",
            )
        project.category_id = project_in.category_id

    if project_in.title is not None:
        project.title = project_in.title
    if project_in.description is not None:
        project.description = project_in.description
    if project_in.image_url is not None:
        project.image_url = project_in.image_url
    if project_in.github_url is not None:
        project.github_url = project_in.github_url
    if project_in.tech_stack is not None:
        project.tech_stack = project_in.tech_stack

    db.commit()
    db.refresh(project)
    return format_project_response(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Permanently delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    db.delete(project)
    db.commit()
    return None
