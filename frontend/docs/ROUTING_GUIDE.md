# Routing Guide

## Overview

This application uses **React Router v7** for client-side routing. The routing system provides navigation between pages, URL parameter extraction, and route guards for future authentication.

## Route Structure

```
/                          → HomePage (Recipe List)
/recipes/new               → RecipeFormPage (Create)
/recipes/:id               → RecipeDetailPage (View)
/recipes/:id/edit          → RecipeFormPage (Edit)
/search                    → SearchResultsPage
/search?q=query            → SearchResultsPage (with query)
/import                    → BulkImportPage
/404                       → NotFoundPage
/*                         → NotFoundPage (catch-all)
```

## File Structure

```
/pages/
  ├── HomePage.tsx              # Recipe list/browse page
  ├── RecipeDetailPage.tsx      # Recipe detail view
  ├── RecipeFormPage.tsx        # Create/edit recipe form
  ├── SearchResultsPage.tsx     # Search results with filters
  ├── BulkImportPage.tsx        # Bulk import interface
  ├── NotFoundPage.tsx          # 404 error page
  └── index.ts                  # Page exports

/routes/
  ├── index.tsx                 # Router configuration
  └── guards.tsx                # Route guard components

/components/layout/
  ├── Layout.tsx                # Main layout wrapper
  ├── Navigation.tsx            # Header navigation
  ├── Breadcrumbs.tsx           # Breadcrumb navigation
  └── index.ts                  # Layout exports
```

## Navigation Methods

### 1. Declarative Navigation (Links)

```tsx
import { Link } from 'react-router-dom';

<Link to="/recipes/new">Create Recipe</Link>
<Link to={`/recipes/${recipeId}`}>View Recipe</Link>
```

### 2. Programmatic Navigation

```tsx
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();

navigate('/');                           // Navigate to home
navigate(`/recipes/${id}`);              // Navigate to recipe detail
navigate(-1);                            // Go back
navigate('/search', { replace: true }); // Replace current entry
```

### 3. URL Parameters

```tsx
import { useParams, useSearchParams } from 'react-router-dom';

// Path parameters
const { id } = useParams<{ id: string }>();

// Query parameters
const [searchParams] = useSearchParams();
const query = searchParams.get('q');
```

## Page Components

### HomePage

**Route:** `/`

**Purpose:** Browse recipes with search functionality

**Features:**
- Search bar (navigates to SearchResultsPage)
- Recipe card grid
- Create recipe button
- Empty state

**State:** Local state for demo (will use API in Phase 2)

### RecipeDetailPage

**Route:** `/recipes/:id`

**Purpose:** Display full recipe information

**Features:**
- Recipe header with metadata
- Info panel (prep/cook time, servings)
- Ingredients list with checkboxes
- Step-by-step instructions
- Nutritional information
- Categories
- Action buttons (Edit, Delete, Find Similar)

**URL Parameters:**
- `id` - Recipe UUID

### RecipeFormPage

**Routes:** `/recipes/new` and `/recipes/:id/edit`

**Purpose:** Create or edit recipes

**Features:**
- Basic information form
- Timing and servings inputs
- Difficulty selector
- Placeholder for full form implementation (Phase 2)

**Mode Detection:**
```tsx
const { id } = useParams();
const isEditMode = Boolean(id);
```

### SearchResultsPage

**Route:** `/search` (with `?q=query` parameter)

**Purpose:** Display search results with AI-powered parsing

**Features:**
- Search bar
- Parsed query info (AI-extracted filters)
- Results grid with relevance scores
- Match type badges (semantic/filter/hybrid)
- Metadata display

**URL Parameters:**
- `q` - Search query string

### BulkImportPage

**Route:** `/import`

**Purpose:** Bulk import recipes from JSON file

**Features:**
- Drag-and-drop file upload
- File format instructions
- Import status display
- Loading state

**Protected:** Requires authentication (when implemented)

### NotFoundPage

**Routes:** `/404` and `*` (catch-all)

**Purpose:** Handle invalid routes

**Features:**
- 404 heading
- Current path display
- Navigation buttons (Home, Back)
- Quick links to main pages

## Layout System

### Layout Component

Main wrapper for all pages with consistent navigation.

```tsx
<Layout>
  <Outlet /> {/* Page content renders here */}
</Layout>
```

**Features:**
- Sticky header navigation
- Responsive mobile menu
- Consistent spacing

### Navigation Component

Header navigation with brand, links, and CTA button.

**Desktop Navigation:**
- Browse, Search, Import links
- Add Recipe button

**Mobile Navigation:**
- Bottom tab bar
- Icons with labels

**Active Route Highlighting:**
```tsx
const isActive = (path: string) => location.pathname === path;
```

