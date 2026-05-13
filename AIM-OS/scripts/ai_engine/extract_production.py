"""
AIM-OS Production Extraction — Phase 28
========================================

Copies only the real, production-important parts of AIM-OS to a clean directory.
Uses the curated SYSTEM_REGISTRY and deep audit data as the guide.

What gets copied:
  - packages/       (68 subsystems — excluding node_modules, __pycache__, dist, build)
  - scripts/ai_engine/ (27+ engine modules)
  - scripts/seer/   (vision/manipulation subsystem)
  - scripts/ root   (sentinel family, bridge scripts, key utilities)
  - .agent/         (genomes, workflows, comms, trails — excluding cache/runtime)
  - Root configs    (pyproject.toml, requirements.txt, SOURCE_OF_TRUTH.yaml, etc.)
  - Key docs        (README.md, AIM_OS_NORTH_STAR.md, PROJECT_TRUTH/)
  - IDE/extensions/ (our cursor extensions, not the Tauri build)

What gets EXCLUDED:
  - IDE/src-tauri/  (5,610 Rust build files)
  - IDE/node_modules/
  - .venv/          (Python dependencies)
  - node_modules/   (everywhere)
  - __pycache__/    (everywhere)
  - dist/, build/   (compiled output)
  - htmlcov/        (coverage reports)
  - forensics_backups/ (old snapshots)
  - .git/           (git internals)
  - *.pyc, *.pdb, *.o, *.rmeta, *.rlib files

Usage:
  python scripts/ai_engine/extract_production.py [--target PATH] [--dry-run]
"""

import os
import sys
import shutil
import json
import time
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Set

logger = logging.getLogger('extract_production')

# ── Configuration ────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, '..', '..'))
DEFAULT_TARGET = os.path.join(os.path.dirname(DEFAULT_ROOT), 'AIM-OS-Production')

# Directories to skip everywhere
GLOBAL_SKIP_DIRS: Set[str] = {
    'node_modules', '__pycache__', '.git', 'dist', 'build',
    '.next', '.cache', '.turbo', '.pytest_cache',
    'htmlcov', 'coverage', '.coverage',
    'cmc_service.egg-info',
}

# File extensions to skip
SKIP_EXTENSIONS: Set[str] = {
    '.pyc', '.pyo', '.pdb', '.o', '.obj', '.rmeta', '.rlib',
    '.exe', '.dll', '.so', '.dylib', '.wasm',
    '.lock',  # lock files (package-lock.json handled separately)
}

# Large binary extensions to skip
BINARY_SKIP: Set[str] = {
    '.zip', '.tar', '.gz', '.7z', '.rar',
    '.db', '.sqlite', '.pickle',
    '.mp4', '.webm', '.avi',
    '.woff', '.woff2', '.ttf', '.eot',
}

# ── What to copy ─────────────────────────────────────────

# Directories to copy (relative to ROOT)
COPY_DIRS = [
    # Core packages (all 68)
    'packages',
    # AI Engine (the brain)
    'scripts/ai_engine',
    # SEER vision system
    'scripts/seer',
    # Agent comms
    'scripts/agent_comms',
    'scripts/offline_comms',
    # Setup/launchers
    'scripts/launchers',
    'scripts/setup',
    # Agent config
    '.agent/genomes',
    '.agent/workflows',
    '.agent/comms',
    '.agent/trails',
    # Source code
    'src',
    # Config
    'config',
    # Schema definitions
    'schema',
    'schemas',
    # Tests  
    'tests',
    'Testing',
    # IDE extensions (OUR code, not Tauri)
    'IDE/extensions',
    'IDE/src',
    'IDE/.agents',
    # Knowledge architecture
    'knowledge_architecture',
    # Cursor addon
    'cursor-addon',
    # UI editor
    'UIeditor',
    # Deployment
    'deployment',
    # Bootloaders
    'bootloaders',
    # MCP Aether
    'mcp-aether',
    # IDE orchestration
    'ide_orchestration',
    # Project truth
    'PROJECT_TRUTH',
]

