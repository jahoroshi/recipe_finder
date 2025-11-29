# Recipe Management System - Frontend Specification

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**API Base URL:** `http://localhost:8009/api`

---

## Table of Contents

1. [System Overview](#system-overview)
2. [API Endpoints Reference](#api-endpoints-reference)
3. [Data Models](#data-models)
4. [Business Logic & Workflows](#business-logic--workflows)
5. [User Interface Requirements](#user-interface-requirements)
6. [User Flows & Interactions](#user-flows--interactions)
7. [Technical Requirements](#technical-requirements)
8. [Error Handling](#error-handling)
9. [Future Enhancements](#future-enhancements)

---

## System Overview

### Purpose

The Recipe Management System is an AI-powered platform for discovering, managing, and sharing cooking recipes. It features:

- **Smart Recipe Search**: Hybrid search combining semantic AI search and traditional filters
- **Recipe Management**: Full CRUD operations for recipes with ingredients, categories, and nutritional information
- **Semantic Discovery**: Find similar recipes using vector embeddings
- **Bulk Operations**: Import multiple recipes from JSON files
- **Rich Metadata**: Support for dietary restrictions, cuisine types, difficulty levels, and nutritional data

### Core Features

1. **Recipe Discovery**
   - Natural language search (e.g., "quick vegetarian pasta under 30 minutes")
   - Semantic search using AI embeddings
   - Filter-based search (cuisine, difficulty, diet types, cooking time)
   - Find similar recipes based on vector similarity

2. **Recipe Management**
   - Create recipes with detailed information
   - Update existing recipes (partial updates supported)
   - Delete recipes (soft delete)
   - View recipe details with all relationships

3. **Advanced Features**
   - Bulk import recipes from JSON
   - Background job processing
   - Real-time search with caching
   - Responsive API with performance monitoring

---

## API Endpoints Reference

### Base Information

- **Base URL**: `http://localhost:8009/api`
- **OpenAPI Docs**: `http://localhost:8009/api/docs`
- **ReDoc**: `http://localhost:8009/api/redoc`
- **Health Check**: `http://localhost:8009/health`

### Authentication

⚠️ **Note**: Authentication is not yet implemented. All endpoints are currently public.

### Common Response Headers

All responses include:
- `X-Request-ID`: Unique request identifier for tracing
- `X-Response-Time`: Response time in milliseconds
- `Content-Type`: `application/json`

---

## Recipe Endpoints

### 1. Create Recipe

**Endpoint**: `POST /api/recipes`
**Status Code**: `201 Created`
**Description**: Create a new recipe with ingredients, categories, and nutritional information

**Request Body**:
```json
{
  "name": "Pasta Carbonara",
  "description": "Classic Italian pasta dish with eggs, cheese, and pancetta",
  "instructions": {
    "steps": [
      "Cook pasta according to package directions",
      "Fry pancetta until crispy",
      "Mix eggs with Parmesan cheese",
      "Combine hot pasta with egg mixture",
      "Add pancetta and serve immediately"
    ]
  },
  "prep_time": 10,
  "cook_time": 15,
  "servings": 4,
  "difficulty": "medium",
  "cuisine_type": "Italian",
  "diet_types": ["vegetarian"],
  "ingredients": [
    {
      "name": "spaghetti",
      "quantity": 400,
      "unit": "g",
      "notes": "Use good quality pasta"
    },
    {
      "name": "eggs",
      "quantity": 3,
      "unit": "pieces"
    },
    {
      "name": "Parmesan cheese",
      "quantity": 100,
      "unit": "g",
      "notes": "Freshly grated"
    },
    {
      "name": "pancetta",
      "quantity": 150,
      "unit": "g"
    }
  ],
  "category_ids": [
    "uuid-of-pasta-category",
    "uuid-of-main-dishes-category"
  ],
  "nutritional_info": {
    "calories": 450,
    "protein_g": 18,
    "carbohydrates_g": 55,
    "fat_g": 16,
    "fiber_g": 3,
    "sugar_g": 2,
    "sodium_mg": 650,
    "cholesterol_mg": 185
  }
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-of-created-recipe",
  "name": "Pasta Carbonara",
  "description": "Classic Italian pasta dish...",
  "instructions": { "steps": [...] },
  "prep_time": 10,
  "cook_time": 15,
  "servings": 4,
  "difficulty": "medium",
  "cuisine_type": "Italian",
  "diet_types": ["vegetarian"],
  "embedding": [0.123, 0.456, ...],  // 768-dimensional vector (may be null initially)
  "ingredients": [
    {
      "id": "ingredient-uuid-1",
      "recipe_id": "uuid-of-created-recipe",
      "name": "spaghetti",
      "quantity": 400,
      "unit": "g",
      "notes": "Use good quality pasta",
      "created_at": "2025-11-15T12:00:00Z",
      "updated_at": "2025-11-15T12:00:00Z"
    },
    // ... more ingredients
  ],
  "categories": [
    {
      "id": "category-uuid-1",
      "name": "Pasta",
      "slug": "pasta",
      "description": "Pasta dishes",
      "parent_id": null,
      "children": [],
      "created_at": "2025-11-15T12:00:00Z",
      "updated_at": "2025-11-15T12:00:00Z"
    },
    // ... more categories
  ],
  "nutritional_info": {
    "id": "nutrition-uuid",
    "recipe_id": "uuid-of-created-recipe",
    "calories": 450,
    "protein_g": 18,
    "carbohydrates_g": 55,
    "fat_g": 16,
    "fiber_g": 3,
    "sugar_g": 2,
    "sodium_mg": 650,
    "cholesterol_mg": 185,
    "additional_info": null,
    "created_at": "2025-11-15T12:00:00Z",
    "updated_at": "2025-11-15T12:00:00Z"
  },
  "created_at": "2025-11-15T12:00:00Z",
  "updated_at": "2025-11-15T12:00:00Z",
  "deleted_at": null
}
```

**Validation Rules**:
- `name`: Required, 1-255 characters, trimmed
- `instructions`: Required, non-empty JSON object
- `prep_time`: Optional, >= 0 minutes
- `cook_time`: Optional, >= 0 minutes
- `servings`: Optional, > 0
- `difficulty`: Enum: "easy", "medium", "hard" (default: "medium")
- `cuisine_type`: Optional, max 100 characters
- `diet_types`: Array of strings (e.g., "vegetarian", "vegan", "gluten-free")
- `ingredients`: Array of ingredient objects
- `category_ids`: Array of valid UUIDs
- `nutritional_info`: Optional, all fields >= 0

**Error Responses**:
- `400 Bad Request`: Validation failed, duplicate name, or business rule violation
- `500 Internal Server Error`: Server error during creation

---

### 2. List Recipes

**Endpoint**: `GET /api/recipes`
**Status Code**: `200 OK`
**Description**: List recipes with optional filtering and pagination

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (1-indexed) |
| `page_size` | integer | No | 50 | Items per page (1-100) |
| `name` | string | No | - | Filter by name (partial match) |
| `cuisine_type` | string | No | - | Filter by cuisine type |
| `difficulty` | string | No | - | Filter by difficulty (easy/medium/hard) |
| `diet_types` | array[string] | No | - | Filter by diet types (any match) |
| `category_ids` | array[UUID] | No | - | Filter by category IDs |
| `min_prep_time` | integer | No | - | Minimum prep time (minutes) |
| `max_prep_time` | integer | No | - | Maximum prep time (minutes) |
| `min_cook_time` | integer | No | - | Minimum cook time (minutes) |
| `max_cook_time` | integer | No | - | Maximum cook time (minutes) |
| `min_servings` | integer | No | - | Minimum servings |
| `max_servings` | integer | No | - | Maximum servings |

**Example Request**:
```
GET /api/recipes?cuisine_type=Italian&difficulty=easy&max_prep_time=30&page=1&page_size=20
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "recipe-uuid-1",
      "name": "Quick Italian Pasta",
      "description": "Simple and delicious",
      // ... full recipe object
    },
    // ... more recipes
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

**Filter Behavior**:
- All filters are optional and combined with AND logic
- `diet_types` uses OR logic (recipe matches if it has ANY of the specified diet types)
- `name` uses case-insensitive partial matching
- Time ranges are inclusive (min <= value <= max)

---

### 3. Get Recipe by ID

**Endpoint**: `GET /api/recipes/{recipe_id}`
**Status Code**: `200 OK`
**Description**: Retrieve a single recipe with all relationships

**Path Parameters**:
- `recipe_id` (UUID): Recipe identifier

**Example Request**:
```
GET /api/recipes/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response** (200 OK):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Pasta Carbonara",
  "description": "Classic Italian pasta dish",
  "instructions": { "steps": [...] },
  "prep_time": 10,
  "cook_time": 15,
  "servings": 4,
  "difficulty": "medium",
  "cuisine_type": "Italian",
  "diet_types": ["vegetarian"],
  "embedding": [0.123, 0.456, ...],
  "ingredients": [...],
  "categories": [...],
  "nutritional_info": {...},
  "created_at": "2025-11-15T12:00:00Z",
  "updated_at": "2025-11-15T12:00:00Z",
  "deleted_at": null
}
```

**Error Responses**:
- `404 Not Found`: Recipe does not exist or has been deleted
- `500 Internal Server Error`: Server error

---

### 4. Update Recipe

**Endpoint**: `PUT /api/recipes/{recipe_id}`
**Status Code**: `200 OK`
**Description**: Update an existing recipe (partial updates supported)

**Path Parameters**:
- `recipe_id` (UUID): Recipe identifier

**Request Body** (all fields optional):
```json
{
  "name": "Updated Recipe Name",
  "description": "New description",
  "instructions": { "steps": [...] },
  "prep_time": 15,
  "cook_time": 20,
  "servings": 6,
  "difficulty": "hard",
  "cuisine_type": "French",
  "diet_types": ["vegan", "gluten-free"],
  "category_ids": ["new-category-uuid"]
}
```

**Response** (200 OK):
```json
{
  "id": "recipe-uuid",
  "name": "Updated Recipe Name",
  // ... full updated recipe object
}
```

**Update Behavior**:
- Only provided fields are updated (partial updates)
- Embedding is automatically regenerated if name, description, cuisine_type, diet_types, or difficulty changes
- Cache is invalidated after update
- `updated_at` timestamp is automatically updated

**Error Responses**:
- `400 Bad Request`: Validation failed or business rule violation
- `404 Not Found`: Recipe does not exist
- `500 Internal Server Error`: Server error

---

### 5. Delete Recipe

**Endpoint**: `DELETE /api/recipes/{recipe_id}`
**Status Code**: `204 No Content`
**Description**: Soft delete a recipe (marks as deleted without removing from database)

**Path Parameters**:
- `recipe_id` (UUID): Recipe identifier

**Response**: No content (empty body)

**Delete Behavior**:
- Soft delete: Recipe is marked with `deleted_at` timestamp
- Recipe no longer appears in list/search results
- Can be restored by backend (not exposed via API yet)
- All related data (ingredients, nutritional info) remains linked
- Cache is invalidated

**Error Responses**:
- `404 Not Found`: Recipe does not exist
- `500 Internal Server Error`: Server error

---

### 6. Find Similar Recipes

**Endpoint**: `GET /api/recipes/{recipe_id}/similar`
**Status Code**: `200 OK`
**Description**: Find recipes similar to the given recipe using vector embeddings

**Path Parameters**:
- `recipe_id` (UUID): Recipe identifier to find similar recipes for

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of similar recipes |

**Example Request**:
```
GET /api/recipes/a1b2c3d4-e5f6-7890-abcd-ef1234567890/similar?limit=5
```

**Response** (200 OK):
```json
[
  {
    "recipe": {
      "id": "similar-recipe-uuid-1",
      "name": "Spaghetti Aglio e Olio",
      "description": "Simple garlic and oil pasta",
      // ... full recipe object
    },
    "score": 0.92,
    "distance": 0.08,
    "match_type": "semantic"
  },
  {
    "recipe": {
      "id": "similar-recipe-uuid-2",
      "name": "Fettuccine Alfredo",
      // ... full recipe object
    },
    "score": 0.87,
    "distance": 0.13,
    "match_type": "semantic"
  },
  // ... more similar recipes
]
```

**Similarity Scoring**:
- `score`: Similarity score (0-1, higher is more similar)
- `distance`: Vector distance (1 - score, lower is more similar)
- Results ordered by score (descending)
- Source recipe is excluded from results

**Error Responses**:
- `404 Not Found`: Recipe does not exist
- `500 Internal Server Error`: Server error or embedding not available

---

### 7. Bulk Import Recipes

**Endpoint**: `POST /api/recipes/bulk`
**Status Code**: `202 Accepted`
**Description**: Import multiple recipes from a JSON file (processed in background)

**Request**:
- Content-Type: `multipart/form-data`
- File field: `file` (must be `.json` file)

**File Format**:
```json
[
  {
    "name": "Recipe 1",
    "description": "Description 1",
    "instructions": { "steps": [...] },
    "prep_time": 10,
    "cook_time": 15,
    "servings": 4,
    "difficulty": "easy",
    "ingredients": [...],
    "category_ids": [...],
    "nutritional_info": {...}
  },
  {
    "name": "Recipe 2",
    // ... another recipe
  }
  // ... more recipes
]
```

**Response** (202 Accepted):
```json
{
  "job_id": "job-uuid-1234",
  "status": "accepted",
  "total_recipes": 25,
  "message": "Bulk import started. Results will be processed in the background."
}
```

**Background Processing**:
- Each recipe is validated and created individually
- Invalid recipes are skipped with errors logged
- Process continues even if some recipes fail
- Currently no status endpoint (job_id returned for future use)

**Error Responses**:
- `400 Bad Request`: Invalid file format, not a JSON file, or not an array
- `500 Internal Server Error`: Failed to start import

---

## Search Endpoints

### 1. Hybrid Search

**Endpoint**: `POST /api/search`
**Status Code**: `200 OK`
**Description**: Perform intelligent hybrid search combining semantic AI search and filter-based search

**Request Body**:
```json
{
  "query": "quick vegetarian pasta under 30 minutes",
  "limit": 10,
  "use_semantic": true,
  "use_filters": true,
  "use_reranking": false,
  "filters": {
    "cuisine_type": "Italian",
    "max_cook_time": 30
  }
}
```

**Request Fields**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | Natural language search query |
| `limit` | integer | No | 10 | Max results (1-100) |
| `use_semantic` | boolean | No | true | Use AI vector search |
| `use_filters` | boolean | No | true | Use filter-based search |
| `use_reranking` | boolean | No | false | Apply AI reranking to results |
| `filters` | object | No | null | Additional filter criteria |

**Response** (200 OK):
```json
{
  "query": "quick vegetarian pasta under 30 minutes",
  "parsed_query": {
    "original_query": "quick vegetarian pasta under 30 minutes",
    "ingredients": ["pasta"],
    "cuisine_type": "Italian",
    "diet_types": ["vegetarian"],
    "max_prep_time": 30,
    "max_cook_time": null,
    "difficulty": null,
    "semantic_query": "vegetarian pasta"
  },
  "results": [
    {
      "recipe": {
        "id": "recipe-uuid-1",
        "name": "Quick Vegetarian Pesto Pasta",
        // ... full recipe object
      },
      "score": 0.95,
      "distance": 0.05,
      "match_type": "hybrid"
    },
    {
      "recipe": {
        "id": "recipe-uuid-2",
        "name": "Simple Pasta Primavera",
        // ... full recipe object
      },
      "score": 0.88,
      "distance": 0.12,
      "match_type": "hybrid"
    }
    // ... more results
  ],
  "total": 8,
  "search_type": "hybrid",
  "metadata": {
    "semantic_results": 12,
    "filter_results": 6,
    "merged_results": 15,
    "final_results": 8
  }
}
```

**Search Process** (LangGraph Workflow):
1. **Parse Query**: AI extracts filters and semantic components from natural language
2. **Generate Embedding**: Convert query to vector (if `use_semantic: true`)
3. **Semantic Search**: Find recipes by vector similarity
4. **Filter Search**: Find recipes matching extracted filters
5. **Merge Results**: Combine using Reciprocal Rank Fusion (RRF) algorithm
6. **Rerank** (optional): AI reranks results for better relevance

**Match Types**:
- `semantic`: Result from vector similarity only
- `filter`: Result from filters only
- `hybrid`: Result from merged semantic + filter searches

**Error Responses**:
- `400 Bad Request`: Empty query or validation failed
- `500 Internal Server Error`: Search operation failed

---

### 2. Semantic Search

**Endpoint**: `POST /api/search/semantic`
**Status Code**: `200 OK`
**Description**: Pure semantic search using AI vector embeddings

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query text |
| `limit` | integer | No | 10 | Maximum results |

**Example Request**:
```
POST /api/search/semantic?query=creamy%20pasta&limit=5
```

**Response** (200 OK):
```json
[
  {
    "recipe": {
      "id": "recipe-uuid-1",
      "name": "Fettuccine Alfredo",
      // ... full recipe object
    },
    "score": 0.93,
    "distance": 0.07,
    "match_type": "semantic"
  },
  {
    "recipe": {
      "id": "recipe-uuid-2",
      "name": "Carbonara",
      // ... full recipe object
    },
    "score": 0.89,
    "distance": 0.11,
    "match_type": "semantic"
  }
  // ... more results
]
```

**Error Responses**:
- `400 Bad Request`: Empty query
- `500 Internal Server Error`: Semantic search failed

---

### 3. Filter Search

**Endpoint**: `POST /api/search/filter`
**Status Code**: `200 OK`
**Description**: Pure filter-based search using attribute matching

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filters` | object | Yes | - | Filter criteria (JSON) |
| `limit` | integer | No | 10 | Maximum results |

**Request Body**:
```json
{
  "cuisine_type": "Italian",
  "difficulty": "easy",
  "max_prep_time": 20,
  "diet_types": ["vegetarian"]
}
```

**Response** (200 OK):
```json
[
  {
    "recipe": {
      "id": "recipe-uuid-1",
      "name": "Simple Caprese Salad",
      // ... full recipe object
    },
    "score": 1.0,
    "match_type": "filter"
  },
  {
    "recipe": {
      "id": "recipe-uuid-2",
      "name": "Quick Bruschetta",
      // ... full recipe object
    },
    "score": 1.0,
    "match_type": "filter"
  }
  // ... more results
]
```

**Filter Matching**:
- All filters use AND logic
- `diet_types` uses OR logic (any match)
- Uniform score of 1.0 for all filter matches
- No distance metric for filter-only results

**Error Responses**:
- `400 Bad Request`: Empty or invalid filters
- `500 Internal Server Error`: Filter search failed

---

## Health Endpoints

### 1. Basic Health Check

**Endpoint**: `GET /health`
**Status Code**: `200 OK`
**Description**: Check if API is running

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Recipe Management API"
}
```

---

### 2. Detailed Health Check

**Endpoint**: `GET /health/detailed`
**Status Code**: `200 OK`
**Description**: Check health of all system components

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Recipe Management API",
  "components": {
    "redis": {
      "status": "healthy",
      "message": "Connected"
    },
    "database": {
      "status": "healthy",
      "message": "Connection pool available"
    }
  }
}
```

**Component Status**:
- `healthy`: Component is working
- `unhealthy`: Component has failed
- Overall `status` is `degraded` if any component is unhealthy

---

## Data Models

### Recipe Model

**Core Entity**: Represents a cooking recipe with instructions, timing, and metadata

**Fields**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Unique identifier |
| `name` | string(255) | No | Recipe name/title |
| `description` | text | Yes | Brief description |
| `instructions` | JSON | No | Cooking steps as structured data |
| `prep_time` | integer | Yes | Preparation time in minutes |
| `cook_time` | integer | Yes | Cooking time in minutes |
| `servings` | integer | Yes | Number of servings |
| `difficulty` | enum | No | easy/medium/hard (default: medium) |
| `cuisine_type` | string(100) | Yes | Type of cuisine |
| `diet_types` | array[string] | No | Diet types (default: []) |
| `embedding` | vector(768) | Yes | AI vector embedding |
| `created_at` | timestamp | No | Creation timestamp |
| `updated_at` | timestamp | No | Last update timestamp |
| `deleted_at` | timestamp | Yes | Soft delete timestamp |

**Relationships**:
- Has many `Ingredient` (cascade delete)
- Belongs to many `Category` (through `RecipeCategory`)
- Has one `NutritionalInfo` (cascade delete)

**Computed Properties**:
- `total_time`: `prep_time + cook_time`

**Business Rules**:
- Name must be unique (case-insensitive)
- Total time (`prep_time + cook_time`) must be < 24 hours (1440 minutes)
- Instructions cannot be empty
- Servings must be > 0 if provided

---

### Ingredient Model

**Purpose**: Represents an ingredient in a recipe

**Fields**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Unique identifier |
| `recipe_id` | UUID | No | Foreign key to recipe |
| `name` | string(255) | No | Ingredient name |
| `quantity` | float | Yes | Quantity amount |
| `unit` | string(50) | Yes | Unit of measurement |
| `notes` | text | Yes | Additional notes |
| `created_at` | timestamp | No | Creation timestamp |
| `updated_at` | timestamp | No | Last update timestamp |

**Relationships**:
- Belongs to `Recipe`

**Validation**:
- `quantity` must be >= 0 if provided
- `name` is trimmed and required

---

### Category Model

**Purpose**: Hierarchical categorization system for recipes

**Fields**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Unique identifier |
| `name` | string(100) | No | Category name (unique) |
| `slug` | string(100) | No | URL-friendly slug (unique) |
| `description` | text | Yes | Category description |
| `parent_id` | UUID | Yes | Parent category for hierarchy |
| `created_at` | timestamp | No | Creation timestamp |
| `updated_at` | timestamp | No | Last update timestamp |

**Relationships**:
- Has one `Category` (parent)
- Has many `Category` (children)
- Belongs to many `Recipe` (through `RecipeCategory`)

**Validation**:
- `slug` must be lowercase, alphanumeric with hyphens only
- Hierarchical depth is unlimited

**Examples**:
- Top-level: "Main Dishes", "Desserts", "Appetizers"
- Second-level: "Pasta" (parent: "Main Dishes"), "Cakes" (parent: "Desserts")

---

### NutritionalInfo Model

**Purpose**: Nutritional information for a recipe (one-to-one with Recipe)

**Fields**:
| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | UUID | No | Unique identifier |
| `recipe_id` | UUID | No | Foreign key to recipe (unique) |
| `calories` | float | Yes | Calories per serving |
| `protein_g` | float | Yes | Protein in grams |
| `carbohydrates_g` | float | Yes | Carbohydrates in grams |
| `fat_g` | float | Yes | Fat in grams |
| `fiber_g` | float | Yes | Fiber in grams |
| `sugar_g` | float | Yes | Sugar in grams |
| `sodium_mg` | float | Yes | Sodium in milligrams |
| `cholesterol_mg` | float | Yes | Cholesterol in milligrams |
| `additional_info` | JSON | Yes | Additional nutritional data |
| `created_at` | timestamp | No | Creation timestamp |
| `updated_at` | timestamp | No | Last update timestamp |

**Relationships**:
- Belongs to `Recipe` (one-to-one)

**Validation**:
- All nutritional values must be >= 0 if provided
- `additional_info` must be a valid JSON object

---

### RecipeCategory Model (Junction Table)

**Purpose**: Many-to-many relationship between recipes and categories

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `recipe_id` | UUID | Foreign key to recipe |
| `category_id` | UUID | Foreign key to category |

**Constraints**:
- Unique constraint on (recipe_id, category_id) - no duplicates

---

## Business Logic & Workflows

### Search Strategy

The system implements a sophisticated hybrid search approach:

#### 1. Query Understanding (AI-Powered)

When a user submits a natural language query, Gemini AI parses it to extract:

- **Ingredients**: Detected ingredient names (e.g., "pasta", "chicken")
- **Cuisine Type**: Cuisine style (e.g., "Italian", "Chinese")
- **Diet Types**: Dietary restrictions (e.g., "vegetarian", "vegan", "gluten-free")
- **Time Constraints**: Maximum prep/cook time (e.g., "under 30 minutes")
- **Difficulty**: Desired difficulty level (e.g., "easy", "quick")
- **Semantic Query**: Cleaned query for vector search

**Example**:
```
Input: "quick vegetarian pasta under 30 minutes"

Parsed Output:
{
  "ingredients": ["pasta"],
  "cuisine_type": "Italian",
  "diet_types": ["vegetarian"],
  "max_prep_time": 30,
  "semantic_query": "vegetarian pasta"
}
```

#### 2. Dual Search Execution (Parallel)

The system executes two searches simultaneously:

**A. Semantic Search (Vector Similarity)**:
- Converts query to 768-dimensional embedding using Gemini AI
- Searches recipes using cosine similarity on embeddings
- Returns semantically similar recipes (understands context and meaning)
- Score: 1 - cosine_distance (0-1, higher is better)

**B. Filter Search (Attribute Matching)**:
- Uses extracted filters (cuisine, diet, time, difficulty)
- Performs SQL-based filtering on recipe attributes
- Returns exact matches based on criteria
- Score: 1.0 for all matches (uniform)

#### 3. Result Merging (Reciprocal Rank Fusion)

Results from both searches are combined using RRF algorithm:

```
For each recipe:
  score = sum(1 / (k + rank_in_list))
  where k = 60 (constant)
```

**Benefits**:
- Balances semantic and filter-based relevance
- Handles overlapping results from both searches
- Recipes appearing in both lists get boosted scores

**Example**:
```
Semantic Results: [Recipe A (rank 1), Recipe B (rank 2), Recipe C (rank 3)]
Filter Results: [Recipe B (rank 1), Recipe D (rank 2)]

RRF Scores:
- Recipe A: 1/(60+1) = 0.0164
- Recipe B: 1/(60+1) + 1/(60+1) = 0.0328 (appears in both!)
- Recipe C: 1/(60+2) = 0.0161
- Recipe D: 1/(60+2) = 0.0161

Final Ranking: B, A, C, D
```

#### 4. Optional Reranking (AI-Enhanced)

If `use_reranking: true`:
- Limited to top 20 results (API token efficiency)
- Gemini AI evaluates relevance of each result to query
- Assigns new scores based on deeper understanding
- Re-sorts results for improved accuracy

**Use Cases**:
- Complex queries with multiple requirements
- When top results need fine-tuning
- Quality over speed (adds 1-2 seconds)

---

### Recipe Creation Workflow

**Process Flow**:

1. **Validation**: Pydantic schemas validate all input fields
2. **Business Rules Check**:
   - Check name uniqueness (case-insensitive)
   - Validate total time < 24 hours
   - Ensure instructions are non-empty
3. **Database Transaction**:
   - Create recipe record
   - Create related ingredients
   - Link to existing categories
   - Create nutritional info if provided
4. **Embedding Generation** (Background):
   - Construct text: "Name | Description | Cuisine: Type | Diet: Types | Difficulty: Level"
   - Generate 768-dimensional vector via Gemini API
   - Update recipe with embedding
5. **Cache Population**:
   - Cache recipe data (1-hour TTL)
6. **Response**: Return created recipe with all relationships

**Example Text for Embedding**:
```
"Pasta Carbonara | Classic Italian pasta with eggs and cheese | Cuisine: Italian | Diet: vegetarian | Difficulty: medium"
```

---

### Recipe Update Workflow

**Process Flow**:

1. **Retrieve Existing**: Load current recipe from database
2. **Validate Updates**: Check provided fields against business rules
3. **Check Embedding Regeneration**: If name, description, cuisine_type, diet_types, or difficulty changed → regenerate embedding
4. **Database Transaction**:
   - Apply updates to recipe
   - Update timestamp
5. **Embedding Update** (If Needed):
   - Generate new embedding
   - Update recipe
6. **Cache Invalidation**:
   - Delete recipe cache entry
   - Delete related search caches
   - Delete stats caches
7. **Response**: Return updated recipe

**Fields Triggering Embedding Regeneration**:
- `name`
- `description`
- `cuisine_type`
- `diet_types`
- `difficulty`

**Fields NOT Triggering Regeneration**:
- `prep_time`, `cook_time`, `servings` (only timing/quantity changes)
- `instructions` (embedding based on metadata, not steps)

---

### Caching Strategy

The system uses Redis for multi-level caching:

**Cache Hierarchy**:

1. **Recipe Cache** (TTL: 1 hour):
   - Key: `recipe:{id}`
   - Stores full recipe with relationships
   - Invalidated on update/delete

2. **Search Results Cache** (TTL: 15 minutes):
   - Key: `search:{query_hash}`
   - Hash includes query + filters
   - Shorter TTL for fresher results
   - Invalidated when any recipe updates

3. **Embedding Cache** (TTL: 24 hours):
   - Key: `embedding:{text_hash}`
   - Stores generated embeddings
   - Long TTL (embeddings are stable)
   - Reduces API calls to Gemini

4. **Stats Cache** (TTL: 5 minutes):
   - Key: `stats:{type}`
   - Aggregated statistics
   - Very short TTL (frequently changing)

**Cache Invalidation**:
- **Recipe Update/Delete**: Invalidates recipe + all search + all stats
- **Pattern-Based**: Uses Redis SCAN for bulk invalidation (non-blocking)
- **TTL-Based**: Automatic expiration for stale data

---

### Embedding Generation

**Purpose**: Convert recipe metadata to 768-dimensional vectors for semantic search

**Model**: Google Gemini `text-embedding-004`

**Input Construction**:
```
"{name} | {description} | Cuisine: {cuisine_type} | Diet: {diet_types} | Difficulty: {difficulty}"
```

**Task Types**:
- `retrieval_document`: For indexing recipes (creation/update)
- `retrieval_query`: For search queries (optimized for matching)
- `semantic_similarity`: For finding similar recipes

**Caching**:
- Embeddings cached for 24 hours
- Hash-based keys for deterministic caching
- Reduces API calls and costs

**Rate Limiting**:
- 60 requests per minute (configurable)
- Automatic sleep between requests
- Thread-safe across async operations

---

### Soft Delete Mechanism

**Behavior**:
- Deletes set `deleted_at` timestamp instead of removing data
- Deleted recipes excluded from all queries automatically
- All relationships preserved (ingredients, categories, nutritional info)
- Can be restored by backend (not yet exposed in API)

**Benefits**:
- Data recovery possible
- Audit trail maintained
- Referential integrity preserved

**Database Filter**:
All repository queries automatically filter: `WHERE deleted_at IS NULL`

---

### Background Job Processing

**Use Case**: Bulk recipe import

**Flow**:
1. User uploads JSON file
2. API validates file format
3. Job ID generated and returned immediately (202 Accepted)
4. Background task processes recipes asynchronously
5. Each recipe validated and created individually
6. Errors logged but don't stop processing
7. Success/error counts tracked (currently logged, not exposed)

**Future Enhancement**: Job status endpoint to check import progress

---

## User Interface Requirements

### Page Structure

The frontend should implement these main pages:

#### 1. Recipe List / Browse Page

**Purpose**: Browse and filter recipes

**Components**:
- **Search Bar**: Natural language input for hybrid search
- **Filter Panel**:
  - Cuisine type dropdown
  - Difficulty level selector (easy/medium/hard)
  - Diet types multi-select (vegetarian, vegan, gluten-free, etc.)
  - Time sliders (prep time, cook time)
  - Servings range
- **Recipe Cards Grid**:
  - Image placeholder
  - Recipe name
  - Cuisine type badge
  - Difficulty badge
  - Prep + cook time
  - Servings count
  - Diet type tags
- **Pagination Controls**: Page numbers, next/prev buttons
- **Results Count**: "Showing X-Y of Z recipes"

**Interactions**:
- Click recipe card → Navigate to recipe detail page
- Type in search bar → Trigger hybrid search
- Change filters → Update recipe list
- Pagination → Load new page of results

#### 2. Recipe Detail Page

**Purpose**: Display full recipe information

**Sections**:
- **Header**:
  - Recipe name (h1)
  - Description
  - Meta badges (cuisine, difficulty, diet types)
  - Action buttons (Edit, Delete, Find Similar)
- **Info Panel**:
  - Prep time
  - Cook time
  - Total time (computed)
  - Servings
  - Created/updated timestamps
- **Ingredients List**:
  - Quantity, unit, name, notes
  - Checkboxes for shopping list (optional feature)
- **Instructions**:
  - Step-by-step display (numbered list)
- **Nutritional Information** (if available):
  - Calories, protein, carbs, fat
  - Fiber, sugar, sodium, cholesterol
  - Visual chart/table
- **Categories**:
  - Category badges (clickable to filter by category)
- **Similar Recipes** (slider/carousel):
  - Thumbnails of similar recipes
  - Click to view

**Interactions**:
- Edit button → Navigate to edit form (pre-filled)
- Delete button → Confirmation modal → Delete recipe → Redirect to list
- Find Similar → Load similar recipes section
- Category badge click → Filter recipes by that category

#### 3. Create/Edit Recipe Form

**Purpose**: Create new or edit existing recipe

**Form Sections**:

**Basic Information**:
- Recipe name (text input, required)
- Description (textarea, optional)
- Cuisine type (text input or dropdown)
- Difficulty (radio buttons: easy/medium/hard)
- Diet types (multi-select checkboxes)

**Timing & Servings**:
- Prep time (number input, minutes)
- Cook time (number input, minutes)
- Servings (number input)

**Ingredients** (Dynamic List):
- Add ingredient button
- For each ingredient:
  - Name (text input, required)
  - Quantity (number input)
  - Unit (text input)
  - Notes (text input)
  - Remove button

**Instructions**:
- JSON editor or step-by-step builder
- Add step button
- Drag to reorder steps
- Remove step button

**Categories**:
- Multi-select dropdown or checkboxes
- Search/filter categories

**Nutritional Information** (Optional, collapsible):
- Calories (number)
- Protein (g)
- Carbohydrates (g)
- Fat (g)
- Fiber (g)
- Sugar (g)
- Sodium (mg)
- Cholesterol (mg)

**Actions**:
- Save button → Validate → API call → Redirect to detail page
- Cancel button → Discard changes → Navigate back
- Validation errors → Display inline

#### 4. Search Results Page

**Purpose**: Display results from hybrid search

**Similar to List Page with Additions**:
- **Search Query Display**: "Showing results for: '{query}'"
- **Parsed Query Info** (expandable):
  - Detected cuisine
  - Detected diet types
  - Detected time constraints
  - Semantic query used
- **Result Cards with Scores**:
  - Relevance score badge
  - Match type indicator (semantic/filter/hybrid)
- **Search Metadata**:
  - Total results
  - Search type performed
  - Processing time (from X-Response-Time header)

**Interactions**:
- New search → Update results
- Filter results further → Combine with search
- Sort by relevance/time/difficulty (client-side)

#### 5. Bulk Import Page

**Purpose**: Upload JSON file to import multiple recipes

**Components**:
- **File Upload**:
  - Drag-and-drop zone
  - Browse file button
  - File format validation (.json only)
- **Instructions**:
  - JSON format example
  - Link to download template
- **Upload Button**: Triggers import
- **Status Display**:
  - Job ID
  - "Import started" message
  - Note about background processing

**Future Enhancement**:
- Progress bar
- Real-time status updates
- List of successfully imported recipes
- Error details for failed imports

---

### UI/UX Guidelines

**Design Principles**:
- **Clean & Modern**: Minimalist design with focus on content
- **Responsive**: Mobile-first approach, works on all screen sizes
- **Accessible**: WCAG 2.1 AA compliance, keyboard navigation
- **Fast**: Optimistic UI updates, skeleton loaders, caching

**Color Scheme**:
- Primary: Food-related warm tones (e.g., orange/red for action buttons)
- Secondary: Neutral grays for backgrounds
- Accent: Green for vegetarian/healthy indicators
- Danger: Red for delete actions
- Success: Green for confirmations

**Typography**:
- Headings: Bold, clear hierarchy (h1, h2, h3)
- Body: Readable font size (16px minimum), good line height
- Code/JSON: Monospace font for instructions editor

**Icons**:
- Cuisine type icons (pizza for Italian, etc.)
- Difficulty icons (chef hat levels)
- Time icon (clock)
- Servings icon (plate/utensils)
- Diet type icons (leaf for vegetarian, etc.)

**Badges**:
- Rounded pills for tags
- Different colors for different types (cuisine, diet, difficulty)
- Small text, high contrast

**Loading States**:
- Skeleton screens for recipe cards
- Spinners for actions (save, delete)
- Progress indicators for search
- Disable buttons during async operations

**Error States**:
- Toast notifications for errors
- Inline validation errors on forms
- Empty states with helpful messages
- Retry buttons for failed operations

**Success States**:
- Toast notifications for confirmations
- Success messages on create/update/delete
- Smooth transitions between states

---

## User Flows & Interactions

### Flow 1: Discover Recipes with Natural Language Search

**User Goal**: Find recipes using conversational search

**Steps**:
1. User navigates to homepage
2. Sees prominent search bar with placeholder: "Search for recipes... (e.g., 'quick vegetarian dinner')"
3. Types query: "easy italian pasta for 2 people under 20 minutes"
4. Presses Enter or clicks Search button
5. **Frontend**: Shows loading skeleton
6. **Frontend**: POST `/api/search` with query
7. **Backend**: Parses query, extracts filters, performs hybrid search
8. **Frontend**: Receives results with parsed query info
9. Displays results with:
   - Highlighted match scores
   - Match type badges (hybrid/semantic/filter)
   - Parsed query details (expandable)
10. User scrolls through results
11. Clicks on a recipe card
12. Navigates to recipe detail page

**Alternative Path**:
- No results found → Display empty state with suggestions:
  - "Try different keywords"
  - "Broaden your search criteria"
  - Links to popular categories

---

### Flow 2: Create a New Recipe

**User Goal**: Add a new recipe to the system

**Steps**:
1. User clicks "Add Recipe" button (navbar or homepage)
2. Navigates to create recipe form
3. Fills in basic information:
   - Name: "Spaghetti Aglio e Olio"
   - Description: "Simple garlic and oil pasta"
   - Cuisine: "Italian"
   - Difficulty: "Easy"
   - Diet types: ["Vegetarian"]
   - Prep time: 5 minutes
   - Cook time: 10 minutes
   - Servings: 2
4. Adds ingredients (clicks "Add Ingredient" for each):
   - Spaghetti, 200g
   - Garlic, 4 cloves
   - Olive oil, 50ml
   - Red pepper flakes, 1 tsp
   - Parsley, 2 tbsp
5. Adds instructions (using step builder):
   - Step 1: "Cook spaghetti according to package directions"
   - Step 2: "Heat olive oil in a pan"
   - Step 3: "Sauté sliced garlic until golden"
   - Step 4: "Add cooked pasta and red pepper flakes"
   - Step 5: "Toss well and garnish with parsley"
6. Selects categories from dropdown (searches "pasta"):
   - Pasta
   - Main Dishes
7. Optionally adds nutritional info
8. Clicks "Save Recipe"
9. **Frontend**: Shows loading spinner on button
10. **Frontend**: POST `/api/recipes` with form data
11. **Backend**: Validates, creates recipe, generates embedding
12. **Frontend**: Receives created recipe
13. Shows success toast: "Recipe created successfully!"
14. Navigates to new recipe detail page

**Validation Errors**:
- If name already exists → Error toast: "Recipe with this name already exists"
- If required fields missing → Inline errors under fields
- If invalid data (negative time) → Field-specific error messages

---

### Flow 3: Find Similar Recipes

**User Goal**: Discover recipes similar to one they like

**Steps**:
1. User viewing recipe detail page ("Pasta Carbonara")
2. Scrolls to bottom or sees "Similar Recipes" section
3. Clicks "Find Similar Recipes" button or section auto-loads
4. **Frontend**: Shows loading skeletons for recipe cards
5. **Frontend**: GET `/api/recipes/{id}/similar?limit=6`
6. **Backend**: Performs vector similarity search
7. **Frontend**: Receives similar recipes with scores
8. Displays in horizontal carousel:
   - 6 recipe cards
   - Similarity score badges (92%, 87%, etc.)
   - Arrows to scroll through
9. User sees "Spaghetti Aglio e Olio" with 92% similarity
10. Clicks on it
11. Navigates to that recipe's detail page
12. Can repeat process to explore related recipes

**Empty State**:
- If no similar recipes found (no embedding) → Message: "No similar recipes available yet. Check back soon!"

---

### Flow 4: Filter Recipes by Criteria

**User Goal**: Browse recipes with specific requirements

**Steps**:
1. User navigates to browse page
2. Sees filter panel on left (desktop) or collapsible (mobile)
3. Selects filters:
   - Cuisine: "Mexican"
   - Difficulty: "Easy"
   - Diet types: "Vegan"
   - Max prep time: 30 minutes
   - Max cook time: 45 minutes
4. **Frontend**: Debounces filter changes (500ms)
5. **Frontend**: GET `/api/recipes?cuisine_type=Mexican&difficulty=easy&diet_types=vegan&max_prep_time=30&max_cook_time=45&page=1&page_size=20`
6. **Backend**: Filters recipes in database
7. **Frontend**: Receives filtered results
8. Updates recipe grid
9. Shows active filters as removable badges
10. Displays count: "12 recipes found"
11. User clicks badge "X" to remove "Vegan" filter
12. Updates and reloads results

**Combined with Search**:
- User can type in search bar while filters active
- Triggers hybrid search with filters merged

---

### Flow 5: Edit Existing Recipe

**User Goal**: Update recipe information

**Steps**:
1. User on recipe detail page
2. Clicks "Edit Recipe" button
3. Navigates to edit form (same as create, pre-filled)
4. Changes prep time from 10 to 15 minutes
5. Adds new ingredient: "Black pepper, 1 tsp"
6. Updates description
7. Clicks "Save Changes"
8. **Frontend**: Shows loading spinner
9. **Frontend**: PUT `/api/recipes/{id}` with updated fields only
10. **Backend**: Validates, updates recipe, regenerates embedding (description changed)
11. **Frontend**: Receives updated recipe
12. Shows success toast: "Recipe updated successfully!"
13. Navigates back to detail page with updated data

**Discard Changes**:
- User clicks "Cancel" → Confirmation modal: "Discard unsaved changes?" → Confirms → Navigates back

---

### Flow 6: Delete Recipe

**User Goal**: Remove a recipe permanently (soft delete)

**Steps**:
1. User on recipe detail page
2. Clicks "Delete Recipe" button (red, destructive style)
3. **Frontend**: Shows confirmation modal:
   - "Are you sure you want to delete 'Pasta Carbonara'?"
   - "This action cannot be undone."
   - Buttons: "Cancel" (default), "Delete" (danger)
4. User clicks "Delete"
5. **Frontend**: Shows loading spinner in modal
6. **Frontend**: DELETE `/api/recipes/{id}`
7. **Backend**: Soft deletes recipe (sets deleted_at)
8. **Frontend**: Receives 204 No Content
9. Closes modal
10. Shows success toast: "Recipe deleted successfully"
11. Navigates to browse page
12. Deleted recipe no longer appears in any lists/searches

---

### Flow 7: Bulk Import Recipes

**User Goal**: Import multiple recipes from a file

**Steps**:
1. User navigates to "Import Recipes" page
2. Sees instructions and JSON format example
3. Clicks "Download Template" to get example file
4. Prepares JSON file with 50 recipes
5. Drags file into upload zone or clicks "Browse"
6. File selected: "recipes.json (125 KB)"
7. Clicks "Upload and Import"
8. **Frontend**: Shows upload progress bar
9. **Frontend**: POST `/api/recipes/bulk` with file
10. **Backend**: Validates file, queues background job
11. **Frontend**: Receives 202 Accepted with job_id
12. Shows success message:
    - "Import started!"
    - "Job ID: abc-123-def"
    - "50 recipes are being processed in the background"
    - "You'll be notified when complete" (future feature)
13. User can navigate away (processing continues)

**Future Enhancement**:
- Poll status endpoint with job_id
- Show progress: "25 of 50 recipes imported"
- Display errors: "3 recipes failed (see details)"

---

### Flow 8: Browse by Category

**User Goal**: Explore recipes in a specific category

**Steps**:
1. User on homepage sees category cards:
   - "Pasta" with icon and count
   - "Desserts"
   - "Salads"
   - "Soups"
2. Clicks "Pasta" card
3. Navigates to browse page with filter pre-applied
4. **Frontend**: GET `/api/recipes?category_ids={pasta-category-id}&page=1&page_size=20`
5. Displays recipes in that category
6. Shows breadcrumb: "Home > Categories > Pasta"
7. Can further filter or search within category

**Hierarchical Categories**:
- If category has children, show subcategory navigation
- Example: "Main Dishes" → "Pasta", "Rice", "Meat"

---

## Technical Requirements

### Frontend Technology Stack (Recommendations)

**Framework Options**:
- React (with hooks)
- Vue 3 (with Composition API)
- Angular 15+
- Svelte

**Styling**:
- TailwindCSS (utility-first, rapid development)
- Or Material-UI / Chakra UI (component libraries)
- CSS Modules / Styled Components

**State Management**:
- React: Context API + hooks or Redux Toolkit
- Vue: Pinia or Vuex
- Zustand (lightweight alternative)

**HTTP Client**:
- Axios (interceptors for auth, error handling)
- Fetch API with wrapper
- React Query / TanStack Query (caching, invalidation)

**Form Handling**:
- React Hook Form (React)
- Formik
- VeeValidate (Vue)
- Built-in form validation

**Routing**:
- React Router (React)
- Vue Router (Vue)
- Angular Router (Angular)

**Additional Libraries**:
- `react-toastify` or similar for notifications
- `react-select` for searchable dropdowns
- Date/time formatting: `date-fns` or `dayjs`
- Icons: `react-icons` or `heroicons`
- Markdown editor for instructions (optional): `react-markdown`

---

### API Integration

**Base Configuration**:
```javascript
// api.config.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8009/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token when available (future)
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log response time
    const responseTime = response.headers['x-response-time'];
    console.log(`Response time: ${responseTime}ms`);
    return response;
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      if (status === 404) {
        // Handle not found
        console.error('Resource not found:', data.error.message);
      } else if (status === 400) {
        // Validation error
        console.error('Validation failed:', data.error.message);
      } else if (status >= 500) {
        // Server error
        console.error('Server error:', data.error.message);
      }
    } else if (error.request) {
      // No response received
      console.error('No response from server');
    } else {
      // Request setup error
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

**API Service Example**:
```javascript
// services/recipeService.js
import apiClient from './api.config';

export const recipeService = {
  // Get all recipes with filters and pagination
  getRecipes: async (filters = {}, page = 1, pageSize = 20) => {
    const params = { ...filters, page, page_size: pageSize };
    const response = await apiClient.get('/recipes', { params });
    return response.data;
  },

  // Get single recipe by ID
  getRecipeById: async (id) => {
    const response = await apiClient.get(`/recipes/${id}`);
    return response.data;
  },

  // Create new recipe
  createRecipe: async (recipeData) => {
    const response = await apiClient.post('/recipes', recipeData);
    return response.data;
  },

  // Update recipe
  updateRecipe: async (id, updates) => {
    const response = await apiClient.put(`/recipes/${id}`, updates);
    return response.data;
  },

  // Delete recipe
  deleteRecipe: async (id) => {
    await apiClient.delete(`/recipes/${id}`);
  },

  // Find similar recipes
  findSimilar: async (id, limit = 10) => {
    const response = await apiClient.get(`/recipes/${id}/similar`, {
      params: { limit },
    });
    return response.data;
  },

  // Bulk import
  bulkImport: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/recipes/bulk', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

export const searchService = {
  // Hybrid search
  hybridSearch: async (query, options = {}) => {
    const response = await apiClient.post('/search', {
      query,
      limit: options.limit || 10,
      use_semantic: options.use_semantic !== false,
      use_filters: options.use_filters !== false,
      use_reranking: options.use_reranking || false,
      filters: options.filters || null,
    });
    return response.data;
  },

  // Semantic search
  semanticSearch: async (query, limit = 10) => {
    const response = await apiClient.post('/search/semantic', null, {
      params: { query, limit },
    });
    return response.data;
  },

  // Filter search
  filterSearch: async (filters, limit = 10) => {
    const response = await apiClient.post('/search/filter', null, {
      params: { filters: JSON.stringify(filters), limit },
    });
    return response.data;
  },
};
```

---

### State Management Example

**Using React Context + Hooks**:
```javascript
// context/RecipeContext.js
import React, { createContext, useContext, useState, useCallback } from 'react';
import { recipeService } from '../services/recipeService';

const RecipeContext = createContext();

export const useRecipes = () => {
  const context = useContext(RecipeContext);
  if (!context) {
    throw new Error('useRecipes must be used within RecipeProvider');
  }
  return context;
};

export const RecipeProvider = ({ children }) => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    pages: 0,
  });

  const fetchRecipes = useCallback(async (filters = {}, page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await recipeService.getRecipes(filters, page, pagination.pageSize);
      setRecipes(data.items);
      setPagination({
        page: data.page,
        pageSize: data.page_size,
        total: data.total,
        pages: data.pages,
      });
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to fetch recipes');
    } finally {
      setLoading(false);
    }
  }, [pagination.pageSize]);

  const createRecipe = useCallback(async (recipeData) => {
    setLoading(true);
    setError(null);
    try {
      const newRecipe = await recipeService.createRecipe(recipeData);
      setRecipes((prev) => [newRecipe, ...prev]);
      return newRecipe;
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to create recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateRecipe = useCallback(async (id, updates) => {
    setLoading(true);
    setError(null);
    try {
      const updatedRecipe = await recipeService.updateRecipe(id, updates);
      setRecipes((prev) =>
        prev.map((recipe) => (recipe.id === id ? updatedRecipe : recipe))
      );
      return updatedRecipe;
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteRecipe = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await recipeService.deleteRecipe(id);
      setRecipes((prev) => prev.filter((recipe) => recipe.id !== id));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to delete recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const value = {
    recipes,
    loading,
    error,
    pagination,
    fetchRecipes,
    createRecipe,
    updateRecipe,
    deleteRecipe,
  };

  return <RecipeContext.Provider value={value}>{children}</RecipeContext.Provider>;
};
```

**Usage in Component**:
```javascript
import React, { useEffect } from 'react';
import { useRecipes } from '../context/RecipeContext';

const RecipeListPage = () => {
  const { recipes, loading, error, pagination, fetchRecipes } = useRecipes();

  useEffect(() => {
    fetchRecipes();
  }, [fetchRecipes]);

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1>Recipes</h1>
      <RecipeGrid recipes={recipes} />
      <Pagination {...pagination} onChange={(page) => fetchRecipes({}, page)} />
    </div>
  );
};
```

---

### Responsive Design

**Breakpoints** (TailwindCSS defaults):
- `sm`: 640px (mobile landscape)
- `md`: 768px (tablet)
- `lg`: 1024px (desktop)
- `xl`: 1280px (large desktop)

**Layout Patterns**:

**Mobile (< 768px)**:
- Single column layout
- Stacked components
- Collapsible filter panel (drawer/modal)
- Full-width recipe cards
- Bottom navigation (optional)

**Tablet (768px - 1024px)**:
- Two-column grid for recipe cards
- Side-by-side form sections
- Expanded filter panel (collapsible)

**Desktop (> 1024px)**:
- Three-column grid for recipe cards
- Fixed sidebar for filters
- Multi-column forms
- Larger images and text

---

### Performance Optimization

**Code Splitting**:
- Lazy load routes
- Dynamic imports for heavy components

**Image Optimization**:
- Use placeholder images (recipe photos not implemented yet)
- Lazy loading for images below fold
- Responsive image sizes

**API Optimization**:
- Debounce search inputs (500ms)
- Cache API responses (React Query)
- Pagination to limit data fetched
- Prefetch next page on hover (optional)

**Rendering Optimization**:
- Virtualized lists for long recipe lists (react-window)
- Memoization for expensive computations (useMemo, React.memo)
- Avoid unnecessary re-renders

---

## Error Handling

### API Error Responses

All errors follow this format:
```json
{
  "error": {
    "message": "Human-readable error message",
    "type": "ErrorType",
    "request_id": "uuid-for-tracing",
    "details": {}  // Optional additional info
  }
}
```

**HTTP Status Codes**:

| Code | Meaning | Use Case | Frontend Action |
|------|---------|----------|-----------------|
| 200 | OK | Success | Display data |
| 201 | Created | Resource created | Show success, redirect |
| 202 | Accepted | Async job started | Show job info, allow navigation |
| 204 | No Content | Delete success | Show success, redirect |
| 400 | Bad Request | Validation failed | Display validation errors |
| 403 | Forbidden | No permission | Show access denied message |
| 404 | Not Found | Resource missing | Show not found page or message |
| 405 | Method Not Allowed | Wrong HTTP method | Log error (shouldn't happen) |
| 422 | Unprocessable Entity | Pydantic validation | Display field errors |
| 500 | Internal Server Error | Server error | Show generic error, retry button |
| 504 | Gateway Timeout | External service timeout | Show timeout message, retry |

---

### Frontend Error Handling Strategy

**1. Network Errors**:
```javascript
if (!error.response) {
  // No response from server
  showToast('error', 'Cannot connect to server. Please check your internet connection.');
}
```

**2. Validation Errors (400, 422)**:
```javascript
if (error.response.status === 400 || error.response.status === 422) {
  const errorMessage = error.response.data.error.message;
  // Display inline on form fields
  setFieldError(errorMessage);
  // Or show toast for general validation
  showToast('error', errorMessage);
}
```

**3. Not Found (404)**:
```javascript
if (error.response.status === 404) {
  // Redirect to 404 page or show inline message
  navigate('/404');
  // Or show toast
  showToast('error', 'Recipe not found. It may have been deleted.');
}
```

**4. Server Errors (500)**:
```javascript
if (error.response.status >= 500) {
  const requestId = error.response.data.error.request_id;
  showToast('error', `Something went wrong. Please try again. (ID: ${requestId})`);
  // Log to error tracking service (Sentry, etc.)
  logError(error, requestId);
}
```

**5. Retry Logic**:
```javascript
const retryRequest = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};

// Usage
const recipes = await retryRequest(() => recipeService.getRecipes());
```

---

### User-Friendly Error Messages

**Mapping Technical Errors to User Messages**:

| Technical Error | User-Friendly Message |
|-----------------|----------------------|
| "Recipe with this name already exists" | "A recipe with this name already exists. Please choose a different name." |
| "Validation failed: prep_time must be >= 0" | "Preparation time must be a positive number." |
| "Recipe not found with id: {uuid}" | "This recipe could not be found. It may have been deleted." |
| "Database connection failed" | "We're having trouble connecting to our servers. Please try again in a moment." |
| "Gemini API rate limit exceeded" | "Too many search requests. Please wait a moment and try again." |

---

## Future Enhancements

### Phase 1: Authentication & Authorization

**Features**:
- User registration and login
- JWT-based authentication
- User profile management
- Recipe ownership (creator can edit/delete their own recipes)
- Public vs. private recipes
- User favorites and collections

**API Changes**:
- Add `user_id` to Recipe model
- New endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
- Protect endpoints with authentication middleware
- Add `Authorization` header to all requests

**Frontend Changes**:
- Login/Register pages
- Auth context for token management
- Protected routes (require authentication)
- User menu in navbar
- "My Recipes" page

---

### Phase 2: Recipe Ratings & Reviews

**Features**:
- Star ratings (1-5)
- Text reviews
- Average rating display
- Sort by rating
- User voting (helpful/not helpful for reviews)

**API Changes**:
- New models: Rating, Review
- Endpoints: POST `/api/recipes/{id}/rate`, GET `/api/recipes/{id}/reviews`

**Frontend Changes**:
- Rating component (stars)
- Reviews section on recipe detail page
- Filter by minimum rating

---

### Phase 3: User Collections

**Features**:
- Create collections (e.g., "Weeknight Dinners", "Holiday Recipes")
- Add recipes to collections
- Share collections with others
- Follow other users' collections

**API Changes**:
- Collection model
- Endpoints: `/api/collections`, `/api/collections/{id}/recipes`

**Frontend Changes**:
- Collection management pages
- Add to collection button on recipes
- Browse collections page

---

### Phase 4: Meal Planning

**Features**:
- Weekly meal planner calendar
- Drag-and-drop recipes to days
- Generate shopping list from meal plan
- Nutritional summary for the week

**API Changes**:
- MealPlan model
- Endpoints: `/api/meal-plans`, `/api/meal-plans/{id}/shopping-list`

**Frontend Changes**:
- Calendar component for meal planning
- Shopping list generator
- Nutritional dashboard

---

### Phase 5: Social Features

**Features**:
- Share recipes on social media
- Recipe comments
- Follow other users
- Activity feed
- Recipe remixes (fork and modify)

**API Changes**:
- Comment model
- Follow relationship model
- Endpoints: `/api/recipes/{id}/comments`, `/api/users/{id}/follow`

**Frontend Changes**:
- Comment section
- Social share buttons
- User profile pages
- Activity feed

---

### Phase 6: Advanced Search

**Features**:
- Fuzzy search (typo tolerance)
- Autocomplete suggestions
- Search history
- Saved searches
- Advanced filters (allergens, equipment needed, etc.)

**API Changes**:
- Implement trigram search
- Add autocomplete endpoint
- SearchHistory model

**Frontend Changes**:
- Autocomplete component
- Search suggestions dropdown
- Saved searches UI

---

### Phase 7: Recipe Generation (AI)

**Features**:
- Generate recipe from ingredients list
- Suggest variations on existing recipes
- Ingredient substitution suggestions
- Cooking technique explanations

**API Changes**:
- LangGraph workflow for recipe generation
- Endpoints: POST `/api/recipes/generate`, GET `/api/ingredients/{name}/substitutes`

**Frontend Changes**:
- Recipe generator form
- Ingredient input with suggestions
- Variation generator UI

---

### Phase 8: Multimedia Support

**Features**:
- Upload recipe photos
- Step-by-step cooking videos
- Photo gallery for recipes
- Video tutorials

**API Changes**:
- Image upload endpoints
- Media storage (S3 or similar)
- Image resizing/optimization

**Frontend Changes**:
- Image upload components
- Photo gallery
- Video player

---

## Appendix

### Example API Calls with cURL

**Create Recipe**:
```bash
curl -X POST http://localhost:8009/api/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Recipe",
    "description": "A test recipe",
    "instructions": {"steps": ["Step 1", "Step 2"]},
    "prep_time": 10,
    "cook_time": 15,
    "servings": 4,
    "difficulty": "easy",
    "ingredients": [
      {"name": "flour", "quantity": 2, "unit": "cups"}
    ],
    "category_ids": []
  }'
```

**Hybrid Search**:
```bash
curl -X POST http://localhost:8009/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quick pasta",
    "limit": 5,
    "use_semantic": true,
    "use_filters": true
  }'
```

**List Recipes with Filters**:
```bash
curl "http://localhost:8009/api/recipes?cuisine_type=Italian&difficulty=easy&page=1&page_size=10"
```

**Get Recipe by ID**:
```bash
curl http://localhost:8009/api/recipes/{recipe-uuid}
```

**Update Recipe**:
```bash
curl -X PUT http://localhost:8009/api/recipes/{recipe-uuid} \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Recipe Name",
    "prep_time": 20
  }'
```

**Delete Recipe**:
```bash
curl -X DELETE http://localhost:8009/api/recipes/{recipe-uuid}
```

**Find Similar Recipes**:
```bash
curl "http://localhost:8009/api/recipes/{recipe-uuid}/similar?limit=5"
```

---

### JSON Example Files

**Recipe JSON Format for Bulk Import**:
```json
[
  {
    "name": "Quick Tomato Pasta",
    "description": "Simple and fast tomato-based pasta",
    "instructions": {
      "steps": [
        "Boil pasta according to package directions",
        "Heat olive oil and sauté garlic",
        "Add crushed tomatoes and herbs",
        "Combine with cooked pasta",
        "Serve with Parmesan"
      ]
    },
    "prep_time": 5,
    "cook_time": 15,
    "servings": 2,
    "difficulty": "easy",
    "cuisine_type": "Italian",
    "diet_types": ["vegetarian"],
    "ingredients": [
      {
        "name": "pasta",
        "quantity": 200,
        "unit": "g"
      },
      {
        "name": "crushed tomatoes",
        "quantity": 400,
        "unit": "g"
      },
      {
        "name": "garlic",
        "quantity": 2,
        "unit": "cloves"
      },
      {
        "name": "olive oil",
        "quantity": 2,
        "unit": "tbsp"
      },
      {
        "name": "basil",
        "quantity": 5,
        "unit": "leaves"
      }
    ],
    "category_ids": [],
    "nutritional_info": {
      "calories": 380,
      "protein_g": 12,
      "carbohydrates_g": 58,
      "fat_g": 10,
      "fiber_g": 5,
      "sodium_mg": 450
    }
  }
]
```

---

### Glossary

| Term | Definition |
|------|------------|
| **Vector Embedding** | 768-dimensional numerical representation of recipe text, used for semantic similarity search |
| **Semantic Search** | AI-powered search that understands meaning and context, not just keywords |
| **Hybrid Search** | Combined semantic and filter-based search for better results |
| **Reciprocal Rank Fusion (RRF)** | Algorithm to merge results from multiple search strategies by ranking |
| **Soft Delete** | Marking records as deleted without removing from database (sets `deleted_at` timestamp) |
| **LangGraph** | Workflow orchestration framework for AI agents |
| **Gemini API** | Google's AI API for text generation and embeddings |
| **pgvector** | PostgreSQL extension for vector similarity search |
| **Cosine Similarity** | Metric for measuring similarity between vector embeddings |
| **Cache TTL** | Time To Live - how long cached data remains valid before expiring |

---

**End of Frontend Specification**

This document provides comprehensive information for developing a frontend application for the Recipe Management System. For API details, refer to the OpenAPI documentation at `http://localhost:8009/api/docs`.
