"""
간단한 Google Sheets 화면 변경 데모
크롬에서 구글 스프레드시트가 열려있는 상태에서 실행하세요.
"""

import time
from src.mcp_desktop.window import get_window_controller
from src.mcp_desktop.mouse import get_mouse_controller
from src.mcp_desktop.keyboard import get_keyboard_controller


def main():
    """간단한 Google Sheets 화면 변경 데모"""
    print("Google Sheets 화면 변경 데모")
    print("-" * 50)
    
    # Chrome 창 찾기 및 활성화
    window = get_window_controller()
    result = window.find_window(title="Chrome")
    
    if result.get("success") and result.get("windows"):
        chrome_window = result["windows"][0]
        print(f"Chrome 창 발견: {chrome_window['title']}")
        
        # 창 활성화
        window.activate_window(chrome_window["hwnd"])
        print("Chrome 창 활성화 완료")
        time.sleep(1)
    else:
        print("Chrome 창을 찾을 수 없습니다.")
        print("Chrome에서 Google Sheets를 열어주세요.")
        return
    
    # 마우스 및 키보드 컨트롤러
    mouse = get_mouse_controller()
    keyboard = get_keyboard_controller()
    
    print("\n3초 후 자동화를 시작합니다...")
    time.sleep(3)
    
    # 예제 1: 아래로 스크롤
    print("\n[1] 아래로 스크롤")
    mouse.scroll(clicks=5)
    time.sleep(1)
    
    # 예제 2: 오른쪽으로 이동 (화살표 키)
    print("[2] 오른쪽으로 이동")
    for _ in range(3):
        keyboard.press("right")
        time.sleep(0.2)
    time.sleep(1)
    
    # 예제 3: 아래로 이동
    print("[3] 아래로 이동")
    for _ in range(3):
        keyboard.press("down")
        time.sleep(0.2)
    time.sleep(1)
    
    # 예제 4: 맨 위로 이동 (Ctrl+Home)
    print("[4] 맨 위로 이동 (Ctrl+Home)")
    keyboard.hotkey("ctrl", "home")
    time.sleep(1)
    
    # 예제 5: 다음 시트로 전환 (Ctrl+PageDown)
    print("[5] 다음 시트로 전환 (Ctrl+PageDown)")
    keyboard.hotkey("ctrl", "pagedown")
    time.sleep(1)
    
    # 예제 6: 이전 시트로 전환 (Ctrl+PageUp)
    print("[6] 이전 시트로 전환 (Ctrl+PageUp)")
    keyboard.hotkey("ctrl", "pageup")
    time.sleep(1)
    
    print("\n완료!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단되었습니다.")
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()

