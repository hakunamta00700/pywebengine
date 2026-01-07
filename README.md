# MCP 데스크탑 자동화 프로젝트

ChatGPT 및 기타 LLM이 데스크탑을 자동으로 제어할 수 있도록 하는 MCP (Model Context Protocol) 서버입니다. **고수준 통합 도구**를 제공하여 LLM이 복잡한 데스크탑 작업을 쉽고 효율적으로 수행할 수 있습니다.

## 주요 특징

### 🎯 고수준 통합 도구
- **`click_text`**: 화면에서 텍스트를 찾아 자동으로 클릭 (인덱싱 → 검색 → 클릭 자동화)
- **`type_text`**: 입력 필드를 찾아 텍스트 입력
- **`find_element`**: 화면에서 요소 찾기 (위치 정보 반환)
- **`interact_window`**: 윈도우에서 일련의 작업 순차 수행

### 🧠 스마트 인덱싱
- **자동 인덱싱**: 필요시에만 화면 인덱싱 수행
- **캐싱 최적화**: 동일 화면에서 반복 작업 시 재인덱싱 방지
- **상태 추적**: 인덱싱 상태를 추적하여 효율적인 작업 수행

### 🔧 기본 자동화 기능
- **마우스 제어**: 클릭, 이동, 드래그, 스크롤
- **키보드 제어**: 텍스트 입력, 단축키, 특수 키
- **윈도우 관리**: 윈도우 찾기, 활성화, 정보 조회
- **파일 시스템**: 파일 읽기, 디렉토리 탐색
- **OCR**: 이미지에서 텍스트 추출 (Tesseract 기반)
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
│   ├── prd.md                      # 제품 요구사항 문서
│   ├── test_scenario.md            # 기본 테스트 시나리오
│   └── test_scenario_advanced.md   # 고급 테스트 시나리오
├── src/
│   └── mcp_desktop/
│       ├── __init__.py
│       ├── server.py               # MCP 서버 메인
│       ├── tools.py                # MCP Tools 정의 (고수준 도구)
│       ├── smart_indexer.py        # 스마트 인덱싱 관리자
│       ├── screen_indexer.py       # 화면 인덱싱 (OCR 기반)
│       ├── resources.py            # MCP Resources
│       ├── mouse.py                # 마우스 제어
│       ├── keyboard.py             # 키보드 제어
│       ├── screenshot.py           # 스크린샷
│       ├── window.py               # 윈도우 관리
│       ├── filesystem.py           # 파일 시스템
│       ├── ocr.py                  # OCR 기능
│       ├── security.py             # 보안 관리
│       └── utils.py                # 유틸리티
├── aidesktop.py                    # 채팅 UI (내장형 서버)
├── main.py                         # 웹 브라우저
├── index.html                      # 채팅 UI HTML
└── pyproject.toml                  # 프로젝트 설정
```

## MCP Tools

### 고수준 통합 도구 (권장)

LLM이 사용하기 쉬운 고수준 도구들입니다. 내부적으로 인덱싱, 검색, 클릭 등을 자동으로 처리합니다.

#### `click_text` - 텍스트 찾아 클릭
화면에서 텍스트를 찾아 자동으로 클릭합니다. 인덱싱이 필요하면 자동으로 수행합니다.

```json
{
  "name": "click_text",
  "arguments": {
    "search_text": "저장",
    "window_id": null,  // 선택적
    "exact_match": false,
    "button": "left"
  }
}
```

#### `type_text` - 입력 필드에 텍스트 입력
입력 필드를 찾아 클릭한 후 텍스트를 입력합니다.

```json
{
  "name": "type_text",
  "arguments": {
    "search_text": "이름",
    "text": "홍길동",
    "window_id": null  // 선택적
  }
}
```

#### `find_element` - 화면 요소 찾기
화면에서 텍스트나 요소를 찾아 위치 정보를 반환합니다.

```json
{
  "name": "find_element",
  "arguments": {
    "search_text": "로그인",
    "window_id": null,  // 선택적
    "exact_match": false
  }
}
```

#### `interact_window` - 윈도우에서 여러 작업 수행
특정 윈도우를 찾아 활성화한 후 여러 작업을 순차적으로 실행합니다.

```json
{
  "name": "interact_window",
  "arguments": {
    "window_title": "메모장",
    "actions": [
      {"type": "click_text", "search_text": "파일"},
      {"type": "type", "text": "안녕하세요"},
      {"type": "hotkey", "keys": ["ctrl", "s"]}
    ]
  }
}
```

### 유틸리티 도구

필요한 경우에만 사용하는 보조 도구들입니다.

- **`window_find`**: 윈도우 찾기
- **`filesystem_read_file`**: 파일 읽기
- **`filesystem_list_directory`**: 디렉토리 목록 조회

> **참고**: 저수준 도구들(`mouse_click`, `keyboard_type` 등)은 내부적으로만 사용되며, 고수준 도구에서 자동으로 호출됩니다.

## 보안

- 시스템 디렉토리 접근 차단
- 위험한 작업에 대한 경고 및 로깅
- 보안 이벤트 로그 저장 (`~/.mcp_desktop/security.log`)

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 사용 예시

### Cursor에서 자연어 명령 사용

MCP 서버가 등록되면 Cursor의 AI 채팅에서 자연어로 명령할 수 있습니다:

#### 예시 1: 간단한 클릭 작업
```
사용자: "저장 버튼을 클릭해줘"
AI: [click_text("저장") 호출] → 자동으로 인덱싱 → 텍스트 검색 → 클릭
```

#### 예시 2: 텍스트 입력
```
사용자: "이름 필드에 '홍길동'을 입력해줘"
AI: [type_text("이름", "홍길동") 호출] → 입력 필드 찾기 → 클릭 → 텍스트 입력
```

#### 예시 3: 복합 작업
```
사용자: "Excel을 열고 A1에 '이름', B1에 '나이'를 입력하고 저장해줘"
AI: [interact_window 호출]
    → Excel 찾기 및 활성화
    → A1 클릭 → "이름" 입력
    → B1 클릭 → "나이" 입력
    → Ctrl+S로 저장
