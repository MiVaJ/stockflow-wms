from __future__ import annotations

import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class InventoryOperationType(StrEnum):
    """Тип складской операции."""

    RECEIPT = "receipt"
    WRITE_OFF = "write_off"
    RESERVE = "reserve"
    RELEASE_RESERVE = "release_reserve"


class InventoryOperation(Base, TimestampMixin):
    """История выполненных операций с товарными остатками."""

    __tablename__ = "inventory_operations"

    __table_args__ = (
        UniqueConstraint(
            "operation_id",
            name="uq_inventory_operations_operation_id",
        ),
        Index(
            "ix_inventory_operations_product_id",
            "product_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    operation_type: Mapped[InventoryOperationType] = mapped_column(
        String(32),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
