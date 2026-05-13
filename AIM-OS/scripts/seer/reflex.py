"""
AIM-OS SEER — Reflex Engine

Async event loop for continuous visual state monitoring.
Inspired by RuneScape's 600ms tick cycle and Braden's macro architecture.

The reflex loop runs at 30-60fps, polling visual anchors and screen regions
for state changes. When a state change is detected, it fires callbacks or
queues actions — without requiring AI vision for every decision.

This is the "Flash" subsystem from the SEER thesis:
- Cognitive layer (Gemini Pro) defines WHAT to watch for
- Reflex layer (this) watches continuously at native speed
- Action layer (kinematics.py) executes the physical response
"""

import asyncio
import time
import logging
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, field

from .vision import VisionEngine

logger = logging.getLogger('seer.reflex')


@dataclass
class WatchTarget:
    """A target the reflex loop is watching for."""
    name: str
    watch_type: str  # 'anchor', 'color', 'change', 'pixel'
    config: Dict
    callback: Optional[Callable] = None
    interval_ms: float = 100  # Poll interval
    timeout_ms: float = 30000  # Max wait time
    active: bool = True
    last_check: float = 0
    result: Optional[Dict] = None
    fired: bool = False


@dataclass
class ReflexEvent:
    """An event fired by the reflex loop."""
    watch_name: str
    event_type: str  # 'found', 'changed', 'timeout', 'lost'
    data: Dict
    timestamp: float = field(default_factory=time.time)


