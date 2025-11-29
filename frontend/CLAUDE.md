# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Recipe Management System Frontend** - a React/TypeScript application for discovering and managing cooking recipes. The frontend connects to a FastAPI backend with AI-powered search capabilities.

**Current State**: Basic React prototype with local state and mock data. Needs integration with the backend Recipe Management API.

**Backend API**: `http://localhost:8009/api` (see `docs/FRONTEND_SPECIFICATION.md` for full API documentation)

## Technology Stack

- **Framework**: React 19.2 with TypeScript
- **Build Tool**: Vite 6.2
- **Styling**: Inline styles (no CSS framework currently - consider TailwindCSS)
- **State**: Local useState hooks (no global state management yet)
- **API Client**: None configured (needs Axios or fetch wrapper)

## Development Commands

```bash
# Install dependencies
npm install

# Run development server (port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
/
├── App.tsx                 # Main app component with routing and state
├── index.tsx              # React entry point
├── types.ts               # TypeScript interfaces (Recipe, NewRecipe)
├── components/            # React components
│   ├── AddRecipeModal.tsx
│   ├── RecipeCard.tsx
│   ├── SearchBar.tsx
│   └── icons/
├── docs/                  # API and business logic documentation
│   ├── FRONTEND_SPECIFICATION.md    # Complete API reference and UI requirements
│   └── BUSINESS_LOGIC_SUMMARY.md    # Backend architecture and workflows
├── vite.config.ts         # Vite configuration with @ alias
└── tsconfig.json          # TypeScript configuration
```

## Key Architecture Decisions

### Current Implementation (Prototype)

- **Data Storage**: Local state with `initialRecipes` array (hardcoded mock data)
- **Search**: Client-side filtering by recipe name and ingredients
- **Recipe Model**: Simple interface with `id`, `name`, `ingredients[]`, `instructions`, `image`
- **No API Integration**: All operations are local (add, search, display)

### Backend API Integration Requirements

The backend provides a sophisticated Recipe Management API with:

1. **CRUD Operations**: Create, read, update, delete recipes with validation
2. **Hybrid Search**: AI-powered semantic search + traditional filters
3. **Vector Embeddings**: 768-dimensional vectors for semantic similarity
4. **Advanced Features**:
   - Find similar recipes by vector similarity
   - Bulk import from JSON
   - Rich metadata (cuisine, difficulty, diet types, nutritional info)
   - Hierarchical categories
   - Soft deletes with recovery

**Critical**: The current frontend `Recipe` type is incompatible with the backend API. See `docs/FRONTEND_SPECIFICATION.md` section "Data Models" for the complete backend schema.

### Environment Configuration

- **API Key**: `GEMINI_API_KEY` in `.env.local` (currently placeholder)
- **Vite Config**: Exposes API key as `process.env.GEMINI_API_KEY` and `process.env.API_KEY`
- **Path Alias**: `@/*` resolves to project root (configured in vite.config.ts and tsconfig.json)

## Common Development Tasks

### Adding API Integration

1. Install HTTP client: `npm install axios`
2. Create API service layer in `services/` directory
3. Configure base URL and interceptors (see FRONTEND_SPECIFICATION.md section "API Integration")
4. Update `types.ts` to match backend models (UUID ids, embedded relationships)
5. Replace local state with API calls in `App.tsx`

### Implementing Search

The backend provides three search types:

1. **Hybrid Search** (Recommended): `POST /api/search`
   - Natural language queries (e.g., "quick vegetarian pasta under 30 minutes")
   - AI parses query → semantic search + filters → merged results
   - Returns recipes with relevance scores and match types

2. **Semantic Search**: `POST /api/search/semantic`
   - Pure AI vector similarity
   - Understands context and synonyms

3. **Filter Search**: `GET /api/recipes` or `POST /api/search/filter`
   - Traditional attribute filtering
   - Supports cuisine, difficulty, diet types, time ranges, etc.

**Current Implementation**: Basic client-side string matching in `App.tsx:79-86`

### Running with Backend

The backend must be running on `http://localhost:8009`. To integrate:

1. Update `GEMINI_API_KEY` in `.env.local` with valid API key
2. Ensure backend is running: check `http://localhost:8009/health`
3. Configure CORS in backend to allow `http://localhost:3000`
4. Update API calls to use backend endpoints

## Important Technical Notes

### TypeScript Configuration

- **Target**: ES2022 with experimental decorators
- **Module System**: ESNext with bundler resolution
- **JSX**: `react-jsx` (new JSX transform, no React import needed)
- **Path Mapping**: `@/*` for absolute imports
- **Type Checking**: Skip lib checks, allow TS extensions

### Vite Configuration

- **Dev Server**: Port 3000, accessible from all network interfaces (0.0.0.0)
- **Plugins**: `@vitejs/plugin-react` for fast refresh
- **Environment Variables**: Gemini API key injected at build time
- **Alias**: `@` resolves to project root

