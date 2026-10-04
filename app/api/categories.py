from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.category import Category
from app.models.project import Project
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, generate_slug
from app.schemas.auth import AdminProfile

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Public: Fetch all categories with total project counts."""
    categories = db.query(Category).order_by(Category.name.asc()).all()

    # Calculate project counts per category
    counts_query = (
        db.query(Project.category_id, func.count(Project.id))
        .group_by(Project.category_id)
        .all()
    )
    counts_map = dict(counts_query)

    result = []
    for cat in categories:
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "created_at": cat.created_at,
            "updated_at": cat.updated_at,
            "projects_count": counts_map.get(cat.id, 0),
        }
        result.append(CategoryResponse(**cat_dict))
    return result


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Create a new category."""
    # Check if duplicate name or slug exists
    slug = category_in.slug or generate_slug(category_in.name)
    existing = (
        db.query(Category)
        .filter((Category.name.ilike(category_in.name)) | (Category.slug == slug))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_in.name}' or slug '{slug}' already exists.",
        )

    category = Category(name=category_in.name, slug=slug)
    db.add(category)
    db.commit()
    db.refresh(category)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        created_at=category.created_at,
        updated_at=category.updated_at,
        projects_count=0,
    )


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Update an existing category name or slug."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    if category_in.name is not None:
        category.name = category_in.name
    if category_in.slug is not None:
        category.slug = generate_slug(category_in.slug)
    elif category_in.name is not None:
        category.slug = generate_slug(category_in.name)

    db.commit()
    db.refresh(category)

    count = db.query(Project).filter(Project.category_id == category.id).count()
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        created_at=category.created_at,
        updated_at=category.updated_at,
        projects_count=count,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Delete a category (cascades deletion to its projects)."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    db.delete(category)
    db.commit()
    return None
