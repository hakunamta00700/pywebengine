# MCP 데스크탑 자동화 프로젝트

ChatGPT 및 기타 LLM이 데스크탑을 자동으로 제어할 수 있도록 하는 MCP (Model Context Protocol) 서버입니다.

## 기능

### 기본 자동화 기능
- **마우스 제어**: 클릭, 이동, 드래그, 스크롤
- **키보드 제어**: 텍스트 입력, 단축키, 특수 키
- **스크린샷**: 전체 화면 또는 영역 캡처
- **화면 정보**: 해상도, 픽셀 색상 조회

### 고급 자동화 기능
- **윈도우 관리**: 윈도우 찾기, 활성화, 크기 조절
- **파일 시스템**: 파일 읽기, 디렉토리 탐색
- **OCR**: 이미지에서 텍스트 추출
- **보안**: 권한 확인, 위험 작업 경고, 로깅

## 설치

### 필수 요구사항
- Python 3.12 이상
- Windows 10/11 (현재 지원)

### 의존성 설치

```bash
# uv를 사용하는 경우
uv sync

# 또는 pip를 사용하는 경우
pip install -e .
```

### 추가 설치 필요 항목

#### Tesseract OCR (OCR 기능 사용 시)
1. [Tesseract 설치 프로그램](https://github.com/UB-Mannheim/tesseract/wiki) 다운로드
2. 설치 후 환경 변수 PATH에 추가

## 사용 방법

### Cursor에서 MCP 서버 등록

Cursor IDE에서 이 MCP 서버를 사용하려면 다음 단계를 따르세요:

#### 1. 프로젝트별 설정 (권장)

프로젝트 루트 디렉토리에 `.cursor/mcp.json` 파일을 생성하고 다음 내용을 추가하세요:

```json
{
  "mcpServers": {
    "desktop-automation": {
      "command": "python",
      "args": ["-m", "src.mcp_desktop.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

또는 절대 경로를 사용하는 경우:

```json
{
  "mcpServers": {
    "desktop-automation": {
      "command": "python",
      "args": ["C:/Users/your-username/workspace/pywebengine/src/mcp_desktop/server.py"],
      "cwd": "C:/Users/your-username/workspace/pywebengine"
    }
  }
}
```

#### 2. 전역 설정

모든 프로젝트에서 사용하려면 홈 디렉토리에 `~/.cursor/mcp.json` 파일을 생성하세요:

```json
{
  "mcpServers": {
    "desktop-automation": {
      "command": "python",
      "args": ["-m", "src.mcp_desktop.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

#### 3. 설정 적용

1. Cursor를 재시작하거나
2. Cursor 설정에서 MCP 서버를 새로고침하세요

설정이 완료되면 Cursor의 AI 채팅에서 데스크탑 자동화 기능을 사용할 수 있습니다.

### 독립 실행형 MCP 서버

```bash
# 모듈로 실행
python -m src.mcp_desktop.server

# 또는 CLI로 실행
python src/mcp_desktop/cli.py
```

### 내장형 서버 (채팅 UI)

```bash
python aidesktop.py
```

채팅 UI에서 다음 명령어를 사용할 수 있습니다:
- `스크린샷` 또는 `화면 캡처`: 화면 캡처
- `마우스 위치`: 현재 마우스 위치 조회
- `화면 크기`: 화면 해상도 조회

## 프로젝트 구조

```
.
├── docs/
│   └── prd.md              # 제품 요구사항 문서
├── src/
│   └── mcp_desktop/
│       ├── __init__.py
│       ├── server.py        # MCP 서버 메인
│       ├── tools.py          # MCP Tools 정의
│       ├── resources.py     # MCP Resources
│       ├── mouse.py         # 마우스 제어
│       ├── keyboard.py      # 키보드 제어
│       ├── screenshot.py   # 스크린샷
│       ├── window.py        # 윈도우 관리
│       ├── filesystem.py   # 파일 시스템
│       ├── ocr.py          # OCR 기능
│       ├── security.py     # 보안 관리
│       └── utils.py        # 유틸리티
├── aidesktop.py            # 채팅 UI (내장형 서버)
├── main.py                 # 웹 브라우저
├── index.html              # 채팅 UI HTML
└── pyproject.toml          # 프로젝트 설정
```

## MCP Tools

다음 MCP Tools를 사용할 수 있습니다:

### 마우스 제어
- `mouse_click`: 마우스 클릭
- `mouse_move`: 마우스 이동
- `mouse_drag`: 마우스 드래그
- `mouse_scroll`: 마우스 스크롤
- `mouse_get_position`: 마우스 위치 조회

### 키보드 제어
- `keyboard_type`: 텍스트 입력
- `keyboard_press`: 키 누르기
- `keyboard_hotkey`: 단축키 조합

### 스크린샷
- `screenshot_full`: 전체 화면 캡처
- `screenshot_region`: 영역 캡처
- `screenshot_get_size`: 화면 크기 조회
- `screenshot_get_pixel_color`: 픽셀 색상 조회

### 윈도우 관리
- `window_find`: 윈도우 찾기
- `window_activate`: 윈도우 활성화
- `window_get_info`: 윈도우 정보 조회

### 파일 시스템
- `filesystem_read_file`: 파일 읽기
- `filesystem_list_directory`: 디렉토리 목록 조회
- `filesystem_get_file_info`: 파일 정보 조회

### OCR
- `ocr_extract_from_image`: 이미지에서 텍스트 추출
- `ocr_extract_from_screenshot`: 스크린샷에서 텍스트 추출

## 보안

- 시스템 디렉토리 접근 차단
- 위험한 작업에 대한 경고 및 로깅
- 보안 이벤트 로그 저장 (`~/.mcp_desktop/security.log`)

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## Cursor에서 사용 예시

MCP 서버가 등록되면 Cursor의 AI 채팅에서 다음과 같이 사용할 수 있습니다:

```
사용자: "화면을 캡처해서 보여줘"
AI: [screenshot_full 도구 호출] → 화면 캡처 결과 표시

사용자: "메모장을 열고 '안녕하세요'를 입력해줘"
AI: [window_find로 메모장 찾기] → [window_activate로 활성화] → [keyboard_type으로 텍스트 입력]

사용자: "다운로드 폴더의 파일 목록을 보여줘"
AI: [filesystem_list_directory로 목록 조회] → 결과 표시
```

## 참고 자료

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Cursor MCP 문서](https://docs.cursor.com/ko/context/mcp)
- [PRD 문서](docs/prd.md)

