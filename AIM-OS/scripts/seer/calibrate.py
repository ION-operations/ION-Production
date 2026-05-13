"""
AIM-OS SEER — Calibration Test Harness

Generates a synthetic stroke map with KNOWN properties,
runs it through the generative_path extractor, and measures precision.

Then tests a REAL Nano Banana output against the same pipeline.

Usage:
  1. Generate synthetic reference:
     python scripts/seer/calibrate.py --generate

  2. Test synthetic (sanity check):
     python scripts/seer/calibrate.py --test-synthetic

  3. Test Nano Banana output:
     python scripts/seer/calibrate.py --test-real path/to/nanobanan_output.png
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from pathlib import Path


# ── Output directory ───────────────────────────────────────

CALIBRATION_DIR = Path(os.path.join(os.path.dirname(__file__),
                                     '..', '..', 'data', 'seer', 'calibration'))


def generate_synthetic_stroke_map(output_path: str = None) -> str:
    """
    Generate a synthetic stroke map with KNOWN properties for calibration.

    Creates a 300x300 image with:
    - A curved path from (30,150) to (270,150) with red→blue gradient
    - A green circle (left-click) at the end point
    - A yellow circle (right-click) at a secondary point
    - A red exclusion zone box
    - Variable line thickness (3px → 8px)
    """
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        output_path = str(CALIBRATION_DIR / 'synthetic_stroke_map.png')

    # Black canvas
    canvas = np.zeros((300, 300, 3), dtype=np.uint8)

    # ── Draw the curved path with red→blue gradient ────────
    # Generate a smooth curve (quadratic bezier-esque)
    num_points = 200
    path_points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        x = int(30 + t * 240)  # 30 → 270
        # Sine curve for visual interest
        y = int(150 + 60 * np.sin(t * np.pi * 1.5))
        path_points.append((x, y))

    # Draw path segments with gradient color and variable thickness
    for i in range(len(path_points) - 1):
        t = i / (len(path_points) - 1)

        # Color: Red (0,0,255 BGR) → Blue (255,0,0 BGR)
        r = int(255 * (1 - t))
        b = int(255 * t)
        color = (b, 0, r)  # BGR format

        # Thickness: 3px → 8px
        thickness = int(3 + t * 5)

        cv2.line(canvas, path_points[i], path_points[i + 1], color, thickness)

    # ── Draw action nodes ──────────────────────────────────
    # Green circle (left-click) at path end
    end_point = path_points[-1]
    cv2.circle(canvas, end_point, 8, (0, 255, 0), -1)  # Solid green

    # Yellow circle (right-click) at an offset
    yellow_point = (220, 80)
    cv2.circle(canvas, yellow_point, 8, (0, 255, 255), -1)  # Solid yellow

    # ── Draw exclusion zone ────────────────────────────────
    # Red rectangle (border only)
    cv2.rectangle(canvas, (100, 40), (180, 80), (0, 0, 255), 3)

    # ── Save ───────────────────────────────────────────────
    cv2.imwrite(output_path, canvas)

    # Save ground truth metadata
    ground_truth = {
        'path_start': list(path_points[0]),
        'path_end': list(path_points[-1]),
        'path_point_count': len(path_points),
        'path_direction': 'left_to_right',
        'velocity_start': 'fast (red)',
        'velocity_end': 'slow (blue)',
        'action_nodes': [
            {'type': 'left_click', 'position': list(end_point), 'color': 'green'},
            {'type': 'right_click', 'position': list(yellow_point), 'color': 'yellow'}
        ],
        'exclusion_zones': [
            {'x': 100, 'y': 40, 'w': 80, 'h': 40}
        ],
        'thickness_range': '3px to 8px',
        'canvas_size': [300, 300]
    }

    truth_path = str(CALIBRATION_DIR / 'ground_truth.json')
    with open(truth_path, 'w') as f:
        json.dump(ground_truth, f, indent=2)

    print(f'[SEER CALIBRATION] Synthetic stroke map saved to: {output_path}')
    print(f'[SEER CALIBRATION] Ground truth saved to: {truth_path}')
    return output_path


def test_extraction(image_path: str, label: str = 'Test'):
    """
    Run the generative path extractor on an image and report results.
    """
    from seer.generative_path import GenerativePathExecutor

    print(f'\n{"=" * 60}')
    print(f'  SEER Calibration: {label}')
    print(f'  Image: {image_path}')
    print(f'{"=" * 60}\n')

    executor = GenerativePathExecutor()

    try:
        plan = executor.extract_plan(image_path)
    except Exception as e:
        print(f'  ✗ Extraction FAILED: {e}')
        return

    # ── Path Analysis ──────────────────────────────────────
    print(f'[PATH]')
    print(f'  Nodes extracted: {len(plan.path)}')
    if plan.path:
        start = plan.path[0]
        end = plan.path[-1]
        print(f'  Start: ({start.x}, {start.y}) — velocity: {start.velocity_modifier:.2f}')
        print(f'  End:   ({end.x}, {end.y}) — velocity: {end.velocity_modifier:.2f}')

        # Velocity profile
        velocities = [n.velocity_modifier for n in plan.path]
        avg_vel = sum(velocities) / len(velocities)
        min_vel = min(velocities)
        max_vel = max(velocities)
        print(f'  Velocity range: {min_vel:.2f} → {max_vel:.2f} (avg: {avg_vel:.2f})')

        # Check for smooth gradient
        jumps = 0
        for i in range(1, len(velocities)):
            if abs(velocities[i] - velocities[i - 1]) > 0.3:
                jumps += 1
        print(f'  Velocity smoothness: {jumps} sudden jumps (0 = perfect gradient)')

        # Spatial spread
        xs = [n.x for n in plan.path]
        ys = [n.y for n in plan.path]
        print(f'  X range: {min(xs)} → {max(xs)} ({max(xs) - min(xs)}px span)')
        print(f'  Y range: {min(ys)} → {max(ys)} ({max(ys) - min(ys)}px span)')

    # ── Action Nodes ───────────────────────────────────────
    print(f'\n[ACTION NODES]')
    print(f'  Found: {len(plan.actions)}')
    for action in plan.actions:
        drag_info = f' → drag to ({action.drag_to[0]}, {action.drag_to[1]})' if action.drag_to else ''
        print(f'  • {action.action} at ({action.x}, {action.y}){drag_info}')

    # ── Exclusion Zones ────────────────────────────────────
    print(f'\n[EXCLUSION ZONES]')
    print(f'  Found: {len(plan.exclusion_zones)}')
    for zone in plan.exclusion_zones:
        print(f'  • ({zone["x"]}, {zone["y"]}) {zone["w"]}x{zone["h"]}')

    # ── Dry Run ────────────────────────────────────────────
    print(f'\n[DRY RUN]')
    report = executor.execute(plan, dry_run=True)
    print(f'  Path nodes processed: {report["path_nodes"]}')
    print(f'  Actions queued: {len(report["actions"])}')
    print(f'  Duration (estimated): {report["duration_ms"]}ms')

    print(f'\n{"=" * 60}')
    print(f'  Calibration Complete')
    print(f'{"=" * 60}')


def get_nano_banana_prompt() -> str:
    """Print the exact prompt to paste into Nano Banana."""
    prompt = """Generate a 300x300 pixel image on a pure black background. This is a kinematic instruction map for a robotic cursor system. Follow these rules EXACTLY:

