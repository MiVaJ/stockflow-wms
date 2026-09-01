from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import Product


class Unit(Base):
    """Единица измерения товара."""

    __tablename__ = "units"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    products: Mapped[list[Product]] = relationship(
        "Product",
        back_populates="unit",
    )
