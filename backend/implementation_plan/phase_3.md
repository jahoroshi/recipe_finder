## Phase 3: Repository Layer 

### 3.1 Base Repository

**Generic Repository Pattern:**
```python
class BaseRepository[T]:
    - async def create(entity: T) -> T
    - async def get(id: UUID) -> Optional[T]
    - async def update(id: UUID, updates: dict) -> T
    - async def delete(id: UUID) -> None
    - async def list(filters: dict, pagination: Pagination) -> List[T]
    - async def count(filters: dict) -> int
    - async def exists(id: UUID) -> bool
    - async def bulk_create(entities: List[T]) -> List[T]
    - async def bulk_update(updates: List[dict]) -> List[T]
```

**Features:**
- Soft delete support by default
- Automatic timestamp updates
- Query builder pattern for complex filters
- Eager/lazy loading configuration

### 3.2 RecipeRepository

**Specialized Methods:**
- Complex filtering with multiple parameters
- Full-text search on title/description
- Aggregation queries for statistics
- Batch operations for bulk imports
- Optimized queries with joined loading

**Key Implementations:**
```python
- async def find_by_ingredients(ingredients: List[str]) -> List[Recipe]
- async def find_by_cuisine_and_difficulty(cuisine: str, difficulty: Enum) -> List[Recipe]
- async def get_with_relations(id: UUID) -> Recipe
  ⚠️ **Important:** Use chained selectinload for nested relationships to prevent lazy loading issues
  Example: selectinload(Recipe.recipe_categories).selectinload(RecipeCategory.category)
- async def update_embedding(id: UUID, embedding: List[float]) -> None
- async def get_popular_recipes(limit: int) -> List[Recipe]
```

### 3.3 VectorRepository

**pgvector Operations:**
```python
- async def similarity_search(embedding: List[float], limit: int) -> List[Recipe]
- async def hybrid_search(embedding: List[float], filters: dict) -> List[Recipe]
- async def find_similar_recipes(recipe_id: UUID, limit: int) -> List[Recipe]
- async def batch_update_embeddings(updates: List[dict]) -> None
- async def reindex_embeddings() -> None
```

**Optimization Strategies:**
- Use approximate nearest neighbor search (HNSW)
- Implement query result caching
- Batch embedding updates
- Parallel similarity computations

---

## Post-Implementation:

### 1. Write unit tests AND RUN created tests(!!!)
Verify implemented repository layer functionality:
- Base repository CRUD operations and filters
- Recipe repository specialized methods
- Vector repository similarity search
- Batch operations and transaction handling

### 2. Update Claude.md
Add to documentation:
- List of implemented repositories
- Repository pattern architecture
- Vector search implementation details
- Known issues and TODOs



---