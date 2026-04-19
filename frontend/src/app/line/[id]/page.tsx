"use client";

import Link from "next/link";
import { use } from "react";
import RiskBadge from "@/components/RiskBadge";
import Sparkline from "@/components/Sparkline";
import { usePredictions } from "@/hooks/usePredictions";
import { getMockHistory } from "@/lib/history";
import { LINE_COLORS, getLineTextColor, RISK_CONFIG } from "@/lib/lines";

interface Props {
  params: Promise<{ id: string }>;
}

export default function LineDetailPage({ params }: Props) {
  const { id } = use(params);
  const line = decodeURIComponent(id);

  const { predictions, loading } = usePredictions();
  const prediction = predictions.find((p) => p.line === line);
  const history = getMockHistory(line);

  const bgColor = LINE_COLORS[line] ?? "#555";
  const textColor = getLineTextColor(line);

  return (
    <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
      {/* Retour */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-[--muted] hover:text-[--foreground] transition-colors mb-6"
      >
        ← Toutes les lignes
      </Link>

      {/* En-tête ligne */}
      <header className="flex items-center gap-5 mb-8">
        <div
          className="w-16 h-16 rounded-full flex-shrink-0 flex items-center justify-center font-bold text-lg"
          style={{ backgroundColor: bgColor, color: textColor }}
        >
          {line}
        </div>
        <div>
          <h1 className="text-xl font-bold">Ligne {line}</h1>
          {loading ? (
            <p className="text-sm text-[--muted] mt-1">Chargement…</p>
          ) : prediction ? (
            <div className="mt-1">
              <RiskBadge level={prediction.risk_level} probability={prediction.disruption_probability} />
            </div>
          ) : (
            <p className="text-sm text-[--muted] mt-1">Ligne inconnue</p>
          )}
        </div>
      </header>

      {/* Carte risque actuel */}
      {prediction && (
        <section className="rounded-xl p-5 bg-[--surface] border border-[--border] mb-6">
          <h2 className="text-xs font-semibold text-[--muted] uppercase tracking-wider mb-4">
            Risque actuel (30 min)
          </h2>
          <div className="flex items-center justify-between">
            <span className="text-4xl font-bold" style={{ color: bgColor }}>
              {Math.round(prediction.disruption_probability * 100)}%
            </span>
            <div className={`text-right px-4 py-2 rounded-lg ${RISK_CONFIG[prediction.risk_level].bg}`}>
              <p className={`text-lg font-bold ${RISK_CONFIG[prediction.risk_level].text}`}>
                {RISK_CONFIG[prediction.risk_level].label}
              </p>
              <p className="text-xs text-[--muted]">niveau de risque</p>
            </div>
          </div>
        </section>
      )}

      {/* Historique 24h */}
      <section className="rounded-xl p-5 bg-[--surface] border border-[--border]">
        <h2 className="text-xs font-semibold text-[--muted] uppercase tracking-wider mb-4">
          Historique 24 h (simulé)
        </h2>
        <Sparkline data={history} color={bgColor} />

        {/* Axe horaire */}
        <div className="flex justify-between mt-2 text-[10px] text-[--muted]">
          {history.filter((_, i) => i % 6 === 0).map((p) => (
            <span key={p.time}>{p.time}</span>
          ))}
          <span>{history[history.length - 1].time}</span>
        </div>

        {/* Tableau */}
        <div className="mt-5 grid grid-cols-4 gap-2">
          {history.map((p) => (
            <div key={p.time} className="text-center rounded-lg py-2 bg-[--surface-2]">
              <p className="text-[10px] text-[--muted]">{p.time}</p>
              <p className="text-xs font-semibold mt-0.5" style={{ color: bgColor }}>
                {Math.round(p.probability * 100)}%
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
