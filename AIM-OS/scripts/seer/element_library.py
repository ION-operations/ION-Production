"""
AIM-OS SEER — Element Library

Production-grade storage system for visual UI elements.
Elements are organized by application and page, searchable by name,
type, and metadata. All elements are available to any agent via MCP tools.

Architecture:
  data/seer/elements/
  ├── apps.json                     ← app registry
  ├── chatgpt/
  │   ├── _profile.json             ← app metadata
  │   ├── main/
  │   │   ├── _page.json            ← page layout + scroll state
  │   │   ├── send_button.png       ← visual anchor
  │   │   ├── send_button.json      ← element metadata
  │   │   ├── input_box.png
  │   │   └── input_box.json
  │   └── settings/
  │       ├── _page.json
  │       └── ...
  ├── joc/
  │   └── dashboard/
  │       └── ...
  └── vscode/
      └── ...
"""

import os
import json
import time
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict

import cv2
import numpy as np


# ── Storage Root ───────────────────────────────────────────

ELEMENTS_DIR = Path(os.environ.get(
    'SEER_ELEMENTS_DIR',
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'seer', 'elements')
))


@dataclass
class Element:
    """A stored UI element with visual anchor and metadata."""
    name: str
    app: str
    page: str
    image_path: str = ''
    selector: str = ''            # CSS selector (from DOM)
    element_type: str = 'button'  # button, input, link, tab, menu, icon, text, region
    description: str = ''
    x: int = 0                    # Last known screen position
    y: int = 0
    w: int = 0                    # Element dimensions
    h: int = 0
    tags: List[str] = field(default_factory=list)
    confidence_threshold: float = 0.8
    click_offset_x: int = 0      # Offset from center for click target
    click_offset_y: int = 0
    dpi_scale: float = 1.0
    created_at: float = 0
    last_found_at: float = 0
    find_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Element':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ElementLibrary:
    """
    Production element storage and retrieval system.
    Organizes visual anchors by app/page with full metadata.
    All elements searchable and available to any agent via MCP.
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root = root_dir or ELEMENTS_DIR
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Element] = {}
        self._load_registry()

    # ── Registry ───────────────────────────────────────────

    def _load_registry(self):
        """Load the app registry."""
        reg_path = self.root / 'apps.json'
        if reg_path.exists():
            with open(reg_path) as f:
                self._registry = json.load(f)
        else:
            self._registry = {'apps': {}, 'created_at': time.time()}
            self._save_registry()

    def _save_registry(self):
        """Save the app registry."""
        with open(self.root / 'apps.json', 'w') as f:
            json.dump(self._registry, f, indent=2)

    # ── App Management ─────────────────────────────────────

    def register_app(self, app_name: str, description: str = '',
                     window_title_pattern: str = '',
                     metadata: Optional[Dict] = None) -> dict:
        """Register a new application in the element library."""
        app_dir = self.root / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        profile = {
            'name': app_name,
            'description': description,
            'window_title_pattern': window_title_pattern,
            'metadata': metadata or {},
            'pages': [],
            'created_at': time.time()
        }

        with open(app_dir / '_profile.json', 'w') as f:
            json.dump(profile, f, indent=2)

        self._registry['apps'][app_name] = {
            'description': description,
            'pages': 0,
            'elements': 0
        }
        self._save_registry()

        return {'success': True, 'app': app_name, 'path': str(app_dir)}

    def list_apps(self) -> List[Dict]:
        """List all registered applications."""
        apps = []
        for app_name, info in self._registry.get('apps', {}).items():
            app_dir = self.root / app_name
            profile_path = app_dir / '_profile.json'
            profile = {}
            if profile_path.exists():
                with open(profile_path) as f:
                    profile = json.load(f)
            apps.append({
                'name': app_name,
                'description': info.get('description', ''),
                'pages': len(list(app_dir.iterdir())) - 1 if app_dir.exists() else 0,
                **{k: v for k, v in profile.items() if k not in ('name', 'description')}
            })
        return apps

    # ── Page Management ────────────────────────────────────

    def register_page(self, app: str, page: str,
                      url_pattern: str = '',
                      description: str = '',
                      scroll_height: int = 0,
                      viewport: Optional[Dict] = None) -> dict:
        """Register a page within an application."""
        page_dir = self.root / app / page
        page_dir.mkdir(parents=True, exist_ok=True)

        page_data = {
            'app': app,
            'page': page,
            'url_pattern': url_pattern,
            'description': description,
            'scroll_height': scroll_height,
            'viewport': viewport or {},
            'elements': [],
            'created_at': time.time(),
            'last_calibrated': time.time()
        }

        with open(page_dir / '_page.json', 'w') as f:
            json.dump(page_data, f, indent=2)

        return {'success': True, 'app': app, 'page': page, 'path': str(page_dir)}

    def list_pages(self, app: str) -> List[Dict]:
        """List all pages for an application."""
        app_dir = self.root / app
        if not app_dir.exists():
            return []

        pages = []
        for item in app_dir.iterdir():
            if item.is_dir():
                page_file = item / '_page.json'
                if page_file.exists():
                    with open(page_file) as f:
                        pages.append(json.load(f))
                else:
                    pages.append({'page': item.name, 'elements': []})
        return pages

    # ── Element Storage ────────────────────────────────────

    def store_element(self, element: Element,
                      image: Optional[np.ndarray] = None) -> dict:
        """
        Store a UI element with its visual anchor image.
        This is the core learning operation — capture once, find forever.
        """
        page_dir = self.root / element.app / element.page
        page_dir.mkdir(parents=True, exist_ok=True)

        element.created_at = time.time()

        # Save the image
        if image is not None:
            img_path = page_dir / f'{element.name}.png'
            cv2.imwrite(str(img_path), image)
            element.image_path = str(img_path)

        # Save metadata
        meta_path = page_dir / f'{element.name}.json'
        with open(meta_path, 'w') as f:
            json.dump(element.to_dict(), f, indent=2)

        # Update page element list
        page_file = page_dir / '_page.json'
        if page_file.exists():
            with open(page_file) as f:
                page_data = json.load(f)
            if element.name not in page_data.get('elements', []):
                page_data.setdefault('elements', []).append(element.name)
                with open(page_file, 'w') as f:
                    json.dump(page_data, f, indent=2)

        # Cache it
        cache_key = f'{element.app}/{element.page}/{element.name}'
        self._cache[cache_key] = element

        # Update registry counts
        self._update_counts(element.app)

        return {
            'success': True,
            'element': element.name,
            'app': element.app,
            'page': element.page,
            'image_saved': image is not None,
            'path': str(page_dir / f'{element.name}.png')
        }

    def get_element(self, app: str, page: str, name: str) -> Optional[Element]:
        """Retrieve a stored element by app/page/name."""
        cache_key = f'{app}/{page}/{name}'
        if cache_key in self._cache:
            return self._cache[cache_key]

        meta_path = self.root / app / page / f'{name}.json'
        if not meta_path.exists():
            return None

        with open(meta_path) as f:
            data = json.load(f)

        element = Element.from_dict(data)
        self._cache[cache_key] = element
        return element

    def get_element_image(self, app: str, page: str, name: str) -> Optional[np.ndarray]:
        """Load the visual anchor image for an element."""
        img_path = self.root / app / page / f'{name}.png'
        if not img_path.exists():
            return None
        return cv2.imread(str(img_path))

    def list_elements(self, app: str, page: str) -> List[Dict]:
        """List all elements for an app/page."""
        page_dir = self.root / app / page
        if not page_dir.exists():
            return []

        elements = []
        for json_file in page_dir.glob('*.json'):
            if json_file.name.startswith('_'):
                continue
            with open(json_file) as f:
                elements.append(json.load(f))
        return elements

    def delete_element(self, app: str, page: str, name: str) -> dict:
        """Remove an element from the library."""
        page_dir = self.root / app / page

        for ext in ['.png', '.json']:
            path = page_dir / f'{name}{ext}'
            if path.exists():
                path.unlink()

        cache_key = f'{app}/{page}/{name}'
        self._cache.pop(cache_key, None)

        return {'success': True, 'deleted': name}

    # ── Search ─────────────────────────────────────────────

    def search(self, query: str = '',
               app: Optional[str] = None,
               element_type: Optional[str] = None,
               tags: Optional[List[str]] = None) -> List[Element]:
        """
        Search elements across all apps and pages.
        Any agent can find the element it needs.
        """
        results = []
        search_dirs = []

        if app:
            app_dir = self.root / app
            if app_dir.exists():
                search_dirs = [app_dir]
        else:
            search_dirs = [d for d in self.root.iterdir() if d.is_dir()]

        for app_dir in search_dirs:
            for page_dir in app_dir.iterdir():
                if not page_dir.is_dir():
                    continue
                for json_file in page_dir.glob('*.json'):
                    if json_file.name.startswith('_'):
                        continue
                    with open(json_file) as f:
                        data = json.load(f)

                    element = Element.from_dict(data)

                    # Apply filters
                    if element_type and element.element_type != element_type:
                        continue
                    if tags and not any(t in element.tags for t in tags):
                        continue
                    if query:
                        query_lower = query.lower()
                        searchable = f'{element.name} {element.description} {" ".join(element.tags)}'.lower()
                        if query_lower not in searchable:
                            continue

                    results.append(element)

        return results

    def find_by_name(self, name: str) -> List[Element]:
        """Find all elements with a given name across all apps."""
        return self.search(query=name)

    # ── Helpers ────────────────────────────────────────────

    def _update_counts(self, app: str):
        """Update registry element counts."""
        app_dir = self.root / app
        total_elements = 0
        total_pages = 0

        if app_dir.exists():
            for page_dir in app_dir.iterdir():
                if page_dir.is_dir():
                    total_pages += 1
                    total_elements += len(list(page_dir.glob('*.png')))

        if app in self._registry.get('apps', {}):
            self._registry['apps'][app]['pages'] = total_pages
            self._registry['apps'][app]['elements'] = total_elements
            self._save_registry()

    def get_stats(self) -> dict:
        """Get library statistics."""
        total_apps = len(self._registry.get('apps', {}))
        total_pages = sum(a.get('pages', 0) for a in self._registry.get('apps', {}).values())
        total_elements = sum(a.get('elements', 0) for a in self._registry.get('apps', {}).values())

        return {
            'total_apps': total_apps,
            'total_pages': total_pages,
            'total_elements': total_elements,
            'cache_size': len(self._cache),
            'root_dir': str(self.root)
        }

    def export_manifest(self) -> dict:
        """Export the complete library manifest for agent consumption."""
        manifest = {'apps': {}}
        for app_name in self._registry.get('apps', {}):
            pages = self.list_pages(app_name)
            manifest['apps'][app_name] = {
                'pages': {}
            }
            for page in pages:
                page_name = page.get('page', 'unknown')
                elements = self.list_elements(app_name, page_name)
                manifest['apps'][app_name]['pages'][page_name] = {
                    'element_count': len(elements),
                    'elements': [e.get('name', '') for e in elements]
                }
        return manifest
