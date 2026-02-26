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
async def list_contacts(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    return await service.get_user_contacts(db, user.id)


# Connection Requests


@router.post("/connections/send", response_model=ConnectionRequestResponse)
async def send_connection(
    payload: ConnectionRequestCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        return await service.send_connection_request(
            db=db, sender_id=user.id, receiver_id=payload.receiver_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/connections/{request_id}", response_model=ConnectionRequestResponse)
async def process_connection(
    request_id: uuid.UUID,
    payload: ConnectionRequestUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        from app.models.connection_request import ConnectionRequestStatus

        accept = payload.status == ConnectionRequestStatus.ACCEPTED
        return await service.process_connection_request(
            db=db, user_id=user.id, request_id=request_id, accept=accept
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/loans", response_model=LoanResponse)
async def create_loan(
    payload: LoanCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        return await service.create_loan(db=db, user_id=user.id, payload=payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/loans", response_model=List[LoanResponse])
async def list_loans(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    return await service.get_user_loans(db, user.id)


@router.post("/loans/{loan_id}/fund", response_model=LoanResponse)
async def fund_loan(
    loan_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        return await service.fund_loan(db=db, user_id=user.id, loan_id=loan_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/loans/{loan_id}/repay", response_model=LoanResponse)
async def repay_loan(
    loan_id: uuid.UUID,
    payload: RepayLoanRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        return await service.repay_loan(
            db=db, user_id=user.id, loan_id=loan_id, payload=payload
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/loans/{loan_id}/settle", response_model=LoanResponse)
async def settle_loan(
    loan_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: P2PService = Depends(get_p2p_service),
):
    try:
        return await service.settle_loan(db=db, user_id=user.id, loan_id=loan_id)
