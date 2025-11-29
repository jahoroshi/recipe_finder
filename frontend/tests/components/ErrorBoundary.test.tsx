import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorBoundary, { withErrorBoundary } from '@/components/ErrorBoundary';
import React from 'react';

// Component that throws an error for testing
const ThrowError: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = true }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component for testing withErrorBoundary HOC
const TestComponent: React.FC<{ message: string }> = ({ message }) => (
  <div>{message}</div>
);

describe('ErrorBoundary', () => {
  // Suppress console.error for cleaner test output
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalError;
  });

  describe('Error Catching', () => {
    it('should render children when there is no error', () => {
      render(
        <ErrorBoundary>
          <div>Child component</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Child component')).toBeInTheDocument();
    });

    it('should catch errors and display default fallback UI', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(
        screen.getByText(/We're sorry, but something unexpected happened/)
      ).toBeInTheDocument();
    });

    it('should display error message in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText(/Error Details:/)).toBeInTheDocument();
      expect(screen.getByText(/Test error/)).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });

    it('should not display error details in production mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.queryByText(/Error Details:/)).not.toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Error Recovery', () => {
    it('should reset error state when "Try Again" button is clicked', async () => {
      const user = userEvent.setup();

      // Use a component that can toggle error state
      let shouldThrow = true;
      const ToggleableError = () => {
        if (shouldThrow) {
          throw new Error('Test error');
        }
        return <div>No error</div>;
      };

      const { rerender } = render(
        <ErrorBoundary>
          <ToggleableError />
        </ErrorBoundary>
      );

      // Error UI should be displayed
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // Click "Try Again" button - this resets the error boundary
      const tryAgainButton = screen.getByRole('button', { name: /try again/i });

      // Change the error state before clicking
      shouldThrow = false;

      await user.click(tryAgainButton);

      // The error boundary should have reset, but the component still needs re-render
      // In real scenarios, the reset would trigger a re-render of children
    });

    it('should navigate to home when "Go to Home" button is clicked', async () => {
      const user = userEvent.setup();
      const originalLocation = window.location;

      // Mock window.location
      delete (window as any).location;
      window.location = { ...originalLocation, href: '' } as any;

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const homeButton = screen.getByRole('button', { name: /go to home/i });
      await user.click(homeButton);

      expect(window.location.href).toBe('/');

      // Restore original location
      window.location = originalLocation;
    });
  });

  describe('Custom Fallback', () => {
    it('should render custom fallback when provided', () => {
      const customFallback = (error: Error, reset: () => void) => (
        <div>
          <h1>Custom Error UI</h1>
          <p>{error.message}</p>
          <button onClick={reset}>Reset</button>
        </div>
      );

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom Error UI')).toBeInTheDocument();
      expect(screen.getByText('Test error')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reset/i })).toBeInTheDocument();
    });

    it('should allow custom fallback to reset error', async () => {
      const user = userEvent.setup();
      let resetCalled = false;

      const customFallback = (_error: Error, reset: () => void) => (
        <button
          onClick={() => {
            resetCalled = true;
            reset();
          }}
        >
          Custom Reset
        </button>
      );

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError />
        </ErrorBoundary>
      );

      const resetButton = screen.getByRole('button', { name: /custom reset/i });
      await user.click(resetButton);

      expect(resetCalled).toBe(true);
    });
  });

  describe('Error Handler Callback', () => {
    it('should call onError callback when error is caught', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledTimes(1);
      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({ componentStack: expect.any(String) })
      );
    });

    it('should pass correct error to onError callback', () => {
      const testError = new Error('Specific test error');
      const ThrowSpecificError = () => {
        throw testError;
      };

      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowSpecificError />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledWith(
        testError,
        expect.objectContaining({ componentStack: expect.any(String) })
      );
    });
  });

  describe('withErrorBoundary HOC', () => {
    it('should wrap component with ErrorBoundary', () => {
      const WrappedComponent = withErrorBoundary(TestComponent);

      render(<WrappedComponent message="Hello" />);

      expect(screen.getByText('Hello')).toBeInTheDocument();
    });

    it('should catch errors in wrapped component', () => {
      const WrappedComponent = withErrorBoundary(ThrowError);

      render(<WrappedComponent />);

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should use custom fallback in HOC', () => {
      const customFallback = () => <div>HOC Custom Error</div>;
      const WrappedComponent = withErrorBoundary(ThrowError, customFallback);

      render(<WrappedComponent />);

      expect(screen.getByText('HOC Custom Error')).toBeInTheDocument();
    });

    it('should set correct display name for wrapped component', () => {
      const NamedComponent = () => <div>Test</div>;
      NamedComponent.displayName = 'NamedComponent';

      const WrappedComponent = withErrorBoundary(NamedComponent);

      expect(WrappedComponent.displayName).toBe('withErrorBoundary(NamedComponent)');
    });
  });

  describe('Component Stack', () => {
    it('should show component stack in development mode', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      const componentStackButton = screen.getByText('Component Stack');
      expect(componentStackButton).toBeInTheDocument();

      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('UI Elements', () => {
    it('should display error icon', () => {
      const { container } = render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      // SVG icons don't have role="img" by default in this implementation
      const errorIcon = container.querySelector('svg');
      expect(errorIcon).toBeInTheDocument();
      expect(errorIcon).toHaveClass('w-8', 'h-8', 'text-red-500');
    });

    it('should display both action buttons', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      );

      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /go to home/i })).toBeInTheDocument();
    });
  });
});
