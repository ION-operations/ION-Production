"""
AIM-OS SEER — Generative Path Executor

Turns AI-drawn images into physical mouse execution.
The image generator (Nano Banana / Gemini) draws a path overlay on a
screenshot, encoding:
  - TRAJECTORY: Red-to-Blue gradient line = mouse path with velocity
  - ACTIONS: Color-coded circles at path terminus
  - DRAG: Cyan lines for click-drag vectors
  - OBSTACLES: Red bounding boxes for exclusion zones

OpenCV extracts the geometry, and the kinematics engine executes it.

Visual Legend (The Color Matrix):
  Red (#FF0000, HSV: 0)     → Fast movement start
  Blue (#0000FF, HSV: 120)  → Slow/precision end
  Green circle (HSV: 60)    → Left-click
  Yellow circle (HSV: 30)   → Right-click
  Magenta circle (HSV: 150) → Double-click
  Cyan line (HSV: 90)       → Drag operation
  Red box (border only)     → Exclusion zone

Credit: Architecture co-designed by Braden (CEO) and Gemini.
"""

import cv2
import numpy as np
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

from .kinematics import MouseKinematics


# ── Color Definitions (HSV ranges for masking) ──────────────

# OpenCV HSV: H=0-179, S=0-255, V=0-255
COLORS = {
    'path_red':    {'lower': (0,   150, 150), 'upper': (10,  255, 255)},
    'path_blue':   {'lower': (100, 150, 150), 'upper': (130, 255, 255)},
    'click_green': {'lower': (50,  150, 150), 'upper': (70,  255, 255)},
    'rclick_yellow': {'lower': (20, 150, 150), 'upper': (40,  255, 255)},
    'dclick_magenta': {'lower': (140, 150, 150), 'upper': (160, 255, 255)},
    'drag_cyan':   {'lower': (80,  150, 150), 'upper': (100, 255, 255)},
    'exclude_red': {'lower': (0,   100, 100), 'upper': (10,  255, 255)},
}

# Action node color → action type mapping
ACTION_MAP = {
    'click_green': 'left_click',
    'rclick_yellow': 'right_click',
    'dclick_magenta': 'double_click',
}


@dataclass
class PathNode:
    """A single point along the kinematic path."""
    x: int
    y: int
    hue: int
    velocity_modifier: float  # 0.0 (fast/red) → 1.0 (slow/blue)


@dataclass
class ActionNode:
    """An action to execute at a specific location."""
    x: int
    y: int
    action: str  # 'left_click', 'right_click', 'double_click', 'drag'
    drag_to: Optional[Tuple[int, int]] = None


@dataclass
class GenerativePlan:
    """A complete kinematic plan extracted from an AI-generated image."""
    path: List[PathNode] = field(default_factory=list)
    actions: List[ActionNode] = field(default_factory=list)
    exclusion_zones: List[Dict] = field(default_factory=list)
    source_image: str = ''
    offset_x: int = 0
    offset_y: int = 0


