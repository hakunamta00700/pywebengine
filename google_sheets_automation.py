"""
Google Sheets 자동화 스크립트
크롬 브라우저에서 구글 스프레드시트 화면을 변경하는 예제
"""

import time
from src.mcp_desktop.window import get_window_controller
from src.mcp_desktop.mouse import get_mouse_controller
from src.mcp_desktop.keyboard import get_keyboard_controller
from src.mcp_desktop.screenshot import get_screenshot_controller


def find_chrome_window():
    """Chrome 브라우저 창 찾기"""
    window = get_window_controller()
    
    # Chrome 창 찾기 (Google Sheets가 열려있는 경우)
    result = window.find_window(title="Google Sheets")
    if not result.get("success") or not result.get("windows"):
        # Google Sheets가 제목에 없는 경우 Chrome 창 찾기
        result = window.find_window(title="Chrome")
    
    if result.get("success") and result.get("windows"):
        windows = result["windows"]
        print(f"찾은 창: {len(windows)}개")
        for w in windows:
            print(f"  - {w['title']} (hwnd={w['hwnd']})")
        return windows[0]  # 첫 번째 창 반환
    else:
        print("Chrome 창을 찾을 수 없습니다.")
        return None


def activate_chrome_window(window_info):
    """Chrome 창 활성화"""
    window = get_window_controller()
    result = window.activate_window(window_info["hwnd"])
    if result.get("success"):
        print(f"창 활성화: {result.get('title')}")
        time.sleep(1)  # 창이 활성화될 시간 대기
        return True
    else:
        print(f"창 활성화 실패: {result.get('error')}")
        return False


def change_sheet_screen(action="scroll"):
    """
    Google Sheets 화면 변경
    
    Args:
        action: 수행할 작업
            - "scroll_down": 아래로 스크롤
            - "scroll_up": 위로 스크롤
            - "scroll_right": 오른쪽으로 스크롤
            - "scroll_left": 왼쪽으로 스크롤
            - "switch_sheet": 다음 시트로 전환 (Ctrl+PageDown)
            - "go_to_cell": 특정 셀로 이동 (Ctrl+G)
            - "zoom_in": 확대 (Ctrl+Plus)
            - "zoom_out": 축소 (Ctrl+Minus)
    """
    mouse = get_mouse_controller()
    keyboard = get_keyboard_controller()
    
    print(f"\n=== Google Sheets 화면 변경: {action} ===")
    
    if action == "scroll_down":
        # 아래로 스크롤
        print("아래로 스크롤 중...")
        mouse.scroll(clicks=5)  # 5칸 아래로 스크롤
        time.sleep(0.5)
        
    elif action == "scroll_up":
        # 위로 스크롤
        print("위로 스크롤 중...")
        mouse.scroll(clicks=-5)  # 5칸 위로 스크롤
        time.sleep(0.5)
        
    elif action == "scroll_right":
        # 오른쪽으로 스크롤 (Shift + 마우스 휠)
        print("오른쪽으로 스크롤 중...")
        # Google Sheets에서 가로 스크롤은 Shift + 마우스 휠 또는 화살표 키 사용
        keyboard.hotkey("shift", "right")
        time.sleep(0.3)
        keyboard.hotkey("shift", "right")
        time.sleep(0.3)
        keyboard.hotkey("shift", "right")
        time.sleep(0.5)
        
    elif action == "scroll_left":
        # 왼쪽으로 스크롤
        print("왼쪽으로 스크롤 중...")
        keyboard.hotkey("shift", "left")
        time.sleep(0.3)
        keyboard.hotkey("shift", "left")
        time.sleep(0.3)
        keyboard.hotkey("shift", "left")
        time.sleep(0.5)
        
    elif action == "switch_sheet":
        # 다음 시트로 전환 (Ctrl+PageDown)
        print("다음 시트로 전환 중...")
        keyboard.hotkey("ctrl", "pagedown")
        time.sleep(0.5)
        
    elif action == "switch_sheet_prev":
        # 이전 시트로 전환 (Ctrl+PageUp)
        print("이전 시트로 전환 중...")
        keyboard.hotkey("ctrl", "pageup")
        time.sleep(0.5)
        
    elif action == "go_to_cell":
        # 특정 셀로 이동 (Ctrl+G)
        print("셀 이동 대화상자 열기...")
        keyboard.hotkey("ctrl", "g")
        time.sleep(0.5)
        # 예: A100 셀로 이동
        keyboard.type("A100")
        time.sleep(0.3)
        keyboard.press("enter")
        time.sleep(0.5)
        
    elif action == "go_to_top":
        # 맨 위로 이동 (Ctrl+Home)
        print("맨 위로 이동 중...")
        keyboard.hotkey("ctrl", "home")
        time.sleep(0.5)
        
    elif action == "zoom_in":
        # 확대 (Ctrl+Plus)
        print("확대 중...")
        keyboard.hotkey("ctrl", "+")
        time.sleep(0.5)
        
    elif action == "zoom_out":
        # 축소 (Ctrl+Minus)
        print("축소 중...")
        keyboard.hotkey("ctrl", "-")
        time.sleep(0.5)
        
    elif action == "zoom_reset":
        # 확대/축소 리셋 (Ctrl+0)
        print("확대/축소 리셋 중...")
        keyboard.hotkey("ctrl", "0")
        time.sleep(0.5)
        
    print("완료!")


def demo_google_sheets_automation():
    """Google Sheets 자동화 데모"""
    print("=" * 60)
    print("Google Sheets 자동화 데모")
    print("=" * 60)
    
    # 1. Chrome 창 찾기
    print("\n1. Chrome 창 찾는 중...")
    window_info = find_chrome_window()
    if not window_info:
        print("Chrome 창을 찾을 수 없습니다. Chrome에서 Google Sheets를 열어주세요.")
        return
    
    # 2. Chrome 창 활성화
    print("\n2. Chrome 창 활성화 중...")
    if not activate_chrome_window(window_info):
        return
    
    # 3. 잠시 대기 (사용자가 준비할 시간)
    print("\n3초 후 자동화를 시작합니다...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # 4. 다양한 화면 변경 작업 수행
    actions = [
        ("scroll_down", "아래로 스크롤"),
        ("scroll_right", "오른쪽으로 스크롤"),
        ("go_to_top", "맨 위로 이동"),
        ("zoom_in", "확대"),
        ("zoom_out", "축소"),
        ("zoom_reset", "확대/축소 리셋"),
    ]
    
    print("\n" + "=" * 60)
    print("화면 변경 작업 시작")
    print("=" * 60)
    
    for action, description in actions:
        print(f"\n작업: {description}")
        change_sheet_screen(action)
        time.sleep(1)  # 각 작업 사이 대기
    
    print("\n" + "=" * 60)
    print("모든 작업 완료!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_google_sheets_automation()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

