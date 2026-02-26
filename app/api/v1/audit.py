from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.services.audit_service import HealthAuditService
from app.core.users import current_active_user
from app.models.user import User

router = APIRouter(tags=["analytics"])
audit_service = HealthAuditService()

@router.get("/", response_model=None)
async def get_financial_audit(
    db: AsyncSession = Depends(deps.get_db),
    user: User = Depends(current_active_user)
