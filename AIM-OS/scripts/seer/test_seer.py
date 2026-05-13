"""
AIM-OS SEER — Desktop Engine Test
Run from a desktop terminal (not headless), e.g.:
    python scripts/seer/test_seer.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print('=' * 60)
print('  AIM-OS SEER — Desktop Engine Test')
print('=' * 60)
print()

# ── Test 1: Imports ────────────────────────────────────────
print('[TEST 1] Module imports')
try:
    from seer.desktop import ScreenCapture, WindowManager, KeyboardController
    from seer.kinematics import MouseKinematics
    print('  ✓ All modules imported')
except Exception as e:
    print(f'  ✗ Import failed: {e}')
    sys.exit(1)

# ── Test 2: Bezier Math ───────────────────────────────────
print()
print('[TEST 2] Bezier kinematics (math only)')
mk = MouseKinematics()
path = mk._bezier_curve(0, 0, 100, 50, 200, 50, 300, 0, 20)
assert len(path) == 21, f'Expected 21 points, got {len(path)}'
assert abs(path[0][0]) < 1 and abs(path[0][1]) < 1, 'Start should be (0,0)'
assert abs(path[-1][0] - 300) < 1, 'End should be (300,0)'
print(f'  ✓ Generated {len(path)} Bezier curve points')
print(f'    Start: ({path[0][0]:.0f}, {path[0][1]:.0f})')
print(f'    Mid:   ({path[10][0]:.0f}, {path[10][1]:.0f})')
print(f'    End:   ({path[-1][0]:.0f}, {path[-1][1]:.0f})')

# ── Test 3: Screen Capture ─────────────────────────────────
print()
print('[TEST 3] Screen capture')
try:
    sc = ScreenCapture()
    monitors = sc.get_monitors()
    print(f'  ✓ Found {len(monitors)} monitor(s)')
    for m in monitors:
        print(f'    {m["name"]}: {m["width"]}x{m["height"]}')

    # Micro-crop test
    crop = sc.micro_crop(100, 100, 150, 150)
    print(f'  ✓ Micro-crop: {crop["width"]}x{crop["height"]}, '
          f'{crop["size_bytes"]} bytes, {crop["capture_ms"]}ms')
except Exception as e:
    print(f'  ✗ Screen capture failed: {e}')

# ── Test 4: Window Manager ─────────────────────────────────
print()
print('[TEST 4] Window manager')
try:
    wm = WindowManager()
    windows = wm.list_windows()
    print(f'  ✓ Found {len(windows)} windows')
    for w in windows[:8]:
        active = '→' if w.get('active') else ' '
        print(f'    {active} {w["title"][:55]}')

    active = wm.get_active_window()
    if active.get('success'):
        print(f'  ✓ Active window: {active["title"][:55]}')
except Exception as e:
    print(f'  ✗ Window manager failed: {e}')

# ── Test 5: Mouse Position ─────────────────────────────────
print()
print('[TEST 5] Mouse position')
try:
    pos = mk.get_position()
    print(f'  ✓ Mouse at: ({pos[0]}, {pos[1]})')
except Exception as e:
    print(f'  ✗ Mouse position failed: {e}')

print()
print('=' * 60)
print('  SEER Engine Tests Complete')
print('=' * 60)
