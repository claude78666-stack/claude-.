import React, { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';
import { ThreeCanvas } from '@remotion/three';
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import tl from '../../public/robot/timeline.json';
import { theme } from '../theme';
import { Robot, type RobotPose } from './Robot';

export const ROBOT_FPS = 30;
const BEAT_START = tl.beats.map((_, i) => tl.beats.slice(0, i).reduce((a, b) => a + b, 0));
export const ROBOT_FRAMES = tl.beats.reduce((a, b) => a + b, 0) * ROBOT_FPS;
const OUT_Z = 2.2; // where Bolt stands once he steps into the rain

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = (x: number) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));
const beatAt = (t: number) => {
  let b = 0;
  BEAT_START.forEach((s, i) => (t >= s ? (b = i) : null));
  return b;
};
const rand = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};


// Procedural textures so surfaces aren't flat: bricks for the wall, grit for the road.
const makeTexture = (draw: (g: CanvasRenderingContext2D, w: number, h: number) => void, w = 512, h = 512, repeat: [number, number] = [1, 1]) => {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  draw(c.getContext('2d')!, w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(...repeat);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
};
const brickDraw = (g: CanvasRenderingContext2D, w: number, h: number) => {
  g.fillStyle = '#2a2420';
  g.fillRect(0, 0, w, h);
  const bh = 32, bw = 96;
  for (let row = 0; row < h / bh; row++) {
    for (let col = -1; col < w / bw + 1; col++) {
      const x = col * bw + (row % 2) * (bw / 2);
      const v = 0.75 + rand(row * 31 + col) * 0.35;
      g.fillStyle = `rgb(${Math.round(110 * v)},${Math.round(62 * v)},${Math.round(48 * v)})`;
      g.fillRect(x + 3, row * bh + 3, bw - 6, bh - 6);
    }
  }
  for (let i = 0; i < 4000; i++) {
    g.fillStyle = `rgba(0,0,0,${rand(i) * 0.18})`;
    g.fillRect(rand(i + 1) * w, rand(i + 2) * h, 2, 2);
  }
};
const gritDraw = (g: CanvasRenderingContext2D, w: number, h: number) => {
  g.fillStyle = '#1a1e21';
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < 26000; i++) {
    const v = Math.round(18 + rand(i) * 40);
    g.fillStyle = `rgba(${v},${v + 3},${v + 6},0.55)`;
    g.fillRect(rand(i + 7) * w, rand(i + 11) * h, 1 + rand(i + 3) * 2, 1 + rand(i + 5) * 2);
  }
};

// ---- environment: a night-street equirect so metal and puddles reflect lamps ----
const NightEnvironment: React.FC = () => {
  const { gl, scene } = useThree();
  useEffect(() => {
    const c = document.createElement('canvas');
    c.width = 1024;
    c.height = 512;
    const g = c.getContext('2d')!;
    const sky = g.createLinearGradient(0, 0, 0, 512);
    sky.addColorStop(0, '#0a1622');
    sky.addColorStop(0.5, '#1d3442');
    sky.addColorStop(0.55, '#2a2620');
    sky.addColorStop(1, '#07090b');
    g.fillStyle = sky;
    g.fillRect(0, 0, 1024, 512);
    for (let i = 0; i < 40; i++) {
      const x = rand(i) * 1024;
      const y = 200 + rand(i + 99) * 70;
      const r = 6 + rand(i + 7) * 22;
      const glow = g.createRadialGradient(x, y, 0, x, y, r);
      glow.addColorStop(0, i % 3 ? 'rgba(255,190,120,0.95)' : 'rgba(150,220,255,0.9)');
      glow.addColorStop(1, 'rgba(0,0,0,0)');
      g.fillStyle = glow;
      g.fillRect(x - r, y - r, r * 2, r * 2);
    }
    const tex = new THREE.CanvasTexture(c);
    tex.mapping = THREE.EquirectangularReflectionMapping;
    tex.colorSpace = THREE.SRGBColorSpace;
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromEquirectangular(tex).texture;
    scene.environment = env;
    scene.background = new THREE.Color('#0b1720');
    scene.fog = new THREE.Fog('#1a2c36', 5, 22);
    tex.dispose();
    pmrem.dispose();
    return () => {
      env.dispose();
    };
  }, [gl, scene]);
  return null;
};

