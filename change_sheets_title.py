"""
Google Sheets 제목 변경 스크립트
크롬 브라우저에서 구글 스프레드시트의 제목을 "안녕하세요"로 변경
"""

import time
from src.mcp_desktop.window import get_window_controller
from src.mcp_desktop.mouse import get_mouse_controller
from src.mcp_desktop.keyboard import get_keyboard_controller


def change_sheets_title(new_title="안녕하세요"):
    """Google Sheets 제목 변경"""
    print("=" * 60)
    print("Google Sheets 제목 변경")
    print("=" * 60)
    
    # 1. Chrome 창 찾기
    print("\n1. Chrome 창 찾는 중...")
    window = get_window_controller()
    result = window.find_window(title="Chrome")
    
    if not result.get("success") or not result.get("windows"):
        print("Chrome 창을 찾을 수 없습니다.")
        return False
    
    # Google Sheets가 열린 창 찾기
    sheets_window = None
    for w in result["windows"]:
        if "Google Sheets" in w["title"] or "스프레드시트" in w["title"]:
            sheets_window = w
            break
    
    if not sheets_window:
        print("Google Sheets 창을 찾을 수 없습니다.")
        print("열려있는 Chrome 창:")
        for w in result["windows"]:
            print(f"  - {w['title']}")
        return False
    
    print(f"Google Sheets 창 발견: {sheets_window['title']}")
    
    # 2. Chrome 창 활성화
    print("\n2. Chrome 창 활성화 중...")
    activate_result = window.activate_window(sheets_window["hwnd"])
    if not activate_result.get("success"):
        print(f"창 활성화 실패: {activate_result.get('error')}")
        # 이미 활성화되어 있을 수 있으므로 계속 진행
    else:
        print("창 활성화 완료")
    
    time.sleep(1)  # 창이 활성화될 시간 대기
    
    # 3. 마우스 및 키보드 컨트롤러
    mouse = get_mouse_controller()
    keyboard = get_keyboard_controller()
    
    # 4. Google Sheets 제목 영역 클릭
    # 제목은 보통 화면 왼쪽 상단에 있습니다
    # Chrome 창의 위치를 기준으로 제목 영역 계산
    window_pos = sheets_window.get("position", {})
    window_left = window_pos.get("left", 0)
    window_top = window_pos.get("top", 0)
    
    # 제목 영역은 보통 창의 왼쪽 상단에서 약간 아래쪽에 있습니다
    # 브라우저 탭 아래, 스프레드시트 영역의 왼쪽 상단
    title_x = window_left + 100  # 창 왼쪽에서 약 100픽셀
    title_y = window_top + 150   # 창 위에서 약 150픽셀 (탭 아래)
    
    print(f"\n3. 제목 영역 클릭 중... (좌표: {title_x}, {title_y})")
    
    # 제목 영역을 더블 클릭하여 편집 모드로 진입
    click_result = mouse.click(x=title_x, y=title_y, button="left", clicks=2, interval=0.1)
    
    if not click_result.get("success"):
        print(f"클릭 실패: {click_result.get('error')}")
        # 다른 위치 시도
        print("다른 위치 시도 중...")
        title_x = window_left + 150
        title_y = window_top + 120
        click_result = mouse.click(x=title_x, y=title_y, button="left", clicks=2, interval=0.1)
    
    time.sleep(0.5)
    
    # 5. 기존 텍스트 선택 및 새 제목 입력
    print(f"\n4. 제목을 '{new_title}'로 변경 중...")
    
    # 기존 텍스트 전체 선택
    keyboard.hotkey("ctrl", "a")
    time.sleep(0.2)
    
    # 새 제목 입력
    keyboard.type(new_title)
    time.sleep(0.3)
    
    # Enter로 완료
    keyboard.press("enter")
    time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("제목 변경 완료!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        change_sheets_title("안녕하세요")
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

