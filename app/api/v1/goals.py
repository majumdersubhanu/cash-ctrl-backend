import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalContribute, GoalResponse
from app.services.goal_service import GoalService


router = APIRouter(tags=["goals"])


