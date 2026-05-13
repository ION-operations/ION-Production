"""
AIM-OS SEER — AI Element Discovery

AI-assisted element detection using Gemini Vision API.
Agents send a screenshot → Gemini identifies all UI elements with
bounding boxes → auto-crop and store in the Element Library.

Also supports Nano Banana (Gemini Image Generation) for visual
annotation and review.

Dependencies:
    pip install google-generativeai Pillow

Requires:
    GEMINI_API_KEY environment variable
"""

import os
import sys
import json
import time
import base64
import io
from pathlib import Path
from typing import Optional, Dict, List, Any

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seer.element_library import ElementLibrary, Element
from seer.capture import CaptureEngine


# ── Gemini API Wrapper ─────────────────────────────────────

class GeminiVision:
    """
    Gemini API integration for visual element discovery
    and image generation (Nano Banana).
    """

    def __init__(self, api_key: Optional[str] = None,
                 model: str = 'gemini-2.0-flash'):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY', '')
        self.model_name = model
        self._client = None
        self._image_model = None

    @property
    def client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
            except ImportError:
                raise ImportError(
                    'google-generativeai is required. Install with: '
                    'pip install google-generativeai'
                )
        return self._client

    @property
    def image_model(self):
        """Nano Banana — Gemini image generation model."""
        if self._image_model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._image_model = genai.GenerativeModel('gemini-2.0-flash-preview-image-generation')
            except ImportError:
                raise ImportError(
                    'google-generativeai is required. Install with: '
                    'pip install google-generativeai'
                )
        return self._image_model

    def is_configured(self) -> bool:
        """Check if the API key is set."""
        return bool(self.api_key)

    def _image_to_pil(self, image: np.ndarray):
        """Convert OpenCV numpy array to PIL Image."""
        from PIL import Image
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert OpenCV image to base64 string."""
        _, buffer = cv2.imencode('.png', image)
        return base64.b64encode(buffer).decode('utf-8')

    # ── Element Discovery ──────────────────────────────────

    def discover_elements(self, screenshot: np.ndarray,
                           context: str = '') -> List[Dict]:
        """
        Send a screenshot to Gemini Vision and get back a list
        of all interactive UI elements with bounding boxes.

        Returns:
            List of dicts: [{name, type, x, y, width, height, description}]
        """
        pil_image = self._image_to_pil(screenshot)

        prompt = f"""Analyze this screenshot of a desktop application.
Identify ALL interactive UI elements (buttons, input fields, links, tabs, menus, dropdowns, checkboxes, etc).

{f'Context: {context}' if context else ''}

Return a JSON array where each element has:
- "name": short snake_case identifier (e.g., "send_button", "search_input")
- "type": one of [button, input, link, tab, menu, dropdown, checkbox, toggle, icon, text_field]
- "x": pixel X coordinate of the top-left corner
- "y": pixel Y coordinate of the top-left corner
- "width": element width in pixels
- "height": element height in pixels
- "description": brief human-readable description of what the element does
- "text": the visible text on the element (if any)

IMPORTANT:
- Be precise with coordinates — they will be used for mouse automation
- Include EVERY clickable or interactive element you can see
- Return ONLY valid JSON, no markdown formatting or explanation
- Estimate coordinates as accurately as possible from the image"""

        response = self.client.generate_content([prompt, pil_image])

        # Parse the response
        text = response.text.strip()

        # Strip markdown code blocks if present
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1])

        try:
            elements = json.loads(text)
            if isinstance(elements, dict) and 'elements' in elements:
                elements = elements['elements']
            return elements
        except json.JSONDecodeError:
            return [{'error': 'Failed to parse Gemini response', 'raw': text[:500]}]

    def annotate_screenshot(self, screenshot: np.ndarray,
                             instruction: str = '') -> Optional[np.ndarray]:
        """
        Send screenshot to Nano Banana with annotation instructions.
        Returns the annotated image for human review.
        """
        pil_image = self._image_to_pil(screenshot)

        prompt = instruction or """Draw colored rectangles around every interactive UI element in this screenshot:
- GREEN rectangles around buttons
- BLUE rectangles around input fields and text areas
- YELLOW rectangles around links and tabs
- RED rectangles around menus and dropdowns
- Number each rectangle with a white label

