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

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: NotificationService = Depends(get_notification_service),
):
    """
    List all notifications for the current user.
    """
    return await service.get_user_notifications(db, user.id, unread_only)

@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: uuid.UUID,
    payload: NotificationUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Mark a notification as read or unread.
    """
    if not payload.is_read:
        raise HTTPException(status_code=400, detail="Only marking as read is supported.")
        
    notification = await service.mark_as_read(db, user.id, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    return notification

@router.post("/mark-all-read")
async def mark_all_read(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Mark all unread notifications for the current user as read.
    """
    count = await service.mark_all_as_read(db, user.id)
    return {"status": "ok", "marked_read_count": count}
