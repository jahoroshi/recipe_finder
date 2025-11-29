import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SearchResultsPage from '@/pages/SearchResultsPage';
import { searchService } from '@/services';
import type { HybridSearchResponse, Recipe, Ingredient } from '@/types';

// Mock services
vi.mock('@/services', () => ({
  searchService: {
    hybrid: vi.fn(),
  },
  recipeService: {},
  healthService: {},
}));

// Mock search history utility
vi.mock('@/utils/searchHistory', () => ({
  addToSearchHistory: vi.fn(),
  getSearchHistory: vi.fn(() => []),
  clearSearchHistory: vi.fn(),
  removeFromSearchHistory: vi.fn(),
}));

const createMockRecipe = (id: string, name: string): Recipe => ({
  id,
  name,
  description: `Description for ${name}`,
  instructions: { steps: ['Step 1', 'Step 2'] },
  difficulty: 'medium' as const,
  diet_types: ['Vegetarian'],
  ingredients: [
    {
      id: `${id}-ingredient-1`,
      recipe_id: id,
      name: 'Test Ingredient',
      quantity: 100,
      unit: 'g',
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
    } as Ingredient,
  ],
  categories: [],
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
});

const createMockSearchResponse = (total: number = 5): HybridSearchResponse => ({
  query: 'test query',
  parsed_query: {
    original_query: 'test query',
    semantic_query: 'looking for test recipes',
    ingredients: ['pasta'],
    cuisine_type: 'Italian',
    diet_types: ['Vegetarian'],
    max_prep_time: 30,
    difficulty: 'easy',
  },
  results: Array.from({ length: Math.min(total, 20) }, (_, i) => ({
    recipe: createMockRecipe(`recipe-${i}`, `Test Recipe ${i + 1}`),
    score: 0.95 - i * 0.05,
    match_type: i % 3 === 0 ? 'hybrid' : i % 3 === 1 ? 'semantic' : 'filter',
  })),
  total,
  search_type: 'hybrid',
  metadata: {
    semantic_results: 3,
    filter_results: 2,
    merged_results: 5,
    final_results: 5,
  },
});

