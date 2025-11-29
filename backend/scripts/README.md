# Recipe Database Seeding System

Comprehensive database seeding system for the Recipe Management API with intelligent recipe generation, batch processing, and validation.

## Quick Start

```bash
# Basic usage - seed 50 recipes
python -m scripts.seed_database

# Dry run (test without API calls)
python -m scripts.seed_database --count 10 --dry-run

# With custom parameters
python -m scripts.seed_database \
    --count 100 \
    --batch-size 20 \
    --seed 42 \
    --output report.json
```

## Features

- **50+ Realistic Recipe Templates** across 6 categories
- **Intelligent Data Generation** with semantic meaning
- **Robust API Client** with retry logic
- **Beautiful CLI** with progress tracking
- **Dry-Run Mode** for safe testing
- **Comprehensive Validation** of seeded data
- **Batch Processing** for efficiency
- **Detailed Reporting** with JSON export
- **Reproducible Seeding** with random seeds

## Components

### 1. Recipe Generator (`recipe_generator.py`)

Generates realistic recipe data:

```python
from scripts.recipe_generator import RecipeDataGenerator

generator = RecipeDataGenerator(seed=42)
recipes = generator.generate_recipes(count=50)
```

**Categories:**
- Breakfast & Brunch (15%)
- Main Courses (30%)
- Appetizers & Snacks (15%)
- Desserts (20%)
- Salads & Sides (10%)
- Beverages (10%)

### 2. API Client (`seeder_client.py`)

Handles API communication with retry logic:

```python
from scripts.seeder_client import SeederAPIClient

async with SeederAPIClient("http://localhost:8009") as client:
    result = await client.create_recipe(recipe_data)
    count = await client.get_recipe_count()
```

### 3. Main Seeder (`seed_database.py`)

Orchestrates the entire seeding process:

```python
from scripts.seed_database import RecipeSeeder

seeder = RecipeSeeder(
    api_url="http://localhost:8009",
    batch_size=10,
    dry_run=False
)

recipes = await seeder.generate_recipes(count=50)
report = await seeder.seed_database(recipes)
```

## CLI Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--count` | int | 50 | Number of recipes to generate |
| `--categories` | list | None | Specific categories to include |
| `--api-url` | str | http://localhost:8009 | API base URL |
| `--batch-size` | int | 10 | Recipes per batch |
| `--dry-run` | flag | False | Validate without API calls |
| `--seed` | int | None | Random seed for reproducibility |
| `--output` | str | None | Output file for report (JSON) |
| `--skip-validation` | flag | False | Skip post-seeding validation |

## Examples

### Dry Run (No API Calls)

```bash
python -m scripts.seed_database --count 20 --dry-run
```

This validates recipe data without making any API calls.

### Reproducible Seeding

```bash
python -m scripts.seed_database --seed 42 --count 50
```

Using a seed ensures the same recipes are generated every time.

### Save Report

```bash
python -m scripts.seed_database --count 100 --output seeding_report.json
```

Saves detailed report including:
- Success/failure counts
- Duration and timing
- Created recipe IDs
- Failed recipes with errors

### Custom API and Batch Size

```bash
python -m scripts.seed_database \
    --api-url http://localhost:8000 \
    --batch-size 20 \
    --count 200
```

## Testing

Run comprehensive test suite:

```bash
# All seeding tests (71 tests)
pytest tests/test_seeding/ -v

# With coverage
pytest tests/test_seeding/ --cov=scripts --cov-report=html

# Specific test file
pytest tests/test_seeding/test_recipe_generator.py -v
```

## Fixtures

Test fixtures available in `fixtures/`:

- `recipes_basic.json` - 10 simple recipes for testing

Load fixtures in tests:

```python
import json
from pathlib import Path

with open("fixtures/recipes_basic.json") as f:
    recipes = json.load(f)
```

## Configuration

Configuration file at `config/seeding.yaml`:

```yaml
api:
  base_url: "http://localhost:8009"
  timeout: 30
  max_retries: 3

seeding:
  default_count: 50
  batch_size: 10

validation:
  sample_queries:
    - "chicken"
    - "pasta"
    - "dessert"
  min_success_rate: 0.95
```

## Output Format

### Console Output

Beautiful formatted output with:
- Progress bars
- Distribution tables
- Success/failure statistics
- Validation results

### Report JSON

```json
{
  "total_attempted": 50,
  "total_succeeded": 48,
  "total_failed": 2,
  "failed_recipes": [...],
  "duration_seconds": 45.3,
  "average_time_per_recipe": 0.906,
  "created_recipe_ids": ["uuid1", "uuid2", ...]
}
```

## Troubleshooting

### API Connection Issues

```
Error: Health check failed!
```

**Solution:** Ensure API is running:
```bash
uvicorn app.main:app --port 8009
```

### Rate Limiting

```
Warning: Request failed (attempt 1/3): 429 Too Many Requests
```

**Solution:** Reduce batch size:
```bash
python -m scripts.seed_database --batch-size 5
```

### Validation Failures

```
Failed Recipes:
  - Recipe Name: Missing required field: instructions
```

**Solution:** Run dry-run first to validate data:
```bash
python -m scripts.seed_database --dry-run
```

## Performance

**Benchmarks** (50 recipes, batch_size=10):
- Total time: ~45-60 seconds
- Throughput: ~0.8-1.1 recipes/second
- Memory usage: < 100 MB

**Optimization:**
```bash
# Faster seeding with larger batches
python -m scripts.seed_database --batch-size 30

# Skip validation to save time
python -m scripts.seed_database --skip-validation
```

## Best Practices

1. **Always test with dry run first**
   ```bash
   python -m scripts.seed_database --count 10 --dry-run
   ```

2. **Use reproducible seeds for testing**
   ```bash
   python -m scripts.seed_database --seed 42
   ```

3. **Save reports for auditing**
   ```bash
   python -m scripts.seed_database --output report.json
   ```

4. **Start small, scale up**
   ```bash
   # Test with 10
   python -m scripts.seed_database --count 10

   # Then scale to 100+
   python -m scripts.seed_database --count 100
   ```

## Documentation

For detailed documentation, see:
- `PHASE_7_SEEDING_DOCUMENTATION.md` - Full implementation details
- `config/seeding.yaml` - Configuration options
- `tests/test_seeding/` - Test examples

## License

Part of the Recipe Management API project.
