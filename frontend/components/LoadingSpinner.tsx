import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'teal' | 'gray' | 'white';
  fullScreen?: boolean;
  message?: string;
}

/**
 * Loading Spinner Component
 * Displays an animated spinner for loading states
 *
 * @param size - Size of the spinner (sm: 4, md: 8, lg: 12, xl: 16)
 * @param color - Color of the spinner (teal, gray, white)
 * @param fullScreen - Whether to display in full screen centered
 * @param message - Optional loading message to display
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'teal',
  fullScreen = false,
  message,
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3',
    xl: 'h-16 w-16 border-4',
  };

  const colorClasses = {
    teal: 'border-teal-500',
    gray: 'border-gray-500',
    white: 'border-white',
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center gap-4">
      <div
        className={`
          animate-spin rounded-full border-t-transparent
          ${sizeClasses[size]}
          ${colorClasses[color]}
        `}
        role="status"
        aria-label="Loading"
      />
      {message && (
        <p className="text-gray-600 text-sm font-medium animate-pulse">{message}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        {spinner}
      </div>
    );
  }

  return spinner;
};

/**
 * Inline Loading Spinner
 * Small spinner for inline loading states (e.g., button loading)
 */
export const InlineSpinner: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div
    className={`inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent ${className}`}
    role="status"
    aria-label="Loading"
  />
);

/**
 * Full Page Loading Spinner
 * Convenient wrapper for full screen loading
 */
export const FullPageSpinner: React.FC<{ message?: string }> = ({ message }) => (
  <LoadingSpinner size="lg" fullScreen message={message} />
);

/**
 * Button Loading Spinner
 * Spinner designed for button loading states
 */
export const ButtonSpinner: React.FC = () => (
  <div className="inline-flex items-center gap-2">
    <InlineSpinner />
    <span>Loading...</span>
  </div>
);

export default LoadingSpinner;
