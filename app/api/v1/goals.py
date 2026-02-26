import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalContribute, GoalResponse
from app.services.goal_service import GoalService


router = APIRouter(tags=["goals"])


async def get_goal_service() -> GoalService:
    return GoalService()


@router.post("/", response_model=GoalResponse)
async def create_goal(
    payload: GoalCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: GoalService = Depends(get_goal_service),
):
    try:
        return await service.create_goal(db=db, user_id=user.id, payload=payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
