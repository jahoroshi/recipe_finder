import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

// Layout (loaded eagerly as it's always needed)
import Layout from '@/components/layout/Layout';

// Error Boundary (loaded eagerly for error handling)
import ErrorBoundary from '@/components/ErrorBoundary';

// Route Guards (loaded eagerly for route protection)
import { ProtectedRoute } from './guards';

// Lazy-loaded pages for code splitting
const HomePage = lazy(() => import('@/pages/HomePage'));
const RecipeDetailPage = lazy(() => import('@/pages/RecipeDetailPage'));
const RecipeFormPage = lazy(() => import('@/pages/RecipeFormPage'));
const SearchResultsPage = lazy(() => import('@/pages/SearchResultsPage'));
const BulkImportPage = lazy(() => import('@/pages/BulkImportPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));
const ServerErrorPage = lazy(() => import('@/pages/ServerErrorPage'));
const NetworkErrorPage = lazy(() => import('@/pages/NetworkErrorPage'));

// Loading fallback component
const PageLoader: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading...</p>
    </div>
  </div>
);

// Wrapper component to add Suspense and ErrorBoundary to each route
const withSuspense = (Component: React.LazyExoticComponent<React.FC>) => (
  <ErrorBoundary>
    <Suspense fallback={<PageLoader />}>
      <Component />
    </Suspense>
  </ErrorBoundary>
);

/**
 * Application Router Configuration
 *
 * Routes:
 * - / - Home/Recipe List
 * - /recipes/:id - Recipe Detail
 * - /recipes/new - Create Recipe
 * - /recipes/:id/edit - Edit Recipe
 * - /search - Search Results
 * - /import - Bulk Import
 * - /404 - Not Found
 * - /500 - Server Error
 * - /network-error - Network Error
 * - * - Catch all (redirects to 404)
 *
 * All routes are wrapped with ErrorBoundary for error handling
 */
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: withSuspense(HomePage)
      },
      {
        path: 'recipes/new',
        element: (
          <ProtectedRoute>
            {withSuspense(RecipeFormPage)}
          </ProtectedRoute>
        )
      },
      {
        path: 'recipes/:id',
        element: withSuspense(RecipeDetailPage)
      },
      {
        path: 'recipes/:id/edit',
        element: (
          <ProtectedRoute>
            {withSuspense(RecipeFormPage)}
          </ProtectedRoute>
        )
      },
      {
        path: 'search',
        element: withSuspense(SearchResultsPage)
      },
      {
        path: 'import',
        element: (
          <ProtectedRoute>
            {withSuspense(BulkImportPage)}
          </ProtectedRoute>
        )
      },
      {
        path: '404',
        element: withSuspense(NotFoundPage)
      },
      {
        path: '500',
        element: withSuspense(ServerErrorPage)
      },
      {
        path: 'network-error',
        element: withSuspense(NetworkErrorPage)
      },
      {
        path: '*',
        element: withSuspense(NotFoundPage)
      }
    ]
  }
]);

/**
 * AppRouter Component
 * Provides routing context to the application
 */
const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter;
