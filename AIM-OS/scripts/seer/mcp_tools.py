"""
AIM-OS SEER — MCP Tool Definitions

Exposes the entire SEER Automation Platform as callable MCP tools.
Any agent (Opus, Sev, Codex, Gemini) can call these to:
- Capture and store UI elements
- Find elements on screen
- Execute clicks, types, scrolls
- Build and run automations
- Manage the element library

These tool definitions are designed to be registered with the
AIM-OS MCP server (scripts/mcp_server.py).

Usage in MCP server:
    from seer.mcp_tools import register_seer_tools
    register_seer_tools(mcp_server)
"""

import os
import sys
import json
import time
from typing import Optional, Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seer.element_library import ElementLibrary, Element
from seer.capture import CaptureEngine
from seer.automation import AutomationEngine, Automation, Action, ActionType
from seer.kinematics import MouseKinematics


# ── Singleton Instances ────────────────────────────────────

_library: Optional[ElementLibrary] = None
_capture: Optional[CaptureEngine] = None
_engine: Optional[AutomationEngine] = None
_kinematics: Optional[MouseKinematics] = None


def _get_library() -> ElementLibrary:
    global _library
    if _library is None:
        _library = ElementLibrary()
    return _library


def _get_capture() -> CaptureEngine:
    global _capture
    if _capture is None:
        _capture = CaptureEngine(_get_library())
    return _capture


def _get_engine() -> AutomationEngine:
    global _engine
    if _engine is None:
        _engine = AutomationEngine(_get_library(), _get_capture(), _get_kinematics())
    return _engine


def _get_kinematics() -> MouseKinematics:
    global _kinematics
    if _kinematics is None:
        _kinematics = MouseKinematics()
    return _kinematics


# ══════════════════════════════════════════════════════════
# ELEMENT LIBRARY TOOLS
# ══════════════════════════════════════════════════════════

def seer_register_app(app_name: str, description: str = '',
                      window_title_pattern: str = '') -> dict:
    """Register a new application in SEER's element library."""
    return _get_library().register_app(app_name, description, window_title_pattern)


def seer_register_page(app: str, page: str,
                       url_pattern: str = '',
                       description: str = '') -> dict:
    """Register a page within an application."""
    return _get_library().register_page(app, page, url_pattern, description)


def seer_list_apps() -> list:
    """List all registered applications."""
    return _get_library().list_apps()


def seer_list_pages(app: str) -> list:
    """List all pages for an application."""
    return _get_library().list_pages(app)


def seer_list_elements(app: str, page: str) -> list:
    """List all stored elements for an app/page."""
    return _get_library().list_elements(app, page)


def seer_search_elements(query: str = '', app: str = None,
                         element_type: str = None) -> list:
    """Search elements across all apps and pages."""
    elements = _get_library().search(query, app, element_type)
    return [e.to_dict() for e in elements]


def seer_get_element(app: str, page: str, name: str) -> dict:
    """Get full details of a stored element."""
    element = _get_library().get_element(app, page, name)
    if element:
        return element.to_dict()
    return {'error': f'Element not found: {app}/{page}/{name}'}


def seer_library_stats() -> dict:
    """Get element library statistics."""
    return _get_library().get_stats()


def seer_export_manifest() -> dict:
    """Export the complete library manifest."""
    return _get_library().export_manifest()


def seer_delete_element(app: str, page: str, name: str) -> dict:
    """Delete an element from the library."""
    return _get_library().delete_element(app, page, name)


# ══════════════════════════════════════════════════════════
# CAPTURE & LEARNING TOOLS
# ══════════════════════════════════════════════════════════

def seer_capture_element(app: str, page: str, name: str,
                         x: int, y: int, w: int, h: int,
                         element_type: str = 'button',
                         selector: str = '',
                         description: str = '',
                         tags: str = '') -> dict:
    """
    Capture a UI element from the screen and store it.
    This is the primary LEARNING operation — capture once, use forever.

    Args:
        app: Application name (e.g., 'chatgpt')
        page: Page name (e.g., 'main')
        name: Element name (e.g., 'send_button')
        x, y: Screen coordinates of the element's top-left corner
        w, h: Element dimensions in pixels
        element_type: button, input, link, tab, menu, icon, text, region
        selector: CSS selector (if from DOM)
        description: Human-readable description
        tags: Comma-separated tags for search
    """
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    return _get_capture().capture_element(
        app, page, name, x, y, w, h,
        element_type=element_type,
        selector=selector,
        description=description,
        tags=tag_list
    )


def seer_import_dom_elements(app: str, page: str,
                              dom_elements_json: str) -> dict:
    """
    Import elements from Chrome extension DOM spatial map.
    Pass the JSON array of DOM elements.
    """
    elements = json.loads(dom_elements_json) if isinstance(dom_elements_json, str) else dom_elements_json
    return _get_capture().import_from_dom(app, page, elements)


