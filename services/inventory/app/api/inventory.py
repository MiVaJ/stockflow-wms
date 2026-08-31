from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.operations.inventory import inventory_service
from app.schemas.inventory import (
    InventoryOperationRequest,
    InventoryResponse,
)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Предоставить асинхронную сессию базы данных."""

    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def _to_response(
    product_id: uuid.UUID,
    quantity: int,
    reserved: int,
) -> InventoryResponse:
    """Преобразовать складской остаток в ответ API."""

    return InventoryResponse(
        product_id=product_id,
        quantity=quantity,
        reserved=reserved,
        available=quantity - reserved,
    )


@router.post(
    "/receipt",
    response_model=InventoryResponse,
)
async def receipt(
    data: InventoryOperationRequest,
    session: SessionDependency,
) -> InventoryResponse:
    """Принять товар на склад."""

    stock = await inventory_service.add_stock(
        session=session,
        product_id=data.product_id,
        quantity=data.quantity,
        operation_id=data.operation_id,
    )

    await session.commit()

    return _to_response(
        product_id=stock.product_id,
        quantity=stock.quantity,
        reserved=stock.reserved,
    )


@router.post(
    "/write-off",
    response_model=InventoryResponse,
)
async def write_off(
    data: InventoryOperationRequest,
    session: SessionDependency,
) -> InventoryResponse:
    """Списать товар со склада."""

    stock = await inventory_service.remove_stock(
        session=session,
        product_id=data.product_id,
        quantity=data.quantity,
        operation_id=data.operation_id,
    )

    await session.commit()

    return _to_response(
        product_id=stock.product_id,
        quantity=stock.quantity,
        reserved=stock.reserved,
    )


@router.post(
    "/reserve",
    response_model=InventoryResponse,
)
async def reserve(
    data: InventoryOperationRequest,
    session: SessionDependency,
) -> InventoryResponse:
    """Зарезервировать товар."""

    stock = await inventory_service.reserve_stock(
        session=session,
        product_id=data.product_id,
        quantity=data.quantity,
        operation_id=data.operation_id,
    )

    await session.commit()

    return _to_response(
        product_id=stock.product_id,
        quantity=stock.quantity,
        reserved=stock.reserved,
    )


@router.post(
    "/release",
    response_model=InventoryResponse,
)
async def release(
    data: InventoryOperationRequest,
    session: SessionDependency,
) -> InventoryResponse:
    """Снять резерв товара."""

    stock = await inventory_service.release_stock(
        session=session,
        product_id=data.product_id,
        quantity=data.quantity,
        operation_id=data.operation_id,
    )

    await session.commit()

    return _to_response(
        product_id=stock.product_id,
        quantity=stock.quantity,
        reserved=stock.reserved,
    )
