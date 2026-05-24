/**
 * ai-service の /recommend/hybrid と互換の型。
 * バックエンドの Pydantic モデル (ai_service.recommend.dto) と shape を一致させること。
 */

export type JapaneseLevel = "N1" | "N2" | "N3" | "N4" | "N5";

export interface UserContext {
  japanese_level: JapaneseLevel | null;
  region: string | null;
  preferred_language: string;
  interest_categories: string[];
}

export interface HybridRecommendRequest {
  user: UserContext;
  query?: string | null;
  region?: string | null;
  limit: number;
  weight_content: number;
  weight_semantic: number;
}

export interface HybridRecommendedItem {
  item_id: string;
  title: string | null;
  hybrid_score: number;
  content_score: number;
  semantic_score: number;
  reasons: string[];
}

export interface HybridRecommendResponse {
  items: HybridRecommendedItem[];
}
