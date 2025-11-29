import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RecipeFormPage from '@/pages/RecipeFormPage';
import { recipeService } from '@/services';
import type { Recipe, RecipeCreate } from '@/types';

// Mock the services
vi.mock('@/services', () => ({
  recipeService: {
    create: vi.fn(),
    update: vi.fn(),
    getById: vi.fn(),
  },
}));

// Mock navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock window.confirm
global.confirm = vi.fn(() => true);

describe('RecipeFormPage', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderCreateForm = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/recipes/new']}>
          <Routes>
            <Route path="/recipes/new" element={<RecipeFormPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  const renderEditForm = (recipeId: string, recipe: Recipe) => {
    vi.mocked(recipeService.getById).mockResolvedValue(recipe);

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[`/recipes/${recipeId}/edit`]}>
          <Routes>
            <Route path="/recipes/:id/edit" element={<RecipeFormPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };

  describe('Create Mode', () => {
    it('should render create form with all sections', () => {
      renderCreateForm();

      expect(screen.getByText('Create New Recipe')).toBeInTheDocument();
      expect(screen.getByText('Basic Information')).toBeInTheDocument();
      expect(screen.getByText('Timing & Servings')).toBeInTheDocument();
      expect(screen.getByText(/Ingredients/)).toBeInTheDocument();
      expect(screen.getByText(/Instructions/)).toBeInTheDocument();
      expect(screen.getByText('Nutritional Information')).toBeInTheDocument();
    });

    it('should have default values', () => {
      renderCreateForm();

      const nameInput = screen.getByLabelText(/Recipe Name/);
      const difficultySelect = screen.getByLabelText('Difficulty');

      expect(nameInput).toHaveValue('');
      expect(difficultySelect).toHaveValue('medium');
    });

    it('should validate required fields', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const submitButton = screen.getByRole('button', { name: /Create Recipe/ });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Recipe name is required')).toBeInTheDocument();
      });

      // Note: Ingredient and instruction validation only applies to the first field
      // which users can fill, so we don't test those here

      expect(recipeService.create).not.toHaveBeenCalled();
    });

    it('should validate name length', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const nameInput = screen.getByLabelText(/Recipe Name/);

      // Test max length (256 chars should fail)
      await user.type(nameInput, 'a'.repeat(256));
      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(screen.getByText('Name must be at most 255 characters')).toBeInTheDocument();
      });
    });

    it('should validate total time under 24 hours', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const prepTimeInput = screen.getByLabelText(/Prep Time/);
      const cookTimeInput = screen.getByLabelText(/Cook Time/);

      await user.clear(prepTimeInput);
      await user.type(prepTimeInput, '720');
      await user.clear(cookTimeInput);
      await user.type(cookTimeInput, '720');

      // Fill required fields to trigger validation
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test');
      const ingredientFields = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientFields[0], 'Test Ingredient');
      await user.type(await screen.findByPlaceholderText('Step 1...'), 'Test Step');

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(screen.getByText('Total time must be less than 24 hours')).toBeInTheDocument();
      });
    });

    it('should add and remove ingredients', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      // Initially 1 ingredient field
      expect(screen.getAllByPlaceholderText(/Ingredient name/)).toHaveLength(1);

      // Add ingredient
      const addButton = screen.getByRole('button', { name: /Add Ingredient/ });
      await user.click(addButton);

      expect(screen.getAllByPlaceholderText(/Ingredient name/)).toHaveLength(2);

      // Remove ingredient (now we have 2, so remove buttons should appear)
      const removeButtons = screen.getAllByTitle('Remove ingredient');
      await user.click(removeButtons[0]);

      expect(screen.getAllByPlaceholderText(/Ingredient name/)).toHaveLength(1);
    });

    it('should add and remove instruction steps', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      // Initially 1 step
      const initialStep = await screen.findByPlaceholderText('Step 1...');
      expect(initialStep).toBeInTheDocument();

      // Add step
      const addButton = screen.getByRole('button', { name: /Add Step/ });
      await user.click(addButton);

      expect(await screen.findByPlaceholderText('Step 1...')).toBeInTheDocument();
      expect(await screen.findByPlaceholderText('Step 2...')).toBeInTheDocument();

      // Remove step
      const removeButtons = screen.getAllByTitle('Remove step');
      await user.click(removeButtons[0]);

      await waitFor(() => {
        expect(screen.queryByPlaceholderText('Step 2...')).not.toBeInTheDocument();
      });
      expect(await screen.findByPlaceholderText('Step 1...')).toBeInTheDocument();
    });

    it('should toggle nutritional information section', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      // Initially hidden
      expect(screen.queryByLabelText('Calories')).not.toBeInTheDocument();

      // Show nutrition
      const showButton = screen.getByRole('button', { name: 'Show' });
      await user.click(showButton);

      expect(screen.getByLabelText('Calories')).toBeInTheDocument();
      expect(screen.getByLabelText(/Protein/)).toBeInTheDocument();

      // Hide nutrition
      const hideButton = screen.getByRole('button', { name: 'Hide' });
      await user.click(hideButton);

      expect(screen.queryByLabelText('Calories')).not.toBeInTheDocument();
    });

    it('should display computed total time', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const prepTimeInput = screen.getByLabelText(/Prep Time/);
      const cookTimeInput = screen.getByLabelText(/Cook Time/);

      await user.clear(prepTimeInput);
      await user.type(prepTimeInput, '30');
      await user.clear(cookTimeInput);
      await user.type(cookTimeInput, '45');

      await waitFor(() => {
        expect(screen.getByText(/Total Time: 75 minutes/)).toBeInTheDocument();
      });
    });

    it('should handle diet type checkboxes', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const vegetarianCheckbox = screen.getByLabelText('vegetarian');
      const veganCheckbox = screen.getByLabelText('vegan');

      await user.click(vegetarianCheckbox);
      await user.click(veganCheckbox);

      expect(vegetarianCheckbox).toBeChecked();
      expect(veganCheckbox).toBeChecked();

      await user.click(vegetarianCheckbox);

      expect(vegetarianCheckbox).not.toBeChecked();
      expect(veganCheckbox).toBeChecked();
    });

    it('should create recipe successfully', async () => {
      const user = userEvent.setup();
      const newRecipe: Recipe = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Recipe',
        description: 'Test Description',
        instructions: { steps: ['Step 1', 'Step 2'] },
        difficulty: 'medium',
        diet_types: ['vegetarian'],
        ingredients: [
          {
            id: '123',
            recipe_id: '123e4567-e89b-12d3-a456-426614174000',
            name: 'Pasta',
            quantity: 400,
            unit: 'g',
            notes: '',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ],
        categories: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(recipeService.create).mockResolvedValue(newRecipe);

      renderCreateForm();

      // Fill in form
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test Recipe');
      await user.type(screen.getByLabelText('Description'), 'Test Description');
      await user.selectOptions(screen.getByLabelText('Difficulty'), 'medium');
      await user.click(screen.getByLabelText('vegetarian'));

      const ingredientInputs = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientInputs[0], 'Pasta');

      const qtyInputs = screen.getAllByPlaceholderText('Qty');
      await user.type(qtyInputs[0], '400');

      const unitInputs = screen.getAllByPlaceholderText('Unit');
      await user.type(unitInputs[0], 'g');

      await user.type(await screen.findByPlaceholderText('Step 1...'), 'Step 1');

      // Add second step
      await user.click(screen.getByRole('button', { name: /Add Step/ }));
      await user.type(await screen.findByPlaceholderText('Step 2...'), 'Step 2');

      // Submit form
      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(recipeService.create).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'Test Recipe',
            description: 'Test Description',
            difficulty: 'medium',
            diet_types: ['vegetarian'],
            ingredients: [
              {
                name: 'Pasta',
                quantity: 400,
                unit: 'g',
                notes: undefined,
              },
            ],
            instructions: {
              steps: ['Step 1', 'Step 2'],
            },
          })
        );
      });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/recipes/123e4567-e89b-12d3-a456-426614174000');
      });
    });

    it('should create recipe with nutritional info', async () => {
      const user = userEvent.setup();
      const newRecipe: Recipe = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Recipe',
        instructions: { steps: ['Step 1'] },
        difficulty: 'easy',
        diet_types: [],
        ingredients: [],
        categories: [],
        nutritional_info: {
          id: 'nutri-123',
          recipe_id: '123e4567-e89b-12d3-a456-426614174000',
          calories: 500,
          protein_g: 20,
          carbohydrates_g: 60,
          fat_g: 15,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(recipeService.create).mockResolvedValue(newRecipe);

      renderCreateForm();

      // Fill required fields
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test Recipe');
      const ingredientInputs = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientInputs[0], 'Test');
      await user.type(await screen.findByPlaceholderText('Step 1...'), 'Step 1');

      // Show and fill nutrition
      await user.click(screen.getByRole('button', { name: 'Show' }));
      await user.type(screen.getByLabelText('Calories'), '500');
      await user.type(screen.getByLabelText(/Protein/), '20');
      await user.type(screen.getByLabelText(/Carbs/), '60');
      await user.type(screen.getByLabelText(/Fat/), '15');

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(recipeService.create).toHaveBeenCalledWith(
          expect.objectContaining({
            nutritional_info: {
              calories: 500,
              protein_g: 20,
              carbohydrates_g: 60,
              fat_g: 15,
              fiber_g: undefined,
              sugar_g: undefined,
              sodium_mg: undefined,
              cholesterol_mg: undefined,
            },
          })
        );
      });
    });

    it('should handle creation error', async () => {
      const user = userEvent.setup();
      const error = new Error('Failed to create recipe');
      vi.mocked(recipeService.create).mockRejectedValue(error);

      renderCreateForm();

      // Fill minimum required fields
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test Recipe');
      const ingredientInputs = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientInputs[0], 'Test');
      await user.type(await screen.findByPlaceholderText('Step 1...'), 'Step 1');

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(recipeService.create).toHaveBeenCalled();
      });

      // Should not navigate on error
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should show cancel confirmation', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      await user.click(screen.getByRole('button', { name: 'Cancel' }));

      expect(global.confirm).toHaveBeenCalledWith('Discard changes?');
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Edit Mode', () => {
    const mockRecipe: Recipe = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      name: 'Existing Recipe',
      description: 'Existing Description',
      cuisine_type: 'Italian',
      difficulty: 'hard',
      diet_types: ['vegetarian', 'vegan'],
      prep_time: 30,
      cook_time: 45,
      servings: 4,
      instructions: { steps: ['Existing Step 1', 'Existing Step 2'] },
      ingredients: [
        {
          id: 'ing-1',
          recipe_id: '123e4567-e89b-12d3-a456-426614174000',
          name: 'Existing Ingredient',
          quantity: 200,
          unit: 'g',
          notes: 'test note',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ],
      categories: [],
      nutritional_info: {
        id: 'nutri-1',
        recipe_id: '123e4567-e89b-12d3-a456-426614174000',
        calories: 300,
        protein_g: 15,
        carbohydrates_g: 40,
        fat_g: 10,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    it('should show loading state while fetching recipe', async () => {
      vi.mocked(recipeService.getById).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      // Should show loading skeleton
      await waitFor(() => {
        expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
      });
    });

    it('should render edit form with existing data', async () => {
      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Existing Recipe')).toBeInTheDocument();
      });

      expect(screen.getByText('Edit Recipe')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Existing Description')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Italian')).toBeInTheDocument();

      // Note: There may be multiple inputs with same values, use getAllByDisplayValue
      const allWithValue30 = screen.getAllByDisplayValue('30');
      expect(allWithValue30.length).toBeGreaterThan(0);

      const allWithValue45 = screen.getAllByDisplayValue('45');
      expect(allWithValue45.length).toBeGreaterThan(0);

      const allWithValue4 = screen.getAllByDisplayValue('4');
      expect(allWithValue4.length).toBeGreaterThan(0);

      expect(screen.getByDisplayValue('Existing Ingredient')).toBeInTheDocument();
      const allWithValue200 = screen.getAllByDisplayValue('200');
      expect(allWithValue200.length).toBeGreaterThan(0);

      expect(screen.getByDisplayValue('g')).toBeInTheDocument();
      expect(screen.getByDisplayValue('test note')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Existing Step 1')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Existing Step 2')).toBeInTheDocument();

      // Diet types should be checked
      expect(screen.getByLabelText('vegetarian')).toBeChecked();
      expect(screen.getByLabelText('vegan')).toBeChecked();

      // Difficulty should be selected
      const difficultySelect = screen.getByLabelText('Difficulty');
      expect(difficultySelect).toHaveValue('hard');
    });

    it('should pre-populate and show nutritional info in edit mode', async () => {
      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Existing Recipe')).toBeInTheDocument();
      });

      // Nutrition should be visible
      expect(screen.getByLabelText('Calories')).toBeInTheDocument();
      expect(screen.getByDisplayValue('300')).toBeInTheDocument();
      expect(screen.getByDisplayValue('15')).toBeInTheDocument();
      expect(screen.getByDisplayValue('40')).toBeInTheDocument();
      expect(screen.getByDisplayValue('10')).toBeInTheDocument();
    });

    it('should update recipe successfully', async () => {
      const user = userEvent.setup();
      const updatedRecipe: Recipe = {
        ...mockRecipe,
        name: 'Updated Recipe',
      };

      vi.mocked(recipeService.update).mockResolvedValue(updatedRecipe);

      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Existing Recipe')).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/Recipe Name/);
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Recipe');

      await user.click(screen.getByRole('button', { name: /Update Recipe/ }));

      await waitFor(() => {
        expect(recipeService.update).toHaveBeenCalledWith(
          '123e4567-e89b-12d3-a456-426614174000',
          expect.objectContaining({
            name: 'Updated Recipe',
          })
        );
      });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/recipes/123e4567-e89b-12d3-a456-426614174000');
      });
    });

    it('should navigate to recipe detail on cancel in edit mode', async () => {
      const user = userEvent.setup();
      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Existing Recipe')).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: 'Cancel' }));

      expect(mockNavigate).toHaveBeenCalledWith('/recipes/123e4567-e89b-12d3-a456-426614174000');
    });

    it('should handle update error', async () => {
      const user = userEvent.setup();
      const error = new Error('Failed to update recipe');
      vi.mocked(recipeService.update).mockRejectedValue(error);

      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Existing Recipe')).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/Recipe Name/);
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Recipe');

      await user.click(screen.getByRole('button', { name: /Update Recipe/ }));

      await waitFor(() => {
        expect(recipeService.update).toHaveBeenCalled();
      });

      // Should not navigate on error
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Form Validation', () => {
    it('should validate servings minimum value', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const servingsInput = screen.getByLabelText('Servings');
      await user.type(servingsInput, '0');

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(screen.getByText('Servings must be at least 1')).toBeInTheDocument();
      });
    });

    it('should validate prep time minimum value', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const prepTimeInput = screen.getByLabelText(/Prep Time/);
      await user.type(prepTimeInput, '-5');

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(screen.getByText('Prep time must be 0 or greater')).toBeInTheDocument();
      });
    });

    it('should validate cook time minimum value', async () => {
      const user = userEvent.setup();
      renderCreateForm();

      const cookTimeInput = screen.getByLabelText(/Cook Time/);
      await user.type(cookTimeInput, '-10');

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(screen.getByText('Cook time must be 0 or greater')).toBeInTheDocument();
      });
    });

    it('should filter out empty ingredients on submit', async () => {
      const user = userEvent.setup();
      const newRecipe: Recipe = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Recipe',
        instructions: { steps: ['Step 1'] },
        difficulty: 'easy',
        diet_types: [],
        ingredients: [],
        categories: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(recipeService.create).mockResolvedValue(newRecipe);

      renderCreateForm();

      // Fill required fields
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test Recipe');
      const ingredientInputs = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientInputs[0], 'Real Ingredient');
      await user.type(await screen.findByPlaceholderText('Step 1...'), 'Step 1');

      // Add empty ingredient
      await user.click(screen.getByRole('button', { name: /Add Ingredient/ }));
      // Don't fill the second ingredient

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(recipeService.create).toHaveBeenCalledWith(
          expect.objectContaining({
            ingredients: [
              {
                name: 'Real Ingredient',
                quantity: undefined,
                unit: undefined,
                notes: undefined,
              },
            ],
          })
        );
      });
    });

    it('should filter out empty instruction steps on submit', async () => {
      const user = userEvent.setup();
      const newRecipe: Recipe = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Recipe',
        instructions: { steps: ['Real Step'] },
        difficulty: 'easy',
        diet_types: [],
        ingredients: [],
        categories: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(recipeService.create).mockResolvedValue(newRecipe);

      renderCreateForm();

      // Fill required fields
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test Recipe');
      const ingredientInputs = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientInputs[0], 'Ingredient');
      await user.type(await screen.findByPlaceholderText('Step 1...'), 'Real Step');

      // Add empty step
      await user.click(screen.getByRole('button', { name: /Add Step/ }));
      // Don't fill the second step

      await user.click(screen.getByRole('button', { name: /Create Recipe/ }));

      await waitFor(() => {
        expect(recipeService.create).toHaveBeenCalledWith(
          expect.objectContaining({
            instructions: {
              steps: ['Real Step'],
            },
          })
        );
      });
    });
  });

  describe('UI State Management', () => {
    it('should disable form during submission', async () => {
      const user = userEvent.setup();
      vi.mocked(recipeService.create).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderCreateForm();

      // Fill minimum required fields
      await user.type(screen.getByLabelText(/Recipe Name/), 'Test Recipe');
      const ingredientInputs = screen.getAllByPlaceholderText(/Ingredient name/);
      await user.type(ingredientInputs[0], 'Test');

      const stepInput = await screen.findByPlaceholderText('Step 1...');
      await user.type(stepInput, 'Step 1');

      const submitButton = screen.getByRole('button', { name: /Create Recipe/ });
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });

      await user.click(submitButton);

      // Buttons should be disabled
      await waitFor(() => {
        expect(submitButton).toBeDisabled();
        expect(cancelButton).toBeDisabled();
      });

      // Button text should change
      expect(screen.getByText('Creating...')).toBeInTheDocument();
    });

    it('should show "Updating..." text in edit mode during submission', async () => {
      const user = userEvent.setup();
      const mockRecipe: Recipe = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Test Recipe',
        instructions: { steps: ['Step 1'] },
        difficulty: 'easy',
        diet_types: [],
        ingredients: [
          {
            id: 'ing-1',
            recipe_id: '123e4567-e89b-12d3-a456-426614174000',
            name: 'Test',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ],
        categories: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      vi.mocked(recipeService.update).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderEditForm('123e4567-e89b-12d3-a456-426614174000', mockRecipe);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test Recipe')).toBeInTheDocument();
      });

      const submitButton = screen.getByRole('button', { name: /Update Recipe/ });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Updating...')).toBeInTheDocument();
      });
    });
  });
});
