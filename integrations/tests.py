from decimal import Decimal
from unittest.mock import patch, MagicMock


from integrations.scanner import ScannerService
from integrations.services import TruecallerService, CashfreeService, SetuService


class TestScannerServiceOCRUnavailable:
    """Tests when pytesseract / PIL are not installed."""

    def test_returns_mock_data_when_ocr_unavailable(self):
        """When OCR_AVAILABLE is False, scan_receipt returns fallback mock data."""
        with patch("integrations.scanner.OCR_AVAILABLE", False):
            result = ScannerService.scan_receipt("/fake/path/receipt.png")

        assert result["amount"] == Decimal("42.00")
        assert "Mocked Receipt" in result["description"]
        assert "raw_text" in result

    def test_fallback_raw_text_is_present(self):
        with patch("integrations.scanner.OCR_AVAILABLE", False):
            result = ScannerService.scan_receipt("/fake/path/receipt.png")

        assert isinstance(result["raw_text"], str)
        assert len(result["raw_text"]) > 0


class TestScannerServiceOCRAvailable:
    """Tests exercising the OCR path (pytesseract mocked)."""

    def _run_scan(self, ocr_text):
        """Helper: patch OCR to return ocr_text, run scan_receipt, return result."""
        mock_image = MagicMock()
        with (
            patch("integrations.scanner.OCR_AVAILABLE", True),
            patch("integrations.scanner.pytesseract", create=True) as mock_tess,
            patch("integrations.scanner.Image", create=True) as mock_pil,
        ):
            mock_pil.open.return_value = mock_image
            mock_tess.image_to_string.return_value = ocr_text
            result = ScannerService.scan_receipt("/fake/path/receipt.png")
        return result

    def test_extracts_max_amount_from_text(self):
        """The highest decimal value in the receipt text becomes the amount."""
        text = "Acme Store\nItem A   10.50\nItem B   22.99\nTotal    33.49"
        result = self._run_scan(text)
        assert result["amount"] == Decimal("33.49")

    def test_uses_first_line_as_merchant(self):
        """The first non-blank line of OCR text becomes the merchant."""
        text = "Best Mart\nBread  2.50\nTotal  2.50"
        result = self._run_scan(text)
        assert "Best Mart" in result["description"]

    def test_raw_text_is_returned(self):
        text = "Shop\nTotal 5.00"
        result = self._run_scan(text)
        assert result["raw_text"] == text

    def test_amount_zero_when_no_decimals_found(self):
        """If OCR produces no decimal numbers, amount is 0.00."""
        text = "No prices here"
        result = self._run_scan(text)
        assert result["amount"] == Decimal("0.00")

    def test_unknown_merchant_when_no_lines(self):
        """Empty OCR text yields 'Unknown Merchant' as the description base."""
        text = ""
        result = self._run_scan(text)
        assert "Unknown Merchant" in result["description"]

    def test_single_amount_in_text(self):
        text = "QuickMart\nTotal 19.99"
        result = self._run_scan(text)
        assert result["amount"] == Decimal("19.99")

    def test_multiple_amounts_picks_largest(self):
        text = "BigStore\n1.00\n50.00\n25.00"
        result = self._run_scan(text)
        assert result["amount"] == Decimal("50.00")


class TestScannerServiceOCRError:
    """Tests the exception handling branch in scan_receipt."""

    def test_returns_error_dict_on_exception(self):
        """If pytesseract raises, scan_receipt returns an error payload."""
        with (
            patch("integrations.scanner.OCR_AVAILABLE", True),
            patch("integrations.scanner.Image", create=True) as mock_pil,
            patch("integrations.scanner.pytesseract", create=True),
        ):
            mock_pil.open.side_effect = Exception("File not found")
            result = ScannerService.scan_receipt("/bad/path.png")

        assert result["amount"] == Decimal("0.00")
        assert "error" in result
        assert "File not found" in result["error"]

    def test_error_description_contains_fallback_text(self):
        with (
            patch("integrations.scanner.OCR_AVAILABLE", True),
            patch("integrations.scanner.Image", create=True) as mock_pil,
            patch("integrations.scanner.pytesseract", create=True),
        ):
            mock_pil.open.side_effect = ValueError("bad image")
            result = ScannerService.scan_receipt("/bad/path.png")

        assert "Scanned Receipt" in result["description"]

    def test_pytesseract_error_is_captured(self):
        """If pytesseract.image_to_string itself raises, error is captured."""
        with (
            patch("integrations.scanner.OCR_AVAILABLE", True),
            patch("integrations.scanner.Image", create=True) as mock_pil,
            patch("integrations.scanner.pytesseract", create=True) as mock_tess,
        ):
            mock_pil.open.return_value = MagicMock()
            mock_tess.image_to_string.side_effect = RuntimeError("OCR crashed")
            result = ScannerService.scan_receipt("/some/path.png")

        assert "error" in result
        assert "OCR crashed" in result["error"]


class TestExternalIntegrationServices:
    """Tests for TruecallerService, CashfreeService, and SetuService."""

    def test_truecaller_service_no_key(self):
        with patch("django.conf.settings.TRUECALLER_PARTNER_KEY", None):
            result = TruecallerService.verify_profile(
                {"phone_number": "123", "name": "A"}
            )
            assert result is None

    def test_truecaller_service_success(self):
        with patch("django.conf.settings.TRUECALLER_PARTNER_KEY", "dummy_key"):
            result = TruecallerService.verify_profile(
                {"phone_number": "123", "name": "A"}
            )
            assert result == {
                "status": "success",
                "phone": "123",
                "name": "A",
            }

    def test_cashfree_service(self):
        with (
            patch("django.conf.settings.CASHFREE_APP_ID", "id"),
            patch("django.conf.settings.CASHFREE_SECRET_KEY", "sec"),
        ):
            result = CashfreeService.verify_aadhaar("123456789012")
            assert result == {
                "status": "SUCCESS",
                "message": "Aadhaar verified successfully",
            }

    def test_setu_service(self):
        with patch("django.conf.settings.SETU_CLIENT_ID", "id"):
            result = SetuService.create_account_linking_request("user_123")
            assert "session_url" in result
            assert "request_id" in result
