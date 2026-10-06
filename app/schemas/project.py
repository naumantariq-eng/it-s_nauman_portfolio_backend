from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10)
    image_url: Optional[str] = Field(default="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80", max_length=500)
    github_url: str = Field(..., min_length=10, max_length=500)
    category_id: int = Field(..., gt=0)
    tech_stack: List[str] = Field(default_factory=list)

    @field_validator("image_url", mode="before")
    @classmethod
    def set_default_image(cls, v: Optional[str]) -> str:
        if not v or not str(v).strip():
            return "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80"
        return str(v).strip()

    @field_validator("github_url")
    @classmethod
    def validate_github(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("GitHub URL must start with http:// or https://")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    image_url: Optional[str] = Field(None, min_length=5, max_length=500)
    github_url: Optional[str] = Field(None, min_length=10, max_length=500)
    category_id: Optional[int] = Field(None, gt=0)
    tech_stack: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    github_url: str
    category_id: int
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    tech_stack: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
