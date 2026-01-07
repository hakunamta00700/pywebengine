"""
MCP Tools 정의 및 호출 처리
"""

import asyncio
import logging
from typing import Any, Dict, List
from mcp.types import Tool, TextContent

from .mouse import get_mouse_controller
from .keyboard import get_keyboard_controller
from .screenshot import get_screenshot_controller
from .window import get_window_controller
from .filesystem import get_filesystem_controller
from .ocr import get_ocr_controller
from .screen_indexer import get_screen_indexer
from .smart_indexer import get_smart_indexer

logger = logging.getLogger("mcp_desktop.tools")


def get_all_tools() -> List[Tool]:
    """
    모든 MCP Tools 목록 반환 (고수준 도구만 노출)
    
    Returns:
        Tool 객체 리스트
    """
    return [
        # 고수준 통합 도구
        Tool(
            name="click_text",
            description="화면에서 텍스트를 찾아서 클릭합니다. 인덱싱이 필요하면 자동으로 수행합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "클릭할 텍스트 (예: '저장', '확인', '로그인')",
                    },
                    "window_id": {
                        "type": "integer",
                        "description": "윈도우 핸들 (선택적). 지정하면 해당 윈도우에서만 검색합니다.",
                    },
                    "exact_match": {
                        "type": "boolean",
                        "default": False,
                        "description": "정확히 일치하는지 여부 (False면 부분 일치)",
                    },
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "default": "left",
                        "description": "클릭 버튼",
                    },
                },
                "required": ["search_text"],
            },
        ),
        Tool(
            name="type_text",
            description="텍스트가 있는 위치를 찾아서 해당 위치에 텍스트를 입력합니다. 먼저 입력 필드를 찾아 클릭한 후 텍스트를 입력합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "입력 필드를 찾기 위한 텍스트 (예: '이름', '검색', '주소')",
                    },
                    "text": {
                        "type": "string",
                        "description": "입력할 텍스트",
                    },
                    "window_id": {
                        "type": "integer",
                        "description": "윈도우 핸들 (선택적). 지정하면 해당 윈도우에서만 검색합니다.",
                    },
                    "exact_match": {
                        "type": "boolean",
                        "default": False,
                        "description": "정확히 일치하는지 여부 (False면 부분 일치)",
                    },
                },
                "required": ["search_text", "text"],
            },
        ),
        Tool(
            name="find_element",
            description="화면에서 텍스트나 요소를 찾아서 위치 정보를 반환합니다. 인덱싱이 필요하면 자동으로 수행합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "검색할 텍스트",
                    },
                    "window_id": {
                        "type": "integer",
                        "description": "윈도우 핸들 (선택적). 지정하면 해당 윈도우에서만 검색합니다.",
                    },
                    "exact_match": {
                        "type": "boolean",
                        "default": False,
                        "description": "정확히 일치하는지 여부 (False면 부분 일치)",
                    },
                },
                "required": ["search_text"],
            },
        ),
        Tool(
            name="interact_window",
            description="특정 윈도우에서 일련의 작업을 수행합니다. 윈도우를 찾아 활성화한 후 여러 작업을 순차적으로 실행합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_title": {
                        "type": "string",
                        "description": "윈도우 제목 (부분 일치)",
                    },
                    "actions": {
                        "type": "array",
                        "description": "수행할 작업 목록",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["click_text", "type", "key", "hotkey"],
                                    "description": "작업 유형",
                                },
                                "search_text": {
                                    "type": "string",
                                    "description": "click_text 작업 시 사용할 검색 텍스트",
                                },
                                "text": {
                                    "type": "string",
                                    "description": "type 작업 시 입력할 텍스트",
                                },
                                "key": {
                                    "type": "string",
                                    "description": "key 작업 시 누를 키",
                                },
                                "keys": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "hotkey 작업 시 사용할 키 조합",
                                },
                            },
                            "required": ["type"],
                        },
                    },
                },
                "required": ["window_title", "actions"],
            },
        ),
        # 유틸리티 도구 (필요한 경우에만 사용)
        Tool(
            name="window_find",
            description="윈도우 찾기",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "윈도우 제목 (부분 일치)"},
                    "class_name": {"type": "string", "description": "윈도우 클래스명"},
                },
            },
        ),
        Tool(
            name="filesystem_read_file",
            description="파일 읽기",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "파일 경로"},
                    "encoding": {"type": "string", "default": "utf-8", "description": "인코딩"},
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="filesystem_list_directory",
            description="디렉토리 목록 조회",
            inputSchema={
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "default": ".",
                        "description": "디렉토리 경로",
                    },
                },
            },
        ),
    ]


