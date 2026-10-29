import {
  CircleGeometry,
  Color,
  DirectionalLight,
  FogExp2,
  HemisphereLight,
  MathUtils,
  Mesh,
  MeshStandardMaterial,
  PerspectiveCamera,
  PlaneGeometry,
  PointLight,
  Scene,
  Timer,
  Vector3,
  WebGLRenderer,
} from "three";
import type { AnimatedScene } from "../../lib/useAnimatedScene";
import type { HauntingColors } from "../haunting/createScene";
import { deadTree } from "./deadTree";
import { SCENE_BOUNDS, WINDOW_SLOTS } from "./facade";
import { fence } from "./fence";
import { ghostEyes } from "./ghostEyes";
import { graveyard } from "./graveyard";
import { houseBody } from "./houseBody";
import type { HousePlan } from "./housePlan";
import { houseWindows } from "./houseWindows";
import { mist } from "./mist";
import { moon } from "./moon";
import { GHOST_SCALE, yardGhosts } from "./yardGhosts";

const FIELD_OF_VIEW = 30;
const MAX_PIXEL_RATIO = 1.5;
const VIEW_DIRECTION = new Vector3(0.16, 0.2, 1).normalize();
const INTRO_SECONDS = 2.6;
const STILL_TIME = 4;
const REFERENCE_HEIGHT = 520;
const PICK_PADDING = 10;

export type HouseScene = AnimatedScene & {
  pick: (x: number, y: number) => number;
  hover: (ghost: number) => void;
};

function tone(base: string, toward: string, amount: number): Color {
  return new Color(base).lerp(new Color(toward), amount);
}

