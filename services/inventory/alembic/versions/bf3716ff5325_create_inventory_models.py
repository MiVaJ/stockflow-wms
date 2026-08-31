"""create inventory models

Revision ID: bf3716ff5325
Revises:
Create Date: 2026-08-31 18:17:00.002567

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "bf3716ff5325"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Создать таблицы каталога и складских остатков."""

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["categories.id"],
            name="fk_categories_parent_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_index(
        "ix_categories_name",
        "categories",
        ["name"],
        unique=False,
    )
    op.create_index(
        "ix_categories_parent_id",
        "categories",
        ["parent_id"],
        unique=False,
    )

    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("barcode", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cost_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("sell_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("weight_kg", sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column("length_cm", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("width_cm", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("height_cm", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column(
            "marketplace_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name="fk_products_category_id",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["unit_id"],
            ["units.id"],
            name="fk_products_unit_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
        sa.UniqueConstraint("barcode"),
        sa.CheckConstraint(
            "cost_price >= 0",
            name="ck_products_cost_price_non_negative",
        ),
        sa.CheckConstraint(
            "sell_price >= 0",
            name="ck_products_sell_price_non_negative",
        ),
        sa.CheckConstraint(
            "weight_kg IS NULL OR weight_kg >= 0",
            name="ck_products_weight_non_negative",
        ),
        sa.CheckConstraint(
            "length_cm IS NULL OR length_cm >= 0",
            name="ck_products_length_non_negative",
        ),
        sa.CheckConstraint(
            "width_cm IS NULL OR width_cm >= 0",
            name="ck_products_width_non_negative",
        ),
        sa.CheckConstraint(
            "height_cm IS NULL OR height_cm >= 0",
            name="ck_products_height_non_negative",
        ),
    )

    op.create_index(
        "ix_products_sku",
        "products",
        ["sku"],
        unique=False,
    )
    op.create_index(
        "ix_products_barcode",
        "products",
        ["barcode"],
        unique=False,
    )
    op.create_index(
        "ix_products_category_id",
        "products",
        ["category_id"],
        unique=False,
    )

    op.create_table(
        "stock",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reserved", sa.Integer(), nullable=False),
        sa.Column("min_stock", sa.Integer(), nullable=False),
        sa.Column("max_stock", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_stock_product_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
        sa.CheckConstraint(
            "quantity >= 0",
            name="ck_stock_quantity_non_negative",
        ),
        sa.CheckConstraint(
            "reserved >= 0",
            name="ck_stock_reserved_non_negative",
        ),
        sa.CheckConstraint(
            "reserved <= quantity",
            name="ck_stock_reserved_lte_quantity",
        ),
        sa.CheckConstraint(
            "min_stock >= 0",
            name="ck_stock_min_stock_non_negative",
        ),
        sa.CheckConstraint(
            "max_stock IS NULL OR max_stock >= 0",
            name="ck_stock_max_stock_non_negative",
        ),
        sa.CheckConstraint(
            "max_stock IS NULL OR max_stock >= min_stock",
            name="ck_stock_max_stock_gte_min_stock",
        ),
    )

    op.create_index(
        "ix_stock_product_id",
        "stock",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:
    """Удалить таблицы каталога и складских остатков."""

    op.drop_index("ix_stock_product_id", table_name="stock")
    op.drop_table("stock")

    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_barcode", table_name="products")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_table("products")

    op.drop_table("units")

    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