### Recipe Data Model Mismatch

**Current Frontend Model**:
```typescript
interface Recipe {
  id: number;              // Simple numeric ID
  name: string;
  ingredients: string[];   // Array of strings
  instructions: string;    // Single string
  image: string;           // URL
}
```

**Backend API Model** (simplified):
```typescript
interface Recipe {
  id: string;              // UUID
  name: string;
  description?: string;
  instructions: object;    // JSON object with steps
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  difficulty: 'easy' | 'medium' | 'hard';
  cuisine_type?: string;
  diet_types: string[];
  embedding?: number[];    // 768-dimensional vector
  ingredients: Ingredient[];  // Array of objects
  categories: Category[];
  nutritional_info?: NutritionalInfo;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

interface Ingredient {
  id: string;
  name: string;
  quantity?: number;
  unit?: string;
  notes?: string;
}
```

**Action Required**: Update `types.ts` and all components to use backend-compatible models before API integration.

## Documentation References

All comprehensive documentation is in the `docs/` directory:

- **`FRONTEND_SPECIFICATION.md`**: Complete API reference, data models, user flows, UI requirements, and integration examples (2,437 lines)
- **`BUSINESS_LOGIC_SUMMARY.md`**: Backend architecture, AI workflows, search algorithms, caching strategies, and performance metrics (1,403 lines)

**Key sections to review before major changes**:
- API Endpoints Reference (FRONTEND_SPECIFICATION.md lines 57-717)
- Data Models (FRONTEND_SPECIFICATION.md lines 771-918)
- Search Algorithm Deep Dive (BUSINESS_LOGIC_SUMMARY.md lines 922-1048)
- User Flows & Interactions (FRONTEND_SPECIFICATION.md lines 1387-1617)

## Backend Integration Checklist

When connecting to the Recipe Management API:

- [ ] Install `axios` or configure fetch client
- [ ] Create API service layer (`services/recipeService.ts`, `services/searchService.ts`)
- [ ] Update `types.ts` with backend-compatible models
- [ ] Add environment variable for API base URL
- [ ] Implement request/response interceptors for error handling
- [ ] Replace mock data with API calls
- [ ] Add loading states and error handling
- [ ] Implement pagination for recipe lists (page_size: 20-50)
- [ ] Cache API responses (consider React Query)
- [ ] Handle 404s, validation errors (400), and server errors (500+)

## Known Limitations

- No state management library (all state is local)
- No routing (single page application)
- No error boundaries
- No loading states
- No pagination
- Mock data hardcoded in `App.tsx`
- Simple string-based search (no semantic capabilities)
- No authentication/authorization
- No image upload (uses placeholder URLs)
- No form validation beyond basic React state

## Performance Considerations

Backend API performance targets (from BUSINESS_LOGIC_SUMMARY.md):
- List recipes (cached): < 50ms
- Hybrid search (uncached): < 3000ms
- Create recipe: < 2000ms (includes AI embedding generation)

**Frontend Recommendations**:
- Debounce search inputs (500ms)
- Use React Query or SWR for caching
- Virtualize long recipe lists (react-window)
- Lazy load images
- Implement pagination (don't load all recipes at once)
- Show skeleton loaders during API calls

## AI Search Features

The backend uses Google Gemini API for advanced search:

1. **Query Parsing**: AI extracts filters from natural language
   - Input: "quick vegetarian pasta under 30 minutes"
   - Extracted: `{ingredients: ["pasta"], diet_types: ["vegetarian"], max_prep_time: 30}`

2. **Vector Embeddings**: 768-dimensional semantic representations
   - Enables "creamy pasta" to match "Alfredo" and "Carbonara"
   - Generated automatically on recipe creation

3. **Hybrid Ranking**: Reciprocal Rank Fusion (RRF) algorithm
   - Merges semantic similarity scores with filter match scores
   - Boosts recipes appearing in both result sets

4. **Judge & Filter**: Quality control with configurable thresholds
   - Semantic score, filter compliance, dietary requirements
   - Fallback strategies when results below minimum

**UI Implication**: Display search results with scores, match types, and parsed query info (see FRONTEND_SPECIFICATION.md lines 1286-1308)

## Styling Approach

Current: Inline CSS with Tailwind-like class names (e.g., `"min-h-screen bg-gray-50"`)

**Note**: No actual Tailwind CSS is installed. These are just class name strings that may not have any effect. Consider:
- Installing TailwindCSS: `npm install -D tailwindcss postcss autoprefixer`
- Or switching to CSS Modules, Styled Components, or Material-UI

## Testing Strategy

**Current**: No tests configured

**Recommended**:
- Unit tests: Vitest (Vite-native)
- Component tests: React Testing Library
- E2E tests: Playwright or Cypress
- API mocking: MSW (Mock Service Worker)
