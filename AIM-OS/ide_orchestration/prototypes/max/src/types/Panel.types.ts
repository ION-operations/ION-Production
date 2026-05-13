// Panel Types
export type PanelType =
  | 'file-explorer'
  | 'component-library'
  | 'ai-memory'
  | 'git'
  | 'templates'
  | 'outline'
  | 'properties'
  | 'layers'
  | 'assets'
  | 'settings'
  | 'terminal'
  | 'problems'
  | 'output'
  | 'debug-console'
  | 'timeline'
  | 'main-chat'
  | 'coding-agent'
  | 'planning-agent'
  | 'context-chat'
  | 'super-index'
  | 'master-index'
  | 'system-map'
  | 'nl-tags'
  | 'documentation'
  | 'context-web'
  | 'evolution-explorer'
  | 'hierarchical-code-explorer'
  | 'file-version-history'
  | 'file-changes-viewer';

// Zone Types
export type ZoneType = 'left' | 'right' | 'top' | 'bottom' | 'center' | 'floating';

// Panel Group Types
export type GroupType = 'tabs' | 'accordion' | 'stack' | 'grid';

// Panel State
export interface Panel {
  id: string;
  type: PanelType;
  zone: ZoneType;
  size: number; // Percentage or pixels
  minSize: number;
  maxSize: number;
  visible: boolean;
  expanded: boolean;
  pinned: boolean;
  groupId?: string;
  order: number;
  settings: Record<string, any>;
}

// Zone State
export interface Zone {
  id: string;
  type: ZoneType;
  size: number;
  minSize: number;
  maxSize: number;
  visible: boolean;
  collapsible: boolean;
  resizable: boolean;
  panels: string[]; // Panel IDs
}

// Layout State
export interface Layout {
  id: string;
  name: string;
  zones: Zone[];
  panels: Panel[];
  createdAt: string;
  updatedAt: string;
}

// Panel Manager State
export interface PanelManagerState {
  layouts: Layout[];
  currentLayout: Layout | null;
  draggedPanel: Panel | null;
  dropTarget: Zone | null;
  selectedPanel: Panel | null;
}

