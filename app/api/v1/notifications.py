import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.services.notification_service import NotificationService

router = APIRouter(tags=["notifications"])

async def get_notification_service() -> NotificationService:
    return NotificationService()

