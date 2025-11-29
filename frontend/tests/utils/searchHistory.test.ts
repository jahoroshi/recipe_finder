import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  getSearchHistory,
  addToSearchHistory,
  clearSearchHistory,
  removeFromSearchHistory,
} from '@/utils/searchHistory';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('searchHistory', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  describe('getSearchHistory', () => {
    it('returns empty array when no history exists', () => {
      const history = getSearchHistory();
      expect(history).toEqual([]);
    });

    it('returns stored history', () => {
      const mockHistory = [
        { query: 'test 1', timestamp: Date.now() },
        { query: 'test 2', timestamp: Date.now() - 1000 },
      ];
      localStorageMock.setItem('recipe-search-history', JSON.stringify(mockHistory));

      const history = getSearchHistory();
      expect(history).toEqual(mockHistory);
    });

    it('filters out expired items (> 30 days)', () => {
      const now = Date.now();
      const thirtyOneDaysAgo = now - (31 * 24 * 60 * 60 * 1000);

      const mockHistory = [
        { query: 'recent', timestamp: now },
        { query: 'expired', timestamp: thirtyOneDaysAgo },
      ];
      localStorageMock.setItem('recipe-search-history', JSON.stringify(mockHistory));

      const history = getSearchHistory();
      expect(history).toHaveLength(1);
      expect(history[0].query).toBe('recent');
    });

    it('handles corrupted localStorage data', () => {
      localStorageMock.setItem('recipe-search-history', 'invalid json');

      const history = getSearchHistory();
      expect(history).toEqual([]);
    });
  });

  describe('addToSearchHistory', () => {
    it('adds new query to history', () => {
      addToSearchHistory('test query');

      const history = getSearchHistory();
      expect(history).toHaveLength(1);
      expect(history[0].query).toBe('test query');
      expect(history[0].timestamp).toBeDefined();
    });

    it('trims whitespace from query', () => {
      addToSearchHistory('  test query  ');

      const history = getSearchHistory();
      expect(history[0].query).toBe('test query');
    });

    it('does not add empty query', () => {
      addToSearchHistory('');

      const history = getSearchHistory();
      expect(history).toHaveLength(0);
    });

    it('does not add whitespace-only query', () => {
      addToSearchHistory('   ');

      const history = getSearchHistory();
      expect(history).toHaveLength(0);
    });

    it('removes duplicate query (case-insensitive)', () => {
      addToSearchHistory('test query');
      addToSearchHistory('TEST QUERY');

      const history = getSearchHistory();
      expect(history).toHaveLength(1);
      expect(history[0].query).toBe('TEST QUERY'); // Latest one
    });

    it('limits history to 10 items', () => {
      for (let i = 0; i < 15; i++) {
        addToSearchHistory(`query ${i}`);
      }

      const history = getSearchHistory();
      expect(history).toHaveLength(10);
      expect(history[0].query).toBe('query 14'); // Most recent
      expect(history[9].query).toBe('query 5'); // Oldest kept
    });

    it('adds new query at the beginning', () => {
      addToSearchHistory('query 1');
      addToSearchHistory('query 2');

      const history = getSearchHistory();
      expect(history[0].query).toBe('query 2');
      expect(history[1].query).toBe('query 1');
    });
  });

  describe('clearSearchHistory', () => {
    it('removes all history', () => {
      addToSearchHistory('query 1');
      addToSearchHistory('query 2');

      clearSearchHistory();

      const history = getSearchHistory();
      expect(history).toEqual([]);
    });

    it('does not throw when no history exists', () => {
      expect(() => clearSearchHistory()).not.toThrow();
    });
  });

  describe('removeFromSearchHistory', () => {
    it('removes specific query', () => {
      addToSearchHistory('query 1');
      addToSearchHistory('query 2');
      addToSearchHistory('query 3');

      removeFromSearchHistory('query 2');

      const history = getSearchHistory();
      expect(history).toHaveLength(2);
      expect(history.some((h) => h.query === 'query 2')).toBe(false);
    });

    it('removes query case-insensitively', () => {
      addToSearchHistory('Test Query');

      removeFromSearchHistory('test query');

      const history = getSearchHistory();
      expect(history).toHaveLength(0);
    });

    it('does not throw when query not found', () => {
      addToSearchHistory('query 1');

      expect(() => removeFromSearchHistory('nonexistent')).not.toThrow();

      const history = getSearchHistory();
      expect(history).toHaveLength(1);
    });
  });

  describe('error handling', () => {
    it('handles localStorage errors gracefully in getSearchHistory', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      vi.spyOn(window.localStorage, 'getItem').mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      const history = getSearchHistory();
      expect(history).toEqual([]);
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it('handles localStorage errors gracefully in addToSearchHistory', () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      vi.spyOn(window.localStorage, 'setItem').mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      expect(() => addToSearchHistory('test')).not.toThrow();
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });
  });
});
