import { LinePrediction, LINE_COLORS, getLineTextColor } from "@/lib/lines";
import RiskBadge from "./RiskBadge";

interface Props {
  prediction: LinePrediction;
}

export default function LineCard({ prediction }: Props) {
  const { line, disruption_probability, risk_level } = prediction;
  const bgColor = LINE_COLORS[line] ?? "#555";
  const textColor = getLineTextColor(line);

  return (
    <article className="flex items-center gap-4 rounded-xl p-4 bg-[--surface] border border-[--border] hover:border-[--accent] transition-colors">
      {/* Pastille ligne */}
      <div
        className="w-12 h-12 rounded-full flex-shrink-0 flex items-center justify-center font-bold text-sm"
        style={{ backgroundColor: bgColor, color: textColor }}
        aria-label={`Ligne ${line}`}
      >
        {line}
      </div>

      {/* Infos */}
      <div className="flex-1 min-w-0">
        <p className="font-semibold text-sm text-[--foreground]">Ligne {line}</p>
        <div className="mt-1">
          <RiskBadge level={risk_level} probability={disruption_probability} />
        </div>
      </div>

      {/* Barre de probabilité */}
      <div className="w-20 flex-shrink-0">
        <div className="h-1.5 rounded-full bg-[--surface-2] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.round(disruption_probability * 100)}%`,
              backgroundColor: bgColor,
            }}
          />
        </div>
      </div>
    </article>
  );
}
