/**
 * Services Index
 * Central export point for all API services
 */

// API Configuration
export { api, apiClient, ApiError } from './api.config';
export type { AxiosRequestConfig, AxiosResponse } from './api.config';

// Recipe Service
export { recipeService } from './recipeService';
export {
  listRecipes,
  getRecipeById,
  createRecipe,
  updateRecipe,
  deleteRecipe,
  findSimilarRecipes,
  bulkImportRecipes,
} from './recipeService';

// Search Service
export { searchService } from './searchService';
export {
  hybridSearch,
  semanticSearch,
  filterSearch,
} from './searchService';

// Health Service
export { healthService } from './healthService';
export {
  checkHealth,
  checkDetailedHealth,
  pingApi,
} from './healthService';
