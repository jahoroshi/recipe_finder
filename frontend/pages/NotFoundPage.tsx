import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-teal-500">404</h1>
          <h2 className="text-3xl font-bold text-gray-800 mt-4">Page Not Found</h2>
          <p className="text-gray-600 mt-4">
            Sorry, we couldn't find the page you're looking for.
          </p>
          {location.pathname && (
            <p className="text-sm text-gray-500 mt-2 font-mono bg-gray-100 p-2 rounded">
              {location.pathname}
            </p>
          )}
        </div>

        <div className="space-y-4">
          <button
            onClick={() => navigate('/')}
            className="w-full bg-teal-500 hover:bg-teal-600 text-white font-bold py-3 px-6 rounded-lg transition"
          >
            Go to Home
          </button>

          <button
            onClick={() => navigate(-1)}
            className="w-full bg-white hover:bg-gray-50 text-gray-700 font-bold py-3 px-6 rounded-lg border border-gray-300 transition"
          >
            Go Back
          </button>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <h3 className="font-semibold text-gray-800 mb-3">Quick Links</h3>
          <div className="space-y-2">
            <button
              onClick={() => navigate('/recipes/new')}
              className="text-teal-500 hover:text-teal-600 block w-full"
            >
              Create a Recipe
            </button>
            <button
              onClick={() => navigate('/search')}
              className="text-teal-500 hover:text-teal-600 block w-full"
            >
              Search Recipes
            </button>
            <button
              onClick={() => navigate('/import')}
              className="text-teal-500 hover:text-teal-600 block w-full"
            >
              Bulk Import
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
