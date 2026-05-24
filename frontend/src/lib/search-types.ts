/**
 * ai-service の /search/items と互換の型。
 * バックエンドの Pydantic モデル (ai_service.search.dto) と shape を一致させること。
 */

export interface SemanticSearchRequest {
  query: string;
  limit: number;
}

export interface SearchResultItem {
  item_id: string;
  title: string | null;
  similarity: number; // 0..1（高いほど近い）
}

export interface SemanticSearchResponse {
  query: string;
  results: SearchResultItem[];
}
