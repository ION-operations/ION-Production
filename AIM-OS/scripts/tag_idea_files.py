#!/usr/bin/env python3
"""
Idea Files Metadata Tagging Script
Adds frontmatter metadata to all idea files
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

def extract_json_metadata(content: str) -> Optional[Dict]:
    """Extract JSON metadata from 'Metadata for Automation' section"""
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            pass
    return None

def extract_contributor_metadata(content: str) -> Dict:
    """Extract metadata from Contributor Metadata section"""
    metadata = {}
    
    # Extract AI Name
    ai_match = re.search(r'\*\*AI Name:\*\*\s*(.+)', content)
    if ai_match:
        metadata['author'] = ai_match.group(1).strip()
    
    # Extract Role
    role_match = re.search(r'\*\*Primary Role:\*\*\s*(.+)', content)
    if role_match:
        metadata['role'] = role_match.group(1).strip().lower()
    
    # Extract Date
    date_match = re.search(r'\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        metadata['created'] = date_match.group(1)
        metadata['updated'] = date_match.group(1)
    
    return metadata

def extract_systems_from_content(content: str) -> List[str]:
    """Extract system references from content"""
    systems = ['CMC', 'HHNI', 'VIF', 'APOE', 'SEG', 'SDF-CVF', 'CAS', 'TCS', 'IIS', 'SCOR', 'MCP', 'LUCID']
    found = []
    for system in systems:
        if system in content or system.lower() in content.lower():
            found.append(system)
    return found

def determine_file_type(filename: str, content: str) -> str:
    """Determine file type from filename and content"""
    # Check filename patterns
    if filename.startswith('SEED_'):
        return 'SEED'
    elif filename.startswith('EXPLORATION_'):
        return 'EXPLORATION'
    elif filename.startswith('BLUEPRINT_'):
        return 'BLUEPRINT'
    elif filename.startswith('FEEDBACK_'):
        return 'FEEDBACK'
    elif filename.startswith('HANDOFF_'):
        return 'HANDOFF'
    elif filename.startswith('SESSION_SUMMARY_') or filename.startswith('SESSION_SUMMARY'):
        return 'SESSION_SUMMARY'
    elif filename.startswith('VALIDATION_'):
        return 'VALIDATION'
    elif filename.startswith('SPEC_'):
        return 'SPEC'
    elif filename.startswith('IMPLEMENTATION_'):
        return 'IMPLEMENTATION'
    elif filename.startswith('ONBOARDING_LOG'):
        return 'ONBOARDING_LOG'
    elif filename.startswith('ANALYSIS_'):
        return 'ANALYSIS'
    elif filename.startswith('HHNI_'):
        return 'HHNI_DOCUMENT'
    elif filename.startswith('TEAM_'):
        return 'TEAM'
    elif filename in ['README.md', 'REGISTRY.md', 'START_HERE.md', 'COORDINATION_GUIDE.md']:
        return 'DOCUMENTATION'
    elif filename.startswith('WELCOME'):
        return 'WELCOME'
    elif 'core_insights' in content.lower() or 'universal' in filename.lower():
        return 'CORE_INSIGHT'
    elif 'discussion' in filename.lower() or 'thread' in filename.lower():
        return 'DISCUSSION'
    elif 'template' in filename.lower():
        return 'TEMPLATE'
    else:
        return 'OTHER'

def determine_role_from_path(filepath: str) -> str:
    """Extract role from file path"""
    # Convert to string and normalize separators
    path_str = str(filepath).replace('\\', '/')
    parts = path_str.split('/')
    
    if 'ideas' in parts:
        idx = parts.index('ideas')
        if idx + 1 < len(parts):
            role = parts[idx + 1]
            # Valid roles
            valid_roles = ['analysts', 'architects', 'builders', 'designers', 'guardians', 'integrators', 'philosophers', 'researchers']
            if role in valid_roles:
                return role.rstrip('s')  # Remove plural: architects -> architect
            # Shared/common directories
            if role in ['core_insights', 'cursor_integration', 'discussions', 'templates', 'ui_innovations']:
                return 'shared'
    return 'shared'

def determine_status(content: str, metadata_json: Optional[Dict]) -> str:
    """Determine status from content and metadata"""
    if metadata_json and 'status' in metadata_json:
        status = metadata_json['status'].lower()
        if status in ['implemented', 'complete', 'done']:
            return 'implemented'
        elif status in ['archived', 'deferred']:
            return 'archived'
        elif status in ['deprecated']:
            return 'deprecated'
    
    # Check content for status indicators
    if 'implemented' in content.lower() or 'complete' in content.lower():
        return 'implemented'
    elif 'archived' in content.lower() or 'deferred' in content.lower():
        return 'archived'
    
    return 'active'

def determine_priority(metadata_json: Optional[Dict], systems: List[str]) -> str:
    """Determine priority from metadata and systems"""
    if metadata_json and 'priority' in metadata_json:
        priority = metadata_json['priority'].lower()
        if priority in ['critical', 'high']:
            return 'high'
        elif priority == 'low':
            return 'low'
        return 'medium'
    
    # Critical systems indicate high priority
    critical_systems = ['CMC', 'HHNI', 'VIF', 'APOE']
    if any(s in critical_systems for s in systems):
        return 'high'
    
    return 'medium'

def generate_idea_id(filepath: str, filename: str, metadata_json: Optional[Dict]) -> str:
    """Generate unique idea ID"""
    if metadata_json and 'id' in metadata_json:
        return metadata_json['id'].lower().replace(' ', '_')
    
    # Generate from path
    parts = filepath.split(os.sep)
    role = determine_role_from_path(filepath)
    name_slug = filename.replace('.md', '').replace('_', '-').lower()
    return f"idea_{role}_{name_slug}"

def create_frontmatter(filepath: str, filename: str, content: str) -> str:
    """Create frontmatter metadata for idea file"""
    # Extract existing metadata
    json_metadata = extract_json_metadata(content)
    contributor_metadata = extract_contributor_metadata(content)
    systems = extract_systems_from_content(content)
    
    # Determine metadata fields
    file_type = determine_file_type(filename, content)
    role = determine_role_from_path(filepath)
    status = determine_status(content, json_metadata)
    priority = determine_priority(json_metadata, systems)
    idea_id = generate_idea_id(filepath, filename, json_metadata)
    
    # Get dates
    created = contributor_metadata.get('created', datetime.now().strftime('%Y-%m-%d'))
    updated = contributor_metadata.get('updated', created)
    author = contributor_metadata.get('author', 'unknown')
    
    # Extract title from content
    title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace('.md', '').replace('_', ' ').title()
    
    # Extract registry ID if exists
    registry_id = None
    if json_metadata and 'id' in json_metadata:
        registry_id = json_metadata['id']
    
    # Generate tags
    tags = [file_type.lower(), role]
    tags.extend([s.lower() for s in systems[:5]])  # Limit to 5 system tags
    
    # Generate related ideas from content
    related_ideas = []
    if json_metadata and 'related_ideas' in json_metadata:
        if isinstance(json_metadata['related_ideas'], list):
            related_ideas = json_metadata['related_ideas']
        elif isinstance(json_metadata['related_ideas'], str):
            related_ideas = [json_metadata['related_ideas']]
    
    # Create frontmatter
    frontmatter = f"""---
