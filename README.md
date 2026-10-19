# Система обработки заказов

Учебный проект по варианту 19. REST API принимает заказ в JSON, проверяет
его структуру, рассчитывает стоимость и скидку, затем формирует итоговый
отчет. Интеграция выполнена нисходящим способом: сначала проверен маршрут
API с заглушками, после чего подключены реальные модули расчета и отчета.

Автор: Тамбовцев Максим Дмитриевич, группа Т9-ИП-25-1.

## Состав проекта

```text
src/api.py              REST API
src/integration.py      порядок вызова модулей и таймаут
src/models.py           модели JSON
src/order_service.py    стоимость и скидки
src/report_service.py   итоговый отчет
src/stubs.py            заглушки первого этапа
tests/                  модульные и интеграционные тесты
docs/                   документация интеграции
```

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Запуск

```bash
python -m src.server
```

После запуска доступны:

- `http://127.0.0.1:8000/docs` - интерактивная документация;
- `GET /health` - проверка доступности;
- `POST /api/v1/orders/calculate` - расчет заказа.

Пример запроса находится в `examples/order_request.json`.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/calculate \
  -H "Content-Type: application/json" \
  --data @examples/order_request.json
```

## Проверка

```bash
flake8 src tests tools
coverage run -m pytest -v
coverage report --fail-under=90
```

Подробное описание архитектуры, REST-контракта, сопоставления полей и
обработки ошибок находится в `docs/integration.md`.
