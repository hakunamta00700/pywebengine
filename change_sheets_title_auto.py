"""
크롬 브라우저에서 구글 스프레드시트를 찾고 제목을 변경하는 스크립트
"""

import sys
import time
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_desktop.window import get_window_controller
from src.mcp_desktop.mouse import get_mouse_controller
from src.mcp_desktop.keyboard import get_keyboard_controller
from src.mcp_desktop.screen_indexer import get_screen_indexer

def main():
    """메인 함수"""
    print("크롬 브라우저 찾는 중...")
    
    # 윈도우 컨트롤러 가져오기
    window = get_window_controller()
    mouse = get_mouse_controller()
    keyboard = get_keyboard_controller()
    screen_indexer = get_screen_indexer()
    
    # 크롬 브라우저 찾기
    result = window.find_window(title="Chrome")
    if not result.get("success") or not result.get("windows"):
        # 다른 제목으로 시도
        result = window.find_window(title="Google")
        if not result.get("success") or not result.get("windows"):
            # 스프레드시트가 포함된 윈도우 찾기
            result = window.find_window(title="스프레드시트")
            if not result.get("success") or not result.get("windows"):
                print("크롬 브라우저를 찾을 수 없습니다.")
                return
    
    chrome_windows = result["windows"]
    print(f"크롬 브라우저 {len(chrome_windows)}개 발견")
    
    # 스프레드시트가 포함된 윈도우 찾기
    sheets_window = None
    for win in chrome_windows:
        if "스프레드시트" in win["title"] or "Sheets" in win["title"]:
            sheets_window = win
            break
    
    if not sheets_window:
        sheets_window = chrome_windows[0]
    
    hwnd = sheets_window["hwnd"]
    print(f"크롬 윈도우 활성화: {sheets_window['title']}")
    
    # 윈도우 활성화
    activate_result = window.activate_window(hwnd)
    if not activate_result.get("success"):
        print(f"윈도우 활성화 실패: {activate_result.get('error')}")
        return
    
    time.sleep(1)  # 윈도우 활성화 대기
    
    # 윈도우 정보 가져오기
    print("윈도우 정보 가져오는 중...")
    window_info = window.get_window_info(hwnd)
    if not window_info.get("success"):
        print("윈도우 정보를 가져올 수 없습니다.")
        return
    
    win_pos = window_info["window"]["position"]
    # 상단 중앙 영역 클릭 (제목 영역)
    # 구글 스프레드시트의 제목은 보통 상단 중앙에 있습니다
    title_x = win_pos["left"] + win_pos["width"] // 2
    title_y = win_pos["top"] + 100  # 상단에서 약간 아래 (제목 영역)
    
    print(f"제목 영역 클릭: ({title_x}, {title_y})")
    print("3초 후 시작합니다...")
    time.sleep(3)  # 사용자가 준비할 시간
    
    # 제목 영역 더블 클릭하여 편집 모드로 전환
    mouse.click(x=title_x, y=title_y, clicks=2)
    time.sleep(0.5)
    
    # 전체 선택 후 새 제목 입력
    keyboard.hotkey("ctrl", "a")
    time.sleep(0.2)
    keyboard.type("안녕하세요")
    time.sleep(0.5)
    keyboard.press("enter")
    
    print("제목 변경 완료!")

if __name__ == "__main__":
    main()

