"""
AIM-OS SEER — Vision Engine

OpenCV-powered visual recognition system inspired by RuneScape macro architecture.
Instead of sending full screenshots to AI models (~100K tokens), this engine uses
localized template matching, HSV color masking, and visual anchors for sub-5ms
element detection.

Design DNA from Braden's Inferno macro:
- ROI polling (never scan full screen)
- Color tolerance via HSV ranges
- Visual anchor library (saved reference images)
- State change detection via frame differencing
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union

import cv2
import numpy as np

try:
    import mss
    HAS_MSS = True
except ImportError:
    HAS_MSS = False


# ── Paths ──────────────────────────────────────────────────────

SEER_DATA_DIR = Path(os.environ.get(
    'SEER_DATA_DIR',
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'seer')
))
ANCHOR_DIR = SEER_DATA_DIR / 'anchors'


class VisualAnchor:
    """
    A saved reference image for template matching.
    Like RuneScape macro ImageSearch — save once, find forever.
    """

    def __init__(self, name: str, image: np.ndarray,
                 metadata: Optional[Dict] = None):
        self.name = name
        self.image = image
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        self.h, self.w = self.gray.shape[:2]
        self.metadata = metadata or {}

    def save(self, directory: Optional[Path] = None):
        """Save anchor to disk."""
        save_dir = directory or ANCHOR_DIR
        save_dir.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(save_dir / f'{self.name}.png'), self.image)
        with open(save_dir / f'{self.name}.json', 'w') as f:
            json.dump({
                'name': self.name,
                'width': self.w,
                'height': self.h,
                **self.metadata
            }, f, indent=2)

    @classmethod
    def load(cls, name: str, directory: Optional[Path] = None) -> 'VisualAnchor':
        """Load anchor from disk."""
        load_dir = directory or ANCHOR_DIR
        img = cv2.imread(str(load_dir / f'{name}.png'))
        if img is None:
            raise FileNotFoundError(f'Anchor not found: {name}')

        metadata = {}
        meta_path = load_dir / f'{name}.json'
        if meta_path.exists():
            with open(meta_path) as f:
                metadata = json.load(f)

        return cls(name, img, metadata)


class VisionEngine:
    """
    SEER's visual recognition system.
    Operates on numpy arrays from mss screen captures.

    Three search modes:
    1. Template matching (matchTemplate) — fast, exact visual search
    2. HSV color masking — resilient to UI theme changes
    3. Frame differencing — detect state changes
    """

    def __init__(self):
        self._anchors: Dict[str, VisualAnchor] = {}
        self._last_frame: Optional[np.ndarray] = None
        self._region_hashes: Dict[str, str] = {}
        self._sct = mss.mss() if HAS_MSS else None

    # ── Screen Capture (to numpy) ──────────────────────────────

    def capture_region(self, x: int, y: int, w: int, h: int) -> np.ndarray:
        """
        Capture a screen region directly to numpy array.
        Much faster than screenshot → PIL → numpy pipeline.
        """
        if not self._sct:
            raise RuntimeError('mss not available')

        raw = self._sct.grab({'left': x, 'top': y, 'width': w, 'height': h})
        # mss returns BGRA, convert to BGR for OpenCV
        frame = np.array(raw)[:, :, :3]
        return frame

    def capture_full(self, monitor: int = 1) -> np.ndarray:
        """Capture full monitor to numpy array."""
        if not self._sct:
            raise RuntimeError('mss not available')
        monitors = self._sct.monitors
        if monitor >= len(monitors):
            monitor = 1
        raw = self._sct.grab(monitors[monitor])
        return np.array(raw)[:, :, :3]

    # ── Anchor Management ──────────────────────────────────────

    def save_anchor(self, name: str, x: int, y: int,
                    w: int, h: int, metadata: Optional[Dict] = None) -> dict:
        """
        Screenshot a region and save as a named visual anchor.
        The anchor can be found later on any screen with find_anchor().
        """
        frame = self.capture_region(x, y, w, h)
        anchor = VisualAnchor(name, frame, metadata)
        anchor.save()
        self._anchors[name] = anchor

        return {
            'success': True,
            'name': name,
            'size': f'{w}x{h}',
            'saved_to': str(ANCHOR_DIR / f'{name}.png')
        }

    def load_anchor(self, name: str) -> VisualAnchor:
        """Load an anchor from disk or cache."""
        if name not in self._anchors:
            self._anchors[name] = VisualAnchor.load(name)
        return self._anchors[name]

    def list_anchors(self) -> List[Dict]:
        """List all saved anchors."""
        ANCHOR_DIR.mkdir(parents=True, exist_ok=True)
        anchors = []
        for png in ANCHOR_DIR.glob('*.png'):
            name = png.stem
            meta_path = png.with_suffix('.json')
            meta = {}
            if meta_path.exists():
                with open(meta_path) as f:
                    meta = json.load(f)
            anchors.append({'name': name, **meta})
        return anchors

    # ── Template Matching (ImageSearch) ────────────────────────

    def find_anchor(self, name: str,
                    roi: Optional[Dict] = None,
                    threshold: float = 0.8,
                    multi: bool = False) -> dict:
        """
        Find a visual anchor on screen using template matching.
        This is SEER's ImageSearch — Braden's macro paradigm.

        Args:
            name: Anchor name to search for
            roi: Optional {x, y, w, h} region of interest (localized search)
            threshold: Match confidence threshold (0.0 - 1.0)
            multi: If True, return all matches above threshold

        Returns:
            dict with found status, coordinates, confidence
        """
        t_start = time.perf_counter()

        anchor = self.load_anchor(name)

        # Capture the search area
        if roi:
            frame = self.capture_region(roi['x'], roi['y'], roi['w'], roi['h'])
            offset_x, offset_y = roi['x'], roi['y']
        else:
            frame = self.capture_full()
            offset_x, offset_y = 0, 0

        # Convert to grayscale for matching
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Template matching
        result = cv2.matchTemplate(gray, anchor.gray, cv2.TM_CCOEFF_NORMED)

        elapsed_ms = (time.perf_counter() - t_start) * 1000

        if multi:
            # Find all matches above threshold
            locations = np.where(result >= threshold)
            matches = []
            for pt in zip(*locations[::-1]):
                matches.append({
                    'x': int(pt[0] + offset_x),
                    'y': int(pt[1] + offset_y),
                    'center_x': int(pt[0] + offset_x + anchor.w // 2),
                    'center_y': int(pt[1] + offset_y + anchor.h // 2),
                    'confidence': float(result[pt[1], pt[0]])
                })
            # Deduplicate nearby matches
            matches = self._dedupe_matches(matches, anchor.w, anchor.h)
            return {
                'found': len(matches) > 0,
                'matches': matches,
                'count': len(matches),
                'search_ms': round(elapsed_ms, 1)
            }
        else:
            # Find best single match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                return {
                    'found': True,
                    'x': int(max_loc[0] + offset_x),
                    'y': int(max_loc[1] + offset_y),
                    'center_x': int(max_loc[0] + offset_x + anchor.w // 2),
                    'center_y': int(max_loc[1] + offset_y + anchor.h // 2),
                    'w': anchor.w,
                    'h': anchor.h,
                    'confidence': round(float(max_val), 4),
                    'search_ms': round(elapsed_ms, 1)
                }
            else:
                return {
                    'found': False,
                    'best_confidence': round(float(max_val), 4),
                    'threshold': threshold,
                    'search_ms': round(elapsed_ms, 1)
                }

    def find_image(self, template: np.ndarray,
                   roi: Optional[Dict] = None,
                   threshold: float = 0.8) -> dict:
        """
        Find an arbitrary image on screen (not a saved anchor).
        Useful for one-off searches.
        """
        if roi:
            frame = self.capture_region(roi['x'], roi['y'], roi['w'], roi['h'])
            offset_x, offset_y = roi['x'], roi['y']
        else:
            frame = self.capture_full()
            offset_x, offset_y = 0, 0

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY) if len(template.shape) == 3 else template

        result = cv2.matchTemplate(gray_frame, gray_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        th, tw = gray_template.shape[:2]

        if max_val >= threshold:
            return {
                'found': True,
                'x': int(max_loc[0] + offset_x),
                'y': int(max_loc[1] + offset_y),
                'center_x': int(max_loc[0] + offset_x + tw // 2),
                'center_y': int(max_loc[1] + offset_y + th // 2),
                'confidence': round(float(max_val), 4)
            }
        return {'found': False, 'best_confidence': round(float(max_val), 4)}

    # ── HSV Color Search ───────────────────────────────────────

    def find_color(self, hsv_lower: Tuple[int, int, int],
                   hsv_upper: Tuple[int, int, int],
                   roi: Optional[Dict] = None,
                   min_area: int = 50) -> dict:
        """
        Find regions matching an HSV color range.
        Like RuneScape macro color tolerance — resilient to UI theme shifts.

        Args:
            hsv_lower: Lower HSV bound, e.g. (100, 50, 50) for blue
            hsv_upper: Upper HSV bound, e.g. (130, 255, 255) for blue
            roi: Optional region of interest
            min_area: Minimum contour area to count as a match

        Returns:
            dict with found regions (bounding boxes + centers)
        """
        t_start = time.perf_counter()

        if roi:
            frame = self.capture_region(roi['x'], roi['y'], roi['w'], roi['h'])
            offset_x, offset_y = roi['x'], roi['y']
        else:
            frame = self.capture_full()
            offset_x, offset_y = 0, 0

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(hsv_lower), np.array(hsv_upper))

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            bx, by, bw, bh = cv2.boundingRect(cnt)
            regions.append({
                'x': int(bx + offset_x),
                'y': int(by + offset_y),
                'w': int(bw),
                'h': int(bh),
                'center_x': int(bx + offset_x + bw // 2),
                'center_y': int(by + offset_y + bh // 2),
                'area': int(area)
            })

        # Sort by area (largest first)
        regions.sort(key=lambda r: r['area'], reverse=True)

        return {
            'found': len(regions) > 0,
            'regions': regions,
            'count': len(regions),
            'search_ms': round((time.perf_counter() - t_start) * 1000, 1)
        }

    def get_pixel_color(self, x: int, y: int,
                        format: str = 'bgr') -> dict:
        """
        Get pixel color at exact coordinates.
        Returns BGR, RGB, or HSV based on format parameter.
        """
        frame = self.capture_region(x, y, 1, 1)
        bgr = tuple(int(v) for v in frame[0, 0])

        result = {'x': x, 'y': y, 'bgr': bgr}

        if format == 'rgb' or format == 'all':
            result['rgb'] = (bgr[2], bgr[1], bgr[0])
        if format == 'hsv' or format == 'all':
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            result['hsv'] = tuple(int(v) for v in hsv_frame[0, 0])
        if format == 'hex' or format == 'all':
            result['hex'] = f'#{bgr[2]:02x}{bgr[1]:02x}{bgr[0]:02x}'

        return result

    # ── State Change Detection ─────────────────────────────────

    def detect_change(self, roi: Dict,
                      threshold: float = 0.02) -> dict:
        """
        Detect if a screen region has changed since last check.
        Uses frame differencing — like macro's "wait until changed".

        Args:
            roi: {x, y, w, h} region to monitor
            threshold: Change sensitivity (0.0 = any change, 1.0 = total change)

        Returns:
            dict with changed status and change magnitude
        """
        key = f'{roi["x"]}_{roi["y"]}_{roi["w"]}_{roi["h"]}'
        frame = self.capture_region(roi['x'], roi['y'], roi['w'], roi['h'])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if key not in self._region_hashes:
            self._region_hashes[key] = gray
            return {'changed': False, 'first_capture': True, 'magnitude': 0.0}

        # Compare with last capture
        prev = self._region_hashes[key]
        diff = cv2.absdiff(prev, gray)
        magnitude = float(np.mean(diff)) / 255.0

        changed = magnitude > threshold
        self._region_hashes[key] = gray

        return {
            'changed': changed,
            'magnitude': round(magnitude, 4),
            'threshold': threshold
        }

    def compute_region_hash(self, roi: Dict) -> str:
        """
        Hash a screen region for fast equality checking.
        Downscales to 16x16 for perceptual hashing.
        """
        frame = self.capture_region(roi['x'], roi['y'], roi['w'], roi['h'])
        small = cv2.resize(frame, (16, 16))
        return hashlib.md5(small.tobytes()).hexdigest()

    # ── Scale-Aware Matching ───────────────────────────────────

    def find_anchor_multiscale(self, name: str,
                                roi: Optional[Dict] = None,
                                scales: Optional[List[float]] = None,
                                threshold: float = 0.75) -> dict:
        """
        Find anchor at multiple scales — handles DPI/zoom differences.
        Searches at 75%, 100%, 125%, 150% by default.
        """
        if scales is None:
            scales = [0.75, 1.0, 1.25, 1.5]

        t_start = time.perf_counter()
        anchor = self.load_anchor(name)

        if roi:
            frame = self.capture_region(roi['x'], roi['y'], roi['w'], roi['h'])
            offset_x, offset_y = roi['x'], roi['y']
        else:
            frame = self.capture_full()
            offset_x, offset_y = 0, 0

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        best_match = None
        best_val = 0

        for scale in scales:
            sw = int(anchor.w * scale)
            sh = int(anchor.h * scale)
            if sw < 5 or sh < 5 or sw > gray.shape[1] or sh > gray.shape[0]:
                continue

            resized = cv2.resize(anchor.gray, (sw, sh))
            result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val
                best_match = {
                    'x': int(max_loc[0] + offset_x),
                    'y': int(max_loc[1] + offset_y),
                    'center_x': int(max_loc[0] + offset_x + sw // 2),
                    'center_y': int(max_loc[1] + offset_y + sh // 2),
                    'w': sw, 'h': sh,
                    'scale': scale,
                    'confidence': round(float(max_val), 4)
                }

        elapsed_ms = (time.perf_counter() - t_start) * 1000

        if best_match and best_match['confidence'] >= threshold:
            return {'found': True, **best_match, 'search_ms': round(elapsed_ms, 1)}
        return {
            'found': False,
            'best_confidence': round(best_val, 4),
            'search_ms': round(elapsed_ms, 1)
        }

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _dedupe_matches(matches: List[Dict], w: int, h: int) -> List[Dict]:
        """Remove overlapping template matches."""
        if not matches:
            return matches

        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m['confidence'], reverse=True)
        filtered = [matches[0]]

        for m in matches[1:]:
            too_close = False
            for f in filtered:
                if abs(m['x'] - f['x']) < w // 2 and abs(m['y'] - f['y']) < h // 2:
                    too_close = True
                    break
            if not too_close:
                filtered.append(m)

        return filtered
