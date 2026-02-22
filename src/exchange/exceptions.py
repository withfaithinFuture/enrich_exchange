class UnavailableServiceError(Exception):
    def __init__(self, service_name: str):
        self.service_name = service_name

        self.error = f"{self.service_name}_is_not_responding"
        self.message = f"{self.service_name} is unavailable"

        super().__init__(self.message)