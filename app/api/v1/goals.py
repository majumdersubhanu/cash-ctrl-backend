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


@router.get("/", response_model=list[GoalResponse])
async def list_goals(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: GoalService = Depends(get_goal_service),
):
    return await service.get_user_goals(db, user.id)


@router.post("/{goal_id}/contribute", response_model=GoalResponse)
async def contribute_to_goal(
    goal_id: uuid.UUID,
    payload: GoalContribute,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: GoalService = Depends(get_goal_service),
):
    try:
        return await service.contribute_to_goal(
            db=db, user_id=user.id, goal_id=goal_id, amount=payload.amount
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
