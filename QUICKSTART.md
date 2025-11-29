# Quick Start Guide

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Google Gemini API Key (free at https://makersuite.google.com)

## Setup

### 1. Configure Environment Variables

Edit the `.env` file and set your Gemini API key:

```env
GEMINI_API_KEY=your-api-key-here
```

Other important settings (defaults should work):
- `POSTGRES_PORT` - PostgreSQL port (default: 5440)
- `REDIS_PORT` - Redis port (default: 6383)
- `BACKEND_PORT` - Backend API port (default: 8009)
- `FRONTEND_PORT` - Frontend port (default: 3002)
- `SECRET_KEY` - Change this for production

### 2. Start All Services

```bash
docker-compose up -d
```

### 3. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3002 |
| Backend API | http://localhost:8009/api |
| API Docs (Swagger) | http://localhost:8009/api/docs |
| API Docs (ReDoc) | http://localhost:8009/api/redoc |

## What Gets Started

The Docker Compose setup launches 4 services:

| Service | Container | Port |
|---------|-----------|------|
| PostgreSQL + pgvector | recipe-finder-postgres | 5440 |
| Redis cache | recipe-finder-redis | 6383 |
| FastAPI backend | recipe-finder-backend | 8009 |
| React frontend | recipe-finder-frontend | 3002 |

## Common Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service status
docker-compose ps

# Stop services
docker-compose down

# Stop and remove all data (includes database)
docker-compose down -v

# Rebuild after code changes
docker-compose build && docker-compose up -d

# Access backend container shell
docker-compose exec backend bash

# Access database
docker-compose exec database psql -U postgres -d recipes

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

## Startup Notes

- **First startup takes 2-5 minutes** - The backend runs database migrations and seeds ~50 sample recipes
- **Subsequent startups**: 30-60 seconds
- Watch startup progress: `docker-compose logs -f backend`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Verify `GEMINI_API_KEY` is valid in `.env` |
| Database connection failed | Wait for PostgreSQL to be healthy, check `docker-compose ps` |
| Port conflicts | Change ports in `.env` if 3002, 5440, 6383, or 8009 are in use |
| Frontend can't reach backend | Ensure backend is running and healthy |
| Search returns no results | Check if database has recipes: `docker-compose exec database psql -U postgres -d recipes -c "SELECT COUNT(*) FROM recipes;"` |

## Running Tests

```bash
# Backend tests
docker-compose exec backend pytest tests/ -v

# With coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
recipe-finder/
├── backend/           # FastAPI application
│   ├── app/           # Application code
│   ├── alembic/       # Database migrations
│   ├── tests/         # Test suite
│   └── scripts/       # Startup scripts
├── frontend/          # React application
│   ├── src/           # Source code
│   └── tests/         # Test suite
├── docker-compose.yml # Service orchestration
└── .env               # Environment configuration
```

