from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.services.gamification_service import GamificationService

router = APIRouter(tags=["gamification"])


async def get_gamification_service() -> GamificationService:
    return GamificationService()


