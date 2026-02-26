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
    report_service: ReportService = Depends(get_report_service),
):
    """
    Export all transactions of the user as a CSV file.
    """
    transactions = await tx_service.tx_repo.get_user_transactions(db, user.id, limit=5000)
    csv_file = report_service.export_transactions_csv(transactions)
    
    return StreamingResponse(
        io.BytesIO(csv_file.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=transactions_export.csv"}
    )

@router.get("/export/json")
async def export_json(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    tx_service: TransactionService = Depends(get_tx_service),
    report_service: ReportService = Depends(get_report_service),
):
    """
    Export all transactions of the user as a JSON file.
    """
    transactions = await tx_service.tx_repo.get_user_transactions(db, user.id, limit=5000)
    json_data = report_service.export_transactions_json(transactions)
    
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=transactions_export.json"}
    )


@router.post("/import-csv")
async def import_transactions_csv(
    account_id: uuid.UUID,
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TransactionService = Depends(get_tx_service),
):
    """
    Very basic CSV import assuming standard "Type,Amount,Description" mapping.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invailid file format. Must be CSV."
        )
    try:
        content = await file.read()
        decoded = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        imported_count = 0
        from app.utils.enums import TransactionType

        for row in reader:
            # Flexible dictionary keys parser logic
            amt = float(row.get("Amount", row.get("amount", 0)))
