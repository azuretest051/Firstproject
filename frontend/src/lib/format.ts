import type { Budget, RecommendationItem } from "./types";

export function tasteScore(rank: number): number {
  const r = Number(rank) || 1;
  return Math.max(72, 99 - (r - 1) * 4);
}

export function formatCost(item: RecommendationItem): string {
  const cost = item.estimated_cost ?? item.cost_for_two;
  if (cost == null || cost === "") return "";
  if (typeof cost === "number") return `₹${Math.round(cost)} for two`;
  const text = String(cost).trim().toLowerCase();
  if (text === "low") return "₹ Low";
  if (text === "medium") return "₹₹ Medium";
  if (text === "high") return "₹₹₹ High";
  return String(cost);
}

export function budgetLabel(budget: Budget | string): string {
  const map: Record<string, string> = {
    low: "₹ Low",
    medium: "₹₹ Medium",
    high: "₹₹₹ High",
  };
  return map[String(budget || "").toLowerCase()] || String(budget || "");
}

export function cuisineTags(cuisine: string | null | undefined, limit = 3): string[] {
  if (!cuisine) return [];
  return String(cuisine)
    .replace(/\|/g, ",")
    .split(",")
    .map((p) => p.trim())
    .filter(Boolean)
    .slice(0, limit);
}

export const PLACEHOLDER_IMAGES = [
  "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80",
  "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80",
];

export const CUISINE_OPTIONS = [
  "North Indian",
  "Chinese",
  "South Indian",
  "Fast Food",
  "Biryani",
  "Italian",
  "Cafe",
  "Continental",
  "Pizza",
  "Street Food",
] as const;

export const NEIGHBORHOOD_PILLS = [
  "Koramangala",
  "Indiranagar",
  "Lavelle Road",
  "HSR",
  "Church Street",
  "Whitefield",
] as const;

export const VIBE_CHIPS = [
  "Candlelit Outdoor",
  "Craft Beer on Tap",
  "Chef's Tasting Menu",
  "Pet-Friendly Garden",
] as const;
