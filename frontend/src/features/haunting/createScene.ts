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
import type { AnimatedScene } from "../../lib/useAnimatedScene";
import { ghostFace } from "./ghostFace";
import { ghostMaterial } from "./ghostMaterial";
import { ghostPoints } from "./ghostPoints";
import { petals } from "./petals";

const GHOST_POINTS = 9000;
const PETAL_COUNT = 70;
const ASSEMBLY_SECONDS = 2.6;
const MAX_PIXEL_RATIO = 1.75;
const SIDE_LAYOUT_WIDTH = 1024;
const REFERENCE_HEIGHT = 900;
const GHOST_SIZE = { width: 2.5, height: 2.9 };
const MAX_SCALE = 0.95;
const WIDE_CENTER = 0.6;
const WIDE_ROOM = 0.72;
const CORE_LAYER = { size: 3.8, opacity: 1 };
const AURA_LAYER = { size: 16, opacity: 0.07 };

export type HauntingColors = {
  spirit: string;
  marigold: string;
  night: string;
  bone: string;
};

export type Haunting = AnimatedScene & {
  point: (x: number, y: number) => void;
  pulse: () => void;
};

export function createScene(
  canvas: HTMLCanvasElement,
  colors: HauntingColors,
): Haunting {
  const renderer = new WebGLRenderer({
    canvas,
    alpha: false,
    antialias: false,
    powerPreference: "low-power",
  });
  renderer.setClearColor(colors.night);
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
      const halfHeight =
        Math.tan(MathUtils.degToRad(camera.fov / 2)) * camera.position.z;
      const halfWidth = halfHeight * camera.aspect;
      const wide = width >= SIDE_LAYOUT_WIDTH;
      const room = wide ? halfWidth * WIDE_ROOM : halfWidth * 1.6;
      ghost.scale.setScalar(
        Math.min(
          MAX_SCALE,
          (halfHeight * 1.5) / GHOST_SIZE.height,
          room / GHOST_SIZE.width,
        ),
      );
      ghost.position.set(
        wide ? halfWidth * WIDE_CENTER : 0,
        wide ? 0.15 : 0.05,
        0,
      );
      const viewport = MathUtils.clamp(
        (height / REFERENCE_HEIGHT) ** 0.75,
        0.45,
        1.2,
      );
      [...layers, petalField.material].forEach(
        (material) => (material.uniforms.uViewport.value = viewport),
      );
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
