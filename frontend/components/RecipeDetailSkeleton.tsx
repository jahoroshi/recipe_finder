import React from 'react';

/**
 * Recipe Detail Page Skeleton Loader
 * Displays a placeholder while recipe details are loading
 */
const RecipeDetailSkeleton: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb skeleton */}
        <div className="py-4 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-48" />
        </div>

        <div className="bg-white rounded-2xl shadow-xl overflow-hidden animate-pulse">
          {/* Header Image skeleton */}
          <div className="relative h-96 bg-gradient-to-br from-gray-200 to-gray-300">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-16 h-16 bg-gray-300 rounded-full" />
            </div>
          </div>

          <div className="p-8">
            {/* Title and actions skeleton */}
            <div className="flex justify-between items-start mb-6">
              <div className="flex-1">
                <div className="h-8 bg-gray-200 rounded w-2/3 mb-4" />
                <div className="flex gap-2">
                  <div className="h-6 bg-gray-200 rounded w-20" />
                  <div className="h-6 bg-gray-200 rounded w-24" />
                  <div className="h-6 bg-gray-200 rounded w-16" />
                </div>
              </div>
              <div className="flex gap-2">
                <div className="h-10 w-24 bg-gray-200 rounded-lg" />
                <div className="h-10 w-24 bg-gray-200 rounded-lg" />
              </div>
            </div>

            {/* Description skeleton */}
            <div className="mb-8 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-full" />
              <div className="h-4 bg-gray-200 rounded w-5/6" />
              <div className="h-4 bg-gray-200 rounded w-4/5" />
            </div>

            {/* Recipe info grid skeleton */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                >
                  <div className="h-4 bg-gray-200 rounded w-16 mb-2" />
                  <div className="h-6 bg-gray-200 rounded w-20" />
                </div>
              ))}
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Ingredients section skeleton */}
              <div>
                <div className="h-6 bg-gray-200 rounded w-32 mb-4" />
                <div className="space-y-3">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-gray-200 rounded-full" />
                      <div className="h-4 bg-gray-200 rounded flex-1" />
                    </div>
                  ))}
                </div>
              </div>

              {/* Nutritional info skeleton */}
              <div>
                <div className="h-6 bg-gray-200 rounded w-40 mb-4" />
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <div className="grid grid-cols-2 gap-4">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                      <div key={i} className="space-y-2">
                        <div className="h-3 bg-gray-200 rounded w-20" />
                        <div className="h-4 bg-gray-200 rounded w-16" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Instructions section skeleton */}
            <div className="mt-8">
              <div className="h-6 bg-gray-200 rounded w-28 mb-4" />
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="flex gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-full" />
                      <div className="h-4 bg-gray-200 rounded w-4/5" />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Categories skeleton */}
            <div className="mt-8">
              <div className="h-6 bg-gray-200 rounded w-24 mb-4" />
              <div className="flex gap-2 flex-wrap">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-8 bg-gray-200 rounded w-24" />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Similar recipes skeleton */}
        <div className="mt-12">
          <div className="h-7 bg-gray-200 rounded w-48 mb-6 animate-pulse" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="bg-white rounded-xl shadow-md overflow-hidden animate-pulse"
              >
                <div className="h-48 bg-gradient-to-br from-gray-200 to-gray-300" />
                <div className="p-4">
                  <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-full" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeDetailSkeleton;
