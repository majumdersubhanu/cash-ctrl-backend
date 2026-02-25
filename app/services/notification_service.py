import uuid
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification, NotificationType

class NotificationService:
    async def create_notification(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        link: Optional[str] = None
    ) -> Notification:
        """
        Creates a new notification for a specific user.
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            link=link
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
