from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    github_url: Mapped[str] = mapped_column(String(500), nullable=False)

    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # JSON array for flexible technology tags: ["React", "FastAPI", "Docker"]
    tech_stack: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="projects")

    def __repr__(self) -> str:
        return f"<Project id={self.id} title='{self.title}'>"
