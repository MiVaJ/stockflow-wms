from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.stock import Stock
    from app.models.unit import Unit


class Product(Base, TimestampMixin):
    """Товар в каталоге складской системы."""

    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_sku", "sku"),
        Index("ix_products_barcode", "barcode"),
        Index("ix_products_category_id", "category_id"),
        CheckConstraint(
            "cost_price >= 0",
            name="ck_products_cost_price_non_negative",
        ),
        CheckConstraint(
            "sell_price >= 0",
            name="ck_products_sell_price_non_negative",
        ),
        CheckConstraint(
            "weight_kg IS NULL OR weight_kg >= 0",
            name="ck_products_weight_non_negative",
        ),
        CheckConstraint(
            "length_cm IS NULL OR length_cm >= 0",
            name="ck_products_length_non_negative",
        ),
        CheckConstraint(
            "width_cm IS NULL OR width_cm >= 0",
            name="ck_products_width_non_negative",
        ),
        CheckConstraint(
            "height_cm IS NULL OR height_cm >= 0",
            name="ck_products_height_non_negative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    barcode: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    unit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("units.id"),
        nullable=False,
    )

    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )

    sell_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )

    weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 3),
        nullable=True,
    )

    length_cm: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2),
        nullable=True,
    )

    width_cm: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2),
        nullable=True,
    )

    height_cm: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2),
        nullable=True,
    )

    marketplace_ids: Mapped[dict[str, str]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        default=dict,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    category: Mapped[Category | None] = relationship(
        "Category",
        back_populates="products",
    )

    unit: Mapped[Unit] = relationship(
        "Unit",
        back_populates="products",
    )

    stock: Mapped[Stock | None] = relationship(
        "Stock",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )
