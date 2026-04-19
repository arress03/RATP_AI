import { LinePrediction } from "./lines";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchAllPredictions(): Promise<LinePrediction[]> {
  const res = await fetch(`${API_BASE}/predict/all`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
