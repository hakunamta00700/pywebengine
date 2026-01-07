"""
PySide6 QWebEngine을 사용한 간단한 웹 브라우저 애플리케이션
"""

import sys
import os
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QToolBar,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlRequestInfo,
)


class CustomUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """HTTP 요청에 추가 헤더를 설정하는 인터셉터"""

    def __init__(self, web_view=None):
        super().__init__()
        self.web_view = web_view

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        """요청 인터셉트하여 추가 헤더 설정"""
        url = info.requestUrl()
        url_string = url.toString()

        # Accept 헤더
        info.setHttpHeader(
            b"Accept",
            b"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        )
        # Accept-Language 헤더
        info.setHttpHeader(b"Accept-Language", b"ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
        # Accept-Encoding 헤더
        info.setHttpHeader(b"Accept-Encoding", b"gzip, deflate, br, zstd")
        # Connection 헤더
        info.setHttpHeader(b"Connection", b"keep-alive")
        # Upgrade-Insecure-Requests 헤더
        info.setHttpHeader(b"Upgrade-Insecure-Requests", b"1")

        # Referer 헤더 동적 설정
        if self.web_view:
            current_url = self.web_view.url()
            if current_url.isValid() and not current_url.isEmpty():
                # 같은 도메인 내에서 이동하는 경우 Referer 설정
                if url.host() == current_url.host() or url.host().endswith(
                    "." + current_url.host()
                ):
                    info.setHttpHeader(b"Referer", current_url.toString().encode())
                # 쿠팡 도메인인 경우 메인 페이지를 Referer로 설정
                elif (
                    "coupang.com" in url_string
                    and "coupang.com" in current_url.toString()
                ):
                    info.setHttpHeader(b"Referer", b"https://www.coupang.com/")

        # Sec-Fetch-Dest 헤더
        if url_string.endswith((".css", ".js", ".png", ".jpg", ".gif", ".svg", ".ico")):
            info.setHttpHeader(
                b"Sec-Fetch-Dest",
                b"style"
                if url_string.endswith(".css")
                else b"script"
                if url_string.endswith(".js")
                else b"image",
            )
        else:
            info.setHttpHeader(b"Sec-Fetch-Dest", b"document")

        # Sec-Fetch-Mode 헤더
        info.setHttpHeader(b"Sec-Fetch-Mode", b"navigate")

        # Sec-Fetch-Site 헤더
        if self.web_view:
            current_url = self.web_view.url()
            if current_url.isValid() and not current_url.isEmpty():
                if url.host() == current_url.host():
                    info.setHttpHeader(b"Sec-Fetch-Site", b"same-origin")
                else:
                    info.setHttpHeader(b"Sec-Fetch-Site", b"cross-site")
            else:
                info.setHttpHeader(b"Sec-Fetch-Site", b"none")
        else:
            info.setHttpHeader(b"Sec-Fetch-Site", b"none")

        # Sec-Fetch-User 헤더
        info.setHttpHeader(b"Sec-Fetch-User", b"?1")

        # Cache-Control 헤더
        info.setHttpHeader(b"Cache-Control", b"max-age=0")

        # DNT (Do Not Track) 헤더 제거 - 일부 사이트가 봇으로 인식할 수 있음
        # info.setHttpHeader(b"DNT", b"1")  # 주석 처리


class BrowserWindow(QMainWindow):
    """웹 브라우저 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyWebEngine Browser")
        self.setGeometry(100, 100, 1200, 800)

        # 쿠팡 접근을 위한 대기 중인 URL
        self.pending_coupang_url = None

        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # 툴바 생성 (URL 입력 및 네비게이션)
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 뒤로 가기 버튼
        self.back_button = QPushButton("◀")
        self.back_button.setToolTip("뒤로 가기")
        self.back_button.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_button)

        # 앞으로 가기 버튼
        self.forward_button = QPushButton("▶")
        self.forward_button.setToolTip("앞으로 가기")
        self.forward_button.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_button)

        # 새로고침 버튼
        self.reload_button = QPushButton("⟳")
        self.reload_button.setToolTip("새로고침")
        self.reload_button.clicked.connect(self.reload_page)
        toolbar.addWidget(self.reload_button)

        # 홈 버튼
        self.home_button = QPushButton("🏠")
        self.home_button.setToolTip("홈")
        self.home_button.clicked.connect(self.go_home)
        toolbar.addWidget(self.home_button)

        toolbar.addSeparator()

        # URL 입력 필드
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL을 입력하세요 (예: https://www.google.com)")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # 이동 버튼
        self.go_button = QPushButton("이동")
        self.go_button.clicked.connect(self.navigate_to_url)
        toolbar.addWidget(self.go_button)

        # 웹 엔진 뷰 생성
        self.web_view = QWebEngineView()

        # 프로필 설정
        profile = self.web_view.page().profile()

        # User-Agent를 최신 Chrome 브라우저로 설정 (봇 차단 방지)
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        profile.setHttpUserAgent(user_agent)

        # 쿠키 및 저장소 활성화
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        profile.setPersistentStoragePath(profile.cachePath())

        # JavaScript 활성화 확인 (기본적으로 활성화되어 있음)
        page = self.web_view.page()
        settings = page.settings()
        settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(
            settings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
        # WebGL 및 Canvas 지원 (브라우저 핑거프린팅 우회)
        settings.setAttribute(settings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(settings.WebAttribute.Accelerated2dCanvasEnabled, True)
        # 플러그인 활성화
        settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
        # 이미지 자동 로드
        settings.setAttribute(settings.WebAttribute.AutoLoadImages, True)

        # URL 요청 인터셉터 설정 (추가 HTTP 헤더, web_view 참조 전달)
        interceptor = CustomUrlRequestInterceptor(web_view=self.web_view)
        profile.setUrlRequestInterceptor(interceptor)

        self.web_view.setUrl(QUrl("https://www.google.com"))

        # URL 변경 시 주소창 업데이트 및 네비게이션 버튼 상태 업데이트
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.web_view.urlChanged.connect(self.update_navigation_buttons)
        self.web_view.titleChanged.connect(self.update_window_title)

        # 페이지 로드 완료 시 쿠팡 대기 URL 처리
        self.web_view.loadFinished.connect(self.handle_coupang_navigation)

        main_layout.addWidget(self.web_view)

        # 초기 네비게이션 버튼 상태 설정
        self.update_navigation_buttons()

    def navigate_to_url(self):
        """URL 입력창의 주소로 이동"""
        url_text = self.url_bar.text().strip()

        # URL 형식이 아니면 검색 엔진으로 검색
        if not url_text:
            return

        if not url_text.startswith(("http://", "https://")):
            # 검색어로 처리 (Google 검색)
            url_text = f"https://www.google.com/search?q={url_text}"
        else:
            # http://를 https://로 자동 변환 (보안 강화)
            if url_text.startswith("http://"):
                url_text = url_text.replace("http://", "https://", 1)

            # 쿠팡 도메인인 경우 메인 페이지를 먼저 방문 (봇 차단 우회)
            if "coupang.com" in url_text:
                current_url = self.web_view.url().toString()
                # 메인 페이지가 아니고, 아직 쿠팡 메인을 방문하지 않은 경우
                if not url_text.startswith("https://www.coupang.com/") or (
                    "www.coupang.com" in url_text
                    and url_text != "https://www.coupang.com/"
                ):
                    if "www.coupang.com" not in current_url:
                        # 메인 페이지를 먼저 방문
                        self.pending_coupang_url = url_text
                        self.web_view.setUrl(QUrl("https://www.coupang.com/"))
                        return

        self.pending_coupang_url = None
        self.web_view.setUrl(QUrl(url_text))

    def handle_coupang_navigation(self, success: bool):
        """쿠팡 메인 페이지 로드 완료 후 목표 페이지로 이동"""
        if self.pending_coupang_url and success:
            current_url = self.web_view.url().toString()
            # 쿠팡 메인 페이지가 로드된 경우
            if "www.coupang.com" in current_url and current_url in [
                "https://www.coupang.com/",
                "https://www.coupang.com",
            ]:
                # 약간의 지연 후 목표 페이지로 이동 (쿠키/세션 설정 시간 확보)
                from PySide6.QtCore import QTimer

                QTimer.singleShot(
                    1000, lambda: self.web_view.setUrl(QUrl(self.pending_coupang_url))
                )
                self.pending_coupang_url = None

    def go_back(self):
        """뒤로 가기"""
        self.web_view.back()

    def go_forward(self):
        """앞으로 가기"""
        self.web_view.forward()

    def reload_page(self):
        """페이지 새로고침"""
        self.web_view.reload()

    def go_home(self):
        """홈으로 이동"""
        self.web_view.setUrl(QUrl("https://www.google.com"))

    def update_url_bar(self, url: QUrl):
        """URL 변경 시 주소창 업데이트"""
        self.url_bar.setText(url.toString())

    def update_navigation_buttons(self):
        """네비게이션 버튼 상태 업데이트"""
        history = self.web_view.history()
        self.back_button.setEnabled(history.canGoBack())
        self.forward_button.setEnabled(history.canGoForward())

    def update_window_title(self, title: str):
        """페이지 제목 변경 시 윈도우 제목 업데이트"""
        self.setWindowTitle(f"{title} - PyWebEngine Browser")


def main():
    """애플리케이션 진입점"""
    # QWebEngine 로깅 레벨 설정 (JavaScript 콘솔 메시지 줄이기)
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-logging")

    app = QApplication(sys.argv)

    # 애플리케이션 정보 설정
    app.setApplicationName("PyWebEngine Browser")
    app.setOrganizationName("PyWebEngine")

    # 브라우저 윈도우 생성 및 표시
    browser = BrowserWindow()
    browser.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
