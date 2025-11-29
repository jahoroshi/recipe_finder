## Phase 6: API Layer (Week 6)

### ⚠️ Common Pitfalls to Avoid

Before implementing the API layer, be aware of these critical issues that can cause runtime errors:

1. **Pagination Schema Mismatch**:
   - `PaginatedResponse` uses `skip`, `limit`, `has_more` (not `page`, `page_size`, `pages`)
   - Always match field names exactly with the base schema definition

2. **SQLAlchemy Enum Configuration**:
   - Add `values_callable=lambda x: [e.value for e in x]` to Enum columns
   - Prevents "invalid input value for enum" errors

3. **Lazy Loading in Async Context**:
   - Use eager loading with chained `selectinload()` for nested relationships
   - Check if relationships are loaded before accessing: `obj.__dict__.get('relation')`
   - Prevents "greenlet_spawn has not been called" errors

4. **Enum Value Handling**:
   - Defensively handle enums that might be strings or enum objects
   - Use: `value if hasattr(obj, 'value') else obj`

### 6.1 FastAPI Application Structure

**Main Application Setup:**
```python
app = FastAPI(
    title="Recipe Management API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Event handlers
@app.on_event("startup")
async def startup():
    # Initialize connections
    # Warm up caches
    # Check external services

@app.on_event("shutdown")
async def shutdown():
    # Clean up connections
    # Flush caches
```

### 6.2 Recipe Endpoints

**Implementation Details:**

```python
@router.post("/recipes", response_model=RecipeResponse)
async def create_recipe(
    recipe: RecipeCreate,
    service: RecipeService = Depends(get_recipe_service),
    current_user: User = Depends(get_current_user)
):
    # Invoke LangGraph workflow
    # Handle validation errors
    # Return created recipe

@router.get("/recipes", response_model=RecipeListResponse)
async def list_recipes(
    filters: RecipeFilters = Depends(),
    pagination: Pagination = Depends(),
    service: RecipeService = Depends(get_recipe_service)
):
    # Apply filters
    # Check cache
    # Return paginated results
    # ⚠️ **Important:** Ensure pagination response fields match PaginatedResponse schema:
    #    - Use 'skip' (not 'page') for offset value
    #    - Use 'limit' (not 'page_size') for page size
    #    - Use 'has_more' (not 'pages') as boolean indicator
    # Example:
    #   RecipeListResponse(
    #       items=recipes,
    #       total=total_count,
    #       skip=pagination.offset,
    #       limit=pagination.limit,
    #       has_more=len(recipes) >= pagination.limit
    #   )

@router.post("/recipes/bulk")
async def bulk_import(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    service: RecipeService = Depends(get_recipe_service)
):
    # Validate file format
    # Queue background processing
    # Return job ID
```

### 6.3 Search Endpoints

```python
@router.post("/search", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    service: SearchService = Depends(get_search_service)
):
    # Check cache
    # Execute search workflow
    # Log search metrics
    # Return results

@router.get("/recipes/{id}/similar")
async def find_similar(
    id: UUID,
    limit: int = Query(10, le=50),
    service: SearchService = Depends(get_search_service)
):
    # Get recipe embedding
    # Find similar vectors
    # Filter and rank
```

### 6.4 Dependencies and Middleware

**Dependency Injection:**
```python
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_recipe_service(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis)
) -> RecipeService:
    return RecipeService(db, cache, ...)

def get_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
) -> Pagination:
    # Convert page-based params to offset-based for repository layer
    offset = (page - 1) * page_size
    return Pagination(offset=offset, limit=page_size)
```

**Custom Middleware:**
- Request ID generation
- Request/Response logging
- Performance monitoring
- Error handling and formatting

**⚠️ IMPORTANT - Pagination Consistency:**
When implementing pagination, ensure consistency between:
- Repository layer model attributes (`Pagination` class with `offset`/`limit`)
- API layer query parameters (user-friendly `page`/`page_size`)
- Dependency injection conversion (convert page-based to offset-based)

Common pitfall: Attempting to access `pagination.page` when the model only has `pagination.offset` and `pagination.page_number` (calculated property). Always verify attribute names match between model definition and usage across all layers.

---

# Post-Implementation Tasks

### 1. Write unit tests AND RUN created tests(!!!)
Verify API layer functionality:
- FastAPI endpoint handlers and request/response validation
- Dependency injection (database sessions, services, pagination)
- Middleware functionality (CORS, logging, error handling, request ID)
- Service integration with LangGraph workflows
- Background task processing
- Authentication and authorization flows
- Cache integration
- Error responses and status codes

### 2. Write integration tests
Test end-to-end API flows:
- Recipe CRUD operations through API endpoints
- Search endpoint with workflow execution
- Bulk import with background processing
- Filter and pagination combinations
- Similar recipe recommendations

### 3. Update Claude.md
Add to documentation:
- API structure and endpoint organization
- Request/response models and schemas
- Middleware stack and custom implementations
- Dependency injection pattern
- Background task handling
- Error handling strategy
- API versioning approach

!!! It's CRITICAL: on this phase you must CREATE and RUN extended tests to ensure everything works as expected !!!

---