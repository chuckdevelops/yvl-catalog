
import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame, ThreeEvent } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Text } from '@react-three/drei';
import * as THREE from 'three';

// Silhouette component that follows the mouse position
const CartiSilhouette = ({ 
  position = [0, 0, 0], 
  scale = 1
}: { 
  position?: [number, number, number], 
  scale?: number 
}) => {
  const mesh = useRef<THREE.Mesh>(null!);
  const [hovered, setHover] = useState(false);
  const [showYVLSign, setShowYVLSign] = useState(false);
  const [targetRotation, setTargetRotation] = useState({ x: 0, y: 0 });
  
  // Follow mouse position
  useFrame((state) => {
    if (!mesh.current) return;
    
    // Smooth rotation towards target
    mesh.current.rotation.x += (targetRotation.x - mesh.current.rotation.x) * 0.1;
    mesh.current.rotation.y += (targetRotation.y - mesh.current.rotation.y) * 0.1;
    
    // Subtle floating animation
    mesh.current.position.y = position[1] + Math.sin(state.clock.elapsedTime) * 0.05;
  });
  
  // Handle pointer move for face tracking
  const handlePointerMove = (e: ThreeEvent<PointerEvent>) => {
    if (!mesh.current) return;
    
    // Calculate normalized position (-1 to 1) using pointer coordinates
    const x = (e.point.x / window.innerWidth) * 2 - 1;
    const y = -((e.point.y / window.innerHeight) * 2 - 1);
    
    // Set target rotation based on mouse position
    setTargetRotation({
      x: y * 0.3, // Tilt up/down based on mouse Y position
      y: x * 0.7  // Turn left/right based on mouse X position
    });
  };

  return (
    <group position={position} scale={scale} onPointerMove={handlePointerMove}>
      {/* Carti silhouette body - simplified shape */}
      <mesh 
        ref={mesh} 
        onPointerOver={() => {
          setHover(true);
          setShowYVLSign(true);
        }}
        onPointerOut={() => {
          setHover(false);
          setTimeout(() => setShowYVLSign(false), 1500);
        }}
      >
        {/* Head */}
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial 
          color={hovered ? '#ff0000' : '#8826ca'} 
          emissive={hovered ? '#ff0000' : '#8826ca'}
          emissiveIntensity={hovered ? 0.8 : 0.3}
          metalness={0.7}
          roughness={0.2}
        />
        
        {/* Body */}
        <mesh position={[0, -1, 0]}>
          <cylinderGeometry args={[0.4, 0.3, 1.2, 32]} />
          <meshStandardMaterial 
            color="#000000" 
            emissive="#8826ca"
            emissiveIntensity={0.1}
            metalness={0.7}
            roughness={0.3}
          />
        </mesh>
      </mesh>
      
      {/* YVL sign that appears when hovered */}
      {showYVLSign && (
        <Text
          position={[0, 0.8, 0.5]}
          fontSize={0.3}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.02}
          outlineColor="#8826ca"
        >
          YVL !
        </Text>
      )}
      
      {/* Light/aura effect around figure */}
      <pointLight position={[0, 0, 2]} intensity={3} color="#8826ca" />
      <pointLight position={[0, 0, -1]} intensity={1} color="#8826ca" />
    </group>
  );
};

const CartiFigure = () => {
  return (
    <div className="h-[300px] sm:h-[400px] w-full rounded-lg overflow-hidden">
      <Canvas className="bg-transparent">
        <PerspectiveCamera makeDefault position={[0, 0, 5]} />
        <ambientLight intensity={0.2} />
        <CartiSilhouette position={[0, -0.5, 0]} scale={1.2} />
        <OrbitControls 
          enablePan={false} 
          enableZoom={false} 
          enableRotate={false} 
        />
      </Canvas>
    </div>
  );
};

export default CartiFigure;
