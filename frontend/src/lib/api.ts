import { LinePrediction } from "./lines";

// Toujours /api — chemin relatif sans domaine.
// Dev local  : next.config.ts rewrite /api/* -> localhost:8000
// Vercel prod : vercel.json rewrite /api/* -> Railway
const API_BASE = "/api";

export async function fetchAllPredictions(): Promise<LinePrediction[]> {
  const res = await fetch(`${API_BASE}/predict/all`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
