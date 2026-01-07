"""
보안 및 권한 관리 모듈
"""

import logging
from typing import Optional, Dict, Any
from .utils import log_security_event, check_dangerous_operation

logger = logging.getLogger("mcp_desktop.security")


class SecurityManager:
    """보안 관리자"""
    
    def __init__(self):
        """보안 관리자 초기화"""
        self.allowed_operations = set()
        self.blocked_operations = set()
        self.require_confirmation = set()
    
    def check_permission(
        self, operation: str, details: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        작업 권한 확인
        
        Args:
            operation: 작업 이름
            details: 작업 상세 정보
        
        Returns:
            (is_allowed, reason) 튜플
        """
        # 차단된 작업 확인
        if operation in self.blocked_operations:
            log_security_event(
                "permission_denied",
                operation,
                details,
                "high",
            )
            return False, f"작업이 차단되었습니다: {operation}"
        
        # 위험한 작업 확인
        is_dangerous, warning = check_dangerous_operation(operation, **(details or {}))
        if is_dangerous:
            # 확인이 필요한 작업인지 확인
            if operation in self.require_confirmation:
                return False, f"확인이 필요한 작업입니다: {warning}"
        
        return True, None
    
    def block_operation(self, operation: str):
        """작업 차단"""
        self.blocked_operations.add(operation)
        logger.info(f"작업 차단: {operation}")
    
    def allow_operation(self, operation: str):
        """작업 허용"""
        self.allowed_operations.add(operation)
        if operation in self.blocked_operations:
            self.blocked_operations.remove(operation)
        logger.info(f"작업 허용: {operation}")
    
    def require_confirmation_for(self, operation: str):
        """작업에 확인 요구"""
        self.require_confirmation.add(operation)
        logger.info(f"확인 요구 작업 추가: {operation}")


# 전역 보안 관리자 인스턴스
_security_manager = None


def get_security_manager() -> SecurityManager:
    """보안 관리자 싱글톤 인스턴스 반환"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
        # 기본적으로 위험한 작업에 확인 요구
        _security_manager.require_confirmation_for("file_delete")
        _security_manager.require_confirmation_for("system_shutdown")
        _security_manager.require_confirmation_for("process_kill_system")
    return _security_manager