# Individual root files to copy
COPY_ROOT_FILES = [
    'README.md',
    'AIM_OS_NORTH_STAR.md',
    'SOURCE_OF_TRUTH.yaml',
    'pyproject.toml',
    'requirements.txt',
    'Makefile',
    '.cursorrules',
    '.editorconfig',
    '.env.template',
    '.gitignore',
    '.gitattributes',
    '10_MODES_SUMMARY.md',
    'AGENTS.md',
    'DO_NOT_TOUCH_MCP.md',
    'MAPPING_COMPLETE_SUMMARY.md',
    'SHARED_MESSAGE_BOARD_ANTIGRAVITY.md',
    'lucid_mcp_server.py',
    'run_mcp_32_tools.py',
    'run_mcp_cross_model.py',
    'pyrightconfig.json',
    'mesh_visualization.html',
]

# Individual script files to copy (sentinel family, key utilities)
COPY_SCRIPT_FILES = [
    'scripts/sentinel.py',
    'scripts/sentinel_chronicle.py',
    'scripts/sentinel_host_baselines.py',
    'scripts/sentinel_mcp_governance.py',
    'scripts/sentinel_nexus.py',
    'scripts/sentinel_phantom.py',
    'scripts/sentinel_policy_engine.py',
    'scripts/sentinel_recon.py',
    'scripts/sentinel_sessions.py',
    'scripts/sentinel_telemetry.py',
    'scripts/sentinel_wraith.py',
    'scripts/security.py',
    'scripts/snapshot_system.py',
    'scripts/mcp_bridge.py',
    'scripts/mcp_sse_server.py',
    'scripts/mcp_http_fallback_server.py',
    'scripts/cloudflare_tunnel.py',
    'scripts/aimos_bridge_host.py',
    'scripts/connection_manager.py',
    'scripts/codebase_analysis.py',
    'scripts/complexity_analysis.py',
    'scripts/assemble_system_map.py',
    'scripts/__init__.py',
]

# .agent root files
COPY_AGENT_FILES = [
    '.agent/SYSTEM_REGISTRY.md',
    '.agent/AIMOS_MASTER_SYSTEM_INDEX.md',
    '.agent/COMMS_DOCTRINE.md',
    '.agent/STARTUP.md',
    '.agent/DO_NOT_PANIC_FIX.md',
    '.agent/DO_NOT_WORK_ALONE.md',
    '.agent/atlas_store.json',
]


# ── Extraction Logic ─────────────────────────────────────

