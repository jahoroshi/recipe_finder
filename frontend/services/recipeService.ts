/**
 * Recipe Service
 * API calls for recipe CRUD operations
 */

import { api } from './api.config';
import type {
  Recipe,
  RecipeCreate,
  RecipeUpdate,
  RecipeListParams,
  RecipeListResponse,
  SearchResult,
  BulkImportResponse,
} from '@/types';

/**
 * Recipe Service
 * All recipe-related API endpoints
 */
export const recipeService = {
  /**
   * List recipes with optional filtering and pagination
   * GET /api/recipes
   *
   * @param params - Filter and pagination parameters
   * @returns Paginated list of recipes
   *
   * @example
   * ```ts
   * const recipes = await recipeService.list({
   *   cuisine_type: 'Italian',
   *   difficulty: 'easy',
   *   max_prep_time: 30,
   *   page: 1,
   *   page_size: 20
   * });
   * ```
   */
  list: async (params?: RecipeListParams): Promise<RecipeListResponse> => {
    return api.get<RecipeListResponse>('/recipes', { params });
  },

  /**
   * Get a single recipe by ID
   * GET /api/recipes/:id
   *
   * @param id - Recipe UUID
   * @returns Recipe with all relationships (ingredients, categories, nutritional info)
   * @throws ApiError with 404 if recipe not found
   *
   * @example
   * ```ts
   * const recipe = await recipeService.getById('a1b2c3d4-e5f6-7890-abcd-ef1234567890');
   * ```
   */
  getById: async (id: string): Promise<Recipe> => {
    return api.get<Recipe>(`/recipes/${id}`);
  },

  /**
   * Create a new recipe
   * POST /api/recipes
   *
   * @param data - Recipe creation data
   * @returns Created recipe with generated ID and timestamps
   * @throws ApiError with 400 if validation fails or duplicate name
   *
   * @example
   * ```ts
   * const newRecipe = await recipeService.create({
   *   name: 'Pasta Carbonara',
   *   description: 'Classic Italian pasta dish',
   *   instructions: { steps: ['Cook pasta', 'Mix eggs and cheese', 'Combine'] },
   *   prep_time: 10,
   *   cook_time: 15,
   *   servings: 4,
   *   difficulty: 'medium',
   *   cuisine_type: 'Italian',
   *   ingredients: [
   *     { name: 'spaghetti', quantity: 400, unit: 'g' },
   *     { name: 'eggs', quantity: 3, unit: 'pieces' }
   *   ]
   * });
   * ```
   */
  create: async (data: RecipeCreate): Promise<Recipe> => {
    return api.post<Recipe>('/recipes', data);
  },

  /**
   * Update an existing recipe
   * PUT /api/recipes/:id
   *
   * Supports partial updates - only provided fields are updated.
   * Embedding is automatically regenerated if relevant fields change.
   *
   * @param id - Recipe UUID
   * @param data - Fields to update
   * @returns Updated recipe
   * @throws ApiError with 404 if recipe not found, 400 if validation fails
   *
   * @example
   * ```ts
   * const updated = await recipeService.update('recipe-id', {
   *   prep_time: 15,
   *   cook_time: 20,
   *   difficulty: 'hard'
   * });
   * ```
   */
  update: async (id: string, data: RecipeUpdate): Promise<Recipe> => {
    return api.put<Recipe>(`/recipes/${id}`, data);
  },

  /**
   * Delete a recipe (soft delete)
   * DELETE /api/recipes/:id
   *
   * Recipe is marked as deleted but not removed from database.
   * Will no longer appear in list/search results.
   *
   * @param id - Recipe UUID
   * @returns void (204 No Content)
   * @throws ApiError with 404 if recipe not found
   *
   * @example
   * ```ts
   * await recipeService.delete('recipe-id');
   * ```
   */
  delete: async (id: string): Promise<void> => {
    return api.delete<void>(`/recipes/${id}`);
  },

  /**
   * Find similar recipes using vector embeddings
   * GET /api/recipes/:id/similar
   *
   * Uses AI vector similarity to find recipes similar to the given recipe.
   * Results are ordered by similarity score (descending).
   *
   * @param id - Recipe UUID to find similar recipes for
   * @param limit - Maximum number of results (default: 10)
   * @returns Array of similar recipes with similarity scores
   * @throws ApiError with 404 if recipe not found
   *
   * @example
   * ```ts
   * const similar = await recipeService.findSimilar('recipe-id', 5);
   * similar.forEach(result => {
   *   console.log(`${result.recipe.name} - Score: ${result.score}`);
   * });
   * ```
   */
  findSimilar: async (id: string, limit: number = 10): Promise<SearchResult[]> => {
    return api.get<SearchResult[]>(`/recipes/${id}/similar`, {
      params: { limit },
    });
  },

  /**
   * Bulk import recipes from JSON file
   * POST /api/recipes/bulk
   *
   * Uploads a JSON file containing an array of recipes.
   * Processing happens in the background.
   *
   * @param file - JSON file containing array of recipes
   * @returns Job information
   * @throws ApiError with 400 if file is invalid
   *
   * @example
   * ```ts
   * const fileInput = document.querySelector('input[type="file"]');
   * const file = fileInput.files[0];
   * const result = await recipeService.bulkImport(file);
   * console.log(`Import started. Job ID: ${result.job_id}`);
   * ```
   */
  bulkImport: async (file: File): Promise<BulkImportResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post<BulkImportResponse>('/recipes/bulk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

/**
 * Export individual functions for tree-shaking
 */
export const {
  list: listRecipes,
  getById: getRecipeById,
  create: createRecipe,
  update: updateRecipe,
  delete: deleteRecipe,
  findSimilar: findSimilarRecipes,
  bulkImport: bulkImportRecipes,
} = recipeService;
