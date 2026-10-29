import { AdditiveBlending, CircleGeometry, Color, Group, Mesh, MeshBasicMaterial, PlaneGeometry, ShaderMaterial } from "three";

const POSITION = { x: -4.4, y: 6.4, z: -9 };

const glowVertex = `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const glowFragment = `
uniform vec3 uColor;
varying vec2 vUv;
void main() {
  float halo = pow(smoothstep(0.5, 0.08, distance(vUv, vec2(0.5))), 2.4);
  gl_FragColor = vec4(uColor, halo * 0.32);
  #include <colorspace_fragment>
}
`;

export function moon(color: string) {
  const disc = new CircleGeometry(0.85, 48);
  const discMaterial = new MeshBasicMaterial({ color: new Color(color), fog: false });
  const plane = new PlaneGeometry(7, 7);
  const haloMaterial = new ShaderMaterial({
    vertexShader: glowVertex,
    fragmentShader: glowFragment,
    uniforms: { uColor: { value: new Color(color) } },
    transparent: true,
    depthWrite: false,
    blending: AdditiveBlending,
  });
  const group = new Group();
  const halo = new Mesh(plane, haloMaterial);
  halo.position.z = -0.05;
  group.add(halo, new Mesh(disc, discMaterial));
  group.position.set(POSITION.x, POSITION.y, POSITION.z);
  return { group, dispose: () => [disc, discMaterial, plane, haloMaterial].forEach((item) => item.dispose()) };
}
