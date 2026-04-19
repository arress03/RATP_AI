"use client";

import { useState } from "react";
import LineCard from "@/components/LineCard";
import LastUpdate from "@/components/LastUpdate";
import { MOCK_PREDICTIONS } from "@/lib/mock";
import { RiskLevel, RISK_CONFIG } from "@/lib/lines";

const RISK_ORDER: RiskLevel[] = ["high", "medium", "low"];

export default function DashboardPage() {
  const [filter, setFilter] = useState<RiskLevel | "all">("all");

  const predictions = MOCK_PREDICTIONS.slice().sort(
    (a, b) => RISK_ORDER.indexOf(a.risk_level) - RISK_ORDER.indexOf(b.risk_level),
  );

  const filtered = filter === "all" ? predictions : predictions.filter((p) => p.risk_level === filter);

  const counts = {
    high:   predictions.filter((p) => p.risk_level === "high").length,
    medium: predictions.filter((p) => p.risk_level === "medium").length,
    low:    predictions.filter((p) => p.risk_level === "low").length,
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
          <LastUpdate updatedAt={new Date()} />
        </div>

        {/* Résumé risques */}
        <div className="mt-6 grid grid-cols-3 gap-3">
          {(["high", "medium", "low"] as RiskLevel[]).map((level) => {
            const { label, bg, text } = RISK_CONFIG[level];
            return (
              <div key={level} className={`rounded-lg p-3 text-center ${bg}`}>
                <p className={`text-2xl font-bold ${text}`}>{counts[level]}</p>
                <p className={`text-xs mt-0.5 ${text} opacity-80`}>{label}</p>
              </div>
            );
          })}
        </div>
      </header>

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
        {filtered.map((p) => (
          <LineCard key={p.line} prediction={p} />
        ))}
      </section>

      <footer className="mt-8 text-center text-xs text-[--muted]">
        Données simulées — connexion API à venir
      </footer>
    </main>
  );
}
