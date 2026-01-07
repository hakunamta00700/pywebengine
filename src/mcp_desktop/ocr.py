"""
OCR (Optical Character Recognition) 모듈
"""

import logging
from typing import Optional
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger("mcp_desktop.ocr")

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract가 설치되지 않았습니다. OCR 기능을 사용할 수 없습니다.")


class OCRController:
    """OCR 제어 클래스"""

    def __init__(self):
        """OCR 컨트롤러 초기화"""
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract OCR이 설치되지 않았습니다.")

    def extract_text_from_image(
        self,
        image_base64: str,
        lang: str = "kor+eng",
    ) -> dict:
        """
        이미지에서 텍스트 추출

        Args:
            image_base64: Base64 인코딩된 이미지
            lang: OCR 언어 (기본값: "kor+eng" - 한국어+영어)

        Returns:
            추출된 텍스트 딕셔너리
        """
        if not TESSERACT_AVAILABLE:
            return {"success": False, "error": "Tesseract OCR이 설치되지 않았습니다."}

        try:
            # Base64 디코딩
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))

            # OCR 수행
            text = pytesseract.image_to_string(image, lang=lang)
            text = text.strip()

            logger.info(f"OCR 텍스트 추출: {len(text)} 문자")
            return {
                "success": True,
                "text": text,
                "length": len(text),
                "language": lang,
                "word_count": len([w for w in text.split() if w]),
            }
        except Exception as e:
            logger.error(f"OCR 텍스트 추출 실패: {e}")
            return {"success": False, "error": str(e)}

    def extract_text_from_screenshot(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        lang: str = "kor+eng",
    ) -> dict:
        """
        스크린샷에서 텍스트 추출

        Args:
            x: 시작 X 좌표 (None이면 전체 화면)
            y: 시작 Y 좌표 (None이면 전체 화면)
            width: 너비 (None이면 전체 화면)
            height: 높이 (None이면 전체 화면)
            lang: OCR 언어

        Returns:
            추출된 텍스트 딕셔너리
        """
        if not TESSERACT_AVAILABLE:
            return {"success": False, "error": "Tesseract OCR이 설치되지 않았습니다."}

        try:
            import pyautogui

            # 스크린샷 캡처
            if (
                x is not None
                and y is not None
                and width is not None
                and height is not None
            ):
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                screenshot = pyautogui.screenshot()

            # OCR 수행
            text = pytesseract.image_to_string(screenshot, lang=lang)
            text = text.strip()

            logger.info(f"스크린샷 OCR: {len(text)} 문자")
            return {
                "success": True,
                "text": text,
                "length": len(text),
                "language": lang,
                "region": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                }
                if x is not None
                else None,
            }
        except Exception as e:
            logger.error(f"스크린샷 OCR 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_ocr_controller = None


def get_ocr_controller() -> OCRController:
    """OCR 컨트롤러 싱글톤 인스턴스 반환"""
    global _ocr_controller
    if _ocr_controller is None:
        _ocr_controller = OCRController()
    return _ocr_controller
