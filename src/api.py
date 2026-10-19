"""REST API интегрированной системы обработки заказов."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.errors import IntegrationError
from src.integration import OrderProcessor
from src.models import API_VERSION, OrderRequest, OrderResponse
from src.order_service import OrderService
from src.report_service import ReportService


def create_app(processor=None) -> FastAPI:
    """Создать приложение и подключить модули через оркестратор."""
    active_processor = processor or OrderProcessor(
        OrderService(), ReportService()
    )
    app = FastAPI(
        title="Система обработки заказов",
        version=API_VERSION,
    )

    @app.exception_handler(IntegrationError)
    async def integration_error_handler(
        request: Request, error: IntegrationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": error.code,
                "message": str(error),
                "path": request.url.path,
            },
        )

    @app.get("/health")
    def health():
        return {"status": "ok", "schema_version": API_VERSION}

    @app.post(
        "/api/v1/orders/calculate",
        response_model=OrderResponse,
    )
    def calculate_order(order: OrderRequest, timeout: float = 2.0):
        return active_processor.process(order, timeout_seconds=timeout)

    return app


app = create_app()
