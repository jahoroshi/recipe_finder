/**
 * Context Exports
 *
 * Central export point for all context providers and hooks.
 */

// App Provider (combines all providers)
export { AppProvider, queryClient } from './AppProvider';

// Recipe Context
export { RecipeProvider, useRecipeContext, RecipeContext } from './RecipeContext';

// Search Context
export { SearchProvider, useSearchContext, SearchContext } from './SearchContext';
export type { SearchState } from './SearchContext';

// UI Context
export { UIProvider, useUIContext, UIContext } from './UIContext';
export type { LoadingState, ErrorState, ModalState } from './UIContext';