// ---- street set ----
const Street: React.FC = () => {
  const bricks = useMemo(() => makeTexture(brickDraw, 512, 512, [8, 4]), []);
  const grit = useMemo(() => makeTexture(gritDraw, 512, 512, [14, 10]), []);
  const windows = useMemo(
    () =>
      Array.from({ length: 70 }).map((_, i) => ({
        x: -9 + (i % 14) * 1.35 + rand(i) * 0.3,
        y: 3.2 + Math.floor(i / 14) * 1.5,
        z: -1.48,
        lit: rand(i + 50) > 0.45,
        warm: rand(i + 80) > 0.3,
      })),
    [],
  );
  const puddles = useMemo(
    () =>
      [
        [0.4, OUT_Z + 0.1, 0.75],
        [-1.6, 3.6, 0.9],
        [2.4, 4.4, 1.1],
        [-0.4, 5.8, 0.7],
        [1.3, 1.6, 0.45],
      ] as const,
    [],
  );
  return (
    <group>
      {/* wet asphalt + sidewalk under the awning */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 6]} receiveShadow>
        <planeGeometry args={[40, 30]} />
        <meshPhysicalMaterial map={grit} color="#9aa3a8" roughness={0.3} metalness={0.15} clearcoat={0.7} clearcoatRoughness={0.15} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.005, -0.3]} receiveShadow>
        <planeGeometry args={[40, 2.4]} />
        <meshPhysicalMaterial color="#2a2e31" roughness={0.6} metalness={0.05} />
      </mesh>
      {puddles.map(([x, z, r], i) => (
        <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[x, 0.01, z]} scale={[1, 0.7, 1]}>
          <circleGeometry args={[r, 48]} />
          <meshPhysicalMaterial color="#05080a" roughness={0.02} metalness={0.9} clearcoat={1} />
        </mesh>
      ))}
      {/* building facade, door, awning */}
      <mesh position={[0, 5, -1.6]} receiveShadow>
        <boxGeometry args={[24, 10, 0.2]} />
        <meshStandardMaterial map={bricks} roughness={0.8} />
      </mesh>
      {/* door: dark frame, wooden panel, warm light through a glass window */}
      <mesh position={[0, 1.2, -1.47]}>
        <boxGeometry args={[1.45, 2.45, 0.08]} />
        <meshStandardMaterial color="#141210" roughness={0.6} />
      </mesh>
      <mesh position={[0, 1.15, -1.42]}>
        <boxGeometry args={[1.2, 2.25, 0.05]} />
        <meshPhysicalMaterial color="#4a2a1a" roughness={0.45} clearcoat={0.5} />
      </mesh>
      <mesh position={[0, 1.65, -1.39]}>
        <planeGeometry args={[0.8, 0.9]} />
        <meshStandardMaterial color="#ffcf8a" emissive="#ffa050" emissiveIntensity={1.3} />
      </mesh>
      <mesh position={[0.45, 1.1, -1.38]}>
        <sphereGeometry args={[0.04, 16, 12]} />
        <meshStandardMaterial color="#c9a24a" metalness={1} roughness={0.25} />
      </mesh>
      <mesh position={[0, 2.62, -0.35]} rotation={[0.16, 0, 0]} castShadow>
        <boxGeometry args={[3.6, 0.06, 2.4]} />
        <meshStandardMaterial color="#8c2f22" roughness={0.6} />
      </mesh>
      {windows.map((w, i) => (
        <mesh key={i} position={[w.x, w.y, w.z]}>
          <planeGeometry args={[0.7, 0.9]} />
          <meshStandardMaterial
            color={w.lit ? (w.warm ? '#ffcf8a' : '#bfe6ff') : '#15181b'}
            emissive={w.lit ? (w.warm ? '#ffa04a' : '#7fc8ff') : '#000'}
            emissiveIntensity={w.lit ? 1.2 : 0}
          />
        </mesh>
      ))}
      {/* street lamps */}
      {[-3.2, 3.4].map((x) => (
        <group key={x} position={[x, 0, 1.2]}>
          <mesh position={[0, 1.8, 0]} castShadow>
            <cylinderGeometry args={[0.05, 0.07, 3.6, 16]} />
            <meshStandardMaterial color="#1c1f22" metalness={0.6} roughness={0.4} />
          </mesh>
          <mesh position={[0, 3.65, 0]}>
            <sphereGeometry args={[0.16, 24, 16]} />
            <meshStandardMaterial color="#fff1d6" emissive="#ffb36b" emissiveIntensity={4} toneMapped={false} />
          </mesh>
          <pointLight position={[0, 3.5, 0]} color="#ffb36b" intensity={26} distance={12} decay={2} />
          {/* soft glow halo around the bulb (fake bloom) */}
          {[0.5, 0.9, 1.5].map((r, k) => (
            <mesh key={r} position={[0, 3.65, 0]}>
              <sphereGeometry args={[r, 24, 16]} />
              <meshBasicMaterial color="#ffb36b" transparent opacity={0.09 - k * 0.025} blending={THREE.AdditiveBlending} depthWrite={false} />
            </mesh>
          ))}
        </group>
      ))}
      {/* distant buildings in the fog */}
      {Array.from({ length: 9 }).map((_, i) => (
        <mesh key={i} position={[-14 + i * 3.5, 4 + rand(i) * 3, 16 + rand(i + 3) * 4]}>
          <boxGeometry args={[3, 8 + rand(i + 9) * 6, 3]} />
          <meshStandardMaterial color="#1a2a33" roughness={0.9} />
        </mesh>
      ))}
    </group>
  );
};

