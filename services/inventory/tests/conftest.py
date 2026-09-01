from collections.abc import AsyncGenerator

import pytest_asyncio
from app.core.config import settings
from app.db.base import Base
from app.models.product import Product
from app.models.unit import Unit
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:"
    f"{settings.postgres_password}@{settings.postgres_host}:"
    f"{settings.postgres_port}/{settings.postgres_db}"
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database() -> AsyncGenerator[None]:
    """Подготовить чистую базу данных для каждого теста."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        yield

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    """Предоставить отдельную сессию для теста."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as session:
            yield session
            await session.rollback()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def product(session: AsyncSession) -> Product:
    """Создать тестовый товар."""
    unit = Unit(
        name="Штука",
        symbol="шт",
    )
    session.add(unit)
    await session.flush()

    product = Product(
        sku="TEST-001",
        name="Тестовый товар",
        unit_id=unit.id,
        cost_price=100,
        sell_price=150,
        marketplace_ids={},
        is_active=True,
    )
    session.add(product)
    await session.flush()

    return product
