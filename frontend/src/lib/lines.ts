export type RiskLevel = "low" | "medium" | "high";

export interface LinePrediction {
  line: string;
  disruption_probability: number;
  risk_level: RiskLevel;
}

// Couleurs officielles RATP par ligne
export const LINE_COLORS: Record<string, string> = {
  "1":   "#FFCD00",
  "2":   "#003CA6",
  "3":   "#837902",
  "3b":  "#6EC4E8",
  "4":   "#CF009E",
  "5":   "#FF7E2E",
  "6":   "#6ECA97",
  "7":   "#FA9ABA",
  "7b":  "#6ECA97",
  "8":   "#E19BDF",
  "9":   "#B6BD00",
  "10":  "#C9910D",
  "11":  "#704B1C",
  "12":  "#007852",
  "13":  "#6EC4E8",
  "14":  "#62259D",
};

export const LINE_TEXT_COLORS: Record<string, string> = {
  "1":  "#000000",
  "3":  "#ffffff",
  "5":  "#ffffff",
  "7":  "#000000",
  "7b": "#000000",
  "8":  "#000000",
  "9":  "#000000",
  "10": "#000000",
  "11": "#ffffff",
};

export function getLineTextColor(line: string): string {
  return LINE_TEXT_COLORS[line] ?? "#ffffff";
}

export const RISK_CONFIG: Record<RiskLevel, { label: string; bg: string; text: string }> = {
  low:    { label: "Faible",  bg: "bg-emerald-900/60", text: "text-emerald-300" },
  medium: { label: "Moyen",   bg: "bg-amber-900/60",   text: "text-amber-300"   },
  high:   { label: "Élevé",   bg: "bg-red-900/60",     text: "text-red-300"     },
};
