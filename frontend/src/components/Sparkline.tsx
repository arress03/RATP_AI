import { HistoryPoint } from "@/lib/history";

interface Props {
  data: HistoryPoint[];
  color: string;
  height?: number;
}

export default function Sparkline({ data, color, height = 80 }: Props) {
  if (data.length === 0) return null;

  const W = 600;
  const H = height;
  const pad = 4;

  const xs = data.map((_, i) => pad + (i / (data.length - 1)) * (W - pad * 2));
  const ys = data.map((d) => pad + (1 - d.probability) * (H - pad * 2));

  const linePath = xs.map((x, i) => `${i === 0 ? "M" : "L"} ${x} ${ys[i]}`).join(" ");
  const areaPath = `${linePath} L ${xs[xs.length - 1]} ${H} L ${xs[0]} ${H} Z`;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" aria-hidden="true">
      <defs>
        <linearGradient id={`grad-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {/* Zone remplie */}
      <path d={areaPath} fill={`url(#grad-${color.replace("#", "")})`} />
      {/* Ligne */}
      <path d={linePath} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" />
      {/* Points */}
      {xs.map((x, i) => (
        <circle key={i} cx={x} cy={ys[i]} r="3" fill={color} />
      ))}
    </svg>
  );
}
