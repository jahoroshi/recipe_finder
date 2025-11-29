import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import HomePage from '@/pages/HomePage';
import * as recipeService from '@/services/recipeService';
import { Recipe } from '@/types';

// Mock the recipe service
vi.mock('@/services/recipeService');

const createMockRecipe = (overrides?: Partial<Recipe>): Recipe => ({
  id: '123e4567-e89b-12d3-a456-426614174000',
  name: 'Test Recipe',
  description: 'A delicious test recipe',
  instructions: { steps: ['Step 1', 'Step 2'] },
  prep_time: 15,
  cook_time: 30,
  servings: 4,
  difficulty: 'medium',
  cuisine_type: 'Italian',
  diet_types: ['Vegetarian'],
  ingredients: [],
  categories: [],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

describe('HomePage - Filter Integration', () => {
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

  const renderHomePage = (initialUrl = '/') => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[initialUrl]}>
          <HomePage />
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  it('renders filter panel on desktop', async () => {
    vi.mocked(recipeService.recipeService.list).mockResolvedValue({
      items: [createMockRecipe()],
      total: 1,
      page: 1,
      page_size: 20,
      pages: 1,
    });

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('Cuisine Type')).toBeInTheDocument();
      expect(screen.getByText('Difficulty')).toBeInTheDocument();
      expect(screen.getByText('Diet Types')).toBeInTheDocument();
    });
  });

  it('shows mobile filter button on small screens', async () => {
    vi.mocked(recipeService.recipeService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage();

    await waitFor(() => {
      const filterButton = screen.getByRole('button', { name: /filters/i });
      expect(filterButton).toBeInTheDocument();
    });
  });

  it('applies cuisine filter from URL', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?cuisine_type=Italian');

    await waitFor(() => {
      expect(mockList).toHaveBeenCalledWith(
        expect.objectContaining({
          cuisine_type: 'Italian',
        })
      );
    });
  });

  it('applies difficulty filter from URL', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?difficulty=easy');

    await waitFor(() => {
      expect(mockList).toHaveBeenCalledWith(
        expect.objectContaining({
          difficulty: 'easy',
        })
      );
    });
  });

  it('applies diet types filter from URL', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?diet_types=Vegetarian,Vegan');

    await waitFor(() => {
      expect(mockList).toHaveBeenCalledWith(
        expect.objectContaining({
          diet_types: ['Vegetarian', 'Vegan'],
        })
      );
    });
  });

  it('applies time range filters from URL', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?min_prep_time=10&max_prep_time=30&min_cook_time=20&max_cook_time=60');

    await waitFor(() => {
      expect(mockList).toHaveBeenCalledWith(
        expect.objectContaining({
          min_prep_time: 10,
          max_prep_time: 30,
          min_cook_time: 20,
          max_cook_time: 60,
        })
      );
    });
  });

  it('applies servings filter from URL', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?min_servings=2&max_servings=6');

    await waitFor(() => {
      expect(mockList).toHaveBeenCalledWith(
        expect.objectContaining({
          min_servings: 2,
          max_servings: 6,
        })
      );
    });
  });

  it('displays active filter badges', async () => {
    vi.mocked(recipeService.recipeService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?cuisine_type=Italian&difficulty=easy');

    await waitFor(() => {
      expect(screen.getByText('Cuisine: Italian')).toBeInTheDocument();
      expect(screen.getByText('Difficulty: Easy')).toBeInTheDocument();
    });
  });

  it('removes filter when badge is clicked', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?cuisine_type=Italian&page=1');

    await waitFor(() => {
      expect(screen.getByText('Cuisine: Italian')).toBeInTheDocument();
    });

    const removeButton = screen.getByLabelText('Remove Cuisine: Italian filter');
    fireEvent.click(removeButton);

    await waitFor(() => {
      // Should be called without cuisine_type
      expect(mockList).toHaveBeenLastCalledWith(
        expect.objectContaining({
          page: 1,
          page_size: 20,
        })
      );
      expect(mockList).toHaveBeenLastCalledWith(
        expect.not.objectContaining({
          cuisine_type: expect.anything(),
        })
      );
    });
  });

  it('resets to page 1 when filters change', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [createMockRecipe()],
      total: 50,
      page: 1,
      page_size: 20,
      pages: 3,
    });

    renderHomePage('/?page=3');

    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });

    // Change cuisine filter
    const cuisineLabel = screen.getByText('Cuisine Type');
    const cuisineSelect = cuisineLabel.parentElement!.querySelector('select')!;
    fireEvent.change(cuisineSelect, { target: { value: 'Mexican' } });

    await waitFor(
      () => {
        // Should reset to page 1
        expect(mockList).toHaveBeenLastCalledWith(
          expect.objectContaining({
            page: 1,
            cuisine_type: 'Mexican',
          })
        );
      },
      { timeout: 1000 }
    );
  });

  it('shows empty state with filter-specific message', async () => {
    vi.mocked(recipeService.recipeService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?cuisine_type=Italian');

    await waitFor(() => {
      expect(screen.getByText('No recipes match your filters')).toBeInTheDocument();
      expect(screen.getByText(/try adjusting your filters/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear all filters/i })).toBeInTheDocument();
    });
  });

  it('combines multiple filters in API call', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?cuisine_type=Italian&difficulty=medium&diet_types=Vegetarian&min_prep_time=15&max_cook_time=45&min_servings=2');

    await waitFor(() => {
      expect(mockList).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        cuisine_type: 'Italian',
        difficulty: 'medium',
        diet_types: ['Vegetarian'],
        min_prep_time: 15,
        max_cook_time: 45,
        min_servings: 2,
      });
    });
  });

  it('updates React Query cache key when filters change', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [createMockRecipe()],
      total: 1,
      page: 1,
      page_size: 20,
      pages: 1,
    });

    renderHomePage();

    await waitFor(() => {
      expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    });

    const initialCallCount = mockList.mock.calls.length;

    // Change filter
    const cuisineLabel = screen.getByText('Cuisine Type');
    const cuisineSelect = cuisineLabel.parentElement!.querySelector('select')!;
    fireEvent.change(cuisineSelect, { target: { value: 'Mexican' } });

    await waitFor(
      () => {
        // Should make a new API call
        expect(mockList.mock.calls.length).toBeGreaterThan(initialCallCount);
      },
      { timeout: 1000 }
    );
  });

  it('shows filter count badge on mobile button', async () => {
    vi.mocked(recipeService.recipeService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?cuisine_type=Italian&difficulty=easy&diet_types=Vegetarian');

    await waitFor(() => {
      // Mobile filter button should show count of 3
      const filterButton = screen.getByRole('button', { name: /filters/i });
      const badge = filterButton.querySelector('.bg-teal-500');
      expect(badge?.textContent).toBe('3');
    });
  });

  it('removes individual diet type from multi-select', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?diet_types=Vegetarian,Vegan,Gluten-Free&page=1');

    await waitFor(() => {
      expect(screen.getByText('Diet: Vegetarian')).toBeInTheDocument();
      expect(screen.getByText('Diet: Vegan')).toBeInTheDocument();
      expect(screen.getByText('Diet: Gluten-Free')).toBeInTheDocument();
    });

    // Remove Vegan
    const removeVeganButton = screen.getByLabelText('Remove Diet: Vegan filter');
    fireEvent.click(removeVeganButton);

    await waitFor(() => {
      expect(mockList).toHaveBeenLastCalledWith(
        expect.objectContaining({
          diet_types: expect.arrayContaining(['Vegetarian', 'Gluten-Free']),
        })
      );
      expect(mockList).toHaveBeenLastCalledWith(
        expect.objectContaining({
          diet_types: expect.not.arrayContaining(['Vegan']),
        })
      );
    });
  });

  it('clears both min and max when removing time range badge', async () => {
    const mockList = vi.mocked(recipeService.recipeService.list);
    mockList.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      pages: 0,
    });

    renderHomePage('/?min_prep_time=10&max_prep_time=30&page=1');

    await waitFor(() => {
      expect(screen.getByText('Prep Time: 10-30 min')).toBeInTheDocument();
    });

    const removeButton = screen.getByLabelText('Remove Prep Time: 10-30 min filter');
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(mockList).toHaveBeenLastCalledWith(
        expect.not.objectContaining({
          min_prep_time: expect.anything(),
          max_prep_time: expect.anything(),
        })
      );
    });
  });
});
