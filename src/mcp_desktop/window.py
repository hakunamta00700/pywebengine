"""
윈도우 관리 모듈
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("mcp_desktop.window")

try:
    import win32gui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("pywin32가 설치되지 않았습니다. 윈도우 관리 기능이 제한됩니다.")


class WindowController:
    """윈도우 제어 클래스"""
    
    def __init__(self):
        """윈도우 컨트롤러 초기화"""
        if not WIN32_AVAILABLE:
            logger.warning("Windows 환경이 아니거나 pywin32가 설치되지 않았습니다.")
    
    def find_window(self, title: Optional[str] = None, class_name: Optional[str] = None) -> dict:
        """
        윈도우 찾기
        
        Args:
            title: 윈도우 제목 (부분 일치)
            class_name: 윈도우 클래스명
        
        Returns:
            찾은 윈도우 정보 딕셔너리
        """
        if not WIN32_AVAILABLE:
            return {"success": False, "error": "Windows 환경이 필요합니다."}
        
        try:
            def enum_handler(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    window_class = win32gui.GetClassName(hwnd)
                    
                    match = True
                    if title and title.lower() not in window_title.lower():
                        match = False
                    if class_name and class_name.lower() not in window_class.lower():
                        match = False
                    
                    if match:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            "hwnd": hwnd,
                            "title": window_title,
                            "class": window_class,
                            "position": {
                                "left": rect[0],
                                "top": rect[1],
                                "right": rect[2],
                                "bottom": rect[3],
                                "width": rect[2] - rect[0],
                                "height": rect[3] - rect[1],
                            },
                        })
            
            windows = []
            win32gui.EnumWindows(enum_handler, windows)
            
            logger.info(f"윈도우 찾기: title={title}, class={class_name}, 결과={len(windows)}개")
            return {"success": True, "windows": windows}
        except Exception as e:
            logger.error(f"윈도우 찾기 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def activate_window(self, hwnd: int) -> dict:
        """
        윈도우 활성화
        
        Args:
            hwnd: 윈도우 핸들
        
        Returns:
            작업 결과 딕셔너리
        """
        if not WIN32_AVAILABLE:
            return {"success": False, "error": "Windows 환경이 필요합니다."}
        
        try:
            # 윈도우를 포그라운드로 가져오기
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            
            title = win32gui.GetWindowText(hwnd)
            logger.info(f"윈도우 활성화: {title} (hwnd={hwnd})")
            return {"success": True, "hwnd": hwnd, "title": title}
        except Exception as e:
            logger.error(f"윈도우 활성화 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_window_info(self, hwnd: int) -> dict:
        """
        윈도우 정보 조회
        
        Args:
            hwnd: 윈도우 핸들
        
        Returns:
            윈도우 정보 딕셔너리
        """
        if not WIN32_AVAILABLE:
            return {"success": False, "error": "Windows 환경이 필요합니다."}
        
        try:
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            
            # 프로세스 정보
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            info = {
                "hwnd": hwnd,
                "title": title,
                "class": class_name,
                "process_id": pid,
                "visible": is_visible,
                "position": {
                    "left": rect[0],
                    "top": rect[1],
                    "right": rect[2],
                    "bottom": rect[3],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1],
                },
            }
            
            logger.info(f"윈도우 정보 조회: {title} (hwnd={hwnd})")
            return {"success": True, "window": info}
        except Exception as e:
            logger.error(f"윈도우 정보 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_window_rect(self, hwnd: int) -> dict:
        """
        윈도우 영역 좌표 조회 (스크린샷용)
        
        Args:
            hwnd: 윈도우 핸들
        
        Returns:
            윈도우 영역 좌표 딕셔너리
        """
        if not WIN32_AVAILABLE:
            return {"success": False, "error": "Windows 환경이 필요합니다."}
        
        try:
            rect = win32gui.GetWindowRect(hwnd)
            return {
                "success": True,
                "hwnd": hwnd,
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
                "width": rect[2] - rect[0],
                "height": rect[3] - rect[1],
            }
        except Exception as e:
            logger.error(f"윈도우 영역 조회 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_window_controller = None


def get_window_controller() -> WindowController:
    """윈도우 컨트롤러 싱글톤 인스턴스 반환"""
    global _window_controller
    if _window_controller is None:
        _window_controller = WindowController()
    return _window_controller

