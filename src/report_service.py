"""Формирование итогового отчета по заказу."""

from src.models import OrderRequest, OrderTotals


class ReportService:
    """Модуль вывода результатов обработки заказа."""

    def build(self, order: OrderRequest, totals: OrderTotals) -> str:
        """Сформировать краткий текстовый отчет."""
        return (
            f"Заказ {order.order_id}: позиций {totals.item_count}, "
            f"сумма {totals.subtotal:.2f} RUB, "
            f"скидка {totals.discount:.2f} RUB, "
            f"к оплате {totals.total:.2f} RUB."
        )
