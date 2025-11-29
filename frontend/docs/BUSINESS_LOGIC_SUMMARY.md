# Recipe Management System - Business Logic & Processes Summary

**Version:** 1.0.0
**Last Updated:** 2025-11-15

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Core Business Processes](#core-business-processes)
3. [AI Integration & Workflows](#ai-integration--workflows)
4. [Data Validation Rules](#data-validation-rules)
5. [Search Algorithm Deep Dive](#search-algorithm-deep-dive)
6. [Caching & Performance Strategy](#caching--performance-strategy)
7. [Key Business Metrics](#key-business-metrics)

---

## System Architecture Overview

### Technology Stack

**Backend:**
- **Framework:** FastAPI (async Python web framework)
- **Database:** PostgreSQL 15+ with pgvector extension
- **Cache:** Redis 7
- **AI Services:** Google Gemini API (embeddings + text generation)
- **Workflow Engine:** LangGraph (AI agent orchestration)
- **ORM:** SQLAlchemy 2.0+ (async)

**Architecture Pattern:** Clean Architecture with Layered Approach

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                      │
│  - REST endpoints                                            │
│  - Request/response validation (Pydantic)                    │
│  - Middleware (CORS, logging, error handling)                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     Service Layer                            │
│  - RecipeService: CRUD + business logic                      │
│  - SearchService: Hybrid search orchestration                │
│  - EmbeddingService: AI embedding generation                 │
│  - CacheService: Redis caching logic                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Repository Layer                            │
│  - RecipeRepository: Database access for recipes             │
│  - VectorRepository: pgvector similarity search              │
│  - BaseRepository: Generic CRUD operations                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Database & External Services                    │
│  - PostgreSQL (recipes, ingredients, categories)             │
│  - pgvector (768-dim embeddings)                             │
│  - Redis (multi-level caching)                               │
│  - Gemini API (AI embeddings & text generation)              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**Recipe Creation Flow:**
```
User Request
    ↓
FastAPI Endpoint (POST /api/recipes)
    ↓
Pydantic Validation (RecipeCreate schema)
    ↓
RecipeService.create_recipe()
    ├─→ Validate business rules (name uniqueness, time constraints)
    ├─→ RecipeRepository.create() - Save to PostgreSQL
    ├─→ Create related entities (ingredients, nutritional info)
    ├─→ Link to categories (many-to-many)
    ├─→ EmbeddingService.create_recipe_embedding()
    │       ├─→ Construct text: "Name | Description | Cuisine | Diet | Difficulty"
    │       ├─→ Check cache (24h TTL)
    │       ├─→ Call Gemini API if not cached
    │       └─→ Return 768-dimensional vector
    ├─→ Update recipe with embedding
    └─→ Cache recipe data (1h TTL)
    ↓
Return RecipeResponse to user
```

**Hybrid Search Flow:**
```
User Query: "quick vegetarian pasta under 30 minutes"
    ↓
SearchService.hybrid_search()
    ├─→ Check cache (15min TTL)
    │   └─→ If hit: Return cached results
    ├─→ Cache miss: Execute workflow
    └─→ LangGraph SearchPipelineGraph.run()
            ├─→ [Node 1] parse_query (Gemini AI)
            │       └─→ Extract: cuisine, diet_types, max_time, ingredients
            │
            ├─→ [Node 2] generate_embedding (Gemini API)
            │       └─→ Convert query → 768-dim vector
            │
            ├─→ [Node 3] Parallel execution:
            │       ├─→ vector_search (pgvector cosine similarity)
            │       │       └─→ Find recipes by embedding similarity
            │       └─→ filter_search (SQL WHERE clauses)
            │               └─→ Find recipes matching filters
            │
            ├─→ [Node 4] merge_results (RRF algorithm)
            │       └─→ Combine semantic + filter results
            │
            ├─→ [Node 5] judge_relevance (Quality filtering)
            │       ├─→ Evaluate semantic score
            │       ├─→ Check filter compliance
            │       ├─→ Validate dietary requirements
            │       └─→ Filter low-quality results
            │
            ├─→ [Node 6] rerank (Optional, Gemini AI)
            │       └─→ Re-score results for better relevance
            │
            └─→ [Node 7] format_response
                    └─→ Structure final results
    ↓
Cache results (15min TTL)
    ↓
Return SearchResponse to user
```

---

## Core Business Processes

### 1. Recipe Lifecycle Management

#### Creation Process

**Inputs:**
- Recipe metadata (name, description, cuisine, difficulty, etc.)
- Ingredients list (name, quantity, unit, notes)
- Category IDs (existing categories to link)
- Nutritional information (optional)
- Cooking instructions (JSON format)

**Business Rules Enforced:**

1. **Name Uniqueness**
   - Query database for existing recipe with same name (case-insensitive)
   - Raise error if duplicate found
   - Ensures recipes are distinguishable

2. **Time Constraints**
   - `prep_time + cook_time < 1440 minutes` (24 hours)
   - Individual times must be >= 0
   - Prevents unrealistic cooking times

3. **Servings Validation**
   - Must be > 0 if provided
   - Ensures practical recipe usage

4. **Instructions Requirement**
   - Instructions JSON cannot be empty
   - Must contain at least basic structure
   - Prevents incomplete recipes

**Automatic Processing:**

1. **Embedding Generation**
   - Triggered automatically on creation
   - Text format: `"{name} | {description} | Cuisine: {cuisine_type} | Diet: {diet_types} | Difficulty: {difficulty}"`
   - Sent to Gemini API for vectorization
   - Stored in `embedding` column (768 dimensions)
   - Enables semantic search

2. **Relationship Creation**
   - Ingredients: Cascade created with recipe
   - Categories: Linked via junction table (RecipeCategory)
   - Nutritional Info: One-to-one creation
   - All within single database transaction

3. **Metadata Timestamps**
   - `created_at`: Set to current UTC timestamp
   - `updated_at`: Set to current UTC timestamp
   - `deleted_at`: NULL (not deleted)

**Output:**
- Complete RecipeResponse with all relationships
- HTTP 201 Created status
- Recipe cached for 1 hour

---

#### Update Process

**Inputs:**
- Recipe ID (UUID)
- Partial updates (only changed fields)

**Business Rules:**

1. **Existence Check**
   - Recipe must exist and not be deleted
   - Raise 404 if not found

2. **Name Uniqueness (if name changed)**
   - Check for duplicates excluding current recipe
   - Raise 400 if duplicate

3. **Selective Embedding Regeneration**
   - Regenerate if any of these fields change:
     - `name`
     - `description`
     - `cuisine_type`
     - `diet_types`
     - `difficulty`
   - Skip if only time/servings/instructions changed
   - Optimizes API usage

**Automatic Processing:**

1. **Timestamp Update**
   - `updated_at` → current UTC timestamp
   - `created_at` unchanged

2. **Cache Invalidation (Cascade)**
   - Delete recipe cache: `recipe:{id}`
   - Delete all search caches: `search:*`
   - Delete stats caches: `stats:*`
   - Ensures fresh data on next request

3. **Transaction Management**
   - All updates in single transaction
   - Rollback on any error
   - Ensures data consistency

**Output:**
- Updated RecipeResponse
- HTTP 200 OK status

---

#### Deletion Process (Soft Delete)

**Input:**
- Recipe ID (UUID)

**Business Rules:**

1. **Existence Check**
   - Recipe must exist and not already deleted
   - Raise 404 if not found

2. **Soft Delete Implementation**
   - Set `deleted_at` → current UTC timestamp
   - Do NOT remove from database
   - All relationships preserved

**Automatic Processing:**

1. **Automatic Exclusion**
   - All queries filter: `WHERE deleted_at IS NULL`
   - Recipe disappears from lists and searches
   - Detail endpoint returns 404

2. **Cache Invalidation**
   - Same cascade as update
   - Ensures deleted recipe doesn't appear cached

3. **Recovery Capability**
   - Can be restored by setting `deleted_at = NULL` (backend only)
   - Soft delete enables recovery from mistakes

**Output:**
- HTTP 204 No Content (empty response)

---

### 2. Search & Discovery

#### Filter-Based Search

**Purpose:** Traditional attribute-based recipe filtering

**Supported Filters:**
- `name`: Partial match (case-insensitive, uses PostgreSQL ILIKE)
- `cuisine_type`: Exact match
- `difficulty`: Enum match (easy/medium/hard)
- `diet_types`: Array contains any (OR logic)
- `category_ids`: Recipe linked to any of the categories
- Time ranges: `min_prep_time`, `max_prep_time`, `min_cook_time`, `max_cook_time`
- Servings range: `min_servings`, `max_servings`

**Query Construction:**
```sql
SELECT * FROM recipes
WHERE deleted_at IS NULL
  AND (name ILIKE '%pasta%')                    -- Partial name match
  AND cuisine_type = 'Italian'                   -- Exact cuisine
  AND difficulty = 'easy'                        -- Difficulty level
  AND diet_types @> ARRAY['vegetarian']          -- Contains diet type
  AND prep_time <= 30                            -- Max prep time
  AND cook_time <= 45                            -- Max cook time
  AND id IN (
      SELECT recipe_id FROM recipe_categories
      WHERE category_id IN ('uuid1', 'uuid2')    -- Category filter
  )
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

**Performance Optimizations:**
- Indexes on: `name`, `cuisine_type`, `difficulty`, `created_at`
- Composite index on `(cuisine_type, difficulty)`
- GIN index on `name` for trigram search (future: fuzzy matching)
- Eager loading relationships (ingredients, categories) to avoid N+1 queries

**Score Assignment:**
- All filter matches receive uniform score of `1.0`
- No ranking within filter results
- Ordered by `created_at DESC` by default

---

#### Semantic Search (Vector Similarity)

**Purpose:** AI-powered search understanding meaning and context

**Process:**

1. **Query Embedding**
   - User query: "creamy pasta"
   - Task type: `retrieval_query` (optimized for matching)
   - Gemini API generates 768-dimensional vector
   - Cached for 24 hours

2. **Vector Similarity Search**
   - Use pgvector extension
   - Distance metric: Cosine distance (`<=>` operator)
   - Query:
     ```sql
     SELECT id, name, embedding, (1 - (embedding <=> query_vector)) AS score
     FROM recipes
     WHERE deleted_at IS NULL AND embedding IS NOT NULL
     ORDER BY embedding <=> query_vector
     LIMIT 50;
     ```
   - `embedding <=> query_vector`: Cosine distance (0-2, lower = more similar)
   - `1 - distance`: Similarity score (0-1, higher = more similar)

3. **Index Optimization**
   - HNSW index on `embedding` column:
     ```sql
     CREATE INDEX recipes_embedding_idx
     ON recipes
     USING hnsw (embedding vector_cosine_ops);
     ```
   - Approximate nearest neighbor (ANN) for fast search
   - Trade-off: 95%+ accuracy with 10x speed improvement

**Advantages:**
- Understands synonyms: "quick" matches "fast", "easy"
- Context-aware: "creamy pasta" finds "Alfredo", "Carbonara"
- Language-agnostic potential: Gemini supports multilingual embeddings

**Limitations:**
- Requires embedding generation (API call overhead)
- Only works for recipes with embeddings (generated on creation)
- Less precise than exact filters for specific attributes

---

#### Hybrid Search (Recommended)

**Purpose:** Best of both worlds - semantic understanding + precise filtering

**Workflow (LangGraph State Machine):**

**State Definition:**
```python
class SearchPipelineState:
    query: str                           # Original user query
    parsed_query: ParsedQuery            # AI-extracted components
    filters: dict                        # Structured filters
    embedding: list[float]               # Query vector
    vector_results: list[Recipe]         # Semantic results
    filter_results: list[Recipe]         # Filter results
    merged_results: list[Recipe]         # Combined results
    judge_metrics: dict                  # Quality metrics
    filtered_results: list[Recipe]       # Post-judge results
    final_results: list[Recipe]          # Final output
    metadata: dict                       # Workflow metadata
```

**Node-by-Node Execution:**

**1. parse_query (AI-Powered)**
- **Input:** User query string
- **Process:** Send to Gemini API with prompt:
  ```
  Parse this recipe search query and extract:
  - Ingredients mentioned
  - Cuisine type
  - Diet types
  - Time constraints
  - Difficulty level
  - Semantic query (cleaned for vector search)
  ```
- **Output:** Structured ParsedQuery object
- **Example:**
  ```json
  {
    "original_query": "quick vegetarian pasta under 30 minutes",
    "ingredients": ["pasta"],
    "cuisine_type": "Italian",
    "diet_types": ["vegetarian"],
    "max_prep_time": 30,
    "max_cook_time": null,
    "difficulty": null,
    "semantic_query": "vegetarian pasta"
  }
  ```
- **Error Handling:** If parsing fails, use original query for semantic search

**2. generate_embedding**
- **Input:** `semantic_query` from parsed query
- **Process:**
  - Check cache: `embedding:{hash(semantic_query)}`
  - If miss: Call Gemini API with task_type="retrieval_query"
  - Store in cache (24h TTL)
- **Output:** 768-dimensional vector
- **Cache Hit Rate:** ~70% for common queries

**3. extract_filters**
- **Input:** `parsed_query`
- **Process:** Convert to database filter dictionary
- **Output:**
  ```python
  {
      "cuisine_type": "Italian",
      "diet_types": ["vegetarian"],
      "max_prep_time": 30
  }
  ```

**4. Parallel Execution (vector_search + filter_search)**

**4a. vector_search**
- Uses embedding from step 2
- pgvector cosine similarity
- Returns top 50 results with scores

**4b. filter_search**
- Uses filters from step 3
- SQL WHERE clauses
- Returns matching recipes (up to 50)

**5. merge_results (Reciprocal Rank Fusion)**

**Algorithm:**
```python
def reciprocal_rank_fusion(results_lists: list[list[Recipe]], k=60):
    scores = defaultdict(float)

    for results in results_lists:
        for rank, recipe in enumerate(results, start=1):
            scores[recipe.id] += 1 / (k + rank)

    # Sort by score descending
    merged = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return merged
```

**Why RRF?**
- Balances different ranking systems (semantic scores vs. uniform filter scores)
- Gives bonus to recipes appearing in both result sets
- Parameter `k=60` controls rank contribution (standard value)
- No need to normalize scores from different sources

**Example:**
```
Semantic Results (with scores):
1. Recipe A (score: 0.95)
2. Recipe B (score: 0.88)
3. Recipe C (score: 0.82)

Filter Results (uniform score: 1.0):
1. Recipe B
2. Recipe D
3. Recipe E

RRF Calculation (k=60):
Recipe A: 1/(60+1) = 0.0164
Recipe B: 1/(60+1) + 1/(60+1) = 0.0328  ← Appears in both!
Recipe C: 1/(60+3) = 0.0159
Recipe D: 1/(60+2) = 0.0161
Recipe E: 1/(60+3) = 0.0159

Final Ranking: B, A, D, C, E
```

**6. judge_relevance (Quality Control)**

**Purpose:** Filter out low-quality results based on configurable thresholds

**Judge Configuration:**
```python
class JudgeConfig:
    semantic_threshold: float = 0.0        # Min semantic similarity (0-1)
    filter_compliance_min: float = 0.0     # Min % of filters matched
    ingredient_match_min: float = 0.0      # Min ingredient match ratio
    dietary_strict_mode: bool = True       # Enforce diet restrictions
    confidence_threshold: float = 0.0      # Min overall confidence
    min_results: int = 0                   # Min results to return
    max_results: int = 100                 # Max results to return
    fallback_strategy: str = "RELAX_THRESHOLDS"  # What to do if min not met
```

**Evaluation Metrics:**

For each result:
1. **Semantic Score:** From vector search (0-1)
2. **Filter Compliance:** Matched filters / Total filters (0-1)
3. **Dietary Compliance:** Boolean (all diet requirements met?)
4. **Confidence Score:** Weighted average:
   ```
   confidence = 0.4 * semantic + 0.4 * filter_compliance + 0.2 * ingredient_match
   ```

**Filtering Logic:**
```python
def evaluate_result(recipe, parsed_query, config):
    # Check thresholds
    if recipe.semantic_score < config.semantic_threshold:
        return False, "Low semantic score"

    if recipe.filter_compliance < config.filter_compliance_min:
        return False, "Low filter compliance"

    if config.dietary_strict_mode:
        if not recipe.meets_dietary_requirements(parsed_query.diet_types):
            return False, "Dietary restriction violation"

    if recipe.confidence < config.confidence_threshold:
        return False, "Low confidence"

    return True, "Passed"
```

**Fallback Strategy:**
- If `len(filtered_results) < min_results`:
  - `RELAX_THRESHOLDS`: Reduce thresholds by 50% and re-evaluate
  - `EMPTY_RESULTS`: Return empty list (strict mode)
  - `SUGGEST_ALTERNATIVES`: Generate alternative queries (future)

**Judge Report:**
```json
{
    "original_count": 15,
    "filtered_count": 8,
    "removed_count": 7,
    "metrics": {
        "total_evaluated": 15,
        "passed_semantic": 12,
        "passed_filter": 10,
        "passed_dietary": 13,
        "failed_semantic": 3,
        "failed_filter": 5,
        "failed_dietary": 2
    },
    "config": { /* judge config used */ }
}
```

**7. rerank (Optional AI Enhancement)**

**When Triggered:**
- `use_reranking: true` in request
- AND `len(filtered_results) > 3`
- AND `removed_count > 5` (significant filtering occurred)

**Process:**
1. Limit to top 20 results (API token efficiency)
2. Send to Gemini with prompt:
   ```
   Query: "{original_query}"

   Rank these recipes by relevance (1-10 scale):
   1. {recipe1.name} - {recipe1.description}
   2. {recipe2.name} - {recipe2.description}
   ...

   Return scores as JSON.
   ```
3. Receive new scores from AI
4. Boost RRF scores: `new_score = old_score * (ai_score / 10)`
5. Re-sort by new scores

**Cost-Benefit:**
- Adds 1-2 seconds latency
- Improves relevance by ~15-20% (subjective)
- Use sparingly for complex queries

**8. format_response**

**Final Output Structure:**
```python
SearchResponse(
    query="original query",
    parsed_query=ParsedQuery(...),
    results=[
        SearchResult(
            recipe=RecipeResponse(...),
            score=0.95,
            distance=0.05,
            match_type="hybrid"
        ),
        ...
    ],
    total=8,
    search_type="hybrid",
    metadata={
        "semantic_results": 12,
        "filter_results": 6,
        "merged_results": 15,
        "judge_removed": 7,
        "final_results": 8,
        "reranked": False
    }
)
```

**Conditional Routing:**

```
parse_query
    ↓
    ├─ Has semantic_query? → generate_embedding → vector_search
    │                                                     ↓
    └─ Has filters? → extract_filters → filter_search →  merge_results
                                                              ↓
                                                        judge_relevance
                                                              ↓
                                                   ├─ Removed > 5? → rerank
                                                   └─ Else → skip rerank
                                                              ↓
                                                        format_response
```

---

## AI Integration & Workflows

### Gemini API Usage

**Model: `text-embedding-004`**
- **Purpose:** Generate 768-dimensional vectors for semantic search
- **Input:** Text strings (recipe metadata or search queries)
- **Output:** Float array of 768 dimensions
- **Cost:** ~$0.00025 per 1000 characters (very cheap)
- **Latency:** ~500-1000ms per request

**Model: `gemini-2.0-flash-exp`**
- **Purpose:** Text generation (query parsing, reranking)
- **Input:** Prompts with structured instructions
- **Output:** JSON or text responses
- **Cost:** ~$0.075 per 1M input tokens, $0.30 per 1M output tokens
- **Latency:** ~1-2 seconds per request

**Task Types for Embeddings:**
1. **retrieval_document**: Indexing recipes (creation/update)
   - Optimizes embedding for being searched
2. **retrieval_query**: Search queries
   - Optimizes embedding for finding matches
3. **semantic_similarity**: Finding similar recipes
   - Optimizes for comparing two items

**Rate Limiting:**
- Default: 60 requests per minute
- Implemented client-side with async lock
- Automatic sleep between requests: `sleep(60 / rate_limit)`
- Prevents 429 errors from API

**Retry Logic:**
- Max retries: 3
- Exponential backoff: 1s, 2s, 4s
- Retries on transient errors (network issues, 5xx responses)
- Fails fast on 4xx errors (invalid requests)

---

### LangGraph Workflow Details

**LangGraph:** Framework for building stateful, multi-step agent workflows

**StateGraph Definition:**
```python
from langgraph.graph import StateGraph

# Define state schema
class SearchPipelineState(TypedDict):
    query: str
    parsed_query: dict
    # ... more fields

# Create graph
workflow = StateGraph(SearchPipelineState)

# Add nodes
workflow.add_node("parse_query", parse_query_node)
workflow.add_node("generate_embedding", generate_embedding_node)
workflow.add_node("vector_search", vector_search_node)
# ... more nodes

# Add edges (unconditional)
workflow.add_edge("parse_query", "generate_embedding")
workflow.add_edge("generate_embedding", "vector_search")

# Add conditional edges
def should_rerank(state):
    if state.get("removed_count", 0) > 5:
        return "rerank"
    return "skip"

workflow.add_conditional_edges(
    "judge_relevance",
    should_rerank,
    {"rerank": "rerank", "skip": "format_response"}
)

# Compile
app = workflow.compile()

# Run
result = await app.ainvoke({"query": "quick pasta"})
```

**Benefits:**
1. **Modularity:** Each node is independently testable
2. **Observability:** State tracked at each step
3. **Flexibility:** Conditional routing based on state
4. **Maintainability:** Clear separation of workflow logic
5. **Debugging:** Can inspect state at any node

**State Persistence:**
- Currently in-memory (workflow execution completes in seconds)
- Future: Can persist to database for long-running workflows
- Enables pause/resume and human-in-the-loop

---

## Data Validation Rules

### Recipe Validation

**At Creation:**
```python
# Name validation
- Required: Yes
- Min length: 1 character
- Max length: 255 characters
- Trimmed: Yes (leading/trailing whitespace removed)
- Unique: Yes (case-insensitive check)

# Description validation
- Required: No
- Type: String (text)

# Instructions validation
- Required: Yes
- Type: JSON object (dict)
- Cannot be empty: Yes
- Example: {"steps": ["Step 1", "Step 2"]}

# Prep time validation
- Required: No
- Type: Integer
- Min value: 0 (minutes)
- Max value: 1440 (24 hours minus cook time)

# Cook time validation
- Required: No
- Type: Integer
- Min value: 0 (minutes)
- Max value: 1440 (24 hours minus prep time)

# Total time validation
- Constraint: prep_time + cook_time < 1440 minutes (24 hours)

# Servings validation
- Required: No
- Type: Integer
- Min value: 1 (must serve at least one person)

# Difficulty validation
- Required: Yes (default: "medium")
- Type: Enum
- Allowed values: "easy", "medium", "hard"

# Cuisine type validation
- Required: No
- Type: String
- Max length: 100 characters
- Trimmed: Yes

# Diet types validation
- Required: No (default: [])
- Type: Array of strings
- Empty strings removed
- Each item trimmed
- Common values: "vegetarian", "vegan", "gluten-free", "dairy-free", "keto", "paleo"
```

**At Update:**
- All fields optional (partial updates)
- Same validation rules apply to provided fields
- Name uniqueness checked excluding current recipe
- Embedding regeneration logic:
  ```python
  needs_embedding_update = any([
      "name" in updates,
      "description" in updates,
      "cuisine_type" in updates,
      "diet_types" in updates,
      "difficulty" in updates
  ])
  ```

---

### Ingredient Validation

```python
# Name validation
- Required: Yes
- Min length: 1 character
- Max length: 255 characters
- Trimmed: Yes

# Quantity validation
- Required: No
- Type: Float
- Min value: 0 (cannot be negative)

# Unit validation
- Required: No
- Type: String
- Max length: 50 characters
- Trimmed: Yes
- Empty string converted to NULL
- Common values: "g", "kg", "ml", "l", "cup", "tbsp", "tsp", "pieces", "oz", "lb"

# Notes validation
- Required: No
- Type: String (text)
```

---

### Nutritional Info Validation

```python
# All nutritional fields follow same pattern:
- Required: No
- Type: Float
- Min value: 0 (cannot be negative)

# Fields:
- calories: Calories per serving
- protein_g: Protein in grams
- carbohydrates_g: Carbohydrates in grams
- fat_g: Fat in grams
- fiber_g: Fiber in grams
- sugar_g: Sugar in grams
- sodium_mg: Sodium in milligrams
- cholesterol_mg: Cholesterol in milligrams

# Additional info validation
- Required: No
- Type: JSON object (dict)
- Can contain custom nutritional data
- Example: {"vitamin_c_mg": 25, "iron_mg": 2}
```

---

### Category Validation

```python
# Name validation
- Required: Yes
- Min length: 1 character
- Max length: 100 characters
- Trimmed: Yes
- Unique: Yes (across all categories)

# Slug validation
- Required: Yes
- Min length: 1 character
- Max length: 100 characters
- Format: Lowercase alphanumeric with hyphens
- Pattern: ^[a-z0-9-]+$
- Unique: Yes (across all categories)
- Example: "main-dishes", "desserts", "quick-meals"

# Description validation
- Required: No
- Type: String (text)

# Parent ID validation
- Required: No
- Type: UUID
- Must reference existing category
- Circular references prevented
```

---

## Search Algorithm Deep Dive

### Reciprocal Rank Fusion (RRF) Mathematics

**Purpose:** Combine rankings from different search systems without score normalization

**Formula:**
```
For each recipe r in union of all result sets:
    RRF_score(r) = Σ (1 / (k + rank_i(r)))

Where:
- k: constant (typically 60)
- rank_i(r): rank of recipe r in result set i (1-indexed)
- Σ: sum across all result sets where r appears
```

**Example Calculation:**

Given:
- Semantic results: [A, B, C, D] (scores: 0.95, 0.88, 0.82, 0.75)
- Filter results: [B, E, F] (uniform score: 1.0)
- k = 60

RRF scores:
```
Recipe A: 1/(60+1) = 0.0164
Recipe B: 1/(60+1) + 1/(60+1) = 0.0328
Recipe C: 1/(60+3) = 0.0159
Recipe D: 1/(60+4) = 0.0156
Recipe E: 1/(60+2) = 0.0161
Recipe F: 1/(60+3) = 0.0159

Final ranking by RRF score:
1. B (0.0328) ← Boosted for appearing in both
2. A (0.0164)
3. E (0.0161)
4. C (0.0159)
5. F (0.0159)
6. D (0.0156)
```

**Properties:**
- **Rank-based:** Uses positions, not raw scores
- **Fusion-friendly:** Combines heterogeneous ranking systems
- **Overlap bonus:** Recipes in multiple result sets get higher scores
- **Parameter-free:** k=60 works well in most cases
- **Proven effective:** Used in information retrieval research

---

### Cosine Similarity Calculation

**Purpose:** Measure similarity between two vectors (recipe embedding and query embedding)

**Formula:**
```
cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)

Where:
- A · B: dot product of vectors A and B
- ||A||: Euclidean norm of A (sqrt(Σ a_i²))
- ||B||: Euclidean norm of B
```

**Cosine Distance:**
```
cosine_distance = 1 - cosine_similarity
```

**Range:**
- Cosine similarity: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite)
- Cosine distance: 0 to 2 (0 = identical, 1 = orthogonal, 2 = opposite)

**In pgvector:**
```sql
SELECT embedding <=> query_vector AS cosine_distance
FROM recipes;
```

**Conversion to Similarity Score:**
```python
similarity_score = 1 - cosine_distance
```

**Why Cosine?**
- Magnitude-independent: Focuses on direction, not length
- Suitable for high-dimensional spaces (768 dimensions)
- Efficient to compute with vector operations
- Standard metric for text embeddings

---

### HNSW Index (Hierarchical Navigable Small World)

**Purpose:** Approximate nearest neighbor search for fast vector queries

**Structure:**
- Multi-layer graph
- Each layer is a subset of the layer below
- Top layer: Few nodes, long connections
- Bottom layer: All nodes, local connections

**Search Process:**
1. Start at top layer with random entry point
2. Greedily navigate to closest node
3. Move down a layer
4. Repeat until bottom layer
5. Perform local search at bottom layer

**Trade-off:**
- Accuracy: ~95-99% (configurable)
- Speed: 10-100x faster than brute force
- Memory: Additional index storage

**Configuration in PostgreSQL:**
```sql
CREATE INDEX recipes_embedding_idx
ON recipes
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- m: Max connections per node (higher = better accuracy, more memory)
-- ef_construction: Size of dynamic candidate list (higher = better index quality)
```

---

## Caching & Performance Strategy

### Multi-Level Caching

**Level 1: Recipe Cache**
- **Key:** `recipe:{uuid}`
- **Value:** Full RecipeResponse JSON
- **TTL:** 3600 seconds (1 hour)
- **Purpose:** Avoid database queries for frequently accessed recipes
- **Invalidation:** On recipe update/delete

**Level 2: Search Results Cache**
- **Key:** `search:{hash(query + filters)}`
- **Value:** SearchResponse JSON
- **TTL:** 900 seconds (15 minutes)
- **Purpose:** Avoid re-running search workflows for common queries
- **Invalidation:** On any recipe creation/update/delete (pattern: `search:*`)

**Level 3: Embedding Cache**
- **Key:** `embedding:{hash(text)}`
- **Value:** 768-dimensional float array
- **TTL:** 86400 seconds (24 hours)
- **Purpose:** Avoid repeated Gemini API calls for same text
- **Invalidation:** TTL-based only (embeddings are stable)

**Level 4: Stats Cache**
- **Key:** `stats:{type}` (e.g., `stats:cuisine_counts`)
- **Value:** Aggregation results JSON
- **TTL:** 300 seconds (5 minutes)
- **Purpose:** Expensive aggregation queries
- **Invalidation:** On recipe creation/update/delete

---

### Cache Invalidation Strategy

**Pattern-Based Invalidation:**
```python
async def invalidate_recipe_cache(recipe_id: UUID):
    # Invalidate specific recipe
    await cache.delete(f"recipe:{recipe_id}")

    # Invalidate all search results (pattern-based)
    await cache.delete_pattern("search:*")

    # Invalidate all stats
    await cache.delete_pattern("stats:*")
```

**Redis SCAN for Pattern Deletion:**
```python
async def delete_pattern(pattern: str):
    cursor = 0
    deleted = 0

    while True:
        # SCAN is non-blocking (unlike KEYS)
        cursor, keys = await redis.scan(cursor, match=pattern, count=100)

        if keys:
            await redis.delete(*keys)
            deleted += len(keys)

        if cursor == 0:
            break

    return deleted
```

**Why SCAN not KEYS?**
- KEYS blocks entire Redis (O(N) operation)
- SCAN is cursor-based, non-blocking
- SCAN iterates incrementally (O(1) per call)
- Production-safe for large key spaces

---

### Database Query Optimization

**Indexes:**
```sql
-- Single column indexes
CREATE INDEX idx_recipes_name ON recipes(name);
CREATE INDEX idx_recipes_cuisine_type ON recipes(cuisine_type);
CREATE INDEX idx_recipes_difficulty ON recipes(difficulty);
CREATE INDEX idx_recipes_created_at_desc ON recipes(created_at DESC);

-- Composite indexes
CREATE INDEX idx_recipes_cuisine_difficulty ON recipes(cuisine_type, difficulty);

-- GIN index for trigram search (partial name matching)
CREATE INDEX idx_recipes_name_trgm ON recipes USING gin (name gin_trgm_ops);

-- Vector index for semantic search
CREATE INDEX idx_recipes_embedding ON recipes USING hnsw (embedding vector_cosine_ops);

-- Soft delete filter index
CREATE INDEX idx_recipes_deleted_at ON recipes(deleted_at) WHERE deleted_at IS NULL;
```

**Eager Loading (N+1 Prevention):**
```python
# SQLAlchemy relationship configuration
ingredients: Mapped[list["Ingredient"]] = relationship(
    "Ingredient",
    back_populates="recipe",
    lazy="selectin"  # Eager load in single query
)

# Generates:
# SELECT * FROM recipes WHERE id = ?
# SELECT * FROM ingredients WHERE recipe_id IN (?, ?, ?)
# (Only 2 queries regardless of number of recipes)
```

**Connection Pooling:**
```python
# SQLAlchemy engine configuration
engine = create_async_engine(
    database_url,
    pool_size=5,                    # Persistent connections
    max_overflow=10,                # Additional connections on demand
    pool_timeout=30,                # Wait time for connection
    pool_recycle=3600,              # Recycle connections after 1 hour
    pool_pre_ping=True,             # Verify connection before use
)
```

---

## Key Business Metrics

### Performance Targets

**API Response Times:**
- List recipes (cached): < 50ms
- List recipes (uncached): < 200ms
- Get recipe by ID (cached): < 10ms
- Get recipe by ID (uncached): < 50ms
- Create recipe (no embedding): < 500ms
- Create recipe (with embedding): < 2000ms
- Hybrid search (cached): < 100ms
- Hybrid search (uncached): < 3000ms
- Semantic search: < 2000ms
- Filter search: < 200ms

**Throughput:**
- List endpoint: 500 requests/second (with cache)
- Search endpoint: 100 requests/second
- Create endpoint: 10 requests/second (rate-limited by Gemini API)

**Cache Hit Rates:**
- Recipe cache: 80-90%
- Search cache: 60-70%
- Embedding cache: 85-95%

---

### Search Quality Metrics

**Precision:**
- Semantic search: ~75% (subjective)
- Filter search: ~95% (objective)
- Hybrid search: ~85% (balanced)

**Recall:**
- Semantic search: ~90% (broad matches)
- Filter search: ~70% (strict matches)
- Hybrid search: ~95% (comprehensive)

**User Satisfaction:**
- Hybrid search with judge: ~85% satisfaction (expected)
- Time to relevant result: < 10 seconds

---

### Cost Metrics

**Gemini API Costs (Monthly, 10K users):**
- Embedding generation: ~$50/month
  - 1M embeddings × $0.00025/1K chars × 200 chars avg = $50
- Text generation (parsing, reranking): ~$20/month
  - 500K requests × $0.075/1M tokens × 100 tokens avg = $3.75 (input)
  - 500K requests × $0.30/1M tokens × 50 tokens avg = $7.50 (output)
  - Total: ~$11.25

**Database Costs:**
- PostgreSQL: $50-100/month (managed service)
- Redis: $20-50/month (managed service)

**Total Infrastructure:**
- API + Database + Cache + AI: ~$150-200/month for 10K users
- Cost per user: ~$0.015-0.02/month

---

### Data Growth Projections

**Assumptions:**
- 10,000 active users
- 5 recipes per user
- 50,000 total recipes
- 10 ingredients per recipe (avg)
- 2 categories per recipe (avg)

**Database Size:**
```
Recipes: 50,000 × 5 KB = 250 MB
Ingredients: 500,000 × 0.5 KB = 250 MB
Categories: 500 × 1 KB = 0.5 MB
Nutritional Info: 50,000 × 0.5 KB = 25 MB
Embeddings: 50,000 × 768 × 4 bytes = 150 MB

Total: ~675 MB
```

**With 10x growth (100K users, 500K recipes):**
- Database: ~7 GB
- Still easily manageable with standard PostgreSQL instance

---

### Monitoring & Observability

**Key Metrics to Track:**

1. **API Metrics:**
   - Request count by endpoint
   - Response times (p50, p95, p99)
   - Error rates (4xx, 5xx)
   - Request rate (per second)

2. **Search Metrics:**
   - Search query count
   - Search latency
   - Cache hit rate
   - Judge filtering rate (% of results removed)
   - Reranking usage

3. **Database Metrics:**
   - Query execution time
   - Connection pool utilization
   - Slow query log
   - Index usage

4. **Cache Metrics:**
   - Hit/miss ratio
   - Eviction rate
   - Memory usage
   - Key count

5. **AI Metrics:**
   - Gemini API latency
   - Gemini API error rate
   - Embedding generation time
   - Rate limit proximity

6. **Business Metrics:**
   - Recipes created per day
   - Searches per day
   - Most searched queries
   - Most popular recipes
   - User engagement (time on site, pages per session)

---

## Appendix

### Environment Variables Reference

```bash
# Application
APP_NAME=Recipe Management API
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5438/recipes
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Redis
REDIS_URL=redis://localhost:6381/0
REDIS_MAX_CONNECTIONS=10

# Cache TTL (seconds)
CACHE_TTL_DEFAULT=3600
CACHE_TTL_SEARCH=900
CACHE_TTL_EMBEDDING=86400
CACHE_TTL_STATS=300

# Gemini API
GEMINI_API_KEY=your-api-key-here
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
GEMINI_TEXT_MODEL=gemini-2.0-flash-exp
GEMINI_RATE_LIMIT_RPM=60
GEMINI_TIMEOUT=30
GEMINI_MAX_RETRIES=3

# API
API_HOST=0.0.0.0
API_PORT=8009
API_PREFIX=/api/v1

# Security
SECRET_KEY=your-secret-key-min-32-characters

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

### Common Error Scenarios & Resolutions

**Scenario 1: Duplicate Recipe Name**
- Error: `ValueError: Recipe with name 'Pasta Carbonara' already exists`
- HTTP Status: 400
- Resolution: Choose different name or append version/variation

**Scenario 2: Total Time Exceeds 24 Hours**
- Error: `ValueError: Total cooking time cannot exceed 24 hours`
- HTTP Status: 400
- Resolution: Reduce prep_time or cook_time

**Scenario 3: Recipe Not Found**
- Error: `ValueError: Recipe not found with id: {uuid}`
- HTTP Status: 404
- Resolution: Check recipe ID or verify recipe wasn't deleted

**Scenario 4: Gemini API Timeout**
- Error: `TimeoutError: Gemini API request timed out`
- HTTP Status: 504
- Resolution: Retry request, check API status, increase timeout

**Scenario 5: Embedding Not Available**
- Error: `ValueError: Recipe embedding not yet generated`
- HTTP Status: 400
- Resolution: Wait for background embedding generation, retry in 30 seconds

**Scenario 6: Cache Connection Lost**
- Error: `ConnectionError: Cannot connect to Redis`
- HTTP Status: 500 (if critical), 200 with degraded performance (if graceful)
- Resolution: Check Redis service, restart connection pool

---

**End of Business Logic Summary**

This document provides a comprehensive overview of the Recipe Management System's business logic, processes, and technical implementation details. For API endpoint details, see [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md).
