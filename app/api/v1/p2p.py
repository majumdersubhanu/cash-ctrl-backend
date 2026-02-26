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
