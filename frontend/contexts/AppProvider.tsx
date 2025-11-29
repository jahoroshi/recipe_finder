/**
 * App Provider
 *
 * Combines all context providers into a single component.
 * Ensures proper provider nesting order and reduces boilerplate in App.tsx.
 */

import React, { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecipeProvider } from './RecipeContext';
import { SearchProvider } from './SearchContext';
import { UIProvider } from './UIContext';

// ============================================================================
// Query Client Configuration
// ============================================================================

/**
 * Configure React Query client with optimized defaults
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time: 5 minutes (data is considered fresh for 5 minutes)
      staleTime: 5 * 60 * 1000,

      // Cache time: 30 minutes (unused data kept in cache for 30 minutes)
      gcTime: 30 * 60 * 1000,

      // Retry failed requests once
      retry: 1,

      // Refetch on window focus (disabled for better UX)
      refetchOnWindowFocus: false,

      // Refetch on reconnect
      refetchOnReconnect: true,

      // Don't refetch on mount if data is still fresh
      refetchOnMount: false,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
    },
  },
});

// ============================================================================
// Types
// ============================================================================

interface AppProviderProps {
  children: ReactNode;
}

// ============================================================================
// Provider Component
// ============================================================================

/**
 * App Provider
 *
 * Wraps the entire application with all necessary context providers.
 * Provider order (outer to inner):
 * 1. QueryClientProvider - React Query for data fetching/caching
 * 2. UIProvider - Global UI state (loading, errors, modals)
 * 3. SearchProvider - Search state and history
 * 4. RecipeProvider - Recipe CRUD operations and cache management
 *
 * This order ensures that:
 * - React Query is available to all providers
 * - UI state is independent and can be used anywhere
 * - Search state doesn't depend on recipes
 * - Recipe operations can use UI state for notifications
 */
export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      <UIProvider>
        <SearchProvider>
          <RecipeProvider>
            {children}
          </RecipeProvider>
        </SearchProvider>
      </UIProvider>
    </QueryClientProvider>
  );
};

// Export query client for testing and direct access
export { queryClient };
