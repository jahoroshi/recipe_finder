"""Base model class with common functionality for all database models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models.

    Provides common SQLAlchemy configuration for all models.
    """

    pass


class TimestampMixin:
    """Mixin for automatic timestamp management.

    Provides created_at and updated_at columns that are automatically
    managed by the database.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when the record was created"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated"
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality.

    Provides deleted_at column for implementing soft deletes instead of
    hard deletes from the database.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
        comment="Timestamp when the record was soft deleted"
    )

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None


class AuditMixin:
    """Mixin for audit fields.

    Tracks who created and last modified the record.
    """

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User ID who created this record"
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User ID who last updated this record"
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Base model with all common functionality.

    Includes:
    - UUID primary key
    - Timestamp tracking (created_at, updated_at)
    - Soft delete support (deleted_at)
    - Audit fields (created_by, updated_by)
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary key UUID"
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
