import { RiskLevel, RISK_CONFIG } from "@/lib/lines";

interface Props {
  level: RiskLevel;
  probability?: number;
}

export default function RiskBadge({ level, probability }: Props) {
  const { label, bg, text } = RISK_CONFIG[level];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${bg} ${text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${text.replace("text-", "bg-")}`} />
      {label}
      {probability !== undefined && (
        <span className="opacity-75">({Math.round(probability * 100)}%)</span>
      )}
    </span>
  );
}
