from uuid import UUID
from pydantic import BaseModel, ConfigDict
from pydantic.v1 import EmailStr


class ErrorResponseSchema(BaseModel):
    error: str
    message: str

    model_config = ConfigDict(extra='allow')


class IncomingEnrichPayload(BaseModel):
    event_id: UUID
    username: str
    email: EmailStr
    shares_broker: str

    model_config = ConfigDict(extra='allow')
