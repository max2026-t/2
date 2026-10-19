"""Модели REST API системы обработки заказов."""

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


API_VERSION = "1.0"


class OrderItem(BaseModel):
    """Одна позиция заказа."""

    product_id: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    quantity: int = Field(gt=0, le=1000)
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class OrderRequest(BaseModel):
    """JSON-запрос на расчет заказа."""

    schema_version: str
    order_id: str = Field(min_length=1, max_length=40)
    customer_id: str = Field(min_length=1, max_length=40)
    items: List[OrderItem] = Field(min_length=1, max_length=100)
    discount_code: Optional[str] = Field(default=None, max_length=30)


class OrderTotals(BaseModel):
    """Результат расчета стоимости."""

    currency: str = "RUB"
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    item_count: int


class OrderResponse(BaseModel):
    """Ответ интегрированной системы."""

    schema_version: str = API_VERSION
    order_id: str
    status: str = "calculated"
    totals: OrderTotals
    report: str
