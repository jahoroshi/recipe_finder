import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import RecipeCardSkeleton, { RecipeCardSkeletonGrid } from '@/components/RecipeCardSkeleton';

describe('RecipeCardSkeleton Component', () => {
  it('should render skeleton loader with animation', () => {
    const { container } = render(<RecipeCardSkeleton />);

    const skeleton = container.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('should have proper structure matching RecipeCard', () => {
    const { container } = render(<RecipeCardSkeleton />);

    // Check for image placeholder
    expect(container.querySelector('.h-48')).toBeInTheDocument();

    // Check for content area
    expect(container.querySelector('.p-6')).toBeInTheDocument();
  });
});

describe('RecipeCardSkeletonGrid Component', () => {
  it('should render default number of skeletons (20)', () => {
    const { container } = render(<RecipeCardSkeletonGrid />);

    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(20);
  });

  it('should render custom number of skeletons', () => {
    const { container } = render(<RecipeCardSkeletonGrid count={5} />);

    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(5);
  });

  it('should use grid layout', () => {
    const { container } = render(<RecipeCardSkeletonGrid count={3} />);

    const grid = container.querySelector('.grid');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('grid-cols-1');
    expect(grid).toHaveClass('sm:grid-cols-2');
    expect(grid).toHaveClass('lg:grid-cols-3');
  });
});
