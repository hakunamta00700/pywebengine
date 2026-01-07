"""
키보드 제어 모듈
"""

import pyautogui
from typing import Optional, List
import logging

logger = logging.getLogger("mcp_desktop.keyboard")


class KeyboardController:
    """키보드 제어 클래스"""
    
    def __init__(self):
        """키보드 컨트롤러 초기화"""
        # 기본 동작 속도 설정
        pyautogui.PAUSE = 0.1
    
    def type(self, text: str, interval: float = 0.0) -> dict:
        """
        텍스트 입력
        
        Args:
            text: 입력할 텍스트
            interval: 각 문자 입력 간 간격 (초)
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"텍스트 입력: {text[:50]}...")  # 처음 50자만 로그
            return {"success": True, "text_length": len(text)}
        except Exception as e:
            logger.error(f"텍스트 입력 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def press(self, key: str, presses: int = 1, interval: float = 0.0) -> dict:
        """
        키 누르기
        
        Args:
            key: 키 이름 (예: "enter", "tab", "ctrl", "alt")
            presses: 누르는 횟수
            interval: 각 키 입력 간 간격 (초)
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            logger.info(f"키 누르기: {key}, 횟수={presses}")
            return {"success": True, "key": key, "presses": presses}
        except Exception as e:
            logger.error(f"키 누르기 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def hotkey(self, *keys: str) -> dict:
        """
        단축키 조합 입력
        
        Args:
            *keys: 키 조합 (예: "ctrl", "c")
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"단축키 입력: {'+'.join(keys)}")
            return {"success": True, "keys": list(keys)}
        except Exception as e:
            logger.error(f"단축키 입력 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def key_down(self, key: str) -> dict:
        """
        키 누르기 (떼지 않음)
        
        Args:
            key: 키 이름
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.keyDown(key)
            logger.info(f"키 누르기 (유지): {key}")
            return {"success": True, "key": key}
        except Exception as e:
            logger.error(f"키 누르기 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def key_up(self, key: str) -> dict:
        """
        키 떼기
        
        Args:
            key: 키 이름
        
        Returns:
            작업 결과 딕셔너리
        """
        try:
            pyautogui.keyUp(key)
            logger.info(f"키 떼기: {key}")
            return {"success": True, "key": key}
        except Exception as e:
            logger.error(f"키 떼기 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_keyboard_controller = None


def get_keyboard_controller() -> KeyboardController:
    """키보드 컨트롤러 싱글톤 인스턴스 반환"""
    global _keyboard_controller
    if _keyboard_controller is None:
        _keyboard_controller = KeyboardController()
    return _keyboard_controller

