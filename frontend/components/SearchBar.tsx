import React, { useEffect, useRef, useState, memo, useCallback } from 'react';
import { SearchIcon } from './icons/SearchIcon';
import { useDebounce } from '@/hooks/useDebounce';

interface SearchBarProps {
    searchQuery: string;
    setSearchQuery: (query: string) => void;
    onSearch?: () => void;
    placeholder?: string;
    autoFocus?: boolean;
    isLoading?: boolean;
    showClear?: boolean;
    maxLength?: number;
    debounceMs?: number;
    enableAutoSearch?: boolean;
}

const EXAMPLE_QUERIES = [
    'quick dinner recipes under 30 minutes',
    'vegetarian pasta dishes',
    'easy Italian desserts',
    'healthy breakfast with eggs',
    'gluten-free chicken recipes',
];

const SearchBar: React.FC<SearchBarProps> = memo(({
    searchQuery,
    setSearchQuery,
    onSearch,
    placeholder = 'Try: "quick vegetarian pasta under 30 minutes"',
    autoFocus = false,
    isLoading = false,
    showClear = true,
    maxLength = 500,
    debounceMs = 500,
    enableAutoSearch = false,
}) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [charCount, setCharCount] = useState(0);

    // Debounced search query for auto-search
    const debouncedSearchQuery = useDebounce(searchQuery, debounceMs);

    // Auto-focus on mount if requested
    useEffect(() => {
        if (autoFocus && inputRef.current) {
            inputRef.current.focus();
        }
    }, [autoFocus]);

    // Update character count
    useEffect(() => {
        setCharCount(searchQuery.length);
    }, [searchQuery]);

    // Auto-search when debounced value changes (if enabled)
    useEffect(() => {
        if (enableAutoSearch && debouncedSearchQuery && onSearch && !isLoading) {
            onSearch();
        }
    }, [debouncedSearchQuery, enableAutoSearch, onSearch, isLoading]);

    const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && onSearch && !isLoading) {
            onSearch();
        }
    }, [onSearch, isLoading]);

    const handleClear = useCallback(() => {
        setSearchQuery('');
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, [setSearchQuery]);

    const handleSearchClick = useCallback(() => {
        if (onSearch && !isLoading) {
            onSearch();
        }
    }, [onSearch, isLoading]);

    return (
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <SearchIcon className="h-6 w-6 text-gray-400" />
            </div>
            <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
                maxLength={maxLength}
                disabled={isLoading}
                className="block w-full pl-12 pr-32 py-3 border border-gray-300 rounded-full text-base sm:text-lg bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 focus:border-transparent shadow-sm transition-all duration-300 ease-in-out focus:shadow-lg disabled:bg-gray-100 disabled:cursor-not-allowed"
                aria-label="Search for recipes with natural language"
            />

            {/* Clear button */}
            {showClear && searchQuery.length > 0 && !isLoading && (
                <button
                    onClick={handleClear}
                    className="absolute inset-y-0 right-24 flex items-center text-gray-400 hover:text-gray-600"
                    aria-label="Clear search"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            )}

            {/* Search button */}
            {onSearch && (
                <button
                    onClick={handleSearchClick}
                    disabled={isLoading || !searchQuery.trim()}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-teal-500 hover:text-teal-600 font-semibold disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                    aria-label={isLoading ? 'Searching...' : 'Search'}
                >
                    {isLoading ? (
                        <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-teal-500"></div>
                            <span className="hidden sm:inline">Searching...</span>
                        </div>
                    ) : (
                        'Search'
                    )}
                </button>
            )}
        </div>
    );
});

SearchBar.displayName = 'SearchBar';

export default SearchBar;
