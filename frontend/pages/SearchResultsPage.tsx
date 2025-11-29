import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { HybridSearchResponse, SearchFilters } from '@/types';
import { searchService } from '@/services';
import { ApiError } from '@/services/api.config';
import RecipeCard from '@/components/RecipeCard';
import SearchBar from '@/components/SearchBar';
import FilterPanel, { FilterState } from '@/components/FilterPanel';
import ActiveFilterBadges from '@/components/ActiveFilterBadges';
import Pagination from '@/components/Pagination';
import RecipeCardSkeleton, { RecipeCardSkeletonGrid } from '@/components/RecipeCardSkeleton';
import ErrorDisplay from '@/components/ErrorDisplay';
import { addToSearchHistory } from '@/utils/searchHistory';

const PAGE_SIZE = 20;

const SearchResultsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const query = searchParams.get('q') || '';
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const [searchQuery, setSearchQuery] = useState(query);
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const [showParsedQuery, setShowParsedQuery] = useState(true);

  // Parse filters from URL
  const parseFiltersFromURL = useCallback((): FilterState => {
    const filters: FilterState = { diet_types: [] };

    const cuisineType = searchParams.get('cuisine_type');
    if (cuisineType) filters.cuisine_type = cuisineType;

    const difficulty = searchParams.get('difficulty');
    if (difficulty) filters.difficulty = difficulty as 'easy' | 'medium' | 'hard';

    const dietTypes = searchParams.get('diet_types');
    if (dietTypes) filters.diet_types = dietTypes.split(',');

    const minPrepTime = searchParams.get('min_prep_time');
    if (minPrepTime) filters.min_prep_time = parseInt(minPrepTime, 10);

    const maxPrepTime = searchParams.get('max_prep_time');
    if (maxPrepTime) filters.max_prep_time = parseInt(maxPrepTime, 10);

    const minCookTime = searchParams.get('min_cook_time');
    if (minCookTime) filters.min_cook_time = parseInt(minCookTime, 10);

    const maxCookTime = searchParams.get('max_cook_time');
    if (maxCookTime) filters.max_cook_time = parseInt(maxCookTime, 10);

    const minServings = searchParams.get('min_servings');
    if (minServings) filters.min_servings = parseInt(minServings, 10);

    const maxServings = searchParams.get('max_servings');
    if (maxServings) filters.max_servings = parseInt(maxServings, 10);

    return filters;
  }, [searchParams]);

  const [filters, setFilters] = useState<FilterState>(parseFiltersFromURL());

  // Sync query from URL
  useEffect(() => {
    setSearchQuery(query);
  }, [query]);

  // Sync filters from URL
  useEffect(() => {
    setFilters(parseFiltersFromURL());
  }, [parseFiltersFromURL]);

  // Build search filters for API
  const buildSearchFilters = useCallback((): SearchFilters | undefined => {
    const apiFilters: SearchFilters = {};
    let hasFilters = false;

    if (filters.cuisine_type) {
      apiFilters.cuisine_type = filters.cuisine_type;
      hasFilters = true;
    }
    if (filters.difficulty) {
      apiFilters.difficulty = filters.difficulty;
      hasFilters = true;
    }
    if (filters.diet_types && filters.diet_types.length > 0) {
      apiFilters.diet_types = filters.diet_types;
      hasFilters = true;
    }
    if (filters.max_prep_time !== undefined) {
      apiFilters.max_prep_time = filters.max_prep_time;
      hasFilters = true;
    }
    if (filters.max_cook_time !== undefined) {
      apiFilters.max_cook_time = filters.max_cook_time;
      hasFilters = true;
    }
    if (filters.min_servings !== undefined) {
      apiFilters.min_servings = filters.min_servings;
      hasFilters = true;
    }
    if (filters.max_servings !== undefined) {
      apiFilters.max_servings = filters.max_servings;
      hasFilters = true;
    }

    return hasFilters ? apiFilters : undefined;
  }, [filters]);

  // Perform hybrid search
  const {
    data: results,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<HybridSearchResponse, ApiError>({
    queryKey: ['search', query, currentPage, filters],
    queryFn: async () => {
      if (!query.trim()) {
        throw new Error('Query is required');
      }

      const searchFilters = buildSearchFilters();
      const response = await searchService.hybrid({
        query: query.trim(),
        limit: PAGE_SIZE,
        use_semantic: true,
        use_filters: true,
        filters: searchFilters,
      });

      // Add to search history on successful search
      addToSearchHistory(query.trim());

      return response;
    },
    enabled: !!query.trim(),
    retry: 1,
  });

  // Handle search submission
  const handleSearch = () => {
    if (!searchQuery.trim()) return;

    const newParams = new URLSearchParams();
    newParams.set('q', searchQuery.trim());
    newParams.set('page', '1');

    // Preserve filters in URL
    if (filters.cuisine_type) newParams.set('cuisine_type', filters.cuisine_type);
    if (filters.difficulty) newParams.set('difficulty', filters.difficulty);
    if (filters.diet_types.length > 0) newParams.set('diet_types', filters.diet_types.join(','));
    if (filters.min_prep_time !== undefined) newParams.set('min_prep_time', filters.min_prep_time.toString());
    if (filters.max_prep_time !== undefined) newParams.set('max_prep_time', filters.max_prep_time.toString());
    if (filters.min_cook_time !== undefined) newParams.set('min_cook_time', filters.min_cook_time.toString());
    if (filters.max_cook_time !== undefined) newParams.set('max_cook_time', filters.max_cook_time.toString());
    if (filters.min_servings !== undefined) newParams.set('min_servings', filters.min_servings.toString());
    if (filters.max_servings !== undefined) newParams.set('max_servings', filters.max_servings.toString());

    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle filter changes
  const handleFiltersChange = useCallback((newFilters: FilterState) => {
    const newParams = new URLSearchParams();

    // Preserve query
    if (query) newParams.set('q', query);

    // Reset to page 1 when filters change
    newParams.set('page', '1');

    // Add filters to URL
    if (newFilters.cuisine_type) newParams.set('cuisine_type', newFilters.cuisine_type);
    if (newFilters.difficulty) newParams.set('difficulty', newFilters.difficulty);
    if (newFilters.diet_types.length > 0) newParams.set('diet_types', newFilters.diet_types.join(','));
    if (newFilters.min_prep_time !== undefined) newParams.set('min_prep_time', newFilters.min_prep_time.toString());
    if (newFilters.max_prep_time !== undefined) newParams.set('max_prep_time', newFilters.max_prep_time.toString());
    if (newFilters.min_cook_time !== undefined) newParams.set('min_cook_time', newFilters.min_cook_time.toString());
    if (newFilters.max_cook_time !== undefined) newParams.set('max_cook_time', newFilters.max_cook_time.toString());
    if (newFilters.min_servings !== undefined) newParams.set('min_servings', newFilters.min_servings.toString());
    if (newFilters.max_servings !== undefined) newParams.set('max_servings', newFilters.max_servings.toString());

    setSearchParams(newParams);
    setIsFilterPanelOpen(false); // Close mobile drawer after applying
  }, [query, setSearchParams]);

  // Handle removing individual filters
  const handleRemoveFilter = (filterKey: string, value?: string) => {
    const newFilters = { ...filters };

    switch (filterKey) {
      case 'cuisine_type':
        delete newFilters.cuisine_type;
        break;
      case 'difficulty':
        delete newFilters.difficulty;
        break;
      case 'diet_types':
        if (value) {
          newFilters.diet_types = newFilters.diet_types.filter((dt) => dt !== value);
        } else {
          newFilters.diet_types = [];
        }
        break;
      case 'prep_time':
        delete newFilters.min_prep_time;
        delete newFilters.max_prep_time;
        break;
      case 'cook_time':
        delete newFilters.min_cook_time;
        delete newFilters.max_cook_time;
        break;
      case 'servings':
        delete newFilters.min_servings;
        delete newFilters.max_servings;
        break;
    }

    handleFiltersChange(newFilters);
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page.toString());
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Get match type label
  const getMatchTypeLabel = (matchType: string) => {
    switch (matchType) {
      case 'semantic':
        return 'Similar';
      case 'filter':
        return 'Exact Match';
      case 'hybrid':
        return 'Best Match';
      default:
        return matchType;
    }
  };

  // Get match type color
  const getMatchTypeBadgeClass = (matchType: string) => {
    switch (matchType) {
      case 'semantic':
        return 'bg-blue-100 text-blue-700';
      case 'filter':
        return 'bg-green-100 text-green-700';
      case 'hybrid':
        return 'bg-purple-100 text-purple-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  // Count active filters
  const activeFilterCount = () => {
    let count = 0;
    if (filters.cuisine_type) count++;
    if (filters.difficulty) count++;
    if (filters.diet_types?.length) count++;
    if (filters.min_prep_time !== undefined || filters.max_prep_time !== undefined) count++;
    if (filters.min_cook_time !== undefined || filters.max_cook_time !== undefined) count++;
    if (filters.min_servings !== undefined || filters.max_servings !== undefined) count++;
    return count;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sticky Search Header */}
      <div className="sticky top-0 z-40 bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-6">
          <div className="max-w-2xl mx-auto">
            <SearchBar
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              onSearch={handleSearch}
              isLoading={isLoading}
              autoFocus={!query}
            />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Mobile Filter Button */}
        <div className="lg:hidden mb-4">
          <button
            onClick={() => setIsFilterPanelOpen(!isFilterPanelOpen)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span className="font-medium">Filters</span>
            {activeFilterCount() > 0 && (
              <span className="bg-teal-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                {activeFilterCount()}
              </span>
            )}
          </button>
        </div>

        {/* Mobile Filter Drawer */}
        {isFilterPanelOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div
              className="absolute inset-0 bg-black bg-opacity-50"
              onClick={() => setIsFilterPanelOpen(false)}
            />
            <div className="absolute left-0 top-0 bottom-0 w-80 bg-white overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
                <h2 className="text-lg font-bold">Filters</h2>
                <button
                  onClick={() => setIsFilterPanelOpen(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <FilterPanel
                filters={filters}
                onFiltersChange={handleFiltersChange}
                className="shadow-none rounded-none"
              />
            </div>
          </div>
        )}

        <div className="flex gap-8">
          {/* Desktop Filter Sidebar */}
          <aside className="hidden lg:block w-64 flex-shrink-0">
            <div className="sticky top-24">
              <FilterPanel filters={filters} onFiltersChange={handleFiltersChange} />
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 min-w-0">
            {query && (
              <>
                {/* Query Info and Parsed Query */}
                <div className="mb-6">
                  <h1 className="text-2xl font-bold text-gray-800 mb-4">
                    Search Results for "{query}"
                  </h1>

                  {/* AI Parsed Query Display */}
                  {results?.parsed_query && (
                    <div className="mb-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-3">
                            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                            </svg>
                            <h3 className="font-semibold text-purple-900">AI understood your search</h3>
                            <button
                              onClick={() => setShowParsedQuery(!showParsedQuery)}
                              className="ml-auto text-purple-600 hover:text-purple-800 text-sm"
                            >
                              {showParsedQuery ? 'Hide' : 'Show'}
                            </button>
                          </div>

                          {showParsedQuery && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                              {results.parsed_query.semantic_query && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Looking for:</span>
                                  <span className="text-purple-900">{results.parsed_query.semantic_query}</span>
                                </div>
                              )}
                              {results.parsed_query.ingredients && results.parsed_query.ingredients.length > 0 && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Ingredients:</span>
                                  <span className="text-purple-900">{results.parsed_query.ingredients.join(', ')}</span>
                                </div>
                              )}
                              {results.parsed_query.cuisine_type && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Cuisine:</span>
                                  <span className="text-purple-900">{results.parsed_query.cuisine_type}</span>
                                </div>
                              )}
                              {results.parsed_query.diet_types && results.parsed_query.diet_types.length > 0 && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Diet:</span>
                                  <span className="text-purple-900">{results.parsed_query.diet_types.join(', ')}</span>
                                </div>
                              )}
                              {results.parsed_query.max_prep_time !== undefined && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Max Prep Time:</span>
                                  <span className="text-purple-900">{results.parsed_query.max_prep_time} min</span>
                                </div>
                              )}
                              {results.parsed_query.max_cook_time !== undefined && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Max Cook Time:</span>
                                  <span className="text-purple-900">{results.parsed_query.max_cook_time} min</span>
                                </div>
                              )}
                              {results.parsed_query.difficulty && (
                                <div className="flex items-start gap-2">
                                  <span className="text-purple-600 font-medium">Difficulty:</span>
                                  <span className="text-purple-900 capitalize">{results.parsed_query.difficulty}</span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Active Filter Badges */}
                  {activeFilterCount() > 0 && (
                    <ActiveFilterBadges filters={filters} onRemoveFilter={handleRemoveFilter} className="mb-4" />
                  )}

                  {/* Search Metadata */}
                  {results && (
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                      <span>
                        Found <strong className="text-gray-900">{results.total}</strong> recipe{results.total !== 1 ? 's' : ''}
                      </span>
                      {results.metadata && (
                        <>
                          <span className="text-gray-400">|</span>
                          <span>Search type: <strong className="text-gray-900 capitalize">{results.search_type}</strong></span>
                          {results.metadata.semantic_results !== undefined && (
                            <>
                              <span className="text-gray-400">|</span>
                              <span>Semantic: <strong className="text-blue-700">{results.metadata.semantic_results}</strong></span>
                            </>
                          )}
                          {results.metadata.filter_results !== undefined && (
                            <>
                              <span className="text-gray-400">|</span>
                              <span>Filter: <strong className="text-green-700">{results.metadata.filter_results}</strong></span>
                            </>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Loading State */}
                {isLoading && <RecipeCardSkeletonGrid count={PAGE_SIZE} />}

                {/* Error State */}
                {isError && (
                  <ErrorDisplay
                    title="Search Failed"
                    message={error?.message || 'Failed to search recipes. Please try again.'}
                    onRetry={refetch}
                  />
                )}

                {/* Results Grid */}
                {!isLoading && !isError && results && (
                  <>
                    {results.results.length > 0 ? (
                      <>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
                          {results.results.map((result, index) => {
                            // Only show "Best Match" on the first result (highest score)
                            const showBestMatch = index === 0 && result.match_type === 'hybrid';
                            // For other results, show their actual match type (but not "Best Match")
                            const displayMatchType = showBestMatch ? result.match_type :
                              (result.match_type === 'hybrid' ? null : result.match_type);

                            return (
                              <div key={result.recipe.id} className="relative">
                                <RecipeCard recipe={result.recipe} />

                                {/* Relevance Score Badge */}
                                <div className="absolute top-2 right-2 bg-white rounded-full px-3 py-1 shadow-md z-10">
                                  <span className="text-xs font-semibold text-teal-600">
                                    {Math.round(result.score * 100)}%
                                  </span>
                                </div>

                                {/* Match Type Badge */}
                                {displayMatchType && (
                                  <div className="absolute top-2 left-2 z-10">
                                    <span className={`text-xs px-2 py-1 rounded-full font-medium shadow-sm ${getMatchTypeBadgeClass(displayMatchType)}`}>
                                      {getMatchTypeLabel(displayMatchType)}
                                    </span>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>

                        {/* Pagination */}
                        {results.total > PAGE_SIZE && (
                          <Pagination
                            total={results.total}
                            page={currentPage}
                            page_size={PAGE_SIZE}
                            pages={Math.ceil(results.total / PAGE_SIZE)}
                            onPageChange={handlePageChange}
                          />
                        )}
                      </>
                    ) : (
                      // No Results State
                      <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                        <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <h2 className="text-xl font-semibold text-gray-700 mb-2">No recipes found for "{query}"</h2>
                        <p className="text-gray-500 mb-6">
                          We couldn't find any recipes matching your search. Try:
                        </p>
                        <ul className="text-gray-600 text-sm space-y-2 mb-6">
                          <li>Using different keywords</li>
                          <li>Removing some filters</li>
                          <li>Making your search more general</li>
                        </ul>
                        <div className="flex gap-4 justify-center">
                          <button
                            onClick={() => handleFiltersChange({ diet_types: [] })}
                            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                          >
                            Clear Filters
                          </button>
                          <button
                            onClick={() => navigate('/')}
                            className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-lg transition-colors"
                          >
                            Browse All Recipes
                          </button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            {/* No Query State */}
            {!query && (
              <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                <svg className="w-16 h-16 text-teal-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h2 className="text-2xl font-semibold text-gray-700 mb-2">Start Your Recipe Search</h2>
                <p className="text-gray-500 mb-6 max-w-md mx-auto">
                  Use natural language to find exactly what you're looking for. Our AI understands your intent!
                </p>
                <div className="space-y-2 text-sm text-gray-600 max-w-md mx-auto">
                  <p className="font-semibold text-gray-800 mb-3">Try these example searches:</p>
                  <ul className="space-y-2">
                    <li className="text-left bg-gray-50 rounded px-4 py-2">"quick dinner recipes under 30 minutes"</li>
                    <li className="text-left bg-gray-50 rounded px-4 py-2">"vegetarian pasta dishes"</li>
                    <li className="text-left bg-gray-50 rounded px-4 py-2">"easy Italian desserts"</li>
                    <li className="text-left bg-gray-50 rounded px-4 py-2">"healthy breakfast with eggs"</li>
                  </ul>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default SearchResultsPage;
