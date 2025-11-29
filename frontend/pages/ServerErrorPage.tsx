import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * 500 Server Error Page
 * Displays when server returns 500+ error
 */
const ServerErrorPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-red-100 rounded-full mb-6">
            <svg
              className="w-12 h-12 text-red-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          <h1 className="text-6xl font-bold text-gray-900 mb-4">500</h1>
          <h2 className="text-3xl font-semibold text-gray-800 mb-6">
            Internal Server Error
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-lg mx-auto">
            Oops! Something went wrong on our end. Our team has been notified and we're
            working to fix the issue.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            What can you do?
          </h3>
          <ul className="text-left text-gray-600 space-y-2">
            <li className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-teal-500 mt-0.5 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Try refreshing the page</span>
            </li>
            <li className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-teal-500 mt-0.5 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Wait a few minutes and try again</span>
            </li>
            <li className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-teal-500 mt-0.5 flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Check our status page for any ongoing issues</span>
            </li>
          </ul>
        </div>

        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={() => window.location.reload()}
            className="bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-8 rounded-lg shadow-md transition-all transform hover:scale-105"
          >
            Refresh Page
          </button>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-8 rounded-lg shadow-md transition-all"
          >
            Go to Home
          </button>
        </div>

        <div className="mt-8 text-sm text-gray-500">
          If the problem persists, please contact support
        </div>
      </div>
    </div>
  );
};

export default ServerErrorPage;
