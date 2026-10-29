import { type PointerEvent, useMemo, useState } from "react";
import { useAnimatedScene } from "../../lib/useAnimatedScene";
import { useTranslation } from "../i18n/useTranslation";
import { WINDOW_SLOTS } from "./facade";
import { type HouseCounts, housePlan } from "./housePlan";
import { loadHouse } from "./loadHouse";
import { revealGhost } from "./revealGhost";

const LEGEND: { state: keyof HouseCounts; swatch: string }[] = [
  { state: "alive", swatch: "bg-marigold" },
  { state: "unknown", swatch: "bg-marigold/40" },
  {
    state: "ghost",
    swatch: "bg-night-deep ring-1 ring-inset ring-spectral/70",
  },
];

const TOOLTIP_HALF_WIDTH = 150;

type HauntedHouseProps = HouseCounts & { ghostUrls: string[] };
type Hovered = { index: number; x: number; y: number };

export default function HauntedHouse({
  alive,
  ghost,
  unknown,
  ghostUrls,
}: HauntedHouseProps) {
  const { t } = useTranslation();
  const counts = { alive, ghost, unknown };
  const plan = useMemo(
    () => housePlan({ alive, ghost, unknown }, WINDOW_SLOTS.length),
    [alive, ghost, unknown],
  );
  const { canvasRef, sceneRef, failed, enabled } = useAnimatedScene(
    (canvas) => loadHouse(canvas, plan),
    `${alive}:${ghost}:${unknown}`,
  );
  const [hovered, setHovered] = useState<Hovered | null>(null);

  const ghostAt = (event: PointerEvent<HTMLCanvasElement>): Hovered | null => {
    const bounds = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - bounds.left;
    const y = event.clientY - bounds.top;
    const index = sceneRef.current?.pick(x, y) ?? -1;
    const edge = Math.min(TOOLTIP_HALF_WIDTH, bounds.width / 2);
    return index >= 0
      ? { index, x: Math.min(Math.max(x, edge), bounds.width - edge), y }
      : null;
  };

  const follow = (event: PointerEvent<HTMLCanvasElement>) => {
    const found = ghostAt(event);
    sceneRef.current?.hover(found ? found.index : -1);
    setHovered(found);
  };

  const leave = () => {
    sceneRef.current?.hover(-1);
    setHovered(null);
  };

  const select = (event: PointerEvent<HTMLCanvasElement>) => {
    const found = ghostAt(event);
    if (found) revealGhost(found.index, enabled);
  };

  if (failed) return null;
  return (
    <figure className="min-w-0">
      <div className="relative h-[clamp(17rem,42vw,30rem)] [mask-image:radial-gradient(ellipse_72%_68%_at_50%_45%,black_62%,transparent_100%)]">
        <canvas
          ref={canvasRef}
          aria-hidden
          onPointerMove={follow}
          onPointerLeave={leave}
          onClick={select}
          className={`block h-full w-full ${hovered ? "cursor-pointer" : ""}`}
        />
        {hovered ? (
          <p
            aria-hidden
            style={{ left: hovered.x, top: hovered.y }}
            className="pointer-events-none absolute max-w-[18rem] -translate-x-1/2 -translate-y-[calc(100%+0.9rem)] break-all rounded-md bg-night-deep/95 px-3 py-1.5 text-[0.85rem] text-bone shadow-lg"
          >
            {ghostUrls[hovered.index]}
          </p>
        ) : null}
      </div>
      <figcaption className="mt-4 text-[0.95rem] leading-[1.6] text-dusk">
        <p>{t.houseTitle}</p>
        <ul className="mt-3 flex flex-wrap gap-x-6 gap-y-2">
          {LEGEND.filter(({ state }) => counts[state] > 0).map(
            ({ state, swatch }) => (
              <li key={state} className="inline-flex items-center gap-2">
                <span
                  aria-hidden
                  className={`size-3 rounded-[3px] ${swatch}`}
                />
                {t.houseLegend[state]} ({counts[state]})
              </li>
            ),
          )}
        </ul>
        {ghost ? (
          <p className="mt-2">
            {ghost > plan.graves
              ? `${t.houseShowing(plan.graves, ghost)} `
              : ""}
            {t.houseHint}
          </p>
        ) : null}
      </figcaption>
    </figure>
  );
}
