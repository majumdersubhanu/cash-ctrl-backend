import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.goal import Goal


class GoalService:
    async def create_goal(self, db: AsyncSession, user_id: uuid.UUID, payload) -> Goal:
        goal = Goal(
            user_id=user_id,
            account_id=payload.account_id,
            name=payload.name,
            target_amount=payload.target_amount,
            deadline=payload.deadline,
