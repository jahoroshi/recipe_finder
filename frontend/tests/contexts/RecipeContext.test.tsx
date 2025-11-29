/**
 * RecipeContext Tests
 *
 * Unit tests for RecipeContext provider and hook.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { toast } from 'react-toastify';
import { RecipeProvider, useRecipeContext } from '@/contexts/RecipeContext';
import { recipeService } from '@/services';
import { createQueryWrapper, createTestQueryClient } from './test-utils';
import type { Recipe, RecipeCreate, RecipeUpdate } from '@/types';

// Mock services
vi.mock('@/services', () => ({
  recipeService: {
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    bulkImport: vi.fn(),
  },
}));

// Mock toast notifications
vi.mock('react-toastify', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// ============================================================================
// Test Data
// ============================================================================

const mockRecipe: Recipe = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'Test Recipe',
  description: 'A test recipe',
  instructions: { steps: ['Step 1', 'Step 2'] },
  difficulty: 'medium',
  diet_types: ['vegetarian'],
  ingredients: [],
  categories: [],
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
};

const mockRecipeCreate: RecipeCreate = {
  name: 'New Recipe',
  description: 'A new recipe',
  instructions: { steps: ['Step 1'] },
  difficulty: 'easy',
  diet_types: [],
};

const mockRecipeUpdate: RecipeUpdate = {
  name: 'Updated Recipe',
};

// ============================================================================
// Tests
// ============================================================================

describe('RecipeContext', () => {
  let queryClient: ReturnType<typeof createTestQueryClient>;

  beforeEach(() => {
    queryClient = createTestQueryClient();
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  // Helper to create wrapper with both QueryClient and RecipeProvider
  const createWrapper = () => {
    const QueryWrapper = createQueryWrapper(queryClient);
    return ({ children }: { children: React.ReactNode }) => (
      <QueryWrapper>
        <RecipeProvider>{children}</RecipeProvider>
      </QueryWrapper>
    );
  };

  describe('useRecipeContext hook', () => {
    it('should throw error when used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useRecipeContext());
      }).toThrow('useRecipeContext must be used within RecipeProvider');

      consoleSpy.mockRestore();
    });

    it('should provide context value when used inside provider', () => {
      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      // Should have access to all context methods
      expect(result.current).toHaveProperty('createRecipe');
      expect(result.current).toHaveProperty('updateRecipe');
      expect(result.current).toHaveProperty('deleteRecipe');
      expect(result.current).toHaveProperty('bulkImport');
      expect(result.current).toHaveProperty('invalidateRecipe');
      expect(result.current).toHaveProperty('invalidateRecipeList');
      expect(result.current).toHaveProperty('invalidateAll');
    });
  });

  describe('createRecipe', () => {
    it('should create recipe successfully', async () => {
      vi.mocked(recipeService.create).mockResolvedValue(mockRecipe);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      let createdRecipe: Recipe | undefined;

      await act(async () => {
        createdRecipe = await result.current.createRecipe(mockRecipeCreate);
      });

      expect(createdRecipe).toEqual(mockRecipe);
      expect(recipeService.create).toHaveBeenCalledWith(mockRecipeCreate);
      expect(toast.success).toHaveBeenCalledWith('Recipe created successfully!');
    });

    it('should handle create error', async () => {
      const error = new Error('Creation failed');
      vi.mocked(recipeService.create).mockRejectedValue(error);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      await act(async () => {
        try {
          await result.current.createRecipe(mockRecipeCreate);
        } catch (e) {
          // Error is expected
        }
      });

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Failed to create recipe: Creation failed');
      });
    });

    it('should update loading state during creation', async () => {
      vi.mocked(recipeService.create).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockRecipe), 100))
      );

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      expect(result.current.isCreating).toBe(false);

      act(() => {
        result.current.createRecipe(mockRecipeCreate);
      });

      await waitFor(() => {
        expect(result.current.isCreating).toBe(true);
      });

      await waitFor(() => {
        expect(result.current.isCreating).toBe(false);
      });
    });
  });

  describe('updateRecipe', () => {
    it('should update recipe successfully', async () => {
      const updatedRecipe = { ...mockRecipe, ...mockRecipeUpdate };
      vi.mocked(recipeService.update).mockResolvedValue(updatedRecipe);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      let updated: Recipe | undefined;

      await act(async () => {
        updated = await result.current.updateRecipe(mockRecipe.id, mockRecipeUpdate);
      });

      expect(updated).toEqual(updatedRecipe);
      expect(recipeService.update).toHaveBeenCalledWith(mockRecipe.id, mockRecipeUpdate);
      expect(toast.success).toHaveBeenCalledWith('Recipe updated successfully!');
    });

    it('should handle update error', async () => {
      const error = new Error('Update failed');
      vi.mocked(recipeService.update).mockRejectedValue(error);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      await act(async () => {
        try {
          await result.current.updateRecipe(mockRecipe.id, mockRecipeUpdate);
        } catch (e) {
          // Error is expected
        }
      });

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Failed to update recipe: Update failed');
      });
    });

    it('should perform optimistic update', async () => {
      const updatedRecipe = { ...mockRecipe, ...mockRecipeUpdate };
      vi.mocked(recipeService.update).mockResolvedValue(updatedRecipe);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      // Pre-populate cache with existing recipe after hook is rendered
      act(() => {
        queryClient.setQueryData(['recipe', mockRecipe.id], mockRecipe);
      });

      await act(async () => {
        await result.current.updateRecipe(mockRecipe.id, mockRecipeUpdate);
      });

      // Verify cache was updated
      const cachedRecipe = queryClient.getQueryData<Recipe>(['recipe', mockRecipe.id]);
      expect(cachedRecipe?.name).toBe('Updated Recipe');
    });
  });

  describe('deleteRecipe', () => {
    it('should delete recipe successfully', async () => {
      vi.mocked(recipeService.delete).mockResolvedValue();

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      await act(async () => {
        await result.current.deleteRecipe(mockRecipe.id);
      });

      expect(recipeService.delete).toHaveBeenCalledWith(mockRecipe.id);
      expect(toast.success).toHaveBeenCalledWith('Recipe deleted successfully!');
    });

    it('should handle delete error', async () => {
      const error = new Error('Delete failed');
      vi.mocked(recipeService.delete).mockRejectedValue(error);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      await act(async () => {
        try {
          await result.current.deleteRecipe(mockRecipe.id);
        } catch (e) {
          // Error is expected
        }
      });

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Failed to delete recipe: Delete failed');
      });
    });
  });

  describe('bulkImport', () => {
    it('should import recipes successfully', async () => {
      const mockResponse = {
        job_id: 'job-123',
        status: 'processing',
        total_recipes: 10,
        message: 'Import started',
      };

      vi.mocked(recipeService.bulkImport).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      const mockFile = new File(['{}'], 'recipes.json', { type: 'application/json' });

      await act(async () => {
        await result.current.bulkImport(mockFile);
      });

      expect(recipeService.bulkImport).toHaveBeenCalledWith(mockFile);
      expect(toast.success).toHaveBeenCalledWith(
        'Bulk import started! Job ID: job-123. Total recipes: 10'
      );
    });

    it('should handle import error', async () => {
      const error = new Error('Import failed');
      vi.mocked(recipeService.bulkImport).mockRejectedValue(error);

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      const mockFile = new File(['{}'], 'recipes.json', { type: 'application/json' });

      await act(async () => {
        try {
          await result.current.bulkImport(mockFile);
        } catch (e) {
          // Error is expected
        }
      });

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith('Failed to import recipes: Import failed');
      });
    });
  });

  describe('cache invalidation', () => {
    it('should invalidate specific recipe', async () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      act(() => {
        result.current.invalidateRecipe(mockRecipe.id);
      });

      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['recipe', mockRecipe.id] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['recipes'] });
    });

    it('should invalidate recipe list', async () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      act(() => {
        result.current.invalidateRecipeList();
      });

      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['recipes'] });
    });

    it('should invalidate all caches', async () => {
      const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries');

      const { result } = renderHook(() => useRecipeContext(), { wrapper: createWrapper() });

      act(() => {
        result.current.invalidateAll();
      });

      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['recipe'] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['recipes'] });
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['search'] });
    });
  });
});
