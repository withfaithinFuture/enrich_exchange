from pydantic import BaseModel, ConfigDict


class ErrorResponseSchema(BaseModel):
    error: str
    message: str

    model_config = ConfigDict(extra='allow')