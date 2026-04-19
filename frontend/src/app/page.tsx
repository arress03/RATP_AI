"use client";

import { useState } from "react";
import LineCard from "@/components/LineCard";
import LastUpdate from "@/components/LastUpdate";
import { usePredictions } from "@/hooks/usePredictions";
import { RiskLevel, RISK_CONFIG } from "@/lib/lines";

const RISK_ORDER: RiskLevel[] = ["high", "medium", "low"];

export default function DashboardPage() {
  const { predictions, updatedAt, loading, error, refresh } = usePredictions();
  const [filter, setFilter] = useState<RiskLevel | "all">("all");

  const sorted = predictions.slice().sort(
    (a, b) => RISK_ORDER.indexOf(a.risk_level) - RISK_ORDER.indexOf(b.risk_level),
  );

  const filtered = filter === "all" ? sorted : sorted.filter((p) => p.risk_level === filter);

  const counts = {
    high:   sorted.filter((p) => p.risk_level === "high").length,
    medium: sorted.filter((p) => p.risk_level === "medium").length,
    low:    sorted.filter((p) => p.risk_level === "low").length,
  };

  return (
    <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
      {/* En-tête */}
      <header className="mb-8">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">RATP AI</h1>
            <p className="text-sm text-[--muted] mt-0.5">Prévision des perturbations — 30 min</p>
          </div>
          <div className="flex items-center gap-3">
            <LastUpdate updatedAt={updatedAt} />
            <button
              onClick={refresh}
              className="text-xs px-2 py-1 rounded bg-[--surface-2] text-[--muted] hover:text-[--foreground] transition-colors"
              aria-label="Rafraîchir"
            >
              ↻
            </button>
          </div>
        </div>

        {/* Résumé risques */}
        <div className="mt-6 grid grid-cols-3 gap-3">
          {(["high", "medium", "low"] as RiskLevel[]).map((level) => {
            const { label, bg, text } = RISK_CONFIG[level];
            return (
              <div key={level} className={`rounded-lg p-3 text-center ${bg}`}>
                <p className={`text-2xl font-bold ${text}`}>{loading ? "—" : counts[level]}</p>
                <p className={`text-xs mt-0.5 ${text} opacity-80`}>{label}</p>
              </div>
            );
          })}
        </div>
      </header>

      {/* Erreur API */}
      {error && (
        <div className="mb-4 rounded-lg px-4 py-3 bg-red-900/40 border border-red-700/50 text-red-300 text-sm">
          Impossible de contacter l&apos;API : {error}
        </div>
      )}

      {/* Filtres */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {(["all", "high", "medium", "low"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              filter === f
                ? "bg-[--accent] text-white"
                : "bg-[--surface-2] text-[--muted] hover:text-[--foreground]"
            }`}
          >
            {f === "all" ? "Toutes" : RISK_CONFIG[f].label}
          </button>
        ))}
      </div>

      {/* Liste des lignes */}
      <section className="flex flex-col gap-3">
        {loading && (
          <p className="text-center text-[--muted] text-sm py-12">Chargement…</p>
        )}
        {!loading && filtered.map((p) => (
          <LineCard key={p.line} prediction={p} />
        ))}
      </section>

      <footer className="mt-8 text-center text-xs text-[--muted]">
        Actualisation automatique toutes les 2 minutes
      </footer>
    </main>
  );
}
