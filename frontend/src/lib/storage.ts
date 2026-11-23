import type { RecommendPrefs, RecommendResponse } from "./types";

const STORAGE_KEY = "tastematch_last_result";
const PREFS_KEY = "tastematch_last_prefs";

export function saveResult(prefs: RecommendPrefs, result: RecommendResponse) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(result));
}

export function loadResult(): {
  prefs: RecommendPrefs | null;
  result: RecommendResponse | null;
} {
  if (typeof window === "undefined") {
    return { prefs: null, result: null };
  }
  try {
    const prefs = JSON.parse(sessionStorage.getItem(PREFS_KEY) || "null");
    const result = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "null");
    return { prefs, result };
  } catch {
    return { prefs: null, result: null };
  }
}
