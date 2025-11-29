/**
 * Search Context
 *
 * Provides global state management for search functionality.
 * Manages search history, recent searches, and search filters.
 */

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import type { SearchFilters } from '@/types';

// ============================================================================
// Constants
// ============================================================================

const SEARCH_HISTORY_KEY = 'recipe_search_history';
const MAX_HISTORY_ITEMS = 10;

// ============================================================================
// Types
// ============================================================================

export interface SearchState {
  query: string;
  filters: SearchFilters;
  recentSearches: string[];
}

interface SearchContextValue extends SearchState {
  // Query Management
  setQuery: (query: string) => void;
  clearQuery: () => void;

  // Filter Management
  setFilters: (filters: SearchFilters) => void;
  updateFilters: (partialFilters: Partial<SearchFilters>) => void;
  clearFilters: () => void;
  hasActiveFilters: () => boolean;

  // History Management
  addToHistory: (query: string) => void;
  removeFromHistory: (query: string) => void;
  clearHistory: () => void;

  // Convenience
  resetSearch: () => void;
}

interface SearchProviderProps {
  children: ReactNode;
}

// ============================================================================
// Default State
// ============================================================================

const defaultFilters: SearchFilters = {};

const defaultState: SearchState = {
  query: '',
  filters: defaultFilters,
  recentSearches: [],
};

// ============================================================================
// Context
// ============================================================================

const SearchContext = createContext<SearchContextValue | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
  // ============================================================================
  // State
  // ============================================================================

  const [query, setQueryState] = useState<string>(defaultState.query);
  const [filters, setFiltersState] = useState<SearchFilters>(defaultState.filters);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // ============================================================================
  // Load Search History from localStorage
  // ============================================================================

  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem(SEARCH_HISTORY_KEY);
      if (storedHistory) {
        const history = JSON.parse(storedHistory);
        if (Array.isArray(history)) {
          setRecentSearches(history.slice(0, MAX_HISTORY_ITEMS));
        }
      }
    } catch (error) {
      console.error('Failed to load search history:', error);
    }
  }, []);

  // ============================================================================
  // Save Search History to localStorage
  // ============================================================================

  const saveHistory = useCallback((history: string[]) => {
    try {
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Failed to save search history:', error);
    }
  }, []);

  // ============================================================================
  // Query Management
  // ============================================================================

  const setQuery = useCallback((newQuery: string) => {
    setQueryState(newQuery);
  }, []);

  const clearQuery = useCallback(() => {
    setQueryState('');
  }, []);

  // ============================================================================
  // Filter Management
  // ============================================================================

  const setFilters = useCallback((newFilters: SearchFilters) => {
    setFiltersState(newFilters);
  }, []);

  const updateFilters = useCallback((partialFilters: Partial<SearchFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...partialFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFiltersState(defaultFilters);
  }, []);

  const hasActiveFilters = useCallback((): boolean => {
    return (
      !!filters.cuisine_type ||
      !!filters.difficulty ||
      (!!filters.diet_types && filters.diet_types.length > 0) ||
      filters.max_prep_time !== undefined ||
      filters.max_cook_time !== undefined ||
      filters.min_servings !== undefined ||
      filters.max_servings !== undefined ||
      (!!filters.category_ids && filters.category_ids.length > 0)
    );
  }, [filters]);

  // ============================================================================
  // History Management
  // ============================================================================

  const addToHistory = useCallback((searchQuery: string) => {
    const trimmedQuery = searchQuery.trim();
    if (!trimmedQuery) return;

    setRecentSearches((prev) => {
      // Remove query if it already exists
      const filtered = prev.filter((q) => q !== trimmedQuery);

      // Add to beginning
      const updated = [trimmedQuery, ...filtered].slice(0, MAX_HISTORY_ITEMS);

      // Save to localStorage
      saveHistory(updated);

      return updated;
    });
  }, [saveHistory]);

  const removeFromHistory = useCallback((searchQuery: string) => {
    setRecentSearches((prev) => {
      const updated = prev.filter((q) => q !== searchQuery);
      saveHistory(updated);
      return updated;
    });
  }, [saveHistory]);

  const clearHistory = useCallback(() => {
    setRecentSearches([]);
    try {
      localStorage.removeItem(SEARCH_HISTORY_KEY);
    } catch (error) {
      console.error('Failed to clear search history:', error);
    }
  }, []);

  // ============================================================================
  // Convenience Methods
  // ============================================================================

  const resetSearch = useCallback(() => {
    clearQuery();
    clearFilters();
  }, [clearQuery, clearFilters]);

  // ============================================================================
  // Context Value
  // ============================================================================

  const value: SearchContextValue = {
    // State
    query,
    filters,
    recentSearches,

    // Query Management
    setQuery,
    clearQuery,

    // Filter Management
    setFilters,
    updateFilters,
    clearFilters,
    hasActiveFilters,

    // History Management
    addToHistory,
    removeFromHistory,
    clearHistory,

    // Convenience
    resetSearch,
  };

  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  );
};

// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access search context
 * @throws {Error} If used outside SearchProvider
 */
export const useSearchContext = (): SearchContextValue => {
  const context = useContext(SearchContext);

  if (context === undefined) {
    throw new Error('useSearchContext must be used within SearchProvider');
  }

  return context;
};

// Export context for testing purposes
export { SearchContext };
