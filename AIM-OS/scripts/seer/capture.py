"""
AIM-OS SEER — Capture System

Production element capture and learning mode.
Provides tools for capturing screen regions, labeling elements,
importing DOM data, and building the element library.

Workflows:
  1. Manual capture: Human selects a region → saves as named element
  2. AI-assisted: AI screenshots an area → labels what it sees
  3. DOM import: Chrome extension exports element data → auto-registers
  4. Batch learning: Walk through an app, capture every interactive element
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seer.element_library import ElementLibrary, Element


@dataclass
class CaptureRegion:
    """A screen region for capture."""
    x: int
    y: int
    w: int
    h: int
    monitor: int = 1


class CaptureEngine:
    """
    Element capture and learning system.
    Captures screen regions, labels them, and stores in the Element Library.
    """

    def __init__(self, library: Optional[ElementLibrary] = None):
        self.library = library or ElementLibrary()
        self._capture_queue: List[Dict] = []

    # ── Screen Capture ─────────────────────────────────────

    def capture_region(self, x: int, y: int, w: int, h: int,
                       monitor: int = 1) -> np.ndarray:
        """Capture a specific screen region as a numpy array."""
        import mss

        with mss.mss() as sct:
            region = {'left': x, 'top': y, 'width': w, 'height': h, 'mon': monitor}
            screenshot = sct.grab(region)
            frame = np.array(screenshot)
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def capture_full_screen(self, monitor: int = 1) -> np.ndarray:
        """Capture the full screen."""
        import mss

        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[monitor])
            frame = np.array(screenshot)
            return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    def capture_window(self, window_title: str) -> Optional[np.ndarray]:
        """Capture a specific window by title."""
        import pygetwindow as gw

        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return None

        win = windows[0]
        if win.isMinimized:
            win.restore()

        return self.capture_region(win.left, win.top, win.width, win.height)

    # ── Element Capture ────────────────────────────────────

    def capture_element(self, app: str, page: str, name: str,
                        x: int, y: int, w: int, h: int,
                        element_type: str = 'button',
                        selector: str = '',
                        description: str = '',
                        tags: Optional[List[str]] = None,
                        monitor: int = 1,
                        click_offset_x: int = 0,
                        click_offset_y: int = 0) -> dict:
        """
        Capture a UI element from the screen and store it.
        This is the primary learning operation.

        Args:
            app: Application name (e.g., 'chatgpt')
            page: Page name (e.g., 'main')
            name: Element name (e.g., 'send_button')
            x, y: Screen coordinates of the element
            w, h: Element dimensions
            element_type: Type of element
            selector: CSS selector from DOM
            description: Human-readable description
            tags: Search tags
            monitor: Monitor number
            click_offset_x/y: Click target offset from center
        """
        # Capture the image
        image = self.capture_region(x, y, w, h, monitor)

        # Create the element
        element = Element(
            name=name,
            app=app,
            page=page,
            element_type=element_type,
            selector=selector,
            description=description,
            x=x, y=y, w=w, h=h,
            tags=tags or [],
            click_offset_x=click_offset_x,
            click_offset_y=click_offset_y
        )

        # Store it
        result = self.library.store_element(element, image)

        return {
            **result,
            'image_shape': list(image.shape),
            'element': element.to_dict()
        }

    def capture_element_from_image(self, app: str, page: str, name: str,
                                    image: np.ndarray,
                                    x: int = 0, y: int = 0,
                                    element_type: str = 'button',
                                    **kwargs) -> dict:
        """Store an element from an already-captured image."""
        h, w = image.shape[:2]

        element = Element(
            name=name,
            app=app,
            page=page,
            element_type=element_type,
            x=x, y=y, w=w, h=h,
            **{k: v for k, v in kwargs.items() if k in Element.__dataclass_fields__}
        )

        return self.library.store_element(element, image)

    # ── DOM Import ─────────────────────────────────────────

    def import_from_dom(self, app: str, page: str,
                        dom_elements: List[Dict]) -> dict:
        """
        Import elements from Chrome extension DOM spatial map.
        The extension sends element data with bounding rects.

        Expected format per element:
        {
            "tag": "button",
            "id": "submit-btn",
            "classes": ["btn", "primary"],
            "text": "Submit",
            "rect": {"x": 100, "y": 200, "width": 80, "height": 30},
            "selector": "#submit-btn",
            "visible": true,
            "interactable": true
        }
        """
        imported = 0
        skipped = 0
        errors = []

        for dom_el in dom_elements:
            if not dom_el.get('visible', True):
                skipped += 1
                continue
            if not dom_el.get('interactable', True):
                skipped += 1
                continue

            rect = dom_el.get('rect', {})
            if not rect:
                skipped += 1
                continue

            # Generate a name from id, text, or tag
            name = (dom_el.get('id') or
                    dom_el.get('text', '')[:30].strip().lower().replace(' ', '_') or
                    f"{dom_el.get('tag', 'element')}_{imported}")

            # Clean name (alphanumeric + underscore only)
            name = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
            name = name.strip('_')[:50]

            if not name:
                skipped += 1
                continue

            # Determine element type
            tag = dom_el.get('tag', '').lower()
            type_map = {
                'button': 'button', 'a': 'link', 'input': 'input',
                'select': 'dropdown', 'textarea': 'input',
                'img': 'icon', 'nav': 'menu'
            }
            element_type = type_map.get(tag, 'button')

            try:
                x = int(rect.get('x', 0))
                y = int(rect.get('y', 0))
                w = int(rect.get('width', 0))
                h = int(rect.get('height', 0))

                if w < 5 or h < 5:
                    skipped += 1
                    continue

                # Capture the screen region for this element
                image = self.capture_region(x, y, w, h)

                element = Element(
                    name=name,
                    app=app,
                    page=page,
                    element_type=element_type,
                    selector=dom_el.get('selector', ''),
                    description=dom_el.get('text', ''),
                    x=x, y=y, w=w, h=h,
                    tags=dom_el.get('classes', []),
                    metadata={
                        'tag': tag,
                        'dom_id': dom_el.get('id', ''),
                        'classes': dom_el.get('classes', [])
                    }
                )

                self.library.store_element(element, image)
                imported += 1

            except Exception as e:
                errors.append({'element': name, 'error': str(e)})

        return {
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'app': app,
            'page': page
        }

    # ── Batch Learning ─────────────────────────────────────

    def learn_page(self, app: str, page: str,
                   interactive_only: bool = True) -> dict:
        """
        Auto-capture all visible interactive elements on the current page.
        Uses the Chrome extension's DOM spatial map for web pages,
        or screenshot-based detection for native apps.
        """
        # This just registers the page — actual capture happens
        # via DOM import or manual capture
        self.library.register_page(app, page)

        return {
            'success': True,
            'message': f'Page {app}/{page} registered. Use capture_element() or import_from_dom() to add elements.',
            'app': app,
            'page': page
        }

    # ── Verification ───────────────────────────────────────

    def verify_element(self, app: str, page: str, name: str,
                       confidence_threshold: float = 0.7) -> dict:
        """
        Verify that a stored element can still be found on screen.
        Returns confidence and current position.
        """
        element = self.library.get_element(app, page, name)
        if not element:
            return {'found': False, 'error': f'Element not found: {app}/{page}/{name}'}

        template = self.library.get_element_image(app, page, name)
        if template is None:
            return {'found': False, 'error': f'No image for: {app}/{page}/{name}'}

        # Capture current screen
        screen = self.capture_full_screen()

        # Template match
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        found = max_val >= confidence_threshold
        h, w = template.shape[:2]

        if found:
            element.last_found_at = time.time()
            element.find_count += 1
            element.x = max_loc[0]
            element.y = max_loc[1]
            self.library.store_element(element)

        return {
            'found': found,
            'confidence': round(float(max_val), 4),
            'threshold': confidence_threshold,
            'position': {
                'x': max_loc[0],
                'y': max_loc[1],
                'center_x': max_loc[0] + w // 2,
                'center_y': max_loc[1] + h // 2
            },
            'element': element.name,
            'app': app,
            'page': page
        }

    def verify_all_elements(self, app: str, page: str) -> dict:
        """Verify all elements for a page. Returns calibration report."""
        elements = self.library.list_elements(app, page)
        results = []

        for el_data in elements:
            name = el_data.get('name', '')
            result = self.verify_element(app, page, name)
            results.append(result)

        found = sum(1 for r in results if r.get('found'))
        total = len(results)

        return {
            'app': app,
            'page': page,
            'total': total,
            'found': found,
            'missing': total - found,
            'calibration_score': round(found / total, 2) if total > 0 else 0,
            'details': results
        }

    # ── Find and Click ─────────────────────────────────────

    def find_element_on_screen(self, app: str, page: str, name: str,
                                confidence_threshold: float = 0.7) -> Optional[Dict]:
        """
        Find a stored element on the current screen.
        Returns the center coordinates for clicking.
        """
        result = self.verify_element(app, page, name, confidence_threshold)
        if result.get('found'):
            return result['position']
        return None

    def find_any_element(self, name: str,
                          confidence_threshold: float = 0.7) -> Optional[Dict]:
        """
        Search for an element by name across ALL apps/pages.
        Tries each stored version until one matches.
        """
        elements = self.library.find_by_name(name)

        for element in elements:
            result = self.verify_element(
                element.app, element.page, element.name,
                confidence_threshold
            )
            if result.get('found'):
                return {
                    **result['position'],
                    'app': element.app,
                    'page': element.page,
                    'confidence': result['confidence']
                }

        return None
