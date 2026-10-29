import { AdditiveBlending, BufferAttribute, BufferGeometry, Color, InstancedBufferAttribute, InstancedMesh, Matrix4, PlaneGeometry, Points, Quaternion, ShaderMaterial, Vector3 } from "three";
import { seededRandom } from "../haunting/random";
import type { Slot } from "./facade";
import { FLICKER_GLSL } from "./flicker";

const GLOW_SIZE = 1.7;

const paneVertex = `
attribute float aState;
attribute float aSeed;
varying vec2 vUv;
varying float vState;
varying float vSeed;

void main() {
  vUv = uv;
  vState = aState;
  vSeed = aSeed;
  gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);
}
`;

const paneFragment = `
uniform vec3 uWarm;
uniform vec3 uFrame;
uniform vec3 uSpirit;
uniform float uTime;
varying vec2 vUv;
varying float vState;
varying float vSeed;
${FLICKER_GLSL}

void main() {
  float pane = step(0.08, vUv.x) * step(vUv.x, 0.92) * step(0.07, vUv.y) * step(vUv.y, 0.93);
  pane *= step(0.035, abs(vUv.x - 0.5)) * step(0.03, abs(vUv.y - 0.6));
  vec3 lamp = uWarm * (0.7 + 0.5 * (1.0 - distance(vUv, vec2(0.5, 0.3))));
  vec3 glass = uFrame * 0.55 + uSpirit * 0.05 * smoothstep(0.06, 0.0, abs(vUv.x - vUv.y * 0.7 - 0.1));
  vec3 inside = vState < 0.5 ? lamp : vState < 1.5 ? glass : lamp * (0.22 + 0.62 * flicker(uTime, vSeed));
  gl_FragColor = vec4(mix(uFrame * 0.45, inside, pane), 1.0);
  #include <colorspace_fragment>
}
`;

const glowVertex = `
uniform float uScale;
uniform float uTime;
attribute float aState;
attribute float aSeed;
varying float vStrength;
${FLICKER_GLSL}

void main() {
  vec4 view = modelViewMatrix * vec4(position, 1.0);
  gl_Position = projectionMatrix * view;
  gl_PointSize = ${GLOW_SIZE.toFixed(2)} * uScale / -view.z;
  vStrength = aState < 0.5 ? 0.3 : aState < 1.5 ? 0.0 : 0.3 * flicker(uTime, aSeed);
}
`;

const glowFragment = `
uniform vec3 uWarm;
varying float vStrength;

void main() {
  float glow = pow(smoothstep(0.5, 0.0, length(gl_PointCoord - 0.5)), 2.2);
  gl_FragColor = vec4(uWarm, glow * vStrength);
  #include <colorspace_fragment>
}
`;

export function houseWindows(slots: Slot[], states: number[], colors: { warm: string; frame: Color; spirit: string }) {
  const random = seededRandom(slots.length * 3 + states.reduce((sum, state) => sum + state, 0));
  const seeds = new Float32Array(slots.map(() => random()));
  const stateArray = new Float32Array(states);
  const plane = new PlaneGeometry(1, 1);
  plane.setAttribute("aState", new InstancedBufferAttribute(stateArray, 1));
  plane.setAttribute("aSeed", new InstancedBufferAttribute(seeds, 1));
  const paneMaterial = new ShaderMaterial({
    vertexShader: paneVertex,
    fragmentShader: paneFragment,
    uniforms: { uTime: { value: 0 }, uWarm: { value: new Color(colors.warm) }, uFrame: { value: colors.frame }, uSpirit: { value: new Color(colors.spirit) } },
  });
  const panes = new InstancedMesh(plane, paneMaterial, slots.length);
  const matrix = new Matrix4();
  slots.forEach((slot, index) => {
    matrix.compose(new Vector3(slot.x, slot.y, slot.z), new Quaternion(), new Vector3(slot.width, slot.height, 1));
    panes.setMatrixAt(index, matrix);
  });

  const glowGeometry = new BufferGeometry();
  glowGeometry.setAttribute("position", new BufferAttribute(new Float32Array(slots.flatMap((slot) => [slot.x, slot.y, slot.z + 0.15])), 3));
  glowGeometry.setAttribute("aState", new BufferAttribute(stateArray, 1));
  glowGeometry.setAttribute("aSeed", new BufferAttribute(seeds, 1));
  const glowMaterial = new ShaderMaterial({
    vertexShader: glowVertex,
    fragmentShader: glowFragment,
    uniforms: { uTime: { value: 0 }, uScale: { value: 1 }, uWarm: { value: new Color(colors.warm) } },
    transparent: true,
    depthWrite: false,
    blending: AdditiveBlending,
  });
  const glow = new Points(glowGeometry, glowMaterial);

  return {
    objects: [panes, glow],
    update: (time: number) => {
      paneMaterial.uniforms.uTime.value = time;
      glowMaterial.uniforms.uTime.value = time;
    },
    scale: (pixelsPerUnit: number) => {
      glowMaterial.uniforms.uScale.value = pixelsPerUnit;
    },
    dispose: () => [plane, paneMaterial, glowGeometry, glowMaterial].forEach((item) => item.dispose()),
  };
}
