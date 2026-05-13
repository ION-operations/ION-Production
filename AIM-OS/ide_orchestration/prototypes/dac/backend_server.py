#!/usr/bin/env python3
"""
Standalone backend server for DAC IDE
Serves system indexes, system maps, and other IDE-specific endpoints
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json
import re
import os
import yaml

app = FastAPI(title="DAC IDE Backend API", version="1.0.0")

# Enable CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache with TTL
cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_MINUTES = 5


def get_cached_or_fetch(key: str, fetch_fn, ttl_minutes: int = CACHE_TTL_MINUTES):
    """Get from cache or fetch and cache."""
    now = datetime.now()
    
    # Check cache
    if key in cache:
        cached_data = cache[key]
        expiry = cached_data.get("expiry")
        if expiry and now < expiry:
            return cached_data["data"]
    
    # Fetch and cache
    data = fetch_fn()
    cache[key] = {
        "data": data,
        "expiry": now + timedelta(minutes=ttl_minutes)
    }
    
    return data


def parse_json5(content: str) -> Dict[str, Any]:
    """
    Parse JSON5 content by stripping comments and trailing commas.
    """
    # Remove single-line comments (// ...)
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Check if // is inside a string (simple check)
        comment_pos = line.find('//')
        if comment_pos >= 0:
            # Check if it's inside quotes
            before_comment = line[:comment_pos]
            quote_count = before_comment.count('"') - before_comment.count('\\"')
            if quote_count % 2 == 0:  # Even number of quotes = not inside string
                line = line[:comment_pos]
        cleaned_lines.append(line)
    cleaned = '\n'.join(cleaned_lines)
    
    # Remove multi-line comments (/* ... */)
    cleaned = re.sub(r'/\*[\s\S]*?\*/', '', cleaned)
    
    # Remove trailing commas before } or ]
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
    
    # Parse as JSON
    return json.loads(cleaned)


def parse_markdown_frontmatter(content: str) -> Dict[str, Any]:
    """
    Parse Markdown file with YAML frontmatter.
    Returns dict with 'frontmatter' and 'content' keys.
    """
    # Check for frontmatter (--- at start)
    if not content.startswith('---'):
        return {"frontmatter": {}, "content": content}
    
    # Find frontmatter end (--- on its own line)
    lines = content.split('\n')
    if len(lines) < 2:
        return {"frontmatter": {}, "content": content}
    
    # Find second ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break
    
    if end_idx is None:
        return {"frontmatter": {}, "content": content}
    
    # Extract frontmatter (lines 1 to end_idx-1)
    frontmatter_lines = lines[1:end_idx]
    frontmatter_text = '\n'.join(frontmatter_lines)
    
    # Extract content (lines end_idx+1 onwards)
    content_lines = lines[end_idx + 1:]
    content_text = '\n'.join(content_lines)
    
    # Parse frontmatter as YAML
    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except Exception:
        frontmatter = {}
    
    return {
        "frontmatter": frontmatter,
        "content": content_text
    }


def find_workspace_root() -> Path:
    """Find workspace root by looking for knowledge_architecture directory."""
    current_dir = Path(os.getcwd())
    workspace_root = current_dir
    max_depth = 5
    depth = 0
    while depth < max_depth:
        if (workspace_root / "knowledge_architecture").exists():
            return workspace_root
        parent = workspace_root.parent
        if parent == workspace_root:  # Reached filesystem root
            break
        workspace_root = parent
        depth += 1
    return workspace_root


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "DAC IDE Backend API"}


@app.get("/api/system-indexes")
def get_system_indexes(systemId: Optional[str] = Query(None, description="Filter by specific system ID")):
    """
    Load all system.index.lucid.json5 files from knowledge_architecture/systems/
    Cached for 5 minutes.
    """
    def fetch():
        workspace_root = find_workspace_root()
        systems_dir = workspace_root / "knowledge_architecture" / "systems"
        
        if not systems_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Systems directory not found: {systems_dir}"
            )
        
        indexes = []
        
        # Recursively find all system.index.lucid.json5 files
        def find_system_indexes(directory: Path):
            try:
                for entry in directory.iterdir():
                    if entry.is_dir():
                        find_system_indexes(entry)
                    elif entry.name == "system.index.lucid.json5":
                        try:
                            content = entry.read_text(encoding="utf-8")
                            parsed = parse_json5(content)
                            
                            # Filter by systemId if provided
                            if systemId and parsed.get("systemId") != systemId:
                                continue
                            
                            indexes.append(parsed)
                        except Exception as e:
                            print(f"Warning: Failed to parse {entry}: {e}")
            except Exception as e:
                print(f"Warning: Error reading directory {directory}: {e}")
        
        find_system_indexes(systems_dir)
        
        if systemId:
            index = next((i for i in indexes if i.get("systemId") == systemId), None)
            if not index:
                raise HTTPException(
                    status_code=404,
                    detail=f"System index not found: {systemId}"
                )
            return {"success": True, "index": index}
        
        return {"success": True, "indexes": indexes}
    
    cache_key = f"system_indexes_{systemId or 'all'}"
    return get_cached_or_fetch(cache_key, fetch)


@app.get("/api/system-indexes/{system_id}")
def get_system_index(system_id: str):
    """Get a specific system index by ID."""
    return get_system_indexes(systemId=system_id)


@app.get("/api/system-maps")
def get_system_maps(systemId: Optional[str] = Query(None, description="Filter by specific system ID")):
    """
    Load all system.map.lucid.json5 files from knowledge_architecture/systems/
    Cached for 5 minutes.
    """
    def fetch():
        workspace_root = find_workspace_root()
        systems_dir = workspace_root / "knowledge_architecture" / "systems"
        
        if not systems_dir.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Systems directory not found: {systems_dir}"
            )
        
        maps = []
        
        # Recursively find all system.map.lucid.json5 files
        def find_system_maps(directory: Path):
            try:
                for entry in directory.iterdir():
                    if entry.is_dir():
                        find_system_maps(entry)
                    elif entry.name == "system.map.lucid.json5":
                        try:
                            content = entry.read_text(encoding="utf-8")
                            parsed = parse_json5(content)
                            
                            # Filter by systemId if provided
                            if systemId and parsed.get("systemId") != systemId:
                                continue
                            
                            maps.append(parsed)
                        except Exception as e:
                            print(f"Warning: Failed to parse {entry}: {e}")
            except Exception as e:
                print(f"Warning: Error reading directory {directory}: {e}")
        
        find_system_maps(systems_dir)
        
        if systemId:
            system_map = next((m for m in maps if m.get("systemId") == systemId), None)
            if not system_map:
                raise HTTPException(
                    status_code=404,
                    detail=f"System map not found: {systemId}"
                )
            return {"success": True, "map": system_map}
        
        return {"success": True, "maps": maps}
    
    cache_key = f"system_maps_{systemId or 'all'}"
    return get_cached_or_fetch(cache_key, fetch)


@app.get("/api/system-maps/{system_id}")
def get_system_map(system_id: str):
    """Get a specific system map by ID."""
    return get_system_maps(systemId=system_id)


@app.get("/api/super-index")
def get_super_index():
    """
    Load SUPER_INDEX.md from knowledge_architecture/
    Returns parsed frontmatter and content.
    """
    def fetch():
        workspace_root = find_workspace_root()
        super_index_path = workspace_root / "knowledge_architecture" / "SUPER_INDEX.md"
        
        if not super_index_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"SUPER_INDEX.md not found: {super_index_path}"
            )
        
        content = super_index_path.read_text(encoding="utf-8")
        parsed = parse_markdown_frontmatter(content)
        
        return {
            "success": True,
            "frontmatter": parsed["frontmatter"],
            "content": parsed["content"],
            "file_path": str(super_index_path.relative_to(workspace_root))
        }
    
    return get_cached_or_fetch("super_index", fetch)


@app.get("/api/goal-tree")
def get_goal_tree():
    """
    Load GOAL_TREE.yaml from goals/
    Returns parsed YAML structure.
    """
    def fetch():
        workspace_root = find_workspace_root()
        goal_tree_path = workspace_root / "goals" / "GOAL_TREE.yaml"
        
        if not goal_tree_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"GOAL_TREE.yaml not found: {goal_tree_path}"
            )
        
        content = goal_tree_path.read_text(encoding="utf-8")
        
        # Parse YAML (may have frontmatter)
        parsed = parse_markdown_frontmatter(content)
        if parsed["frontmatter"]:
            # If frontmatter exists, parse main content as YAML too
            try:
                goal_data = yaml.safe_load(parsed["content"])
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse GOAL_TREE.yaml: {str(e)}"
                )
            # Merge frontmatter with goal data
            goal_data = {**parsed["frontmatter"], **goal_data}
        else:
            # No frontmatter, parse entire content as YAML
            try:
                goal_data = yaml.safe_load(content)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse GOAL_TREE.yaml: {str(e)}"
                )
        
        return {
            "success": True,
            "data": goal_data,
            "file_path": str(goal_tree_path.relative_to(workspace_root))
        }
    
    return get_cached_or_fetch("goal_tree", fetch)


@app.get("/api/hierarchical-navigation")
def get_hierarchical_navigation():
    """
    Load HIERARCHICAL_NAVIGATION_INDEX.md from knowledge_architecture/
    Returns parsed frontmatter and content.
    """
    def fetch():
        workspace_root = find_workspace_root()
        nav_index_path = workspace_root / "knowledge_architecture" / "HIERARCHICAL_NAVIGATION_INDEX.md"
        
        if not nav_index_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"HIERARCHICAL_NAVIGATION_INDEX.md not found: {nav_index_path}"
            )
        
        content = nav_index_path.read_text(encoding="utf-8")
        parsed = parse_markdown_frontmatter(content)
        
        return {
            "success": True,
            "frontmatter": parsed["frontmatter"],
            "content": parsed["content"],
            "file_path": str(nav_index_path.relative_to(workspace_root))
        }
    
    return get_cached_or_fetch("hierarchical_navigation", fetch)


if __name__ == "__main__":
    import uvicorn
    # Run without reload to avoid import string requirement
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

