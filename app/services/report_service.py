import csv
import io
import json
import uuid
from typing import Sequence
from fastapi.responses import StreamingResponse
from app.models.transaction import Transaction

class ReportService:
    def export_transactions_csv(self, transactions: Sequence[Transaction]) -> io.StringIO:
        """
        Generates a CSV report of transactions.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(["Date", "Amount", "Type", "Note", "Category ID", "Account ID"])
        
        for tx in transactions:
            writer.writerow([
                tx.transaction_date,
                float(tx.amount),
                tx.type.value,
                tx.note or "",
                tx.category_id,
                tx.account_id
            ])
            
        output.seek(0)
        return output

    def export_transactions_json(self, transactions: Sequence[Transaction]) -> str:
        """
        Generates a JSON report of transactions.
        """
        data = []
        for tx in transactions:
            data.append({
                "id": str(tx.id),
                "date": str(tx.transaction_date),
                "amount": float(tx.amount),
                "type": tx.type.value,
                "note": tx.note,
                "category_id": str(tx.category_id) if tx.category_id else None,
