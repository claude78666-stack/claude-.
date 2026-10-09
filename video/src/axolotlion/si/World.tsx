import React, {useMemo} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {interpolate, random} from 'remotion';

/* ---------------------------------------------------------------------------------------------
   A deterministic underwater world for the Axolotlion film. Every value is a pure function of
   time `t` (seconds) so Remotion can render any frame in isolation.
--------------------------------------------------------------------------------------------- */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const FOG = '#06212c';
const ss = (x: number) => x * x * (3 - 2 * x);
/** keyframed value with smoothstep easing between keys */
export const key = (t: number, ts: number[], vs: number[]) => {
  if (t <= ts[0]) return vs[0];
  for (let i = 1; i < ts.length; i++) if (t <= ts[i]) return vs[i - 1] + (vs[i] - vs[i - 1]) * ss((t - ts[i - 1]) / (ts[i] - ts[i - 1]));
  return vs[vs.length - 1];
};

/* ---------- camera rig: one shot per scene, hard cuts between shots ---------- */
type V3 = [number, number, number];
type CamShot = {a: number; b: number; from: V3; to: V3; lookFrom: V3; lookTo: V3; fov: number};
export const SHOTS: CamShot[] = [
  {a: 0, b: 8.2, from: [0, 16, 13], to: [0, 5.2, 11], lookFrom: [0, 10, 0], lookTo: [0, 2.2, 0], fov: 42},
  {a: 8.2, b: 17.25, from: [0, 2.0, 15.5], to: [0, 1.9, 9.6], lookFrom: [0, 1.7, 0], lookTo: [0, 1.6, 0], fov: 36},
  {a: 17.25, b: 28.6, from: [-1.6, 1.7, 7.6], to: [3.4, 2.1, 6.9], lookFrom: [0, 1.55, 0], lookTo: [0, 1.6, 0], fov: 34},
  {a: 28.6, b: 32.4, from: [0.15, 2.35, 4.6], to: [0.1, 2.3, 3.9], lookFrom: [0.15, 2.25, 0], lookTo: [0.15, 2.25, 0], fov: 30},
  {a: 32.4, b: 35.6, from: [-2.6, 0.35, 5.6], to: [-1.8, 0.4, 5.0], lookFrom: [0, 2.2, 0], lookTo: [0, 2.3, 0], fov: 38},
  {a: 35.6, b: 39.3, from: [4.0, 5.2, 7.5], to: [5.6, 5.7, 4.6], lookFrom: [5.2, 5.6, -2.5], lookTo: [5.6, 5.9, -3.2], fov: 40},
  {a: 39.3, b: 45.1, from: [0, 2.6, 13.5], to: [0, 3.4, 11.8], lookFrom: [0, 2.6, 0], lookTo: [0, 3.0, 0], fov: 40},
  {a: 45.1, b: 56.0, from: [0, 1.2, 10.5], to: [0, 6.0, 15.5], lookFrom: [0, 1.5, -2], lookTo: [0, 1.2, -3], fov: 42},
  {a: 56.0, b: 64.5, from: [0, 1.6, 9.0], to: [0, 1.7, 7.4], lookFrom: [0, 2.05, 0], lookTo: [0, 2.15, 0], fov: 37},
];
export const shotAt = (t: number) => SHOTS.find((s) => t >= s.a && t < s.b) ?? SHOTS[SHOTS.length - 1];

const lerp3 = (a: V3, b: V3, k: number): V3 => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];

const CameraRig: React.FC<{t: number}> = ({t}) => {
  const {camera, size} = useThree();
  const s = shotAt(t);
  const k = ss(Math.min(1, Math.max(0, (t - s.a) / (s.b - s.a))));
  const p = lerp3(s.from, s.to, k), l = lerp3(s.lookFrom, s.lookTo, k);
  // gentle handheld float
  const hx = Math.sin(t * 0.7) * 0.03 + Math.sin(t * 1.9) * 0.012, hy = Math.sin(t * 0.9 + 1) * 0.025;
  camera.position.set(p[0] + hx, p[1] + hy, p[2]);
  camera.lookAt(l[0], l[1], l[2]);
  const cam = camera as THREE.PerspectiveCamera;
  cam.fov = s.fov; cam.aspect = size.width / size.height; cam.near = 0.05; cam.far = 200;
  cam.updateProjectionMatrix();
  return null;
};

