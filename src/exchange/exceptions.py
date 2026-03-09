from src.exchange.exchange_entities import ErrorResponseSchema


def check_status(response, object_name: str, object_type: str):
    if response.status_code >= 500:
        raise UnavailableServiceError(service_name=object_name)

    if 400 <= response.status_code < 500:
        if response.status_code == 404:
            raise NotFoundByNameError(object_name=object_name, object_type=object_type)
        raise BadValueError(field_name=object_name)


class CacheNotSavedError(Exception):
    pass


class UnavailableServiceError(Exception):
    def __init__(self, service_name: str):
        self.service_name = service_name

        self.error = f"{self.service_name}_is_not_responding"
        self.message = f"{self.service_name} is unavailable"

        self.error_schema = ErrorResponseSchema(
            error=self.error,
            message=self.message
        )

        super().__init__(self.message)


class NotFoundByNameError(Exception):
    def __init__(self, object_name: str, object_type: str):
        self.object_name = object_name
        self.object_type = object_type

        self.error = f"{self.object_type}_not_found"
        self.message = f"{self.object_type} with name={self.object_name} was not found"

        self.error_schema = ErrorResponseSchema(
            error=self.error,
            message=self.message
        )

        super().__init__(self.message)


class BadValueError(Exception):
    def __init__(self, field_name: str):
        self.field_name = field_name

        self.error = f"{self.field_name}_is_invalid"
        self.message = f"{self.field_name} has invalid value"

        self.error_schema = ErrorResponseSchema(
            error=self.error,
            message=self.message
        )

        super().__init__(self.message)
