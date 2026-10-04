from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_mixin, declared_attr, Mapped, mapped_column


@declarative_mixin
class TimestampMixin:
    """Mixin for models requiring created_at and updated_at tracking."""

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False,
        )
