import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RecipeDetailPage from '@/pages/RecipeDetailPage';
import { recipeService } from '@/services';
import { ApiError } from '@/services/api.config';
import type { Recipe } from '@/types';

// Mock the recipe service
vi.mock('@/services', () => ({
  recipeService: {
    getById: vi.fn(),
    delete: vi.fn(),
  },
}));

// Mock date-fns
vi.mock('date-fns', () => ({
  format: vi.fn((date: Date, formatStr: string) => {
    return 'Jan 1, 2024';
  }),
}));

describe('RecipeDetailPage', () => {
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

  const mockRecipe: Recipe = {
    id: 'recipe-123',
    name: 'Pasta Carbonara',
    description: 'Classic Italian pasta dish with eggs and cheese',
    instructions: {
      steps: [
        'Cook pasta according to package directions',
        'Mix eggs and cheese in a bowl',
        'Combine hot pasta with egg mixture',
        'Serve immediately with black pepper',
      ],
    },
    prep_time: 10,
    cook_time: 15,
    servings: 4,
    difficulty: 'medium',
    cuisine_type: 'Italian',
    diet_types: ['vegetarian'],
    ingredients: [
      {
        id: 'ing-1',
        recipe_id: 'recipe-123',
        name: 'spaghetti',
        quantity: 400,
        unit: 'g',
        notes: 'Use good quality pasta',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'ing-2',
        recipe_id: 'recipe-123',
        name: 'eggs',
        quantity: 3,
        unit: 'pieces',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'ing-3',
        recipe_id: 'recipe-123',
        name: 'parmesan cheese',
        quantity: 100,
        unit: 'g',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ],
    categories: [
      {
        id: 'cat-1',
        name: 'Main Dishes',
        slug: 'main-dishes',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'cat-2',
        name: 'Pasta',
        slug: 'pasta',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ],
    nutritional_info: {
      id: 'nutr-1',
      recipe_id: 'recipe-123',
      calories: 450,
      protein_g: 18,
      carbohydrates_g: 60,
      fat_g: 15,
      fiber_g: 3,
      sugar_g: 2,
      sodium_mg: 350,
      cholesterol_mg: 120,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  };

  const renderPage = (recipeId: string = 'recipe-123') => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[`/recipes/${recipeId}`]}>
          <Routes>
            <Route path="/recipes/:id" element={<RecipeDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  describe('Loading State', () => {
    it('should display skeleton loader while fetching recipe', () => {
      vi.mocked(recipeService.getById).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderPage();

      // Skeleton should be visible (has animate-pulse class)
      const skeleton = screen.getByTestId = document.querySelector('.animate-pulse');
      expect(skeleton).toBeTruthy();
    });
  });

  describe('Success State', () => {
    beforeEach(() => {
      vi.mocked(recipeService.getById).mockResolvedValue(mockRecipe);
    });

    it('should display recipe name and description', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
        expect(
          screen.getByText('Classic Italian pasta dish with eggs and cheese')
        ).toBeInTheDocument();
      });
    });

    it('should display meta badges (cuisine, difficulty, diet)', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Italian')).toBeInTheDocument();
        expect(screen.getByText('Medium')).toBeInTheDocument();
        expect(screen.getByText('vegetarian')).toBeInTheDocument();
      });
    });

    it('should display timing information', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('10 min')).toBeInTheDocument(); // Prep time
        expect(screen.getByText('15 min')).toBeInTheDocument(); // Cook time
        expect(screen.getByText('25 min')).toBeInTheDocument(); // Total time (10 + 15)
      });
    });

    it('should display servings', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Servings')).toBeInTheDocument();
        const servingsValue = screen.getByText('Servings').nextElementSibling;
        expect(servingsValue).toHaveTextContent('4');
      });
    });

    it('should display ingredients with quantities and units', async () => {
      renderPage();

      await waitFor(() => {
        const ingredientsSection = screen.getByText('Ingredients').closest('.bg-white');
        expect(ingredientsSection).toHaveTextContent('400 g spaghetti');
        expect(ingredientsSection).toHaveTextContent('3 pieces eggs');
        expect(ingredientsSection).toHaveTextContent('100 g parmesan cheese');
      });
    });

    it('should display ingredient notes', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText(/Use good quality pasta/)).toBeInTheDocument();
      });
    });

    it('should display instructions as numbered steps', async () => {
      renderPage();

      await waitFor(() => {
        expect(
          screen.getByText('Cook pasta according to package directions')
        ).toBeInTheDocument();
        expect(screen.getByText('Mix eggs and cheese in a bowl')).toBeInTheDocument();
        expect(
          screen.getByText('Combine hot pasta with egg mixture')
        ).toBeInTheDocument();
        expect(
          screen.getByText('Serve immediately with black pepper')
        ).toBeInTheDocument();
      });
    });

    it('should display nutritional information', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Nutritional Information')).toBeInTheDocument();
        expect(screen.getByText('450')).toBeInTheDocument(); // Calories
        expect(screen.getByText('18g')).toBeInTheDocument(); // Protein
        expect(screen.getByText('60g')).toBeInTheDocument(); // Carbs
        expect(screen.getByText('15g')).toBeInTheDocument(); // Fat
      });
    });

    it('should display categories', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Categories')).toBeInTheDocument();
        expect(screen.getByText('Main Dishes')).toBeInTheDocument();
        expect(screen.getByText('Pasta')).toBeInTheDocument();
      });
    });

    it('should display action buttons', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Edit')).toBeInTheDocument();
        expect(screen.getByText('Delete')).toBeInTheDocument();
        expect(screen.getByText('Find Similar')).toBeInTheDocument();
      });
    });

    it('should display similar recipes placeholder', async () => {
      renderPage();

      await waitFor(() => {
        expect(
          screen.getByText(/Similar recipes feature coming soon/)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('should display 404 error message when recipe not found', async () => {
      const error = new ApiError('Recipe not found', 404);
      vi.mocked(recipeService.getById).mockRejectedValue(error);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Recipe Not Found')).toBeInTheDocument();
        expect(
          screen.getByText('Recipe not found. It may have been deleted.')
        ).toBeInTheDocument();
      });
    });

    it('should display generic error message for other errors', async () => {
      const error = new ApiError('Server error', 500);
      vi.mocked(recipeService.getById).mockRejectedValue(error);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Error Loading Recipe')).toBeInTheDocument();
        expect(screen.getByText('Server error')).toBeInTheDocument();
      });
    });

    it('should display network error message', async () => {
      const error = new ApiError('Network error. Please check your connection and try again.');
      vi.mocked(recipeService.getById).mockRejectedValue(error);

      renderPage();

      await waitFor(() => {
        expect(
          screen.getByText(/Network error. Please check your connection and try again./)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Delete Functionality', () => {
    beforeEach(() => {
      vi.mocked(recipeService.getById).mockResolvedValue(mockRecipe);
      vi.mocked(recipeService.delete).mockResolvedValue();
    });

    it('should show confirmation modal when delete button clicked', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
      });

      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText('Delete Recipe?')).toBeInTheDocument();
        expect(
          screen.getByText(/Are you sure you want to delete/)
        ).toBeInTheDocument();
      });
    });

    it('should close modal when cancel button clicked', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
      });

      // Open modal
      fireEvent.click(screen.getByText('Delete'));

      await waitFor(() => {
        expect(screen.getByText('Delete Recipe?')).toBeInTheDocument();
      });

      // Close modal
      const cancelButton = screen.getAllByText('Cancel')[0];
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText('Delete Recipe?')).not.toBeInTheDocument();
      });
    });

    it('should delete recipe when confirm button clicked', async () => {
      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
      });

      // Open modal
      fireEvent.click(screen.getByText('Delete'));

      await waitFor(() => {
        expect(screen.getByText('Delete Recipe?')).toBeInTheDocument();
      });

      // Confirm delete
      const confirmButtons = screen.getAllByText('Delete');
      const confirmButton = confirmButtons[confirmButtons.length - 1]; // Last "Delete" button in modal
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(recipeService.delete).toHaveBeenCalledWith('recipe-123');
      });
    });

    it('should show deleting state while deleting', async () => {
      let resolveDelete: () => void;
      vi.mocked(recipeService.delete).mockImplementation(
        () => new Promise((resolve) => { resolveDelete = resolve as any; })
      );

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
      });

      // Open modal
      fireEvent.click(screen.getByText('Delete'));

      await waitFor(() => {
        expect(screen.getByText('Delete Recipe?')).toBeInTheDocument();
      });

      // Click confirm
      const confirmButtons = screen.getAllByText('Delete');
      const confirmButton = confirmButtons[confirmButtons.length - 1];
      fireEvent.click(confirmButton);

      // Check for deleting state - use getAllByText since there might be multiple
      await waitFor(() => {
        const deletingTexts = screen.queryAllByText('Deleting...');
        expect(deletingTexts.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Empty Data Handling', () => {
    it('should handle recipe with no ingredients', async () => {
      const recipeWithoutIngredients = {
        ...mockRecipe,
        ingredients: [],
      };
      vi.mocked(recipeService.getById).mockResolvedValue(recipeWithoutIngredients);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('No ingredients listed')).toBeInTheDocument();
      });
    });

    it('should handle recipe with no instructions', async () => {
      const recipeWithoutInstructions = {
        ...mockRecipe,
        instructions: { steps: [] },
      };
      vi.mocked(recipeService.getById).mockResolvedValue(recipeWithoutInstructions);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('No instructions available')).toBeInTheDocument();
      });
    });

    it('should handle recipe without nutritional info', async () => {
      const recipeWithoutNutrition = {
        ...mockRecipe,
        nutritional_info: undefined,
      };
      vi.mocked(recipeService.getById).mockResolvedValue(recipeWithoutNutrition);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
        expect(screen.queryByText('Nutritional Information')).not.toBeInTheDocument();
      });
    });

    it('should handle recipe without categories', async () => {
      const recipeWithoutCategories = {
        ...mockRecipe,
        categories: [],
      };
      vi.mocked(recipeService.getById).mockResolvedValue(recipeWithoutCategories);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('Pasta Carbonara')).toBeInTheDocument();
        expect(screen.queryByText('Categories')).not.toBeInTheDocument();
      });
    });

    it('should handle ingredient without quantity or unit', async () => {
      const recipeWithSimpleIngredient = {
        ...mockRecipe,
        ingredients: [
          {
            id: 'ing-1',
            recipe_id: 'recipe-123',
            name: 'salt to taste',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ],
      };
      vi.mocked(recipeService.getById).mockResolvedValue(recipeWithSimpleIngredient);

      renderPage();

      await waitFor(() => {
        expect(screen.getByText('salt to taste')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    beforeEach(() => {
      vi.mocked(recipeService.getById).mockResolvedValue(mockRecipe);
    });

    it('should render mobile-friendly action buttons', async () => {
      renderPage();

      await waitFor(() => {
        const actionButtons = screen.getByText('Edit').parentElement;
        expect(actionButtons).toHaveClass('flex-wrap');
      });
    });

    it('should render responsive grid for ingredients and instructions', async () => {
      renderPage();

      await waitFor(() => {
        const grid = screen.getByText('Ingredients').closest('.grid');
        expect(grid).toHaveClass('lg:grid-cols-2');
      });
    });
  });
});
