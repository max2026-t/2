"""Интеграционный слой между REST API и прикладными модулями."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError

from src.errors import (
    IntegrationError,
    IntegrationTimeoutError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.models import API_VERSION, OrderRequest, OrderResponse


class OrderProcessor:
    """Оркестратор модулей расчета и формирования отчета."""

    def __init__(self, order_service, report_service):
        if order_service is None or report_service is None:
            raise ModuleUnavailableError("не передан обязательный модуль")
        self.order_service = order_service
        self.report_service = report_service

    def _process(self, order: OrderRequest) -> OrderResponse:
        try:
            totals = self.order_service.calculate(order)
            report = self.report_service.build(order, totals)
        except IntegrationError:
            raise
        except Exception as error:
            raise ModuleUnavailableError(
                "ошибка вызова внутреннего модуля"
            ) from error
        return OrderResponse(
            order_id=order.order_id,
            totals=totals,
            report=report,
        )

    def process(
        self, order: OrderRequest, timeout_seconds: float = 2.0
    ) -> OrderResponse:
        """Проверить контракт и выполнить обработку с таймаутом."""
        if order.schema_version != API_VERSION:
            raise VersionConflictError(
                f"версия {order.schema_version} не поддерживается; "
                f"ожидается {API_VERSION}"
            )
        if timeout_seconds <= 0:
            raise IntegrationTimeoutError("таймаут должен быть положительным")

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self._process, order)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError as error:
            future.cancel()
            raise IntegrationTimeoutError(
                "превышено время обработки заказа"
            ) from error
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
