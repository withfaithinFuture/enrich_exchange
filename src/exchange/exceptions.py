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