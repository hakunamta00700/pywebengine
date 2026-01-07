"""
CLI 진입점
독립 실행형 MCP 서버 실행
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mcp_desktop.server import main

if __name__ == "__main__":
    asyncio.run(main())

