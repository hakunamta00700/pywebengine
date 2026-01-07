"""
파일 시스템 접근 모듈
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("mcp_desktop.filesystem")


class FilesystemController:
    """파일 시스템 제어 클래스"""
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> dict:
        """
        파일 읽기
        
        Args:
            file_path: 파일 경로
            encoding: 인코딩 (기본값: utf-8)
        
        Returns:
            파일 내용 딕셔너리
        """
        try:
            from .utils import safe_file_path, validate_file_access, log_security_event
            
            # 파일 접근 검증
            is_allowed, error_msg = validate_file_access(file_path, "read")
            if not is_allowed:
                return {"success": False, "error": error_msg}
            
            path = safe_file_path(file_path)
            
            # 보안 로깅
            log_security_event(
                "file_access",
                f"read {file_path}",
                {"path": str(path)},
                "low",
            )
            
            if not path.exists():
                return {"success": False, "error": f"파일이 존재하지 않습니다: {file_path}"}
            
            if not path.is_file():
                return {"success": False, "error": f"파일이 아닙니다: {file_path}"}
            
            # 파일 크기 확인 (너무 큰 파일은 읽지 않음)
            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return {"success": False, "error": "파일이 너무 큽니다 (10MB 제한)"}
            
            content = path.read_text(encoding=encoding)
            
            logger.info(f"파일 읽기: {file_path} ({len(content)} bytes)")
            return {
                "success": True,
                "path": str(path),
                "content": content,
                "size": len(content),
                "encoding": encoding,
            }
        except UnicodeDecodeError:
            return {"success": False, "error": f"인코딩 오류: {encoding}"}
        except Exception as e:
            logger.error(f"파일 읽기 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def list_directory(self, dir_path: str = ".") -> dict:
        """
        디렉토리 목록 조회
        
        Args:
            dir_path: 디렉토리 경로 (기본값: 현재 디렉토리)
        
        Returns:
            디렉토리 내용 딕셔너리
        """
        try:
            from .utils import safe_file_path
            
            path = safe_file_path(dir_path)
            
            if not path.exists():
                return {"success": False, "error": f"디렉토리가 존재하지 않습니다: {dir_path}"}
            
            if not path.is_dir():
                return {"success": False, "error": f"디렉토리가 아닙니다: {dir_path}"}
            
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "is_file": item.is_file(),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None,
                })
            
            logger.info(f"디렉토리 목록 조회: {dir_path} ({len(items)}개 항목)")
            return {
                "success": True,
                "path": str(path),
                "items": items,
                "count": len(items),
            }
        except Exception as e:
            logger.error(f"디렉토리 목록 조회 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def get_file_info(self, file_path: str) -> dict:
        """
        파일 정보 조회
        
        Args:
            file_path: 파일 경로
        
        Returns:
            파일 정보 딕셔너리
        """
        try:
            from .utils import safe_file_path
            
            path = safe_file_path(file_path)
            
            if not path.exists():
                return {"success": False, "error": f"파일이 존재하지 않습니다: {file_path}"}
            
            stat = path.stat()
            info = {
                "path": str(path),
                "name": path.name,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
            }
            
            logger.info(f"파일 정보 조회: {file_path}")
            return {"success": True, "info": info}
        except Exception as e:
            logger.error(f"파일 정보 조회 실패: {e}")
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_filesystem_controller = None


def get_filesystem_controller() -> FilesystemController:
    """파일 시스템 컨트롤러 싱글톤 인스턴스 반환"""
    global _filesystem_controller
    if _filesystem_controller is None:
        _filesystem_controller = FilesystemController()
    return _filesystem_controller

