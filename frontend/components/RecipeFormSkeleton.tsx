import React from 'react';

/**
 * Recipe Form Page Skeleton Loader
 * Displays a placeholder while form is initializing (e.g., loading existing recipe data for edit)
 */
const RecipeFormSkeleton: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page title skeleton */}
        <div className="mb-8 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-48 mb-2" />
          <div className="h-4 bg-gray-200 rounded w-96" />
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 animate-pulse">
          {/* Form sections skeleton */}
          <div className="space-y-8">
            {/* Basic Information Section */}
            <div>
              <div className="h-6 bg-gray-200 rounded w-40 mb-4" />
              <div className="space-y-4">
                {/* Recipe name */}
                <div>
                  <div className="h-4 bg-gray-200 rounded w-32 mb-2" />
                  <div className="h-10 bg-gray-200 rounded w-full" />
                </div>

                {/* Description */}
                <div>
                  <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
                  <div className="h-24 bg-gray-200 rounded w-full" />
                </div>
              </div>
            </div>

            {/* Recipe Details Section */}
            <div>
              <div className="h-6 bg-gray-200 rounded w-32 mb-4" />
              <div className="grid grid-cols-2 gap-4">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i}>
                    <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
                    <div className="h-10 bg-gray-200 rounded w-full" />
                  </div>
                ))}
              </div>
            </div>

            {/* Ingredients Section */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <div className="h-6 bg-gray-200 rounded w-28" />
                <div className="h-10 bg-gray-200 rounded w-32" />
              </div>
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex-1 grid grid-cols-4 gap-3">
                      <div className="col-span-2 h-10 bg-gray-200 rounded" />
                      <div className="h-10 bg-gray-200 rounded" />
                      <div className="h-10 bg-gray-200 rounded" />
                    </div>
                    <div className="h-10 w-10 bg-gray-200 rounded" />
                  </div>
                ))}
              </div>
            </div>

            {/* Instructions Section */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <div className="h-6 bg-gray-200 rounded w-32" />
                <div className="h-10 bg-gray-200 rounded w-32" />
              </div>
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0" />
                    <div className="flex-1 h-20 bg-gray-200 rounded" />
                    <div className="h-10 w-10 bg-gray-200 rounded" />
                  </div>
                ))}
              </div>
            </div>

            {/* Nutritional Info Section */}
            <div>
              <div className="h-6 bg-gray-200 rounded w-48 mb-4" />
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i}>
                    <div className="h-4 bg-gray-200 rounded w-20 mb-2" />
                    <div className="h-10 bg-gray-200 rounded w-full" />
                  </div>
                ))}
              </div>
            </div>

            {/* Categories Section */}
            <div>
              <div className="h-6 bg-gray-200 rounded w-28 mb-4" />
              <div className="grid grid-cols-3 gap-3">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div
                    key={i}
                    className="h-10 bg-gray-200 rounded flex items-center px-3"
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Action buttons skeleton */}
          <div className="mt-8 pt-6 border-t border-gray-200 flex justify-end gap-4">
            <div className="h-12 bg-gray-200 rounded-lg w-24" />
            <div className="h-12 bg-gray-200 rounded-lg w-32" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeFormSkeleton;
