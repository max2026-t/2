from decimal import Decimal

import pytest

from src.errors import InvalidIntegrationDataError
from src.models import OrderItem, OrderRequest
from src.order_service import OrderService, as_money


def make_order(code=None, price="100.00", quantity=2):
    return OrderRequest(
        schema_version="1.0",
        order_id="ORD-1",
        customer_id="CUS-1",
        items=[
            OrderItem(
                product_id="P-1",
                name="Товар",
                quantity=quantity,
                unit_price=Decimal(price),
            )
        ],
        discount_code=code,
    )


def test_calculate_without_discount():
    result = OrderService().calculate(make_order())
    assert result.subtotal == Decimal("200.00")
    assert result.discount == Decimal("0.00")
    assert result.total == Decimal("200.00")


def test_welcome_discount():
    result = OrderService().calculate(make_order("welcome10"))
    assert result.discount == Decimal("20.00")
    assert result.total == Decimal("180.00")


def test_student_discount():
    result = OrderService().calculate(make_order("STUDENT5"))
    assert result.total == Decimal("190.00")


def test_bulk_discount_for_large_order():
    result = OrderService().calculate(
        make_order("BULK15", price="5000", quantity=2)
    )
    assert result.discount == Decimal("1500.00")


def test_bulk_discount_rejects_small_order():
    with pytest.raises(InvalidIntegrationDataError):
        OrderService().calculate(make_order("BULK15"))


def test_unknown_discount_is_rejected():
    with pytest.raises(InvalidIntegrationDataError):
        OrderService().calculate(make_order("UNKNOWN"))


def test_item_count_is_sum_of_quantities():
    assert OrderService().calculate(make_order(quantity=7)).item_count == 7


def test_money_rounding():
    assert as_money(Decimal("1.005")) == Decimal("1.01")
