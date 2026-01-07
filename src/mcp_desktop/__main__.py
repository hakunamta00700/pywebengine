"""
MCP 서버 실행 진입점
python -m mcp_desktop 으로 실행 가능
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())

