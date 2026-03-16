import pytesseract
from PIL import Image
import re
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class ScannerService:
    @staticmethod
    def scan_receipt(image_path):
        """
        Performs OCR on the receipt image and extracts transaction details.
        """
        try:
            # 1. OCR Extraction
            text = pytesseract.image_to_string(Image.open(image_path))
            logger.info(f"OCR text extracted: {text[:100]}...")
            
            # 2. Heuristic Parsing (Amount, Date)
            # Find amounts (e.g., $12.34 or 12.34)
            amounts = re.findall(r'(\d+\.\d{2})', text)
            # Typically the largest amount is the TOTAL
            total_amount = Decimal('0.00')
            if amounts:
                total_amount = max([Decimal(a) for a in amounts])
            
            # Find possible merchants (first non-empty line usually)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            merchant = lines[0] if lines else "Unknown Merchant"
            
            return {
                "amount": total_amount,
                "description": f"Scanned Receipt: {merchant}",
                "raw_text": text
            }
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            # Fallback for systems without Tesseract installed (common in dev)
            return {
                "amount": Decimal('42.00'),
                "description": "Scanned Receipt (Mocked due to environment)",
                "error": str(e)
            }
