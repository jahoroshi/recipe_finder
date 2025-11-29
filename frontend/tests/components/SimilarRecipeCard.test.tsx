import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SimilarRecipeCard from '@/components/SimilarRecipeCard';
import type { SearchResult, Recipe } from '@/types';

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const createMockRecipe = (overrides?: Partial<Recipe>): Recipe => ({
  id: 'recipe-123',
  name: 'Test Recipe',
  description: 'A delicious test recipe',
  instructions: { steps: ['Step 1', 'Step 2'] },
  prep_time: 15,
  cook_time: 30,
  servings: 4,
  difficulty: 'medium',
  cuisine_type: 'Italian',
  diet_types: ['vegetarian'],
  ingredients: [],
  categories: [],
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  ...overrides,
});

const createMockSearchResult = (score: number, recipe?: Partial<Recipe>): SearchResult => ({
  recipe: createMockRecipe(recipe),
  score,
  match_type: 'semantic',
});

describe('SimilarRecipeCard', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders recipe information correctly', () => {
    const result = createMockSearchResult(0.85);

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
    expect(screen.getByText('A delicious test recipe')).toBeInTheDocument();
    expect(screen.getByText('Italian')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
  });

  it('displays similarity score correctly', () => {
    const result = createMockSearchResult(0.92);

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.getByText('92% similar')).toBeInTheDocument();
  });

  it('rounds similarity percentage correctly', () => {
    const result = createMockSearchResult(0.8567);

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.getByText('86% similar')).toBeInTheDocument();
  });

  it('applies correct badge color for excellent match (90-100%)', () => {
    const result = createMockSearchResult(0.95);

    const { container } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    const badge = screen.getByText('95% similar');
    expect(badge).toHaveClass('bg-green-100', 'text-green-800');
  });

  it('applies correct badge color for good match (75-89%)', () => {
    const result = createMockSearchResult(0.82);

    const { container } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    const badge = screen.getByText('82% similar');
    expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('applies correct badge color for fair match (60-74%)', () => {
    const result = createMockSearchResult(0.68);

    const { container } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    const badge = screen.getByText('68% similar');
    expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800');
  });

  it('applies correct badge color for weak match (<60%)', () => {
    const result = createMockSearchResult(0.45);

    const { container } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    const badge = screen.getByText('45% similar');
    expect(badge).toHaveClass('bg-gray-100', 'text-gray-800');
  });

  it('displays prep time when available', () => {
    const result = createMockSearchResult(0.85, { prep_time: 20 });

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.getByText('20m prep')).toBeInTheDocument();
  });

  it('displays servings when available', () => {
    const result = createMockSearchResult(0.85, { servings: 6 });

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.getByText('6 servings')).toBeInTheDocument();
  });

  it('does not render cuisine badge when not available', () => {
    const result = createMockSearchResult(0.85, { cuisine_type: undefined });

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.queryByText('Italian')).not.toBeInTheDocument();
  });

  it('does not render description when not available', () => {
    const result = createMockSearchResult(0.85, { description: undefined });

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    expect(screen.queryByText(/delicious/)).not.toBeInTheDocument();
  });

  it('navigates to recipe detail on click', () => {
    const result = createMockSearchResult(0.85);

    render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    const card = screen.getByText('Test Recipe').closest('div');
    fireEvent.click(card!);

    expect(mockNavigate).toHaveBeenCalledWith('/recipes/recipe-123');
  });

  it('applies difficulty-based text color', () => {
    const easyResult = createMockSearchResult(0.85, { difficulty: 'easy' });

    const { rerender } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={easyResult} />
      </BrowserRouter>
    );

    const easyDifficulty = screen.getByText('easy');
    expect(easyDifficulty).toHaveClass('text-green-600');

    const mediumResult = createMockSearchResult(0.85, { difficulty: 'medium' });
    rerender(
      <BrowserRouter>
        <SimilarRecipeCard result={mediumResult} />
      </BrowserRouter>
    );

    const mediumDifficulty = screen.getByText('medium');
    expect(mediumDifficulty).toHaveClass('text-yellow-600');

    const hardResult = createMockSearchResult(0.85, { difficulty: 'hard' });
    rerender(
      <BrowserRouter>
        <SimilarRecipeCard result={hardResult} />
      </BrowserRouter>
    );

    const hardDifficulty = screen.getByText('hard');
    expect(hardDifficulty).toHaveClass('text-red-600');
  });

  it('has fixed width for carousel layout', () => {
    const result = createMockSearchResult(0.85);

    const { container } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    const card = container.querySelector('[style*="width"]');
    expect(card).toHaveStyle({ width: '280px' });
  });

  it('displays hover shadow effect class', () => {
    const result = createMockSearchResult(0.85);

    const { container } = render(
      <BrowserRouter>
        <SimilarRecipeCard result={result} />
      </BrowserRouter>
    );

    // Find the outermost card container
    const card = container.querySelector('.bg-white.rounded-lg.shadow-md');
    expect(card).toHaveClass('hover:shadow-lg');
  });
});
