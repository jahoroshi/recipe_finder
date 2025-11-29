import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import FilterPanel, { FilterState } from '@/components/FilterPanel';

describe('FilterPanel', () => {
  const mockOnFiltersChange = vi.fn();

  const defaultFilters: FilterState = {
    diet_types: [],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all filter sections', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    expect(screen.getByText('Cuisine Type')).toBeInTheDocument();
    expect(screen.getByText('Difficulty')).toBeInTheDocument();
    expect(screen.getByText('Diet Types')).toBeInTheDocument();
    expect(screen.getByText('Prep Time (minutes)')).toBeInTheDocument();
    expect(screen.getByText('Cook Time (minutes)')).toBeInTheDocument();
    expect(screen.getByText('Servings')).toBeInTheDocument();
  });

  it('displays filter count badge when filters are active', () => {
    const filtersWithValues: FilterState = {
      cuisine_type: 'Italian',
      difficulty: 'easy',
      diet_types: ['Vegetarian'],
    };

    render(
      <FilterPanel
        filters={filtersWithValues}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    // Filter count should be 3 (cuisine, difficulty, diet types)
    // Two badges exist: one for mobile, one for desktop
    const badges = screen.getAllByText('3');
    expect(badges.length).toBeGreaterThanOrEqual(1);
  });

  it('handles cuisine type selection', async () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const cuisineLabel = screen.getByText('Cuisine Type');
    const cuisineSelect = cuisineLabel.parentElement!.querySelector('select')!;
    fireEvent.change(cuisineSelect, { target: { value: 'Italian' } });

    await waitFor(
      () => {
        expect(mockOnFiltersChange).toHaveBeenCalledWith(
          expect.objectContaining({ cuisine_type: 'Italian' })
        );
      },
      { timeout: 600 }
    );
  });

  it('handles difficulty radio button selection', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const easyRadio = screen.getByLabelText('Easy');
    fireEvent.click(easyRadio);

    // Should trigger immediate update (no debounce for radio buttons)
    expect(mockOnFiltersChange).toHaveBeenCalledWith(
      expect.objectContaining({ difficulty: 'easy' })
    );
  });

  it('handles diet type checkbox toggling (immediate update)', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const vegetarianCheckbox = screen.getByLabelText('Vegetarian');
    fireEvent.click(vegetarianCheckbox);

    // Diet types should update immediately (no debounce)
    expect(mockOnFiltersChange).toHaveBeenCalledWith(
      expect.objectContaining({ diet_types: ['Vegetarian'] })
    );
  });

  it('handles multiple diet type selections', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const vegetarianCheckbox = screen.getByLabelText('Vegetarian');
    const veganCheckbox = screen.getByLabelText('Vegan');

    fireEvent.click(vegetarianCheckbox);
    fireEvent.click(veganCheckbox);

    // Should have both diet types
    expect(mockOnFiltersChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ diet_types: expect.arrayContaining(['Vegetarian', 'Vegan']) })
    );
  });

  it('handles diet type deselection', () => {
    const filtersWithDietType: FilterState = {
      diet_types: ['Vegetarian'],
    };

    render(
      <FilterPanel
        filters={filtersWithDietType}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const vegetarianCheckbox = screen.getByLabelText('Vegetarian');
    fireEvent.click(vegetarianCheckbox);

    expect(mockOnFiltersChange).toHaveBeenCalledWith(
      expect.objectContaining({ diet_types: [] })
    );
  });

  it('handles prep time range inputs with debouncing', async () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const prepTimeInputs = screen.getAllByPlaceholderText(/min|max/i);
    const minPrepTime = prepTimeInputs[0]; // First "Min" placeholder

    fireEvent.change(minPrepTime, { target: { value: '10' } });

    // Should debounce (500ms)
    await waitFor(
      () => {
        expect(mockOnFiltersChange).toHaveBeenCalledWith(
          expect.objectContaining({ min_prep_time: 10 })
        );
      },
      { timeout: 600 }
    );
  });

  it('handles cook time range inputs', async () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const cookTimeSection = screen.getByText('Cook Time (minutes)').parentElement;
    const cookTimeInputs = cookTimeSection!.querySelectorAll('input[type="number"]');
    const maxCookTime = cookTimeInputs[1];

    fireEvent.change(maxCookTime, { target: { value: '60' } });

    await waitFor(
      () => {
        expect(mockOnFiltersChange).toHaveBeenCalledWith(
          expect.objectContaining({ max_cook_time: 60 })
        );
      },
      { timeout: 600 }
    );
  });

  it('handles servings range inputs', async () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const servingsSection = screen.getByText('Servings').parentElement;
    const servingsInputs = servingsSection!.querySelectorAll('input[type="number"]');
    const minServings = servingsInputs[0];

    fireEvent.change(minServings, { target: { value: '2' } });

    await waitFor(
      () => {
        expect(mockOnFiltersChange).toHaveBeenCalledWith(
          expect.objectContaining({ min_servings: 2 })
        );
      },
      { timeout: 600 }
    );
  });

  it('clears all filters when Clear All is clicked', () => {
    const filtersWithValues: FilterState = {
      cuisine_type: 'Italian',
      difficulty: 'medium',
      diet_types: ['Vegetarian', 'Vegan'],
      min_prep_time: 10,
      max_prep_time: 30,
    };

    render(
      <FilterPanel
        filters={filtersWithValues}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const clearAllButton = screen.getByText('Clear All');
    fireEvent.click(clearAllButton);

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      diet_types: [],
    });
  });

  it('handles empty string inputs by setting undefined', async () => {
    const filtersWithValues: FilterState = {
      min_prep_time: 10,
      diet_types: [],
    };

    render(
      <FilterPanel
        filters={filtersWithValues}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const prepTimeInputs = screen.getAllByPlaceholderText(/min|max/i);
    const minPrepTime = prepTimeInputs[0];

    // Clear the input
    fireEvent.change(minPrepTime, { target: { value: '' } });

    await waitFor(
      () => {
        expect(mockOnFiltersChange).toHaveBeenCalledWith(
          expect.objectContaining({ min_prep_time: undefined })
        );
      },
      { timeout: 600 }
    );
  });

  it('displays all cuisine options', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    const cuisineLabel = screen.getByText('Cuisine Type');
    const cuisineSelect = cuisineLabel.parentElement!.querySelector('select')!;
    const options = cuisineSelect.querySelectorAll('option');

    // Should have "Any Cuisine" + 12 cuisine types
    expect(options.length).toBe(13);
    expect(options[0].textContent).toBe('Any Cuisine');
    expect(options[1].textContent).toBe('Italian');
  });

  it('displays all diet type checkboxes', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
      />
    );

    expect(screen.getByLabelText('Vegetarian')).toBeInTheDocument();
    expect(screen.getByLabelText('Vegan')).toBeInTheDocument();
    expect(screen.getByLabelText('Gluten-Free')).toBeInTheDocument();
    expect(screen.getByLabelText('Dairy-Free')).toBeInTheDocument();
    expect(screen.getByLabelText('Keto')).toBeInTheDocument();
    expect(screen.getByLabelText('Paleo')).toBeInTheDocument();
  });

  it('renders collapsed on mobile when isCollapsed is true', () => {
    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
        isCollapsed={true}
        onToggleCollapse={vi.fn()}
      />
    );

    // Filter controls should be hidden on mobile with class "hidden lg:block"
    const cuisineTypeLabel = screen.getByText('Cuisine Type');
    const filterContainer = cuisineTypeLabel.closest('.p-4')?.parentElement;
    expect(filterContainer).toHaveClass('hidden');
    expect(filterContainer).toHaveClass('lg:block');
  });

  it('calls onToggleCollapse when collapse button is clicked', () => {
    const mockToggle = vi.fn();

    render(
      <FilterPanel
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
        isCollapsed={false}
        onToggleCollapse={mockToggle}
      />
    );

    const collapseButton = screen.getByLabelText(/collapse filters/i);
    fireEvent.click(collapseButton);

    expect(mockToggle).toHaveBeenCalled();
  });
});
