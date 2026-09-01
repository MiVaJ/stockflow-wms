import uuid

import pytest
from app.models.inventory_operation import InventoryOperation, InventoryOperationType
from app.models.product import Product
from app.operations.inventory import inventory_service
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_add_stock(
    session: AsyncSession,
    product: Product,
) -> None:
    """Приход товара увеличивает остаток."""
    operation_id = uuid.uuid4()

    stock = await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=operation_id,
    )
    await session.commit()

    assert stock.quantity == 10
    assert stock.reserved == 0

    operation = await session.scalar(
        select(InventoryOperation).where(
            InventoryOperation.operation_id == operation_id,
        ),
    )

    assert operation is not None
    assert operation.operation_type == InventoryOperationType.RECEIPT
    assert operation.quantity == 10


@pytest.mark.asyncio
async def test_remove_stock(
    session: AsyncSession,
    product: Product,
) -> None:
    """Списание уменьшает доступный остаток."""
    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    stock = await inventory_service.remove_stock(
        session=session,
        product_id=product.id,
        quantity=4,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    assert stock.quantity == 6
    assert stock.reserved == 0


@pytest.mark.asyncio
async def test_reserve_stock(
    session: AsyncSession,
    product: Product,
) -> None:
    """Резервирование увеличивает зарезервированное количество."""
    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    stock = await inventory_service.reserve_stock(
        session=session,
        product_id=product.id,
        quantity=4,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    assert stock.quantity == 10
    assert stock.reserved == 4


@pytest.mark.asyncio
async def test_release_stock(
    session: AsyncSession,
    product: Product,
) -> None:
    """Снятие резерва уменьшает зарезервированное количество."""
    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    await inventory_service.reserve_stock(
        session=session,
        product_id=product.id,
        quantity=4,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    stock = await inventory_service.release_stock(
        session=session,
        product_id=product.id,
        quantity=2,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    assert stock.quantity == 10
    assert stock.reserved == 2


@pytest.mark.asyncio
async def test_remove_stock_fails_when_quantity_is_insufficient(
    session: AsyncSession,
    product: Product,
) -> None:
    """Списание большего количества, чем доступно, завершается ошибкой."""
    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=5,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    with pytest.raises(
        ValueError,
        match="Недостаточно доступного товара для списания",
    ):
        await inventory_service.remove_stock(
            session=session,
            product_id=product.id,
            quantity=6,
            operation_id=uuid.uuid4(),
        )

    await session.rollback()


@pytest.mark.asyncio
async def test_reserve_stock_fails_when_quantity_is_insufficient(
    session: AsyncSession,
    product: Product,
) -> None:
    """Резервирование большего количества, чем доступно, завершается ошибкой."""
    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=5,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    with pytest.raises(
        ValueError,
        match="Недостаточно доступного товара для резервирования",
    ):
        await inventory_service.reserve_stock(
            session=session,
            product_id=product.id,
            quantity=6,
            operation_id=uuid.uuid4(),
        )

    await session.rollback()


@pytest.mark.asyncio
async def test_release_stock_fails_when_reserve_is_insufficient(
    session: AsyncSession,
    product: Product,
) -> None:
    """Нельзя снять больше товара, чем находится в резерве."""
    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=5,
        operation_id=uuid.uuid4(),
    )
    await session.commit()

    with pytest.raises(
        ValueError,
        match="Нельзя снять больше товара, чем зарезервировано",
    ):
        await inventory_service.release_stock(
            session=session,
            product_id=product.id,
            quantity=1,
            operation_id=uuid.uuid4(),
        )

    await session.rollback()


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [0, -1, -10])
async def test_operation_fails_for_non_positive_quantity(
    session: AsyncSession,
    product: Product,
    quantity: int,
) -> None:
    """Операция с неположительным количеством завершается ошибкой."""
    with pytest.raises(
        ValueError,
        match="Количество должно быть больше нуля",
    ):
        await inventory_service.add_stock(
            session=session,
            product_id=product.id,
            quantity=quantity,
            operation_id=uuid.uuid4(),
        )

    await session.rollback()


@pytest.mark.asyncio
async def test_operation_fails_for_unknown_product(
    session: AsyncSession,
) -> None:
    """Операция для несуществующего товара завершается ошибкой."""
    with pytest.raises(
        ValueError,
        match="Товар не найден",
    ):
        await inventory_service.add_stock(
            session=session,
            product_id=uuid.uuid4(),
            quantity=1,
            operation_id=uuid.uuid4(),
        )

    await session.rollback()


@pytest.mark.asyncio
async def test_operation_is_idempotent(
    session: AsyncSession,
    product: Product,
) -> None:
    """Повторная операция с тем же operation_id не изменяет остаток."""
    operation_id = uuid.uuid4()

    first_stock = await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=operation_id,
    )
    await session.commit()

    second_stock = await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=operation_id,
    )
    await session.commit()

    assert first_stock.quantity == 10
    assert second_stock.quantity == 10

    operations = (
        await session.scalars(
            select(InventoryOperation).where(
                InventoryOperation.operation_id == operation_id,
            ),
        )
    ).all()

    assert len(operations) == 1


@pytest.mark.asyncio
async def test_operation_id_cannot_be_reused_with_different_parameters(
    session: AsyncSession,
    product: Product,
) -> None:
    """Один operation_id нельзя использовать для другой операции."""
    operation_id = uuid.uuid4()

    await inventory_service.add_stock(
        session=session,
        product_id=product.id,
        quantity=10,
        operation_id=operation_id,
    )
    await session.commit()

    with pytest.raises(
        ValueError,
        match="Operation ID уже используется для другой операции",
    ):
        await inventory_service.add_stock(
            session=session,
            product_id=product.id,
            quantity=5,
            operation_id=operation_id,
        )

    await session.rollback()
