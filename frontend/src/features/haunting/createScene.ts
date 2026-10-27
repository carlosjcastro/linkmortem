import {
  BufferAttribute,
  BufferGeometry,
  Group,
  MathUtils,
  PerspectiveCamera,
  Points,
  Scene,
  Timer,
  WebGLRenderer,
} from "three";
import { ghostFace } from "./ghostFace";
import { ghostMaterial } from "./ghostMaterial";
import { ghostPoints } from "./ghostPoints";
import { petals } from "./petals";

const GHOST_POINTS = 9000;
const PETAL_COUNT = 70;
const ASSEMBLY_SECONDS = 2.6;
const MAX_PIXEL_RATIO = 1.75;
const WIDE_ASPECT = 1.1;
const CORE_LAYER = { size: 3.8, opacity: 1 };
const AURA_LAYER = { size: 16, opacity: 0.07 };

export type HauntingColors = {
  spirit: string;
  marigold: string;
  night: string;
};

export type Haunting = {
  start: () => void;
  stop: () => void;
  still: () => void;
  resize: (width: number, height: number) => void;
  point: (x: number, y: number) => void;
  pulse: () => void;
  dispose: () => void;
};

export function createScene(
  canvas: HTMLCanvasElement,
  colors: HauntingColors,
): Haunting {
  const renderer = new WebGLRenderer({
    canvas,
    alpha: true,
    antialias: false,
    powerPreference: "low-power",
  });
  const pixelRatio = Math.min(window.devicePixelRatio, MAX_PIXEL_RATIO);
  renderer.setPixelRatio(pixelRatio);

  const scene = new Scene();
  const camera = new PerspectiveCamera(34, 1, 0.1, 60);
  camera.position.set(0, 0.1, 7.2);

  const buffers = ghostPoints(GHOST_POINTS);
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(buffers.targets, 3));
  geometry.setAttribute("aScatter", new BufferAttribute(buffers.scatter, 3));
  geometry.setAttribute("aSeed", new BufferAttribute(buffers.seeds, 1));
  const spirit = ghostMaterial(colors.spirit, pixelRatio, CORE_LAYER);
  const aura = ghostMaterial(colors.spirit, pixelRatio, AURA_LAYER);
  const layers = [spirit, aura];
  const ghost = new Group();
  const face = ghostFace(colors.night);
  ghost.add(
    new Points(geometry, aura),
    new Points(geometry, spirit),
    face.face,
  );
  const petalField = petals(PETAL_COUNT, colors.marigold, pixelRatio);
  scene.add(ghost, petalField);

  const timer = new Timer();
  const pointer = { x: 0, y: 0 };
  let frame = 0;
  let pulse = 0;

  const draw = (elapsed: number, progress: number) => {
    for (const layer of layers) {
      layer.uniforms.uTime.value = elapsed;
      layer.uniforms.uProgress.value = progress;
      layer.uniforms.uPulse.value = pulse;
    }
    petalField.material.uniforms.uTime.value = elapsed;
    ghost.rotation.y = MathUtils.lerp(ghost.rotation.y, pointer.x * 0.45, 0.05);
    ghost.rotation.x = MathUtils.lerp(ghost.rotation.x, pointer.y * 0.18, 0.05);
    renderer.render(scene, camera);
  };

  const loop = (time: number) => {
    timer.update(time);
    const elapsed = timer.getElapsed();
    pulse = Math.max(0, pulse - timer.getDelta() * 1.4);
    draw(elapsed, Math.min(1, elapsed / ASSEMBLY_SECONDS));
    frame = requestAnimationFrame(loop);
  };

  return {
    start: () => {
      if (frame === 0) frame = requestAnimationFrame(loop);
    },
    stop: () => {
      cancelAnimationFrame(frame);
      frame = 0;
    },
    still: () => draw(0, 1),
    resize: (width, height) => {
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      const wide = camera.aspect > WIDE_ASPECT;
      ghost.position.set(wide ? 1.75 : 0, wide ? 0.25 : 0.1, 0);
      ghost.scale.setScalar(wide ? 0.82 : 0.95);
    },
    point: (x, y) => {
      pointer.x = x;
      pointer.y = y;
    },
    pulse: () => {
      pulse = 1;
    },
    dispose: () => {
      cancelAnimationFrame(frame);
      geometry.dispose();
      layers.forEach((layer) => layer.dispose());
      face.dispose();
      petalField.geometry.dispose();
      petalField.material.dispose();
      renderer.dispose();
    },
  };
}
