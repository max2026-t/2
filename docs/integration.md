# Интеграция системы обработки заказов

## Архитектура

Вариант 19 реализован как версионированный REST API с JSON. Верхний уровень системы -
маршрут `POST /api/v1/orders/calculate`. Он принимает заказ и передает его
в `OrderProcessor`. Оркестратор проверяет версию контракта, ограничивает
время выполнения и последовательно вызывает модуль расчета и модуль отчета.

Состав системы:

- `api.py` - HTTP-интерфейс и преобразование ошибок в ответы REST;
- `integration.py` - порядок вызова модулей и контроль таймаута;
- `order_service.py` - расчет стоимости и скидки;
- `report_service.py` - формирование итогового текста;
- `models.py` - структуры входных и выходных данных;
- `stubs.py` - заглушки, использованные на первом этапе интеграции.

## Порядок нисходящей интеграции

1. Создан маршрут REST API и согласован JSON-контракт.
2. Вместо нижних модулей подключены `OrderServiceStub` и
   `ReportServiceStub`.
3. После проверки маршрута заглушка расчета заменена `OrderService`.
4. Последней подключена реальная реализация `ReportService`.
5. Полный маршрут проверен интеграционными тестами и CI.

## Поток данных

```text
HTTP-клиент
    -> FastAPI /api/v1/orders/calculate
    -> OrderRequest
    -> OrderProcessor
    -> OrderService.calculate
    -> ReportService.build
    -> OrderResponse
    -> HTTP JSON
```

## Контракт запроса

```json
{
  "schema_version": "1.0",
  "order_id": "ORD-2026-001",
  "customer_id": "CUS-015",
  "items": [
    {
      "product_id": "P-101",
      "name": "Клавиатура",
      "quantity": 2,
      "unit_price": "2500.00"
    }
  ],
  "discount_code": "WELCOME10"
}
```

## Контракт ответа

```json
{
  "schema_version": "1.0",
  "order_id": "ORD-2026-001",
  "status": "calculated",
  "totals": {
    "currency": "RUB",
    "subtotal": "5000.00",
    "discount": "500.00",
    "total": "4500.00",
    "item_count": 2
  },
  "report": "Заказ ORD-2026-001: позиций 2, сумма 5000.00 RUB, скидка 500.00 RUB, к оплате 4500.00 RUB."
}
```

## Сопоставление данных

| Поле JSON | Модель API | Модуль назначения | Преобразование |
|---|---|---|---|
| `schema_version` | `OrderRequest.schema_version` | интеграционный слой | сравнение с версией 1.0 |
| `order_id` | `OrderRequest.order_id` | отчет | перенос без изменения |
| `items[].quantity` | `OrderItem.quantity` | расчет | проверка целого положительного числа |
| `items[].unit_price` | `OrderItem.unit_price` | расчет | строка JSON преобразуется в `Decimal` |
| `discount_code` | `OrderRequest.discount_code` | расчет | нормализация регистра |
| результат расчета | `OrderTotals` | отчет и API | денежные значения округляются до копеек |

## Ошибки REST API

- `400 invalid_data` - неизвестная или неприменимая скидка;
- `409 version_conflict` - неподдерживаемая версия контракта;
- `422` - JSON не соответствует модели Pydantic;
- `503 module_unavailable` - внутренний модуль недоступен;
- `504 integration_timeout` - превышено время обработки.