def should_skip_file(filepath: str) -> bool:
    """Check if a file should be skipped."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in SKIP_EXTENSIONS or ext in BINARY_SKIP:
        return True
    basename = os.path.basename(filepath)
    if basename.startswith('.DS_Store'):
        return True
    # Skip very large files (>2MB) — likely generated/binary
    try:
        if os.path.getsize(filepath) > 2_000_000:
            # Exception: allow large .py and .ts files (some are legit)
            if ext not in {'.py', '.ts', '.tsx', '.js', '.md'}:
                return True
    except:
        pass
    return False


def should_skip_dir(dirname: str) -> bool:
    """Check if a directory should be skipped."""
    return dirname in GLOBAL_SKIP_DIRS


def copy_tree(src: str, dst: str, dry_run: bool = False) -> Dict[str, int]:
    """Copy a directory tree, skipping excluded files/dirs. Returns stats."""
    stats = {'files': 0, 'dirs': 0, 'skipped': 0, 'bytes': 0}
    
    if not os.path.isdir(src):
        return stats
    
    for dirpath, dirnames, filenames in os.walk(src):
        # Filter directories in-place
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        
        rel = os.path.relpath(dirpath, src)
        dst_dir = os.path.join(dst, rel) if rel != '.' else dst
        
        if not dry_run:
            os.makedirs(dst_dir, exist_ok=True)
        stats['dirs'] += 1
        
        for f in filenames:
            src_file = os.path.join(dirpath, f)
            if should_skip_file(src_file):
                stats['skipped'] += 1
                continue
            
            dst_file = os.path.join(dst_dir, f)
            if not dry_run:
                shutil.copy2(src_file, dst_file)
            
            try:
                stats['bytes'] += os.path.getsize(src_file)
            except:
                pass
            stats['files'] += 1
    
    return stats


def copy_file(src: str, dst: str, dry_run: bool = False) -> bool:
    """Copy a single file. Returns True if copied."""
    if not os.path.isfile(src):
        return False
    if should_skip_file(src):
        return False
    
    if not dry_run:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return True


def extract(root: str, target: str, dry_run: bool = False) -> Dict[str, any]:
    """Main extraction function."""
    start = time.monotonic()
    
    total_stats = {'files': 0, 'dirs': 0, 'skipped': 0, 'bytes': 0}
    section_stats = {}
    
    if not dry_run:
        os.makedirs(target, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"  AIM-OS Production Extraction")
    print(f"  Source:  {root}")
    print(f"  Target:  {target}")
    print(f"  Mode:    {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")
    
    # 1. Copy directory trees
    for rel_dir in COPY_DIRS:
        src = os.path.join(root, rel_dir)
        dst = os.path.join(target, rel_dir)
        if os.path.isdir(src):
            stats = copy_tree(src, dst, dry_run)
            section_stats[rel_dir] = stats
            for k in total_stats:
                total_stats[k] += stats[k]
            print(f"  {rel_dir:<40s} {stats['files']:>5,} files ({stats['bytes']//1024:>7,} KB)")
        else:
            print(f"  {rel_dir:<40s} (not found, skipped)")
    
    # 2. Copy root files
    root_copied = 0
    for rel_file in COPY_ROOT_FILES:
        src = os.path.join(root, rel_file)
        dst = os.path.join(target, rel_file)
        if copy_file(src, dst, dry_run):
            root_copied += 1
            total_stats['files'] += 1
    print(f"  {'<root files>':<40s} {root_copied:>5,} files")
    
    # 3. Copy script files
    script_copied = 0
    for rel_file in COPY_SCRIPT_FILES:
        src = os.path.join(root, rel_file)
        dst = os.path.join(target, rel_file)
        if copy_file(src, dst, dry_run):
            script_copied += 1
            total_stats['files'] += 1
    print(f"  {'<script files>':<40s} {script_copied:>5,} files")
    
    # 4. Copy .agent files
    agent_copied = 0
    for rel_file in COPY_AGENT_FILES:
        src = os.path.join(root, rel_file)
        dst = os.path.join(target, rel_file)
        if copy_file(src, dst, dry_run):
            agent_copied += 1
            total_stats['files'] += 1
    print(f"  {'<agent files>':<40s} {agent_copied:>5,} files")
    
    elapsed = time.monotonic() - start
    
    # Summary
    print(f"\n{'─'*60}")
    print(f"  TOTAL:")
    print(f"    Files copied:  {total_stats['files']:>8,}")
    print(f"    Files skipped: {total_stats['skipped']:>8,}")
    print(f"    Directories:   {total_stats['dirs']:>8,}")
    print(f"    Size:          {total_stats['bytes']/1024/1024:>8.1f} MB")
    print(f"    Time:          {elapsed:>8.1f}s")
    print(f"{'='*60}\n")
    
    # Write extraction manifest
    manifest = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'source': root,
        'target': target,
        'dry_run': dry_run,
        'total_files': total_stats['files'],
        'total_bytes': total_stats['bytes'],
        'section_stats': {
            k: {'files': v['files'], 'bytes': v['bytes']}
            for k, v in section_stats.items()
        },
    }
    
    manifest_path = os.path.join(target, '_EXTRACTION_MANIFEST.json')
    if not dry_run:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"  Manifest: {manifest_path}")
    
    return total_stats


# ── CLI ──────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract AIM-OS production code')
    parser.add_argument('--source', default=DEFAULT_ROOT, help='Source AIM-OS root')
    parser.add_argument('--target', default=DEFAULT_TARGET, help='Target directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be copied')
    args = parser.parse_args()
    
    extract(args.source, args.target, args.dry_run)
