import React, { useMemo } from 'react';
import * as THREE from 'three';

export type RobotPose = {
  headPitch: number; // radians, + looks up
  headYaw: number;
  armRaise: number; // 0..1 right arm reaching forward, palm up
  squash: number; // 1 = normal, <1 squashed
  blink: number; // 1 open, 0 closed
  happy: number; // 0..1 eyes curve into a smile
  wetness: number; // 0..1 makes the metal glossier
  bob: number; // walking/idle bob offset (metres)
};

const capsule = (r: number, len: number) => new THREE.CapsuleGeometry(r, len, 12, 24);

// A small, rounded robot built from primitives with physically based materials.
// About 1.25 m tall, feet at y=0.
export const Robot: React.FC<{ pose: RobotPose }> = ({ pose }) => {
  const geo = useMemo(
    () => ({
      body: capsule(0.27, 0.22),
      head: new THREE.SphereGeometry(0.3, 48, 32),
      limb: capsule(0.06, 0.26),
      foot: capsule(0.085, 0.12),
      joint: new THREE.SphereGeometry(0.075, 24, 16),
      eye: new THREE.SphereGeometry(0.055, 24, 16),
      antenna: new THREE.CylinderGeometry(0.012, 0.012, 0.18, 12),
      bulb: new THREE.SphereGeometry(0.035, 16, 12),
      panel: new THREE.CircleGeometry(0.11, 32),
    }),
    [],
  );
  const rough = THREE.MathUtils.lerp(0.32, 0.08, pose.wetness);
  const metal = (
    <meshPhysicalMaterial color="#cfd6dc" metalness={0.75} roughness={rough} clearcoat={1} clearcoatRoughness={rough * 0.6} />
  );
  const dark = <meshPhysicalMaterial color="#2b3137" metalness={0.5} roughness={0.35} clearcoat={0.6} />;
  const eyeMat = (
    <meshStandardMaterial color="#9ff3ff" emissive="#43e0ff" emissiveIntensity={2.6} toneMapped={false} />
  );
  const eyeScaleY = Math.max(0.08, pose.blink) * (1 - 0.55 * pose.happy);
  const arm = pose.armRaise;

  return (
    <group position={[0, pose.bob, 0]} scale={[1 + (1 - pose.squash) * 0.6, pose.squash, 1 + (1 - pose.squash) * 0.6]}>
      {/* legs + feet */}
      {[-0.13, 0.13].map((x) => (
        <group key={x} position={[x, 0, 0]}>
          <mesh geometry={geo.limb} position={[0, 0.25, 0]} castShadow>
            {dark}
          </mesh>
          <mesh geometry={geo.foot} position={[0, 0.07, 0.05]} rotation={[Math.PI / 2, 0, 0]} castShadow>
            {metal}
          </mesh>
        </group>
      ))}
      {/* body */}
      <mesh geometry={geo.body} position={[0, 0.68, 0]} castShadow>
        {metal}
      </mesh>
      <mesh geometry={geo.panel} position={[0, 0.7, 0.272]}>
        <meshPhysicalMaterial color="#e2603f" metalness={0.3} roughness={rough + 0.1} clearcoat={1} />
      </mesh>
      {/* left arm, relaxed */}
      <group position={[-0.32, 0.86, 0]} rotation={[0, 0, -0.18]}>
        <mesh geometry={geo.joint} castShadow>
          {dark}
        </mesh>
        <mesh geometry={geo.limb} position={[0, -0.2, 0]} castShadow>
          {metal}
        </mesh>
      </group>
      {/* right arm, raises forward palm-up */}
      <group position={[0.32, 0.86, 0]} rotation={[-arm * 1.35, 0, 0.18 - arm * 0.1]}>
        <mesh geometry={geo.joint} castShadow>
          {dark}
        </mesh>
        <mesh geometry={geo.limb} position={[0, -0.2, 0]} castShadow>
          {metal}
        </mesh>
        <mesh geometry={geo.joint} position={[0, -0.4, 0]} scale={[1.1, 0.7, 1.1]} castShadow>
          {dark}
        </mesh>
      </group>
      {/* neck + head */}
      <group position={[0, 1.0, 0]} rotation={[-pose.headPitch, pose.headYaw, 0]}>
        <mesh geometry={geo.head} position={[0, 0.2, 0]} scale={[1.12, 0.86, 1]} castShadow>
          {metal}
        </mesh>
        {/* glossy face screen */}
        <mesh position={[0, 0.2, 0.17]} scale={[0.27, 0.19, 0.14]}>
          <sphereGeometry args={[1, 48, 32]} />
          <meshPhysicalMaterial color="#0b0f13" metalness={0.2} roughness={0.05} clearcoat={1} clearcoatRoughness={0.02} />
        </mesh>
        {[-0.1, 0.1].map((x) => (
          <mesh key={x} geometry={geo.eye} position={[x, 0.22, 0.305]} scale={[1, eyeScaleY, 0.4]}>
            {eyeMat}
          </mesh>
        ))}
        <pointLight position={[0, 0.22, 0.4]} color="#43e0ff" intensity={0.6} distance={1.2} />
        <mesh geometry={geo.antenna} position={[0, 0.52, 0]}>
          {dark}
        </mesh>
        <mesh geometry={geo.bulb} position={[0, 0.62, 0]}>
          <meshStandardMaterial color="#ffb36b" emissive="#ff8a3d" emissiveIntensity={2} toneMapped={false} />
        </mesh>
      </group>
    </group>
  );
};
