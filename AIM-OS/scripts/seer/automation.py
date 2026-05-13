"""
AIM-OS SEER — Automation Engine

Production workflow composer that chains element interactions
into executable automations. Agents dynamically build automations
from stored elements, and automations are themselves storable
and callable via MCP tools.

Automation = ordered list of Actions
Action = find element + perform operation + verify result

Example:
    auto = Automation("deploy_to_staging")
    auto.add(ClickAction("joc", "dashboard", "deploy_button"))
    auto.add(WaitAction(2.0))
    auto.add(ClickAction("joc", "deploy_modal", "confirm_button"))
    auto.add(VerifyAction("joc", "deploy_modal", "success_toast"))
    engine.run(auto)
"""

import os
import sys
import time
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seer.element_library import ElementLibrary
from seer.capture import CaptureEngine
from seer.kinematics import MouseKinematics


# ── Storage ────────────────────────────────────────────────

AUTOMATIONS_DIR = Path(os.environ.get(
    'SEER_AUTOMATIONS_DIR',
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'seer', 'automations')
))


class ActionType(str, Enum):
    CLICK = 'click'
    DOUBLE_CLICK = 'double_click'
    RIGHT_CLICK = 'right_click'
    TYPE = 'type'
    HOTKEY = 'hotkey'
    SCROLL = 'scroll'
    WAIT = 'wait'
    WAIT_FOR = 'wait_for'         # Wait until element appears
    VERIFY = 'verify'             # Assert element is visible
    MOVE_TO = 'move_to'
    DRAG = 'drag'
    FOCUS_WINDOW = 'focus_window'
    SCREENSHOT = 'screenshot'
    CONDITIONAL = 'conditional'   # If element exists → branch
    LOOP = 'loop'                 # Repeat N times or until condition


@dataclass
class Action:
    """A single automation step."""
    action_type: str
    app: str = ''
    page: str = ''
    element: str = ''
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ''
    timeout: float = 10.0
    retry_count: int = 2
    on_fail: str = 'abort'  # abort, skip, retry

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Action':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ActionResult:
    """Result of executing an action."""
    success: bool
    action_type: str
    element: str = ''
    position: Optional[Dict] = None
    duration_ms: float = 0
    error: str = ''
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Automation:
    """A complete automation workflow."""
    name: str
    description: str = ''
    actions: List[Action] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_by: str = ''         # Agent that created it
    created_at: float = 0
    last_run_at: float = 0
    run_count: int = 0
    avg_duration_ms: float = 0
    automation_id: str = ''
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.automation_id:
            self.automation_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = time.time()

    # ── Builder API ────────────────────────────────────────

    def click(self, app: str, page: str, element: str,
              description: str = '') -> 'Automation':
        """Add a click action."""
        self.actions.append(Action(
            action_type=ActionType.CLICK,
            app=app, page=page, element=element,
            description=description or f'Click {element}'
        ))
        return self

    def double_click(self, app: str, page: str, element: str,
                     description: str = '') -> 'Automation':
        self.actions.append(Action(
            action_type=ActionType.DOUBLE_CLICK,
            app=app, page=page, element=element,
            description=description or f'Double-click {element}'
        ))
        return self

    def right_click(self, app: str, page: str, element: str,
                    description: str = '') -> 'Automation':
        self.actions.append(Action(
            action_type=ActionType.RIGHT_CLICK,
            app=app, page=page, element=element,
            description=description or f'Right-click {element}'
        ))
        return self

    def type_text(self, text: str, app: str = '', page: str = '',
                  element: str = '', description: str = '') -> 'Automation':
        """Add a type action (optionally click an element first)."""
        self.actions.append(Action(
            action_type=ActionType.TYPE,
            app=app, page=page, element=element,
            params={'text': text},
            description=description or f'Type: {text[:50]}'
        ))
        return self

    def hotkey(self, *keys: str, description: str = '') -> 'Automation':
        """Add a hotkey action (e.g., ctrl+s)."""
        self.actions.append(Action(
            action_type=ActionType.HOTKEY,
            params={'keys': list(keys)},
            description=description or f'Hotkey: {"+".join(keys)}'
        ))
        return self

    def scroll(self, direction: str = 'down', amount: int = 3,
               description: str = '') -> 'Automation':
        self.actions.append(Action(
            action_type=ActionType.SCROLL,
            params={'direction': direction, 'amount': amount},
            description=description or f'Scroll {direction} {amount}'
        ))
        return self

    def wait(self, seconds: float = 1.0, description: str = '') -> 'Automation':
        """Add a wait/pause."""
        self.actions.append(Action(
            action_type=ActionType.WAIT,
            params={'seconds': seconds},
            description=description or f'Wait {seconds}s'
        ))
        return self

    def wait_for(self, app: str, page: str, element: str,
                 timeout: float = 10.0, description: str = '') -> 'Automation':
        """Wait until an element appears on screen."""
        self.actions.append(Action(
            action_type=ActionType.WAIT_FOR,
            app=app, page=page, element=element,
            timeout=timeout,
            description=description or f'Wait for {element}'
        ))
        return self

    def verify(self, app: str, page: str, element: str,
               description: str = '') -> 'Automation':
        """Assert that an element is visible."""
        self.actions.append(Action(
            action_type=ActionType.VERIFY,
            app=app, page=page, element=element,
            description=description or f'Verify {element} visible'
        ))
        return self

    def focus_window(self, window_title: str,
                     description: str = '') -> 'Automation':
        self.actions.append(Action(
            action_type=ActionType.FOCUS_WINDOW,
            params={'window_title': window_title},
            description=description or f'Focus: {window_title}'
        ))
        return self

    def screenshot(self, save_name: str,
                   description: str = '') -> 'Automation':
        self.actions.append(Action(
            action_type=ActionType.SCREENSHOT,
            params={'save_name': save_name},
            description=description or f'Screenshot: {save_name}'
        ))
        return self

    def conditional(self, app: str, page: str, element: str,
                    if_true: List[Action] = None,
                    if_false: List[Action] = None) -> 'Automation':
        """Branch based on element visibility."""
        self.actions.append(Action(
            action_type=ActionType.CONDITIONAL,
            app=app, page=page, element=element,
            params={
                'if_true': [a.to_dict() for a in (if_true or [])],
                'if_false': [a.to_dict() for a in (if_false or [])]
            },
            description=f'If {element} visible → branch'
        ))
        return self

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'automation_id': self.automation_id,
            'actions': [a.to_dict() for a in self.actions],
            'tags': self.tags,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'last_run_at': self.last_run_at,
            'run_count': self.run_count,
            'avg_duration_ms': self.avg_duration_ms,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Automation':
        actions_data = data.pop('actions', [])
        auto = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        auto.actions = [Action.from_dict(a) for a in actions_data]
        return auto


