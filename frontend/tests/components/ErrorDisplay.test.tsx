import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorDisplay from '@/components/ErrorDisplay';

describe('ErrorDisplay Component', () => {
  it('should render default title', () => {
    render(<ErrorDisplay message="Test error message" />);

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
  });

  it('should render custom title', () => {
    render(<ErrorDisplay title="Custom Error" message="Test error message" />);

    expect(screen.getByText('Custom Error')).toBeInTheDocument();
  });

  it('should render error message', () => {
    render(<ErrorDisplay message="Test error message" />);

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('should render retry button when onRetry provided', () => {
    const mockRetry = vi.fn();
    render(<ErrorDisplay message="Test error message" onRetry={mockRetry} />);

    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('should not render retry button when onRetry not provided', () => {
    render(<ErrorDisplay message="Test error message" />);

    expect(screen.queryByText('Try Again')).not.toBeInTheDocument();
  });

  it('should call onRetry when retry button clicked', () => {
    const mockRetry = vi.fn();
    render(<ErrorDisplay message="Test error message" onRetry={mockRetry} />);

    const retryButton = screen.getByText('Try Again');
    fireEvent.click(retryButton);

    expect(mockRetry).toHaveBeenCalledTimes(1);
  });

  it('should render error icon', () => {
    const { container } = render(<ErrorDisplay message="Test error message" />);

    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });
});
