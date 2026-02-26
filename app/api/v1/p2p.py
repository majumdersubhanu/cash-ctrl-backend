import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.p2p import (
    ContactCreate,
    ContactResponse,
    LoanCreate,
    LoanResponse,
    RepayLoanRequest,
)
from app.schemas.connection import (
    ConnectionRequestCreate,
    ConnectionRequestResponse,
    ConnectionRequestUpdate,
)
from app.services.p2p_service import P2PService


router = APIRouter(tags=["p2p-lending"])


async def get_p2p_service() -> P2PService:
    return P2PService()


@router.post("/contacts", response_model=ContactResponse)
async def create_contact(
    payload: ContactCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        return await service.create_contact(db=db, user_id=user.id, payload=payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contacts", response_model=List[ContactResponse])
