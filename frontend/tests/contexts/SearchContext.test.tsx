/**
 * SearchContext Tests
 *
 * Unit tests for SearchContext provider and hook.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { SearchProvider, useSearchContext } from '@/contexts/SearchContext';
import { mockLocalStorage } from './test-utils';
import type { SearchFilters } from '@/types';

// ============================================================================
// Test Setup
// ============================================================================

const SEARCH_HISTORY_KEY = 'recipe_search_history';

describe('SearchContext', () => {
  let localStorageMock: ReturnType<typeof mockLocalStorage>;

  beforeEach(() => {
    localStorageMock = mockLocalStorage();
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // Hook Tests
  // ============================================================================

  describe('useSearchContext hook', () => {
    it('should throw error when used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useSearchContext());
      }).toThrow('useSearchContext must be used within SearchProvider');

      consoleSpy.mockRestore();
    });

    it('should provide context value when used inside provider', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      expect(result.current).toHaveProperty('query');
      expect(result.current).toHaveProperty('filters');
      expect(result.current).toHaveProperty('recentSearches');
      expect(result.current).toHaveProperty('setQuery');
      expect(result.current).toHaveProperty('setFilters');
      expect(result.current).toHaveProperty('addToHistory');
    });

    it('should initialize with default state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      expect(result.current.query).toBe('');
      expect(result.current.filters).toEqual({});
      expect(result.current.recentSearches).toEqual([]);
    });
  });

  // ============================================================================
  // Query Management Tests
  // ============================================================================

  describe('query management', () => {
    it('should set query', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setQuery('pasta recipes');
      });

      expect(result.current.query).toBe('pasta recipes');
    });

    it('should clear query', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setQuery('pasta recipes');
      });

      expect(result.current.query).toBe('pasta recipes');

      act(() => {
        result.current.clearQuery();
      });

      expect(result.current.query).toBe('');
    });
  });

  // ============================================================================
  // Filter Management Tests
  // ============================================================================

  describe('filter management', () => {
    it('should set filters', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      const filters: SearchFilters = {
        cuisine_type: 'Italian',
        difficulty: 'easy',
      };

      act(() => {
        result.current.setFilters(filters);
      });

      expect(result.current.filters).toEqual(filters);
    });

    it('should update filters partially', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setFilters({ cuisine_type: 'Italian' });
      });

      act(() => {
        result.current.updateFilters({ difficulty: 'easy' });
      });

      expect(result.current.filters).toEqual({
        cuisine_type: 'Italian',
        difficulty: 'easy',
      });
    });

    it('should clear filters', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setFilters({
          cuisine_type: 'Italian',
          difficulty: 'easy',
        });
      });

      expect(result.current.filters).toEqual({
        cuisine_type: 'Italian',
        difficulty: 'easy',
      });

      act(() => {
        result.current.clearFilters();
      });

      expect(result.current.filters).toEqual({});
    });

    it('should detect active filters', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      expect(result.current.hasActiveFilters()).toBe(false);

      act(() => {
        result.current.setFilters({ cuisine_type: 'Italian' });
      });

      expect(result.current.hasActiveFilters()).toBe(true);

      act(() => {
        result.current.clearFilters();
      });

      expect(result.current.hasActiveFilters()).toBe(false);
    });

    it('should detect diet_types as active filter', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setFilters({ diet_types: ['vegetarian'] });
      });

      expect(result.current.hasActiveFilters()).toBe(true);
    });

    it('should not detect empty diet_types as active filter', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setFilters({ diet_types: [] });
      });

      expect(result.current.hasActiveFilters()).toBe(false);
    });
  });

  // ============================================================================
  // History Management Tests
  // ============================================================================

  describe('history management', () => {
    it('should load history from localStorage on mount', () => {
      const history = ['pasta', 'pizza', 'salad'];
      localStorageMock.getItem.mockReturnValue(JSON.stringify(history));

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      expect(result.current.recentSearches).toEqual(history);
      expect(localStorageMock.getItem).toHaveBeenCalledWith(SEARCH_HISTORY_KEY);
    });

    it('should handle corrupted localStorage data', () => {
      localStorageMock.getItem.mockReturnValue('invalid json');
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      expect(result.current.recentSearches).toEqual([]);
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it('should add query to history', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.addToHistory('pasta recipes');
      });

      expect(result.current.recentSearches).toContain('pasta recipes');
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        SEARCH_HISTORY_KEY,
        JSON.stringify(['pasta recipes'])
      );
    });

    it('should not add empty query to history', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.addToHistory('  ');
      });

      expect(result.current.recentSearches).toEqual([]);
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });

    it('should move existing query to top of history', () => {
      localStorageMock.getItem.mockReturnValue(JSON.stringify(['pizza', 'pasta', 'salad']));

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.addToHistory('pasta');
      });

      expect(result.current.recentSearches[0]).toBe('pasta');
      expect(result.current.recentSearches).toEqual(['pasta', 'pizza', 'salad']);
    });

    it('should limit history to max items', () => {
      const longHistory = Array.from({ length: 15 }, (_, i) => `query${i}`);
      localStorageMock.getItem.mockReturnValue(JSON.stringify(longHistory));

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      expect(result.current.recentSearches.length).toBeLessThanOrEqual(10);
    });

    it('should remove query from history', () => {
      localStorageMock.getItem.mockReturnValue(JSON.stringify(['pasta', 'pizza', 'salad']));

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.removeFromHistory('pizza');
      });

      expect(result.current.recentSearches).toEqual(['pasta', 'salad']);
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        SEARCH_HISTORY_KEY,
        JSON.stringify(['pasta', 'salad'])
      );
    });

    it('should clear all history', () => {
      localStorageMock.getItem.mockReturnValue(JSON.stringify(['pasta', 'pizza', 'salad']));

      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.clearHistory();
      });

      expect(result.current.recentSearches).toEqual([]);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith(SEARCH_HISTORY_KEY);
    });
  });

  // ============================================================================
  // Convenience Methods Tests
  // ============================================================================

  describe('convenience methods', () => {
    it('should reset search state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <SearchProvider>{children}</SearchProvider>
      );

      const { result } = renderHook(() => useSearchContext(), { wrapper });

      act(() => {
        result.current.setQuery('pasta');
        result.current.setFilters({ cuisine_type: 'Italian' });
      });

      expect(result.current.query).toBe('pasta');
      expect(result.current.filters).toEqual({ cuisine_type: 'Italian' });

      act(() => {
        result.current.resetSearch();
      });

      expect(result.current.query).toBe('');
      expect(result.current.filters).toEqual({});
    });
  });
});
