import React from 'react';
import { Panel as PanelComponent } from '../Panel/Panel';
import type { Zone, Panel } from '../../types/Panel.types';
import './Zone.css';

interface ZoneProps {
  zone: Zone;
  panels: Panel[];
}

export const Zone: React.FC<ZoneProps> = ({ zone, panels }) => {
  const sortedPanels = panels
    .filter((p) => p.zone === zone.type && p.visible)
    .sort((a, b) => a.order - b.order);

  return (
    <div className="zone" data-zone-type={zone.type}>
      <div className="zone-header">
        {zone.type.charAt(0).toUpperCase() + zone.type.slice(1)} Zone
      </div>
      <div className="zone-content">
        {sortedPanels.length === 0 ? (
          <div className="zone-empty">
            <p>No panels in this zone</p>
            <p className="zone-hint">Drag panels here to add them</p>
          </div>
        ) : (
          sortedPanels.map((panel) => (
            <PanelComponent key={panel.id} panel={panel} />
          ))
        )}
      </div>
    </div>
  );
};

