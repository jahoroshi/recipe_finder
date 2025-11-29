import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import EmptyState, {
  NoRecipesFound,
  NoSearchResults,
  EmptyRecipeList,
} from '@/components/EmptyState';

describe('EmptyState', () => {
  describe('Basic Rendering', () => {
    it('should render title and message', () => {
      render(<EmptyState title="No Results" message="Try adjusting your filters" />);

      expect(screen.getByText('No Results')).toBeInTheDocument();
      expect(screen.getByText('Try adjusting your filters')).toBeInTheDocument();
    });

    it('should render with default search icon', () => {
      const { container } = render(
        <EmptyState title="Empty" message="No data available" />
      );

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveClass('w-16', 'h-16', 'text-gray-400');
    });
  });

  describe('Icons', () => {
    it('should render search icon when specified', () => {
      const { container } = render(
        <EmptyState title="No Results" message="Search again" icon="search" />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('should render recipe icon when specified', () => {
      const { container } = render(
        <EmptyState title="No Recipes" message="Create one" icon="recipe" />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('should render filter icon when specified', () => {
      const { container } = render(
        <EmptyState title="No Matches" message="Clear filters" icon="filter" />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });

    it('should render error icon when specified', () => {
      const { container } = render(
        <EmptyState title="Error" message="Something went wrong" icon="error" />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    it('should render primary action button when provided', () => {
      const onAction = vi.fn();

      render(
        <EmptyState
          title="No Data"
          message="Get started"
          actionLabel="Create New"
          onAction={onAction}
        />
      );

      const button = screen.getByRole('button', { name: /create new/i });
      expect(button).toBeInTheDocument();
    });

    it('should call onAction when primary button is clicked', async () => {
      const user = userEvent.setup();
      const onAction = vi.fn();

      render(
        <EmptyState
          title="No Data"
          message="Get started"
          actionLabel="Create New"
          onAction={onAction}
        />
      );

      const button = screen.getByRole('button', { name: /create new/i });
      await user.click(button);

      expect(onAction).toHaveBeenCalledTimes(1);
    });

    it('should render secondary action button when provided', () => {
      const onSecondaryAction = vi.fn();

      render(
        <EmptyState
          title="No Data"
          message="Get started"
          secondaryActionLabel="Go Back"
          onSecondaryAction={onSecondaryAction}
        />
      );

      const button = screen.getByRole('button', { name: /go back/i });
      expect(button).toBeInTheDocument();
    });

    it('should call onSecondaryAction when secondary button is clicked', async () => {
      const user = userEvent.setup();
      const onSecondaryAction = vi.fn();

      render(
        <EmptyState
          title="No Data"
          message="Get started"
          secondaryActionLabel="Go Back"
          onSecondaryAction={onSecondaryAction}
        />
      );

      const button = screen.getByRole('button', { name: /go back/i });
      await user.click(button);

      expect(onSecondaryAction).toHaveBeenCalledTimes(1);
    });

    it('should render both action buttons when both are provided', () => {
      render(
        <EmptyState
          title="No Data"
          message="Get started"
          actionLabel="Primary"
          onAction={vi.fn()}
          secondaryActionLabel="Secondary"
          onSecondaryAction={vi.fn()}
        />
      );

      expect(screen.getByRole('button', { name: /primary/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /secondary/i })).toBeInTheDocument();
    });

    it('should not render action button when only label is provided without handler', () => {
      render(<EmptyState title="No Data" message="Get started" actionLabel="Create" />);

      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });

    it('should not render action button when only handler is provided without label', () => {
      render(<EmptyState title="No Data" message="Get started" onAction={vi.fn()} />);

      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should have proper text alignment and spacing', () => {
      const { container } = render(
        <EmptyState title="No Data" message="No content" />
      );

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('text-center', 'py-16', 'px-4');
    });

    it('should style title correctly', () => {
      render(<EmptyState title="No Results" message="Try again" />);

      const title = screen.getByText('No Results');
      expect(title).toHaveClass('text-2xl', 'font-bold', 'text-gray-900', 'mb-3');
    });

    it('should style message correctly', () => {
      render(<EmptyState title="Title" message="Message text" />);

      const message = screen.getByText('Message text');
      expect(message).toHaveClass('text-gray-600', 'mb-8', 'max-w-md', 'mx-auto', 'text-lg');
    });
  });
});

describe('NoRecipesFound', () => {
  it('should render with appropriate title and message', () => {
    render(<NoRecipesFound />);

    expect(screen.getByText('No recipes found')).toBeInTheDocument();
    expect(
      screen.getByText(/We couldn't find any recipes matching your criteria/)
    ).toBeInTheDocument();
  });

  it('should render clear filters button when handler provided', () => {
    const onClearFilters = vi.fn();
    render(<NoRecipesFound onClearFilters={onClearFilters} />);

    expect(screen.getByRole('button', { name: /clear filters/i })).toBeInTheDocument();
  });

  it('should render create recipe button when handler provided', () => {
    const onCreateRecipe = vi.fn();
    render(<NoRecipesFound onCreateRecipe={onCreateRecipe} />);

    expect(screen.getByRole('button', { name: /create recipe/i })).toBeInTheDocument();
  });

  it('should call handlers when buttons are clicked', async () => {
    const user = userEvent.setup();
    const onClearFilters = vi.fn();
    const onCreateRecipe = vi.fn();

    render(
      <NoRecipesFound onClearFilters={onClearFilters} onCreateRecipe={onCreateRecipe} />
    );

    await user.click(screen.getByRole('button', { name: /clear filters/i }));
    expect(onClearFilters).toHaveBeenCalledTimes(1);

    await user.click(screen.getByRole('button', { name: /create recipe/i }));
    expect(onCreateRecipe).toHaveBeenCalledTimes(1);
  });

  it('should use recipe icon', () => {
    const { container } = render(<NoRecipesFound />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
});

describe('NoSearchResults', () => {
  it('should render with appropriate title', () => {
    render(<NoSearchResults />);

    expect(screen.getByText('No results found')).toBeInTheDocument();
  });

  it('should display query in message when provided', () => {
    render(<NoSearchResults query="pasta" />);

    expect(
      screen.getByText(/We couldn't find any recipes matching "pasta"/)
    ).toBeInTheDocument();
  });

  it('should display generic message when no query provided', () => {
    render(<NoSearchResults />);

    expect(
      screen.getByText(/We couldn't find any results. Try a different search term./)
    ).toBeInTheDocument();
  });

  it('should render clear search button when handler provided', () => {
    const onClearSearch = vi.fn();
    render(<NoSearchResults onClearSearch={onClearSearch} />);

    expect(screen.getByRole('button', { name: /clear search/i })).toBeInTheDocument();
  });

  it('should call handler when clear search is clicked', async () => {
    const user = userEvent.setup();
    const onClearSearch = vi.fn();

    render(<NoSearchResults onClearSearch={onClearSearch} />);

    await user.click(screen.getByRole('button', { name: /clear search/i }));
    expect(onClearSearch).toHaveBeenCalledTimes(1);
  });

  it('should use search icon', () => {
    const { container } = render(<NoSearchResults />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
});

describe('EmptyRecipeList', () => {
  it('should render with appropriate title and message', () => {
    render(<EmptyRecipeList />);

    expect(screen.getByText('No recipes yet')).toBeInTheDocument();
    expect(
      screen.getByText(/Get started by creating your first recipe/)
    ).toBeInTheDocument();
  });

  it('should render create recipe button when handler provided', () => {
    const onCreateRecipe = vi.fn();
    render(<EmptyRecipeList onCreateRecipe={onCreateRecipe} />);

    expect(
      screen.getByRole('button', { name: /create your first recipe/i })
    ).toBeInTheDocument();
  });

  it('should call handler when create recipe is clicked', async () => {
    const user = userEvent.setup();
    const onCreateRecipe = vi.fn();

    render(<EmptyRecipeList onCreateRecipe={onCreateRecipe} />);

    await user.click(screen.getByRole('button', { name: /create your first recipe/i }));
    expect(onCreateRecipe).toHaveBeenCalledTimes(1);
  });

  it('should use recipe icon', () => {
    const { container } = render(<EmptyRecipeList />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('should not render button when no handler provided', () => {
    render(<EmptyRecipeList />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});

describe('Icon Rendering', () => {
  it('should render all icon types without errors', () => {
    const { rerender, container } = render(
      <EmptyState title="Test" message="Test" icon="search" />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();

    rerender(<EmptyState title="Test" message="Test" icon="recipe" />);
    expect(container.querySelector('svg')).toBeInTheDocument();

    rerender(<EmptyState title="Test" message="Test" icon="filter" />);
    expect(container.querySelector('svg')).toBeInTheDocument();

    rerender(<EmptyState title="Test" message="Test" icon="error" />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});
