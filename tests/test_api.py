from fastapi.testclient import TestClient

from src.api import app, create_app
from src.integration import OrderProcessor
from src.stubs import OrderServiceStub, ReportServiceStub


client = TestClient(app)

VALID_ORDER = {
    "schema_version": "1.0",
    "order_id": "ORD-200",
    "customer_id": "CUS-10",
    "items": [
        {
            "product_id": "P-10",
            "name": "Мышь",
            "quantity": 2,
            "unit_price": "1200.00",
        }
    ],
    "discount_code": "STUDENT5",
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "schema_version": "1.0"}


def test_calculate_endpoint():
    response = client.post("/api/v1/orders/calculate", json=VALID_ORDER)
    assert response.status_code == 200
    assert response.json()["totals"]["total"] == "2280.00"


def test_api_returns_validation_error_for_empty_items():
    payload = {**VALID_ORDER, "items": []}
    response = client.post("/api/v1/orders/calculate", json=payload)
    assert response.status_code == 422


def test_api_returns_validation_error_for_negative_quantity():
    payload = {**VALID_ORDER}
    payload["items"] = [{**VALID_ORDER["items"][0], "quantity": -1}]
    response = client.post("/api/v1/orders/calculate", json=payload)
    assert response.status_code == 422


def test_api_returns_version_conflict():
    response = client.post(
        "/api/v1/orders/calculate",
        json={**VALID_ORDER, "schema_version": "2.0"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "version_conflict"


def test_api_returns_invalid_discount_error():
    response = client.post(
        "/api/v1/orders/calculate",
        json={**VALID_ORDER, "discount_code": "NOPE"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_data"


def test_api_returns_timeout_error():
    response = client.post(
        "/api/v1/orders/calculate?timeout=0",
        json=VALID_ORDER,
    )
    assert response.status_code == 504


def test_api_can_run_top_down_with_stubs():
    processor = OrderProcessor(OrderServiceStub(), ReportServiceStub())
    stub_client = TestClient(create_app(processor))
    response = stub_client.post(
        "/api/v1/orders/calculate", json=VALID_ORDER
    )
    assert response.status_code == 200
    assert response.json()["report"].startswith("Заглушка")


def test_openapi_contains_order_endpoint():
    schema = client.get("/openapi.json").json()
    assert "/api/v1/orders/calculate" in schema["paths"]