async def call_tool(name: str, arguments: Dict[str, Any]) -> str:
    """
    Tool 호출 처리
    
    Args:
        name: Tool 이름
        arguments: Tool 인자
    
    Returns:
        결과 JSON 문자열
    """
    import json
    
    try:
        mouse = get_mouse_controller()
        keyboard = get_keyboard_controller()
        screenshot = get_screenshot_controller()
        window = get_window_controller()
        filesystem = get_filesystem_controller()
        ocr = get_ocr_controller()
        screen_indexer = get_screen_indexer()
        smart_indexer = get_smart_indexer()
        
        result = None
        
        # 고수준 통합 도구
        if name == "click_text":
            result = _handle_click_text(
                arguments, mouse, screen_indexer, smart_indexer
            )
        elif name == "type_text":
            result = _handle_type_text(
                arguments, mouse, keyboard, screen_indexer, smart_indexer
            )
        elif name == "find_element":
            result = _handle_find_element(
                arguments, screen_indexer, smart_indexer
            )
        elif name == "interact_window":
            result = await _handle_interact_window(
                arguments, mouse, keyboard, window, screen_indexer, smart_indexer
            )
        
        # 저수준 도구들 (내부적으로만 사용, 고수준 도구에서 호출)
        elif name == "mouse_click":
            result = mouse.click(
                x=arguments.get("x"),
                y=arguments.get("y"),
                button=arguments.get("button", "left"),
                clicks=arguments.get("clicks", 1),
                interval=arguments.get("interval", 0.0),
            )
        elif name == "mouse_move":
            result = mouse.move(
                x=arguments["x"],
                y=arguments["y"],
                duration=arguments.get("duration", 0.0),
            )
        elif name == "mouse_drag":
            result = mouse.drag(
                start_x=arguments["start_x"],
                start_y=arguments["start_y"],
                end_x=arguments["end_x"],
                end_y=arguments["end_y"],
                duration=arguments.get("duration", 0.5),
                button=arguments.get("button", "left"),
            )
        elif name == "mouse_scroll":
            result = mouse.scroll(
                x=arguments.get("x"),
                y=arguments.get("y"),
                clicks=arguments.get("clicks", 3),
            )
        elif name == "mouse_get_position":
            result = mouse.get_position()
        
        # 키보드 제어
        elif name == "keyboard_type":
            result = keyboard.type(
                text=arguments["text"],
                interval=arguments.get("interval", 0.0),
            )
        elif name == "keyboard_press":
            result = keyboard.press(
                key=arguments["key"],
                presses=arguments.get("presses", 1),
                interval=arguments.get("interval", 0.0),
            )
        elif name == "keyboard_hotkey":
            result = keyboard.hotkey(*arguments["keys"])
        
        # 스크린샷
        # 주의: screenshot_full은 컨텍스트를 많이 소모하므로 제공하지 않음
        # 대신 screen_index를 사용하여 텍스트 기반으로 작업하세요
        elif name == "screenshot_region":
            result = screenshot.capture_region(
                x=arguments["x"],
                y=arguments["y"],
                width=arguments["width"],
                height=arguments["height"],
                format=arguments.get("format", "PNG"),
            )
        elif name == "screenshot_get_size":
            result = screenshot.get_screen_size()
        elif name == "screenshot_get_pixel_color":
            result = screenshot.get_pixel_color(x=arguments["x"], y=arguments["y"])
        
        # 윈도우 관리
        elif name == "window_find":
            result = window.find_window(
                title=arguments.get("title"),
                class_name=arguments.get("class_name"),
            )
        elif name == "window_activate":
            result = window.activate_window(hwnd=arguments["hwnd"])
        elif name == "window_get_info":
            result = window.get_window_info(hwnd=arguments["hwnd"])
        
        # 파일 시스템
        elif name == "filesystem_read_file":
            result = filesystem.read_file(
                file_path=arguments["file_path"],
                encoding=arguments.get("encoding", "utf-8"),
            )
        elif name == "filesystem_list_directory":
            result = filesystem.list_directory(dir_path=arguments.get("dir_path", "."))
        elif name == "filesystem_get_file_info":
            result = filesystem.get_file_info(file_path=arguments["file_path"])
        
        # OCR
        elif name == "ocr_extract_from_image":
            result = ocr.extract_text_from_image(
                image_base64=arguments["image_base64"],
                lang=arguments.get("lang", "kor+eng"),
            )
        elif name == "ocr_extract_from_screenshot":
            result = ocr.extract_text_from_screenshot(
                x=arguments.get("x"),
                y=arguments.get("y"),
                width=arguments.get("width"),
                height=arguments.get("height"),
                lang=arguments.get("lang", "kor+eng"),
            )
        
        # 화면 인덱싱
        elif name == "screen_index":
            result = screen_indexer.index_screen(
                grid_size=arguments.get("grid_size"),
            )
        elif name == "screen_index_window":
            result = screen_indexer.index_window(
                hwnd=arguments["hwnd"],
                grid_size=arguments.get("grid_size"),
            )
        elif name == "screen_find_text":
            result = screen_indexer.find_text(
                search_text=arguments["search_text"],
                exact_match=arguments.get("exact_match", False),
                window_id=arguments.get("window_id"),
            )
        elif name == "screen_get_indexed_texts":
            result = screen_indexer.get_indexed_texts(
                limit=arguments.get("limit", 100),
                window_id=arguments.get("window_id"),
            )
        
        else:
            return json.dumps({"error": f"알 수 없는 도구: {name}"})
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"도구 호출 오류 ({name}): {e}", exc_info=True)
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# 고수준 도구 핸들러 함수들

