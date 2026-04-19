"use client";

import { useEffect, useRef, useState } from "react";
import { fetchAllPredictions } from "@/lib/api";
import { LinePrediction } from "@/lib/lines";

const POLL_INTERVAL_MS = 2 * 60 * 1000; // 2 minutes

interface State {
  predictions: LinePrediction[];
  updatedAt: Date | null;
  loading: boolean;
  error: string | null;
}

export function usePredictions() {
  const [state, setState] = useState<State>({
    predictions: [],
    updatedAt: null,
    loading: true,
    error: null,
  });
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function load() {
    try {
      const data = await fetchAllPredictions();
      setState({ predictions: data, updatedAt: new Date(), loading: false, error: null });
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Erreur inconnue",
      }));
    }
  }

  useEffect(() => {
    load();
    timerRef.current = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return { ...state, refresh: load };
}
