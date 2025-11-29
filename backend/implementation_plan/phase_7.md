# Task 7: Database Seeding Script

## Phase 7: Manual Database Seeding

### 7.1 Seeding Script Structure

**Core Components:**
```python
class RecipeSeeder:
    def __init__(self,
                 api_client: httpx.AsyncClient,
                 base_url: str,
                 batch_size: int = 10):
        ...
    
    async def generate_recipes(self, count: int) -> List[dict]
    async def seed_database(self, recipes: List[dict]) -> SeederReport
    async def validate_seeded_data(self) -> ValidationReport
    async def cleanup_test_data(self, tag: str) -> None
```

**Script Entry Point:**
```python
# scripts/seed_database.py
async def main(
    count: int = 50,
    categories: List[str] = None,
    complexity_distribution: dict = None,
    api_url: str = "http://localhost:8000"
) -> None
```

### 7.2 Recipe Generation Strategy

**Data Generation Parameters:**
- 50+ diverse recipes across different categories
- Realistic cooking times (15-180 minutes)
- Varied complexity levels (easy/medium/hard)
- Multiple cuisines representation
- Ingredient combinations that make culinary sense
- Nutritional information within realistic ranges

**Recipe Categories Distribution:**
- Breakfast & Brunch (15%)
- Main Courses (30%)
- Appetizers & Snacks (15%)
- Desserts (20%)
- Salads & Sides (10%)
- Beverages (10%)

### 7.3 Generated Recipe Examples

**Sample Recipe Templates:**
1. **Classic Dishes** - Traditional recipes with standard ingredients
2. **Fusion Cuisine** - Cross-cultural combinations
3. **Dietary Specific** - Vegan, gluten-free, keto recipes
4. **Quick Meals** - Under 30-minute preparations
5. **Gourmet Options** - Complex, multi-step recipes

**Data Richness Requirements:**
- Detailed step-by-step instructions
- Proper ingredient measurements and units
- Cooking tips and variations
- Allergen information
- Serving suggestions

### 7.4 API Integration

**Seeding Process:**
```python
class SeederAPIClient:
    async def create_recipe_batch(self, recipes: List[dict]) -> List[Response]
    async def verify_recipe_exists(self, recipe_id: UUID) -> bool
    async def trigger_embedding_generation(self, recipe_ids: List[UUID]) -> None
    async def verify_search_indexing(self, sample_queries: List[str]) -> bool
```

**Error Handling:**
- Retry logic for failed API calls
- Partial batch failure recovery
- Duplicate detection and skipping
- Rate limiting compliance

### 7.5 Validation and Reporting

**Post-Seeding Validation:**
```python
class SeederValidator:
    async def validate_recipe_count(self) -> bool
    async def validate_search_functionality(self) -> bool
    async def validate_embeddings_generated(self) -> bool
    async def generate_seeding_report(self) -> dict
```

**Report Metrics:**
- Total recipes attempted/succeeded/failed
- Categories distribution verification
- Average seeding time per recipe
- API response times
- Search index coverage

---

## Post-Implementation Tasks

### 1. Create and Test Seeding Script
**WITHOUT RUNNING THE FULL SEEDING:**
- Generate 50+ recipe JSON objects programmatically
- Implement batch upload logic with error handling
- Add progress bar for seeding process
- Create dry-run mode for testing
- Validate JSON schema compliance

### 2. Write Unit Tests
Test seeding components:
- Recipe data generation logic
- API client batch operations
- Error recovery mechanisms
- Validation checks
- Report generation

### 3. Create Test Fixtures
Generate reusable test data:
- `fixtures/recipes_basic.json` - 10 simple recipes
- `fixtures/recipes_complex.json` - 10 complex recipes
- `fixtures/recipes_dietary.json` - Special diet recipes
- `fixtures/invalid_recipes.json` - For error testing

### 4. Documentation Updates
Add to project docs:
- Seeding script usage instructions
- Recipe data generation strategy
- Validation criteria
- Troubleshooting guide
- Sample generated recipes

### 5. Configuration
Create seeding configuration:
- `config/seeding.yaml` - Default parameters
- Environment-specific settings
- Category and complexity distributions
- Rate limiting configuration

---

**Key Requirements:**
- Script must be idempotent (safe to run multiple times)
- Support partial seeding and resume capability
- Generate semantically meaningful recipe content
- Include metadata for testing purposes (tags, timestamps)
- Provide clear console output and logging
- Support both full and incremental seeding modes

**Testing Approach:**
- Unit test all generation functions
- Mock API calls for testing
- Validate generated JSON structure
- Test error scenarios (API down, invalid data)
- Verify idempotency with multiple runs
- DO NOT execute actual database seeding