"""Регрессионные проверки варианта 19 по таблице решений."""

from pathlib import Path
from runpy import run_path

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.models import OrderRequest, OrderTotals
from src.report_service import ReportService
from src.server import main
from test_api import VALID_ORDER


ENDPOINT = "/api/v1/orders/calculate"


@pytest.fixture
def api():
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize(
    "code,price,status,value",
    [
        (None, "10000.00", 200, "10000.00"),
        ("welcome10", "9999.99", 200, "8999.99"),
        ("STUDENT5", "0.10", 200, "0.09"),
        ("BULK15", "9999.99", 400, "invalid_data"),
        ("BULK15", "10000.00", 200, "8500.00"),
        ("BULK15", "10000.01", 200, "8500.01"),
        ("UNKNOWN", "10000.00", 400, "invalid_data"),
    ],
)
def test_discount_decision_table(api, code, price, status, value):
    item = {**VALID_ORDER["items"][0], "quantity": 1, "unit_price": price}
    payload = {**VALID_ORDER, "discount_code": code, "items": [item]}
    response = api.post(ENDPOINT, json=payload)
    assert response.status_code == status
    result = response.json()
    if status == 200:
        assert result["totals"]["total"] == value
        assert f"к оплате {value} RUB" in result["report"]
    else:
        assert result["error"] == value
        assert result["path"] == ENDPOINT


@pytest.mark.parametrize(
    "quantity,status", [(0, 422), (1, 200), (1000, 200), (1001, 422)]
)
def test_quantity_boundaries(api, quantity, status):
    item = {**VALID_ORDER["items"][0], "quantity": quantity}
    response = api.post(ENDPOINT, json={**VALID_ORDER, "items": [item]})
    assert response.status_code == status


@pytest.mark.parametrize("quantity", [True, False])
def test_boolean_quantity_is_not_a_count(api, quantity):
    item = {**VALID_ORDER["items"][0], "quantity": quantity}
    response = api.post(ENDPOINT, json={**VALID_ORDER, "items": [item]})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == [
        "body", "items", 0, "quantity"
    ]


def test_report_formats_money_and_count():
    order = OrderRequest.model_validate(VALID_ORDER)
    totals = OrderTotals(
        subtotal="10", discount="0.5", total="9.5", item_count=2
    )
    assert ReportService().build(order, totals) == (
        "Заказ ORD-200: позиций 2, сумма 10.00 RUB, "
        "скидка 0.50 RUB, к оплате 9.50 RUB."
    )


@pytest.mark.parametrize("as_script", [False, True])
def test_server_entry_point(monkeypatch, as_script):
    calls = []

    def record(app, **options):
        calls.append((app, options))

    monkeypatch.setattr("src.server.uvicorn.run", record)
    if as_script:
        path = Path(__file__).resolve().parents[1] / "src" / "server.py"
        run_path(str(path), run_name="__main__")
    else:
        main()
    assert calls == [
        ("src.api:app", {"host": "127.0.0.1", "port": 8000, "reload": False})
    ]
