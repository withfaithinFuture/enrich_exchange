from fastapi import HTTPException
from starlette import status


class UnavailableServiceError(Exception):
    def __init__(self, service_name: str):
        self.service_name = service_name

        self.error = f"{self.service_name}_is_not_responding"
        self.message = f"{self.service_name} is unavailable"

        super().__init__(self.message)


class Server500Error(Exception):
    def __init__(self, service_name: str, status_code: int):
        self.service_name = service_name
        self.status_code = status_code

        self.error = f"{self.service_name}_internal_error_{self.status_code}"
        self.message = f"{self.service_name} returned server error: {self.status_code}"

        super().__init__(self.message)


class NotFoundByNameError(HTTPException):
    def __init__(self, object_name: str, object_type: str):
        self.object_name = object_name
        self.object_type = object_type

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": f"{self.object_type}_not_found",
            "message": f"{self.object_type} with name={self.object_name} was not found",
            f"{self.object_type}_name": str(self.object_name)})