class ReflexEngine:
    """
    SEER's continuous visual monitoring loop.

    Usage:
        reflex = ReflexEngine()

        # Watch for a button to appear
        reflex.watch_anchor('deploy_button', interval_ms=50)

        # Watch for color change in a region
        reflex.watch_change('status_bar', roi={'x': 100, 'y': 50, 'w': 300, 'h': 30})

        # Watch for specific pixel color
        reflex.watch_color('green_light', hsv_lower=(35, 50, 50), hsv_upper=(85, 255, 255),
                           roi={'x': 500, 'y': 200, 'w': 100, 'h': 100})

        # Start the loop
        events = await reflex.run_until(condition='any_fired', timeout_ms=10000)
    """

    def __init__(self, tick_rate_ms: float = 33):  # ~30fps default
        self.vision = VisionEngine()
        self.tick_rate_ms = tick_rate_ms
        self._watches: Dict[str, WatchTarget] = {}
        self._events: List[ReflexEvent] = []
        self._running = False
        self._tick_count = 0
        self._callbacks: Dict[str, List[Callable]] = {}

    # ── Watch Registration ─────────────────────────────────────

    def watch_anchor(self, anchor_name: str, *,
                     roi: Optional[Dict] = None,
                     threshold: float = 0.8,
                     interval_ms: float = 100,
                     timeout_ms: float = 30000,
                     callback: Optional[Callable] = None) -> str:
        """
        Watch for a visual anchor to appear on screen.
        Like macro's WaitUntilImageFound.
        """
        watch = WatchTarget(
            name=f'anchor_{anchor_name}',
            watch_type='anchor',
            config={
                'anchor_name': anchor_name,
                'roi': roi,
                'threshold': threshold
            },
            interval_ms=interval_ms,
            timeout_ms=timeout_ms,
            callback=callback
        )
        self._watches[watch.name] = watch
        return watch.name

    def watch_change(self, name: str, *,
                     roi: Dict,
                     sensitivity: float = 0.02,
                     interval_ms: float = 100,
                     timeout_ms: float = 30000,
                     callback: Optional[Callable] = None) -> str:
        """
        Watch a screen region for any visual change.
        Fires when the region's pixels change beyond sensitivity threshold.
        """
        watch = WatchTarget(
            name=f'change_{name}',
            watch_type='change',
            config={
                'roi': roi,
                'sensitivity': sensitivity
            },
            interval_ms=interval_ms,
            timeout_ms=timeout_ms,
            callback=callback
        )
        self._watches[watch.name] = watch
        return watch.name

    def watch_color(self, name: str, *,
                    hsv_lower: tuple, hsv_upper: tuple,
                    roi: Optional[Dict] = None,
                    min_area: int = 50,
                    interval_ms: float = 100,
                    timeout_ms: float = 30000,
                    callback: Optional[Callable] = None) -> str:
        """
        Watch for a specific color range to appear.
        Like RuneScape's color-tolerance pixel search.
        """
        watch = WatchTarget(
            name=f'color_{name}',
            watch_type='color',
            config={
                'hsv_lower': hsv_lower,
                'hsv_upper': hsv_upper,
                'roi': roi,
                'min_area': min_area
            },
            interval_ms=interval_ms,
            timeout_ms=timeout_ms,
            callback=callback
        )
        self._watches[watch.name] = watch
        return watch.name

    def watch_pixel(self, name: str, *,
                    x: int, y: int,
                    expected_color: Optional[tuple] = None,
                    color_tolerance: int = 20,
                    interval_ms: float = 50,
                    timeout_ms: float = 30000,
                    callback: Optional[Callable] = None) -> str:
        """
        Watch a single pixel for color match or change.
        Fastest possible check — like PixelGetColor in a loop.
        """
        watch = WatchTarget(
            name=f'pixel_{name}',
            watch_type='pixel',
            config={
                'x': x, 'y': y,
                'expected_color': expected_color,
                'color_tolerance': color_tolerance
            },
            interval_ms=interval_ms,
            timeout_ms=timeout_ms,
            callback=callback
        )
        self._watches[watch.name] = watch
        return watch.name

    def remove_watch(self, name: str):
        """Remove a watch by name."""
        self._watches.pop(name, None)

    def clear_watches(self):
        """Remove all watches."""
        self._watches.clear()

    # ── Event Loop ─────────────────────────────────────────────

    async def run_until(self, *,
                        condition: str = 'any_fired',
                        timeout_ms: float = 30000,
                        max_ticks: int = 0) -> List[ReflexEvent]:
        """
        Run the reflex loop until a condition is met.

        Conditions:
            'any_fired'  — stop when any watch fires
            'all_fired'  — stop when all watches fire
            'timeout'    — run until timeout
            'manual'     — run until stop() is called

        Returns:
            List of events that occurred during the run
        """
        self._running = True
        self._events.clear()
        self._tick_count = 0
        start_time = time.perf_counter()

        try:
            while self._running:
                tick_start = time.perf_counter()
                self._tick_count += 1

                # Check timeout
                elapsed_ms = (tick_start - start_time) * 1000
                if timeout_ms > 0 and elapsed_ms >= timeout_ms:
                    self._fire_event('_system', 'timeout', {'elapsed_ms': elapsed_ms})
                    break

                if max_ticks > 0 and self._tick_count >= max_ticks:
                    break

                # Process all active watches
                for watch in list(self._watches.values()):
                    if not watch.active or watch.fired:
                        continue

                    # Check if it's time to poll this watch
                    now = time.perf_counter()
                    if (now - watch.last_check) * 1000 < watch.interval_ms:
                        continue
                    watch.last_check = now

                    # Check per-watch timeout
                    if watch.timeout_ms > 0:
                        watch_elapsed = (now - start_time) * 1000
                        if watch_elapsed >= watch.timeout_ms:
                            watch.fired = True
                            self._fire_event(watch.name, 'timeout', {})
                            continue

                    # Execute the watch check
                    self._check_watch(watch)

                # Check stop conditions
                if condition == 'any_fired' and any(w.fired for w in self._watches.values()):
                    break
                elif condition == 'all_fired' and all(w.fired for w in self._watches.values()):
                    break

                # Sleep for remaining tick time
                tick_elapsed = (time.perf_counter() - tick_start) * 1000
                sleep_ms = max(self.tick_rate_ms - tick_elapsed, 1)
                await asyncio.sleep(sleep_ms / 1000)

        finally:
            self._running = False

        return self._events

    def stop(self):
        """Stop the reflex loop."""
        self._running = False

    # ── Watch Execution ────────────────────────────────────────

    def _check_watch(self, watch: WatchTarget):
        """Execute a single watch check."""
        try:
            if watch.watch_type == 'anchor':
                result = self.vision.find_anchor(
                    watch.config['anchor_name'],
                    roi=watch.config.get('roi'),
                    threshold=watch.config['threshold']
                )
                if result.get('found'):
                    watch.result = result
                    watch.fired = True
                    self._fire_event(watch.name, 'found', result)

            elif watch.watch_type == 'change':
                result = self.vision.detect_change(
                    watch.config['roi'],
                    threshold=watch.config['sensitivity']
                )
                if result.get('changed'):
                    watch.result = result
                    watch.fired = True
                    self._fire_event(watch.name, 'changed', result)

            elif watch.watch_type == 'color':
                result = self.vision.find_color(
                    watch.config['hsv_lower'],
                    watch.config['hsv_upper'],
                    roi=watch.config.get('roi'),
                    min_area=watch.config.get('min_area', 50)
                )
                if result.get('found'):
                    watch.result = result
                    watch.fired = True
                    self._fire_event(watch.name, 'found', result)

            elif watch.watch_type == 'pixel':
                color_info = self.vision.get_pixel_color(
                    watch.config['x'], watch.config['y'], format='all'
                )
                expected = watch.config.get('expected_color')
                if expected:
                    bgr = color_info['bgr']
                    tolerance = watch.config.get('color_tolerance', 20)
                    if all(abs(bgr[i] - expected[i]) <= tolerance for i in range(3)):
                        watch.result = color_info
                        watch.fired = True
                        self._fire_event(watch.name, 'found', color_info)
                else:
                    # No expected color — just report what's there
                    watch.result = color_info

        except Exception as e:
            logger.error(f'Watch {watch.name} error: {e}')

    def _fire_event(self, watch_name: str, event_type: str, data: Dict):
        """Create and store a reflex event."""
        event = ReflexEvent(
            watch_name=watch_name,
            event_type=event_type,
            data=data
        )
        self._events.append(event)
        logger.info(f'[REFLEX] {event_type}: {watch_name} — {data}')

        # Fire callback if registered
        watch = self._watches.get(watch_name)
        if watch and watch.callback:
            try:
                watch.callback(event)
            except Exception as e:
                logger.error(f'Callback error for {watch_name}: {e}')

    # ── Convenience Methods ────────────────────────────────────

    async def wait_for_anchor(self, anchor_name: str, *,
                               roi: Optional[Dict] = None,
                               threshold: float = 0.8,
                               timeout_ms: float = 10000) -> Optional[Dict]:
        """
        Wait for a visual anchor to appear. Returns match result or None on timeout.
        The simplest possible SEER pattern — "wait until you see this."
        """
        self.clear_watches()
        self.watch_anchor(anchor_name, roi=roi, threshold=threshold, timeout_ms=timeout_ms)
        events = await self.run_until(condition='any_fired', timeout_ms=timeout_ms)

        for event in events:
            if event.event_type == 'found':
                return event.data
        return None

    async def wait_for_change(self, roi: Dict, *,
                               sensitivity: float = 0.02,
                               timeout_ms: float = 10000) -> Optional[Dict]:
        """Wait for a screen region to change visually."""
        self.clear_watches()
        self.watch_change('region', roi=roi, sensitivity=sensitivity, timeout_ms=timeout_ms)
        events = await self.run_until(condition='any_fired', timeout_ms=timeout_ms)

        for event in events:
            if event.event_type == 'changed':
                return event.data
        return None

    def get_stats(self) -> Dict:
        """Get reflex engine stats."""
        return {
            'tick_count': self._tick_count,
            'tick_rate_ms': self.tick_rate_ms,
            'active_watches': len([w for w in self._watches.values() if w.active]),
            'total_events': len(self._events),
            'running': self._running
        }
