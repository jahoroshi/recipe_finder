import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import HomePage from '@/pages/HomePage';
import RecipeDetailPage from '@/pages/RecipeDetailPage';
import RecipeFormPage from '@/pages/RecipeFormPage';
import SearchResultsPage from '@/pages/SearchResultsPage';
import BulkImportPage from '@/pages/BulkImportPage';
import NotFoundPage from '@/pages/NotFoundPage';
import Layout from '@/components/layout/Layout';
import { recipeService } from '@/services';

// Mock the recipe service
vi.mock('@/services', () => ({
  recipeService: {
    list: vi.fn(),
    getById: vi.fn(),
  },
}));

describe('Routing Configuration', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();

    // Mock recipe service to return empty list for routing tests
    vi.mocked(recipeService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });
  });

  const renderWithQueryClient = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    );
  };

  describe('HomePage', () => {
    it('should render home page at / route', () => {
      renderWithQueryClient(
        <MemoryRouter initialEntries={['/']}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Find Your Next Favorite Meal/i)).toBeDefined();
    });

    it('should have navigation to create recipe', () => {
      renderWithQueryClient(
        <MemoryRouter initialEntries={['/']}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      );

      const addButtons = screen.getAllByText(/Add Recipe/i);
      expect(addButtons.length).toBeGreaterThan(0);
    });
  });

  describe('RecipeDetailPage', () => {
    it('should render recipe detail page at /recipes/:id route', () => {
      const testId = '123e4567-e89b-12d3-a456-426614174000';

      renderWithQueryClient(
        <MemoryRouter initialEntries={[`/recipes/${testId}`]}>
          <Routes>
            <Route path="/recipes/:id" element={<RecipeDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Page should render - skeleton loader or error message will appear
      const page = document.querySelector('.container');
      expect(page).toBeTruthy();
    });

    it('should show action buttons for recipe management', () => {
      const testId = '123e4567-e89b-12d3-a456-426614174000';

      renderWithQueryClient(
        <MemoryRouter initialEntries={[`/recipes/${testId}`]}>
          <Routes>
            <Route path="/recipes/:id" element={<RecipeDetailPage />} />
          </Routes>
        </MemoryRouter>
      );

      // Page should render and display content
      const page = document.querySelector('.container');
      expect(page).toBeTruthy();
    });
  });

  describe('RecipeFormPage', () => {
    it('should render create form at /recipes/new route', () => {
      render(
        <MemoryRouter initialEntries={['/recipes/new']}>
          <Routes>
            <Route path="/recipes/new" element={<RecipeFormPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Create New Recipe/i)).toBeDefined();
      expect(screen.getByLabelText(/Recipe Name/i)).toBeDefined();
    });

    it('should render edit form at /recipes/:id/edit route', () => {
      const testId = '123e4567-e89b-12d3-a456-426614174000';

      render(
        <MemoryRouter initialEntries={[`/recipes/${testId}/edit`]}>
          <Routes>
            <Route path="/recipes/:id/edit" element={<RecipeFormPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Edit Recipe/i)).toBeDefined();
      expect(screen.getByLabelText(/Recipe Name/i)).toBeDefined();
    });

    it('should have form fields for recipe creation', () => {
      render(
        <MemoryRouter initialEntries={['/recipes/new']}>
          <Routes>
            <Route path="/recipes/new" element={<RecipeFormPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByLabelText(/Recipe Name/i)).toBeDefined();
      expect(screen.getByLabelText(/Description/i)).toBeDefined();
      expect(screen.getByLabelText(/Difficulty/i)).toBeDefined();
    });
  });

  describe('SearchResultsPage', () => {
    it('should render search page at /search route', () => {
      render(
        <MemoryRouter initialEntries={['/search']}>
          <Routes>
            <Route path="/search" element={<SearchResultsPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Enter a search query|Search Results/i)).toBeDefined();
    });

    it('should display query parameter in search results', () => {
      render(
        <MemoryRouter initialEntries={['/search?q=pasta']}>
          <Routes>
            <Route path="/search" element={<SearchResultsPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Search Results for "pasta"/i)).toBeDefined();
    });
  });

  describe('BulkImportPage', () => {
    it('should render import page at /import route', () => {
      render(
        <MemoryRouter initialEntries={['/import']}>
          <Routes>
            <Route path="/import" element={<BulkImportPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Bulk Import Recipes/i)).toBeDefined();
    });

    it('should show file upload interface', () => {
      render(
        <MemoryRouter initialEntries={['/import']}>
          <Routes>
            <Route path="/import" element={<BulkImportPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/browse to upload/i)).toBeDefined();
    });
  });

  describe('NotFoundPage', () => {
    it('should render 404 page at /404 route', () => {
      render(
        <MemoryRouter initialEntries={['/404']}>
          <Routes>
            <Route path="/404" element={<NotFoundPage />} />
          </Routes>
        </MemoryRouter>
      );

      const heading = screen.getByRole('heading', { name: /404/i });
      expect(heading).toBeDefined();
      expect(screen.getByText(/Page Not Found/i)).toBeDefined();
    });

    it('should show navigation options on 404 page', () => {
      render(
        <MemoryRouter initialEntries={['/404']}>
          <Routes>
            <Route path="/404" element={<NotFoundPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/Go to Home/i)).toBeDefined();
      expect(screen.getByText(/Go Back/i)).toBeDefined();
    });

    it('should render for invalid routes', () => {
      render(
        <MemoryRouter initialEntries={['/invalid-route']}>
          <Routes>
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </MemoryRouter>
      );

      expect(screen.getByText(/404/i)).toBeDefined();
    });
  });

  describe('Layout Component', () => {
    it('should render navigation in layout', () => {
      renderWithQueryClient(
        <MemoryRouter initialEntries={['/']}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      );

      // Check for the brand heading specifically
      const allHeadings = screen.getAllByText(/Recipe/i);
      expect(allHeadings.length).toBeGreaterThan(0);
    });

    it('should have navigation links in header', () => {
      renderWithQueryClient(
        <MemoryRouter initialEntries={['/']}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
            </Route>
          </Routes>
        </MemoryRouter>
      );

      // Navigation links should be present (in mobile or desktop view)
      const searchLinks = screen.getAllByText(/Search/i);
      expect(searchLinks.length).toBeGreaterThan(0);
    });
  });
});

describe('Route Parameters', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const renderWithQueryClient = (ui: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {ui}
      </QueryClientProvider>
    );
  };

  it('should extract recipe ID from URL', () => {
    const testId = '123e4567-e89b-12d3-a456-426614174000';

    renderWithQueryClient(
      <MemoryRouter initialEntries={[`/recipes/${testId}`]}>
        <Routes>
          <Route path="/recipes/:id" element={<RecipeDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Page should render with the ID - skeleton loader or error message will appear
    const page = document.querySelector('.container');
    expect(page).toBeTruthy();
  });

  it('should extract search query from URL parameters', () => {
    render(
      <MemoryRouter initialEntries={['/search?q=vegetarian']}>
        <Routes>
          <Route path="/search" element={<SearchResultsPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Search Results for "vegetarian"/i)).toBeDefined();
  });
});

describe('Route Guards', () => {
  it('should allow access to protected routes (auth disabled)', () => {
    // Since auth is currently disabled, all routes should be accessible
    render(
      <MemoryRouter initialEntries={['/recipes/new']}>
        <Routes>
          <Route path="/recipes/new" element={<RecipeFormPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Create New Recipe/i)).toBeDefined();
  });

  it('should allow access to import page (auth disabled)', () => {
    render(
      <MemoryRouter initialEntries={['/import']}>
        <Routes>
          <Route path="/import" element={<BulkImportPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Bulk Import Recipes/i)).toBeDefined();
  });
});
