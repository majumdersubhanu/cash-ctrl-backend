from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.utils.enums import CategoryType


class CategoryCreate(BaseModel):
    name: str
    type: CategoryType
    parent_id: UUID | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    type: CategoryType
    parent_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
