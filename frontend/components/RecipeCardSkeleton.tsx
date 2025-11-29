import React from 'react';

/**
 * Recipe Card Skeleton Loader
 * Displays a placeholder while recipes are loading
 */
const RecipeCardSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden animate-pulse">
      {/* Image skeleton */}
      <div className="h-48 bg-gradient-to-br from-gray-200 to-gray-300" />

      {/* Content skeleton */}
      <div className="p-6 space-y-4">
        {/* Title skeleton */}
        <div className="h-6 bg-gray-200 rounded w-3/4" />

        {/* Description skeleton */}
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
        </div>

        {/* Badges skeleton */}
        <div className="flex gap-2">
          <div className="h-6 bg-gray-200 rounded w-20" />
          <div className="h-6 bg-gray-200 rounded w-16" />
          <div className="h-6 bg-gray-200 rounded w-24" />
        </div>

        {/* Ingredients skeleton */}
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-24" />
          <div className="h-3 bg-gray-200 rounded w-full" />
          <div className="h-3 bg-gray-200 rounded w-4/5" />
          <div className="h-3 bg-gray-200 rounded w-3/4" />
        </div>

        {/* Footer skeleton */}
        <div className="pt-4 border-t border-gray-100 flex justify-between">
          <div className="h-4 bg-gray-200 rounded w-16" />
          <div className="h-4 bg-gray-200 rounded w-16" />
          <div className="h-4 bg-gray-200 rounded w-20" />
        </div>

        {/* Button skeleton */}
        <div className="h-10 bg-gray-200 rounded-lg w-full" />
      </div>
    </div>
  );
};

/**
 * Grid of skeleton loaders
 * @param count - Number of skeletons to display (default: 20)
 */
export const RecipeCardSkeletonGrid: React.FC<{ count?: number }> = ({ count = 20 }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
      {Array.from({ length: count }, (_, i) => (
        <RecipeCardSkeleton key={i} />
      ))}
    </div>
  );
};

export default RecipeCardSkeleton;