def seer_verify_element(app: str, page: str, name: str,
                        confidence: float = 0.7) -> dict:
    """
    Verify a stored element can be found on the current screen.
    Returns confidence score and current position.
    """
    return _get_capture().verify_element(app, page, name, confidence)


def seer_verify_page(app: str, page: str) -> dict:
    """Verify all elements for a page. Returns calibration report."""
    return _get_capture().verify_all_elements(app, page)


# ══════════════════════════════════════════════════════════
# DIRECT ACTION TOOLS
# ══════════════════════════════════════════════════════════

def seer_find_and_click(app: str, page: str, element: str,
                        button: str = 'left',
                        double: bool = False) -> dict:
    """
    Find a stored element on screen and click it.
    The primary EXECUTION tool — agents call this to interact with any UI.
    """
    capture = _get_capture()
    pos = capture.find_element_on_screen(app, page, element)

    if not pos:
        return {'success': False, 'error': f'Element not found: {element}'}

    kinematics = _get_kinematics()
    kinematics.move_to(pos['center_x'], pos['center_y'],
                       click=True, button=button, double=double)

    return {
        'success': True,
        'element': element,
        'clicked_at': {'x': pos['center_x'], 'y': pos['center_y']},
        'button': button,
        'double': double
    }


def seer_find_click_type(app: str, page: str, element: str,
                          text: str) -> dict:
    """Find an element, click it, then type text into it."""
    click_result = seer_find_and_click(app, page, element)
    if not click_result.get('success'):
        return click_result

    time.sleep(0.2)

    import pyautogui
    pyautogui.typewrite(text, interval=0.02) if text.isascii() else pyautogui.write(text)

    return {
        'success': True,
        'element': element,
        'typed': text[:100],
        'clicked_at': click_result['clicked_at']
    }


def seer_find_element(name: str) -> dict:
    """
    Search for an element by name across ALL apps/pages.
    Returns its current screen position if found.
    """
    result = _get_capture().find_any_element(name)
    if result:
        return {'found': True, **result}
    return {'found': False, 'element': name}


def seer_move_mouse(x: int, y: int, click: bool = False,
                    button: str = 'left') -> dict:
    """Move mouse to absolute screen coordinates with Bezier kinematics."""
    kinematics = _get_kinematics()
    kinematics.move_to(x, y, click=click, button=button)
    return {'success': True, 'moved_to': {'x': x, 'y': y}, 'clicked': click}


def seer_type_text(text: str) -> dict:
    """Type text at the current cursor position."""
    import pyautogui
    pyautogui.typewrite(text, interval=0.02) if text.isascii() else pyautogui.write(text)
    return {'success': True, 'typed': text[:100], 'length': len(text)}


def seer_hotkey(*keys: str) -> dict:
    """Execute a keyboard shortcut (e.g., 'ctrl', 's')."""
    import pyautogui
    pyautogui.hotkey(*keys)
    return {'success': True, 'keys': list(keys)}


def seer_scroll(direction: str = 'down', amount: int = 3) -> dict:
    """Scroll up or down."""
    import pyautogui
    clicks = amount if direction == 'down' else -amount
    pyautogui.scroll(clicks)
    return {'success': True, 'direction': direction, 'amount': amount}


def seer_screenshot(region: str = None) -> dict:
    """
    Take a screenshot. Optionally specify a region as 'x,y,w,h'.
    Returns the path to the saved screenshot.
    """
    capture = _get_capture()
    save_dir = capture.library.root.parent / 'screenshots'
    save_dir.mkdir(parents=True, exist_ok=True)
    filename = f'screenshot_{int(time.time())}.png'
    save_path = save_dir / filename

    if region:
        parts = [int(p.strip()) for p in region.split(',')]
        frame = capture.capture_region(*parts[:4])
    else:
        frame = capture.capture_full_screen()

    import cv2
    cv2.imwrite(str(save_path), frame)

    return {'success': True, 'path': str(save_path), 'shape': list(frame.shape)}


def seer_focus_window(title: str) -> dict:
    """Focus a window by title (partial match)."""
    import pygetwindow as gw
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        return {'success': False, 'error': f'No window matching: {title}'}
    windows[0].activate()
    return {'success': True, 'window': windows[0].title}


# ══════════════════════════════════════════════════════════
# AUTOMATION TOOLS
# ══════════════════════════════════════════════════════════

def seer_create_automation(name: str, description: str = '',
                            created_by: str = '',
                            tags: str = '') -> dict:
    """Create a new empty automation workflow."""
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    auto = Automation(
        name=name,
        description=description,
        created_by=created_by,
        tags=tag_list
    )
    engine = _get_engine()
    return engine.save(auto)


