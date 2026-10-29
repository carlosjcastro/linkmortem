import { useEffect } from "react";
import { useAnimatedScene } from "../../lib/useAnimatedScene";
import { loadHaunting } from "./loadHaunting";

type HauntingCanvasProps = { pulseSignal: number };

export default function HauntingCanvas({ pulseSignal }: HauntingCanvasProps) {
  const { canvasRef, sceneRef, failed, enabled } =
    useAnimatedScene(loadHaunting);

  useEffect(() => {
    if (!enabled) return;
    const follow = (event: PointerEvent) =>
      sceneRef.current?.point(
        event.clientX / window.innerWidth - 0.5,
        event.clientY / window.innerHeight - 0.5,
      );
    window.addEventListener("pointermove", follow, { passive: true });
    return () => window.removeEventListener("pointermove", follow);
  }, [enabled, sceneRef]);

  useEffect(() => {
    if (pulseSignal > 0) sceneRef.current?.pulse();
  }, [pulseSignal, sceneRef]);

  if (failed) return null;
  return <canvas ref={canvasRef} aria-hidden className="block h-full w-full" />;
}
