from typing import List, Tuple

import easyocr

from informed_be.config.settings import settings
from informed_be.config.logging import get_logger
from informed_be.metrics import OCR_REQUESTS, OCR_ERRORS, OCR_DURATION

logger = get_logger(__name__)


class OCRService:
    @staticmethod
    def extract_text(image_bytes: bytes) -> List[Tuple[str, float]]:
        OCR_REQUESTS.inc()

        try:
            reader = easyocr.Reader([settings.OCR_LANGUAGE or 'en'], gpu=False)

            with OCR_DURATION.time():
                results = reader.readtext(image_bytes)

            extracted = [(text.strip(), prob) for _, text, prob in results if prob > settings.OCR_CONFIDENCE_THRESHOLD]
            logger.debug(f"Extracted text with confidence: {extracted}")
            return extracted
        except Exception as e:
            error_type = type(e).__name__
            OCR_ERRORS.labels(error_type=error_type).inc()
            logger.error(f"OCR extraction failed: {str(e)}")
            raise ValueError(f"OCR extraction failed: {str(e)}")
