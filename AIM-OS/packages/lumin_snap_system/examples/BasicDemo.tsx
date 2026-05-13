/**
 * Basic Demo - Lumin Snap System
 * 
 * Complete working example showing ghost preview on hover
 * and snap-to-position on click.
 */

import React, { useState, useRef, Suspense } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import * as THREE from 'three';

// Import from the package
import {
  GhostPreviewRenderer,
  SnapOptionPanel,
  SnapEngine,
  LODManager,
  SnapOption
} from '../src';

/**
 * Interactive mesh that can be selected
 */
const SelectableMesh: React.FC<{
  isSelected: boolean;
  onClick: () => void;
  meshRef: React.MutableRefObject<THREE.Mesh | null>;
}> = ({ isSelected, onClick, meshRef }) => {
  return (
    <mesh
      ref={meshRef}
      position={[0, 1, 0]}
      onClick={onClick}
    >
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial 
        color={isSelected ? '#00ffff' : '#ff8844'} 
        transparent 
        opacity={isSelected ? 0.8 : 1}
      />
    </mesh>
  );
};

/**
 * Scene content with ghost preview
 */
const SceneContent: React.FC<{
  selectedMesh: THREE.Mesh | null;
  ghostPosition: THREE.Vector3 | null;
  snapOption: SnapOption | null;
  onMeshSelect: (mesh: THREE.Mesh) => void;
  onMeshRef: (mesh: THREE.Mesh | null) => void;
}> = ({ selectedMesh, ghostPosition, snapOption, onMeshSelect, onMeshRef }) => {
  const { scene } = useThree();
  const meshRef = useRef<THREE.Mesh | null>(null);
  
  // Update container for SnapEngine
  React.useEffect(() => {
    const engine = SnapEngine.getInstance();
    engine.setContainer(new THREE.Box3(
      new THREE.Vector3(-10, 0, -10),
      new THREE.Vector3(10, 10, 10)
    ));
    engine.setScene(scene);
  }, [scene]);

  // Share mesh ref with parent
  React.useEffect(() => {
    onMeshRef(meshRef.current);
  }, [meshRef.current, onMeshRef]);

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 5]} intensity={1} />
      
      {/* Grid */}
      <Grid 
        args={[20, 20]} 
        position={[0, 0, 0]}
        cellSize={1}
        cellColor="#444"
        sectionColor="#666"
        sectionSize={5}
        fadeDistance={30}
      />
      
      {/* Container visualization */}
      <mesh position={[0, 5, 0]}>
        <boxGeometry args={[20, 10, 20]} />
        <meshBasicMaterial color="#333" wireframe transparent opacity={0.3} />
      </mesh>
      
      {/* Selectable object */}
      <SelectableMesh
        meshRef={meshRef}
        isSelected={selectedMesh === meshRef.current}
        onClick={() => meshRef.current && onMeshSelect(meshRef.current)}
      />
      
      {/* Other objects for collision detection */}
      <mesh position={[5, 1, 0]}>
        <boxGeometry args={[2, 2, 2]} />
        <meshStandardMaterial color="#4488ff" />
      </mesh>
      
      <mesh position={[-5, 1, 0]}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial color="#88ff44" />
      </mesh>
      
      {/* Ghost Preview Renderer */}
      <GhostPreviewRenderer
        originalObject={selectedMesh}
        targetPosition={ghostPosition}
        snapOption={snapOption}
        scene={scene}
        opacity={0.5}
        enableCollisionDetection={true}
        enableMeasurements={true}
        onRenderComplete={(event) => {
          console.log(`Ghost render: ${event.renderTimeMs.toFixed(2)}ms, LOD: ${event.lodLevel}`);
        }}
      />
      
      {/* Controls */}
      <OrbitControls />
    </>
  );
};

/**
 * Main Demo Component
 */
export const BasicDemo: React.FC = () => {
  const [selectedMesh, setSelectedMesh] = useState<THREE.Mesh | null>(null);
  const [ghostPosition, setGhostPosition] = useState<THREE.Vector3 | null>(null);
  const [snapOption, setSnapOption] = useState<SnapOption | null>(null);
  const meshRefFromScene = useRef<THREE.Mesh | null>(null);

  // Handle snap option hover
  const handleSnapHover = ({ option, targetPosition }: { option: SnapOption; targetPosition: THREE.Vector3 }) => {
    setSnapOption(option);
    setGhostPosition(targetPosition);
  };

  // Handle snap option leave
  const handleSnapLeave = () => {
    setSnapOption(null);
    setGhostPosition(null);
  };

  // Handle snap option click
  const handleSnapClick = ({ targetPosition }: { targetPosition: THREE.Vector3 }) => {
    if (selectedMesh) {
      selectedMesh.position.copy(targetPosition);
    }
    handleSnapLeave();
  };

  // Handle mesh selection
  const handleMeshSelect = (mesh: THREE.Mesh) => {
    setSelectedMesh(mesh);
  };

  return (
    <div className="flex w-full h-screen bg-gray-900">
      {/* 3D Canvas */}
      <div className="flex-1">
        <Canvas
          camera={{ position: [10, 10, 10], fov: 60 }}
          shadows
        >
          <Suspense fallback={null}>
            <SceneContent
              selectedMesh={selectedMesh}
              ghostPosition={ghostPosition}
              snapOption={snapOption}
              onMeshSelect={handleMeshSelect}
              onMeshRef={(mesh) => { meshRefFromScene.current = mesh; }}
            />
          </Suspense>
        </Canvas>
      </div>

      {/* Snap Panel */}
      <div className="w-72 p-4">
        <SnapOptionPanel
          selectedObject={selectedMesh}
          onSnapOptionHover={handleSnapHover}
          onSnapOptionLeave={handleSnapLeave}
          onSnapOptionClick={handleSnapClick}
          showShortcuts={true}
        />
        
        {/* Stats Panel */}
        <div className="mt-4 p-4 bg-gray-800 rounded-lg">
          <h4 className="text-sm font-semibold text-white mb-2">LOD Manager Stats</h4>
          <Stats />
        </div>

        {/* Instructions */}
        <div className="mt-4 p-4 bg-gray-800 rounded-lg">
          <h4 className="text-sm font-semibold text-white mb-2">Instructions</h4>
          <ul className="text-xs text-gray-400 space-y-1">
            <li>• Click the orange box to select it</li>
            <li>• Hover over snap options to see ghost preview</li>
            <li>• Click a snap option to move the object</li>
            <li>• Use keyboard shortcuts (T, R, B, L, C, X, Y)</li>
            <li>• Yellow/red ghost = collision warning</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

/**
 * Stats display component
 */
const Stats: React.FC = () => {
  const [stats, setStats] = React.useState({
    cacheEntries: 0,
    cacheHits: 0,
    cacheMisses: 0,
    averageRenderTimeMs: 0
  });

  React.useEffect(() => {
    const interval = setInterval(() => {
      const manager = LODManager.getInstance();
      setStats(manager.getStats());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-xs text-gray-400 space-y-1">
      <div>Cache Entries: {stats.cacheEntries}</div>
      <div>Cache Hits: {stats.cacheHits}</div>
      <div>Cache Misses: {stats.cacheMisses}</div>
      <div>Avg Render: {stats.averageRenderTimeMs.toFixed(2)}ms</div>
    </div>
  );
};

export default BasicDemo;