1. Draw a single smooth curved line from the left side (approximately x=30, y=150) to the right side (approximately x=270, y=150).
   - The curve should have a gentle S-shape or wave.
   - The line must be approximately 3-5 pixels wide.
   - The line color must be a smooth gradient starting with PURE RED (#FF0000) on the left, transitioning smoothly through orange and purple to PURE BLUE (#0000FF) on the right.

2. At the exact endpoint of the line (right end), draw a SOLID FILLED GREEN CIRCLE (#00FF00), approximately 10 pixels in diameter.

3. Somewhere above the main path (around y=80), draw a SOLID FILLED YELLOW CIRCLE (#FFFF00), approximately 10 pixels in diameter.

4. Draw a RED RECTANGLE BORDER (no fill, just the outline, 2-3 pixels thick) in the upper-center area of the image, approximately 80x40 pixels.

5. CRITICAL: Do NOT add any text, labels, shadows, glow effects, gradients on the background, or anti-aliased soft edges. Use only hard, solid, saturated colors on a pure black (#000000) background. This image will be read by a computer vision system."""

    return prompt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SEER Calibration Test')
    parser.add_argument('--generate', action='store_true', help='Generate synthetic stroke map')
    parser.add_argument('--test-synthetic', action='store_true', help='Test synthetic map extraction')
    parser.add_argument('--test-real', type=str, help='Test a real Nano Banana output')
    parser.add_argument('--prompt', action='store_true', help='Print the Nano Banana prompt')
    args = parser.parse_args()

    if args.prompt:
        print('\n' + '=' * 60)
        print('  NANO BANANA PROMPT — Copy and paste this exactly:')
        print('=' * 60 + '\n')
        print(get_nano_banana_prompt())
        print()

    elif args.generate:
        generate_synthetic_stroke_map()

    elif args.test_synthetic:
        synth_path = str(CALIBRATION_DIR / 'synthetic_stroke_map.png')
        if not os.path.exists(synth_path):
            print('Generating synthetic map first...')
            generate_synthetic_stroke_map()
        test_extraction(synth_path, label='SYNTHETIC Reference')

    elif args.test_real:
        if not os.path.exists(args.test_real):
            print(f'Error: File not found: {args.test_real}')
            sys.exit(1)
        test_extraction(args.test_real, label='NANO BANANA Output')

    else:
        # Run full calibration: generate + test synthetic
        print('[SEER] Full calibration run...\n')
        path = generate_synthetic_stroke_map()
        test_extraction(path, label='SYNTHETIC Reference')
        print('\n\nNext step: Run with a real Nano Banana image:')
        print('  python scripts/seer/calibrate.py --test-real path/to/image.png')
        print('\nTo get the prompt for Nano Banana:')
        print('  python scripts/seer/calibrate.py --prompt')
