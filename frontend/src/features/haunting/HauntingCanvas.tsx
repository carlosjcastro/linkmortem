import { useEffect, useRef, useState } from "react";
import { useMotion } from "../motion/useMotion";
import type { Haunting } from "./createScene";
import { readColors } from "./readColors";

type HauntingCanvasProps = { pulseSignal: number };

export default function HauntingCanvas({ pulseSignal }: HauntingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const hauntingRef = useRef<Haunting | null>(null);
  const { enabled } = useMotion();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    let disposed = false;
    let cleanup = () => {};

    import("./createScene")
      .then(({ createScene }) => {
        if (disposed) return;
        const haunting = createScene(
          canvas,
          readColors(document.documentElement),
        );
        hauntingRef.current = haunting;
        let visible = true;
        const play = () =>
          enabled && visible && !document.hidden
            ? haunting.start()
            : (haunting.stop(), haunting.still());
        const resize = () => {
          haunting.resize(canvas.clientWidth, canvas.clientHeight);
          if (!enabled) haunting.still();
        };
        const sizeObserver = new ResizeObserver(resize);
        const viewObserver = new IntersectionObserver(([entry]) => {
          visible = entry.isIntersecting;
          play();
        });
        const follow = (event: PointerEvent) =>
          haunting.point(
            event.clientX / window.innerWidth - 0.5,
            event.clientY / window.innerHeight - 0.5,
          );

        sizeObserver.observe(canvas);
        viewObserver.observe(canvas);
        document.addEventListener("visibilitychange", play);
        if (enabled)
          window.addEventListener("pointermove", follow, { passive: true });
        resize();
        play();

        cleanup = () => {
          sizeObserver.disconnect();
          viewObserver.disconnect();
          document.removeEventListener("visibilitychange", play);
          window.removeEventListener("pointermove", follow);
          haunting.dispose();
          hauntingRef.current = null;
        };
      })
      .catch(() => setFailed(true));

    return () => {
      disposed = true;
      cleanup();
    };
  }, [enabled]);

  useEffect(() => {
    if (pulseSignal > 0) hauntingRef.current?.pulse();
  }, [pulseSignal]);

  if (failed) return null;
  return <canvas ref={canvasRef} aria-hidden className="block h-full w-full" />;
}