// ---- rain streaks + ground splash rings, both instanced and frame-deterministic ----
const DROPS = 3200;
const RINGS = 180;
const Rain: React.FC<{ t: number; intensity: number }> = ({ t, intensity }) => {
  const drops = useRef<THREE.InstancedMesh>(null);
  const rings = useRef<THREE.InstancedMesh>(null);
  const tmp = useMemo(() => new THREE.Object3D(), []);
  useLayoutEffect(() => {
    const d = drops.current;
    const r = rings.current;
    if (!d || !r) return;
    const active = Math.floor(DROPS * intensity);
    for (let i = 0; i < DROPS; i++) {
      const x = -4.5 + rand(i) * 9;
      const z = 0.95 + rand(i + 1000) * 7; // only outside the awning
      const speed = 7 + rand(i + 2000) * 3;
      const h = 9;
      const y = h - ((rand(i + 3000) * h + t * speed) % h);
      tmp.position.set(x + y * 0.04, y, z);
      tmp.rotation.set(0, 0, 0.04);
      tmp.scale.setScalar(i < active ? 1 : 0);
      tmp.updateMatrix();
      d.setMatrixAt(i, tmp.matrix);
    }
    d.instanceMatrix.needsUpdate = true;
    const activeRings = Math.floor(RINGS * intensity);
    for (let i = 0; i < RINGS; i++) {
      const period = 0.55 + rand(i + 4000) * 0.5;
      const phase = ((t + rand(i + 5000) * period) % period) / period;
      const cycle = Math.floor((t + rand(i + 5000) * period) / period);
      const x = -5 + rand(i * 31 + cycle) * 10;
      const z = 1.0 + rand(i * 17 + cycle + 9) * 8;
      tmp.position.set(x, 0.015, z);
      tmp.rotation.set(-Math.PI / 2, 0, 0);
      const s = i < activeRings ? 0.01 + phase * 0.11 : 0;
      tmp.scale.set(s, s, s);
      tmp.updateMatrix();
      r.setMatrixAt(i, tmp.matrix);
    }
    r.instanceMatrix.needsUpdate = true;
  }, [t, intensity, tmp]);
  return (
    <group>
      <instancedMesh ref={drops} args={[undefined, undefined, DROPS]} frustumCulled={false}>
        <boxGeometry args={[0.005, 0.4, 0.005]} />
        <meshBasicMaterial color="#eef8ff" transparent opacity={0.6} depthWrite={false} />
      </instancedMesh>
      <instancedMesh ref={rings} args={[undefined, undefined, RINGS]} frustumCulled={false}>
        <ringGeometry args={[0.93, 1, 40]} />
        <meshBasicMaterial color="#dff3ff" transparent opacity={0.16} depthWrite={false} side={THREE.DoubleSide} />
      </instancedMesh>
    </group>
  );
};

