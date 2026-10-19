"""Ошибки интеграционного слоя системы обработки заказов."""


class IntegrationError(Exception):
    """Базовая ошибка взаимодействия модулей."""

    code = "integration_error"
    status_code = 500


class InvalidIntegrationDataError(IntegrationError):
    """Переданные между модулями данные не прошли проверку."""

    code = "invalid_data"
    status_code = 400


class ModuleUnavailableError(IntegrationError):
    """Не удалось вызвать один из модулей системы."""

    code = "module_unavailable"
    status_code = 503


class IntegrationTimeoutError(IntegrationError):
    """Время ожидания ответа модуля истекло."""

    code = "integration_timeout"
    status_code = 504


class VersionConflictError(IntegrationError):
    """Версия входного контракта не поддерживается."""

    code = "version_conflict"
    status_code = 409