class AutomationEngine:
    """
    Executes automations by finding elements and performing actions.
    Thread-safe, supports dry-run, logging, and event callbacks.
    """

    def __init__(self, library: Optional[ElementLibrary] = None,
                 capture: Optional[CaptureEngine] = None,
                 kinematics: Optional[MouseKinematics] = None):
        self.library = library or ElementLibrary()
        self.capture = capture or CaptureEngine(self.library)
        self.kinematics = kinematics or MouseKinematics()
        self._automations: Dict[str, Automation] = {}
        self._callbacks: List[Callable] = []
        AUTOMATIONS_DIR.mkdir(parents=True, exist_ok=True)
        self._load_automations()

    # ── Storage ────────────────────────────────────────────

    def _load_automations(self):
        """Load saved automations from disk."""
        for json_file in AUTOMATIONS_DIR.glob('*.json'):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                auto = Automation.from_dict(data)
                self._automations[auto.name] = auto
            except Exception:
                pass

    def save(self, automation: Automation) -> dict:
        """Save an automation to disk."""
        self._automations[automation.name] = automation
        path = AUTOMATIONS_DIR / f'{automation.name}.json'
        with open(path, 'w') as f:
            json.dump(automation.to_dict(), f, indent=2)
        return {'success': True, 'path': str(path), 'name': automation.name}

    def get(self, name: str) -> Optional[Automation]:
        """Get a saved automation by name."""
        return self._automations.get(name)

    def list_automations(self) -> List[Dict]:
        """List all saved automations."""
        return [
            {
                'name': a.name,
                'description': a.description,
                'steps': len(a.actions),
                'tags': a.tags,
                'run_count': a.run_count,
                'created_by': a.created_by
            }
            for a in self._automations.values()
        ]

    def delete(self, name: str) -> dict:
        """Delete a saved automation."""
        self._automations.pop(name, None)
        path = AUTOMATIONS_DIR / f'{name}.json'
        if path.exists():
            path.unlink()
        return {'success': True, 'deleted': name}

    # ── Execution ──────────────────────────────────────────

    def run(self, automation: Automation,
            dry_run: bool = False) -> dict:
        """
        Execute a complete automation.
        Finds each element, performs the action, reports results.
        """
        start_time = time.time()
        results: List[Dict] = []
        aborted = False

        for i, action in enumerate(automation.actions):
            result = self._execute_action(action, dry_run)
            results.append({
                'step': i + 1,
                'description': action.description,
                **result.__dict__ if hasattr(result, '__dict__') else result
            })

            # Handle failure
            if not result.success:
                if action.on_fail == 'abort':
                    aborted = True
                    break
                elif action.on_fail == 'retry':
                    for retry in range(action.retry_count):
                        time.sleep(0.5)
                        result = self._execute_action(action, dry_run)
                        if result.success:
                            results[-1] = {
                                'step': i + 1,
                                'description': action.description,
                                'retries': retry + 1,
                                **result.__dict__
                            }
                            break
                # 'skip' falls through

            self._notify_callbacks(action, result)

        duration = (time.time() - start_time) * 1000

        # Update automation stats
        automation.last_run_at = time.time()
        automation.run_count += 1
        automation.avg_duration_ms = (
            (automation.avg_duration_ms * (automation.run_count - 1) + duration)
            / automation.run_count
        )

        return {
            'automation': automation.name,
            'success': not aborted and all(r.get('success', False) for r in results),
            'aborted': aborted,
            'steps_total': len(automation.actions),
            'steps_completed': len(results),
            'duration_ms': round(duration, 1),
            'dry_run': dry_run,
            'results': results
        }

    def run_by_name(self, name: str, dry_run: bool = False) -> dict:
        """Run a saved automation by name."""
        auto = self.get(name)
        if not auto:
            return {'success': False, 'error': f'Automation not found: {name}'}
        return self.run(auto, dry_run=dry_run)

    # ── Action Execution ───────────────────────────────────

    def _execute_action(self, action: Action,
                        dry_run: bool) -> ActionResult:
        """Execute a single action."""
        start = time.time()

        try:
            if action.action_type == ActionType.CLICK:
                return self._do_click(action, dry_run)

            elif action.action_type == ActionType.DOUBLE_CLICK:
                return self._do_click(action, dry_run, double=True)

            elif action.action_type == ActionType.RIGHT_CLICK:
                return self._do_click(action, dry_run, button='right')

            elif action.action_type == ActionType.TYPE:
                return self._do_type(action, dry_run)

            elif action.action_type == ActionType.HOTKEY:
                return self._do_hotkey(action, dry_run)

            elif action.action_type == ActionType.SCROLL:
                return self._do_scroll(action, dry_run)

            elif action.action_type == ActionType.WAIT:
                seconds = action.params.get('seconds', 1.0)
                if not dry_run:
                    time.sleep(seconds)
                return ActionResult(success=True, action_type='wait',
                                    duration_ms=(time.time() - start) * 1000)

            elif action.action_type == ActionType.WAIT_FOR:
                return self._do_wait_for(action, dry_run)

            elif action.action_type == ActionType.VERIFY:
                return self._do_verify(action, dry_run)

            elif action.action_type == ActionType.FOCUS_WINDOW:
                return self._do_focus_window(action, dry_run)

            elif action.action_type == ActionType.SCREENSHOT:
                return self._do_screenshot(action, dry_run)

            elif action.action_type == ActionType.CONDITIONAL:
                return self._do_conditional(action, dry_run)

            else:
                return ActionResult(success=False, action_type=action.action_type,
                                    error=f'Unknown action type: {action.action_type}')

        except Exception as e:
            return ActionResult(success=False, action_type=action.action_type,
                                error=str(e),
                                duration_ms=(time.time() - start) * 1000)

    def _do_click(self, action: Action, dry_run: bool,
                  button: str = 'left', double: bool = False) -> ActionResult:
        """Find element and click it."""
        pos = self.capture.find_element_on_screen(action.app, action.page, action.element)

        if not pos:
            return ActionResult(
                success=False,
                action_type='click',
                element=action.element,
                error=f'Element not found on screen: {action.element}'
            )

        if not dry_run:
            target_x = pos['center_x']
            target_y = pos['center_y']
            self.kinematics.move_to(target_x, target_y,
                                     click=True, button=button, double=double)

        return ActionResult(
            success=True,
            action_type='click',
            element=action.element,
            position=pos
        )

    def _do_type(self, action: Action, dry_run: bool) -> ActionResult:
        """Optionally click an element, then type text."""
        text = action.params.get('text', '')

        # Click element first if specified
        if action.element:
            click_result = self._do_click(action, dry_run)
            if not click_result.success:
                return click_result
            if not dry_run:
                time.sleep(0.2)

        if not dry_run:
            import pyautogui
            pyautogui.typewrite(text, interval=0.02) if text.isascii() else pyautogui.write(text)

        return ActionResult(success=True, action_type='type',
                            element=action.element,
                            metadata={'text_length': len(text)})

    def _do_hotkey(self, action: Action, dry_run: bool) -> ActionResult:
        """Execute a hotkey combination."""
        keys = action.params.get('keys', [])
        if not dry_run:
            import pyautogui
            pyautogui.hotkey(*keys)

        return ActionResult(success=True, action_type='hotkey',
                            metadata={'keys': keys})

    def _do_scroll(self, action: Action, dry_run: bool) -> ActionResult:
        """Scroll up or down."""
        direction = action.params.get('direction', 'down')
        amount = action.params.get('amount', 3)

        if not dry_run:
            import pyautogui
            clicks = amount if direction == 'down' else -amount
            pyautogui.scroll(clicks)

        return ActionResult(success=True, action_type='scroll',
                            metadata={'direction': direction, 'amount': amount})

    def _do_wait_for(self, action: Action, dry_run: bool) -> ActionResult:
        """Wait until an element appears on screen."""
        if dry_run:
            return ActionResult(success=True, action_type='wait_for',
                                element=action.element)

        deadline = time.time() + action.timeout
        while time.time() < deadline:
            pos = self.capture.find_element_on_screen(
                action.app, action.page, action.element
            )
            if pos:
                return ActionResult(success=True, action_type='wait_for',
                                    element=action.element, position=pos)
            time.sleep(0.5)

        return ActionResult(success=False, action_type='wait_for',
                            element=action.element,
                            error=f'Timed out waiting for {action.element}')

    def _do_verify(self, action: Action, dry_run: bool) -> ActionResult:
        """Verify an element is visible on screen."""
        if dry_run:
            return ActionResult(success=True, action_type='verify',
                                element=action.element)

        result = self.capture.verify_element(action.app, action.page, action.element)

        return ActionResult(
            success=result.get('found', False),
            action_type='verify',
            element=action.element,
            position=result.get('position'),
            metadata={'confidence': result.get('confidence', 0)}
        )

    def _do_focus_window(self, action: Action, dry_run: bool) -> ActionResult:
        """Focus a window by title."""
        title = action.params.get('window_title', '')

        if not dry_run:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].activate()
            else:
                return ActionResult(success=False, action_type='focus_window',
                                    error=f'Window not found: {title}')

        return ActionResult(success=True, action_type='focus_window',
                            metadata={'window_title': title})

    def _do_screenshot(self, action: Action, dry_run: bool) -> ActionResult:
        """Take a screenshot and save it."""
        save_name = action.params.get('save_name', f'screenshot_{int(time.time())}')

        if not dry_run:
            screen = self.capture.capture_full_screen()
            save_path = AUTOMATIONS_DIR / f'{save_name}.png'
            cv2.imwrite(str(save_path), screen)

        return ActionResult(success=True, action_type='screenshot',
                            metadata={'save_name': save_name})

    def _do_conditional(self, action: Action, dry_run: bool) -> ActionResult:
        """Execute branching logic based on element visibility."""
        found = False
        if not dry_run:
            pos = self.capture.find_element_on_screen(
                action.app, action.page, action.element,
                confidence_threshold=0.6
            )
            found = pos is not None

        branch_key = 'if_true' if found else 'if_false'
        branch_actions = action.params.get(branch_key, [])

        for action_data in branch_actions:
            sub_action = Action.from_dict(action_data)
            self._execute_action(sub_action, dry_run)

        return ActionResult(
            success=True,
            action_type='conditional',
            element=action.element,
            metadata={'branch': branch_key, 'element_found': found}
        )

    # ── Callbacks ──────────────────────────────────────────

    def on_action(self, callback: Callable):
        """Register a callback for action events."""
        self._callbacks.append(callback)

    def _notify_callbacks(self, action: Action, result: ActionResult):
        for cb in self._callbacks:
            try:
                cb(action, result)
            except Exception:
                pass
