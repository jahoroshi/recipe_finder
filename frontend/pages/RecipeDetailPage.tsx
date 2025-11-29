import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { recipeService } from '@/services';
import ErrorDisplay from '@/components/ErrorDisplay';
import RecipeCarousel, { RecipeCarouselSkeleton } from '@/components/RecipeCarousel';
import { ApiError } from '@/services/api.config';
import type { Recipe, SearchResult } from '@/types';
import { format } from 'date-fns';
import { recipeNotifications } from '@/utils/notifications';

/**
 * Recipe Detail Page
 * Displays complete recipe information with actions
 */
const RecipeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Fetch recipe data
  const {
    data: recipe,
    isLoading,
    isError,
    error,
  } = useQuery<Recipe, ApiError>({
    queryKey: ['recipe', id],
    queryFn: () => recipeService.getById(id!),
    enabled: !!id,
  });

  // Fetch similar recipes
  const {
    data: similarRecipes,
    isLoading: isSimilarLoading,
    isError: isSimilarError,
    error: similarError,
  } = useQuery<SearchResult[], ApiError>({
    queryKey: ['similar-recipes', id],
    queryFn: () => recipeService.findSimilar(id!, 6),
    enabled: !!id && !!recipe, // Only fetch after recipe is loaded
    staleTime: 10 * 60 * 1000, // 10 minutes cache
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => recipeService.delete(id!),
    onSuccess: () => {
      // Invalidate recipe list cache
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      // Show success notification
      recipeNotifications.deleted(recipe?.name || 'Recipe');
      // Navigate to home page
      navigate('/');
    },
    onError: (error: ApiError) => {
      setShowDeleteModal(false);
      // Show error notification with retry option
      recipeNotifications.deleteFailed(
        error.message || 'Unknown error',
        () => {
          setShowDeleteModal(true);
        }
      );
    },
  });

  const handleEdit = () => {
    navigate(`/recipes/${id}/edit`);
  };

  const handleDeleteConfirm = () => {
    deleteMutation.mutate();
  };

  const handleFindSimilar = () => {
    // Scroll to similar recipes section
    const similarSection = document.getElementById('similar-recipes-section');
    if (similarSection) {
      similarSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleCategoryClick = (categorySlug: string) => {
    navigate(`/?category=${categorySlug}`);
  };

  // Loading state
  if (isLoading) {
    return <RecipeDetailSkeleton />;
  }

  // Error state
  if (isError) {
    const errorMessage =
      error?.statusCode === 404
        ? 'Recipe not found. It may have been deleted.'
        : error?.message || 'Failed to load recipe details.';

    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorDisplay
          title={error?.statusCode === 404 ? 'Recipe Not Found' : 'Error Loading Recipe'}
          message={errorMessage}
          onRetry={() => navigate('/')}
        />
      </div>
    );
  }

  // Recipe not found (should not happen with error handling above)
  if (!recipe) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorDisplay
          title="Recipe Not Found"
          message="The recipe you're looking for doesn't exist."
          onRetry={() => navigate('/')}
        />
      </div>
    );
  }

  const totalTime = (recipe.prep_time || 0) + (recipe.cook_time || 0);

  return (
    <>
      <div className="container mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-4">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-gray-800 mb-2">{recipe.name}</h1>
              {recipe.description && (
                <p className="text-gray-600 text-lg">{recipe.description}</p>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={handleEdit}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => setShowDeleteModal(true)}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors font-medium"
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
              <button
                onClick={handleFindSimilar}
                className="bg-teal-500 hover:bg-teal-600 text-white px-4 py-2 rounded-lg transition-colors font-medium"
              >
                Find Similar
              </button>
            </div>
          </div>

          {/* Meta Badges */}
          <div className="flex flex-wrap gap-2">
            {recipe.cuisine_type && (
              <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                {recipe.cuisine_type}
              </span>
            )}
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                recipe.difficulty === 'easy'
                  ? 'bg-green-100 text-green-800'
                  : recipe.difficulty === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {recipe.difficulty.charAt(0).toUpperCase() + recipe.difficulty.slice(1)}
            </span>
            {recipe.diet_types.map((diet) => (
              <span
                key={diet}
                className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium"
              >
                {diet}
              </span>
            ))}
          </div>
        </div>

        {/* Info Panel */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {recipe.prep_time !== undefined && recipe.prep_time > 0 && (
              <div>
                <p className="text-gray-500 text-sm">Prep Time</p>
                <p className="text-gray-800 font-semibold">{recipe.prep_time} min</p>
              </div>
            )}
            {recipe.cook_time !== undefined && recipe.cook_time > 0 && (
              <div>
                <p className="text-gray-500 text-sm">Cook Time</p>
                <p className="text-gray-800 font-semibold">{recipe.cook_time} min</p>
              </div>
            )}
            {totalTime > 0 && (
              <div>
                <p className="text-gray-500 text-sm">Total Time</p>
                <p className="text-gray-800 font-semibold">{totalTime} min</p>
              </div>
            )}
            {recipe.servings !== undefined && recipe.servings > 0 && (
              <div>
                <p className="text-gray-500 text-sm">Servings</p>
                <p className="text-gray-800 font-semibold">{recipe.servings}</p>
              </div>
            )}
            <div>
              <p className="text-gray-500 text-sm">Created</p>
              <p className="text-gray-800 font-semibold">
                {format(new Date(recipe.created_at), 'MMM d, yyyy')}
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ingredients */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Ingredients</h2>
            {recipe.ingredients.length > 0 ? (
              <ul className="space-y-2">
                {recipe.ingredients.map((ingredient) => (
                  <li key={ingredient.id} className="flex items-start">
                    <input
                      type="checkbox"
                      className="mt-1 mr-3 w-4 h-4 text-teal-500 border-gray-300 rounded focus:ring-teal-500"
                    />
                    <span className="text-gray-700">
                      {ingredient.quantity && ingredient.unit ? (
                        <strong>
                          {ingredient.quantity} {ingredient.unit}{' '}
                        </strong>
                      ) : ingredient.quantity ? (
                        <strong>{ingredient.quantity} </strong>
                      ) : null}
                      {ingredient.name}
                      {ingredient.notes && (
                        <span className="text-gray-500 text-sm ml-2">
                          ({ingredient.notes})
                        </span>
                      )}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 italic">No ingredients listed</p>
            )}
          </div>

          {/* Instructions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Instructions</h2>
            {recipe.instructions.steps && recipe.instructions.steps.length > 0 ? (
              <ol className="space-y-4">
                {recipe.instructions.steps.map((step, index) => (
                  <li key={index} className="flex">
                    <span className="bg-teal-500 text-white font-bold rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
                      {index + 1}
                    </span>
                    <p className="text-gray-700 pt-1">{step}</p>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="text-gray-500 italic">No instructions available</p>
            )}
          </div>
        </div>

        {/* Nutritional Info */}
        {recipe.nutritional_info && (
          <div className="bg-white rounded-lg shadow-md p-6 mt-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Nutritional Information
              <span className="text-sm font-normal text-gray-500 ml-2">(per serving)</span>
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
              {recipe.nutritional_info.calories !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Calories</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.calories}
                  </p>
                </div>
              )}
              {recipe.nutritional_info.protein_g !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Protein</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.protein_g}g
                  </p>
                </div>
              )}
              {recipe.nutritional_info.carbohydrates_g !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Carbs</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.carbohydrates_g}g
                  </p>
                </div>
              )}
              {recipe.nutritional_info.fat_g !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Fat</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.fat_g}g
                  </p>
                </div>
              )}
              {recipe.nutritional_info.fiber_g !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Fiber</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.fiber_g}g
                  </p>
                </div>
              )}
              {recipe.nutritional_info.sugar_g !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Sugar</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.sugar_g}g
                  </p>
                </div>
              )}
              {recipe.nutritional_info.sodium_mg !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Sodium</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.sodium_mg}mg
                  </p>
                </div>
              )}
              {recipe.nutritional_info.cholesterol_mg !== undefined && (
                <div>
                  <p className="text-gray-500 text-sm">Cholesterol</p>
                  <p className="text-gray-800 font-semibold">
                    {recipe.nutritional_info.cholesterol_mg}mg
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Categories */}
        {recipe.categories.length > 0 && (
          <div className="mt-6">
            <h2 className="text-xl font-bold text-gray-800 mb-3">Categories</h2>
            <div className="flex flex-wrap gap-2">
              {recipe.categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategoryClick(category.slug)}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-lg transition-colors"
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Similar Recipes Section */}
        <div id="similar-recipes-section" className="mt-8">
          <SimilarRecipesSection
            loading={isSimilarLoading}
            error={isSimilarError ? similarError : null}
            results={similarRecipes || []}
            hasEmbedding={!!recipe.embedding}
          />
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <DeleteConfirmationModal
          recipeName={recipe.name}
          onConfirm={handleDeleteConfirm}
          onCancel={() => setShowDeleteModal(false)}
          isDeleting={deleteMutation.isPending}
        />
      )}
    </>
  );
};