export function createHouse(
  canvas: HTMLCanvasElement,
  colors: HauntingColors,
  plan: HousePlan,
): HouseScene {
  const renderer = new WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
    powerPreference: "low-power",
  });
  const pixelRatio = Math.min(window.devicePixelRatio, MAX_PIXEL_RATIO);
  renderer.setPixelRatio(pixelRatio);

  const scene = new Scene();
  scene.fog = new FogExp2(colors.night, 0.034);
  const camera = new PerspectiveCamera(FIELD_OF_VIEW, 1, 0.1, 80);
  const target = new Vector3(
    SCENE_BOUNDS.target.x,
    SCENE_BOUNDS.target.y,
    SCENE_BOUNDS.target.z,
  );

  const wall = new MeshStandardMaterial({
    color: tone(colors.night, colors.bone, 0.2),
    roughness: 0.95,
    flatShading: true,
  });
  const wood = new MeshStandardMaterial({
    color: tone(colors.night, "#000000", 0.35),
    roughness: 1,
    flatShading: true,
  });
  const stone = new MeshStandardMaterial({
    color: tone(colors.night, colors.bone, 0.38),
    roughness: 0.9,
    flatShading: true,
  });
  const earth = new MeshStandardMaterial({
    color: tone(colors.night, "#000000", 0.45),
    roughness: 1,
  });
  const trail = new MeshStandardMaterial({
    color: tone(colors.night, colors.bone, 0.1),
    roughness: 1,
  });

  const ground = new Mesh(
    new CircleGeometry(14, 48).rotateX(-Math.PI / 2),
    earth,
  );
  const path = new Mesh(
    new PlaneGeometry(0.95, 1.6).rotateX(-Math.PI / 2).translate(0, 0.006, 3.3),
    trail,
  );
  const body = houseBody(wall, wood, colors.bone);
  const windows = houseWindows(WINDOW_SLOTS, plan.windows, {
    warm: colors.marigold,
    frame: tone(colors.night, "#000000", 0.4),
    spirit: colors.spirit,
  });
  const graves = graveyard(plan.graves, stone);
  const ghosts = yardGhosts(graves.origins, colors.spirit, pixelRatio);
  const faces = ghostEyes(graves.origins, GHOST_SCALE, colors.night);
  const tree = deadTree(wood);
  const yardFence = fence(wood);
  const sky = moon(colors.bone);
  const fog = mist(colors.bone);

  const moonLight = new DirectionalLight(
    tone(colors.bone, colors.spirit, 0.35),
    1.5,
  );
  moonLight.position.set(-6, 9, 4);
  const rimLight = new DirectionalLight(colors.spirit, 0.7);
  rimLight.position.set(5, 4, -6);
  const porchLight = new PointLight(colors.marigold, 2.4, 4.5, 2);
  porchLight.position.set(0, 1.25, 2.1);

  scene.add(
    new HemisphereLight(tone(colors.night, colors.spirit, 0.4), "#000000", 1.1),
    moonLight,
    rimLight,
    porchLight,
    ground,
    path,
    body.group,
    ...windows.objects,
    graves.stones,
    ghosts.points,
    faces.eyes,
    tree,
    yardFence.group,
    sky.group,
    fog.points,
  );

  const timer = new Timer();
  const size = { width: 1, height: 1, distance: 10 };
  const projected = new Vector3();
  let frame = 0;

  const aim = (elapsed: number) => {
    const angle = Math.sin(elapsed * 0.09) * 0.12;
    const direction = VIEW_DIRECTION.clone().applyAxisAngle(
      new Vector3(0, 1, 0),
      angle,
    );
    camera.position.copy(target).addScaledVector(direction, size.distance);
    camera.lookAt(target);
  };

  const draw = (elapsed: number, intro: number) => {
    aim(elapsed);
    windows.update(elapsed);
    ghosts.uniforms.uTime.value = elapsed;
    ghosts.uniforms.uIntro.value = intro;
    faces.update(elapsed, intro, ghosts.uniforms.uHover.value);
    fog.uniforms.uTime.value = elapsed;
    renderer.render(scene, camera);
  };

  const loop = (time: number) => {
    timer.update(time);
    const elapsed = timer.getElapsed();
    draw(elapsed + STILL_TIME, Math.min(1, elapsed / INTRO_SECONDS));
    frame = requestAnimationFrame(loop);
  };

  const screenOf = (point: Vector3) => {
    projected.copy(point).project(camera);
    return {
      x: ((projected.x + 1) / 2) * size.width,
      y: ((1 - projected.y) / 2) * size.height,
    };
  };

  return {
    start: () => {
      if (frame === 0) frame = requestAnimationFrame(loop);
    },
    stop: () => {
      cancelAnimationFrame(frame);
      frame = 0;
    },
    still: () => draw(STILL_TIME, 1),
    resize: (width, height) => {
      renderer.setSize(width, height, false);
      size.width = width;
      size.height = height;
      camera.aspect = width / height;
      const tangent = Math.tan(MathUtils.degToRad(FIELD_OF_VIEW / 2));
      const halfWidth = (SCENE_BOUNDS.right - SCENE_BOUNDS.left) / 2;
      size.distance =
        Math.max(
          SCENE_BOUNDS.top / 2 / tangent,
          halfWidth / (tangent * camera.aspect),
        ) *
          1.02 +
        2.2;
      camera.updateProjectionMatrix();
      const pixelsPerUnit = (height * pixelRatio) / (2 * tangent);
      windows.scale(pixelsPerUnit);
      fog.uniforms.uScale.value = pixelsPerUnit;
      ghosts.uniforms.uViewport.value = MathUtils.clamp(
        (height / REFERENCE_HEIGHT) ** 0.75,
        0.5,
        1.4,
      );
      aim(STILL_TIME);
    },
    pick: (x, y) => {
      let best = -1;
      let closest = Number.POSITIVE_INFINITY;
      graves.origins.forEach((origin, index) => {
        const center = screenOf(origin);
        const top = screenOf(
          origin.clone().add(new Vector3(0, GHOST_SCALE * 1.4, 0)),
        );
        const reach = Math.abs(center.y - top.y) + PICK_PADDING;
        const distance = Math.hypot(center.x - x, center.y - y);
        if (distance < reach && distance < closest) {
          best = index;
          closest = distance;
        }
      });
      return best;
    },
    hover: (ghost) => {
      ghosts.uniforms.uHover.value = ghost;
      if (frame === 0) draw(STILL_TIME, 1);
    },
    dispose: () => {
      cancelAnimationFrame(frame);
      [
        wall,
        wood,
        stone,
        earth,
        trail,
        ground.geometry,
        path.geometry,
        tree.geometry,
      ].forEach((item) => item.dispose());
      [body, windows, graves, ghosts, faces, yardFence, sky, fog].forEach(
        (part) => part.dispose(),
      );
      renderer.dispose();
    },
  };
}
