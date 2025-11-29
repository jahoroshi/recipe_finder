import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner, {
  InlineSpinner,
  FullPageSpinner,
  ButtonSpinner,
} from '@/components/LoadingSpinner';

describe('LoadingSpinner', () => {
  describe('Basic Rendering', () => {
    it('should render spinner with default props', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveAttribute('aria-label', 'Loading');
    });

    it('should apply correct size classes for sm size', () => {
      const { container } = render(<LoadingSpinner size="sm" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('h-4', 'w-4', 'border-2');
    });

    it('should apply correct size classes for md size', () => {
      const { container } = render(<LoadingSpinner size="md" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('h-8', 'w-8', 'border-2');
    });

    it('should apply correct size classes for lg size', () => {
      const { container } = render(<LoadingSpinner size="lg" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('h-12', 'w-12', 'border-3');
    });

    it('should apply correct size classes for xl size', () => {
      const { container } = render(<LoadingSpinner size="xl" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('h-16', 'w-16', 'border-4');
    });
  });

  describe('Color Variants', () => {
    it('should apply teal color class', () => {
      const { container } = render(<LoadingSpinner color="teal" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('border-teal-500');
    });

    it('should apply gray color class', () => {
      const { container } = render(<LoadingSpinner color="gray" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('border-gray-500');
    });

    it('should apply white color class', () => {
      const { container } = render(<LoadingSpinner color="white" />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('border-white');
    });
  });

  describe('Loading Message', () => {
    it('should display loading message when provided', () => {
      render(<LoadingSpinner message="Loading recipes..." />);

      expect(screen.getByText('Loading recipes...')).toBeInTheDocument();
    });

    it('should not display message when not provided', () => {
      const { container } = render(<LoadingSpinner />);

      const message = container.querySelector('p');
      expect(message).not.toBeInTheDocument();
    });

    it('should apply animation to loading message', () => {
      render(<LoadingSpinner message="Loading..." />);

      const message = screen.getByText('Loading...');
      expect(message).toHaveClass('animate-pulse');
    });
  });

  describe('Full Screen Mode', () => {
    it('should render in full screen mode when enabled', () => {
      const { container } = render(<LoadingSpinner fullScreen />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass('min-h-screen', 'bg-gray-50');
    });

    it('should not render in full screen mode by default', () => {
      const { container } = render(<LoadingSpinner />);

      const wrapper = container.firstChild;
      expect(wrapper).not.toHaveClass('min-h-screen');
    });
  });

  describe('Animation', () => {
    it('should have spin animation class', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('animate-spin');
    });

    it('should have rounded-full class for circular shape', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('rounded-full');
    });

    it('should have border-t-transparent for spinner effect', () => {
      const { container } = render(<LoadingSpinner />);

      const spinner = container.querySelector('[role="status"]');
      expect(spinner).toHaveClass('border-t-transparent');
    });
  });
});

describe('InlineSpinner', () => {
  it('should render inline spinner', () => {
    const { container } = render(<InlineSpinner />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('inline-block');
  });

  it('should have small size for inline use', () => {
    const { container } = render(<InlineSpinner />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toHaveClass('h-4', 'w-4');
  });

  it('should apply custom className', () => {
    const { container } = render(<InlineSpinner className="custom-class" />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toHaveClass('custom-class');
  });

  it('should have white border by default', () => {
    const { container } = render(<InlineSpinner />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toHaveClass('border-white');
  });
});

describe('FullPageSpinner', () => {
  it('should render full page spinner', () => {
    const { container } = render(<FullPageSpinner />);

    expect(container.firstChild).toHaveClass('min-h-screen');
  });

  it('should have large size', () => {
    const { container } = render(<FullPageSpinner />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toHaveClass('h-12', 'w-12');
  });

  it('should display message when provided', () => {
    render(<FullPageSpinner message="Loading application..." />);

    expect(screen.getByText('Loading application...')).toBeInTheDocument();
  });

  it('should render in full screen by default', () => {
    const { container } = render(<FullPageSpinner />);

    expect(container.firstChild).toHaveClass('min-h-screen', 'bg-gray-50');
  });
});

describe('ButtonSpinner', () => {
  it('should render button spinner with text', () => {
    render(<ButtonSpinner />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should have inline flex layout', () => {
    const { container } = render(<ButtonSpinner />);

    const wrapper = container.querySelector('.inline-flex');
    expect(wrapper).toBeInTheDocument();
    expect(wrapper).toHaveClass('items-center', 'gap-2');
  });

  it('should contain inline spinner', () => {
    const { container } = render(<ButtonSpinner />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('inline-block');
  });
});

describe('Accessibility', () => {
  it('should have proper ARIA labels for all spinner variants', () => {
    const { container: container1 } = render(<LoadingSpinner />);
    const { container: container2 } = render(<InlineSpinner />);
    const { container: container3 } = render(<FullPageSpinner />);
    const { container: container4 } = render(<ButtonSpinner />);

    const spinner1 = container1.querySelector('[role="status"]');
    const spinner2 = container2.querySelector('[role="status"]');
    const spinner3 = container3.querySelector('[role="status"]');
    const spinner4 = container4.querySelector('[role="status"]');

    expect(spinner1).toHaveAttribute('aria-label', 'Loading');
    expect(spinner2).toHaveAttribute('aria-label', 'Loading');
    expect(spinner3).toHaveAttribute('aria-label', 'Loading');
    expect(spinner4).toHaveAttribute('aria-label', 'Loading');
  });

  it('should have role="status" for screen readers', () => {
    const { container } = render(<LoadingSpinner />);

    const spinner = container.querySelector('[role="status"]');
    expect(spinner).toBeInTheDocument();
  });
});