### Breadcrumbs Component

Contextual navigation showing page hierarchy.

**Features:**
- Automatic breadcrumb generation from URL
- Custom labels for routes
- UUID segment filtering
- Hidden on home page

**Example:**
```
Home > Recipes > Edit Recipe
```

## Route Guards

Route guards control access to protected routes. Currently configured for future authentication.

### ProtectedRoute

Guards routes requiring authentication.

```tsx
<ProtectedRoute>
  <RecipeFormPage />
</ProtectedRoute>
```

**Current Behavior:** All users allowed (auth disabled)

**Future:** Redirects to login if not authenticated

### AdminRoute

Guards routes requiring admin privileges.

```tsx
<AdminRoute>
  <AdminPanel />
</AdminRoute>
```

### GuestRoute

Guards routes for non-authenticated users only.

```tsx
<GuestRoute>
  <LoginPage />
</GuestRoute>
```

### RoleBasedRoute

Guards routes based on specific roles.

```tsx
<RoleBasedRoute allowedRoles={['admin', 'editor']}>
  <EditorComponent />
</RoleBasedRoute>
```

## Router Configuration

Main router setup in `/routes/index.tsx`:

```tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'recipes/new', element: <ProtectedRoute><RecipeFormPage /></ProtectedRoute> },
      { path: 'recipes/:id', element: <RecipeDetailPage /> },
      { path: 'recipes/:id/edit', element: <ProtectedRoute><RecipeFormPage /></ProtectedRoute> },
      { path: 'search', element: <SearchResultsPage /> },
      { path: 'import', element: <ProtectedRoute><BulkImportPage /></ProtectedRoute> },
      { path: '404', element: <NotFoundPage /> },
      { path: '*', element: <NotFoundPage /> }
    ]
  }
]);
```

## Navigation Patterns

### Recipe Card Click

```tsx
const navigate = useNavigate();

const handleClick = () => {
  navigate(`/recipes/${recipe.id}`);
};
```

### Search Submission

```tsx
const handleSearch = () => {
  if (searchQuery.trim()) {
    navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
  }
};
```

### Form Submission

```tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // Submit to API (Phase 2)
  navigate('/'); // Redirect to home
};
```

### Cancel Action

```tsx
const handleCancel = () => {
  navigate(isEditMode ? `/recipes/${id}` : '/');
};
```

## Testing Routes

Routing tests use `MemoryRouter` for isolated testing:

```tsx
import { MemoryRouter, Routes, Route } from 'react-router-dom';

render(
  <MemoryRouter initialEntries={['/recipes/123']}>
    <Routes>
      <Route path="/recipes/:id" element={<RecipeDetailPage />} />
    </Routes>
  </MemoryRouter>
);
```

**Test Coverage:**
- Route rendering (20 tests)
- URL parameter extraction
- Navigation flows
- 404 handling
- Layout integration
- Route guard behavior

## Common Tasks

### Add a New Page

1. Create page component in `/pages/`
2. Add route to `/routes/index.tsx`
3. Add navigation link in `Navigation.tsx`
4. Add tests in `/tests/routes/`

### Add Route Protection

```tsx
{
  path: 'admin',
  element: (
    <AdminRoute>
      <AdminPage />
    </AdminRoute>
  )
}
```

### Handle Route Parameters

```tsx
const RecipePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  useEffect(() => {
    // Fetch recipe with id
  }, [id]);

  // ...
};
```

### Add Query Parameters

```tsx
const [searchParams, setSearchParams] = useSearchParams();

// Read
const filter = searchParams.get('filter');

// Set
setSearchParams({ filter: 'italian', sort: 'name' });
// URL: /recipes?filter=italian&sort=name
```

## Browser History

React Router uses the HTML5 History API for clean URLs:

```
✅ /recipes/123           (clean URL)
❌ /#/recipes/123         (hash routing - not used)
```

**Benefits:**
- SEO-friendly URLs
- Better user experience
- Native browser navigation

**Server Configuration:**
All routes must serve `index.html` for client-side routing to work. Vite dev server handles this automatically.

## Future Enhancements

Phase 2 will add:
- [ ] Actual authentication integration
- [ ] Role-based access control
- [ ] Protected route redirects
- [ ] Route-based code splitting
- [ ] Route prefetching
- [ ] Analytics integration
- [ ] Scroll restoration
- [ ] Route transitions/animations

## Resources

- [React Router Documentation](https://reactrouter.com/)
- [useNavigate Hook](https://reactrouter.com/hooks/use-navigate)
- [useParams Hook](https://reactrouter.com/hooks/use-params)
- [useSearchParams Hook](https://reactrouter.com/hooks/use-search-params)
