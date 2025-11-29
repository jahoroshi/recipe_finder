import React from 'react';

interface ErrorDisplayProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

/**
 * Error Display Component
 * Shows user-friendly error messages with optional retry button
 */
const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  title = 'Oops! Something went wrong',
  message,
  onRetry,
}) => {
  return (
    <div className="text-center py-20">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
        <svg
          className="w-8 h-8 text-red-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      <h2 className="text-2xl font-semibold text-gray-800 mb-2">{title}</h2>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{message}</p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-all transform hover:scale-105"
        >
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorDisplay;
