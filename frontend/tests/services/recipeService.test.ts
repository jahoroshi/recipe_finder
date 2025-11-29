/**
 * Recipe Service Tests
 * Unit tests for recipe API service
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { recipeService } from '@/services/recipeService';
import { apiClient } from '@/services/api.config';
import type { Recipe, RecipeCreate } from '@/types';

// Mock axios
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

describe('Recipe Service', () => {
  const mockRecipe: Recipe = {
    id: 'recipe-123',
    name: 'Test Recipe',
    description: 'Test description',
    instructions: { steps: ['Step 1', 'Step 2'] },
    prep_time: 10,
    cook_time: 15,
    servings: 4,
    difficulty: 'medium',
    cuisine_type: 'Italian',
    diet_types: ['vegetarian'],
    ingredients: [
      {
        id: 'ingredient-1',
        recipe_id: 'recipe-123',
        name: 'pasta',
        quantity: 400,
        unit: 'g',
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z',
      },
    ],
    categories: [],
    created_at: '2025-11-15T12:00:00Z',
    updated_at: '2025-11-15T12:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('list', () => {
    it('should fetch recipes with filters', async () => {
      const mockResponse = {
        data: {
          items: [mockRecipe],
          total: 1,
          page: 1,
          page_size: 20,
          pages: 1,
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      const params = {
        cuisine_type: 'Italian',
        difficulty: 'easy' as const,
        max_prep_time: 30,
        page: 1,
        page_size: 20,
      };

      const result = await recipeService.list(params);

      expect(apiClient.get).toHaveBeenCalledWith('/recipes', { params });
      expect(result).toEqual(mockResponse.data);
      expect(result.items).toHaveLength(1);
      expect(result.items[0].name).toBe('Test Recipe');
    });

    it('should fetch recipes without filters', async () => {
      const mockResponse = {
        data: {
          items: [mockRecipe],
          total: 1,
          page: 1,
          page_size: 50,
          pages: 1,
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      const result = await recipeService.list();

      expect(apiClient.get).toHaveBeenCalledWith('/recipes', { params: undefined });
      expect(result.items).toHaveLength(1);
    });
  });

  describe('getById', () => {
    it('should fetch a single recipe', async () => {
      const mockResponse = { data: mockRecipe };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      const result = await recipeService.getById('recipe-123');

      expect(apiClient.get).toHaveBeenCalledWith('/recipes/recipe-123', undefined);
      expect(result).toEqual(mockRecipe);
      expect(result.name).toBe('Test Recipe');
    });

    it('should throw error for non-existent recipe', async () => {
      vi.mocked(apiClient.get).mockRejectedValueOnce({
        response: {
          status: 404,
          data: { message: 'Recipe not found' },
        },
      });

      await expect(recipeService.getById('non-existent')).rejects.toThrow();
    });
  });

  describe('create', () => {
    it('should create a new recipe', async () => {
      const createData: RecipeCreate = {
        name: 'New Recipe',
        description: 'New description',
        instructions: { steps: ['Cook it'] },
        prep_time: 5,
        cook_time: 10,
        servings: 2,
        difficulty: 'easy',
        cuisine_type: 'Italian',
        ingredients: [
          { name: 'pasta', quantity: 200, unit: 'g' },
        ],
      };

      const mockResponse = { data: { ...mockRecipe, ...createData } };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await recipeService.create(createData);

      expect(apiClient.post).toHaveBeenCalledWith('/recipes', createData, undefined);
      expect(result.name).toBe('New Recipe');
    });

    it('should throw error for duplicate name', async () => {
      vi.mocked(apiClient.post).mockRejectedValueOnce({
        response: {
          status: 400,
          data: { message: 'Recipe name already exists' },
        },
      });

      const createData: RecipeCreate = {
        name: 'Duplicate',
        instructions: { steps: [] },
      };

      await expect(recipeService.create(createData)).rejects.toThrow();
    });
  });

  describe('update', () => {
    it('should update a recipe', async () => {
      const updateData = {
        prep_time: 20,
        cook_time: 30,
      };

      const updatedRecipe = { ...mockRecipe, ...updateData };
      const mockResponse = { data: updatedRecipe };

      vi.mocked(apiClient.put).mockResolvedValueOnce(mockResponse);

      const result = await recipeService.update('recipe-123', updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/recipes/recipe-123', updateData, undefined);
      expect(result.prep_time).toBe(20);
      expect(result.cook_time).toBe(30);
    });
  });

  describe('delete', () => {
    it('should delete a recipe', async () => {
      const mockResponse = { data: undefined };

      vi.mocked(apiClient.delete).mockResolvedValueOnce(mockResponse);

      await recipeService.delete('recipe-123');

      expect(apiClient.delete).toHaveBeenCalledWith('/recipes/recipe-123', undefined);
    });
  });

  describe('findSimilar', () => {
    it('should find similar recipes', async () => {
      const mockResponse = {
        data: [
          {
            recipe: mockRecipe,
            score: 0.95,
            distance: 0.05,
            match_type: 'semantic' as const,
          },
        ],
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      const result = await recipeService.findSimilar('recipe-123', 5);

      expect(apiClient.get).toHaveBeenCalledWith('/recipes/recipe-123/similar', {
        params: { limit: 5 },
      });
      expect(result).toHaveLength(1);
      expect(result[0].score).toBe(0.95);
    });

    it('should use default limit', async () => {
      const mockResponse = { data: [] };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      await recipeService.findSimilar('recipe-123');

      expect(apiClient.get).toHaveBeenCalledWith('/recipes/recipe-123/similar', {
        params: { limit: 10 },
      });
    });
  });

  describe('bulkImport', () => {
    it('should upload and import recipes from file', async () => {
      const mockFile = new File(['[]'], 'recipes.json', { type: 'application/json' });

      const mockResponse = {
        data: {
          job_id: 'job-123',
          status: 'accepted',
          total_recipes: 10,
          message: 'Import started',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const result = await recipeService.bulkImport(mockFile);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/recipes/bulk',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      expect(result.job_id).toBe('job-123');
      expect(result.total_recipes).toBe(10);
    });
  });
});
