/**
 * Search Service
 * API calls for search operations (hybrid, semantic, and filter-based)
 */

import { api } from './api.config';
import type {
  HybridSearchRequest,
  HybridSearchResponse,
  SemanticSearchParams,
  FilterSearchParams,
  SearchResult,
} from '@/types';

/**
 * Search Service
 * All search-related API endpoints
 */
export const searchService = {
  /**
   * Hybrid Search - Intelligent search combining semantic AI and filters
   * POST /api/search
   *
   * Uses LangGraph workflow to:
   * 1. Parse natural language query with AI
   * 2. Generate embeddings for semantic search
   * 3. Execute filter-based search
   * 4. Merge results using Reciprocal Rank Fusion
   * 5. Optionally rerank with AI
   *
   * @param request - Search query and options
   * @returns Search results with parsed query and metadata
   *
   * @example
   * ```ts
   * const results = await searchService.hybrid({
   *   query: 'quick vegetarian pasta under 30 minutes',
   *   limit: 10,
   *   use_semantic: true,
   *   use_filters: true
   * });
   *
   * console.log('Parsed query:', results.parsed_query);
   * console.log('Found:', results.total, 'recipes');
   * results.results.forEach(r => {
   *   console.log(`${r.recipe.name} - Score: ${r.score} (${r.match_type})`);
   * });
   * ```
   */
  hybrid: async (request: HybridSearchRequest): Promise<HybridSearchResponse> => {
    return api.post<HybridSearchResponse>('/search', request);
  },

  /**
   * Semantic Search - Pure AI vector similarity search
   * POST /api/search/semantic
   *
   * Uses vector embeddings to find recipes semantically similar to the query.
   * Understands context and synonyms (e.g., "creamy pasta" matches "Alfredo", "Carbonara").
   *
   * @param params - Query and limit
   * @returns Array of recipes with similarity scores
   *
   * @example
   * ```ts
   * const results = await searchService.semantic({
   *   query: 'creamy pasta',
   *   limit: 5
   * });
   *
   * results.forEach(r => {
   *   console.log(`${r.recipe.name} - Similarity: ${r.score}`);
   * });
   * ```
   */
  semantic: async (params: SemanticSearchParams): Promise<SearchResult[]> => {
    return api.post<SearchResult[]>('/search/semantic', null, { params });
  },

  /**
   * Filter Search - Pure attribute-based filtering
   * POST /api/search/filter
   *
   * Traditional search using exact attribute matching.
   * All filters use AND logic, except diet_types which uses OR.
   *
   * @param params - Filter criteria
   * @returns Array of matching recipes
   *
   * @example
   * ```ts
   * const results = await searchService.filter({
   *   filters: {
   *     cuisine_type: 'Italian',
   *     difficulty: 'easy',
   *     max_prep_time: 20,
   *     diet_types: ['vegetarian', 'vegan']
   *   },
   *   limit: 10
   * });
   * ```
   */
  filter: async (params: FilterSearchParams): Promise<SearchResult[]> => {
    return api.post<SearchResult[]>('/search/filter', params.filters, {
      params: { limit: params.limit },
    });
  },
};

/**
 * Export individual functions for tree-shaking
 */
export const {
  hybrid: hybridSearch,
  semantic: semanticSearch,
  filter: filterSearch,
} = searchService;
