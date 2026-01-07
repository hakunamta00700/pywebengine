"""
스크린샷 캡처 모듈
"""

import pyautogui
import base64
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image
import logging

logger = logging.getLogger("mcp_desktop.screenshot")


class ScreenshotController:
    """스크린샷 제어 클래스"""
    
    def capture_full_screen(self, format: str = "PNG") -> dict:
        """
        전체 화면 캡처
        
        Args:
            format: 이미지 형식 ("PNG", "JPEG")
        
        Returns:
            작업 결과 딕셔너리 (base64 인코딩된 이미지 포함)
        """
        try:
            screenshot = pyautogui.screenshot()
            
            # 이미지를 바이트로 변환
            buffer = BytesIO()
            screenshot.save(buffer, format=format)
            image_bytes = buffer.getvalue()
            
            # Base64 인코딩
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # 해상도 정보
            width, height = screenshot.size
            
            logger.info(f"전체 화면 캡처: {width}x{height}, 형식={format}")
            return {
                "success": True,
                "image_base64": image_base64,
                "format": format.lower(),
                "width": width,
                "height": height,
            }
        except Exception as e:
            logger.error(f"전체 화면 캡처 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        format: str = "PNG",
    ) -> dict:
        """
        화면 영역 캡처
        
        Args:
            x: 시작 X 좌표
            y: 시작 Y 좌표
            width: 너비
            height: 높이
            format: 이미지 형식 ("PNG", "JPEG")
        
        Returns:
            작업 결과 딕셔너리 (base64 인코딩된 이미지 포함)
        """
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # 이미지를 바이트로 변환
            buffer = BytesIO()
            screenshot.save(buffer, format=format)
            image_bytes = buffer.getvalue()
            
            # Base64 인코딩
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            logger.info(f"영역 캡처: ({x}, {y}) {width}x{height}, 형식={format}")
            return {
                "success": True,
                "image_base64": image_base64,
                "format": format.lower(),
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        except Exception as e:
            logger.error(f"영역 캡처 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_screen_size(self) -> dict:
        """
        화면 크기 조회
        
        Returns:
            화면 크기 정보 딕셔너리
        """
        try:
            width, height = pyautogui.size()
            logger.info(f"화면 크기: {width}x{height}")
            return {"success": True, "width": width, "height": height}
        except Exception as e:
            logger.error(f"화면 크기 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_pixel_color(self, x: int, y: int) -> dict:
        """
        특정 좌표의 픽셀 색상 조회
        
        Args:
            x: X 좌표
            y: Y 좌표
        
        Returns:
            픽셀 색상 정보 딕셔너리 (RGB)
        """
        try:
            screenshot = pyautogui.screenshot()
            rgb = screenshot.getpixel((x, y))
            logger.info(f"픽셀 색상 조회: ({x}, {y}) = RGB{rgb}")
            return {
                "success": True,
                "position": (x, y),
                "rgb": rgb,
                "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            }
        except Exception as e:
            logger.error(f"픽셀 색상 조회 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_screenshot_controller = None


def get_screenshot_controller() -> ScreenshotController:
    """스크린샷 컨트롤러 싱글톤 인스턴스 반환"""
    global _screenshot_controller
    if _screenshot_controller is None:
        _screenshot_controller = ScreenshotController()
    return _screenshot_controller

