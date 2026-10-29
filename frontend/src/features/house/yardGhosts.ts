import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  Color,
  Points,
  ShaderMaterial,
  type Vector3,
} from "three";
import { ghostPoints } from "../haunting/ghostPoints";

const PER_GHOST = 1600;
export const GHOST_SCALE = 0.3;

const vertexShader = `
uniform float uTime;
uniform float uIntro;
uniform float uHover;
uniform float uPixelRatio;
uniform float uViewport;
uniform float uScale;
attribute vec3 aOrigin;
attribute float aSeed;
attribute float aGhost;
varying float vAlpha;
varying float vHover;

void main() {
  float hovered = 1.0 - step(0.5, abs(aGhost - uHover));
  float rise = smoothstep(0.0, 1.0, clamp(uIntro * 1.4 - aGhost * 0.06, 0.0, 1.0));
  float hem = smoothstep(-0.55, -1.3, position.y);
  vec3 local = position * uScale * (1.0 + hovered * 0.22);
  local.x += sin(position.y * 3.0 + uTime * 1.8 + aGhost) * 0.01 + sin(uTime * 2.4 + position.x * 4.0 + aSeed * 3.0) * 0.022 * hem;
  vec3 point = aOrigin + local;
  point.y += sin(uTime * 1.1 + aGhost * 1.9) * 0.07 - (1.0 - rise) * 0.8;
  vec4 view = modelViewMatrix * vec4(point, 1.0);
  gl_Position = projectionMatrix * view;
  gl_PointSize = (1.6 + aSeed * 1.8) * (1.0 + hovered * 0.3) * uPixelRatio * uViewport * (14.0 / -view.z);
  float front = mix(0.12, 1.0, smoothstep(-0.6, 0.85, position.z));
  vAlpha = front * rise * (0.75 + 0.25 * sin(uTime * 1.7 + aSeed * 21.0));
  vHover = hovered;
}
`;

const fragmentShader = `
uniform vec3 uColor;
varying float vAlpha;
varying float vHover;

void main() {
  float glow = pow(smoothstep(0.5, 0.0, length(gl_PointCoord - 0.5)), 1.5);
  gl_FragColor = vec4(mix(uColor, vec3(1.0), vHover * 0.25), glow * vAlpha * (0.42 + vHover * 0.3));
  #include <colorspace_fragment>
}
`;

export function yardGhosts(
  origins: Vector3[],
  color: string,
  pixelRatio: number,
) {
  const shape = ghostPoints(PER_GHOST);
  const total = origins.length * PER_GHOST;
  const positions = new Float32Array(total * 3);
  const anchors = new Float32Array(total * 3);
  const seeds = new Float32Array(total);
  const ghosts = new Float32Array(total);
  origins.forEach((origin, ghost) => {
    positions.set(shape.targets, ghost * PER_GHOST * 3);
    seeds.set(shape.seeds, ghost * PER_GHOST);
    for (let index = 0; index < PER_GHOST; index += 1) {
      anchors.set(
        [origin.x, origin.y, origin.z],
        (ghost * PER_GHOST + index) * 3,
      );
      ghosts[ghost * PER_GHOST + index] = ghost;
    }
  });
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(positions, 3));
  geometry.setAttribute("aOrigin", new BufferAttribute(anchors, 3));
  geometry.setAttribute("aSeed", new BufferAttribute(seeds, 1));
  geometry.setAttribute("aGhost", new BufferAttribute(ghosts, 1));
  const material = new ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uIntro: { value: 0 },
      uHover: { value: -1 },
      uPixelRatio: { value: pixelRatio },
      uViewport: { value: 1 },
      uScale: { value: GHOST_SCALE },
      uColor: { value: new Color(color) },
    },
    transparent: true,
    depthWrite: false,
    blending: AdditiveBlending,
  });
  const points = new Points(geometry, material);
  points.frustumCulled = false;
  return {
    points,
    uniforms: material.uniforms,
    dispose: () => (geometry.dispose(), material.dispose()),
  };
}
