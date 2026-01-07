"""
마우스 제어 모듈
"""

import pyautogui
from typing import Optional, Tuple
import logging

logger = logging.getLogger("mcp_desktop.mouse")


class MouseController:
    """마우스 제어 클래스"""
    
    def __init__(self):
        """마우스 컨트롤러 초기화"""
        # Fail-safe 활성화: 마우스가 화면 모서리로 이동하면 모든 작업 중단
        pyautogui.FAILSAFE = True
        # 기본 동작 속도 설정
        pyautogui.PAUSE = 0.1
    
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.0,
    ) -> dict:
        """
        마우스 클릭
        
        Args:
            x: X 좌표 (None이면 현재 위치)
            y: Y 좌표 (None이면 현재 위치)
            button: 클릭 버튼 ("left", "right", "middle")
            clicks: 클릭 횟수
            interval: 클릭 간 간격 (초)
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
                position = (x, y)
            else:
                pyautogui.click(button=button, clicks=clicks, interval=interval)
                position = pyautogui.position()
            
            logger.info(f"마우스 클릭: {position}, 버튼={button}, 횟수={clicks}")
            return {
                "success": True,
                "position": position,
                "button": button,
                "clicks": clicks,
            }
        except Exception as e:
            logger.error(f"마우스 클릭 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def move(self, x: int, y: int, duration: float = 0.0) -> dict:
        """
        마우스 이동
        
        Args:
            x: X 좌표
            y: Y 좌표
            duration: 이동 시간 (초, 0이면 즉시 이동)
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"마우스 이동: ({x}, {y}), duration={duration}")
            return {"success": True, "position": (x, y)}
        except Exception as e:
            logger.error(f"마우스 이동 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5,
        button: str = "left",
    ) -> dict:
        """
        마우스 드래그
        
        Args:
            start_x: 시작 X 좌표
            start_y: 시작 Y 좌표
            end_x: 끝 X 좌표
            end_y: 끝 Y 좌표
            duration: 드래그 시간 (초)
            button: 드래그 버튼 ("left", "right", "middle")
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.drag(start_x, start_y, end_x - start_x, end_y - start_y, duration=duration, button=button)
            logger.info(f"마우스 드래그: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            return {
                "success": True,
                "start": (start_x, start_y),
                "end": (end_x, end_y),
            }
        except Exception as e:
            logger.error(f"마우스 드래그 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def scroll(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 3) -> dict:
        """
        마우스 스크롤
        
        Args:
            x: X 좌표 (None이면 현재 위치)
            y: Y 좌표 (None이면 현재 위치)
            clicks: 스크롤 클릭 수 (양수=아래, 음수=위)
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x=x, y=y)
                position = (x, y)
            else:
                pyautogui.scroll(clicks)
                position = pyautogui.position()
            
            logger.info(f"마우스 스크롤: {position}, clicks={clicks}")
            return {"success": True, "position": position, "clicks": clicks}
        except Exception as e:
            logger.error(f"마우스 스크롤 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_position(self) -> dict:
        """
        현재 마우스 위치 조회
        
        Returns:
            현재 위치 정보 딕셔너리
        """
        try:
            x, y = pyautogui.position()
            return {"success": True, "position": (x, y)}
        except Exception as e:
            logger.error(f"마우스 위치 조회 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_mouse_controller = None


def get_mouse_controller() -> MouseController:
    """마우스 컨트롤러 싱글톤 인스턴스 반환"""
    global _mouse_controller
    if _mouse_controller is None:
        _mouse_controller = MouseController()
    return _mouse_controller

