import uuid
import datetime
from pydantic import BaseModel, ConfigDict
from app.models.connection_request import ConnectionRequestStatus


class ConnectionRequestCreate(BaseModel):
    receiver_id: uuid.UUID


class ConnectionRequestResponse(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    status: ConnectionRequestStatus
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ConnectionRequestUpdate(BaseModel):
    status: ConnectionRequestStatus
