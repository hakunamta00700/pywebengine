"""
화면 인덱싱 모듈
화면을 분할하고 OCR을 수행하여 텍스트와 위치 정보를 인덱싱
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
from pathlib import Path

from .ocr import get_ocr_controller, TESSERACT_AVAILABLE
from .screenshot import get_screenshot_controller
from .window import get_window_controller

logger = logging.getLogger("mcp_desktop.screen_indexer")


@dataclass
class TextRegion:
    """텍스트 영역 정보"""
    text: str
    x: int
    y: int
    width: int
    height: int
    center_x: int
    center_y: int
    confidence: float = 0.0


class ScreenIndexer:
    """화면 인덱서"""
    
    def __init__(self, grid_size: int = 200):
        """
        Args:
            grid_size: 그리드 크기 (픽셀). 화면을 이 크기로 분할
        """
        self.grid_size = grid_size
        self.ocr = get_ocr_controller()
        self.screenshot = get_screenshot_controller()
        self.window = get_window_controller()
        self._db_path = Path.home() / ".mcp_desktop" / "screen_index.db"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """임시 DB 초기화"""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS screen_regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                window_id INTEGER,
                text TEXT NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                center_x INTEGER NOT NULL,
                center_y INTEGER NOT NULL,
                confidence REAL DEFAULT 0.0
            )
        """)
        # 기존 테이블에 window_id 컬럼이 없으면 추가
        try:
            conn.execute("ALTER TABLE screen_regions ADD COLUMN window_id INTEGER")
        except sqlite3.OperationalError:
            # 컬럼이 이미 존재하는 경우 무시
            pass
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_text ON screen_regions(text)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON screen_regions(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_window_id ON screen_regions(window_id)
        """)
        conn.commit()
        conn.close()
    
    def index_screen(self, grid_size: Optional[int] = None) -> dict:
        """
        화면을 인덱싱 (분할 + OCR)
        
        Args:
            grid_size: 그리드 크기 (None이면 기본값 사용)
        
        Returns:
            인덱싱 결과 딕셔너리
        """
        if not TESSERACT_AVAILABLE:
            return {"success": False, "error": "Tesseract OCR이 필요합니다."}
        
        try:
            grid_size = grid_size or self.grid_size
            
            # 화면 크기 조회
            screen_info = self.screenshot.get_screen_size()
            if not screen_info.get("success"):
                return {"success": False, "error": "화면 크기 조회 실패"}
            
            width = screen_info["width"]
            height = screen_info["height"]
            
            # 이전 인덱스 삭제
            self._clear_index()
            
            # 화면을 그리드로 분할
            regions = []
            total_regions = 0
            text_regions = []
            
            for y in range(0, height, grid_size):
                for x in range(0, width, grid_size):
                    region_width = min(grid_size, width - x)
                    region_height = min(grid_size, height - y)
                    
                    # 각 영역에 대해 OCR 수행
                    ocr_result = self.ocr.extract_text_from_screenshot(
                        x=x,
                        y=y,
                        width=region_width,
                        height=region_height,
                    )
                    
                    total_regions += 1
                    
                    if ocr_result.get("success") and ocr_result.get("text"):
                        text = ocr_result["text"].strip()
                        if text:
                            center_x = x + region_width // 2
                            center_y = y + region_height // 2
                            
                            region = TextRegion(
                                text=text,
                                x=x,
                                y=y,
                                width=region_width,
                                height=region_height,
                                center_x=center_x,
                                center_y=center_y,
                            )
                            text_regions.append(region)
                            regions.append(asdict(region))
            
            # DB에 저장 (전체 화면이므로 window_id는 NULL)
            timestamp = datetime.now().isoformat()
            conn = sqlite3.connect(str(self._db_path))
            for region in text_regions:
                conn.execute("""
                    INSERT INTO screen_regions 
                    (timestamp, window_id, text, x, y, width, height, center_x, center_y, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    None,  # 전체 화면 인덱스
                    region.text,
                    region.x,
                    region.y,
                    region.width,
                    region.height,
                    region.center_x,
                    region.center_y,
                    region.confidence,
                ))
            conn.commit()
            conn.close()
            
            logger.info(f"화면 인덱싱 완료: {total_regions}개 영역, {len(text_regions)}개 텍스트 영역")
            
            return {
                "success": True,
                "total_regions": total_regions,
                "text_regions": len(text_regions),
                "timestamp": timestamp,
                "grid_size": grid_size,
                "screen_size": {"width": width, "height": height},
                "regions": regions[:50],  # 처음 50개만 반환 (컨텍스트 절약)
            }
        
        except Exception as e:
            logger.error(f"화면 인덱싱 실패: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def index_window(self, hwnd: int, grid_size: Optional[int] = None) -> dict:
        """
        특정 윈도우를 인덱싱 (분할 + OCR)
        
        Args:
            hwnd: 윈도우 핸들
            grid_size: 그리드 크기 (None이면 기본값 사용)
        
        Returns:
            인덱싱 결과 딕셔너리
        """
        if not TESSERACT_AVAILABLE:
            return {"success": False, "error": "Tesseract OCR이 필요합니다."}
        
        try:
            grid_size = grid_size or self.grid_size
            
            # 윈도우 정보 조회
            window_rect = self.window.get_window_rect(hwnd)
            if not window_rect.get("success"):
                return {"success": False, "error": f"윈도우 정보 조회 실패: {window_rect.get('error')}"}
            
            window_left = window_rect["left"]
            window_top = window_rect["top"]
            window_width = window_rect["width"]
            window_height = window_rect["height"]
            
            # 해당 윈도우의 이전 인덱스 삭제
            self._clear_index(window_id=hwnd)
            
            # 윈도우를 그리드로 분할
            regions = []
            total_regions = 0
            text_regions = []
            
            for y in range(0, window_height, grid_size):
                for x in range(0, window_width, grid_size):
                    region_width = min(grid_size, window_width - x)
                    region_height = min(grid_size, window_height - y)
                    
                    # 화면 좌표로 변환 (윈도우 좌표 + 윈도우 위치)
                    screen_x = window_left + x
                    screen_y = window_top + y
                    
                    # 각 영역에 대해 OCR 수행
                    ocr_result = self.ocr.extract_text_from_screenshot(
                        x=screen_x,
                        y=screen_y,
                        width=region_width,
                        height=region_height,
                    )
                    
                    total_regions += 1
                    
                    if ocr_result.get("success") and ocr_result.get("text"):
                        text = ocr_result["text"].strip()
                        if text:
                            center_x = screen_x + region_width // 2
                            center_y = screen_y + region_height // 2
                            
                            region = TextRegion(
                                text=text,
                                x=screen_x,
                                y=screen_y,
                                width=region_width,
                                height=region_height,
                                center_x=center_x,
                                center_y=center_y,
                            )
                            text_regions.append(region)
                            regions.append(asdict(region))
            
            # DB에 저장 (window_id는 hwnd)
            timestamp = datetime.now().isoformat()
            conn = sqlite3.connect(str(self._db_path))
            for region in text_regions:
                conn.execute("""
                    INSERT INTO screen_regions 
                    (timestamp, window_id, text, x, y, width, height, center_x, center_y, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    hwnd,  # 윈도우 ID
                    region.text,
                    region.x,
                    region.y,
                    region.width,
                    region.height,
                    region.center_x,
                    region.center_y,
                    region.confidence,
                ))
            conn.commit()
            conn.close()
            
            logger.info(f"윈도우 인덱싱 완료: hwnd={hwnd}, {total_regions}개 영역, {len(text_regions)}개 텍스트 영역")
            
            return {
                "success": True,
                "hwnd": hwnd,
                "total_regions": total_regions,
                "text_regions": len(text_regions),
                "timestamp": timestamp,
                "grid_size": grid_size,
                "window_size": {"width": window_width, "height": window_height},
                "window_position": {"left": window_left, "top": window_top},
                "regions": regions[:50],  # 처음 50개만 반환 (컨텍스트 절약)
            }
        
        except Exception as e:
            logger.error(f"윈도우 인덱싱 실패: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def find_text(self, search_text: str, exact_match: bool = False, window_id: Optional[int] = None) -> dict:
        """
        텍스트 검색하여 위치 반환
        
        Args:
            search_text: 검색할 텍스트
            exact_match: 정확히 일치하는지 여부
            window_id: 윈도우 ID (None이면 전체 화면에서 검색)
        
        Returns:
            찾은 텍스트 영역 정보
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            
            if window_id is not None:
                # 특정 윈도우에서 검색
                if exact_match:
                    cursor = conn.execute("""
                        SELECT text, x, y, width, height, center_x, center_y, confidence, window_id
                        FROM screen_regions
                        WHERE text = ? AND window_id = ?
                        ORDER BY timestamp DESC
                        LIMIT 10
                    """, (search_text, window_id))
                else:
                    cursor = conn.execute("""
                        SELECT text, x, y, width, height, center_x, center_y, confidence, window_id
                        FROM screen_regions
                        WHERE text LIKE ? AND window_id = ?
                        ORDER BY timestamp DESC
                        LIMIT 10
                    """, (f"%{search_text}%", window_id))
            else:
                # 전체 화면에서 검색 (window_id가 NULL인 것만)
                if exact_match:
                    cursor = conn.execute("""
                        SELECT text, x, y, width, height, center_x, center_y, confidence, window_id
                        FROM screen_regions
                        WHERE text = ? AND window_id IS NULL
                        ORDER BY timestamp DESC
                        LIMIT 10
                    """, (search_text,))
                else:
                    cursor = conn.execute("""
                        SELECT text, x, y, width, height, center_x, center_y, confidence, window_id
                        FROM screen_regions
                        WHERE text LIKE ? AND window_id IS NULL
                        ORDER BY timestamp DESC
                        LIMIT 10
                    """, (f"%{search_text}%",))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "text": row[0],
                    "x": row[1],
                    "y": row[2],
                    "width": row[3],
                    "height": row[4],
                    "center_x": row[5],
                    "center_y": row[6],
                    "confidence": row[7],
                    "window_id": row[8],
                })
            
            conn.close()
            
            return {
                "success": True,
                "search_text": search_text,
                "window_id": window_id,
                "count": len(results),
                "regions": results,
            }
        
        except Exception as e:
            logger.error(f"텍스트 검색 실패: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def get_indexed_texts(self, limit: int = 100, window_id: Optional[int] = None) -> dict:
        """
        인덱싱된 텍스트 목록 조회
        
        Args:
            limit: 최대 반환 개수
            window_id: 윈도우 ID (None이면 전체 화면에서 조회)
        
        Returns:
            텍스트 목록
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            
            if window_id is not None:
                # 특정 윈도우에서 조회
                cursor = conn.execute("""
                    SELECT DISTINCT text, COUNT(*) as count
                    FROM screen_regions
                    WHERE window_id = ?
                    GROUP BY text
                    ORDER BY count DESC, text
                    LIMIT ?
                """, (window_id, limit))
            else:
                # 전체 화면에서 조회 (window_id가 NULL인 것만)
                cursor = conn.execute("""
                    SELECT DISTINCT text, COUNT(*) as count
                    FROM screen_regions
                    WHERE window_id IS NULL
                    GROUP BY text
                    ORDER BY count DESC, text
                    LIMIT ?
                """, (limit,))
            
            texts = [{"text": row[0], "count": row[1]} for row in cursor.fetchall()]
            conn.close()
            
            return {
                "success": True,
                "window_id": window_id,
                "count": len(texts),
                "texts": texts,
            }
        
        except Exception as e:
            logger.error(f"텍스트 목록 조회 실패: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _clear_index(self, window_id: Optional[int] = None):
        """
        인덱스 초기화
        
        Args:
            window_id: 윈도우 ID (None이면 전체 인덱스 삭제)
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            if window_id is not None:
                conn.execute("DELETE FROM screen_regions WHERE window_id = ?", (window_id,))
            else:
                conn.execute("DELETE FROM screen_regions WHERE window_id IS NULL")
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"인덱스 초기화 실패: {e}")
    
    def get_index_status(self, window_id: Optional[int] = None) -> dict:
        """
        현재 인덱싱 상태 조회
        
        Args:
            window_id: 윈도우 ID (None이면 전체 화면)
        
        Returns:
            인덱싱 상태 딕셔너리
        """
        from .smart_indexer import get_smart_indexer
        smart_indexer = get_smart_indexer()
        return smart_indexer.get_index_status(window_id)
    
    def clear_stale_index(self, max_age_seconds: int = 3600) -> dict:
        """
        오래된 인덱스 정리
        
        Args:
            max_age_seconds: 최대 유효 시간 (초, 기본 1시간)
        
        Returns:
            정리 결과 딕셔너리
        """
        from .smart_indexer import get_smart_indexer
        smart_indexer = get_smart_indexer()
        return smart_indexer.clear_stale_index(max_age_seconds)


# 전역 인스턴스
_indexer = None


def get_screen_indexer() -> ScreenIndexer:
    """화면 인덱서 싱글톤 인스턴스 반환"""
    global _indexer
    if _indexer is None:
        _indexer = ScreenIndexer()
    return _indexer

