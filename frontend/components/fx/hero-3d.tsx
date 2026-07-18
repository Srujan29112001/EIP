"use client";

/** The Observatory — the landing hero's living 3D scene.
 *
 * An abstract orchestra: three tilted particle rings (the movements) orbiting
 * a pulsing wireframe core (the Manager), inside a slow starfield. The whole
 * scene breathes and parallaxes toward the cursor. Pure three/R3F (already in
 * the stack), additive-blended, capped DPR — silky on laptops, fine on phones.
 */

import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

function ParticleRing({ radius, count, color, tilt, speed, size = 0.045 }: {
  radius: number; count: number; color: string; tilt: [number, number, number];
  speed: number; size?: number;
}) {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const a = (i / count) * Math.PI * 2;
      const r = radius + (Math.random() - 0.5) * 0.5;
      arr[i * 3] = Math.cos(a) * r;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 0.22;
      arr[i * 3 + 2] = Math.sin(a) * r;
    }
    return arr;
  }, [radius, count]);

  useFrame((_, dt) => {
    if (ref.current) ref.current.rotation.y += dt * speed;
  });

  return (
    <group rotation={tilt}>
      <points ref={ref}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        </bufferGeometry>
        <pointsMaterial size={size} color={color} transparent opacity={0.85}
          blending={THREE.AdditiveBlending} depthWrite={false} sizeAttenuation />
      </points>
    </group>
  );
}

function Starfield({ count = 900 }: { count?: number }) {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 9 + Math.random() * 14;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.6;
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, [count]);

  useFrame((_, dt) => {
    if (ref.current) ref.current.rotation.y += dt * 0.008;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.028} color="#8b94a8" transparent opacity={0.5}
        blending={THREE.AdditiveBlending} depthWrite={false} sizeAttenuation />
    </points>
  );
}

function Core() {
  const outer = useRef<THREE.Mesh>(null);
  const inner = useRef<THREE.Mesh>(null);
  useFrame(({ clock }, dt) => {
    const t = clock.elapsedTime;
    const pulse = 1 + Math.sin(t * 1.6) * 0.06;
    if (outer.current) {
      outer.current.rotation.x += dt * 0.18;
      outer.current.rotation.y += dt * 0.24;
      outer.current.scale.setScalar(pulse);
    }
    if (inner.current) {
      inner.current.rotation.y -= dt * 0.4;
      inner.current.scale.setScalar(0.55 * (2 - pulse));
    }
  });
  return (
    <group>
      <mesh ref={outer}>
        <icosahedronGeometry args={[1.05, 1]} />
        <meshBasicMaterial color="#67e8f9" wireframe transparent opacity={0.5} />
      </mesh>
      <mesh ref={inner}>
        <icosahedronGeometry args={[1, 0]} />
        <meshBasicMaterial color="#a78bfa" wireframe transparent opacity={0.75} />
      </mesh>
      <pointLight intensity={2} color="#67e8f9" />
    </group>
  );
}

function Scene() {
  const rig = useRef<THREE.Group>(null);
  const target = useRef({ x: 0, y: 0 });

  useFrame(({ pointer }, dt) => {
    // parallax toward the cursor + a slow breathing drift
    target.current.x = pointer.x * 0.28;
    target.current.y = pointer.y * 0.18;
    if (rig.current) {
      rig.current.rotation.y += (target.current.x - rig.current.rotation.y) * dt * 2.2;
      rig.current.rotation.x += (-target.current.y - rig.current.rotation.x) * dt * 2.2;
    }
  });

  return (
    <group ref={rig}>
      <Starfield />
      <Core />
      <ParticleRing radius={2.6} count={340} color="#22d3ee" tilt={[0.5, 0, 0.18]} speed={0.14} />
      <ParticleRing radius={3.7} count={420} color="#a78bfa" tilt={[0.32, 0, -0.3]} speed={-0.1} />
      <ParticleRing radius={4.9} count={480} color="#f0cb78" tilt={[0.68, 0, 0.08]} speed={0.055} size={0.038} />
    </group>
  );
}

export default function Hero3D() {
  return (
    <Canvas
      camera={{ position: [0, 1.1, 8.2], fov: 48 }}
      dpr={[1, 1.6]}
      // opaque ink-colored buffer: additive particles glow correctly (a transparent
      // buffer washes white — premultiplied-alpha can't represent additive color)
      gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
      onCreated={({ gl }) => gl.setClearColor("#070b18", 1)}
      style={{ position: "absolute", inset: 0 }}
      aria-hidden
    >
      <Scene />
    </Canvas>
  );
}
