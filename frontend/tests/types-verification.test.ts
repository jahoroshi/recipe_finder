/**
 * Type Verification Tests
 * Ensures TypeScript models match backend API schema exactly
 */

import { describe, it, expect } from 'vitest';
import type {
  Recipe,
  RecipeCreate,
  RecipeUpdate,
  Ingredient,
  IngredientCreate,
  Category,
  NutritionalInfo,
  NutritionalInfoCreate,
  RecipeInstructions,
  RecipeDifficulty,
  PaginatedResponse,
  SearchResult,
  ParsedQuery,
  HybridSearchResponse,
  HybridSearchRequest,
  RecipeListParams,
  SearchFilters,
  HealthResponse,
  DetailedHealthResponse,
} from '../types';

describe('Type Verification', () => {
  describe('Core Entity Types', () => {
    it('should validate complete Recipe object', () => {
      const recipe: Recipe = {
        id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        name: 'Pasta Carbonara',
        description: 'Classic Italian pasta dish',
        instructions: {
          steps: [
            'Cook pasta',
            'Fry pancetta',
            'Mix eggs with cheese',
            'Combine and serve'
          ]
        },
        prep_time: 10,
        cook_time: 15,
        servings: 4,
        difficulty: 'medium',
        cuisine_type: 'Italian',
        diet_types: ['vegetarian'],
        embedding: new Array(768).fill(0.5),
        ingredients: [
          {
            id: 'ing-uuid-1',
            recipe_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            name: 'spaghetti',
            quantity: 400,
            unit: 'g',
            notes: 'Use good quality pasta',
            created_at: '2025-11-15T12:00:00Z',
            updated_at: '2025-11-15T12:00:00Z'
          }
        ],
        categories: [
          {
            id: 'cat-uuid-1',
            name: 'Pasta',
            slug: 'pasta',
            description: 'Pasta dishes',
            parent_id: undefined,
            children: [],
            created_at: '2025-11-15T12:00:00Z',
            updated_at: '2025-11-15T12:00:00Z'
          }
        ],
        nutritional_info: {
          id: 'nut-uuid-1',
          recipe_id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
          calories: 450,
          protein_g: 18,
          carbohydrates_g: 55,
          fat_g: 16,
          fiber_g: 3,
          sugar_g: 2,
          sodium_mg: 650,
          cholesterol_mg: 185,
          additional_info: {},
          created_at: '2025-11-15T12:00:00Z',
          updated_at: '2025-11-15T12:00:00Z'
        },
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z',
        deleted_at: undefined
      };

      expect(recipe.id).toBe('a1b2c3d4-e5f6-7890-abcd-ef1234567890');
      expect(recipe.name).toBe('Pasta Carbonara');
      expect(recipe.difficulty).toBe('medium');
      expect(recipe.ingredients).toHaveLength(1);
      expect(recipe.categories).toHaveLength(1);
      expect(recipe.embedding).toHaveLength(768);
    });

    it('should validate RecipeCreate request', () => {
      const createData: RecipeCreate = {
        name: 'New Recipe',
        description: 'Test recipe',
        instructions: { steps: ['Step 1', 'Step 2'] },
        prep_time: 10,
        cook_time: 20,
        servings: 4,
        difficulty: 'easy',
        cuisine_type: 'Italian',
        diet_types: ['vegetarian', 'gluten-free'],
        ingredients: [
          {
            name: 'tomatoes',
            quantity: 500,
            unit: 'g',
            notes: 'Fresh tomatoes'
          }
        ],
        category_ids: ['cat-uuid-1', 'cat-uuid-2'],
        nutritional_info: {
          calories: 350,
          protein_g: 15,
          carbohydrates_g: 45,
          fat_g: 12
        }
      };

      expect(createData.name).toBe('New Recipe');
      expect(createData.difficulty).toBe('easy');
      expect(createData.ingredients).toHaveLength(1);
      expect(createData.category_ids).toHaveLength(2);
    });

    it('should validate RecipeUpdate with partial fields', () => {
      const updateData: RecipeUpdate = {
        name: 'Updated Name',
        difficulty: 'hard'
      };

      expect(updateData.name).toBe('Updated Name');
      expect(updateData.difficulty).toBe('hard');
      // Other fields are optional
      expect(updateData.description).toBeUndefined();
    });

    it('should validate Ingredient with all fields', () => {
      const ingredient: Ingredient = {
        id: 'ing-uuid',
        recipe_id: 'recipe-uuid',
        name: 'flour',
        quantity: 500,
        unit: 'g',
        notes: 'All-purpose flour',
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z'
      };

      expect(ingredient.id).toBe('ing-uuid');
      expect(ingredient.quantity).toBe(500);
      expect(ingredient.unit).toBe('g');
    });

    it('should validate IngredientCreate', () => {
      const ingredientCreate: IngredientCreate = {
        name: 'sugar',
        quantity: 100,
        unit: 'g',
        notes: 'White granulated sugar'
      };

      expect(ingredientCreate.name).toBe('sugar');
    });

    it('should validate hierarchical Category', () => {
      const parentCategory: Category = {
        id: 'parent-uuid',
        name: 'Main Dishes',
        slug: 'main-dishes',
        description: 'Main course recipes',
        parent_id: undefined,
        children: [
          {
            id: 'child-uuid',
            name: 'Pasta',
            slug: 'pasta',
            description: 'Pasta dishes',
            parent_id: 'parent-uuid',
            children: [],
            created_at: '2025-11-15T12:00:00Z',
            updated_at: '2025-11-15T12:00:00Z'
          }
        ],
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z'
      };

      expect(parentCategory.children).toHaveLength(1);
      expect(parentCategory.children![0].parent_id).toBe('parent-uuid');
    });

    it('should validate NutritionalInfo', () => {
      const nutrition: NutritionalInfo = {
        id: 'nut-uuid',
        recipe_id: 'recipe-uuid',
        calories: 450,
        protein_g: 18,
        carbohydrates_g: 55,
        fat_g: 16,
        fiber_g: 3,
        sugar_g: 2,
        sodium_mg: 650,
        cholesterol_mg: 185,
        additional_info: { vitamin_c: '10mg' },
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z'
      };

      expect(nutrition.calories).toBe(450);
      expect(nutrition.additional_info).toEqual({ vitamin_c: '10mg' });
    });

    it('should validate RecipeInstructions structure', () => {
      const instructions: RecipeInstructions = {
        steps: ['Step 1', 'Step 2', 'Step 3'],
        tips: 'Useful tip',
        warnings: 'Safety warning'
      };

      expect(instructions.steps).toHaveLength(3);
      expect(instructions.tips).toBe('Useful tip');
    });

    it('should validate RecipeDifficulty enum', () => {
      const difficulties: RecipeDifficulty[] = ['easy', 'medium', 'hard'];

      expect(difficulties).toContain('easy');
      expect(difficulties).toContain('medium');
      expect(difficulties).toContain('hard');
    });
  });

  describe('Response Types', () => {
    it('should validate PaginatedResponse', () => {
      const paginatedRecipes: PaginatedResponse<Recipe> = {
        items: [],
        total: 100,
        page: 2,
        page_size: 20,
        pages: 5
      };

      expect(paginatedRecipes.total).toBe(100);
      expect(paginatedRecipes.pages).toBe(5);
    });

    it('should validate SearchResult', () => {
      const searchResult: SearchResult = {
        recipe: {
          id: 'recipe-uuid',
          name: 'Test Recipe',
          instructions: { steps: ['Step 1'] },
          difficulty: 'easy',
          diet_types: [],
          ingredients: [],
          categories: [],
          created_at: '2025-11-15T12:00:00Z',
          updated_at: '2025-11-15T12:00:00Z'
        },
        score: 0.95,
        distance: 0.05,
        match_type: 'hybrid'
      };

      expect(searchResult.score).toBe(0.95);
      expect(searchResult.match_type).toBe('hybrid');
    });

    it('should validate ParsedQuery', () => {
      const parsedQuery: ParsedQuery = {
        original_query: 'quick vegetarian pasta under 30 minutes',
        ingredients: ['pasta'],
        cuisine_type: 'Italian',
        diet_types: ['vegetarian'],
        max_prep_time: 30,
        max_cook_time: undefined,
        difficulty: 'easy',
        semantic_query: 'quick easy pasta'
      };

      expect(parsedQuery.ingredients).toContain('pasta');
      expect(parsedQuery.max_prep_time).toBe(30);
    });

    it('should validate HybridSearchResponse', () => {
      const searchResponse: HybridSearchResponse = {
        query: 'quick vegetarian pasta',
        parsed_query: {
          original_query: 'quick vegetarian pasta',
          ingredients: ['pasta'],
          diet_types: ['vegetarian']
        },
        results: [],
        total: 15,
        search_type: 'hybrid',
        metadata: {
          semantic_results: 8,
          filter_results: 10,
          merged_results: 15,
          final_results: 15
        }
      };

      expect(searchResponse.total).toBe(15);
      expect(searchResponse.search_type).toBe('hybrid');
      expect(searchResponse.metadata?.semantic_results).toBe(8);
    });

    it('should validate HealthResponse', () => {
      const health: HealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        service: 'Recipe Management API'
      };

      expect(health.status).toBe('healthy');
      expect(health.version).toBe('1.0.0');
    });

    it('should validate DetailedHealthResponse', () => {
      const detailedHealth: DetailedHealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        service: 'Recipe Management API',
        components: {
          database: {
            status: 'healthy',
            message: 'Connected'
          },
          gemini_api: {
            status: 'healthy',
            message: 'API key configured'
          }
        }
      };

      expect(detailedHealth.components.database.status).toBe('healthy');
      expect(detailedHealth.components.gemini_api.status).toBe('healthy');
    });
  });

  describe('Request Parameter Types', () => {
    it('should validate RecipeListParams', () => {
      const params: RecipeListParams = {
        page: 1,
        page_size: 20,
        name: 'pasta',
        cuisine_type: 'Italian',
        difficulty: 'easy',
        diet_types: ['vegetarian'],
        category_ids: ['cat-uuid-1'],
        min_prep_time: 10,
        max_prep_time: 30,
        min_cook_time: 15,
        max_cook_time: 45,
        min_servings: 2,
        max_servings: 6
      };

      expect(params.page).toBe(1);
      expect(params.cuisine_type).toBe('Italian');
      expect(params.diet_types).toContain('vegetarian');
    });

    it('should validate SearchFilters', () => {
      const filters: SearchFilters = {
        cuisine_type: 'Italian',
        difficulty: 'medium',
        diet_types: ['vegetarian', 'gluten-free'],
        max_prep_time: 30,
        max_cook_time: 60,
        min_servings: 2,
        max_servings: 4,
        category_ids: ['cat-uuid-1', 'cat-uuid-2']
      };

      expect(filters.difficulty).toBe('medium');
      expect(filters.diet_types).toHaveLength(2);
    });

    it('should validate HybridSearchRequest', () => {
      const searchRequest: HybridSearchRequest = {
        query: 'quick vegetarian pasta',
        limit: 10,
        use_semantic: true,
        use_filters: true,
        use_reranking: true,
        filters: {
          cuisine_type: 'Italian',
          max_prep_time: 30,
          diet_types: ['vegetarian']
        }
      };

      expect(searchRequest.query).toBe('quick vegetarian pasta');
      expect(searchRequest.limit).toBe(10);
      expect(searchRequest.use_semantic).toBe(true);
    });
  });

  describe('Type Safety Checks', () => {
    it('should enforce UUID string type for IDs', () => {
      const recipe: Recipe = {
        id: 'uuid-string', // Must be string, not number
        name: 'Test',
        instructions: { steps: [] },
        difficulty: 'easy',
        diet_types: [],
        ingredients: [],
        categories: [],
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z'
      };

      expect(typeof recipe.id).toBe('string');
    });

    it('should enforce Ingredient as object, not string', () => {
      const ingredient: Ingredient = {
        id: 'ing-uuid',
        recipe_id: 'recipe-uuid',
        name: 'flour',
        quantity: 500,
        unit: 'g',
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z'
      };

      expect(typeof ingredient).toBe('object');
      expect(ingredient.name).toBe('flour');
      expect(ingredient.quantity).toBe(500);
    });

    it('should enforce RecipeInstructions as object, not string', () => {
      const instructions: RecipeInstructions = {
        steps: ['Step 1', 'Step 2']
      };

      expect(typeof instructions).toBe('object');
      expect(Array.isArray(instructions.steps)).toBe(true);
    });

    it('should allow optional fields to be undefined', () => {
      const recipe: Recipe = {
        id: 'uuid',
        name: 'Minimal Recipe',
        instructions: { steps: ['Cook'] },
        difficulty: 'easy',
        diet_types: [],
        ingredients: [],
        categories: [],
        // These are optional
        description: undefined,
        prep_time: undefined,
        cook_time: undefined,
        servings: undefined,
        cuisine_type: undefined,
        embedding: undefined,
        nutritional_info: undefined,
        deleted_at: undefined,
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z'
      };

      expect(recipe.description).toBeUndefined();
      expect(recipe.prep_time).toBeUndefined();
    });

    it('should validate ISO 8601 timestamp format', () => {
      const timestamp = '2025-11-15T12:00:00Z';
      const date = new Date(timestamp);

      // JavaScript adds milliseconds (.000), but the timestamp is valid
      expect(date.toISOString()).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/);
      expect(date.getTime()).toBe(new Date(timestamp).getTime());
    });

    it('should validate 768-dimensional embedding array', () => {
      const embedding = new Array(768).fill(0.5);

      expect(embedding).toHaveLength(768);
      expect(embedding.every(v => typeof v === 'number')).toBe(true);
    });
  });

  describe('Backend Compatibility', () => {
    it('should match backend Recipe schema exactly', () => {
      // Simulates a backend API response
      const backendResponse: Recipe = {
        id: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        name: 'Pasta Carbonara',
        description: 'Classic Italian pasta',
        instructions: {
          steps: ['Cook pasta', 'Mix eggs', 'Combine']
        },
        prep_time: 10,
        cook_time: 15,
        servings: 4,
        difficulty: 'medium',
        cuisine_type: 'Italian',
        diet_types: ['vegetarian'],
        embedding: new Array(768).fill(0.5),
        ingredients: [],
        categories: [],
        nutritional_info: undefined,
        created_at: '2025-11-15T12:00:00Z',
        updated_at: '2025-11-15T12:00:00Z',
        deleted_at: undefined
      };

      // Verify all required fields are present
      expect(backendResponse.id).toBeDefined();
      expect(backendResponse.name).toBeDefined();
      expect(backendResponse.instructions).toBeDefined();
      expect(backendResponse.difficulty).toBeDefined();
      expect(backendResponse.diet_types).toBeDefined();
      expect(backendResponse.ingredients).toBeDefined();
      expect(backendResponse.categories).toBeDefined();
      expect(backendResponse.created_at).toBeDefined();
      expect(backendResponse.updated_at).toBeDefined();
    });
  });
});