/**
 * Similar Recipes Section Component
 */
interface SimilarRecipesSectionProps {
  loading: boolean;
  error: ApiError | null;
  results: SearchResult[];
  hasEmbedding: boolean;
}

const SimilarRecipesSection: React.FC<SimilarRecipesSectionProps> = ({
  loading,
  error,
  results,
  hasEmbedding,
}) => {
  // Recipe doesn't have embedding (old recipe or embedding generation failed)
  if (!hasEmbedding) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <div className="max-w-md mx-auto">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-12 w-12 mx-auto text-gray-400 mb-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Similar Recipes Not Available
          </h3>
          <p className="text-gray-600 text-sm">
            This recipe was created before the AI similarity feature was enabled. Similar recipe
            recommendations are not available.
          </p>
        </div>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Similar Recipes</h2>
        <p className="text-gray-600 mb-4">Based on ingredients and cooking style</p>
        <RecipeCarouselSkeleton />
      </div>
    );
  }

  // Error state (network failure or server error)
  if (error) {
    return (
      <div className="bg-red-50 rounded-lg p-6">
        <div className="flex items-start">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6 text-red-400 mr-3 flex-shrink-0 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="flex-1">
            <h3 className="text-red-800 font-semibold mb-1">
              Could not load similar recipes
            </h3>
            <p className="text-red-700 text-sm mb-3">
              {error.message || 'An error occurred while fetching similar recipes.'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-red-100 hover:bg-red-200 text-red-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No similar recipes found
  if (results.length === 0) {
    return (
      <div className="bg-teal-50 rounded-lg p-8 text-center">
        <div className="max-w-md mx-auto">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-12 w-12 mx-auto text-teal-500 mb-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-teal-800 mb-2">
            This Recipe is One of a Kind!
          </h3>
          <p className="text-teal-700 text-sm mb-4">
            We couldn't find any similar recipes in our database. This makes your recipe truly
            unique!
          </p>
          <a
            href="/"
            className="inline-block bg-teal-500 hover:bg-teal-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Browse More Recipes
          </a>
        </div>
      </div>
    );
  }

  // Success - display similar recipes
  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-1">Similar Recipes</h2>
        <p className="text-gray-600">
          Based on ingredients and cooking style ({results.length} found)
        </p>
      </div>
      <RecipeCarousel results={results} />
    </div>
  );
};

/**
 * Delete Confirmation Modal Component
 */
interface DeleteConfirmationModalProps {
  recipeName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting: boolean;
}

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({
  recipeName,
  onConfirm,
  onCancel,
  isDeleting,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Delete Recipe?</h3>
        <p className="text-gray-600 mb-6">
          Are you sure you want to delete <strong>"{recipeName}"</strong>? This action
          cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={isDeleting}
            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isDeleting}
            className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Recipe Detail Skeleton Loader
 */
const RecipeDetailSkeleton: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8 animate-pulse">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="h-10 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-6 bg-gray-200 rounded w-1/2" />
          </div>
          <div className="flex gap-2">
            <div className="h-10 w-20 bg-gray-200 rounded" />
            <div className="h-10 w-20 bg-gray-200 rounded" />
            <div className="h-10 w-32 bg-gray-200 rounded" />
          </div>
        </div>
        <div className="flex gap-2">
          <div className="h-7 w-24 bg-gray-200 rounded-full" />
          <div className="h-7 w-20 bg-gray-200 rounded-full" />
          <div className="h-7 w-28 bg-gray-200 rounded-full" />
        </div>
      </div>

      {/* Info Panel Skeleton */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i}>
              <div className="h-4 bg-gray-200 rounded w-20 mb-2" />
              <div className="h-5 bg-gray-200 rounded w-16" />
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ingredients Skeleton */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="h-7 bg-gray-200 rounded w-32 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-5 bg-gray-200 rounded w-full" />
            ))}
          </div>
        </div>

        {/* Instructions Skeleton */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="h-7 bg-gray-200 rounded w-32 mb-4" />
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex">
                <div className="w-8 h-8 bg-gray-200 rounded-full mr-4 flex-shrink-0" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-full" />
                  <div className="h-4 bg-gray-200 rounded w-3/4" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeDetailPage;
