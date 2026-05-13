#!/usr/bin/env python3
"""AIM-OS Disk Scanner — Fast top-level directory size analysis.
Uses os.scandir() for speed. Reports top N directories by size.
Usage: python scripts/tools/disk_scanner.py [path] [depth]
"""
import os
import sys
import time
from pathlib import Path

def get_dir_size_fast(path: str, max_depth: int = 1, current_depth: int = 0) -> int:
    """Get directory size using os.scandir (fast, handles permission errors)."""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False) and current_depth < max_depth:
                        total += get_dir_size_fast(entry.path, max_depth, current_depth + 1)
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return total

def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def scan_directory(root: str, scan_depth: int = 10):
    """Scan top-level children of root, recursing up to scan_depth for size calculation."""
    print(f"\n{'='*60}")
    print(f"  AIM-OS Disk Scanner")
    print(f"  Scanning: {root}")
    print(f"{'='*60}\n")

    start = time.time()
    results = []

    # Check for large root-level files
    root_files_size = 0
    try:
        with os.scandir(root) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        fsize = entry.stat(follow_symlinks=False).st_size
                        root_files_size += fsize
                        if fsize > 100 * 1024 * 1024:  # Files > 100MB
                            results.append((entry.name + " [FILE]", fsize))
                    elif entry.is_dir(follow_symlinks=False):
                        dname = entry.name
                        print(f"  Scanning {dname}...", end="", flush=True)
                        dsize = get_dir_size_fast(entry.path, max_depth=scan_depth)
                        results.append((dname, dsize))
                        print(f" {format_size(dsize)}")
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError) as e:
        print(f"Error scanning {root}: {e}")
        return

    if root_files_size > 0:
        results.append(("(root files)", root_files_size))

    elapsed = time.time() - start
    results.sort(key=lambda x: -x[1])

    total = sum(s for _, s in results)
    print(f"\n{'─'*60}")
    print(f"{'Directory':<40} {'Size':>15} {'%':>6}")
    print(f"{'─'*60}")
    for name, size in results:
        pct = (size / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 2)
        flag = " ⚠️" if pct > 20 else ""
        print(f"  {name[:38]:<38} {format_size(size):>15} {pct:>5.1f}% {bar}{flag}")
    print(f"{'─'*60}")
    print(f"  {'TOTAL':<38} {format_size(total):>15}")
    print(f"\n  Scanned in {elapsed:.1f}s")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "C:\\Users\\bombe"
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    scan_directory(target, depth)
