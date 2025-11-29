/**
 * Search Service Tests
 * Unit tests for search API service
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { searchService } from '@/services/searchService';
import { apiClient } from '@/services/api.config';
import type { Recipe, HybridSearchRequest } from '@/types';

// Mock is already set up in recipeService.test.ts
vi.mock('@/services/api.config', () => {
  const mockGet = vi.fn();
  const mockPost = vi.fn();
  const mockPut = vi.fn();
  const mockDelete = vi.fn();

  return {
    apiClient: {
      get: mockGet,
      post: mockPost,
      put: mockPut,
      delete: mockDelete,
    },
    api: {
      get: vi.fn((url, config) => mockGet(url, config).then((res: any) => res.data)),
      post: vi.fn((url, data, config) => mockPost(url, data, config).then((res: any) => res.data)),
      put: vi.fn((url, data, config) => mockPut(url, data, config).then((res: any) => res.data)),
      delete: vi.fn((url, config) => mockDelete(url, config).then((res: any) => res.data)),
    },
  };
});

describe('Search Service', () => {
  const mockRecipe: Recipe = {
    id: 'recipe-123',
    name: 'Vegetarian Pasta',
    description: 'Quick and easy pasta',
    instructions: { steps: ['Cook pasta', 'Add sauce'] },
    prep_time: 10,
    cook_time: 15,
    servings: 4,
    difficulty: 'easy',
    cuisine_type: 'Italian',
    diet_types: ['vegetarian'],
    ingredients: [],
    categories: [],
    created_at: '2025-11-15T12:00:00Z',
    updated_at: '2025-11-15T12:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('hybrid', () => {
    it('should perform hybrid search', async () => {
      const request: HybridSearchRequest = {
        query: 'quick vegetarian pasta under 30 minutes',
        limit: 10,
        use_semantic: true,
        use_filters: true,
      };

      const mockResponse = {
        data: {
          query: request.query,
          parsed_query: {
            original_query: request.query,
            ingredients: ['pasta'],
            diet_types: ['vegetarian'],
            max_prep_time: 30,
            semantic_query: 'vegetarian pasta',
          },
          results: [
            {
              recipe: mockRecipe,
              score: 0.95,
              distance: 0.05,
              match_type: 'hybrid' as const,
            },
          ],
          total: 1,
          search_type: 'hybrid' as const,
          metadata: {
            semantic_results: 5,
            filter_results: 3,
            merged_results: 7,
            final_results: 1,
          },
        },
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await searchService.hybrid(request);

      expect(apiClient.post).toHaveBeenCalledWith('/search', request, undefined);
      expect(result.query).toBe(request.query);
      expect(result.parsed_query?.diet_types).toContain('vegetarian');
      expect(result.results).toHaveLength(1);
      expect(result.results[0].score).toBe(0.95);
      expect(result.search_type).toBe('hybrid');
    });

    it('should handle search with filters', async () => {
      const request: HybridSearchRequest = {
        query: 'pasta',
        limit: 5,
        filters: {
          cuisine_type: 'Italian',
          difficulty: 'easy',
          max_prep_time: 20,
        },
      };

      const mockResponse = {
        data: {
          query: request.query,
          results: [],
          total: 0,
          search_type: 'hybrid' as const,
        },
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await searchService.hybrid(request);

      expect(apiClient.post).toHaveBeenCalledWith('/search', request, undefined);
      expect(result.total).toBe(0);
    });
  });

  describe('semantic', () => {
    it('should perform semantic search', async () => {
      const params = {
        query: 'creamy pasta',
        limit: 5,
      };

      const mockResponse = {
        data: [
          {
            recipe: mockRecipe,
            score: 0.92,
            distance: 0.08,
            match_type: 'semantic' as const,
          },
        ],
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await searchService.semantic(params);

      expect(apiClient.post).toHaveBeenCalledWith('/search/semantic', null, { params });
      expect(result).toHaveLength(1);
      expect(result[0].match_type).toBe('semantic');
      expect(result[0].score).toBe(0.92);
    });

    it('should use default limit', async () => {
      const params = { query: 'pasta' };

      const mockResponse = { data: [] };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      await searchService.semantic(params);

      expect(apiClient.post).toHaveBeenCalledWith('/search/semantic', null, { params });
    });
  });

  describe('filter', () => {
    it('should perform filter-based search', async () => {
      const params = {
        filters: {
          cuisine_type: 'Italian',
          difficulty: 'easy' as const,
          max_prep_time: 20,
          diet_types: ['vegetarian', 'vegan'],
        },
        limit: 10,
      };

      const mockResponse = {
        data: [
          {
            recipe: mockRecipe,
            score: 1.0,
            match_type: 'filter' as const,
          },
        ],
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await searchService.filter(params);

      expect(apiClient.post).toHaveBeenCalledWith('/search/filter', params.filters, {
        params: { limit: params.limit },
      });
      expect(result).toHaveLength(1);
      expect(result[0].match_type).toBe('filter');
      expect(result[0].score).toBe(1.0);
    });

    it('should handle empty results', async () => {
      const params = {
        filters: {
          cuisine_type: 'Mexican',
          difficulty: 'hard' as const,
        },
      };

      const mockResponse = { data: [] };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await searchService.filter(params);

      expect(result).toHaveLength(0);
    });
  });
});
