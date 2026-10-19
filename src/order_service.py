"""Расчет стоимости заказа и скидки."""

from decimal import Decimal, ROUND_HALF_UP

from src.errors import InvalidIntegrationDataError
from src.models import OrderRequest, OrderTotals


MONEY_STEP = Decimal("0.01")
DISCOUNTS = {
    "WELCOME10": Decimal("0.10"),
    "STUDENT5": Decimal("0.05"),
}


def as_money(value: Decimal) -> Decimal:
    """Округлить денежное значение до копеек."""
    return value.quantize(MONEY_STEP, rounding=ROUND_HALF_UP)


class OrderService:
    """Основной модуль обработки заказов."""

    def calculate(self, order: OrderRequest) -> OrderTotals:
        """Рассчитать сумму, скидку и итог заказа."""
        subtotal = sum(
            (item.unit_price * item.quantity for item in order.items),
            start=Decimal("0"),
        )
        rate = Decimal("0")
        if order.discount_code:
            code = order.discount_code.upper()
            if code == "BULK15":
                if subtotal < Decimal("10000"):
                    raise InvalidIntegrationDataError(
                        "скидка BULK15 доступна для суммы от 10000 рублей"
                    )
                rate = Decimal("0.15")
            elif code in DISCOUNTS:
                rate = DISCOUNTS[code]
            else:
                raise InvalidIntegrationDataError("неизвестный код скидки")

        subtotal = as_money(subtotal)
        discount = as_money(subtotal * rate)
        return OrderTotals(
            subtotal=subtotal,
            discount=discount,
            total=as_money(subtotal - discount),
            item_count=sum(item.quantity for item in order.items),
        )
