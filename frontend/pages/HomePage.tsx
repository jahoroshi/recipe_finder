import React, { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { recipeService } from '@/services';
import { RecipeListParams } from '@/types';
import RecipeCard from '@/components/RecipeCard';
import SearchBar from '@/components/SearchBar';
import Pagination from '@/components/Pagination';
import { RecipeCardSkeletonGrid } from '@/components/RecipeCardSkeleton';
import ErrorDisplay from '@/components/ErrorDisplay';
import { PlusIcon } from '@/components/icons/PlusIcon';
import FilterPanel, { FilterState } from '@/components/FilterPanel';
import ActiveFilterBadges from '@/components/ActiveFilterBadges';

const PAGE_SIZE = 20;

/**
 * Home Page - Recipe List with Pagination and Filters
 * Displays paginated and filtered list of recipes fetched from API
 */
const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [isFilterCollapsed, setIsFilterCollapsed] = useState(true);
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);

  // Parse filters from URL
  const parseFiltersFromURL = useCallback((): FilterState => {
    const filters: FilterState = {
      diet_types: [],
    };

    const cuisineType = searchParams.get('cuisine_type');
    if (cuisineType) filters.cuisine_type = cuisineType;

    const difficulty = searchParams.get('difficulty');
    if (difficulty === 'easy' || difficulty === 'medium' || difficulty === 'hard') {
      filters.difficulty = difficulty;
    }

    const dietTypes = searchParams.get('diet_types');
    if (dietTypes) {
      filters.diet_types = dietTypes.split(',');
    }

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

  const [filters, setFilters] = useState<FilterState>(parseFiltersFromURL);

  // Update filters when URL changes
  useEffect(() => {
    setFilters(parseFiltersFromURL());
  }, [parseFiltersFromURL]);

  // Get current page from URL or default to 1
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  // Build API parameters from filters and pagination
  const buildAPIParams = useCallback((): RecipeListParams => {
    const params: RecipeListParams = {
      page: currentPage,
      page_size: PAGE_SIZE,
    };

    if (filters.cuisine_type) params.cuisine_type = filters.cuisine_type;
    if (filters.difficulty) params.difficulty = filters.difficulty;
    if (filters.diet_types && filters.diet_types.length > 0) {
      params.diet_types = filters.diet_types;
    }
    if (filters.min_prep_time !== undefined) params.min_prep_time = filters.min_prep_time;
    if (filters.max_prep_time !== undefined) params.max_prep_time = filters.max_prep_time;
    if (filters.min_cook_time !== undefined) params.min_cook_time = filters.min_cook_time;
    if (filters.max_cook_time !== undefined) params.max_cook_time = filters.max_cook_time;
    if (filters.min_servings !== undefined) params.min_servings = filters.min_servings;
    if (filters.max_servings !== undefined) params.max_servings = filters.max_servings;

    return params;
  }, [currentPage, filters]);

  // Fetch recipes with React Query
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['recipes', currentPage, filters],
    queryFn: () => recipeService.list(buildAPIParams()),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handlePageChange = (page: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page.toString());
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleFiltersChange = useCallback((newFilters: FilterState) => {
    const newParams = new URLSearchParams();

    // Reset to page 1 when filters change
    newParams.set('page', '1');

    // Add all active filters to URL
    if (newFilters.cuisine_type) {
      newParams.set('cuisine_type', newFilters.cuisine_type);
    }
    if (newFilters.difficulty) {
      newParams.set('difficulty', newFilters.difficulty);
    }
    if (newFilters.diet_types && newFilters.diet_types.length > 0) {
      newParams.set('diet_types', newFilters.diet_types.join(','));
    }
    if (newFilters.min_prep_time !== undefined) {
      newParams.set('min_prep_time', newFilters.min_prep_time.toString());
    }
    if (newFilters.max_prep_time !== undefined) {
      newParams.set('max_prep_time', newFilters.max_prep_time.toString());
    }
    if (newFilters.min_cook_time !== undefined) {
      newParams.set('min_cook_time', newFilters.min_cook_time.toString());
    }
    if (newFilters.max_cook_time !== undefined) {
      newParams.set('max_cook_time', newFilters.max_cook_time.toString());
    }
    if (newFilters.min_servings !== undefined) {
      newParams.set('min_servings', newFilters.min_servings.toString());
    }
    if (newFilters.max_servings !== undefined) {
      newParams.set('max_servings', newFilters.max_servings.toString());
    }

    setSearchParams(newParams);
  }, [setSearchParams]);

  const handleRemoveFilter = useCallback((filterKey: keyof FilterState, value?: string) => {
    const newFilters = { ...filters };

    if (filterKey === 'diet_types' && value) {
      // Remove specific diet type
      newFilters.diet_types = newFilters.diet_types?.filter((dt) => dt !== value) || [];
    } else if (filterKey === 'min_prep_time' || filterKey === 'max_prep_time') {
      // Clear both prep time filters
      delete newFilters.min_prep_time;
      delete newFilters.max_prep_time;
    } else if (filterKey === 'min_cook_time' || filterKey === 'max_cook_time') {
      // Clear both cook time filters
      delete newFilters.min_cook_time;
      delete newFilters.max_cook_time;
    } else if (filterKey === 'min_servings' || filterKey === 'max_servings') {
      // Clear both servings filters
      delete newFilters.min_servings;
      delete newFilters.max_servings;
    } else {
      // Clear single filter
      delete newFilters[filterKey];
    }

    handleFiltersChange(newFilters);
  }, [filters, handleFiltersChange]);

  const hasActiveFilters =
    filters.cuisine_type ||
    filters.difficulty ||
    (filters.diet_types && filters.diet_types.length > 0) ||
    filters.min_prep_time !== undefined ||
    filters.max_prep_time !== undefined ||
    filters.min_cook_time !== undefined ||
    filters.max_cook_time !== undefined ||
    filters.min_servings !== undefined ||
    filters.max_servings !== undefined;

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <main>
        {/* Hero section with search */}
        <section className="bg-teal-50/50 py-12 sm:py-16">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-800 tracking-tight">
              Find Your Next Favorite Meal
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
              Search our collection of delicious recipes, from quick weeknight dinners to gourmet feasts.
            </p>
            <div className="mt-8 max-w-xl mx-auto">
              <SearchBar
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                onSearch={handleSearch}
              />
            </div>
          </div>
        </section>

        {/* Recipe list section with filters */}
        <section className="container mx-auto p-4 sm:p-6 lg:p-8">
          {/* Mobile filter button */}
          <div className="lg:hidden mb-4">
            <button
              onClick={() => setIsMobileFiltersOpen(!isMobileFiltersOpen)}
              className="flex items-center justify-center w-full py-3 px-4 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
            >
              <svg className="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span className="font-medium text-gray-700">Filters</span>
              {hasActiveFilters && (
                <span className="ml-2 bg-teal-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                  {[
                    filters.cuisine_type,
                    filters.difficulty,
                    ...(filters.diet_types || []),
                    filters.min_prep_time !== undefined || filters.max_prep_time !== undefined ? 'prep' : null,
                    filters.min_cook_time !== undefined || filters.max_cook_time !== undefined ? 'cook' : null,
                    filters.min_servings !== undefined || filters.max_servings !== undefined ? 'servings' : null,
                  ].filter(Boolean).length}
                </span>
              )}
            </button>
          </div>

          {/* Mobile filter drawer */}
          {isMobileFiltersOpen && (
            <div className="lg:hidden fixed inset-0 z-50 overflow-hidden">
              {/* Backdrop */}
              <div
                className="absolute inset-0 bg-black bg-opacity-50"
                onClick={() => setIsMobileFiltersOpen(false)}
              />
              {/* Drawer */}
              <div className="absolute inset-y-0 left-0 max-w-sm w-full bg-white shadow-xl overflow-y-auto">
                <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between z-10">
                  <h3 className="text-lg font-bold text-gray-800">Filters</h3>
                  <button
                    onClick={() => setIsMobileFiltersOpen(false)}
                    className="text-gray-500 hover:text-gray-700"
                    aria-label="Close filters"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <FilterPanel
                  filters={filters}
                  onFiltersChange={(newFilters) => {
                    handleFiltersChange(newFilters);
                    setIsMobileFiltersOpen(false);
                  }}
                />
              </div>
            </div>
          )}

          {/* Desktop layout: sidebar + content */}
          <div className="flex gap-6">
            {/* Desktop filter sidebar */}
            <aside className="hidden lg:block w-64 flex-shrink-0">
              <div className="sticky top-6">
                <FilterPanel
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                />
              </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 min-w-0">
              {/* Header with title and add button */}
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-bold text-gray-800">
                  {data ? `${data.total} Recipes` : 'Browse Recipes'}
                </h3>
                <button
                  onClick={() => navigate('/recipes/new')}
                  className="flex items-center justify-center bg-teal-500 hover:bg-teal-600 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-all duration-300 ease-in-out transform hover:scale-105"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  <span className="hidden sm:inline">Add Recipe</span>
                  <span className="sm:hidden">Add</span>
                </button>
              </div>

              {/* Active filter badges */}
              {hasActiveFilters && (
                <div className="mb-6">
                  <ActiveFilterBadges
                    filters={filters}
                    onRemoveFilter={handleRemoveFilter}
                  />
                </div>
              )}

              {/* Loading state */}
              {isLoading && <RecipeCardSkeletonGrid count={PAGE_SIZE} />}

              {/* Error state */}
              {isError && (
                <ErrorDisplay
                  title="Failed to load recipes"
                  message={
                    error instanceof Error
                      ? error.message
                      : 'Unable to fetch recipes. Please check your connection and try again.'
                  }
                  onRetry={() => refetch()}
                />
              )}

              {/* Empty state */}
              {!isLoading && !isError && data && data.items.length === 0 && (
                <div className="text-center py-20">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                    <svg
                      className="w-8 h-8 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                      />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-700">
                    {hasActiveFilters ? 'No recipes match your filters' : 'No recipes yet'}
                  </h2>
                  <p className="text-gray-500 mt-2">
                    {hasActiveFilters
                      ? 'Try adjusting your filters or clearing them to see more results.'
                      : 'Start building your recipe collection by adding your first recipe!'}
                  </p>
                  {hasActiveFilters ? (
                    <button
                      onClick={() => handleFiltersChange({ diet_types: [] })}
                      className="mt-6 bg-teal-500 hover:bg-teal-600 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-all"
                    >
                      Clear All Filters
                    </button>
                  ) : (
                    <button
                      onClick={() => navigate('/recipes/new')}
                      className="mt-6 bg-teal-500 hover:bg-teal-600 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-all"
                    >
                      Create Your First Recipe
                    </button>
                  )}
                </div>
              )}

              {/* Recipe grid */}
              {!isLoading && !isError && data && data.items.length > 0 && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {data.items.map((recipe) => (
                      <RecipeCard key={recipe.id} recipe={recipe} />
                    ))}
                  </div>

                  {/* Pagination */}
                  <Pagination
                    currentPage={currentPage}
                    totalPages={data.pages}
                    totalItems={data.total}
                    pageSize={PAGE_SIZE}
                    onPageChange={handlePageChange}
                  />
                </>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default HomePage;
