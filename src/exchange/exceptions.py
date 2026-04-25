from src.schemas import ErrorResponseSchema


class CacheNotSavedError(Exception):
    pass


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