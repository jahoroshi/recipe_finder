## Phase 2: Database Layer Implementation (Week 2)

### 2.1 Database Models

**SQLAlchemy Models Implementation:**

1. **Base Model Class:**
   - UUID primary keys
   - Soft delete support with `deleted_at`
   - Timestamp mixins (`created_at`, `updated_at`)
   - Audit fields mixin

2. **Recipe Model:**
   - Vector column for embeddings (768 dimensions)
   - JSONB for instructions storage
   - Array fields for diet_types
   - Enum for difficulty levels
     ⚠️ **Important:** When using SQLAlchemy Enum with string-based Python enums, always specify `values_callable=lambda x: [e.value for e in x]` to ensure the database stores the enum values (e.g., "easy") instead of member names (e.g., "EASY")
   - Relationships to ingredients, categories, nutritional info

3. **Supporting Models:**
   - Ingredient (with recipe relationship)
   - Category (hierarchical with self-reference)
   - RecipeCategory (many-to-many junction)
   - NutritionalInfo (one-to-one with recipe)

**Database Indexes:**
- B-tree indexes on frequently filtered columns
- GIN indexes on JSONB fields
- HNSW index on embedding vector column
- Composite indexes for common query patterns

### 2.2 Alembic Migrations

**Migration Strategy:**
1. Initial schema creation
2. pgvector extension installation
3. Index creation (separate migration for performance)
4. Seed data for categories and common ingredients

**Migration Files Structure:**
```
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_pgvector_extension.py
│   ├── 003_create_indexes.py
│   └── 004_seed_categories.py
├── alembic.ini
└── env.py
```

### 2.3 Database Session Management

**Async Session Factory:**
- Implement async context manager for sessions
- Configure connection pooling (min=5, max=20)
- Set up query timeout parameters
- Implement automatic retry logic for transient failures

**Dependency Injection:**
- Create FastAPI dependency for database sessions
- Implement transaction management decorators
- Set up read replica support for scaling

---

## Post-Implementation:

### 1. Write unit tests AND RUN created tests(!!!)
Verify implemented database layer functionality:
- SQLAlchemy models and relationships
- Alembic migrations
- Async session management and dependency injection
- Connection pooling and retry logic

### 2. Update Claude.md
Add to documentation:
- List of implemented database models
- Migration strategy and structure
- Session management approach
- Known issues and TODOs



---