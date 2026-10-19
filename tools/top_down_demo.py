"""Демонстрация первого этапа нисходящей интеграции."""

from src.integration import OrderProcessor
from src.models import OrderRequest
from src.stubs import OrderServiceStub, ReportServiceStub


def main():
    request = OrderRequest.model_validate(
        {
            "schema_version": "1.0",
            "order_id": "STUB-001",
            "customer_id": "CUS-001",
            "items": [
                {
                    "product_id": "P-1",
                    "name": "Тестовый товар",
                    "quantity": 1,
                    "unit_price": "100.00",
                }
            ],
        }
    )
    processor = OrderProcessor(OrderServiceStub(), ReportServiceStub())
    print(processor.process(request).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