// A single "hero" drop falling to a target, with a little splash burst on impact.
const HeroDrop: React.FC<{ t: number; hitAt: number; target: [number, number, number] }> = ({ t, hitAt, target }) => {
  const fall = 0.55;
  const dt = t - hitAt;
  if (dt < -fall || dt > 0.45) return null;
  if (dt < 0) {
    const y = target[1] + (-dt / fall) * 3;
    return (
      <mesh position={[target[0], y, target[2]]} scale={[1, 1.6, 1]}>
        <sphereGeometry args={[0.018, 12, 8]} />
        <meshPhysicalMaterial color="#e6f6ff" transmission={0.9} roughness={0} thickness={0.02} />
      </mesh>
    );
  }
  return (
    <group position={target}>
      {Array.from({ length: 8 }).map((_, i) => {
        const a = (i / 8) * Math.PI * 2;
        const v = 0.6 + rand(i + hitAt) * 0.4;
        const k = dt * v;
        return (
          <mesh key={i} position={[Math.cos(a) * k * 0.5, k * 0.9 - 4.9 * dt * dt, Math.sin(a) * k * 0.5]}>
            <sphereGeometry args={[0.009, 8, 6]} />
            <meshBasicMaterial color="#e6f6ff" transparent opacity={1 - dt / 0.45} />
          </mesh>
        );
      })}
    </group>
  );
};

// ---- choreography: robot pose + camera per beat ----
const poseAt = (t: number): { pose: RobotPose; z: number; jumpY: number; spin: number } => {
  const b = beatAt(t);
  const blinkCycle = (t % 3.4) / 3.4;
  const blink = blinkCycle > 0.95 ? Math.abs(blinkCycle - 0.975) / 0.025 : 1;
  const flinch = Math.exp(-Math.max(0, t - tl.headHit) * 8) * (t >= tl.headHit ? 1 : 0);
  const lookUp = ease((t - (tl.headHit + 0.25)) / 0.6) * (1 - ease((t - BEAT_START[2] - 0.2) / 0.8));
  const armRaise = ease((t - BEAT_START[2] - 0.3) / 0.8) * (1 - ease((t - BEAT_START[3]) / 0.6));
  const walk = ease((t - BEAT_START[3] - 0.6) / 2.2);
  const z = walk * OUT_Z;
  const walking = t > BEAT_START[3] + 0.6 && t < BEAT_START[3] + 2.8;
  const spin = b === 3 ? ease((t - BEAT_START[3] - 3.0) / 3.5) * Math.PI * 2 : 0;
  const jt = (t - tl.jumpStart) / (tl.land - tl.jumpStart);
  const jumpY = jt > 0 && jt < 1 ? Math.sin(jt * Math.PI) * 0.55 : 0;
  const crouch = Math.exp(-Math.pow((t - (tl.jumpStart - 0.08)) / 0.1, 2)) + Math.exp(-Math.pow((t - (tl.land + 0.06)) / 0.1, 2));
  const wetness = interpolate(t, [BEAT_START[3] + 1, BEAT_START[3] + 6], [0, 1], clamp);
  return {
    z,
    jumpY,
    spin,
    pose: {
      headPitch: lookUp * 0.55 + (b === 2 ? -0.35 * armRaise : 0) + (b >= 3 ? 0.25 : 0),
      headYaw: b === 2 ? 0.25 * armRaise : Math.sin(t * 0.7) * 0.06,
      armRaise,
      squash: 1 - flinch * 0.12 - crouch * 0.18,
      blink: t > tl.headHit && t < tl.headHit + 0.12 ? 0 : blink,
      happy: ease((t - BEAT_START[4] - 1.6) / 0.5),
      wetness,
      bob: walking ? Math.abs(Math.sin(t * 9)) * 0.04 : Math.sin(t * 2) * 0.008,
    },
  };
};

