"""
AIM-OS SEER — Biomechanical Mouse Kinematics Engine

Generates human-like mouse trajectories using cubic Bezier curves
with variable velocity, micro-corrections, and natural overshoots.
This makes SEER's physical manipulation indistinguishable from a
human operator, bypassing bot-detection and enabling realistic
drag-and-drop in complex web applications.
"""

import math
import random
import time
from typing import Tuple, List, Optional

import pyautogui


# Disable pyautogui's built-in pause (we handle timing ourselves)
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True  # Move mouse to corner to abort


class MouseKinematics:
    """
    Human-like mouse movement using cubic Bezier curves with
    biomechanical velocity profiles.
    """

    def __init__(self,
                 base_speed: float = 1.0,
                 overshoot_chance: float = 0.15,
                 jitter_amplitude: float = 2.0):
        """
        Args:
            base_speed: Multiplier for movement speed (1.0 = natural, 0.5 = slow, 2.0 = fast)
            overshoot_chance: Probability of overshooting the target (0.0 - 1.0)
            jitter_amplitude: Max pixel jitter for micro-corrections
        """
        self.base_speed = base_speed
        self.overshoot_chance = overshoot_chance
        self.jitter_amplitude = jitter_amplitude

    def move_to(self, x: int, y: int, click: bool = False,
                button: str = 'left', double: bool = False) -> dict:
        """
        Move mouse to (x, y) with human-like Bezier trajectory.

        Returns dict with movement details for logging/debugging.
        """
        start_x, start_y = pyautogui.position()
        distance = math.sqrt((x - start_x) ** 2 + (y - start_y) ** 2)

        if distance < 3:
            # Already at target — just click if needed
            if click:
                self._do_click(button, double)
            return {
                'start': (start_x, start_y),
                'end': (x, y),
                'distance': distance,
                'skipped': True,
                'clicked': click
            }

        # Generate Bezier control points
        cp1, cp2 = self._generate_control_points(start_x, start_y, x, y, distance)

        # Calculate movement duration based on Fitts' Law approximation
        duration = self._calculate_duration(distance)

        # Generate path points along the Bezier curve
        steps = max(int(duration * 120), 10)  # ~120 points per second
        path = self._bezier_curve(start_x, start_y, cp1[0], cp1[1],
                                   cp2[0], cp2[1], x, y, steps)

        # Execute the movement with velocity easing
        t_start = time.perf_counter()
        for i, (px, py) in enumerate(path):
            # Apply subtle jitter for realism
            jx = px + random.gauss(0, self.jitter_amplitude * 0.3)
            jy = py + random.gauss(0, self.jitter_amplitude * 0.3)

            pyautogui.moveTo(int(jx), int(jy), _pause=False)

            # Variable timing with easing (slower at start/end, faster in middle)
            t = i / len(path)
            ease = self._ease_in_out(t)
            sleep_time = (duration / steps) * (1.5 - ease)
            time.sleep(max(sleep_time / self.base_speed, 0.001))

        # Overshoot correction
        if random.random() < self.overshoot_chance and distance > 50:
            self._overshoot_correction(x, y, distance)

        # Final precise positioning
        pyautogui.moveTo(x, y, _pause=False)

        result = {
            'start': (start_x, start_y),
            'end': (x, y),
            'distance': round(distance, 1),
            'duration_ms': round((time.perf_counter() - t_start) * 1000, 1),
            'steps': steps,
            'control_points': [cp1, cp2],
            'clicked': click
        }

        # Click if requested
        if click:
            time.sleep(random.uniform(0.03, 0.08))  # Natural pre-click pause
            self._do_click(button, double)

        return result

    def drag_to(self, from_x: int, from_y: int, to_x: int, to_y: int,
                button: str = 'left') -> dict:
        """
        Perform a human-like drag from one point to another.
        """
        # Move to start position
        move_result = self.move_to(from_x, from_y)

        # Press, drag with Bezier, release
        pyautogui.mouseDown(button=button, _pause=False)
        time.sleep(random.uniform(0.05, 0.12))

        drag_result = self.move_to(to_x, to_y)

        time.sleep(random.uniform(0.03, 0.08))
        pyautogui.mouseUp(button=button, _pause=False)

        return {
            'action': 'drag',
            'from': (from_x, from_y),
            'to': (to_x, to_y),
            'move_result': move_result,
            'drag_result': drag_result
        }

    def scroll(self, clicks: int = 3, x: Optional[int] = None,
               y: Optional[int] = None) -> dict:
        """Scroll with natural speed variation."""
        if x is not None and y is not None:
            self.move_to(x, y)

        for i in range(abs(clicks)):
            direction = 1 if clicks > 0 else -1
            pyautogui.scroll(direction, _pause=False)
            time.sleep(random.uniform(0.03, 0.1))

        return {'action': 'scroll', 'clicks': clicks, 'position': pyautogui.position()}

    # ── Bezier Math ───────────────────────────────────────────────

    def _generate_control_points(self, x0: float, y0: float,
                                  x3: float, y3: float,
                                  distance: float) -> Tuple[Tuple, Tuple]:
        """
        Generate two control points for a cubic Bezier curve.
        The control points create a natural arc, not a straight line.
        """
        # Midpoint
        mx, my = (x0 + x3) / 2, (y0 + y3) / 2

        # Perpendicular offset for arc (scaled by distance)
        arc_scale = distance * random.uniform(0.1, 0.35)
        angle = math.atan2(y3 - y0, x3 - x0)
        perp = angle + math.pi / 2 * random.choice([-1, 1])

        # Control point 1: ~30% along path with arc offset
        t1 = random.uniform(0.2, 0.4)
        cp1 = (
            x0 + (x3 - x0) * t1 + math.cos(perp) * arc_scale * random.uniform(0.3, 0.7),
            y0 + (y3 - y0) * t1 + math.sin(perp) * arc_scale * random.uniform(0.3, 0.7)
        )

        # Control point 2: ~70% along path with smaller offset
        t2 = random.uniform(0.6, 0.8)
        cp2 = (
            x0 + (x3 - x0) * t2 + math.cos(perp) * arc_scale * random.uniform(0.1, 0.4),
            y0 + (y3 - y0) * t2 + math.sin(perp) * arc_scale * random.uniform(0.1, 0.4)
        )

        return cp1, cp2

    def _bezier_curve(self, x0, y0, x1, y1, x2, y2, x3, y3,
                       steps: int) -> List[Tuple[float, float]]:
        """Compute points along a cubic Bezier curve."""
        points = []
        for i in range(steps + 1):
            t = i / steps
            t2 = t * t
            t3 = t2 * t
            mt = 1 - t
            mt2 = mt * mt
            mt3 = mt2 * mt

            px = mt3 * x0 + 3 * mt2 * t * x1 + 3 * mt * t2 * x2 + t3 * x3
            py = mt3 * y0 + 3 * mt2 * t * y1 + 3 * mt * t2 * y2 + t3 * y3
            points.append((px, py))

        return points

    def _calculate_duration(self, distance: float) -> float:
        """
        Calculate movement duration using Fitts' Law approximation.
        Returns duration in seconds.
        """
        # Base: ~0.2s for short moves, ~0.8s for long moves
        base = 0.15 + 0.12 * math.log2(max(distance / 10, 1) + 1)
        # Add human variability
        return base * random.uniform(0.8, 1.2) / self.base_speed

    def _ease_in_out(self, t: float) -> float:
        """Smooth ease-in-out curve (slow-fast-slow)."""
        if t < 0.5:
            return 2 * t * t
        return 1 - (-2 * t + 2) ** 2 / 2

    def _overshoot_correction(self, target_x: int, target_y: int,
                               distance: float):
        """
        Slightly overshoot the target, then correct back —
        mimicking human muscle memory imprecision.
        """
        overshoot_dist = random.uniform(3, min(distance * 0.08, 15))
        angle = random.uniform(0, 2 * math.pi)

        ox = target_x + math.cos(angle) * overshoot_dist
        oy = target_y + math.sin(angle) * overshoot_dist

        pyautogui.moveTo(int(ox), int(oy), _pause=False)
        time.sleep(random.uniform(0.04, 0.1))

        # Correct back to target
        correction_steps = random.randint(3, 8)
        cx, cy = ox, oy
        for _ in range(correction_steps):
            cx += (target_x - cx) * random.uniform(0.3, 0.6)
            cy += (target_y - cy) * random.uniform(0.3, 0.6)
            pyautogui.moveTo(int(cx), int(cy), _pause=False)
            time.sleep(random.uniform(0.01, 0.03))

    def _do_click(self, button: str = 'left', double: bool = False):
        """Perform a click with natural timing."""
        if double:
            pyautogui.click(button=button, _pause=False)
            time.sleep(random.uniform(0.05, 0.12))
            pyautogui.click(button=button, _pause=False)
        else:
            pyautogui.click(button=button, _pause=False)

    @staticmethod
    def get_position() -> Tuple[int, int]:
        """Get current mouse position."""
        return pyautogui.position()
