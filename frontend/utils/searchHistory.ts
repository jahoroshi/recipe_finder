/**
 * Search History Utility
 * Manages local storage for search history with privacy controls
 */

const STORAGE_KEY = 'recipe-search-history';
const MAX_HISTORY_ITEMS = 10;
const EXPIRY_DAYS = 30;

export interface SearchHistoryItem {
  query: string;
  timestamp: number;
}

/**
 * Get all search history items
 */
export const getSearchHistory = (): SearchHistoryItem[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const items: SearchHistoryItem[] = JSON.parse(stored);
    const now = Date.now();
    const expiryMs = EXPIRY_DAYS * 24 * 60 * 60 * 1000;

    // Filter out expired items
    const validItems = items.filter(
      (item) => now - item.timestamp < expiryMs
    );

    // Update storage if items were removed
    if (validItems.length !== items.length) {
      saveSearchHistory(validItems);
    }

    return validItems;
  } catch (error) {
    console.error('Failed to read search history:', error);
    return [];
  }
};

/**
 * Add a search query to history
 */
export const addToSearchHistory = (query: string): void => {
  if (!query.trim()) return;

  try {
    const history = getSearchHistory();

    // Remove duplicate if exists
    const filteredHistory = history.filter(
      (item) => item.query.toLowerCase() !== query.toLowerCase()
    );

    // Add new item at the beginning
    const newHistory: SearchHistoryItem[] = [
      { query: query.trim(), timestamp: Date.now() },
      ...filteredHistory,
    ].slice(0, MAX_HISTORY_ITEMS);

    saveSearchHistory(newHistory);
  } catch (error) {
    console.error('Failed to add to search history:', error);
  }
};

/**
 * Clear all search history
 */
export const clearSearchHistory = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear search history:', error);
  }
};

/**
 * Remove a specific item from history
 */
export const removeFromSearchHistory = (query: string): void => {
  try {
    const history = getSearchHistory();
    const filtered = history.filter(
      (item) => item.query.toLowerCase() !== query.toLowerCase()
    );
    saveSearchHistory(filtered);
  } catch (error) {
    console.error('Failed to remove from search history:', error);
  }
};

/**
 * Save history to local storage
 */
const saveSearchHistory = (items: SearchHistoryItem[]): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch (error) {
    console.error('Failed to save search history:', error);
  }
};