type Shot = { from: [number, number, number]; to: [number, number, number]; look: (z: number, y: number) => [number, number, number] };
const SHOTS: Shot[] = [
  { from: [3.8, 1.6, 7.5], to: [3.1, 1.45, 6.2], look: () => [0, 1.0, 0] },
  { from: [0.85, 1.55, 1.9], to: [0.7, 1.5, 1.65], look: () => [0, 1.3, 0] },
  { from: [1.5, 1.25, 1.75], to: [1.35, 1.2, 1.55], look: () => [0.35, 1.0, 0.35] },
  { from: [0, 0, 0], to: [0, 0, 0], look: (z) => [0, 0.9, z] }, // orbit, computed below
  { from: [1.3, 0.35, OUT_Z + 2.4], to: [0.6, 3.2, OUT_Z + 8.5], look: (z, y) => [0, 0.7 + y, z] },
];

const CameraRig: React.FC<{ t: number; z: number; jumpY: number }> = ({ t, z, jumpY }) => {
  const { camera } = useThree();
  useLayoutEffect(() => {
    const b = beatAt(t);
    const p = (t - BEAT_START[b]) / tl.beats[b];
    const shot = SHOTS[b];
    let pos: THREE.Vector3;
    if (b === 3) {
      const a = -0.9 + ease(p) * 2.0;
      const r = 3.4 - ease(p) * 0.6;
      pos = new THREE.Vector3(Math.sin(a) * r, 1.35, z + Math.cos(a) * r);
    } else {
      const e = b === 4 ? ease(Math.max(0, (p - 0.35) / 0.65)) : ease(p);
      pos = new THREE.Vector3().lerpVectors(new THREE.Vector3(...shot.from), new THREE.Vector3(...shot.to), e);
    }
    // a touch of handheld drift
    pos.x += Math.sin(t * 1.3) * 0.015;
    pos.y += Math.sin(t * 1.7 + 1) * 0.012;
    camera.position.copy(pos);
    camera.lookAt(...shot.look(z, jumpY));
    camera.updateProjectionMatrix();
  }, [t, z, jumpY, camera]);
  return null;
};

const World: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / ROBOT_FPS;
  const { pose, z, jumpY, spin } = poseAt(t);
  const intensity = interpolate(t, [0, 5, 6, 11, 17], [0.03, 0.08, 0.15, 1, 1], clamp);
  const sunken = 0;
  return (
    <>
      <NightEnvironment />
      <CameraRig t={t} z={z} jumpY={jumpY} />
      <ambientLight intensity={0.28} color="#9cc7e0" />
      {/* cool rim light from behind so Bolt separates from the dark street */}
      <spotLight position={[1.5, 3.2, z - 3]} target-position={[0, 1, z]} angle={0.6} penumbra={0.8} intensity={30} color="#9fd8ff" distance={9} />
      {/* warm key from the nearest street lamp */}
      <spotLight position={[3.2, 3.4, z + 2.5]} angle={0.5} penumbra={0.9} intensity={22} color="#ffc08a" distance={10} />
      <directionalLight
        position={[-4, 8, 6]}
        intensity={0.9}
        color="#a9c8ff"
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-left={-5}
        shadow-camera-right={5}
        shadow-camera-top={5}
        shadow-camera-bottom={-5}
        shadow-bias={-0.0004}
      />
      <Street />
      <group position={[0, jumpY - sunken, z]} rotation={[0, spin, 0]}>
        <Robot pose={pose} />
      </group>
      <Rain t={t} intensity={intensity} />
      <HeroDrop t={t} hitAt={tl.headHit} target={[0, 1.52, 0]} />
      {tl.handHits.map((h) => (
        <HeroDrop key={h} t={t} hitAt={h} target={[0.36, 0.95, 0.38]} />
      ))}
      {/* landing splash crown in the puddle */}
      {t > tl.land && t < tl.land + 0.7 && (
        <group position={[0, 0.02, z]}>
          {Array.from({ length: 22 }).map((_, i) => {
            const a = (i / 22) * Math.PI * 2;
            const dt = t - tl.land;
            const v = 1.2 + rand(i) * 0.8;
            return (
              <mesh key={i} position={[Math.cos(a) * dt * v * 0.8, dt * v * 1.6 - 4.9 * dt * dt * 1.4, Math.sin(a) * dt * v * 0.8]}>
                <sphereGeometry args={[0.02, 8, 6]} />
                <meshBasicMaterial color="#e6f6ff" transparent opacity={1 - dt / 0.7} />
              </mesh>
            );
          })}
        </group>
      )}
    </>
  );
};

