import type {
  LocationsResponse,
  RecommendPrefs,
  RecommendResponse,
} from "./types";

const API_BASE = "/api/backend";

async function readError(res: Response): Promise<string> {
  const data = await res.json().catch(() => ({}));
  const detail = data.detail || data.error || res.statusText;
  return typeof detail === "string" ? detail : JSON.stringify(detail);
}

export async function fetchLocations(): Promise<LocationsResponse> {
  const res = await fetch(`${API_BASE}/meta/locations`);
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function postRecommend(
  prefs: RecommendPrefs,
): Promise<RecommendResponse> {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prefs),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}
