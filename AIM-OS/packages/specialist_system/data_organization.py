"""
Data Organization System

Organizes specialist data hierarchically (primary, connected, extended).

NL_TAG: SPECIALIST-DATA-001 | Organize specialist data hierarchically | organizeData | []
NL_TAG_CONNECT: SPECIALIST-CMC-003 | Store organized data in CMC | organizeData → cmc.storeAtom | [SPECIALIST-DATA-001, CMC-STORE-001]
NL_TAG_INTENT: SPECIALIST-DESIGN-003 | Hierarchical data organization | primary → connected → extended | [ADR-SPECIALIST]
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DataItem:
    """
    Individual data item for specialist.
    """
    id: str
    content: Any
    type: str  # 'primary' | 'connected' | 'extended'
    tags: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SpecialistData:
    """
    Organized specialist data with hierarchical structure.
    """
    specialist_id: str
    primary_data: List[DataItem] = field(default_factory=list)
    connected_data: List[DataItem] = field(default_factory=list)
    extended_data: List[DataItem] = field(default_factory=list)
    tags: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_all_data(self) -> List[DataItem]:
        """Get all data items (primary + connected + extended)."""
        return self.primary_data + self.connected_data + self.extended_data
    
    def count(self) -> int:
        """Get total number of data items."""
        return len(self.primary_data) + len(self.connected_data) + len(self.extended_data)


class DataOrganizer:
    """
    Organizes specialist data hierarchically.
    
    Data Hierarchy:
    - Primary Data: Core domain knowledge (specialist-owned)
    - Connected Data: Related systems and connections (shared)
    - Extended Data: Broader context and background (general)
    
    NL_TAG: SPECIALIST-DATA-002 | Tag data with specialist metadata | tagData | [SPECIALIST-DATA-001]
    """
    
    def __init__(self):
        """Initialize data organizer."""
        pass
    
    def organize_data(
        self,
        specialist_id: str,
        data: List[Any],
        classification_fn: Optional[callable] = None
    ) -> SpecialistData:
        """
        Organize data into hierarchical structure.
        
        Args:
            specialist_id: ID of specialist
            data: List of data items to organize
            classification_fn: Optional function to classify data items
                              (primary/connected/extended). If None, uses default.
        
        Returns:
            Organized SpecialistData
        """
        specialist_data = SpecialistData(specialist_id=specialist_id)
        
        for item in data:
            # Classify data item
            if classification_fn:
                data_type = classification_fn(item)
            else:
                data_type = self._default_classify(item, specialist_id)
            
            # Create data item
            data_item = DataItem(
                id=f"{specialist_id}_{item.get('id', len(specialist_data.get_all_data()))}",
                content=item,
                type=data_type,
                tags=self._generate_tags(item, specialist_id, data_type)
            )
            
            # Add to appropriate list
            if data_type == 'primary':
                specialist_data.primary_data.append(data_item)
            elif data_type == 'connected':
                specialist_data.connected_data.append(data_item)
            else:
                specialist_data.extended_data.append(data_item)
        
        # Generate overall tags
        specialist_data.tags = self._generate_overall_tags(specialist_data)
        specialist_data.updated_at = datetime.now()
        
        return specialist_data
    
    def _default_classify(
        self,
        item: Any,
        specialist_id: str
    ) -> str:
        """
        Default classification function.
        
        Args:
            item: Data item to classify
            specialist_id: ID of specialist
        
        Returns:
            'primary' | 'connected' | 'extended'
        """
        # Check if item has explicit type
        if isinstance(item, dict) and 'type' in item:
            return item['type']
        
        # Check if item has specialist-specific tags
        if isinstance(item, dict) and 'tags' in item:
            tags = item.get('tags', {})
            if tags.get('specialist') == specialist_id and tags.get('primary'):
                return 'primary'
            if tags.get('specialist') == specialist_id:
                return 'connected'
        
        # Default to extended
        return 'extended'
    
    def _generate_tags(
        self,
        item: Any,
        specialist_id: str,
        data_type: str
    ) -> Dict[str, Any]:
        """
        Generate tags for data item.
        
        Args:
            item: Data item
            specialist_id: ID of specialist
            data_type: Type of data (primary/connected/extended)
        
        Returns:
            Tags dictionary
        """
        tags = {
            'specialist': specialist_id,
            'type': data_type,
            'created_at': datetime.now().isoformat()
        }
        
        # Add item-specific tags if available
        if isinstance(item, dict):
            if 'tags' in item:
                tags.update(item['tags'])
            if 'domain' in item:
                tags['domain'] = item['domain']
            if 'system' in item:
                tags['system'] = item['system']
        
        return tags
    
    def _generate_overall_tags(
        self,
        specialist_data: SpecialistData
    ) -> Dict[str, Any]:
        """
        Generate overall tags for specialist data.
        
        Args:
            specialist_data: Organized specialist data
        
        Returns:
            Overall tags dictionary
        """
        # Collect all domains and systems from data
        domains = set()
        systems = set()
        
        for item in specialist_data.get_all_data():
            if isinstance(item.content, dict):
                if 'domain' in item.content:
                    if isinstance(item.content['domain'], list):
                        domains.update(item.content['domain'])
                    else:
                        domains.add(item.content['domain'])
                if 'system' in item.content:
                    if isinstance(item.content['system'], list):
                        systems.update(item.content['system'])
                    else:
                        systems.add(item.content['system'])
        
        return {
            'specialist': specialist_data.specialist_id,
            'domain': list(domains),
            'systems': list(systems),
            'primary_count': len(specialist_data.primary_data),
            'connected_count': len(specialist_data.connected_data),
            'extended_count': len(specialist_data.extended_data),
            'total_count': specialist_data.count(),
            'updated_at': specialist_data.updated_at.isoformat()
        }
    
    def get_primary_data(
        self,
        specialist_data: SpecialistData
    ) -> List[DataItem]:
        """
        Get primary data items.
        
        Args:
            specialist_data: Organized specialist data
        
        Returns:
            List of primary data items
        """
        return specialist_data.primary_data
    
    def get_connected_data(
        self,
        specialist_data: SpecialistData
    ) -> List[DataItem]:
        """
        Get connected data items.
        
        Args:
            specialist_data: Organized specialist data
        
        Returns:
            List of connected data items
        """
        return specialist_data.connected_data
    
    def get_extended_data(
        self,
        specialist_data: SpecialistData
    ) -> List[DataItem]:
        """
        Get extended data items.
        
        Args:
            specialist_data: Organized specialist data
        
        Returns:
            List of extended data items
        """
        return specialist_data.extended_data
    
    def tag_data(
        self,
        data: Any,
        specialist_id: str,
        domain: Optional[List[str]] = None,
        systems: Optional[List[str]] = None,
        connections: Optional[List[str]] = None,
        relevance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Tag data with specialist metadata.
        
        Args:
            data: Data to tag
            specialist_id: ID of specialist
            domain: Domain tags
            systems: System tags
            connections: Connection tags
            relevance: Relevance score
        
        Returns:
            Tagged data dictionary
        """
        tags = {
            'specialist': specialist_id,
            'tagged_at': datetime.now().isoformat()
        }
        
        if domain:
            tags['domain'] = domain
        if systems:
            tags['systems'] = systems
        if connections:
            tags['connections'] = connections
        if relevance is not None:
            tags['relevance'] = relevance
        
        # If data is a dict, add tags to it
        if isinstance(data, dict):
            if 'tags' not in data:
                data['tags'] = {}
            data['tags'].update(tags)
            return data
        
        # Otherwise, return dict with data and tags
        return {
            'data': data,
            'tags': tags
        }

