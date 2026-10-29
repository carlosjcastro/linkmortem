import { useEffect, useEffectEvent, useRef, useState } from "react";
import { useMotion } from "../features/motion/useMotion";

export type AnimatedScene = {
  start: () => void;
  stop: () => void;
  still: () => void;
  resize: (width: number, height: number) => void;
  dispose: () => void;
};

export function useAnimatedScene<T extends AnimatedScene>(
  build: (canvas: HTMLCanvasElement) => Promise<T>,
  key = "",
) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneRef = useRef<T | null>(null);
  const { enabled } = useMotion();
  const [failed, setFailed] = useState(false);
  const create = useEffectEvent(build);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    let disposed = false;
    let cleanup = () => {};

    create(canvas)
      .then((scene) => {
        if (disposed) return scene.dispose();
        sceneRef.current = scene;
        let visible = true;
        const play = () =>
          enabled && visible && !document.hidden
            ? scene.start()
            : (scene.stop(), scene.still());
        const resize = () => {
          scene.resize(canvas.clientWidth, canvas.clientHeight);
          if (!enabled) scene.still();
        };
        const sizeObserver = new ResizeObserver(resize);
        const viewObserver = new IntersectionObserver(([entry]) => {
          visible = entry.isIntersecting;
          play();
        });

        sizeObserver.observe(canvas);
        viewObserver.observe(canvas);
        document.addEventListener("visibilitychange", play);
        resize();
        play();

        cleanup = () => {
          sizeObserver.disconnect();
          viewObserver.disconnect();
          document.removeEventListener("visibilitychange", play);
          scene.dispose();
          sceneRef.current = null;
        };
      })
      .catch(() => setFailed(true));

    return () => {
      disposed = true;
      cleanup();
    };
  }, [enabled, key]);

  return { canvasRef, sceneRef, failed, enabled };
}
