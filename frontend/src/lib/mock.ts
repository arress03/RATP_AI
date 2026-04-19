import { LinePrediction, RiskLevel } from "./lines";

const LINES = ["1", "2", "3", "3b", "4", "5", "6", "7", "7b", "8", "9", "10", "11", "12", "13", "14"];

function risk(p: number): RiskLevel {
  if (p >= 0.7) return "high";
  if (p >= 0.4) return "medium";
  return "low";
}

export const MOCK_PREDICTIONS: LinePrediction[] = [
  { line: "1",  disruption_probability: 0.12, risk_level: risk(0.12) },
  { line: "2",  disruption_probability: 0.55, risk_level: risk(0.55) },
  { line: "3",  disruption_probability: 0.78, risk_level: risk(0.78) },
  { line: "3b", disruption_probability: 0.20, risk_level: risk(0.20) },
  { line: "4",  disruption_probability: 0.43, risk_level: risk(0.43) },
  { line: "5",  disruption_probability: 0.08, risk_level: risk(0.08) },
  { line: "6",  disruption_probability: 0.61, risk_level: risk(0.61) },
  { line: "7",  disruption_probability: 0.33, risk_level: risk(0.33) },
  { line: "7b", disruption_probability: 0.15, risk_level: risk(0.15) },
  { line: "8",  disruption_probability: 0.82, risk_level: risk(0.82) },
  { line: "9",  disruption_probability: 0.47, risk_level: risk(0.47) },
  { line: "10", disruption_probability: 0.09, risk_level: risk(0.09) },
  { line: "11", disruption_probability: 0.70, risk_level: risk(0.70) },
  { line: "12", disruption_probability: 0.25, risk_level: risk(0.25) },
  { line: "13", disruption_probability: 0.58, risk_level: risk(0.58) },
  { line: "14", disruption_probability: 0.17, risk_level: risk(0.17) },
];