class GenerativePathExecutor:
    """
    Ingests AI-drawn kinematic images and executes them physically.
    The image generator draws the plan, OpenCV reads it, pyautogui executes it.
    """

    def __init__(self, kinematics: Optional[MouseKinematics] = None):
        self.kinematics = kinematics or MouseKinematics()
        self._base_sleep = 0.001
        self._max_velocity_delay = 0.015

    # ── Plan Extraction ────────────────────────────────────────

    def extract_plan(self, image_path: str,
                     offset_x: int = 0,
                     offset_y: int = 0) -> GenerativePlan:
        """
        Extract a complete kinematic plan from an AI-generated image.

        Args:
            image_path: Path to the generated heatmap image
            offset_x: Screen X offset (for micro-crop → full screen mapping)
            offset_y: Screen Y offset

        Returns:
            GenerativePlan with path, actions, and exclusion zones
        """
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f'Could not load image: {image_path}')

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        plan = GenerativePlan(
            source_image=image_path,
            offset_x=offset_x,
            offset_y=offset_y
        )

        # Extract the main path
        plan.path = self._extract_path(img, hsv)

        # Extract action nodes
        plan.actions = self._extract_actions(hsv, offset_x, offset_y)

        # Extract exclusion zones
        plan.exclusion_zones = self._extract_exclusions(hsv, offset_x, offset_y)

        return plan

    def extract_plan_from_array(self, frame: np.ndarray,
                                 offset_x: int = 0,
                                 offset_y: int = 0) -> GenerativePlan:
        """Extract plan from a numpy array (e.g., from screenshot + AI overlay)."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        plan = GenerativePlan(offset_x=offset_x, offset_y=offset_y)
        plan.path = self._extract_path(frame, hsv)
        plan.actions = self._extract_actions(hsv, offset_x, offset_y)
        plan.exclusion_zones = self._extract_exclusions(hsv, offset_x, offset_y)
        return plan

    # ── Path Extraction ────────────────────────────────────────

    def _extract_path(self, img: np.ndarray,
                       hsv: np.ndarray) -> List[PathNode]:
        """
        Extract the red-to-blue gradient path.
        Uses grayscale thresholding to isolate the drawn line,
        then reads HSV hue at each point for velocity encoding.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

        # Find contours — CHAIN_APPROX_NONE keeps ALL boundary points
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if not contours:
            return []

        # The longest contour is our primary path
        main_contour = max(contours, key=lambda c: len(c))

        path = []
        for point in main_contour:
            px, py = point[0]
            # Read the hue at this pixel for velocity encoding
            hue = int(hsv[py, px, 0])

            # Velocity: Red(0) = fast (0.0), Blue(120) = slow (1.0)
            velocity = min(hue / 120.0, 1.0) if hue < 150 else 0.0

            path.append(PathNode(x=px, y=py, hue=hue, velocity_modifier=velocity))

        return path

    def _extract_actions(self, hsv: np.ndarray,
                          offset_x: int,
                          offset_y: int) -> List[ActionNode]:
        """Extract action nodes (colored circles) from the image."""
        actions = []

        for color_name, action_type in ACTION_MAP.items():
            color_range = COLORS[color_name]
            mask = cv2.inRange(hsv,
                               np.array(color_range['lower']),
                               np.array(color_range['upper']))

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 20:  # Skip noise
                    continue

                # Find center of the action node
                M = cv2.moments(cnt)
                if M['m00'] == 0:
                    continue
                cx = int(M['m10'] / M['m00']) + offset_x
                cy = int(M['m01'] / M['m00']) + offset_y

                actions.append(ActionNode(x=cx, y=cy, action=action_type))

        # Extract drag vectors (cyan)
        drag_actions = self._extract_drags(hsv, offset_x, offset_y)
        actions.extend(drag_actions)

        return actions

    def _extract_drags(self, hsv: np.ndarray,
                        offset_x: int,
                        offset_y: int) -> List[ActionNode]:
        """Extract drag vectors from cyan lines."""
        color_range = COLORS['drag_cyan']
        mask = cv2.inRange(hsv,
                           np.array(color_range['lower']),
                           np.array(color_range['upper']))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        drags = []

        for cnt in contours:
            if len(cnt) < 2:
                continue

            # Start = first point, End = last point of the contour
            start = cnt[0][0]
            end = cnt[-1][0]

            drags.append(ActionNode(
                x=int(start[0]) + offset_x,
                y=int(start[1]) + offset_y,
                action='drag',
                drag_to=(int(end[0]) + offset_x, int(end[1]) + offset_y)
            ))

        return drags

    def _extract_exclusions(self, hsv: np.ndarray,
                             offset_x: int,
                             offset_y: int) -> List[Dict]:
        """Extract red exclusion zone bounding boxes."""
        color_range = COLORS['exclude_red']
        mask = cv2.inRange(hsv,
                           np.array(color_range['lower']),
                           np.array(color_range['upper']))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        zones = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Exclusion zones should be rectangular and substantial (not path pixels)
            if area < 500:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            # Quick rectangularity check (area vs bounding rect area)
            rect_area = w * h
            if area / rect_area < 0.3:  # Must be at least 30% filled
                continue

            zones.append({
                'x': x + offset_x,
                'y': y + offset_y,
                'w': w, 'h': h,
                'area': int(area)
            })

        return zones

    # ── Execution ──────────────────────────────────────────────

    def execute(self, plan: GenerativePlan,
                step_size: int = 3,
                dry_run: bool = False) -> dict:
        """
        Execute a generative kinematic plan.

        Args:
            plan: Extracted GenerativePlan
            step_size: Step every N path nodes (smoothness vs speed)
            dry_run: If True, log actions without executing

        Returns:
            Execution report with timing and actions taken
        """
        report = {
            'path_nodes': len(plan.path),
            'actions': [],
            'exclusion_zones': len(plan.exclusion_zones),
            'dry_run': dry_run,
            'start_time': time.time()
        }

        if not plan.path:
            report['error'] = 'No path detected in plan'
            return report

        # Execute the path with velocity-encoded movement
        for i in range(0, len(plan.path), step_size):
            node = plan.path[i]

            # Map from image coordinates to screen coordinates
            screen_x = node.x + plan.offset_x
            screen_y = node.y + plan.offset_y

            # Check exclusion zones
            if self._in_exclusion_zone(screen_x, screen_y, plan.exclusion_zones):
                continue

            # Calculate dynamic sleep from velocity heatmap
            dynamic_sleep = self._base_sleep + (node.velocity_modifier * self._max_velocity_delay)

            if not dry_run:
                import pyautogui
                pyautogui.moveTo(screen_x, screen_y, _pause=False)
                time.sleep(dynamic_sleep)

        # Execute action nodes
        for action in plan.actions:
            action_report = {'type': action.action, 'x': action.x, 'y': action.y}

            if not dry_run:
                if action.action == 'left_click':
                    self.kinematics.move_to(action.x, action.y, click=True)
                elif action.action == 'right_click':
                    self.kinematics.move_to(action.x, action.y, click=True, button='right')
                elif action.action == 'double_click':
                    self.kinematics.move_to(action.x, action.y, click=True, double=True)
                elif action.action == 'drag' and action.drag_to:
                    self.kinematics.drag_to(action.x, action.y,
                                            action.drag_to[0], action.drag_to[1])
                    action_report['drag_to'] = action.drag_to

            report['actions'].append(action_report)

        report['end_time'] = time.time()
        report['duration_ms'] = round((report['end_time'] - report['start_time']) * 1000, 1)

        return report

    def execute_from_image(self, image_path: str,
                            offset_x: int = 0,
                            offset_y: int = 0,
                            dry_run: bool = False) -> dict:
        """
        One-shot: extract plan from image and execute immediately.
        The simplest API — give it an AI-drawn image, it moves the mouse.
        """
        plan = self.extract_plan(image_path, offset_x, offset_y)
        return self.execute(plan, dry_run=dry_run)

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _in_exclusion_zone(x: int, y: int, zones: List[Dict]) -> bool:
        """Check if a point falls within any exclusion zone."""
        for zone in zones:
            if (zone['x'] <= x <= zone['x'] + zone['w'] and
                zone['y'] <= y <= zone['y'] + zone['h']):
                return True
        return False

    @staticmethod
    def get_prompt_template(current_pos: str = 'center-left',
                            target: str = 'Deploy button') -> str:
        """
        Generate the Nano Banana prompt for kinematic path generation.

        Returns the standardized prompt that tells the image generator
        exactly how to draw the velocity-encoded path overlay.
        """
        return f"""You are the visual kinematic engine for an autonomous OS.
I am providing a 300x300 pixel crop of a user interface.

Current State: The mouse cursor is located at {current_pos}.
Target: {target}

Task: Draw an overlay on this image following these strict rules:
1. Draw a single, smooth, curved 3-pixel-wide line connecting the current mouse position to the center of the Target.
2. The line must have a color gradient starting with pure Red (#FF0000) at the mouse position and fading into pure Blue (#0000FF) as it reaches the Target.
3. Draw a solid, 5-pixel-wide pure Green circle (#00FF00) exactly at the end of the line on the Target.
4. If there are UI elements between the cursor and target that should not be hovered over, draw a 2-pixel Red rectangle border around them as exclusion zones.
5. Do not add any text, shadows, or anti-aliasing to your drawings. Use raw, solid colors only."""
