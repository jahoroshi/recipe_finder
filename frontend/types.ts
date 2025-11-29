/**
 * Type Definitions
 * Backend-compatible types for Recipe Management API
 */

// ============================================================================
// Core Entities
// ============================================================================

/**
 * Recipe difficulty levels
 */
export type RecipeDifficulty = 'easy' | 'medium' | 'hard';

/**
 * Ingredient in a recipe
 */
export interface Ingredient {
  id: string; // UUID
  recipe_id: string; // UUID
  name: string;
  quantity?: number;
  unit?: string;
  notes?: string;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

/**
 * Ingredient creation data (without ID and timestamps)
 */
export interface IngredientCreate {
  name: string;
  quantity?: number;
  unit?: string;
  notes?: string;
}

/**
 * Category for recipe classification
 */
export interface Category {
  id: string; // UUID
  name: string;
  slug: string;
  description?: string;
  parent_id?: string; // UUID
  children?: Category[];
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

/**
 * Nutritional information for a recipe
 */
export interface NutritionalInfo {
  id: string; // UUID
  recipe_id: string; // UUID
  calories?: number;
  protein_g?: number;
  carbohydrates_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sugar_g?: number;
  sodium_mg?: number;
  cholesterol_mg?: number;
  additional_info?: Record<string, any>;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

/**
 * Nutritional information creation data
 */
export interface NutritionalInfoCreate {
  calories?: number;
  protein_g?: number;
  carbohydrates_g?: number;
  fat_g?: number;
  fiber_g?: number;
  sugar_g?: number;
  sodium_mg?: number;
  cholesterol_mg?: number;
  additional_info?: Record<string, any>;
}

/**
 * Recipe instructions (structured data)
 */
export interface RecipeInstructions {
  steps: string[];
  [key: string]: any; // Allow additional fields
}

/**
 * Complete recipe model
 */
export interface Recipe {
  id: string; // UUID
  name: string;
  description?: string;
  instructions: RecipeInstructions;
  prep_time?: number; // minutes
  cook_time?: number; // minutes
  servings?: number;
  difficulty: RecipeDifficulty;
  cuisine_type?: string;
  diet_types: string[];
  embedding?: number[]; // 768-dimensional vector
  ingredients: Ingredient[];
  categories: Category[];
  nutritional_info?: NutritionalInfo;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
  deleted_at?: string; // ISO 8601 timestamp (soft delete)
}

/**
 * Recipe creation data
 */
export interface RecipeCreate {
  name: string;
  description?: string;
  instructions: RecipeInstructions;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  difficulty?: RecipeDifficulty;
  cuisine_type?: string;
  diet_types?: string[];
  ingredients?: IngredientCreate[];
  category_ids?: string[]; // UUIDs
  nutritional_info?: NutritionalInfoCreate;
}

/**
 * Recipe update data (all fields optional)
 */
export interface RecipeUpdate {
  name?: string;
  description?: string;
  instructions?: RecipeInstructions;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  difficulty?: RecipeDifficulty;
  cuisine_type?: string;
  diet_types?: string[];
  category_ids?: string[];
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Paginated response wrapper
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/**
 * Recipe list response
 */
export type RecipeListResponse = PaginatedResponse<Recipe>;

/**
 * Search result with scoring
 */
export interface SearchResult {
  recipe: Recipe;
  score: number;
  distance?: number;
  match_type: 'semantic' | 'filter' | 'hybrid';
}

/**
 * Parsed query from AI
 */
export interface ParsedQuery {
  original_query: string;
  ingredients?: string[];
  cuisine_type?: string;
  diet_types?: string[];
  max_prep_time?: number;
  max_cook_time?: number;
  difficulty?: RecipeDifficulty;
  semantic_query?: string;
}

/**
 * Hybrid search response
 */
export interface HybridSearchResponse {
  query: string;
  parsed_query?: ParsedQuery;
  results: SearchResult[];
  total: number;
  search_type: 'hybrid' | 'semantic' | 'filter';
  metadata?: {
    semantic_results?: number;
    filter_results?: number;
    merged_results?: number;
    final_results?: number;
  };
}

/**
 * Bulk import response
 */
export interface BulkImportResponse {
  job_id: string;
  status: string;
  total_recipes: number;
  message: string;
}

/**
 * Health check response
 */
export interface HealthResponse {
  status: 'healthy' | 'unhealthy' | 'degraded';
  version: string;
  service: string;
}

/**
 * Detailed health check response
 */
export interface DetailedHealthResponse extends HealthResponse {
  components: {
    [key: string]: {
      status: 'healthy' | 'unhealthy';
      message?: string;
    };
  };
}

// ============================================================================
// Request Parameter Types
// ============================================================================

/**
 * Recipe list filter parameters
 */
export interface RecipeListParams {
  page?: number;
  page_size?: number;
  name?: string;
  cuisine_type?: string;
  difficulty?: RecipeDifficulty;
  diet_types?: string[];
  category_ids?: string[];
  min_prep_time?: number;
  max_prep_time?: number;
  min_cook_time?: number;
  max_cook_time?: number;
  min_servings?: number;
  max_servings?: number;
}

/**
 * Search filter criteria
 */
export interface SearchFilters {
  cuisine_type?: string;
  difficulty?: RecipeDifficulty;
  diet_types?: string[];
  max_prep_time?: number;
  max_cook_time?: number;
  min_servings?: number;
  max_servings?: number;
  category_ids?: string[];
}

/**
 * Hybrid search request
 */
export interface HybridSearchRequest {
  query: string;
  limit?: number;
  use_semantic?: boolean;
  use_filters?: boolean;
  use_reranking?: boolean;
  filters?: SearchFilters;
}

/**
 * Semantic search parameters
 */
export interface SemanticSearchParams {
  query: string;
  limit?: number;
}

/**
 * Filter search parameters
 */
export interface FilterSearchParams {
  filters: SearchFilters;
  limit?: number;
}

// ============================================================================
// Legacy Types (for backward compatibility)
// ============================================================================

/**
 * @deprecated Use Recipe instead
 * Legacy recipe type from prototype
 */
export interface LegacyRecipe {
  id: number;
  name: string;
  ingredients: string[];
  instructions: string;
  image: string;
}

/**
 * @deprecated Use RecipeCreate instead
 */
export type NewRecipe = Omit<LegacyRecipe, 'id'>;
