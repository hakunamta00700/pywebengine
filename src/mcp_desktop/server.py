"""
MCP 서버 메인 모듈
독립 실행형 stdin/stdout 기반 MCP 서버
"""

import asyncio
import sys
import logging
from typing import Any, Dict

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("mcp 패키지가 설치되지 않았습니다. MCP 서버를 사용할 수 없습니다.")

from .utils import setup_logging
from .tools import get_all_tools, call_tool

logger = setup_logging()

# Resources는 선택적으로 import (MCP 버전에 따라 지원되지 않을 수 있음)
try:
    from .resources import get_all_resources, read_resource
    RESOURCES_AVAILABLE = True
except ImportError:
    RESOURCES_AVAILABLE = False
    logger.warning("Resources 모듈을 로드할 수 없습니다. Resources 기능이 비활성화됩니다.")


class DesktopMCPServer:
    """데스크탑 자동화 MCP 서버"""
    
    def __init__(self):
        """서버 초기화"""
        if not MCP_AVAILABLE:
            raise ImportError("mcp 패키지가 필요합니다. pip install mcp로 설치하세요.")
        
        self.server = Server("mcp-desktop-automation")
        self._setup_handlers()
        logger.info("MCP 데스크탑 자동화 서버 초기화 완료")
    
    def _setup_handlers(self):
        """MCP 핸들러 설정"""
        # Tools 목록 제공
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """사용 가능한 도구 목록 반환"""
            tools = get_all_tools()
            logger.info(f"도구 목록 요청: {len(tools)}개")
            return tools
        
        # Tool 호출 처리
        @self.server.call_tool()
        async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
            """도구 호출 처리"""
            logger.info(f"도구 호출: {name}, 인자: {arguments}")
            try:
                result = await call_tool(name, arguments)
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"도구 호출 실패: {e}", exc_info=True)
                return [TextContent(type="text", text=f"오류: {str(e)}")]
        
        # Resources 목록 제공 (선택적)
        if RESOURCES_AVAILABLE:
            try:
                from mcp.types import Resource
                @self.server.list_resources()
                async def list_resources() -> list[Resource]:
                    """사용 가능한 리소스 목록 반환"""
                    resources = get_all_resources()
                    logger.info(f"리소스 목록 요청: {len(resources)}개")
                    return resources
                
                # Resource 읽기 처리
                @self.server.read_resource()
                async def read_resource_handler(uri: str) -> str:
                    """리소스 읽기 처리"""
                    logger.info(f"리소스 읽기: {uri}")
                    try:
                        return await read_resource(uri)
                    except Exception as e:
                        logger.error(f"리소스 읽기 실패: {e}", exc_info=True)
                        return f"오류: {str(e)}"
            except (ImportError, AttributeError) as e:
                # Resources가 지원되지 않는 경우 무시
                logger.debug(f"Resources 핸들러 등록 실패 (무시됨): {e}")
                pass
    
    async def run(self):
        """서버 실행"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    """메인 진입점"""
    try:
        server = DesktopMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("서버 종료 요청")
    except Exception as e:
        logger.error(f"서버 오류: {e}", exc_info=True)
        sys.exit(1)


def main_sync():
    """동기 래퍼 함수 (entry-points용)"""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())