def seer_add_action(automation_name: str,
                     action_type: str,
                     app: str = '', page: str = '', element: str = '',
                     params_json: str = '{}',
                     description: str = '',
                     on_fail: str = 'abort') -> dict:
    """
    Add an action to an existing automation.

    action_type: click, double_click, right_click, type, hotkey,
                 scroll, wait, wait_for, verify, focus_window, screenshot
    params_json: JSON string of action parameters
                 type: {"text": "hello"}
                 hotkey: {"keys": ["ctrl", "s"]}
                 scroll: {"direction": "down", "amount": 3}
                 wait: {"seconds": 2.0}
    """
    engine = _get_engine()
    auto = engine.get(automation_name)
    if not auto:
        return {'error': f'Automation not found: {automation_name}'}

    params = json.loads(params_json) if isinstance(params_json, str) else params_json

    action = Action(
        action_type=action_type,
        app=app,
        page=page,
        element=element,
        params=params,
        description=description,
        on_fail=on_fail
    )

    auto.actions.append(action)
    engine.save(auto)

    return {
        'success': True,
        'automation': automation_name,
        'action_added': action_type,
        'total_steps': len(auto.actions)
    }


def seer_run_automation(name: str, dry_run: bool = False) -> dict:
    """
    Run a saved automation by name.
    Set dry_run=True to simulate without moving the mouse.
    """
    return _get_engine().run_by_name(name, dry_run=dry_run)


def seer_list_automations() -> list:
    """List all saved automations."""
    return _get_engine().list_automations()


def seer_delete_automation(name: str) -> dict:
    """Delete a saved automation."""
    return _get_engine().delete(name)


def seer_quick_automation(name: str, steps_json: str,
                           created_by: str = '') -> dict:
    """
    Create and save a complete automation from a JSON steps array.

    steps_json format:
    [
        {"action": "click", "app": "chatgpt", "page": "main", "element": "input_box"},
        {"action": "type", "params": {"text": "Hello!"}},
        {"action": "click", "app": "chatgpt", "page": "main", "element": "send_button"},
        {"action": "wait", "params": {"seconds": 2}},
        {"action": "verify", "app": "chatgpt", "page": "main", "element": "response_area"}
    ]
    """
    steps = json.loads(steps_json) if isinstance(steps_json, str) else steps_json

    auto = Automation(name=name, created_by=created_by)

    for step in steps:
        action = Action(
            action_type=step.get('action', 'click'),
            app=step.get('app', ''),
            page=step.get('page', ''),
            element=step.get('element', ''),
            params=step.get('params', {}),
            description=step.get('description', ''),
            on_fail=step.get('on_fail', 'abort')
        )
        auto.actions.append(action)

    engine = _get_engine()
    engine.save(auto)

    return {
        'success': True,
        'automation': name,
        'steps': len(auto.actions),
        'created_by': created_by
    }


# ══════════════════════════════════════════════════════════
# REGISTRATION
# ══════════════════════════════════════════════════════════

# All tool definitions for MCP server registration
SEER_TOOLS = {
    # Element Library
    'seer_register_app': seer_register_app,
    'seer_register_page': seer_register_page,
    'seer_list_apps': seer_list_apps,
    'seer_list_pages': seer_list_pages,
    'seer_list_elements': seer_list_elements,
    'seer_search_elements': seer_search_elements,
    'seer_get_element': seer_get_element,
    'seer_library_stats': seer_library_stats,
    'seer_export_manifest': seer_export_manifest,
    'seer_delete_element': seer_delete_element,

    # Capture & Learning
    'seer_capture_element': seer_capture_element,
    'seer_import_dom_elements': seer_import_dom_elements,
    'seer_verify_element': seer_verify_element,
    'seer_verify_page': seer_verify_page,

    # Direct Actions
    'seer_find_and_click': seer_find_and_click,
    'seer_find_click_type': seer_find_click_type,
    'seer_find_element': seer_find_element,
    'seer_move_mouse': seer_move_mouse,
    'seer_type_text': seer_type_text,
    'seer_hotkey': seer_hotkey,
    'seer_scroll': seer_scroll,
    'seer_screenshot': seer_screenshot,
    'seer_focus_window': seer_focus_window,

    # Automations
    'seer_create_automation': seer_create_automation,
    'seer_add_action': seer_add_action,
    'seer_run_automation': seer_run_automation,
    'seer_list_automations': seer_list_automations,
    'seer_delete_automation': seer_delete_automation,
    'seer_quick_automation': seer_quick_automation,
}


def register_seer_tools(mcp_server):
    """
    Register all SEER tools with an MCP server instance.
    Call this from the main MCP server setup.

    Usage:
        from seer.mcp_tools import register_seer_tools
        register_seer_tools(my_mcp_server)
    """
    for name, func in SEER_TOOLS.items():
        mcp_server.tool(name)(func)

    return {'registered': len(SEER_TOOLS), 'tools': list(SEER_TOOLS.keys())}
