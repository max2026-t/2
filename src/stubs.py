"""Заглушки для первого этапа нисходящей интеграции."""

from decimal import Decimal

from src.models import OrderTotals


class OrderServiceStub:
    """Возвращает фиксированный результат без реального расчета."""

    def calculate(self, order):
        return OrderTotals(
            subtotal=Decimal("100.00"),
            discount=Decimal("0.00"),
            total=Decimal("100.00"),
            item_count=len(order.items),
        )


class ReportServiceStub:
    """Имитирует еще не подключенный модуль отчета."""

    def build(self, order, totals):
        return f"Заглушка отчета для заказа {order.order_id}"
