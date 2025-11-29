import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import HomePage from '@/pages/HomePage';
import { recipeService } from '@/services';
import type { RecipeListResponse, Recipe } from '@/types';

// Mock the recipe service
vi.mock('@/services', () => ({
  recipeService: {
    list: vi.fn(),
  },
}));

describe('HomePage Component', () => {
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

  const renderHomePage = (initialEntries: string[] = ['/']) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={initialEntries}>
          <HomePage />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  const mockRecipe: Recipe = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    name: 'Test Recipe',
    description: 'A delicious test recipe',
    instructions: { steps: ['Step 1', 'Step 2'] },
    prep_time: 15,
    cook_time: 30,
    servings: 4,
    difficulty: 'medium',
    cuisine_type: 'Italian',
    diet_types: ['vegetarian'],
    ingredients: [
      {
        id: '456e7890-e89b-12d3-a456-426614174001',
        recipe_id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Tomatoes',
        quantity: 3,
        unit: 'pieces',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      },
    ],
    categories: [],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  };

  const mockRecipeListResponse: RecipeListResponse = {
    items: [mockRecipe],
    total: 1,
    page: 1,
    page_size: 20,
    pages: 1,
  };

  it('should render loading skeletons while fetching', () => {
    vi.mocked(recipeService.list).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderHomePage();

    // Should show multiple skeleton loaders
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should render recipes after successful fetch', async () => {
    vi.mocked(recipeService.list).mockResolvedValue(mockRecipeListResponse);

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });

    expect(screen.getByText('1 Recipes')).toBeInTheDocument();
  });

  it('should render empty state when no recipes', async () => {
    vi.mocked(recipeService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('No recipes yet')).toBeInTheDocument();
    });

    expect(screen.getByText(/Start building your recipe collection/i)).toBeInTheDocument();
  });

  it('should render error state on fetch failure', async () => {
    vi.mocked(recipeService.list).mockRejectedValue(new Error('Network error'));

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('Failed to load recipes')).toBeInTheDocument();
    });

    expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('should render pagination when multiple pages exist', async () => {
    vi.mocked(recipeService.list).mockResolvedValue({
      items: Array(20).fill(mockRecipe).map((r, i) => ({ ...r, id: `recipe-${i}` })),
      total: 100,
      page: 1,
      page_size: 20,
      pages: 5,
    });

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText((content, element) => {
        return element?.textContent === 'Showing 1 to 20 of 100 recipes';
      })).toBeInTheDocument();
    });

    expect(screen.getByLabelText('Next page')).toBeInTheDocument();
    expect(screen.getByLabelText('Previous page')).toBeInTheDocument();
  });

  it('should not render pagination when only one page', async () => {
    vi.mocked(recipeService.list).mockResolvedValue(mockRecipeListResponse);

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });

    expect(screen.queryByLabelText('Next page')).not.toBeInTheDocument();
  });

  it('should fetch correct page from URL parameters', async () => {
    vi.mocked(recipeService.list).mockResolvedValue({
      items: [mockRecipe],
      total: 100,
      page: 3,
      page_size: 20,
      pages: 5,
    });

    renderHomePage(['/?page=3']);

    await waitFor(() => {
      expect(recipeService.list).toHaveBeenCalledWith({
        page: 3,
        page_size: 20,
      });
    });
  });

  it('should default to page 1 when no page parameter', async () => {
    vi.mocked(recipeService.list).mockResolvedValue(mockRecipeListResponse);

    renderHomePage();

    await waitFor(() => {
      expect(recipeService.list).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
      });
    });
  });

  it('should render hero section with search bar', async () => {
    vi.mocked(recipeService.list).mockResolvedValue(mockRecipeListResponse);

    renderHomePage();

    expect(screen.getByText('Find Your Next Favorite Meal')).toBeInTheDocument();
    expect(
      screen.getByText(/Search our collection of delicious recipes/i)
    ).toBeInTheDocument();
  });

  it('should render Add Recipe button', async () => {
    vi.mocked(recipeService.list).mockResolvedValue(mockRecipeListResponse);

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('Add Recipe')).toBeInTheDocument();
    });
  });

  it('should use page size of 20', async () => {
    vi.mocked(recipeService.list).mockResolvedValue(mockRecipeListResponse);

    renderHomePage();

    await waitFor(() => {
      expect(recipeService.list).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
      });
    });
  });
});
