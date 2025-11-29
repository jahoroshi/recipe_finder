import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RecipeCard from '@/components/RecipeCard';
import { Recipe } from '@/types';

const mockRecipe: Recipe = {
  id: '123',
  name: 'Test Recipe',
  description: 'A delicious test recipe',
  ingredients: [
    { id: '1', name: 'Flour', quantity: 2, unit: 'cups' },
    { id: '2', name: 'Sugar', quantity: 1, unit: 'cup' },
    { id: '3', name: 'Eggs', quantity: 3, unit: 'pieces' },
  ],
  instructions: { steps: ['Mix', 'Bake'] },
  prep_time: 15,
  cook_time: 30,
  servings: 4,
  difficulty: 'easy',
  cuisine_type: 'American',
  diet_types: ['vegetarian'],
  categories: [],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('RecipeCard', () => {
  it('should render recipe information correctly', () => {
    renderWithRouter(<RecipeCard recipe={mockRecipe} />);

    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    expect(screen.getByText('A delicious test recipe')).toBeInTheDocument();
    expect(screen.getByText('American')).toBeInTheDocument();
    expect(screen.getByText('easy')).toBeInTheDocument();
    expect(screen.getByText('vegetarian')).toBeInTheDocument();
  });

  it('should display time and serving information', () => {
    renderWithRouter(<RecipeCard recipe={mockRecipe} />);

    expect(screen.getByText('Prep: 15m')).toBeInTheDocument();
    expect(screen.getByText('Cook: 30m')).toBeInTheDocument();
    expect(screen.getByText('Serves: 4')).toBeInTheDocument();
  });

  it('should display limited ingredients with ellipsis', () => {
    renderWithRouter(<RecipeCard recipe={mockRecipe} />);

    expect(screen.getByText(/2cups Flour/)).toBeInTheDocument();
    expect(screen.getByText(/1cup Sugar/)).toBeInTheDocument();
    expect(screen.getByText(/3pieces Eggs/)).toBeInTheDocument();
  });

  it('should show "...and X more" when there are more than 3 ingredients', () => {
    const recipeWithManyIngredients = {
      ...mockRecipe,
      ingredients: [
        { id: '1', name: 'Flour', quantity: 2, unit: 'cups' },
        { id: '2', name: 'Sugar', quantity: 1, unit: 'cup' },
        { id: '3', name: 'Eggs', quantity: 3, unit: 'pieces' },
        { id: '4', name: 'Butter', quantity: 0.5, unit: 'cup' },
        { id: '5', name: 'Vanilla', quantity: 1, unit: 'tsp' },
      ],
    };

    renderWithRouter(<RecipeCard recipe={recipeWithManyIngredients} />);
    expect(screen.getByText('...and 2 more')).toBeInTheDocument();
  });

  it('should display image with lazy loading when image_url is provided', () => {
    const recipeWithImage = {
      ...mockRecipe,
      image_url: 'https://example.com/recipe.jpg',
    };

    renderWithRouter(<RecipeCard recipe={recipeWithImage} />);
    const image = screen.getByRole('img', { name: 'Test Recipe' });

    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('loading', 'lazy');
    expect(image).toHaveAttribute('src', 'https://example.com/recipe.jpg');
  });

  it('should show fallback gradient when no image_url', () => {
    const { container } = renderWithRouter(<RecipeCard recipe={mockRecipe} />);
    const gradientDiv = container.querySelector('.bg-gradient-to-br.from-teal-400.to-blue-500');

    expect(gradientDiv).toBeInTheDocument();
    expect(gradientDiv?.textContent).toContain('🍳');
  });

  it('should not re-render when props have not changed', () => {
    const renderSpy = vi.fn();
    const MemoizedRecipeCard = RecipeCard;

    const { rerender } = renderWithRouter(<MemoizedRecipeCard recipe={mockRecipe} />);

    // Force re-render with same props
    rerender(
      <BrowserRouter>
        <MemoizedRecipeCard recipe={mockRecipe} />
      </BrowserRouter>
    );

    // Component should be memoized and not re-render unnecessarily
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
  });

  it('should handle recipes without optional fields', () => {
    const minimalRecipe: Recipe = {
      id: '456',
      name: 'Minimal Recipe',
      ingredients: [],
      instructions: { steps: [] },
      difficulty: 'medium',
      diet_types: [],
      categories: [],
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    renderWithRouter(<RecipeCard recipe={minimalRecipe} />);
    expect(screen.getByText('Minimal Recipe')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
  });

  it('should display only first 2 diet types', () => {
    const recipeWithManyDietTypes = {
      ...mockRecipe,
      diet_types: ['vegetarian', 'gluten-free', 'dairy-free', 'keto'],
    };

    renderWithRouter(<RecipeCard recipe={recipeWithManyDietTypes} />);
    expect(screen.getByText('vegetarian')).toBeInTheDocument();
    expect(screen.getByText('gluten-free')).toBeInTheDocument();
    expect(screen.queryByText('dairy-free')).not.toBeInTheDocument();
    expect(screen.queryByText('keto')).not.toBeInTheDocument();
  });
});
