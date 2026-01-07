"""
스마트 인덱싱 관리자
인덱싱 상태를 추적하고 필요시 자동으로 인덱싱을 수행
"""

import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

from .screen_indexer import get_screen_indexer
from .screenshot import get_screenshot_controller
from .window import get_window_controller

logger = logging.getLogger("mcp_desktop.smart_indexer")

# 인덱싱이 유효한 시간 (초) - 5분
INDEX_VALIDITY_SECONDS = 300


class SmartIndexer:
    """스마트 인덱싱 관리자"""
    
    def __init__(self):
        """스마트 인덱서 초기화"""
        self.indexer = get_screen_indexer()
        self.screenshot = get_screenshot_controller()
        self.window = get_window_controller()
        self._db_path = Path.home() / ".mcp_desktop" / "screen_index.db"
        self._init_metadata_table()
    
    def _init_metadata_table(self):
        """인덱싱 메타데이터 테이블 초기화"""
        try:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS index_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    window_id INTEGER UNIQUE,
                    last_indexed TEXT NOT NULL,
                    screen_width INTEGER,
                    screen_height INTEGER,
                    window_width INTEGER,
                    window_height INTEGER
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_window_id_meta ON index_metadata(window_id)
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"메타데이터 테이블 초기화 실패: {e}")
    
    def get_index_status(self, window_id: Optional[int] = None) -> dict:
        """
        현재 인덱싱 상태 조회
        
        Args:
            window_id: 윈도우 ID (None이면 전체 화면)
        
        Returns:
            인덱싱 상태 딕셔너리
        """
        try:
            conn = sqlite3.connect(str(self._db_path))
            
            # 메타데이터 조회
            if window_id is not None:
                cursor = conn.execute("""
                    SELECT last_indexed, window_width, window_height
                    FROM index_metadata
                    WHERE window_id = ?
                """, (window_id,))
            else:
                cursor = conn.execute("""
                    SELECT last_indexed, screen_width, screen_height
                    FROM index_metadata
                    WHERE window_id IS NULL
                """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                return {
                    "indexed": False,
                    "last_indexed": None,
                    "age_seconds": None,
                    "needs_indexing": True,
                }
            
            last_indexed_str = row[0]
            last_indexed = datetime.fromisoformat(last_indexed_str)
            age_seconds = (datetime.now() - last_indexed).total_seconds()
            
            # 화면 크기 확인 (전체 화면인 경우)
            if window_id is None:
                screen_info = self.screenshot.get_screen_size()
                if screen_info.get("success"):
                    current_width = screen_info["width"]
                    current_height = screen_info["height"]
                    stored_width = row[1]
                    stored_height = row[2]
                    
                    # 화면 크기가 변경되었으면 재인덱싱 필요
                    if stored_width != current_width or stored_height != current_height:
                        return {
                            "indexed": True,
                            "last_indexed": last_indexed_str,
                            "age_seconds": age_seconds,
                            "needs_indexing": True,
                            "reason": "screen_size_changed",
                        }
            
            # 윈도우 크기 확인 (특정 윈도우인 경우)
            else:
                window_rect = self.window.get_window_rect(window_id)
                if window_rect.get("success"):
                    current_width = window_rect["width"]
                    current_height = window_rect["height"]
                    stored_width = row[1]
                    stored_height = row[2]
                    
                    # 윈도우 크기가 변경되었으면 재인덱싱 필요
                    if stored_width != current_width or stored_height != current_height:
                        return {
                            "indexed": True,
                            "last_indexed": last_indexed_str,
                            "age_seconds": age_seconds,
                            "needs_indexing": True,
                            "reason": "window_size_changed",
                        }
            
            # 인덱싱이 오래되었으면 재인덱싱 필요
            needs_indexing = age_seconds > INDEX_VALIDITY_SECONDS
            
            return {
                "indexed": True,
                "last_indexed": last_indexed_str,
                "age_seconds": age_seconds,
                "needs_indexing": needs_indexing,
                "reason": "expired" if needs_indexing else None,
            }
        
        except Exception as e:
            logger.error(f"인덱싱 상태 조회 실패: {e}", exc_info=True)
            return {
                "indexed": False,
                "error": str(e),
                "needs_indexing": True,
            }
    
    def is_indexing_needed(self, window_id: Optional[int] = None) -> bool:
        """
        인덱싱이 필요한지 판단
        
        Args:
            window_id: 윈도우 ID (None이면 전체 화면)
        
        Returns:
            인덱싱 필요 여부
        """
        status = self.get_index_status(window_id)
        return status.get("needs_indexing", True)
    
    def get_index_age(self, window_id: Optional[int] = None) -> Optional[float]:
        """
        마지막 인덱싱 이후 경과 시간 (초)
        
        Args:
            window_id: 윈도우 ID (None이면 전체 화면)
        
        Returns:
            경과 시간 (초), 인덱싱이 없으면 None
        """
        status = self.get_index_status(window_id)
        return status.get("age_seconds")
    
    def ensure_indexed(
        self,
        window_id: Optional[int] = None,
        force: bool = False,
        grid_size: Optional[int] = None,
    ) -> dict:
        """
        인덱싱이 최신인지 확인하고 필요시 수행
        
        Args:
            window_id: 윈도우 ID (None이면 전체 화면)
            force: 강제 재인덱싱 여부
            grid_size: 그리드 크기 (None이면 기본값 사용)
        
        Returns:
            인덱싱 결과 딕셔너리
        """
        try:
            # 강제 재인덱싱이 아니면 상태 확인
            if not force:
                if not self.is_indexing_needed(window_id):
                    logger.info(f"인덱싱이 최신 상태입니다. window_id={window_id}")
                    return {
                        "success": True,
                        "indexed": False,  # 새로 인덱싱하지 않음
                        "message": "이미 최신 인덱싱이 있습니다.",
                    }
            
            # 인덱싱 수행
            logger.info(f"인덱싱 시작: window_id={window_id}, force={force}")
            
            if window_id is not None:
                result = self.indexer.index_window(hwnd=window_id, grid_size=grid_size)
            else:
                result = self.indexer.index_screen(grid_size=grid_size)
            
            if not result.get("success"):
                return result
            
            # 메타데이터 저장
            self._update_metadata(window_id, result)
            
            logger.info(f"인덱싱 완료: window_id={window_id}")
            return {
                "success": True,
                "indexed": True,  # 새로 인덱싱함
                "result": result,
            }
        
        except Exception as e:
            logger.error(f"인덱싱 보장 실패: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _update_metadata(self, window_id: Optional[int], index_result: dict):
        """
        인덱싱 메타데이터 업데이트
        
        Args:
            window_id: 윈도우 ID (None이면 전체 화면)
            index_result: 인덱싱 결과
        """
        try:
            timestamp = datetime.now().isoformat()
            conn = sqlite3.connect(str(self._db_path))
            
            if window_id is not None:
                # 윈도우 인덱싱
                window_size = index_result.get("window_size", {})
                conn.execute("""
                    INSERT OR REPLACE INTO index_metadata
                    (window_id, last_indexed, window_width, window_height)
                    VALUES (?, ?, ?, ?)
                """, (
                    window_id,
                    timestamp,
                    window_size.get("width"),
                    window_size.get("height"),
                ))
            else:
                # 전체 화면 인덱싱
                screen_size = index_result.get("screen_size", {})
                conn.execute("""
                    INSERT OR REPLACE INTO index_metadata
                    (window_id, last_indexed, screen_width, screen_height)
                    VALUES (?, ?, ?, ?)
                """, (
                    None,
                    timestamp,
                    screen_size.get("width"),
                    screen_size.get("height"),
                ))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"메타데이터 업데이트 실패: {e}", exc_info=True)
    
    def clear_stale_index(self, max_age_seconds: int = 3600) -> dict:
        """
        오래된 인덱스 정리
        
        Args:
            max_age_seconds: 최대 유효 시간 (초, 기본 1시간)
        
        Returns:
            정리 결과 딕셔너리
        """
        try:
            cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
            cutoff_str = cutoff_time.isoformat()
            
            conn = sqlite3.connect(str(self._db_path))
            
            # 오래된 인덱스 삭제
            cursor = conn.execute("""
                DELETE FROM screen_regions
                WHERE timestamp < ?
            """, (cutoff_str,))
            
            deleted_count = cursor.rowcount
            
            # 오래된 메타데이터 삭제
            cursor = conn.execute("""
                DELETE FROM index_metadata
                WHERE last_indexed < ?
            """, (cutoff_str,))
            
            deleted_meta_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"오래된 인덱스 정리: {deleted_count}개 영역, {deleted_meta_count}개 메타데이터")
            
            return {
                "success": True,
                "deleted_regions": deleted_count,
                "deleted_metadata": deleted_meta_count,
            }
        
        except Exception as e:
            logger.error(f"인덱스 정리 실패: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


# 전역 인스턴스
_smart_indexer = None


def get_smart_indexer() -> SmartIndexer:
    """스마트 인덱서 싱글톤 인스턴스 반환"""
    global _smart_indexer
    if _smart_indexer is None:
        _smart_indexer = SmartIndexer()
    return _smart_indexer

