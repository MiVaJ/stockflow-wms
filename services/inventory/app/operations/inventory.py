from __future__ import annotations

import uuid

from app.models.inventory_operation import (
    InventoryOperation,
    InventoryOperationType,
)
from app.models.product import Product
from app.models.stock import Stock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class InventoryService:
    """Сервис управления складскими остатками."""

    async def add_stock(
        self,
        session: AsyncSession,
        product_id: uuid.UUID,
        quantity: int,
        operation_id: uuid.UUID,
    ) -> Stock:
        """Принять товар на склад."""

        return await self._execute_operation(
            session=session,
            product_id=product_id,
            quantity=quantity,
            operation_id=operation_id,
            operation_type=InventoryOperationType.RECEIPT,
        )

    async def remove_stock(
        self,
        session: AsyncSession,
        product_id: uuid.UUID,
        quantity: int,
        operation_id: uuid.UUID,
    ) -> Stock:
        """Списать товар со склада."""

        return await self._execute_operation(
            session=session,
            product_id=product_id,
            quantity=quantity,
            operation_id=operation_id,
            operation_type=InventoryOperationType.WRITE_OFF,
        )

    async def reserve_stock(
        self,
        session: AsyncSession,
        product_id: uuid.UUID,
        quantity: int,
        operation_id: uuid.UUID,
    ) -> Stock:
        """Зарезервировать товар."""

        return await self._execute_operation(
            session=session,
            product_id=product_id,
            quantity=quantity,
            operation_id=operation_id,
            operation_type=InventoryOperationType.RESERVE,
        )

    async def release_stock(
        self,
        session: AsyncSession,
        product_id: uuid.UUID,
        quantity: int,
        operation_id: uuid.UUID,
    ) -> Stock:
        """Снять резерв товара."""

        return await self._execute_operation(
            session=session,
            product_id=product_id,
            quantity=quantity,
            operation_id=operation_id,
            operation_type=InventoryOperationType.RELEASE_RESERVE,
        )

    async def _execute_operation(
        self,
        session: AsyncSession,
        product_id: uuid.UUID,
        quantity: int,
        operation_id: uuid.UUID,
        operation_type: InventoryOperationType,
    ) -> Stock:
        """Выполнить складскую операцию с проверкой идемпотентности."""

        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля.")

        product = await session.scalar(
            select(Product).where(Product.id == product_id).with_for_update(),
        )

        if product is None:
            raise ValueError("Товар не найден.")

        operation = await session.scalar(
            select(InventoryOperation).where(
                InventoryOperation.operation_id == operation_id,
            ),
        )

        if operation is not None:
            self._validate_existing_operation(
                operation=operation,
                product_id=product_id,
                quantity=quantity,
                operation_type=operation_type,
            )

            stock = await session.scalar(
                select(Stock).where(
                    Stock.product_id == product_id,
                ),
            )

            if stock is None:
                raise ValueError(
                    "Остаток для указанного товара не найден.",
                )

            return stock

        stock = await session.scalar(
            select(Stock).where(Stock.product_id == product_id).with_for_update(),
        )

        if stock is None:
            if operation_type is not InventoryOperationType.RECEIPT:
                raise ValueError(
                    "Остаток для указанного товара не найден.",
                )

            stock = Stock(
                product_id=product_id,
                quantity=0,
            )
            session.add(stock)
            await session.flush()

        available_quantity = stock.quantity - stock.reserved

        if operation_type is InventoryOperationType.RECEIPT:
            stock.quantity += quantity

        elif operation_type is InventoryOperationType.WRITE_OFF:
            if quantity > available_quantity:
                raise ValueError(
                    "Недостаточно доступного товара для списания.",
                )

            stock.quantity -= quantity

        elif operation_type is InventoryOperationType.RESERVE:
            if quantity > available_quantity:
                raise ValueError(
                    "Недостаточно доступного товара для резервирования.",
                )

            stock.reserved += quantity

        elif operation_type is InventoryOperationType.RELEASE_RESERVE:
            if quantity > stock.reserved:
                raise ValueError(
                    "Нельзя снять больше товара, чем зарезервировано.",
                )

            stock.reserved -= quantity

        session.add(
            InventoryOperation(
                operation_id=operation_id,
                product_id=product_id,
                operation_type=operation_type,
                quantity=quantity,
            ),
        )

        await session.flush()

        return stock

    @staticmethod
    def _validate_existing_operation(
        operation: InventoryOperation,
        product_id: uuid.UUID,
        quantity: int,
        operation_type: InventoryOperationType,
    ) -> None:
        """Проверить параметры повторной идемпотентной операции."""

        if (
            operation.product_id != product_id
            or operation.quantity != quantity
            or operation.operation_type != operation_type
        ):
            raise ValueError(
                "Operation ID уже используется для другой операции.",
            )


inventory_service = InventoryService()