Use 2-pixel thick borders. Do NOT modify the underlying screenshot.
Only add the rectangle overlays and numbers."""

        try:
            response = self.image_model.generate_content(
                [prompt, pil_image],
                generation_config={'response_modalities': ['IMAGE', 'TEXT']}
            )

            # Extract image from response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image'):
                    img_bytes = part.inline_data.data
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        except Exception as e:
            print(f'[SEER Discovery] Annotation failed: {e}')

        return None

    def generate_image(self, prompt: str,
                        reference_image: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        Generate an image using Nano Banana.
        Optionally accepts a reference image for editing/overlay.
        """
        contents = [prompt]
        if reference_image is not None:
            contents.append(self._image_to_pil(reference_image))

        try:
            response = self.image_model.generate_content(
                contents,
                generation_config={'response_modalities': ['IMAGE', 'TEXT']}
            )

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image'):
                    img_bytes = part.inline_data.data
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        except Exception as e:
            print(f'[SEER] Image generation failed: {e}')

        return None


# ── Discovery Engine ───────────────────────────────────────

class DiscoveryEngine:
    """
    AI-assisted element discovery and auto-learning.
    Combines Gemini Vision with the Element Library for
    self-service agent learning.
    """

    def __init__(self, library: Optional[ElementLibrary] = None,
                 capture: Optional[CaptureEngine] = None,
                 vision: Optional[GeminiVision] = None):
        self.library = library or ElementLibrary()
        self.capture = capture or CaptureEngine(self.library)
        self.vision = vision or GeminiVision()

    def is_available(self) -> dict:
        """Check if Gemini API is configured and ready."""
        return {
            'configured': self.vision.is_configured(),
            'api_key_set': bool(self.vision.api_key),
            'model': self.vision.model_name
        }

    # ── Full Discovery Pipeline ────────────────────────────

    def discover_and_learn(self, app: str, page: str,
                            monitor: int = 1,
                            context: str = '',
                            auto_save: bool = True,
                            min_size: int = 10) -> dict:
        """
        Full discovery pipeline:
        1. Screenshot the screen
        2. Send to Gemini Vision → get element list with bounding boxes
        3. Auto-crop each element from the ORIGINAL screenshot
        4. Store in Element Library

        Args:
            app: Application name
            page: Page name
            monitor: Monitor number to screenshot
            context: Optional context for Gemini (e.g., "This is a ChatGPT window")
            auto_save: If True, automatically save all discovered elements
            min_size: Minimum element size in pixels (filters noise)
        """
        if not self.vision.is_configured():
            return {'error': 'Gemini API key not configured. Set GEMINI_API_KEY.'}

        # 1. Capture screenshot
        screenshot = self.capture.capture_full_screen(monitor)
        screen_h, screen_w = screenshot.shape[:2]

        # 2. Discover elements via Gemini Vision
        discoveries = self.vision.discover_elements(screenshot, context)

        if not discoveries or (len(discoveries) == 1 and 'error' in discoveries[0]):
            return {
                'success': False,
                'error': 'Discovery failed',
                'raw': discoveries
            }

        # 3. Register app/page
        self.library.register_app(app)
        self.library.register_page(app, page)

        # 4. Process and store each discovered element
        saved = 0
        skipped = 0
        errors = []

        for disc in discoveries:
            try:
                name = disc.get('name', '').strip()
                if not name:
                    skipped += 1
                    continue

                x = int(disc.get('x', 0))
                y = int(disc.get('y', 0))
                w = int(disc.get('width', 0))
                h = int(disc.get('height', 0))

                # Validate bounds
                if w < min_size or h < min_size:
                    skipped += 1
                    continue
                if x < 0 or y < 0 or x + w > screen_w or y + h > screen_h:
                    # Clamp to screen bounds
                    x = max(0, min(x, screen_w - 1))
                    y = max(0, min(y, screen_h - 1))
                    w = min(w, screen_w - x)
                    h = min(h, screen_h - y)

                # Crop from ORIGINAL screenshot (not Gemini's output)
                element_image = screenshot[y:y+h, x:x+w].copy()

                if auto_save:
                    element = Element(
                        name=name,
                        app=app,
                        page=page,
                        element_type=disc.get('type', 'button'),
                        description=disc.get('description', ''),
                        x=x, y=y, w=w, h=h,
                        tags=[disc.get('type', 'button')],
                        metadata={
                            'discovered_by': 'gemini_vision',
                            'text': disc.get('text', ''),
                            'discovery_time': time.time()
                        }
                    )
                    self.library.store_element(element, element_image)

                saved += 1

            except Exception as e:
                errors.append({'element': disc.get('name', 'unknown'), 'error': str(e)})

        return {
            'success': True,
            'app': app,
            'page': page,
            'discovered': len(discoveries),
            'saved': saved,
            'skipped': skipped,
            'errors': errors,
            'elements': [d.get('name', '') for d in discoveries if d.get('name')]
        }

    def discover_window(self, window_title: str, app: str, page: str,
                         context: str = '') -> dict:
        """Discover elements within a specific window."""
        screenshot = self.capture.capture_window(window_title)
        if screenshot is None:
            return {'error': f'Window not found: {window_title}'}

        # Same pipeline but with window-specific screenshot
        if not self.vision.is_configured():
            return {'error': 'Gemini API key not configured.'}

        discoveries = self.vision.discover_elements(screenshot, context)
        # Get window position for offset mapping
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(window_title)
        offset_x = windows[0].left if windows else 0
        offset_y = windows[0].top if windows else 0

        self.library.register_app(app)
        self.library.register_page(app, page)

        saved = 0
        for disc in discoveries:
            try:
                name = disc.get('name', '')
                if not name:
                    continue

                x = int(disc.get('x', 0))
                y = int(disc.get('y', 0))
                w = int(disc.get('width', 0))
                h = int(disc.get('height', 0))

                if w < 10 or h < 10:
                    continue

                element_image = screenshot[y:y+h, x:x+w].copy()

                element = Element(
                    name=name, app=app, page=page,
                    element_type=disc.get('type', 'button'),
                    description=disc.get('description', ''),
                    x=x + offset_x, y=y + offset_y, w=w, h=h,
                    metadata={
                        'discovered_by': 'gemini_vision',
                        'window': window_title,
                        'window_offset': [offset_x, offset_y]
                    }
                )
                self.library.store_element(element, element_image)
                saved += 1

            except Exception:
                pass

        return {
            'success': True, 'app': app, 'page': page,
            'discovered': len(discoveries), 'saved': saved,
            'window': window_title
        }

    # ── Visual Annotation (Human Review) ───────────────────

    def annotate_for_review(self, app: str = '', page: str = '',
                              monitor: int = 1,
                              save_path: Optional[str] = None) -> dict:
        """
        Screenshot → Nano Banana annotates with colored boxes →
        Save annotated image for human review.
        """
        if not self.vision.is_configured():
            return {'error': 'Gemini API key not configured.'}

        screenshot = self.capture.capture_full_screen(monitor)
        annotated = self.vision.annotate_screenshot(screenshot)

        if annotated is None:
            return {'success': False, 'error': 'Annotation failed'}

        # Save annotated image
        if save_path is None:
            save_dir = self.library.root.parent / 'discovery'
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = str(save_dir / f'annotated_{app}_{page}_{int(time.time())}.png')

        cv2.imwrite(save_path, annotated)

        return {
            'success': True,
            'annotated_image': save_path,
            'message': 'Review the annotated image, then call discover_and_learn() to save elements.'
        }

    # ── Gemini General API ─────────────────────────────────

    def ask_gemini(self, prompt: str,
                    image: Optional[np.ndarray] = None) -> str:
        """
        General-purpose Gemini API call.
        Can include an image for vision tasks.
        """
        if not self.vision.is_configured():
            return 'Error: Gemini API key not configured.'

        contents = [prompt]
        if image is not None:
            contents.append(self.vision._image_to_pil(image))

        response = self.vision.client.generate_content(contents)
        return response.text

    def generate_nano_banana(self, prompt: str,
                               reference_image: Optional[np.ndarray] = None,
                               save_path: Optional[str] = None) -> dict:
        """
        Generate an image using Nano Banana (Gemini Image Generation).
        Optionally pass a reference image for editing/overlay.
        """
        if not self.vision.is_configured():
            return {'error': 'Gemini API key not configured.'}

        result = self.vision.generate_image(prompt, reference_image)
        if result is None:
            return {'success': False, 'error': 'Image generation failed'}

        if save_path is None:
            save_dir = self.library.root.parent / 'generated'
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = str(save_dir / f'nanobanan_{int(time.time())}.png')

        cv2.imwrite(save_path, result)

        return {
            'success': True,
            'image_path': save_path,
            'shape': list(result.shape)
        }
