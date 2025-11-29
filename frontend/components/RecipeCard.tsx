import React, { memo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Recipe } from '../types';

interface RecipeCardProps {
    recipe: Recipe;
}

const RecipeCard: React.FC<RecipeCardProps> = memo(({ recipe }) => {
    const navigate = useNavigate();

    const handleClick = useCallback(() => {
        navigate(`/recipes/${recipe.id}`);
    }, [navigate, recipe.id]);

    return (
        <div
            className="bg-white rounded-xl shadow-lg overflow-hidden transform hover:-translate-y-2 transition-transform duration-300 ease-in-out flex flex-col cursor-pointer"
            onClick={handleClick}
        >
            <div className="relative h-48">
                {recipe.image_url ? (
                    <img
                        src={recipe.image_url}
                        alt={recipe.name}
                        loading="lazy"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                            // Fallback to gradient background if image fails to load
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            if (target.nextElementSibling) {
                                (target.nextElementSibling as HTMLElement).style.display = 'flex';
                            }
                        }}
                    />
                ) : null}
                <div
                    className="w-full h-full bg-gradient-to-br from-teal-400 to-blue-500 flex items-center justify-center"
                    style={{ display: recipe.image_url ? 'none' : 'flex' }}
                >
                    <span className="text-white text-6xl">🍳</span>
                </div>
            </div>
            <div className="p-6 flex flex-col flex-grow">
                <h3 className="text-xl font-bold text-gray-800 mb-2">{recipe.name}</h3>

                {recipe.description && (
                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">{recipe.description}</p>
                )}

                <div className="flex flex-wrap gap-2 mb-3">
                    {recipe.cuisine_type && (
                        <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs font-medium">
                            {recipe.cuisine_type}
                        </span>
                    )}
                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                        {recipe.difficulty}
                    </span>
                    {recipe.diet_types.slice(0, 2).map(diet => (
                        <span key={diet} className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-medium">
                            {diet}
                        </span>
                    ))}
                </div>

                <div className="flex-grow">
                    <p className="text-gray-600 font-semibold mb-2 text-sm">Ingredients:</p>
                    <ul className="list-disc list-inside text-gray-500 text-sm space-y-1">
                        {recipe.ingredients.slice(0, 3).map((ingredient) => (
                            <li key={ingredient.id} className="truncate">
                                {ingredient.quantity && ingredient.unit && `${ingredient.quantity}${ingredient.unit} `}
                                {ingredient.name}
                            </li>
                        ))}
                        {recipe.ingredients.length > 3 && (
                            <li className="text-gray-400">...and {recipe.ingredients.length - 3} more</li>
                        )}
                    </ul>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between text-sm text-gray-500">
                    {recipe.prep_time && (
                        <span>Prep: {recipe.prep_time}m</span>
                    )}
                    {recipe.cook_time && (
                        <span>Cook: {recipe.cook_time}m</span>
                    )}
                    {recipe.servings && (
                        <span>Serves: {recipe.servings}</span>
                    )}
                </div>

                <button
                    className="mt-4 w-full bg-teal-100 text-teal-700 font-semibold py-2 px-4 rounded-lg hover:bg-teal-200 transition-colors duration-300"
                    onClick={handleClick}
                >
                    View Recipe
                </button>
            </div>
        </div>
    );
});

RecipeCard.displayName = 'RecipeCard';

export default RecipeCard;