/* ---------- shaders ---------- */
const rayMat = () =>
  new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: {uOpacity: {value: 0.2}, uColor: {value: new THREE.Color('#5fe6ff')}},
    vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform float uOpacity; uniform vec3 uColor; varying vec2 vUv;
      void main(){ float edge = sin(vUv.x*3.14159); float fall = pow(vUv.y, 1.6);
        gl_FragColor = vec4(uColor, uOpacity*edge*edge*fall); }`,
  });

const glowTex = (() => {
  let tex: THREE.CanvasTexture | null = null;
  return () => {
    if (tex) return tex;
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d')!; const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,.45)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); tex = new THREE.CanvasTexture(c); return tex;
  };
})();

const jellyBellMat = (color: string) =>
  new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: {uColor: {value: new THREE.Color(color)}, uPulse: {value: 0}, uFade: {value: 1}},
    vertexShader: `varying vec3 vN; varying vec3 vV; varying float vY;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vN = normalize(normalMatrix*normal); vV = normalize(-mv.xyz); vY = position.y; gl_Position = projectionMatrix*mv; }`,
    fragmentShader: `uniform vec3 uColor; uniform float uPulse; uniform float uFade; varying vec3 vN; varying vec3 vV; varying float vY;
      void main(){ float f = pow(1.0-abs(dot(vN,vV)), 2.2); float core = 0.06 + 0.12*uPulse;
        float rim = smoothstep(0.0, 0.08, vY+0.02);
        vec3 col = mix(vec3(1.0), uColor, 0.55);
        gl_FragColor = vec4(col*(f*1.3+core)*rim, (f*0.7+core*0.5)*uFade); }`,
  });

/* ---------- jellyfish: pulsing bell, inner glow, trailing tentacles ---------- */
const Jelly: React.FC<{t: number; seed: number; base: V3; size: number; color: string; drift?: number}> = ({t, seed, base, size, color, drift = 1}) => {
  const bell = useMemo(() => new THREE.SphereGeometry(1, 40, 20, 0, Math.PI * 2, 0, Math.PI * 0.55), []);
  const mat = useMemo(() => jellyBellMat(color), [color]);
  const ph = t * 1.3 + seed * 2.1;
  const pulse = 0.5 + 0.5 * Math.sin(ph);
  mat.uniforms.uPulse.value = pulse;
  const strands = 10;
  const lines = useMemo(() => {
    const arr: THREE.Line[] = [];
    for (let i = 0; i < strands; i++) {
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(24 * 3), 3));
      const m = new THREE.LineBasicMaterial({color, transparent: true, opacity: 0.32, blending: THREE.AdditiveBlending, depthWrite: false});
      arr.push(new THREE.Line(g, m));
    }
    return arr;
  }, [color]);
  lines.forEach((ln, i) => {
    const pos = ln.geometry.getAttribute('position') as THREE.BufferAttribute;
    const ang = (i / strands) * Math.PI * 2, r = 0.75;
    const len = 2.6 + (i % 3) * 0.8;
    for (let k = 0; k < 24; k++) {
      const u = k / 23;
      const sway = Math.sin(ph * 0.8 - u * 4 + i) * 0.25 * u;
      pos.setXYZ(k, Math.cos(ang) * r * (1 - u * 0.4) + sway, -u * len, Math.sin(ang) * r * (1 - u * 0.4) + Math.cos(ph * 0.7 - u * 3 + i) * 0.2 * u);
    }
    pos.needsUpdate = true;
  });
  const y = base[1] + Math.sin(t * 0.35 * drift + seed) * 0.6 + (t * 0.06 * drift);
  const x = base[0] + Math.sin(t * 0.21 + seed * 3) * 0.5;
  const sq = 1 + (pulse - 0.5) * 0.18;
  return (
    <group position={[x, y, base[2]]} scale={size} rotation={[Math.sin(t * 0.3 + seed) * 0.15, seed, Math.sin(t * 0.4 + seed) * 0.12]}>
      <mesh geometry={bell} material={mat} scale={[sq, 1 / sq, sq]} />
      <sprite scale={[2.6, 2.6, 1]} position={[0, 0.25, 0]}>
        <spriteMaterial map={glowTex()} color={color} transparent opacity={0.18 + pulse * 0.16} blending={THREE.AdditiveBlending} depthWrite={false} />
      </sprite>
      {lines.map((l, i) => <primitive key={i} object={l} />)}
    </group>
  );
};

/* ---------- marine snow ---------- */
const Snow: React.FC<{t: number}> = ({t}) => {
  const count = 2600;
  const {geo, base} = useMemo(() => {
    const b = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      b[i * 3] = (random(`sx${i}`) - 0.5) * 40; b[i * 3 + 1] = random(`sy${i}`) * 22 - 2; b[i * 3 + 2] = (random(`sz${i}`) - 0.5) * 40;
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(b.slice(), 3));
    return {geo: g, base: b};
  }, []);
  const pos = geo.getAttribute('position') as THREE.BufferAttribute;
  for (let i = 0; i < count; i++) {
    const y = base[i * 3 + 1] - t * (0.08 + random(`sv${i}`) * 0.12);
    pos.setXYZ(i, base[i * 3] + Math.sin(t * 0.3 + i) * 0.2, ((y + 2) % 22 + 22) % 22 - 2, base[i * 3 + 2]);
  }
  pos.needsUpdate = true;
  return (
    <points geometry={geo}>
      <pointsMaterial size={0.06} map={glowTex()} alphaTest={0.01} color="#bfefff" transparent opacity={0.55} sizeAttenuation depthWrite={false} blending={THREE.AdditiveBlending} />
    </points>
  );
};

/* ---------- god rays ---------- */
const Rays: React.FC<{t: number; strength: number}> = ({t, strength}) => {
  const mats = useMemo(() => Array.from({length: 7}, () => rayMat()), []);
  const geo = useMemo(() => new THREE.CylinderGeometry(0.6, 3.2, 26, 24, 1, true), []);
  return (
    <group>
      {mats.map((m, i) => {
        m.uniforms.uOpacity.value = strength * (0.22 + 0.1 * Math.sin(t * 0.5 + i * 1.7));
        const x = -9 + i * 3 + Math.sin(i * 7.1) * 1.5;
        return <mesh key={i} geometry={geo} material={m} position={[x, 11, -4 - (i % 3) * 3]} rotation={[0.08 * Math.sin(t * 0.2 + i), 0, 0.22 + Math.sin(t * 0.15 + i) * 0.05 - i * 0.04]} />;
      })}
    </group>
  );
};

/* ---------- seabed with animated caustics ---------- */
const Floor: React.FC<{t: number; fogD: number}> = ({t, fogD}) => {
  const mat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        uniforms: {uT: {value: 0}, fogColor: {value: new THREE.Color(FOG)}, uFogD: {value: 0.05}},
        vertexShader: `varying vec2 vP; varying float vDepth; void main(){ vP = position.xy; vec4 mv = modelViewMatrix*vec4(position,1.); vDepth = -mv.z; gl_Position = projectionMatrix*mv; }`,
        fragmentShader: `uniform float uT; uniform vec3 fogColor; uniform float uFogD; varying vec2 vP; varying float vDepth;
          float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
          void main(){
            vec2 p = vP*0.55;
            float a = sin(p.x*1.3 + uT*0.55 + sin(p.y*1.7 + uT*0.35)*1.4);
            float b = sin(p.y*1.2 - uT*0.45 + sin(p.x*1.9 - uT*0.3)*1.4);
            float k = pow(1.0 - abs(a*b), 14.0);
            float grain = h(floor(vP*40.0))*0.04;
            vec3 sand = vec3(0.045,0.085,0.10) + grain + vec3(0.25,0.75,0.85)*k*0.22;
            float r = length(vP - vec2(0.0, 0.0));
            sand += vec3(0.55,0.25,0.7)*0.10*exp(-r*r*0.12);
            float f = 1.0 - exp(-pow(uFogD*vDepth,2.0));
            gl_FragColor = vec4(mix(sand, fogColor, f), 1.0); }`,
      }),
    [],
  );
  mat.uniforms.uT.value = t; mat.uniforms.uFogD.value = fogD;
  return <mesh rotation={[-Math.PI / 2, 0, 0]} material={mat}><planeGeometry args={[160, 160, 1, 1]} /></mesh>;
};

/* ---------- sky dome: light from the surface far above ---------- */
const Dome: React.FC<{t: number}> = ({t}) => {
  const mat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        side: THREE.BackSide, depthWrite: false, fog: false,
        uniforms: {uT: {value: 0}},
        vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
        fragmentShader: `uniform float uT; varying vec3 vD;
          void main(){ float y = vD.y;
            vec3 deep = vec3(0.012,0.05,0.07); vec3 mid = vec3(0.024,0.125,0.17); vec3 top = vec3(0.16,0.55,0.62);
            vec3 c = mix(deep, mid, smoothstep(-0.2, 0.25, y)); c = mix(c, top, smoothstep(0.35, 1.0, y));
            float sun = pow(max(0.0, dot(vD, normalize(vec3(0.15,1.0,-0.25)))), 24.0);
            float shimmer = 0.5 + 0.5*sin(vD.x*40.0 + uT*0.8)*sin(vD.z*37.0 - uT*0.6);
            c += vec3(0.45,0.85,0.9)*sun*(0.7 + 0.3*shimmer);
            gl_FragColor = vec4(c, 1.0); }`,
      }),
    [],
  );
  mat.uniforms.uT.value = t;
  return <mesh material={mat}><sphereGeometry args={[95, 48, 24]} /></mesh>;
};

/* ---------- rocks and kelp for depth ---------- */
const Rocks: React.FC = () => {
  const rocks = useMemo(
    () => Array.from({length: 22}, (_, i) => {
      const side = i % 2 ? 1 : -1;
      return {pos: [side * (4.5 + random(`rx${i}`) * 18), 0, -5 - random(`rz${i}`) * 22] as V3, s: [0.8 + random(`rs${i}`) * 2.8, 0.6 + random(`rh${i}`) * 3.5, 0.8 + random(`rd${i}`) * 2.5] as V3, rot: random(`rt${i}`) * 6};
    }),
    [],
  );
  const geo = useMemo(() => new THREE.DodecahedronGeometry(1, 1), []);
  return <>{rocks.map((r, i) => (
    <mesh key={i} geometry={geo} position={r.pos} scale={r.s} rotation={[0.3, r.rot, 0.2]}>
      <meshLambertMaterial color="#0f2a33" />
    </mesh>
  ))}</>;
};

const Kelp: React.FC<{t: number}> = ({t}) => {
  const blades = useMemo(
    () => Array.from({length: 46}, (_, i) => {
      const side = i % 2 ? 1 : -1;
      return {x: side * (3.5 + random(`kx${i}`) * 14), z: -3 - random(`kz${i}`) * 16, h: 3 + random(`kh${i}`) * 7, w: 0.25 + random(`kw${i}`) * 0.35, ph: random(`kp${i}`) * 6, tip: random(`kt${i}`)};
    }),
    [],
  );
  const mat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        side: THREE.DoubleSide, transparent: true, fog: true,
        uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {uT: {value: 0}}]),
        vertexShader: `uniform float uT; attribute float aPh; varying float vV; #include <fog_pars_vertex>
          void main(){ vec3 p = position; vV = uv.y; float sway = sin(uT*0.9 + aPh + p.y*0.5)*0.35*uv.y*uv.y; p.x += sway; p.z += cos(uT*0.7 + aPh)*0.2*uv.y;
            vec4 mvPosition = modelViewMatrix*vec4(p,1.); gl_Position = projectionMatrix*mvPosition; #include <fog_vertex> }`,
        fragmentShader: `varying float vV; #include <fog_pars_fragment>
          void main(){ vec3 c = mix(vec3(0.02,0.09,0.07), vec3(0.08,0.32,0.26), vV); c += vec3(0.4,0.9,0.7)*smoothstep(0.85,1.0,vV)*0.35;
            gl_FragColor = vec4(c, 0.95); #include <fog_fragment> }`,
      }),
    [],
  );
  mat.uniforms.uT.value = t;
  const geos = useMemo(() => blades.map((b) => {
    const g = new THREE.PlaneGeometry(b.w, b.h, 1, 14); g.translate(0, b.h / 2, 0);
    g.setAttribute('aPh', new THREE.BufferAttribute(new Float32Array(g.attributes.position.count).fill(b.ph), 1)); return g;
  }), [blades]);
  return <>{blades.map((b, i) => <mesh key={i} geometry={geos[i]} material={mat} position={[b.x, 0, b.z]} rotation={[0, b.ph, 0]} />)}</>;
};

