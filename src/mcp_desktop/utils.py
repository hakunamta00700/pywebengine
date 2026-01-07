"""
유틸리티 함수 모음
"""

import logging
import json
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime

# 보안 로그 파일 경로
SECURITY_LOG_FILE = Path.home() / ".mcp_desktop" / "security.log"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    로깅 설정
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger("mcp_desktop")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def validate_coordinates(x: Optional[int], y: Optional[int]) -> tuple[int, int]:
    """
    좌표 검증 및 기본값 설정
    
    Args:
        x: X 좌표 (None이면 현재 마우스 위치 사용)
        y: Y 좌표 (None이면 현재 마우스 위치 사용)
    
    Returns:
        (x, y) 튜플
    """
    import pyautogui
    
    if x is None or y is None:
        current_x, current_y = pyautogui.position()
        x = x if x is not None else current_x
        y = y if y is not None else current_y
    
    return (x, y)


def safe_file_path(path: str) -> Path:
    """
    안전한 파일 경로 생성 및 검증
    
    Args:
        path: 파일 경로 문자열
    
    Returns:
        Path 객체
    
    Raises:
        ValueError: 경로가 안전하지 않은 경우
    """
    file_path = Path(path).resolve()
    
    # 위험한 경로 차단 (시스템 디렉토리 등)
    dangerous_paths = [
        Path("C:/Windows"),
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path("C:/System32"),
    ]
    
    for dangerous in dangerous_paths:
        try:
            if file_path.is_relative_to(dangerous):
                raise ValueError(f"접근이 제한된 경로입니다: {path}")
        except (ValueError, AttributeError):
            # Python 3.8 이하에서는 is_relative_to가 없을 수 있음
            if str(file_path).startswith(str(dangerous)):
                raise ValueError(f"접근이 제한된 경로입니다: {path}")
    
    return file_path


def create_error_response(
    code: int, message: str, data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    에러 응답 생성
    
    Args:
        code: 에러 코드
        message: 에러 메시지
        data: 추가 데이터
    
    Returns:
        에러 응답 딕셔너리
    """
    response = {"error": {"code": code, "message": message}}
    if data:
        response["error"]["data"] = data
    return response


def log_security_event(
    event_type: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    risk_level: str = "low",
):
    """
    보안 이벤트 로깅
    
    Args:
        event_type: 이벤트 타입 (예: "file_access", "system_control", "window_management")
        action: 수행된 작업
        details: 추가 상세 정보
        risk_level: 위험 수준 ("low", "medium", "high", "critical")
    """
    try:
        # 로그 디렉토리 생성
        SECURITY_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "action": action,
            "risk_level": risk_level,
            "details": details or {},
        }
        
        # 파일에 로그 기록
        with open(SECURITY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # 위험 수준이 높은 경우 콘솔에도 출력
        if risk_level in ["high", "critical"]:
            logger = logging.getLogger("mcp_desktop.security")
            logger.warning(f"[{risk_level.upper()}] {event_type}: {action}")
    
    except Exception as e:
        # 로깅 실패해도 프로그램은 계속 실행
        logging.getLogger("mcp_desktop.security").error(f"보안 로그 기록 실패: {e}")


def check_dangerous_operation(operation: str, **kwargs) -> tuple[bool, Optional[str]]:
    """
    위험한 작업인지 확인
    
    Args:
        operation: 작업 이름
        **kwargs: 작업 관련 인자
    
    Returns:
        (is_dangerous, warning_message) 튜플
    """
    dangerous_operations = {
        "file_delete": {
            "risk": "high",
            "message": "파일 삭제는 위험한 작업입니다.",
        },
        "system_shutdown": {
            "risk": "critical",
            "message": "시스템 종료는 매우 위험한 작업입니다.",
        },
        "file_write_system": {
            "risk": "high",
            "message": "시스템 파일 쓰기는 위험한 작업입니다.",
        },
        "process_kill_system": {
            "risk": "high",
            "message": "시스템 프로세스 종료는 위험한 작업입니다.",
        },
    }
    
    if operation in dangerous_operations:
        info = dangerous_operations[operation]
        log_security_event(
            "dangerous_operation",
            operation,
            kwargs,
            info["risk"],
        )
        return True, info["message"]
    
    return False, None


def validate_file_access(file_path: str, operation: str = "read") -> tuple[bool, Optional[str]]:
    """
    파일 접근 검증
    
    Args:
        file_path: 파일 경로
        operation: 작업 타입 ("read", "write", "delete")
    
    Returns:
        (is_allowed, error_message) 튜플
    """
    try:
        path = safe_file_path(file_path)
        
        # 쓰기/삭제 작업은 추가 검증
        if operation in ["write", "delete"]:
            # 시스템 디렉토리 차단
            system_dirs = [
                "C:/Windows",
                "C:/Program Files",
                "C:/Program Files (x86)",
                "C:/System32",
                "C:/ProgramData",
            ]
            
            for sys_dir in system_dirs:
                try:
                    if path.is_relative_to(Path(sys_dir)):
                        log_security_event(
                            "file_access_denied",
                            f"{operation} {file_path}",
                            {"reason": "system_directory"},
                            "high",
                        )
                        return False, f"시스템 디렉토리 접근이 차단되었습니다: {sys_dir}"
                except (ValueError, AttributeError):
                    if str(path).startswith(sys_dir):
                        log_security_event(
                            "file_access_denied",
                            f"{operation} {file_path}",
                            {"reason": "system_directory"},
                            "high",
                        )
                        return False, f"시스템 디렉토리 접근이 차단되었습니다: {sys_dir}"
            
            # 위험한 작업 로깅
            log_security_event(
                "file_access",
                f"{operation} {file_path}",
                {"path": str(path)},
                "medium" if operation == "write" else "high",
            )
        
        return True, None
    
    except Exception as e:
        return False, str(e)

