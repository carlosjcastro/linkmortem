import {
  BufferAttribute,
  BufferGeometry,
  Color,
  NormalBlending,
  Points,
  ShaderMaterial,
} from "three";
import { seededRandom } from "./random";

const FIELD = { width: 14, height: 9, depth: 6 };

const vertexShader = `
uniform float uTime;
uniform float uPixelRatio;
uniform float uHeight;
attribute float aSeed;
varying float vSeed;

void main() {
  vec3 point = position;
  point.y = mod(position.y - uTime * (0.1 + aSeed * 0.14) + uHeight * 0.5, uHeight) - uHeight * 0.5;
  point.x += sin(uTime * 0.6 + aSeed * 12.0) * 0.4;
  vec4 view = modelViewMatrix * vec4(point, 1.0);
  gl_Position = projectionMatrix * view;
  gl_PointSize = (12.0 + aSeed * 14.0) * uPixelRatio * (5.0 / -view.z);
  vSeed = aSeed;
}
`;

const fragmentShader = `
uniform vec3 uColor;
uniform float uTime;
varying float vSeed;

void main() {
  float angle = vSeed * 6.2831 + uTime * (0.4 + vSeed);
  vec2 centered = gl_PointCoord - 0.5;
  vec2 turned = vec2(cos(angle) * centered.x - sin(angle) * centered.y, sin(angle) * centered.x + cos(angle) * centered.y);
  float petal = smoothstep(0.5, 0.42, length(turned * vec2(1.0, 2.1)));
  float vein = 1.0 - smoothstep(0.0, 0.05, abs(turned.x)) * 0.25;
  gl_FragColor = vec4(uColor * (0.9 + vSeed * 0.25) * vein, petal * (0.55 + vSeed * 0.4));
}
`;

export function petals(
  count: number,
  color: string,
  pixelRatio: number,
): Points<BufferGeometry, ShaderMaterial> {
  const random = seededRandom(1102);
  const positions = new Float32Array(count * 3);
  const seeds = new Float32Array(count);
  for (let index = 0; index < count; index += 1) {
    positions.set(
      [
        (random() - 0.5) * FIELD.width,
        (random() - 0.5) * FIELD.height,
        (random() - 0.5) * FIELD.depth,
      ],
      index * 3,
    );
    seeds[index] = random();
  }
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(positions, 3));
  geometry.setAttribute("aSeed", new BufferAttribute(seeds, 1));
  const material = new ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uPixelRatio: { value: pixelRatio },
      uHeight: { value: FIELD.height },
      uColor: { value: new Color(color) },
    },
    transparent: true,
    depthWrite: false,
    blending: NormalBlending,
  });
  return new Points(geometry, material);
}
