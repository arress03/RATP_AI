import { LinePrediction } from "./lines";

// NEXT_PUBLIC_API_URL est defini en dev local (.env.local) pour pointer vers localhost:8000.
// En production Vercel, cette variable n'est pas definie : on utilise /api
// qui est proxifie vers Railway via le rewrite dans vercel.json.
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api";

export async function fetchAllPredictions(): Promise<LinePrediction[]> {
  const res = await fetch(`${API_BASE}/predict/all`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