describe('SearchResultsPage', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const renderWithRouter = (initialRoute = '/search') => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[initialRoute]}>
          <SearchResultsPage />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  describe('No Query State', () => {
    it('shows empty state when no query parameter', () => {
      renderWithRouter('/search');

      expect(screen.getByText(/start your recipe search/i)).toBeInTheDocument();
      expect(screen.getByText(/use natural language/i)).toBeInTheDocument();
    });

    it('shows example searches', () => {
      renderWithRouter('/search');

      expect(screen.getByText(/"quick dinner recipes under 30 minutes"/i)).toBeInTheDocument();
      expect(screen.getByText(/"vegetarian pasta dishes"/i)).toBeInTheDocument();
      expect(screen.getByText(/"easy italian desserts"/i)).toBeInTheDocument();
      expect(screen.getByText(/"healthy breakfast with eggs"/i)).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('shows skeleton loaders while searching', async () => {
      vi.mocked(searchService.hybrid).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        // Check for loading skeleton or spinner
        const skeletons = screen.queryAllByTestId('recipe-card-skeleton');
        expect(skeletons.length > 0 || screen.getByLabelText(/searching/i)).toBeTruthy();
      });
    });
  });

  describe('Search Results', () => {
    it('displays search results successfully', async () => {
      const mockResponse = createMockSearchResponse(5);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test+query');

      await waitFor(() => {
        expect(screen.getByText(/search results for "test query"/i)).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Test Recipe 1')).toBeInTheDocument();
        expect(screen.getByText('Test Recipe 2')).toBeInTheDocument();
      });
    });

    it('displays AI parsed query information', async () => {
      const mockResponse = createMockSearchResponse(5);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=quick+vegetarian+pasta');

      await waitFor(() => {
        expect(screen.getByText(/ai understood your search/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/looking for test recipes/i)).toBeInTheDocument();
      expect(screen.getByText(/pasta/i)).toBeInTheDocument();
      expect(screen.getByText(/italian/i)).toBeInTheDocument();
      expect(screen.getByText(/vegetarian/i)).toBeInTheDocument();
    });

    it('shows relevance scores on recipe cards', async () => {
      const mockResponse = createMockSearchResponse(3);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.getByText(/95%/)).toBeInTheDocument();
        expect(screen.getByText(/90%/)).toBeInTheDocument();
        expect(screen.getByText(/85%/)).toBeInTheDocument();
      });
    });

    it('shows match type badges', async () => {
      const mockResponse = createMockSearchResponse(3);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.getByText(/best match/i)).toBeInTheDocument();
        expect(screen.getByText(/similar/i)).toBeInTheDocument();
        expect(screen.getByText(/exact match/i)).toBeInTheDocument();
      });
    });

    it('displays search metadata', async () => {
      const mockResponse = createMockSearchResponse(5);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.getByText(/found/i)).toBeInTheDocument();
        expect(screen.getByText('5')).toBeInTheDocument();
        expect(screen.getByText(/semantic: 3/i)).toBeInTheDocument();
        expect(screen.getByText(/filter: 2/i)).toBeInTheDocument();
      });
    });

    it('collapses/expands parsed query section', async () => {
      const mockResponse = createMockSearchResponse(5);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.getByText(/ai understood your search/i)).toBeInTheDocument();
      });

      const showHideButton = screen.getByText(/hide/i);
      fireEvent.click(showHideButton);

      expect(screen.getByText(/show/i)).toBeInTheDocument();
    });
  });

  describe('No Results State', () => {
    it('shows no results message when search returns empty', async () => {
      vi.mocked(searchService.hybrid).mockResolvedValue({
        query: 'test',
        results: [],
        total: 0,
        search_type: 'hybrid',
      });

      renderWithRouter('/search?q=nonexistent');

      await waitFor(() => {
        expect(screen.getByText(/no recipes found for "nonexistent"/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/using different keywords/i)).toBeInTheDocument();
      expect(screen.getByText(/removing some filters/i)).toBeInTheDocument();
    });

    it('shows clear filters button in no results state', async () => {
      vi.mocked(searchService.hybrid).mockResolvedValue({
        query: 'test',
        results: [],
        total: 0,
        search_type: 'hybrid',
      });

      renderWithRouter('/search?q=test&cuisine_type=Italian');

      await waitFor(() => {
        expect(screen.getByText(/clear filters/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('shows error message on API failure', async () => {
      vi.mocked(searchService.hybrid).mockRejectedValue(new Error('API Error'));

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.getByText(/search failed/i)).toBeInTheDocument();
      });
    });

    it('shows retry button on error', async () => {
      vi.mocked(searchService.hybrid).mockRejectedValue(new Error('Network error'));

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        const retryButton = screen.getByRole('button', { name: /retry/i });
        expect(retryButton).toBeInTheDocument();
      });
    });
  });

  describe('Filter Integration', () => {
    it('shows filter panel on desktop', async () => {
      renderWithRouter('/search?q=test');

      // Filter panel should be present (hidden on mobile via CSS)
      expect(screen.getByText(/filters/i)).toBeInTheDocument();
    });

    it('shows active filter badges', async () => {
      const mockResponse = createMockSearchResponse(5);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test&cuisine_type=Italian&difficulty=easy');

      await waitFor(() => {
        expect(screen.getByText(/italian/i)).toBeInTheDocument();
        expect(screen.getByText(/easy/i)).toBeInTheDocument();
      });
    });

    it('applies filters to search query', async () => {
      vi.mocked(searchService.hybrid).mockResolvedValue(createMockSearchResponse(5));

      renderWithRouter('/search?q=test&cuisine_type=Italian&difficulty=easy');

      await waitFor(() => {
        expect(searchService.hybrid).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'test',
            filters: expect.objectContaining({
              cuisine_type: 'Italian',
              difficulty: 'easy',
            }),
          })
        );
      });
    });
  });

  describe('Pagination', () => {
    it('shows pagination when results exceed page size', async () => {
      const mockResponse = createMockSearchResponse(50);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.getByLabelText(/go to next page/i)).toBeInTheDocument();
      });
    });

    it('does not show pagination for small result sets', async () => {
      const mockResponse = createMockSearchResponse(5);
      vi.mocked(searchService.hybrid).mockResolvedValue(mockResponse);

      renderWithRouter('/search?q=test');

      await waitFor(() => {
        expect(screen.queryByLabelText(/go to next page/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Search Submission', () => {
    it('updates URL when search button clicked', async () => {
      vi.mocked(searchService.hybrid).mockResolvedValue(createMockSearchResponse(5));

      renderWithRouter('/search');

      const input = screen.getByRole('textbox');
      const searchButton = screen.getByRole('button', { name: /search/i });

      fireEvent.change(input, { target: { value: 'new search' } });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(searchService.hybrid).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'new search',
          })
        );
      });
    });

    it('preserves filters when performing new search', async () => {
      vi.mocked(searchService.hybrid).mockResolvedValue(createMockSearchResponse(5));

      renderWithRouter('/search?cuisine_type=Italian');

      const input = screen.getByRole('textbox');
      const searchButton = screen.getByRole('button', { name: /search/i });

      fireEvent.change(input, { target: { value: 'pasta' } });
      fireEvent.click(searchButton);

      await waitFor(() => {
        expect(searchService.hybrid).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'pasta',
            filters: expect.objectContaining({
              cuisine_type: 'Italian',
            }),
          })
        );
      });
    });
  });

  describe('Search History', () => {
    it('adds successful search to history', async () => {
      const { addToSearchHistory } = await import('@/utils/searchHistory');
      vi.mocked(searchService.hybrid).mockResolvedValue(createMockSearchResponse(5));

      renderWithRouter('/search?q=test+query');

      await waitFor(() => {
        expect(addToSearchHistory).toHaveBeenCalledWith('test query');
      });
    });
  });

  describe('Mobile Responsive', () => {
    it('shows mobile filter button', () => {
      renderWithRouter('/search?q=test');

      // Mobile filter button with "Filters" text should be present
      const filterButtons = screen.getAllByText(/filters/i);
      expect(filterButtons.length).toBeGreaterThan(0);
    });

    it('shows filter count badge on mobile button', async () => {
      renderWithRouter('/search?q=test&cuisine_type=Italian&difficulty=easy');

      await waitFor(() => {
        // Should show count badge with "2" (for 2 active filters)
        const badges = screen.getAllByText('2');
        expect(badges.length).toBeGreaterThan(0);
      });
    });
  });
});
