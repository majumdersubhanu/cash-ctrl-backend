import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.models.loan import Loan
from app.schemas.p2p import LoanResponse


router = APIRouter(tags=["social"])


@router.get("/vouch-score")
async def get_my_vouch_score(user: User = Depends(current_active_user)):
    """
    Returns the active authenticated user's Vouch Score.
    """
    return {"vouch_score": user.vouch_score}


@router.get("/contacts/{contact_id}/ledger", response_model=List[LoanResponse])
async def get_contact_public_ledger(
    contact_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Allows a user to query the P2P lending history of a *trusted contact*
    to evaluate their creditworthiness before issuing a new loan.
    """
    from app.models.contact import Contact

    # 1. Verify this contact actually belongs to the requesting user
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    contact = (await db.execute(stmt)).scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=404, detail="Contact not found in your social network."
        )

    if not contact.linked_user_id:
        raise HTTPException(
            status_code=400,
            detail="This contact is not a registered user on the platform. No ledger available.",
        )

    # 2. Query the actual public Loan history of the target user
    loan_stmt = select(Loan).where(Loan.user_id == contact.linked_user_id)
    result = await db.execute(loan_stmt)
    loans = result.scalars().all()

    return loans
