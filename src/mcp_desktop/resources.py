"""
MCP Resources 정의
"""

import logging
from typing import List

try:
    from mcp.types import Resource
    MCP_RESOURCE_AVAILABLE = True
except ImportError:
    MCP_RESOURCE_AVAILABLE = False
    Resource = None  # type: ignore

logger = logging.getLogger("mcp_desktop.resources")


def get_all_resources() -> List[Resource]:
    """
    모든 MCP Resources 목록 반환
    
    Returns:
        Resource 객체 리스트
    """
    if not MCP_RESOURCE_AVAILABLE or Resource is None:
        return []
    
    return [
        Resource(
            uri="desktop://screen/info",
            name="화면 정보",
            description="현재 화면 해상도 및 정보",
            mimeType="application/json",
        ),
        Resource(
            uri="desktop://mouse/position",
            name="마우스 위치",
            description="현재 마우스 위치",
            mimeType="application/json",
        ),
    ]


async def read_resource(uri: str) -> str:
    """
    Resource 읽기
    
    Args:
        uri: Resource URI
    
    Returns:
        Resource 내용 (JSON 문자열)
    """
    import json
    from .screenshot import get_screenshot_controller
    from .mouse import get_mouse_controller
    
    try:
        if uri == "desktop://screen/info":
            screenshot = get_screenshot_controller()
            result = screenshot.get_screen_size()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif uri == "desktop://mouse/position":
            mouse = get_mouse_controller()
            result = mouse.get_position()
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        else:
            return json.dumps({"error": f"알 수 없는 리소스: {uri}"})
    
    except Exception as e:
        logger.error(f"리소스 읽기 오류 ({uri}): {e}", exc_info=True)
        return json.dumps({"error": str(e)}, ensure_ascii=False)