```

#### 예시 4: 윈도우 작업
```
사용자: "메모장을 열고 '안녕하세요'를 입력해줘"
AI: [interact_window("메모장", [{"type": "type", "text": "안녕하세요"}])]
```

#### 예시 5: 파일 시스템 작업
```
사용자: "다운로드 폴더의 파일 목록을 보여줘"
AI: [filesystem_list_directory("C:/Users/.../Downloads")] → 결과 표시
```

### 실제 사용 사례

더 많은 실제 사용 사례는 [고급 테스트 시나리오 문서](docs/test_scenario_advanced.md)를 참고하세요:
- Excel에서 데이터 입력 및 분석
- Word 문서 작성 및 서식 적용
- 웹 브라우저에서 검색 및 로그인
- 파일 탐색기에서 파일 정리
- Outlook에서 이메일 작성 및 전송

## 작동 원리

### 스마트 인덱싱 워크플로우

1. **요청 수신**: LLM이 `click_text("저장")` 같은 고수준 도구 호출
2. **인덱싱 상태 확인**: 마지막 인덱싱 시간과 화면 크기 확인
3. **자동 인덱싱** (필요시): 화면을 그리드로 분할하고 OCR 수행
4. **텍스트 검색**: 인덱싱된 데이터에서 텍스트 검색
5. **작업 수행**: 찾은 위치를 클릭하거나 텍스트 입력

### Before vs After

**Before (저수준 도구 사용)**:
```
screen_index() → screen_find_text("저장") → mouse_click(x, y)
```
- 3번의 도구 호출 필요
- LLM이 각 단계를 계획해야 함
- 인덱싱 상태를 확인할 방법 없음

**After (고수준 도구 사용)**:
```
click_text("저장")
```
- 1번의 도구 호출로 완료
- 내부적으로 모든 단계 자동 처리
- 인덱싱 상태 자동 관리

## 문서

- [제품 요구사항 문서 (PRD)](docs/prd.md) - 프로젝트 전체 요구사항
- [기본 테스트 시나리오](docs/test_scenario.md) - 도구별 기본 테스트
- [고급 테스트 시나리오](docs/test_scenario_advanced.md) - 실제 사용 사례 기반 테스트

## 참고 자료

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Cursor MCP 문서](https://docs.cursor.com/ko/context/mcp)