id: "{idea_id}"
type: "{file_type}"
role: "{role}"
author: "{author}"
created: "{created}"
updated: "{updated}"
status: "{status}"
priority: "{priority}"
title: "{title}"
systems: {json.dumps(systems)}
tags: {json.dumps(tags)}
related_ideas: {json.dumps(related_ideas)}
hhni_indexed: false
"""
    
    if registry_id:
        frontmatter += f'registry_id: "{registry_id}"\n'
    
    frontmatter += "---\n\n"
    
    return frontmatter

def add_frontmatter_to_file(filepath: Path) -> bool:
    """Add frontmatter to a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has frontmatter
        if content.startswith('---'):
            return False  # Already has frontmatter
        
        # Create frontmatter
        rel_path = str(filepath.relative_to(Path('ideas')))
        frontmatter = create_frontmatter(rel_path, filepath.name, content)
        
        # Add frontmatter to content
        new_content = frontmatter + content
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main function to tag all idea files"""
    ideas_dir = Path('ideas')
    files_tagged = 0
    files_skipped = 0
    
    # Process files in priority order: SEED first, then others
    all_files = list(ideas_dir.rglob('*.md'))
    
    # Sort: SEED files first, then by type
    def sort_key(f):
        if 'SEED' in f.name:
            return (0, f.name)
        elif 'SESSION_SUMMARY' in f.name:
            return (1, f.name)
        elif 'VALIDATION' in f.name:
            return (2, f.name)
        else:
            return (3, f.name)
    
    all_files.sort(key=sort_key)
    
    for filepath in all_files:
        # Skip README.md, REGISTRY.md, START_HERE.md, etc. - process separately
        if filepath.name in ['README.md', 'REGISTRY.md', 'START_HERE.md']:
            continue
        
        if add_frontmatter_to_file(filepath):
            files_tagged += 1
            print(f"Tagged: {filepath.name}")
        else:
            files_skipped += 1
    
    print(f"\nTagged: {files_tagged} files")
    print(f"Skipped (already tagged): {files_skipped} files")
    print(f"Total: {files_tagged + files_skipped} files")

if __name__ == '__main__':
    main()

