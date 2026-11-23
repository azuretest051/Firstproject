export type Budget = "low" | "medium" | "high";

export interface RecommendPrefs {
  location: string;
  budget: Budget;
  cuisine: string;
  min_rating: number;
  additional_preferences?: string | null;
  top_n?: number;
}

export interface RecommendationItem {
  rank: number;
  restaurant_name: string;
  cuisine?: string | null;
  rating?: number | null;
  estimated_cost?: string | null;
  explanation: string;
  location?: string | null;
  cost_for_two?: number | null;
}

export interface RecommendMeta {
  candidates_considered: number;
  used_fallback: boolean;
  match_count: number;
  no_matches: boolean;
  capped: boolean;
  status: string;
  provider?: string | null;
  model?: string | null;
  fallback_reason?: string | null;
}

export interface RecommendResponse {
  summary: string;
  recommendations: RecommendationItem[];
  meta: RecommendMeta;
}

export interface LocationsResponse {
  cities: string[];
  locations: string[];
}
