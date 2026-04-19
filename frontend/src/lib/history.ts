export interface HistoryPoint {
  time: string;   // "HH:MM"
  probability: number;
}

// Génère 24h de données simulées pour une ligne donnée
export function getMockHistory(line: string): HistoryPoint[] {
  // Seed pseudo-aléatoire déterministe par ligne pour des données cohérentes
  const seed = line.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const rng = (i: number) => {
    const x = Math.sin(seed * 9301 + i * 49297 + 233) * 10000;
    return x - Math.floor(x);
  };

  const now = new Date();
  const points: HistoryPoint[] = [];

  for (let i = 23; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 60 * 60 * 1000);
    const h = d.getHours();
    // Pics aux heures de pointe (7-9h, 17-19h)
    const peakBoost = (h >= 7 && h <= 9) || (h >= 17 && h <= 19) ? 0.3 : 0;
    const base = 0.15 + peakBoost + rng(i) * 0.35;
    points.push({
      time: `${String(h).padStart(2, "0")}:00`,
      probability: Math.min(1, base),
    });
  }

  return points;
}