def _handle_click_text(
    arguments: Dict[str, Any],
    mouse,
    screen_indexer,
    smart_indexer,
) -> dict:
    """
    텍스트를 찾아서 클릭하는 고수준 도구 핸들러
    
    Args:
        arguments: 도구 인자
        mouse: 마우스 컨트롤러
        screen_indexer: 화면 인덱서
        smart_indexer: 스마트 인덱서
    
    Returns:
        작업 결과 딕셔너리
    """
    try:
        search_text = arguments["search_text"]
        window_id = arguments.get("window_id")
        exact_match = arguments.get("exact_match", False)
        button = arguments.get("button", "left")
        
        # 인덱싱 보장
        index_result = smart_indexer.ensure_indexed(window_id=window_id)
        if not index_result.get("success"):
            return {
                "success": False,
                "error": f"인덱싱 실패: {index_result.get('error')}",
            }
        
        # 텍스트 검색
        find_result = screen_indexer.find_text(
            search_text=search_text,
            exact_match=exact_match,
            window_id=window_id,
        )
        
        if not find_result.get("success"):
            return {
                "success": False,
                "error": f"텍스트 검색 실패: {find_result.get('error')}",
            }
        
        regions = find_result.get("regions", [])
        if not regions:
            return {
                "success": False,
                "error": f"텍스트를 찾을 수 없습니다: '{search_text}'",
                "search_result": find_result,
            }
        
        # 첫 번째 결과를 클릭
        first_region = regions[0]
        center_x = first_region["center_x"]
        center_y = first_region["center_y"]
        
        # 클릭 수행
        click_result = mouse.click(x=center_x, y=center_y, button=button)
        
        if not click_result.get("success"):
            return click_result
        
        return {
            "success": True,
            "clicked_text": search_text,
            "position": (center_x, center_y),
            "region": first_region,
            "all_matches": len(regions),
        }
    
    except Exception as e:
        logger.error(f"click_text 처리 실패: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def _handle_type_text(
    arguments: Dict[str, Any],
    mouse,
    keyboard,
    screen_indexer,
    smart_indexer,
) -> dict:
    """
    텍스트 위치를 찾아서 입력하는 고수준 도구 핸들러
    
    Args:
        arguments: 도구 인자
        mouse: 마우스 컨트롤러
        keyboard: 키보드 컨트롤러
        screen_indexer: 화면 인덱서
        smart_indexer: 스마트 인덱서
    
    Returns:
        작업 결과 딕셔너리
    """
    try:
        search_text = arguments["search_text"]
        text = arguments["text"]
        window_id = arguments.get("window_id")
        exact_match = arguments.get("exact_match", False)
        
        # 인덱싱 보장
        index_result = smart_indexer.ensure_indexed(window_id=window_id)
        if not index_result.get("success"):
            return {
                "success": False,
                "error": f"인덱싱 실패: {index_result.get('error')}",
            }
        
        # 입력 필드 찾기
        find_result = screen_indexer.find_text(
            search_text=search_text,
            exact_match=exact_match,
            window_id=window_id,
        )
        
        if not find_result.get("success"):
            return {
                "success": False,
                "error": f"입력 필드 검색 실패: {find_result.get('error')}",
            }
        
        regions = find_result.get("regions", [])
        if not regions:
            return {
                "success": False,
                "error": f"입력 필드를 찾을 수 없습니다: '{search_text}'",
                "search_result": find_result,
            }
        
        # 첫 번째 결과를 클릭
        first_region = regions[0]
        center_x = first_region["center_x"]
        center_y = first_region["center_y"]
        
        # 클릭 후 입력
        click_result = mouse.click(x=center_x, y=center_y)
        if not click_result.get("success"):
            return {
                "success": False,
                "error": f"클릭 실패: {click_result.get('error')}",
            }
        
        # 텍스트 입력
        type_result = keyboard.type(text=text)
        if not type_result.get("success"):
            return {
                "success": False,
                "error": f"텍스트 입력 실패: {type_result.get('error')}",
            }
        
        return {
            "success": True,
            "field_text": search_text,
            "input_text": text,
            "position": (center_x, center_y),
            "region": first_region,
        }
    
    except Exception as e:
        logger.error(f"type_text 처리 실패: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def _handle_find_element(
    arguments: Dict[str, Any],
    screen_indexer,
    smart_indexer,
) -> dict:
    """
    화면에서 요소를 찾는 고수준 도구 핸들러
    
    Args:
        arguments: 도구 인자
        screen_indexer: 화면 인덱서
        smart_indexer: 스마트 인덱서
    
    Returns:
        작업 결과 딕셔너리
    """
    try:
        search_text = arguments["search_text"]
        window_id = arguments.get("window_id")
        exact_match = arguments.get("exact_match", False)
        
        # 인덱싱 보장
        index_result = smart_indexer.ensure_indexed(window_id=window_id)
        if not index_result.get("success"):
            return {
                "success": False,
                "error": f"인덱싱 실패: {index_result.get('error')}",
            }
        
        # 텍스트 검색
        find_result = screen_indexer.find_text(
            search_text=search_text,
            exact_match=exact_match,
            window_id=window_id,
        )
        
        if not find_result.get("success"):
            return find_result
        
        regions = find_result.get("regions", [])
        if not regions:
            return {
                "success": True,
                "found": False,
                "search_text": search_text,
                "message": f"텍스트를 찾을 수 없습니다: '{search_text}'",
            }
        
        return {
            "success": True,
            "found": True,
            "search_text": search_text,
            "count": len(regions),
            "regions": regions,
        }
    
    except Exception as e:
        logger.error(f"find_element 처리 실패: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def _handle_interact_window(
    arguments: Dict[str, Any],
    mouse,
    keyboard,
    window,
    screen_indexer,
    smart_indexer,
) -> dict:
    """
    윈도우에서 일련의 작업을 수행하는 고수준 도구 핸들러
    
    Args:
        arguments: 도구 인자
        mouse: 마우스 컨트롤러
        keyboard: 키보드 컨트롤러
        window: 윈도우 컨트롤러
        screen_indexer: 화면 인덱서
        smart_indexer: 스마트 인덱서
    
    Returns:
        작업 결과 딕셔너리
    """
    try:
        window_title = arguments["window_title"]
        actions = arguments["actions"]
        
        # 윈도우 찾기
        find_result = window.find_window(title=window_title)
        if not find_result.get("success"):
            return {
                "success": False,
                "error": f"윈도우 찾기 실패: {find_result.get('error')}",
            }
        
        windows = find_result.get("windows", [])
        if not windows:
            return {
                "success": False,
                "error": f"윈도우를 찾을 수 없습니다: '{window_title}'",
            }
        
        # 첫 번째 윈도우 사용
        target_window = windows[0]
        hwnd = target_window["hwnd"]
        
        # 윈도우 활성화
        activate_result = window.activate_window(hwnd=hwnd)
        if not activate_result.get("success"):
            return {
                "success": False,
                "error": f"윈도우 활성화 실패: {activate_result.get('error')}",
            }
        
        # 윈도우 인덱싱 보장
        index_result = smart_indexer.ensure_indexed(window_id=hwnd)
        if not index_result.get("success"):
            return {
                "success": False,
                "error": f"윈도우 인덱싱 실패: {index_result.get('error')}",
            }
        
        # 작업 수행
        results = []
        for i, action in enumerate(actions):
            action_type = action.get("type")
            
            try:
                if action_type == "click_text":
                    search_text = action.get("search_text")
                    if not search_text:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": "search_text가 필요합니다",
                        })
                        continue
                    
                    click_result = _handle_click_text(
                        {
                            "search_text": search_text,
                            "window_id": hwnd,
                            "exact_match": action.get("exact_match", False),
                            "button": action.get("button", "left"),
                        },
                        mouse,
                        screen_indexer,
                        smart_indexer,
                    )
                    results.append({"index": i, "type": "click_text", **click_result})
                
                elif action_type == "type":
                    text = action.get("text")
                    if not text:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": "text가 필요합니다",
                        })
                        continue
                    
                    type_result = keyboard.type(text=text)
                    results.append({"index": i, "type": "type", **type_result})
                
                elif action_type == "key":
                    key = action.get("key")
                    if not key:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": "key가 필요합니다",
                        })
                        continue
                    
                    key_result = keyboard.press(key=key)
                    results.append({"index": i, "type": "key", **key_result})
                
                elif action_type == "hotkey":
                    keys = action.get("keys")
                    if not keys:
                        results.append({
                            "index": i,
                            "success": False,
                            "error": "keys가 필요합니다",
                        })
                        continue
                    
                    hotkey_result = keyboard.hotkey(*keys)
                    results.append({"index": i, "type": "hotkey", **hotkey_result})
                
                else:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": f"알 수 없는 작업 유형: {action_type}",
                    })
            
            except Exception as e:
                logger.error(f"작업 {i} 수행 실패: {e}", exc_info=True)
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e),
                })
        
        # 전체 성공 여부 확인
        all_success = all(r.get("success", False) for r in results)
        
        return {
            "success": all_success,
            "window": target_window,
            "actions_count": len(actions),
            "results": results,
        }
    
    except Exception as e:
        logger.error(f"interact_window 처리 실패: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

