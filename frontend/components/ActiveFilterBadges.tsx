import React from 'react';
import { FilterState } from './FilterPanel';

interface ActiveFilterBadgesProps {
  filters: FilterState;
  onRemoveFilter: (filterKey: keyof FilterState, value?: string) => void;
  className?: string;
}

/**
 * ActiveFilterBadges Component
 * Displays active filters as removable badges
 */
const ActiveFilterBadges: React.FC<ActiveFilterBadgesProps> = ({
  filters,
  onRemoveFilter,
  className = '',
}) => {
  const badges: Array<{ label: string; key: keyof FilterState; value?: string }> = [];

  // Cuisine type
  if (filters.cuisine_type) {
    badges.push({
      label: `Cuisine: ${filters.cuisine_type}`,
      key: 'cuisine_type',
    });
  }

  // Difficulty
  if (filters.difficulty) {
    badges.push({
      label: `Difficulty: ${filters.difficulty.charAt(0).toUpperCase() + filters.difficulty.slice(1)}`,
      key: 'difficulty',
    });
  }

  // Diet types
  if (filters.diet_types && filters.diet_types.length > 0) {
    filters.diet_types.forEach((dietType) => {
      badges.push({
        label: `Diet: ${dietType}`,
        key: 'diet_types',
        value: dietType,
      });
    });
  }

  // Prep time range
  if (filters.min_prep_time !== undefined || filters.max_prep_time !== undefined) {
    const min = filters.min_prep_time ?? 0;
    const max = filters.max_prep_time ?? '∞';
    badges.push({
      label: `Prep Time: ${min}-${max} min`,
      key: 'min_prep_time', // We'll clear both min and max
    });
  }

  // Cook time range
  if (filters.min_cook_time !== undefined || filters.max_cook_time !== undefined) {
    const min = filters.min_cook_time ?? 0;
    const max = filters.max_cook_time ?? '∞';
    badges.push({
      label: `Cook Time: ${min}-${max} min`,
      key: 'min_cook_time',
    });
  }

  // Servings range
  if (filters.min_servings !== undefined || filters.max_servings !== undefined) {
    const min = filters.min_servings ?? 1;
    const max = filters.max_servings ?? '∞';
    badges.push({
      label: `Servings: ${min}-${max}`,
      key: 'min_servings',
    });
  }

  if (badges.length === 0) {
    return null;
  }

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {badges.map((badge, index) => (
        <div
          key={`${badge.key}-${badge.value || index}`}
          className="inline-flex items-center gap-1 bg-teal-100 text-teal-800 text-sm font-medium px-3 py-1 rounded-full"
        >
          <span>{badge.label}</span>
          <button
            onClick={() => onRemoveFilter(badge.key, badge.value)}
            className="ml-1 hover:bg-teal-200 rounded-full p-0.5 transition-colors"
            aria-label={`Remove ${badge.label} filter`}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
};

export default ActiveFilterBadges;