/* ---------- the character: turntable frames as a camera-facing card, with glow and contact shadow ---------- */
export type HeroTex = {frames: THREE.Texture[]};
const HERO_H = 3.1, HERO_W = (HERO_H * 1400) / 764;

const Hero: React.FC<{t: number; tex: HeroTex; reveal: number; glow: number; pos?: V3; scale?: number; angle?: number; tint?: number}> = ({t, tex, reveal, glow, pos = [0, 0, 0], scale = 1, angle = 0, tint = 1}) => {
  const {camera} = useThree();
  const a = Math.max(0, Math.min(180, angle));
  const f = a / 2.5, i0 = Math.min(72, Math.floor(f)), i1 = Math.min(72, i0 + 1), k = f - Math.floor(f);
  const breathe = 1 + Math.sin(t * 1.6) * 0.008;
  const c = new THREE.Color(0.93 * reveal * tint, 0.96 * reveal * tint, 1.0 * reveal * tint);
  const yaw = Math.atan2(camera.position.x - pos[0], camera.position.z - pos[2]);
  return (
    <group position={pos} scale={scale} rotation={[0, yaw, 0]}>
      <mesh position={[0, 0.02, 0.05]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[4.6, 2.2]} />
        <meshBasicMaterial alphaMap={glowTex()} color="#000" transparent opacity={0.7 * reveal} depthWrite={false} />
      </mesh>
      <sprite position={[0.2, 1.85, -0.3]} scale={[7 * (0.9 + glow * 0.3), 6 * (0.9 + glow * 0.3), 1]}>
        <spriteMaterial map={glowTex()} color="#b56bff" transparent opacity={0.22 * glow * reveal} blending={THREE.AdditiveBlending} depthWrite={false} />
      </sprite>
      <sprite position={[0.6, 2.0, -0.25]} scale={[4.2, 4.2, 1]}>
        <spriteMaterial map={glowTex()} color="#ffd27a" transparent opacity={0.16 * glow * reveal} blending={THREE.AdditiveBlending} depthWrite={false} />
      </sprite>
      <mesh position={[0, (HERO_H / 2) * breathe, 0]} scale={[1, breathe, 1]}>
        <planeGeometry args={[HERO_W, HERO_H]} />
        <meshBasicMaterial map={tex.frames[i0]} transparent alphaTest={0.02} color={c} depthWrite={false} toneMapped={false} />
      </mesh>
      {k > 0.02 && (
        <mesh position={[0, (HERO_H / 2) * breathe, 0.001]} scale={[1, breathe, 1]}>
          <planeGeometry args={[HERO_W, HERO_H]} />
          <meshBasicMaterial map={tex.frames[i1]} transparent opacity={k} color={c} depthWrite={false} toneMapped={false} />
        </mesh>
      )}
    </group>
  );
};

