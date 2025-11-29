import React from 'react';

/**
 * Search Results Page Skeleton Loader
 * Displays a placeholder while search results are loading
 */
const SearchResultsSkeleton: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Search header skeleton */}
        <div className="mb-8 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-4" />
          <div className="flex gap-4 items-center">
            <div className="h-4 bg-gray-200 rounded w-40" />
            <div className="h-4 bg-gray-200 rounded w-32" />
          </div>
        </div>

        {/* Parsed query info skeleton */}
        <div className="bg-white rounded-lg p-6 mb-8 shadow-md animate-pulse">
          <div className="h-5 bg-gray-200 rounded w-48 mb-4" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i}>
                <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
                <div className="flex gap-2 flex-wrap">
                  <div className="h-6 bg-gray-200 rounded w-20" />
                  <div className="h-6 bg-gray-200 rounded w-16" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Search filters skeleton */}
        <div className="mb-6 animate-pulse">
          <div className="flex gap-2 flex-wrap">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-8 bg-gray-200 rounded-full w-32" />
            ))}
          </div>
        </div>

        {/* Results grid skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div
              key={i}
              className="bg-white rounded-xl shadow-lg overflow-hidden animate-pulse"
            >
              {/* Image skeleton */}
              <div className="h-48 bg-gradient-to-br from-gray-200 to-gray-300" />

              {/* Content skeleton */}
              <div className="p-6 space-y-4">
                {/* Score badge */}
                <div className="flex justify-between items-start">
                  <div className="h-6 bg-gray-200 rounded-full w-20" />
                  <div className="h-6 bg-gray-200 rounded-full w-16" />
                </div>

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
                  <div className="h-6 bg-gray-200 rounded w-24" />
                </div>

                {/* Match info skeleton */}
                <div className="pt-4 border-t border-gray-100">
                  <div className="h-3 bg-gray-200 rounded w-32" />
                </div>

                {/* Button skeleton */}
                <div className="h-10 bg-gray-200 rounded-lg w-full" />
              </div>
            </div>
          ))}
        </div>

        {/* Pagination skeleton */}
        <div className="mt-8 flex justify-center animate-pulse">
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-10 w-10 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Compact Search Results Skeleton
 * Smaller skeleton for inline search results
 */
export const CompactSearchResultsSkeleton: React.FC = () => {
  return (
    <div className="space-y-4 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="bg-white rounded-lg shadow-md overflow-hidden flex gap-4 p-4"
        >
          <div className="h-24 w-24 bg-gradient-to-br from-gray-200 to-gray-300 rounded-lg flex-shrink-0" />
          <div className="flex-1 space-y-3">
            <div className="h-5 bg-gray-200 rounded w-3/4" />
            <div className="h-4 bg-gray-200 rounded w-full" />
            <div className="flex gap-2">
              <div className="h-6 bg-gray-200 rounded w-16" />
              <div className="h-6 bg-gray-200 rounded w-20" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SearchResultsSkeleton;
