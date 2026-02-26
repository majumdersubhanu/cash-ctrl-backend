import uuid
import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.models.transaction import Transaction
from app.services.transaction_service import TransactionService
from app.services.report_service import ReportService
from fastapi.responses import StreamingResponse, Response

router = APIRouter(tags=["data"])


async def get_tx_service() -> TransactionService:
    return TransactionService()


async def get_report_service() -> ReportService:
    return ReportService()

@router.get("/export/csv")
async def export_csv(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    tx_service: TransactionService = Depends(get_tx_service),
