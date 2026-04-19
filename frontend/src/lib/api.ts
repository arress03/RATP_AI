import { LinePrediction } from "./lines";

// En prod Vercel, le rewrite /api/* proxifie vers Railway (pas de CORS).
// En dev local, on tape directement sur l'API FastAPI.
const API_BASE =
  typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "/api"
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");

export async function fetchAllPredictions(): Promise<LinePrediction[]> {
  const res = await fetch(`${API_BASE}/predict/all`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
