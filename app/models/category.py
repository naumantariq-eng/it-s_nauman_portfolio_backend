from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)

    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="desc(Project.created_at)",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name='{self.name}'>"
