import React from 'react';

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: 'search' | 'recipe' | 'filter' | 'error';
  actionLabel?: string;
  onAction?: () => void;
  secondaryActionLabel?: string;
  onSecondaryAction?: () => void;
}

/**
 * Empty State Component
 * Displays a helpful message when no data is available
 *
 * Usage:
 * ```tsx
 * <EmptyState
 *   title="No recipes found"
 *   message="Try adjusting your filters or search query"
 *   icon="search"
 *   actionLabel="Clear Filters"
 *   onAction={handleClearFilters}
 * />
 * ```
 */
const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  message,
  icon = 'search',
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
}) => {
  const icons = {
    search: (
      <svg
        className="w-16 h-16 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    ),
    recipe: (
      <svg
        className="w-16 h-16 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
    ),
    filter: (
      <svg
        className="w-16 h-16 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
        />
      </svg>
    ),
    error: (
      <svg
        className="w-16 h-16 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  };

  return (
    <div className="text-center py-16 px-4">
      <div className="inline-flex items-center justify-center w-24 h-24 bg-gray-100 rounded-full mb-6">
        {icons[icon]}
      </div>

      <h2 className="text-2xl font-bold text-gray-900 mb-3">{title}</h2>
      <p className="text-gray-600 mb-8 max-w-md mx-auto text-lg">{message}</p>

      <div className="flex gap-4 justify-center flex-wrap">
        {actionLabel && onAction && (
          <button
            onClick={onAction}
            className="bg-teal-500 hover:bg-teal-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-all transform hover:scale-105"
          >
            {actionLabel}
          </button>
        )}
        {secondaryActionLabel && onSecondaryAction && (
          <button
            onClick={onSecondaryAction}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-3 px-6 rounded-lg shadow-md transition-all"
          >
            {secondaryActionLabel}
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * No Recipes Found Empty State
 */
export const NoRecipesFound: React.FC<{
  onClearFilters?: () => void;
  onCreateRecipe?: () => void;
}> = ({ onClearFilters, onCreateRecipe }) => (
  <EmptyState
    icon="recipe"
    title="No recipes found"
    message="We couldn't find any recipes matching your criteria. Try adjusting your filters or create a new recipe."
    actionLabel={onClearFilters ? 'Clear Filters' : undefined}
    onAction={onClearFilters}
    secondaryActionLabel={onCreateRecipe ? 'Create Recipe' : undefined}
    onSecondaryAction={onCreateRecipe}
  />
);

/**
 * No Search Results Empty State
 */
export const NoSearchResults: React.FC<{
  query?: string;
  onClearSearch?: () => void;
}> = ({ query, onClearSearch }) => (
  <EmptyState
    icon="search"
    title="No results found"
    message={
      query
        ? `We couldn't find any recipes matching "${query}". Try a different search term or browse all recipes.`
        : "We couldn't find any results. Try a different search term."
    }
    actionLabel={onClearSearch ? 'Clear Search' : undefined}
    onAction={onClearSearch}
  />
);

/**
 * Empty Recipe List State
 */
export const EmptyRecipeList: React.FC<{ onCreateRecipe?: () => void }> = ({
  onCreateRecipe,
}) => (
  <EmptyState
    icon="recipe"
    title="No recipes yet"
    message="Get started by creating your first recipe. Share your favorite dishes with the community!"
    actionLabel={onCreateRecipe ? 'Create Your First Recipe' : undefined}
    onAction={onCreateRecipe}
  />
);

export default EmptyState;
