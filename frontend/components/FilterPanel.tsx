import React, { useState, useEffect, memo, useCallback } from 'react';
import { RecipeDifficulty } from '@/types';

export interface FilterState {
  cuisine_type?: string;
  difficulty?: RecipeDifficulty;
  diet_types: string[];
  min_prep_time?: number;
  max_prep_time?: number;
  min_cook_time?: number;
  max_cook_time?: number;
  min_servings?: number;
  max_servings?: number;
}

interface FilterPanelProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  className?: string;
}

const DIET_TYPES = [
  'Vegetarian',
  'Vegan',
  'Gluten-Free',
  'Dairy-Free',
  'Keto',
  'Paleo',
];

const CUISINES = [
  'Italian',
  'Mexican',
  'Chinese',
  'Indian',
  'Thai',
  'French',
  'Japanese',
  'American',
  'Mediterranean',
  'Korean',
  'Vietnamese',
  'Spanish',
];

/**
 * FilterPanel Component
 * Provides comprehensive filtering controls for recipes
 */
const FilterPanel: React.FC<FilterPanelProps> = memo(({
  filters,
  onFiltersChange,
  isCollapsed = false,
  onToggleCollapse,
  className = '',
}) => {
  const [localFilters, setLocalFilters] = useState<FilterState>(filters);
  const [debouncedFilters, setDebouncedFilters] = useState<FilterState>(filters);

  // Debounce filter changes for text inputs and range sliders
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(localFilters);
    }, 500);

    return () => clearTimeout(timer);
  }, [localFilters]);

  // Propagate debounced changes to parent
  useEffect(() => {
    onFiltersChange(debouncedFilters);
  }, [debouncedFilters, onFiltersChange]);

  const handleCuisineChange = (value: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      cuisine_type: value || undefined,
    }));
  };

  const handleDifficultyChange = (value: RecipeDifficulty | '') => {
    const newFilters = {
      ...localFilters,
      difficulty: value || undefined,
    };
    setLocalFilters(newFilters);
    // Immediately update for radio buttons (no debounce)
    onFiltersChange(newFilters);
  };

  const handleDietTypeToggle = (dietType: string) => {
    setLocalFilters((prev) => {
      const currentDietTypes = prev.diet_types || [];
      const newDietTypes = currentDietTypes.includes(dietType)
        ? currentDietTypes.filter((dt) => dt !== dietType)
        : [...currentDietTypes, dietType];

      // Immediately update for checkboxes (no debounce)
      onFiltersChange({
        ...prev,
        diet_types: newDietTypes,
      });

      return {
        ...prev,
        diet_types: newDietTypes,
      };
    });
  };

  const handleNumberChange = (
    field: keyof FilterState,
    value: string
  ) => {
    const numValue = value === '' ? undefined : parseInt(value, 10);
    setLocalFilters((prev) => ({
      ...prev,
      [field]: numValue,
    }));
  };

  const handleClearAll = () => {
    const clearedFilters: FilterState = {
      diet_types: [],
    };
    setLocalFilters(clearedFilters);
    setDebouncedFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

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

  const filterCount = activeFilterCount();

  return (
    <div className={`bg-white rounded-lg shadow-md ${className}`}>
      {/* Header with collapse toggle on mobile */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 lg:hidden">
        <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
          Filters
          {filterCount > 0 && (
            <span className="bg-teal-500 text-white text-xs font-bold px-2 py-1 rounded-full">
              {filterCount}
            </span>
          )}
        </h3>
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="text-gray-500 hover:text-gray-700"
            aria-label={isCollapsed ? 'Expand filters' : 'Collapse filters'}
          >
            <svg
              className={`w-5 h-5 transform transition-transform ${
                isCollapsed ? 'rotate-0' : 'rotate-180'
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Desktop header */}
      <div className="hidden lg:flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
          Filters
          {filterCount > 0 && (
            <span className="bg-teal-500 text-white text-xs font-bold px-2 py-1 rounded-full">
              {filterCount}
            </span>
          )}
        </h3>
        {filterCount > 0 && (
          <button
            onClick={handleClearAll}
            className="text-sm text-teal-600 hover:text-teal-800 font-medium"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Filter controls */}
      <div className={`${isCollapsed ? 'hidden lg:block' : 'block'}`}>
        <div className="p-4 space-y-6">
          {/* Cuisine Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Cuisine Type
            </label>
            <select
              value={localFilters.cuisine_type || ''}
              onChange={(e) => handleCuisineChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              <option value="">Any Cuisine</option>
              {CUISINES.map((cuisine) => (
                <option key={cuisine} value={cuisine}>
                  {cuisine}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Difficulty
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="difficulty"
                  value=""
                  checked={!localFilters.difficulty}
                  onChange={(e) => handleDifficultyChange(e.target.value as '')}
                  className="w-4 h-4 text-teal-600 border-gray-300 focus:ring-teal-500"
                />
                <span className="ml-2 text-sm text-gray-700">Any</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="difficulty"
                  value="easy"
                  checked={localFilters.difficulty === 'easy'}
                  onChange={(e) => handleDifficultyChange(e.target.value as RecipeDifficulty)}
                  className="w-4 h-4 text-teal-600 border-gray-300 focus:ring-teal-500"
                />
                <span className="ml-2 text-sm text-gray-700">Easy</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="difficulty"
                  value="medium"
                  checked={localFilters.difficulty === 'medium'}
                  onChange={(e) => handleDifficultyChange(e.target.value as RecipeDifficulty)}
                  className="w-4 h-4 text-teal-600 border-gray-300 focus:ring-teal-500"
                />
                <span className="ml-2 text-sm text-gray-700">Medium</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="difficulty"
                  value="hard"
                  checked={localFilters.difficulty === 'hard'}
                  onChange={(e) => handleDifficultyChange(e.target.value as RecipeDifficulty)}
                  className="w-4 h-4 text-teal-600 border-gray-300 focus:ring-teal-500"
                />
                <span className="ml-2 text-sm text-gray-700">Hard</span>
              </label>
            </div>
          </div>

          {/* Diet Types */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Diet Types
            </label>
            <div className="space-y-2">
              {DIET_TYPES.map((dietType) => (
                <label key={dietType} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={localFilters.diet_types?.includes(dietType) || false}
                    onChange={() => handleDietTypeToggle(dietType)}
                    className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{dietType}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Prep Time Range */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Prep Time (minutes)
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <input
                  type="number"
                  placeholder="Min"
                  min="0"
                  value={localFilters.min_prep_time ?? ''}
                  onChange={(e) => handleNumberChange('min_prep_time', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
              <div>
                <input
                  type="number"
                  placeholder="Max"
                  min="0"
                  value={localFilters.max_prep_time ?? ''}
                  onChange={(e) => handleNumberChange('max_prep_time', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Cook Time Range */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Cook Time (minutes)
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <input
                  type="number"
                  placeholder="Min"
                  min="0"
                  value={localFilters.min_cook_time ?? ''}
                  onChange={(e) => handleNumberChange('min_cook_time', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
              <div>
                <input
                  type="number"
                  placeholder="Max"
                  min="0"
                  value={localFilters.max_cook_time ?? ''}
                  onChange={(e) => handleNumberChange('max_cook_time', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Servings Range */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Servings
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <input
                  type="number"
                  placeholder="Min"
                  min="1"
                  value={localFilters.min_servings ?? ''}
                  onChange={(e) => handleNumberChange('min_servings', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
              <div>
                <input
                  type="number"
                  placeholder="Max"
                  min="1"
                  value={localFilters.max_servings ?? ''}
                  onChange={(e) => handleNumberChange('max_servings', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Clear All button for mobile */}
          <div className="lg:hidden">
            {filterCount > 0 && (
              <button
                onClick={handleClearAll}
                className="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-md transition-colors"
              >
                Clear All Filters
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

FilterPanel.displayName = 'FilterPanel';

export default FilterPanel;
