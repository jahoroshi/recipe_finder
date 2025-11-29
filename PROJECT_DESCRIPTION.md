# Recipe Finder - Project Description

## Overview

Recipe Finder is an AI-powered recipe management system that enables intelligent recipe discovery through semantic search. Built with FastAPI and React, it combines traditional filtering with Google Gemini AI embeddings to deliver highly relevant search results based on natural language queries.

## Key Features

### Core Functionality
- **AI-Powered Semantic Search** - Natural language recipe queries using Google Gemini embeddings and pgvector similarity
- **Hybrid Search Strategy** - Combines vector similarity with traditional attribute filtering using Reciprocal Rank Fusion (RRF)
- **Full Recipe Management** - Complete CRUD operations with automatic embedding generation
- **Advanced Filtering** - Search by cuisine, difficulty, cooking time, diet types, and ingredients

### Technical Features
- **Vector Similarity Search** - 768-dimensional embeddings stored in PostgreSQL with pgvector extension
- **Query Understanding** - AI-powered natural language query parsing to extract filters and intent
- **Result Quality Control** - Judge pattern validates search results against configurable thresholds
- **Smart Caching** - Multi-tier Redis caching (recipes, embeddings, search results) with automatic invalidation
- **Background Processing** - Bulk recipe imports and embedding generation via async tasks
- **Comprehensive API** - RESTful API with OpenAPI documentation (Swagger/ReDoc)

### Architecture Highlights
- **LangGraph Workflows** - State-based orchestration for complex search pipelines
- **Clean Architecture** - Layered design with repositories, services, and workflows
- **Async Throughout** - Non-blocking I/O with SQLAlchemy async and Redis async client
- **Type Safety** - Full type hints with Pydantic validation

## Main Flow

### 1. Recipe Creation Flow
```
User Input → API Validation → Recipe Service
    ↓
Business Rules Check (uniqueness, time constraints)
    ↓
Repository → Database Insert
    ↓
Embedding Service → Generate AI embedding via Gemini
    ↓
Update recipe with embedding vector
    ↓
Cache recipe data
    ↓
Return created recipe
```

### 2. Search Flow (Hybrid)
```
Natural Language Query → Search Pipeline Workflow
    ↓
┌─────────────────────────────────────────┐
│ Query Understanding (Gemini AI)         │
│ - Extract cuisine, diet, time filters   │
│ - Identify ingredients                  │
│ - Generate semantic query               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────┬───────────────────┐
│ Semantic Search     │ Filter Search     │
│ (Vector Similarity) │ (SQL Queries)     │
└─────────────────────┴───────────────────┘
    ↓
Merge Results with Reciprocal Rank Fusion (RRF)
    ↓
Judge Relevance (Quality Control)
    ├─ Check semantic similarity threshold
    ├─ Validate filter compliance
    ├─ Verify dietary requirements
    └─ Calculate confidence scores
    ↓
Optional AI Reranking (for refined relevance)
    ↓
Cache Results (15 min TTL)
    ↓
Return ranked recipes with scores
```

### 3. Data Pipeline
```
Recipe Data → Text Construction
    ↓
"Name | Description | Cuisine | Diet | Difficulty"
    ↓
Gemini API → Generate 768-dim embedding
    ↓
Cache embedding (24 hour TTL)
    ↓
Store in PostgreSQL with pgvector
    ↓
Create HNSW index for fast similarity search
```

### 4. Caching Strategy
```
Level 1: Recipe Cache (1 hour)
Level 2: Search Results (15 minutes)
Level 3: Embeddings (24 hours)
Level 4: Statistics (5 minutes)

Invalidation:
Recipe Update → Clear recipe + search + stats caches
Recipe Delete → Pattern-based cache invalidation
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15 with pgvector extension
- **Cache**: Redis 7
- **AI**: Google Gemini (embeddings + text generation)
- **Workflows**: LangGraph for orchestration
- **ORM**: SQLAlchemy 2.0 (async)

### Frontend
- **Framework**: React 19 with TypeScript
- **Build**: Vite 6
- **Styling**: Tailwind CSS
- **State**: React Query
- **Routing**: React Router

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database Extensions**: pgvector for vector operations
- **Reverse Proxy**: Nginx (production)

## Architecture Layers

```
┌─────────────────────────────────────────┐
│ API Layer (FastAPI REST)                │
│ - Endpoints, validation, middleware     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Workflow Layer (LangGraph)              │
│ - Search pipeline, judge pattern        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Service Layer (Business Logic)          │
│ - Recipe, Search, Embedding, Cache      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Repository Layer (Data Access)          │
│ - Recipe, Vector repositories           │
└─────────────────────────────────────────┘
              ↓
┌───────────────┬─────────────┬───────────┐
│ PostgreSQL    │ Redis       │ Gemini AI │
│ (+ pgvector)  │ (Cache)     │ (Embeddings)│
└───────────────┴─────────────┴───────────┘
```

## Use Cases

1. **Semantic Recipe Search**
   - "Quick vegetarian pasta under 30 minutes"
   - Returns relevant recipes ranked by similarity

2. **Ingredient-Based Discovery**
   - "Recipes with chicken, garlic, and tomatoes"
   - Matches recipes containing specified ingredients

3. **Dietary Filtering**
   - "Vegan gluten-free desserts"
   - Strict dietary requirement enforcement

4. **Similar Recipe Discovery**
   - Find recipes similar to a specific dish
   - Uses embedding vectors for similarity

5. **Recipe Management**
   - Create, update, delete recipes
   - Automatic embedding generation and cache management

## Getting Started

See [QUICKSTART.md](QUICKSTART.md) for setup instructions.

## API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8009/api/docs
- **ReDoc**: http://localhost:8009/api/redoc
- **Frontend**: http://localhost:3002
