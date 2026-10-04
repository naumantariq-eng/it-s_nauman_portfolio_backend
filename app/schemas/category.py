import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def generate_slug(text: str) -> str:
    """Generate URL-safe lowercase slug from text."""
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Category name")


class CategoryCreate(CategoryBase):
    slug: Optional[str] = Field(None, max_length=120)

    @field_validator("slug", mode="before")
    @classmethod
    def set_slug(cls, v: Optional[str], info) -> str:
        if not v and "name" in info.data:
            return generate_slug(info.data["name"])
        return generate_slug(v) if v else ""


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, max_length=120)


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime
    projects_count: Optional[int] = 0

    model_config = {"from_attributes": True}
