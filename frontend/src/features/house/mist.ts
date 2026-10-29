import { BufferAttribute, BufferGeometry, Color, Points, ShaderMaterial } from "three";
import { seededRandom } from "../haunting/random";

const COUNT = 46;
const FIELD = { width: 13, depth: 6 };

const vertexShader = `
uniform float uTime;
uniform float uScale;
uniform float uWidth;
attribute float aSeed;
varying float vSeed;

void main() {
  vec3 point = position;
  point.x = mod(position.x + uTime * (0.05 + aSeed * 0.08) + uWidth * 0.5, uWidth) - uWidth * 0.5;
  vec4 view = modelViewMatrix * vec4(point, 1.0);
  gl_Position = projectionMatrix * view;
  gl_PointSize = (2.2 + aSeed * 1.6) * uScale / -view.z;
  vSeed = aSeed;
}
`;

const fragmentShader = `
uniform vec3 uColor;
varying float vSeed;

void main() {
  float cloud = smoothstep(0.5, 0.0, length(gl_PointCoord - 0.5));
  gl_FragColor = vec4(uColor, cloud * (0.018 + vSeed * 0.022));
  #include <colorspace_fragment>
}
`;

export function mist(color: string) {
  const random = seededRandom(512);
  const positions = new Float32Array(COUNT * 3);
  const seeds = new Float32Array(COUNT);
  for (let index = 0; index < COUNT; index += 1) {
    positions.set([(random() - 0.5) * FIELD.width, 0.15 + random() * 0.35, -0.5 + random() * FIELD.depth], index * 3);
    seeds[index] = random();
  }
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(positions, 3));
  geometry.setAttribute("aSeed", new BufferAttribute(seeds, 1));
  const material = new ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: { uTime: { value: 0 }, uScale: { value: 1 }, uWidth: { value: FIELD.width }, uColor: { value: new Color(color) } },
    transparent: true,
    depthWrite: false,
  });
  const points = new Points(geometry, material);
  return { points, uniforms: material.uniforms, dispose: () => (geometry.dispose(), material.dispose()) };
}
