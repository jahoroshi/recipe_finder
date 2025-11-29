import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ActiveFilterBadges from '@/components/ActiveFilterBadges';
import { FilterState } from '@/components/FilterPanel';

describe('ActiveFilterBadges', () => {
  const mockOnRemoveFilter = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders nothing when no filters are active', () => {
    const filters: FilterState = {
      diet_types: [],
    };

    const { container } = render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('renders cuisine type badge', () => {
    const filters: FilterState = {
      cuisine_type: 'Italian',
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Cuisine: Italian')).toBeInTheDocument();
  });

  it('renders difficulty badge with capitalization', () => {
    const filters: FilterState = {
      difficulty: 'easy',
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Difficulty: Easy')).toBeInTheDocument();
  });

  it('renders multiple diet type badges', () => {
    const filters: FilterState = {
      diet_types: ['Vegetarian', 'Vegan', 'Gluten-Free'],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Diet: Vegetarian')).toBeInTheDocument();
    expect(screen.getByText('Diet: Vegan')).toBeInTheDocument();
    expect(screen.getByText('Diet: Gluten-Free')).toBeInTheDocument();
  });

  it('renders prep time range badge', () => {
    const filters: FilterState = {
      min_prep_time: 10,
      max_prep_time: 30,
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Prep Time: 10-30 min')).toBeInTheDocument();
  });

  it('renders prep time badge with only min value', () => {
    const filters: FilterState = {
      min_prep_time: 15,
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Prep Time: 15-∞ min')).toBeInTheDocument();
  });

  it('renders prep time badge with only max value', () => {
    const filters: FilterState = {
      max_prep_time: 45,
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Prep Time: 0-45 min')).toBeInTheDocument();
  });

  it('renders cook time range badge', () => {
    const filters: FilterState = {
      min_cook_time: 20,
      max_cook_time: 60,
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Cook Time: 20-60 min')).toBeInTheDocument();
  });

  it('renders servings range badge', () => {
    const filters: FilterState = {
      min_servings: 2,
      max_servings: 6,
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Servings: 2-6')).toBeInTheDocument();
  });

  it('calls onRemoveFilter when cuisine badge is removed', () => {
    const filters: FilterState = {
      cuisine_type: 'Italian',
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    const removeButton = screen.getByLabelText('Remove Cuisine: Italian filter');
    fireEvent.click(removeButton);

    expect(mockOnRemoveFilter).toHaveBeenCalledWith('cuisine_type', undefined);
  });

  it('calls onRemoveFilter when difficulty badge is removed', () => {
    const filters: FilterState = {
      difficulty: 'medium',
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    const removeButton = screen.getByLabelText('Remove Difficulty: Medium filter');
    fireEvent.click(removeButton);

    expect(mockOnRemoveFilter).toHaveBeenCalledWith('difficulty', undefined);
  });

  it('calls onRemoveFilter with diet type value when diet badge is removed', () => {
    const filters: FilterState = {
      diet_types: ['Vegetarian', 'Vegan'],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    const removeButton = screen.getByLabelText('Remove Diet: Vegetarian filter');
    fireEvent.click(removeButton);

    expect(mockOnRemoveFilter).toHaveBeenCalledWith('diet_types', 'Vegetarian');
  });

  it('calls onRemoveFilter when prep time badge is removed', () => {
    const filters: FilterState = {
      min_prep_time: 10,
      max_prep_time: 30,
      diet_types: [],
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    const removeButton = screen.getByLabelText('Remove Prep Time: 10-30 min filter');
    fireEvent.click(removeButton);

    expect(mockOnRemoveFilter).toHaveBeenCalledWith('min_prep_time', undefined);
  });

  it('renders all badge types together', () => {
    const filters: FilterState = {
      cuisine_type: 'Mexican',
      difficulty: 'hard',
      diet_types: ['Vegan'],
      min_prep_time: 15,
      max_cook_time: 45,
      min_servings: 4,
    };

    render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
      />
    );

    expect(screen.getByText('Cuisine: Mexican')).toBeInTheDocument();
    expect(screen.getByText('Difficulty: Hard')).toBeInTheDocument();
    expect(screen.getByText('Diet: Vegan')).toBeInTheDocument();
    expect(screen.getByText('Prep Time: 15-∞ min')).toBeInTheDocument();
    expect(screen.getByText('Cook Time: 0-45 min')).toBeInTheDocument();
    expect(screen.getByText('Servings: 4-∞')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const filters: FilterState = {
      cuisine_type: 'Thai',
      diet_types: [],
    };

    const { container } = render(
      <ActiveFilterBadges
        filters={filters}
        onRemoveFilter={mockOnRemoveFilter}
        className="custom-class"
      />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });
});
