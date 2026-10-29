import { AdditiveBlending, Color, ShaderMaterial } from "three";

const vertexShader = `
uniform float uTime;
uniform float uProgress;
uniform float uPulse;
uniform float uPixelRatio;
uniform float uViewport;
uniform float uSize;
uniform float uOpacity;
attribute vec3 aScatter;
attribute float aSeed;
varying float vAlpha;

void main() {
  float settle = smoothstep(0.0, 1.0, clamp(uProgress * 1.3 - aSeed * 0.3, 0.0, 1.0));
  vec3 point = mix(aScatter, position, settle);
  float hem = smoothstep(-0.55, -1.3, position.y);
  point.x += sin(point.y * 3.0 + uTime * 1.6 + aSeed * 6.2831) * 0.03;
  point.z += cos(point.y * 2.6 + uTime * 1.3) * 0.03;
  point.x += sin(uTime * 2.2 + position.x * 4.0 + aSeed * 3.0) * 0.08 * hem;
  point.y += sin(uTime * 0.9) * 0.07 + hem * sin(uTime * 1.8 + aSeed * 9.0) * 0.04;
  point *= 1.0 + uPulse * 0.06;
  vec4 view = modelViewMatrix * vec4(point, 1.0);
  gl_Position = projectionMatrix * view;
  gl_PointSize = uSize * (1.0 + aSeed) * (1.0 + uPulse * 0.9) * uPixelRatio * uViewport * (6.0 / -view.z);
  float front = mix(0.08, 1.0, smoothstep(-0.6, 0.85, position.z));
  vAlpha = uOpacity * mix(0.1, 1.0, settle) * front * (0.7 + 0.3 * sin(uTime * 1.7 + aSeed * 21.0));
}
`;

const fragmentShader = `
uniform vec3 uColor;
varying float vAlpha;

void main() {
  float distanceToCenter = length(gl_PointCoord - 0.5);
  float glow = pow(smoothstep(0.5, 0.0, distanceToCenter), 1.6);
  gl_FragColor = vec4(uColor, glow * vAlpha);
}
`;

export type GlowLayer = { size: number; opacity: number };

export function ghostMaterial(
  color: string,
  pixelRatio: number,
  layer: GlowLayer,
): ShaderMaterial {
  return new ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uProgress: { value: 0 },
      uPulse: { value: 0 },
      uPixelRatio: { value: pixelRatio },
      uViewport: { value: 1 },
      uSize: { value: layer.size },
      uOpacity: { value: layer.opacity },
      uColor: { value: new Color(color) },
    },
    transparent: true,
    depthWrite: false,
    blending: AdditiveBlending,
  });
}
