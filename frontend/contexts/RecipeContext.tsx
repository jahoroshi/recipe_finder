/**
 * Recipe Context
 *
 * Provides global state management for recipe data and CRUD operations.
 * Manages recipe cache, optimistic updates, and mutation states.
 */

import React, { createContext, useContext, useCallback, ReactNode } from 'react';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { recipeService } from '@/services';
import type { Recipe, RecipeCreate, RecipeUpdate } from '@/types';

// ============================================================================
// Types
// ============================================================================

interface RecipeContextValue {
  // CRUD Operations
  createRecipe: (data: RecipeCreate) => Promise<Recipe>;
  updateRecipe: (id: string, data: RecipeUpdate) => Promise<Recipe>;
  deleteRecipe: (id: string) => Promise<void>;

  // Bulk Operations
  bulkImport: (file: File) => Promise<void>;

  // Cache Management
  invalidateRecipe: (id: string) => void;
  invalidateRecipeList: () => void;
  invalidateAll: () => void;

  // Mutation States
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  isImporting: boolean;
}

interface RecipeProviderProps {
  children: ReactNode;
}

// ============================================================================
// Context
// ============================================================================

const RecipeContext = createContext<RecipeContextValue | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

export const RecipeProvider: React.FC<RecipeProviderProps> = ({ children }) => {
  const queryClient = useQueryClient();

  // ============================================================================
  // Cache Invalidation Helpers
  // ============================================================================

  const invalidateRecipe = useCallback((id: string) => {
    queryClient.invalidateQueries({ queryKey: ['recipe', id] });
    queryClient.invalidateQueries({ queryKey: ['recipes'] });
  }, [queryClient]);

  const invalidateRecipeList = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['recipes'] });
  }, [queryClient]);

  const invalidateAll = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['recipe'] });
    queryClient.invalidateQueries({ queryKey: ['recipes'] });
    queryClient.invalidateQueries({ queryKey: ['search'] });
  }, [queryClient]);

  // ============================================================================
  // Create Recipe Mutation
  // ============================================================================

  const createMutation = useMutation({
    mutationFn: (data: RecipeCreate) => recipeService.create(data),
    onSuccess: (newRecipe) => {
      // Invalidate recipe list to refetch with new recipe
      invalidateRecipeList();

      // Pre-populate cache for the new recipe
      queryClient.setQueryData(['recipe', newRecipe.id], newRecipe);

      toast.success('Recipe created successfully!');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create recipe: ${error.message}`);
    },
  });

  // ============================================================================
  // Update Recipe Mutation
  // ============================================================================

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: RecipeUpdate }) =>
      recipeService.update(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['recipe', id] });

      // Snapshot previous value
      const previousRecipe = queryClient.getQueryData<Recipe>(['recipe', id]);

      // Optimistically update cache
      if (previousRecipe) {
        queryClient.setQueryData<Recipe>(['recipe', id], {
          ...previousRecipe,
          ...data,
          updated_at: new Date().toISOString(),
        });
      }

      return { previousRecipe };
    },
    onSuccess: (updatedRecipe) => {
      // Update cache with server response
      queryClient.setQueryData(['recipe', updatedRecipe.id], updatedRecipe);
      invalidateRecipeList();

      toast.success('Recipe updated successfully!');
    },
    onError: (error: Error, { id }, context) => {
      // Rollback on error
      if (context?.previousRecipe) {
        queryClient.setQueryData(['recipe', id], context.previousRecipe);
      }

      toast.error(`Failed to update recipe: ${error.message}`);
    },
    onSettled: (_, __, { id }) => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['recipe', id] });
    },
  });

  // ============================================================================
  // Delete Recipe Mutation
  // ============================================================================

  const deleteMutation = useMutation({
    mutationFn: (id: string) => recipeService.delete(id),
    onMutate: async (id) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['recipe', id] });
      await queryClient.cancelQueries({ queryKey: ['recipes'] });

      // Snapshot previous values
      const previousRecipe = queryClient.getQueryData<Recipe>(['recipe', id]);

      // Optimistically remove from cache
      queryClient.removeQueries({ queryKey: ['recipe', id] });

      return { previousRecipe };
    },
    onSuccess: () => {
      invalidateRecipeList();
      toast.success('Recipe deleted successfully!');
    },
    onError: (error: Error, id, context) => {
      // Rollback on error
      if (context?.previousRecipe) {
        queryClient.setQueryData(['recipe', id], context.previousRecipe);
      }

      toast.error(`Failed to delete recipe: ${error.message}`);
    },
  });

  // ============================================================================
  // Bulk Import Mutation
  // ============================================================================

  const bulkImportMutation = useMutation({
    mutationFn: (file: File) => recipeService.bulkImport(file),
    onSuccess: (response) => {
      invalidateAll();
      toast.success(`Bulk import started! Job ID: ${response.job_id}. Total recipes: ${response.total_recipes}`);
    },
    onError: (error: Error) => {
      toast.error(`Failed to import recipes: ${error.message}`);
    },
  });

  // ============================================================================
  // Public API
  // ============================================================================

  const createRecipe = useCallback(
    async (data: RecipeCreate): Promise<Recipe> => {
      return createMutation.mutateAsync(data);
    },
    [createMutation]
  );

  const updateRecipe = useCallback(
    async (id: string, data: RecipeUpdate): Promise<Recipe> => {
      return updateMutation.mutateAsync({ id, data });
    },
    [updateMutation]
  );

  const deleteRecipe = useCallback(
    async (id: string): Promise<void> => {
      await deleteMutation.mutateAsync(id);
    },
    [deleteMutation]
  );

  const bulkImport = useCallback(
    async (file: File): Promise<void> => {
      await bulkImportMutation.mutateAsync(file);
    },
    [bulkImportMutation]
  );

  // ============================================================================
  // Context Value
  // ============================================================================

  const value: RecipeContextValue = {
    // CRUD Operations
    createRecipe,
    updateRecipe,
    deleteRecipe,

    // Bulk Operations
    bulkImport,

    // Cache Management
    invalidateRecipe,
    invalidateRecipeList,
    invalidateAll,

    // Mutation States
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isImporting: bulkImportMutation.isPending,
  };

  return (
    <RecipeContext.Provider value={value}>
      {children}
    </RecipeContext.Provider>
  );
};

// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access recipe context
 * @throws {Error} If used outside RecipeProvider
 */
export const useRecipeContext = (): RecipeContextValue => {
  const context = useContext(RecipeContext);

  if (context === undefined) {
    throw new Error('useRecipeContext must be used within RecipeProvider');
  }

  return context;
};

// Export context for testing purposes
export { RecipeContext };
