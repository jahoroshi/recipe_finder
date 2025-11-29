import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Network Error Page
 * Displays when there's a network connectivity issue
 */
const NetworkErrorPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        <div className="mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-orange-100 rounded-full mb-6">
            <svg
              className="w-12 h-12 text-orange-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
              />
            </svg>
          </div>

          <h1 className="text-6xl font-bold text-gray-900 mb-4">Offline</h1>
          <h2 className="text-3xl font-semibold text-gray-800 mb-6">
            No Internet Connection
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-lg mx-auto">
            We're having trouble connecting to our servers. Please check your internet
            connection and try again.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            Troubleshooting Steps
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
              <span>Check your Wi-Fi or mobile data connection</span>
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
              <span>Try turning airplane mode off and on</span>
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
              <span>Restart your router or modem</span>
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
              <span>Check if other websites are accessible</span>
            </li>
          </ul>
        </div>

        {/* Connection status indicator */}
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-8">
          <div className="flex items-center justify-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" />
              <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse delay-100" />
              <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse delay-200" />
            </div>
            <span className="text-sm font-medium text-orange-700">
              Attempting to reconnect...
            </span>
          </div>
        </div>

        <div className="flex gap-4 justify-center flex-wrap">
          <button
            onClick={() => window.location.reload()}
            className="bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-8 rounded-lg shadow-md transition-all transform hover:scale-105"
          >
            Try Again
          </button>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-8 rounded-lg shadow-md transition-all"
          >
            Go to Home
          </button>
        </div>

        <div className="mt-8 text-sm text-gray-500">
          This page will automatically refresh when connection is restored
        </div>
      </div>
    </div>
  );
};

export default NetworkErrorPage;
