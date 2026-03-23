from src.schemas import ErrorResponseSchema


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


class ExternalClientError(Exception):
    def __init__(self, service_name: str, status_code: int, details: str):
        self.service_name = service_name
        self.status_code = status_code
        self.details = details

        self.error = f"{self.service_name}_client_error"
        self.message = f"Request to {self.service_name} failed with status {self.status_code}"

        self.error_schema = ErrorResponseSchema(
            error=self.error,
            message=self.message
        )

        super().__init__(self.message)