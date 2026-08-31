from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Stock(Base, TimestampMixin):
    """Текущий физический остаток и резерв товара."""

    __tablename__ = "stock"

    __table_args__ = (
        Index("ix_stock_product_id", "product_id"),
        CheckConstraint(
            "quantity >= 0",
            name="ck_stock_quantity_non_negative",
        ),
        CheckConstraint(
            "reserved >= 0",
            name="ck_stock_reserved_non_negative",
        ),
        CheckConstraint(
            "reserved <= quantity",
            name="ck_stock_reserved_lte_quantity",
        ),
        CheckConstraint(
            "min_stock >= 0",
            name="ck_stock_min_stock_non_negative",
        ),
        CheckConstraint(
            "max_stock IS NULL OR max_stock >= 0",
            name="ck_stock_max_stock_non_negative",
        ),
        CheckConstraint(
            "max_stock IS NULL OR max_stock >= min_stock",
            name="ck_stock_max_stock_gte_min_stock",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    reserved: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    min_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    max_stock: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product: Mapped[Product] = relationship(
        "Product",
        back_populates="stock",
    )
