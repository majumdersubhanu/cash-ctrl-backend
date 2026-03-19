try:
    import pytesseract
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

import logging
import re
from decimal import Decimal

logger = logging.getLogger(__name__)


class ScannerService:
    @staticmethod
    def scan_receipt(image_path):
        """
        Performs OCR on the receipt image and extracts transaction details.
        """
        if not OCR_AVAILABLE:
            logger.warning(
                "OCR (Pytesseract) is not installed. Using fallback mock data."
            )
            return {
                "amount": Decimal("42.00"),
                "description": "Mocked Receipt (OCR unavailable)",
                "raw_text": "Sample Receipt Text\nTotal: $42.00\nMerchant: Gemini Mart",
            }

        try:
            # 1. OCR Extraction
            text = pytesseract.image_to_string(Image.open(image_path))
            logger.info(f"OCR text extracted: {text[:100]}...")

            # 2. Heuristic Parsing
            amounts = re.findall(r"(\d+\.\d{2})", text)
            total_amount = Decimal("0.00")
            if amounts:
                total_amount = max([Decimal(a) for a in amounts])

            lines = [line.strip() for line in text.split("\n") if line.strip()]
            merchant = lines[0] if lines else "Unknown Merchant"

            return {
                "amount": total_amount,
                "description": f"Scanned Receipt: {merchant}",
                "raw_text": text,
            }
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            return {
                "amount": Decimal("0.00"),
                "description": "Scanned Receipt (Error)",
                "error": str(e),
            }
