from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class InventoryOperationRequest(BaseModel):
    """Запрос на выполнение складской операции."""

    product_id: uuid.UUID
    quantity: int = Field(gt=0)
    operation_id: uuid.UUID


class InventoryResponse(BaseModel):
    """Текущий остаток товара после складской операции."""

    product_id: uuid.UUID
    quantity: int
    reserved: int
    available: int
