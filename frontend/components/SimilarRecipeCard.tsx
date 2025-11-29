import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { SearchResult } from '@/types';

interface SimilarRecipeCardProps {
  result: SearchResult;
}

/**
 * Compact recipe card for similar recipes display
 * Shows recipe preview with similarity score badge
 */
const SimilarRecipeCard: React.FC<SimilarRecipeCardProps> = ({ result }) => {
  const navigate = useNavigate();
  const { recipe, score } = result;

  const handleClick = () => {
    navigate(`/recipes/${recipe.id}`);
  };

  /**
   * Get color styling based on similarity score
   * 90-100%: Excellent match (green)
   * 75-89%: Good match (blue)
   * 60-74%: Fair match (yellow)
   * <60%: Weak match (gray)
   */
  const getSimilarityBadgeColor = (score: number): string => {
    const percentage = score * 100;
    if (percentage >= 90) return 'bg-green-100 text-green-800';
    if (percentage >= 75) return 'bg-blue-100 text-blue-800';
    if (percentage >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const similarityPercentage = Math.round(score * 100);

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer flex-shrink-0"
      style={{ width: '280px' }}
      onClick={handleClick}
    >
      {/* Recipe Image Placeholder */}
      <div className="relative h-40 bg-gradient-to-br from-teal-400 to-blue-500 flex items-center justify-center">
        <span className="text-white text-5xl">🍳</span>
        {/* Similarity Score Badge */}
        <div className="absolute top-2 right-2">
          <span
            className={`${getSimilarityBadgeColor(
              score
            )} px-2 py-1 rounded-full text-xs font-bold shadow-sm`}
          >
            {similarityPercentage}% similar
          </span>
        </div>
      </div>

      {/* Recipe Info */}
      <div className="p-4">
        <h3 className="text-lg font-bold text-gray-800 mb-2 line-clamp-2" title={recipe.name}>
          {recipe.name}
        </h3>

        {/* Cuisine Badge */}
        {recipe.cuisine_type && (
          <div className="mb-2">
            <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-medium">
              {recipe.cuisine_type}
            </span>
          </div>
        )}

        {/* Description Preview */}
        {recipe.description && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{recipe.description}</p>
        )}

        {/* Quick Info */}
        <div className="flex justify-between text-xs text-gray-500 pt-2 border-t border-gray-100">
          {recipe.prep_time && <span>{recipe.prep_time}m prep</span>}
          {recipe.difficulty && (
            <span
              className={`font-medium ${
                recipe.difficulty === 'easy'
                  ? 'text-green-600'
                  : recipe.difficulty === 'medium'
                  ? 'text-yellow-600'
                  : 'text-red-600'
              }`}
            >
              {recipe.difficulty}
            </span>
          )}
          {recipe.servings && <span>{recipe.servings} servings</span>}
        </div>
      </div>
    </div>
  );
};

export default SimilarRecipeCard;
