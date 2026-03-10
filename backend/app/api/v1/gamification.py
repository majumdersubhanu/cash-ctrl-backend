from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.services.gamification_service import GamificationService

router = APIRouter(tags=["gamification"])


async def get_gamification_service() -> GamificationService:
    return GamificationService()


@router.get("/streaks")
async def get_streaks(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: GamificationService = Depends(get_gamification_service),
):
    streak = await service.get_no_spend_streak(db, user.id)
    return {"current_streak_days": streak}


@router.get("/achievements")
async def get_achievements(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: GamificationService = Depends(get_gamification_service),
):
    achievements = await service.check_achievements(db, user.id)
    return {"achievements": achievements}
