## Phase 4: Service Layer

### 4.1 RecipeService

**Core Business Logic:**
```python
class RecipeService:
    def __init__(self, 
                 recipe_repo: RecipeRepository,
                 vector_repo: VectorRepository,
                 embedding_service: EmbeddingService,
                 cache_service: CacheService,
                 workflow_engine: RecipeProcessingGraph):
        ...
    
    async def create_recipe(self, data: RecipeCreate) -> RecipeResponse
    async def update_recipe(self, id: UUID, updates: RecipeUpdate) -> RecipeResponse
    async def enrich_recipe_data(self, recipe: Recipe) -> Recipe
    async def validate_business_rules(self, recipe: RecipeCreate) -> None
    async def calculate_recipe_metrics(self, recipe: Recipe) -> dict
```

**Key Features:**
- Input validation and sanitization
- Business rule enforcement
- Cache invalidation on updates
- Audit logging for all operations
- Transaction management
- ⚠️ **Important:** When converting models to response schemas, avoid triggering lazy loading:
  ```python
  # Safe way to check if relationship is loaded
  category = rc.__dict__.get('category')
  if category is not None:
      # Process category safely
  ```
  This prevents "greenlet_spawn has not been called" errors in async contexts

### 4.2 SearchService

**Search Strategies Implementation:**
```python
class SearchService:
    async def hybrid_search(self, query: SearchRequest) -> SearchResponse:
        # 1. Parse query with Gemini
        # 2. Generate embedding
        # 3. Parallel execution of vector and filter search
        # 4. Merge results with RRF
        # 5. Optional reranking
        # 6. Format response with metadata
    
    async def semantic_search(self, query: str, limit: int) -> List[Recipe]
    async def filter_search(self, filters: dict) -> List[Recipe]
    async def query_understanding(self, query: str) -> ParsedQuery
    async def result_reranking(self, results: List[Recipe], query: str) -> List[Recipe]
```

**Search Optimization:**
- Query result caching with Redis
- Parallel search execution
- Early termination for large result sets
- Relevance score calculation
- ⚠️ **Critical:** SQLAlchemy AsyncSession does NOT support concurrent operations. When implementing parallel searches:
  ```python
  # ❌ WRONG - Both searches use the same session
  results = await asyncio.gather(
      self.semantic_search(query),    # Uses session
      self.filter_search(filters)     # Uses same session
  )
  # Error: "This session is provisioning a new connection; concurrent operations are not permitted"

  # ✅ CORRECT - Run sequentially
  semantic_results = await self.semantic_search(query)
  filter_results = await self.filter_search(filters)
  # Or use separate sessions for true parallelism
  ```
  This prevents InvalidRequestError and IllegalStateChangeError exceptions

### 4.3 EmbeddingService

**Gemini Integration:**
```python
class EmbeddingService:
    def __init__(self, gemini_client: genai.Client, cache: Redis):
        self.model = "gemini-embedding-001"
        self.batch_size = 100
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    async def generate_embedding(self, text: str) -> List[float]
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]
    async def create_recipe_embedding(self, recipe: Recipe) -> List[float]
    async def update_all_embeddings(self) -> None
```

**Features:**
- Rate limiting and retry logic
- Batch processing for efficiency
- Embedding caching strategy
- Error handling for API failures
- ⚠️ **Important:** When constructing text from model enums (e.g., difficulty), use defensive coding:
  ```python
  difficulty_value = (
      recipe.difficulty.value if hasattr(recipe.difficulty, "value")
      else recipe.difficulty
  )
  ```
  This handles both enum objects and string values from Pydantic schemas with `use_enum_values=True`

### 4.4 CacheService

**Redis Caching Strategy:**
```python
class CacheService:
    async def get(self, key: str) -> Optional[Any]
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None
    async def delete(self, key: str) -> None
    async def delete_pattern(self, pattern: str) -> None
    async def invalidate_recipe_cache(self, recipe_id: UUID) -> None
```

**Cache Keys Structure:**
- `recipe:{id}` - Individual recipes (TTL: 1 hour)
- `search:{query_hash}` - Search results (TTL: 15 minutes)
- `embedding:{text_hash}` - Embeddings (TTL: 24 hours)
- `stats:{type}` - Aggregated statistics (TTL: 5 minutes)

---

# Post-Implementation Tasks

### 1. Write unit tests AND RUN created tests(!!!)
Verify implemented service layer functionality:
- RecipeService business logic and validation
- SearchService hybrid search and query parsing
- EmbeddingService batch processing and caching
- CacheService Redis operations and invalidation

### 2. Update Claude.md
Add to documentation:
- List of implemented services
- Service layer architecture
- Search strategies and optimization
- Caching strategy and TTL configuration



---