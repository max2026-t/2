import time

import pytest

from src.errors import (
    IntegrationTimeoutError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.integration import OrderProcessor
from src.models import OrderRequest
from src.order_service import OrderService
from src.report_service import ReportService
from src.stubs import OrderServiceStub, ReportServiceStub


PAYLOAD = {
    "schema_version": "1.0",
    "order_id": "ORD-100",
    "customer_id": "CUS-7",
    "items": [
        {
            "product_id": "P-1",
            "name": "Клавиатура",
            "quantity": 2,
            "unit_price": "2500.00",
        }
    ],
    "discount_code": "WELCOME10",
}


def order(**changes):
    data = {**PAYLOAD, **changes}
    return OrderRequest.model_validate(data)


def test_top_down_stage_works_with_stubs():
    processor = OrderProcessor(OrderServiceStub(), ReportServiceStub())
    response = processor.process(order())
    assert response.totals.total == 100
    assert response.report.startswith("Заглушка")


def test_real_modules_are_integrated():
    processor = OrderProcessor(OrderService(), ReportService())
    response = processor.process(order())
    assert response.totals.total == 4500
    assert "ORD-100" in response.report


def test_response_preserves_order_id():
    processor = OrderProcessor(OrderService(), ReportService())
    assert processor.process(order()).order_id == "ORD-100"


def test_version_conflict_is_detected():
    processor = OrderProcessor(OrderService(), ReportService())
    with pytest.raises(VersionConflictError):
        processor.process(order(schema_version="2.0"))


def test_missing_module_is_detected():
    with pytest.raises(ModuleUnavailableError):
        OrderProcessor(None, ReportService())


def test_unexpected_module_error_is_wrapped():
    class BrokenService:
        def calculate(self, value):
            raise RuntimeError("сбой")

    processor = OrderProcessor(BrokenService(), ReportService())
    with pytest.raises(ModuleUnavailableError):
        processor.process(order())


def test_non_positive_timeout_is_rejected():
    processor = OrderProcessor(OrderService(), ReportService())
    with pytest.raises(IntegrationTimeoutError):
        processor.process(order(), timeout_seconds=0)


def test_slow_module_causes_timeout():
    class SlowService(OrderService):
        def calculate(self, value):
            time.sleep(0.05)
            return super().calculate(value)

    processor = OrderProcessor(SlowService(), ReportService())
    with pytest.raises(IntegrationTimeoutError):
        processor.process(order(), timeout_seconds=0.001)


def test_report_contains_all_totals():
    processor = OrderProcessor(OrderService(), ReportService())
    report = processor.process(order()).report
    assert "5000.00" in report
    assert "500.00" in report
    assert "4500.00" in report