const Grade: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6) 100%)' }} />
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(20,60,80,0.18), rgba(255,140,60,0.08))', mixBlendMode: 'soft-light' }} />
      <svg width="1080" height="1920" style={{ position: 'absolute', opacity: 0.07, mixBlendMode: 'overlay' }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={frame % 40} />
        </filter>
        <rect width="1080" height="1920" filter="url(#grain)" />
      </svg>
    </>
  );
};

const Caption: React.FC<{ text: string; spokenFrames: number }> = ({ text, spokenFrames }) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const n = Math.min(words.length, Math.floor((frame / Math.max(spokenFrames, 1)) * words.length) + 1);
  const start = Math.floor((n - 1) / 5) * 5;
  const opacity = interpolate(frame, [spokenFrames + 20, spokenFrames + 35], [1, 0], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 300,
        width: '100%',
        textAlign: 'center',
        fontFamily: theme.font,
        fontWeight: 800,
        fontSize: 54,
        color: '#fff',
        padding: '0 90px',
        textShadow: '0 3px 14px rgba(0,0,0,0.85)',
        opacity,
      }}
    >
      {words.slice(start, n).join(' ')}
    </div>
  );
};

const EndTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 20], [0, 1], clamp);
  return (
    <div style={{ position: 'absolute', top: 260, width: '100%', textAlign: 'center', fontFamily: theme.font, opacity: o }}>
      <div style={{ color: '#fff', fontSize: 150, fontWeight: 900, letterSpacing: 6, textShadow: '0 6px 30px rgba(0,0,0,0.7)' }}>BOLT</div>
      <div style={{ color: '#9ff3ff', fontSize: 40, fontWeight: 700, letterSpacing: 10, marginTop: 6 }}>FIRST RAIN</div>
    </div>
  );
};

export const RobotRain: React.FC = () => {
  const { width, height, fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 20], [1, 0], clamp);
  const fadeOut = interpolate(frame, [ROBOT_FRAMES - 30, ROBOT_FRAMES], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: '#05080a' }}>
      <ThreeCanvas
        width={width}
        height={height}
        shadows
        camera={{ fov: 40, near: 0.05, far: 80, position: [3.8, 1.6, 7.5] }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.55 }}
      >
        <World />
      </ThreeCanvas>
      <Grade />
      <Audio src={staticFile('robot/bed.mp3')} volume={0.9} />
      {tl.lines.map((line, i) => (
        <Sequence key={i} from={Math.round((BEAT_START[i] + tl.lineOffset) * fps)} durationInFrames={Math.round((tl.beats[i] - tl.lineOffset) * fps)}>
          <Audio src={staticFile(`robot/line${i + 1}.wav`)} />
          <Caption text={line} spokenFrames={Math.round(2.6 * fps * (line.split(' ').length / 8))} />
        </Sequence>
      ))}
      <Sequence from={Math.round((tl.land + 0.6) * fps)}>
        <EndTitle />
      </Sequence>
      <AbsoluteFill style={{ backgroundColor: '#000', opacity: Math.max(fadeIn, fadeOut) }} />
    </AbsoluteFill>
  );
};
