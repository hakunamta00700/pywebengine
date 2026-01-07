"""
PySide6 QWebEngine을 사용한 ChatGPT 스타일 채팅 데스크톱 애플리케이션
"""

import sys
import os
import base64
import json
import asyncio
from pathlib import Path
from PySide6.QtCore import QUrl, QObject, Slot, Signal, QByteArray, QBuffer, QIODevice
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel

# MCP 데스크탑 모듈 import
try:
    from src.mcp_desktop.tools import call_tool, get_all_tools
    from src.mcp_desktop.screenshot import get_screenshot_controller

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("경고: MCP 데스크탑 모듈을 찾을 수 없습니다. 일부 기능이 제한될 수 있습니다.")


class ChatBridge(QObject):
    """Python과 JavaScript 간의 통신을 위한 Bridge 클래스"""

    # 시그널: JavaScript에서 메시지 전송 시 발생
    messageSent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chat_window = None

    def set_chat_window(self, chat_window):
        """ChatWindow 참조 설정"""
        self._chat_window = chat_window

    @Slot(str)
    def onMessageSent(self, message: str):
        """JavaScript에서 메시지 전송 시 호출되는 슬롯"""
        if self._chat_window:
            self._chat_window.handle_user_message(message)

    @Slot()
    def onReady(self):
        """JavaScript 초기화 완료 시 호출되는 슬롯"""
        pass

    @Slot(str, str)
    def callMCPTool(self, tool_name: str, arguments_json: str):
        """MCP 도구 호출 (비동기)"""
        if not MCP_AVAILABLE:
            self._send_tool_result({"error": "MCP 모듈을 사용할 수 없습니다."})
            return

        try:
            arguments = json.loads(arguments_json) if arguments_json else {}

            # 비동기로 도구 호출
            async def call_async():
                try:
                    result = await call_tool(tool_name, arguments)
                    result_dict = json.loads(result)
                    self._send_tool_result(result_dict)
                except Exception as e:
                    self._send_tool_result({"error": str(e)})

            # 이벤트 루프에서 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(call_async())
            loop.close()

        except Exception as e:
            self._send_tool_result({"error": f"도구 호출 오류: {str(e)}"})

    @Slot(result=str)
    def getMCPTools(self) -> str:
        """사용 가능한 MCP 도구 목록 반환"""
        if not MCP_AVAILABLE:
            return json.dumps({"error": "MCP 모듈을 사용할 수 없습니다."})

        try:
            tools = get_all_tools()
            tools_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
                for tool in tools
            ]
            return json.dumps({"tools": tools_list}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _send_tool_result(self, result: dict):
        """도구 호출 결과를 JavaScript로 전달"""
        if self._chat_window and self._chat_window.web_view:
            result_json = json.dumps(result, ensure_ascii=False)
            script = f"window.onMCPToolResult({repr(result_json)});"
            self._chat_window.web_view.page().runJavaScript(script)

    @Slot()
    def captureScreen(self):
        """모니터 화면을 캡쳐하고 JavaScript로 결과 전달"""
        try:
            print("화면 캡쳐 시작...")
            # 기본 화면 캡쳐
            screen = QApplication.primaryScreen()
            if screen is None:
                print("화면을 찾을 수 없습니다.")
                self._send_capture_result("")
                return

            print(f"화면 크기: {screen.size()}")
            print(f"화면 지오메트리: {screen.geometry()}")

            # Windows에서 더 안정적인 화면 캡쳐 방법 시도
            # 먼저 grabWindow(0) 시도
            pixmap = screen.grabWindow(0)

            # Windows에서 실패할 경우 geometry를 사용한 캡쳐 시도
            if pixmap.isNull() or pixmap.width() == 0 or pixmap.height() == 0:
                print("grabWindow(0) 실패, geometry 사용 시도...")
                geometry = screen.geometry()
                pixmap = screen.grabWindow(
                    0, geometry.x(), geometry.y(), geometry.width(), geometry.height()
                )

            if pixmap.isNull():
                print("화면 캡쳐 실패: pixmap이 null입니다.")
                self._send_capture_result("")
                return

            print(f"캡쳐된 이미지 크기: {pixmap.width()}x{pixmap.height()}")

            # QPixmap을 QByteArray로 변환 (PNG 형식)
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            success = pixmap.save(buffer, "PNG")
            buffer.close()

            if not success:
                print("이미지 저장 실패")
                self._send_capture_result("")
                return

            print(f"이미지 데이터 크기: {len(byte_array)} bytes")

            # base64 인코딩
            base64_data = base64.b64encode(byte_array.data()).decode("utf-8")
            print(f"Base64 데이터 길이: {len(base64_data)}")

            # JavaScript로 결과 전달
            self._send_capture_result(base64_data)
            print("화면 캡쳐 완료")
        except Exception as e:
            print(f"화면 캡쳐 오류: {e}")
            import traceback

            traceback.print_exc()
            self._send_capture_result("")

    def _send_capture_result(self, base64_data: str):
        """캡쳐 결과를 JavaScript로 전달"""
        if self._chat_window and self._chat_window.web_view:
            # JavaScript 함수 호출
            script = f"window.onScreenCaptureComplete({repr(base64_data)});"
            self._chat_window.web_view.page().runJavaScript(script)


class ChatWindow(QMainWindow):
    """채팅 메인 윈도우 (QWebEngine 사용)"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setWindowTitle("AI Desktop - 채팅")
        self.setGeometry(100, 100, 800, 600)

    def setup_ui(self):
        """UI 설정"""
        # WebEngineView 생성
        self.web_view = QWebEngineView()

        # 프로필 설정
        profile = self.web_view.page().profile()

        # User-Agent 설정
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        profile.setHttpUserAgent(user_agent)

        # JavaScript 설정
        page = self.web_view.page()
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )

        # WebChannel 설정 (Python-JavaScript 통신)
        self.channel = QWebChannel()
        self.bridge = ChatBridge()
        self.bridge.set_chat_window(self)
        self.channel.registerObject("pyBridge", self.bridge)
        page.setWebChannel(self.channel)

        # index.html 로드
        html_path = Path(__file__).parent / "index.html"
        if html_path.exists():
            file_url = QUrl.fromLocalFile(str(html_path.absolute()))
            self.web_view.setUrl(file_url)
        else:
            # index.html이 없으면 기본 HTML 콘텐츠 사용
            html_content = """
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>index.html 파일을 찾을 수 없습니다.</h1>
                <p>프로젝트 루트에 index.html 파일이 있는지 확인하세요.</p>
            </body>
            </html>
            """
            self.web_view.setHtml(html_content)

        self.setCentralWidget(self.web_view)

    def handle_user_message(self, message: str):
        """사용자 메시지 처리"""
        if not message.strip():
            return

        # 간단한 명령어 파싱 (향후 LLM 통합 시 대체)
        message_lower = message.lower().strip()

        # 스크린샷 명령
        if message_lower in ["스크린샷", "screenshot", "화면 캡처", "캡처"]:
            if MCP_AVAILABLE:
                screenshot = get_screenshot_controller()
                result = screenshot.capture_full_screen()
                if result.get("success"):
                    # 스크린샷을 JavaScript로 전달
                    script = f"window.onScreenCaptureComplete({repr(result['image_base64'])});"
                    self.web_view.page().runJavaScript(script)
                    self.add_ai_message("화면을 캡처했습니다.")
                else:
                    self.add_ai_message(
                        f"스크린샷 실패: {result.get('error', '알 수 없는 오류')}"
                    )
            else:
                self.add_ai_message("MCP 모듈을 사용할 수 없습니다.")
            return

        # 마우스 위치 조회
        if message_lower in ["마우스 위치", "mouse position", "마우스"]:
            if MCP_AVAILABLE:
                from src.mcp_desktop.mouse import get_mouse_controller

                mouse = get_mouse_controller()
                result = mouse.get_position()
                if result.get("success"):
                    pos = result["position"]
                    self.add_ai_message(f"현재 마우스 위치: ({pos[0]}, {pos[1]})")
                else:
                    self.add_ai_message(f"마우스 위치 조회 실패: {result.get('error')}")
            else:
                self.add_ai_message("MCP 모듈을 사용할 수 없습니다.")
            return

        # 화면 크기 조회
        if message_lower in ["화면 크기", "screen size", "해상도"]:
            if MCP_AVAILABLE:
                screenshot = get_screenshot_controller()
                result = screenshot.get_screen_size()
                if result.get("success"):
                    self.add_ai_message(
                        f"화면 크기: {result['width']}x{result['height']}"
                    )
                else:
                    self.add_ai_message(f"화면 크기 조회 실패: {result.get('error')}")
            else:
                self.add_ai_message("MCP 모듈을 사용할 수 없습니다.")
            return

        # 기본 응답 (향후 LLM 통합 시 대체)
        response = f"받은 메시지: {message}\n\n사용 가능한 명령어:\n- 스크린샷/화면 캡처\n- 마우스 위치\n- 화면 크기"
        self.add_ai_message(response)

    def add_ai_message(self, message: str):
        """AI 메시지를 채팅에 추가"""
        # JavaScript 함수 호출
        script = f"window.addAIMessage({repr(message)});"
        self.web_view.page().runJavaScript(script)


def main():
    """애플리케이션 진입점"""
    # QWebEngine 로깅 레벨 설정
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-logging")

    app = QApplication(sys.argv)

    # 애플리케이션 정보 설정
    app.setApplicationName("AI Desktop")
    app.setOrganizationName("AI Desktop")

    # 채팅 윈도우 생성 및 표시
    chat_window = ChatWindow()
    chat_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
