import {
  CROSSES,
  FENCE,
  GROUND,
  HORIZON_HEIGHT,
  HORIZON_WIDTH,
  STONES,
  picketPath,
  picketPositions,
  stonePath,
} from "./horizonShapes";

const STONE_BASE = 104;
const CANDLE = { x: 774, y: 96 };

export default function GraveyardHorizon() {
  return (
    <svg
      viewBox={`0 0 ${HORIZON_WIDTH} ${HORIZON_HEIGHT}`}
      preserveAspectRatio="xMidYMax slice"
      className="-mb-px block h-24 w-full sm:h-32"
      aria-hidden
    >
      <defs>
        <linearGradient id="horizon-mist" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="var(--spectral)" stopOpacity="0" />
          <stop offset="1" stopColor="var(--spectral)" stopOpacity="0.08" />
        </linearGradient>
        <radialGradient id="horizon-candle">
          <stop offset="0" stopColor="var(--marigold)" stopOpacity="0.55" />
          <stop offset="1" stopColor="var(--marigold)" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect
        width={HORIZON_WIDTH}
        height={HORIZON_HEIGHT}
        fill="url(#horizon-mist)"
      />
      <g fill="var(--grave)">
        {STONES.map((stone) => (
          <path
            key={stone.x}
            d={stonePath(stone, STONE_BASE)}
            transform={`rotate(${stone.tilt} ${stone.x + stone.width / 2} ${STONE_BASE})`}
          />
        ))}
        {CROSSES.map(({ x, height }) => (
          <path
            key={x}
            d={`M${x - 2.5} ${STONE_BASE}V${STONE_BASE - height}h5V${STONE_BASE}ZM${x - 11} ${STONE_BASE - height + 10}h22v5h-22Z`}
          />
        ))}
        {picketPositions(FENCE.from, FENCE.to, FENCE.gap).map((x) => (
          <path key={x} d={picketPath(x, FENCE.base, FENCE.height)} />
        ))}
        <rect
          x={FENCE.from}
          y={FENCE.base - FENCE.height + 6}
          width={FENCE.to - FENCE.from}
          height="2.5"
        />
        <rect
          x={FENCE.from}
          y={FENCE.base - 10}
          width={FENCE.to - FENCE.from}
          height="2.5"
        />
        <path d={GROUND} />
      </g>
      <circle
        className="horizon-candle"
        cx={CANDLE.x}
        cy={CANDLE.y - 4}
        r="14"
        fill="url(#horizon-candle)"
      />
      <rect
        x={CANDLE.x - 2}
        y={CANDLE.y}
        width="4"
        height="7"
        rx="1"
        fill="var(--bone)"
      />
      <ellipse
        className="horizon-flame"
        cx={CANDLE.x}
        cy={CANDLE.y - 3}
        rx="1.8"
        ry="3.2"
        fill="var(--marigold)"
      />
    </svg>
  );
}