/* ---------- the whole world ---------- */
export const World: React.FC<{t: number; tex: HeroTex}> = ({t, tex}) => {
  const {scene} = useThree();
  const fogD = key(t, [0, 7, 9, 17, 18, 64], [0.06, 0.05, 0.06, 0.04, 0.035, 0.035]);
  const fogCol = new THREE.Color(FOG);
  scene.fog = new THREE.FogExp2(fogCol, fogD);
  scene.background = null;

  // character staging
  const reveal = key(t, [0, 8.2, 9.2, 14.5, 17.25], [0, 0, 0.12, 0.6, 1]);
  const glowBase = key(t, [0, 14.4, 15.4, 17.25, 64], [0.2, 0.3, 1.1, 0.8, 0.9]);
  const regrowPulse = Math.exp(-Math.pow((t - 8.6) / 0.6, 2)) + Math.exp(-Math.pow((t - 58.4) / 0.5, 2)) * 1.5;
  const s = shotAt(t);
  // turntable angle follows the orbit in the hero shot, otherwise faces camera at a slight 3/4
  let angle = 5;
  if (s.a === 17.25) angle = key(t, [17.25, 28.6], [0, 30]);
  else if (s.a === 32.4) angle = 20;
  else if (s.a === 45.1) angle = key(t, [45.1, 56], [10, 0]);

  const rayStrength = key(t, [0, 6, 11.9, 12.6, 17, 64], [1.3, 0.9, 0.8, 1.6, 1.1, 1.1]);
  const packIn = key(t, [45.1, 47.2], [0, 1]);

  const jellies = useMemo(
    () =>
      Array.from({length: 15}, (_, i) => ({
        base: [(random(`jx${i}`) - 0.5) * 26, 2.5 + random(`jy${i}`) * 9, -14 + random(`jz${i}`) * 12] as V3,
        size: 0.2 + random(`js${i}`) * 0.45,
        color: ['#7fe8ff', '#c08bff', '#ff8fd8', '#9fffe6'][i % 4],
      })),
    [],
  );
  // a dense cluster for the "light of the jellyfish" shot
  const cluster = useMemo(
    () => Array.from({length: 11}, (_, i) => ({base: [3.4 + random(`cx${i}`) * 4.4, 3.6 + random(`cy${i}`) * 2.6, -3.2 - random(`cz${i}`) * 3.5] as V3, size: 0.3 + random(`cs${i}`) * 0.4, color: ['#ff9be8', '#8fe9ff', '#c9a0ff'][i % 3]})),
    [],
  );
  const pack = useMemo(
    () => Array.from({length: 8}, (_, i) => {
      const side = i % 2 ? 1 : -1, row = Math.floor(i / 2);
      return {pos: [side * (2.6 + row * 1.7), 0, -2.5 - row * 2.6] as V3, scale: 0.42 - row * 0.04, angle: side > 0 ? 25 : 2.5, delay: i * 0.25};
    }),
    [],
  );

  return (
    <>
      <CameraRig t={t} />
      <Dome t={t} />
      <hemisphereLight args={['#6fd6e6', '#071820', 1.1]} />
      <directionalLight position={[3, 12, 4]} intensity={0.8} color="#9fe8ff" />
      <Floor t={t} fogD={fogD} />
      <Rocks />
      <Kelp t={t} />
      <Rays t={t} strength={rayStrength} />
      <Snow t={t} />
      {jellies.map((j, i) => <Jelly key={i} t={t} seed={i + 1} base={j.base} size={j.size} color={j.color} />)}
      {cluster.map((j, i) => <Jelly key={`c${i}`} t={t} seed={i + 40} base={j.base} size={j.size} color={j.color} drift={0.6} />)}
      <Hero t={t} tex={tex} reveal={reveal} glow={glowBase + regrowPulse} angle={angle} />
      {packIn > 0 && pack.map((p, i) => (
        <Hero key={i} t={t + i} tex={tex} reveal={Math.min(1, Math.max(0, packIn * 1.6 - p.delay)) * 0.85} glow={0.7} pos={p.pos} scale={p.scale} angle={p.angle} tint={0.9} />
      ))}
      {/* regrowth light pulse */}
      <sprite position={[0.3, 2.0, 0.4]} scale={[6 + regrowPulse * 6, 6 + regrowPulse * 6, 1]}>
        <spriteMaterial map={glowTex()} color="#ff9be8" transparent opacity={Math.min(0.9, regrowPulse * 0.55)} blending={THREE.AdditiveBlending} depthWrite={false} />
      </sprite>
    </>
  );
};
