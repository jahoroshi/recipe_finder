import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { recipeService } from '@/services';
import { useRecipeContext } from '@/contexts/RecipeContext';
import type { RecipeCreate, Recipe, IngredientCreate, ApiError } from '@/types';

// Form data type (matches RecipeCreate but with better defaults)
interface RecipeFormData {
  name: string;
  description: string;
  cuisine_type: string;
  difficulty: 'easy' | 'medium' | 'hard';
  diet_types: string[];
  prep_time: number | '';
  cook_time: number | '';
  servings: number | '';
  ingredients: IngredientCreate[];
  instructions: {
    steps: string[];
  };
  nutritional_info?: {
    calories?: number | '';
    protein_g?: number | '';
    carbohydrates_g?: number | '';
    fat_g?: number | '';
    fiber_g?: number | '';
    sugar_g?: number | '';
    sodium_mg?: number | '';
    cholesterol_mg?: number | '';
  };
}

// Available diet types
const DIET_TYPES = [
  'vegetarian',
  'vegan',
  'gluten-free',
  'dairy-free',
  'keto',
  'paleo',
];

const RecipeFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const { createRecipe, updateRecipe, isCreating, isUpdating } = useRecipeContext();
  const [showNutrition, setShowNutrition] = useState(false);

  // Fetch recipe data for edit mode
  const { data: existingRecipe, isLoading: isLoadingRecipe } = useQuery<Recipe, ApiError>({
    queryKey: ['recipe', id],
    queryFn: () => recipeService.getById(id!),
    enabled: isEditMode && !!id,
  });

  // Initialize form with react-hook-form
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset,
  } = useForm<RecipeFormData>({
    defaultValues: {
      name: '',
      description: '',
      cuisine_type: '',
      difficulty: 'medium',
      diet_types: [],
      prep_time: '',
      cook_time: '',
      servings: '',
      ingredients: [{ name: '', quantity: undefined, unit: '', notes: '' }],
      instructions: {
        steps: [''],
      },
      nutritional_info: {
        calories: '',
        protein_g: '',
        carbohydrates_g: '',
        fat_g: '',
        fiber_g: '',
        sugar_g: '',
        sodium_mg: '',
        cholesterol_mg: '',
      },
    },
  });

  // Field arrays for dynamic lists
  const { fields: ingredientFields, append: appendIngredient, remove: removeIngredient } = useFieldArray({
    control,
    name: 'ingredients',
  });

  const { fields: stepFields, append: appendStep, remove: removeStep } = useFieldArray({
    control,
    name: 'instructions.steps',
  });

  // Watch values for computed fields
  const prepTime = watch('prep_time');
  const cookTime = watch('cook_time');
  const totalTime = (prepTime || 0) + (cookTime || 0);

  // Pre-fill form in edit mode
  useEffect(() => {
    if (existingRecipe && isEditMode) {
      reset({
        name: existingRecipe.name,
        description: existingRecipe.description || '',
        cuisine_type: existingRecipe.cuisine_type || '',
        difficulty: existingRecipe.difficulty,
        diet_types: existingRecipe.diet_types || [],
        prep_time: existingRecipe.prep_time || '',
        cook_time: existingRecipe.cook_time || '',
        servings: existingRecipe.servings || '',
        ingredients: existingRecipe.ingredients.length > 0
          ? existingRecipe.ingredients.map(ing => ({
              name: ing.name,
              quantity: ing.quantity,
              unit: ing.unit || '',
              notes: ing.notes || '',
            }))
          : [{ name: '', quantity: undefined, unit: '', notes: '' }],
        instructions: {
          steps: existingRecipe.instructions.steps.length > 0
            ? existingRecipe.instructions.steps
            : [''],
        },
        nutritional_info: existingRecipe.nutritional_info
          ? {
              calories: existingRecipe.nutritional_info.calories || '',
              protein_g: existingRecipe.nutritional_info.protein_g || '',
              carbohydrates_g: existingRecipe.nutritional_info.carbohydrates_g || '',
              fat_g: existingRecipe.nutritional_info.fat_g || '',
              fiber_g: existingRecipe.nutritional_info.fiber_g || '',
              sugar_g: existingRecipe.nutritional_info.sugar_g || '',
              sodium_mg: existingRecipe.nutritional_info.sodium_mg || '',
              cholesterol_mg: existingRecipe.nutritional_info.cholesterol_mg || '',
            }
          : undefined,
      });

      if (existingRecipe.nutritional_info) {
        setShowNutrition(true);
      }
    }
  }, [existingRecipe, isEditMode, reset]);

  // Form submission handler
  const onSubmit = async (data: RecipeFormData) => {
    // Transform form data to API format
    const recipeData: RecipeCreate = {
      name: data.name.trim(),
      description: data.description.trim() || undefined,
      cuisine_type: data.cuisine_type.trim() || undefined,
      difficulty: data.difficulty,
      diet_types: data.diet_types,
      prep_time: data.prep_time ? Number(data.prep_time) : undefined,
      cook_time: data.cook_time ? Number(data.cook_time) : undefined,
      servings: data.servings ? Number(data.servings) : undefined,
      ingredients: data.ingredients
        .filter(ing => ing.name.trim() !== '')
        .map(ing => ({
          name: ing.name.trim(),
          quantity: ing.quantity ? Number(ing.quantity) : undefined,
          unit: ing.unit?.trim() || undefined,
          notes: ing.notes?.trim() || undefined,
        })),
      instructions: {
        steps: data.instructions.steps.filter(step => step.trim() !== ''),
      },
      nutritional_info: showNutrition && data.nutritional_info
        ? {
            calories: data.nutritional_info.calories ? Number(data.nutritional_info.calories) : undefined,
            protein_g: data.nutritional_info.protein_g ? Number(data.nutritional_info.protein_g) : undefined,
            carbohydrates_g: data.nutritional_info.carbohydrates_g ? Number(data.nutritional_info.carbohydrates_g) : undefined,
            fat_g: data.nutritional_info.fat_g ? Number(data.nutritional_info.fat_g) : undefined,
            fiber_g: data.nutritional_info.fiber_g ? Number(data.nutritional_info.fiber_g) : undefined,
            sugar_g: data.nutritional_info.sugar_g ? Number(data.nutritional_info.sugar_g) : undefined,
            sodium_mg: data.nutritional_info.sodium_mg ? Number(data.nutritional_info.sodium_mg) : undefined,
            cholesterol_mg: data.nutritional_info.cholesterol_mg ? Number(data.nutritional_info.cholesterol_mg) : undefined,
          }
        : undefined,
    };

    try {
      if (isEditMode) {
        const updatedRecipe = await updateRecipe(id!, recipeData);
        navigate(`/recipes/${updatedRecipe.id}`);
      } else {
        const newRecipe = await createRecipe(recipeData);
        navigate(`/recipes/${newRecipe.id}`);
      }
    } catch (error) {
      // Error notification is handled by RecipeContext
      console.error('Form submission error:', error);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    if (window.confirm('Discard changes?')) {
      navigate(isEditMode ? `/recipes/${id}` : '/');
    }
  };

  // Loading state for edit mode
  if (isEditMode && isLoadingRecipe) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
            <div className="space-y-4">
              <div className="h-10 bg-gray-200 rounded"></div>
              <div className="h-20 bg-gray-200 rounded"></div>
              <div className="h-10 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          {isEditMode ? 'Edit Recipe' : 'Create New Recipe'}
        </h1>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          {/* Basic Information Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Basic Information</h2>

            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2" htmlFor="name">
                Recipe Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                {...register('name', {
                  required: 'Recipe name is required',
                  minLength: { value: 1, message: 'Name must be at least 1 character' },
                  maxLength: { value: 255, message: 'Name must be at most 255 characters' },
                })}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="e.g., Pasta Carbonara"
              />
              {errors.name && (
                <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
              )}
            </div>

            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2" htmlFor="description">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                {...register('description')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Brief description of the recipe..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2" htmlFor="cuisine_type">
                  Cuisine Type
                </label>
                <input
                  type="text"
                  id="cuisine_type"
                  {...register('cuisine_type', {
                    maxLength: { value: 100, message: 'Cuisine type must be at most 100 characters' },
                  })}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                    errors.cuisine_type ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="e.g., Italian, Mexican"
                />
                {errors.cuisine_type && (
                  <p className="text-red-500 text-sm mt-1">{errors.cuisine_type.message}</p>
                )}
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2" htmlFor="difficulty">
                  Difficulty
                </label>
                <select
                  id="difficulty"
                  {...register('difficulty')}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            {/* Diet Types */}
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">
                Diet Types
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {DIET_TYPES.map((diet) => (
                  <label key={diet} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      value={diet}
                      {...register('diet_types')}
                      className="w-4 h-4 text-teal-500 border-gray-300 rounded focus:ring-2 focus:ring-teal-500"
                    />
                    <span className="text-gray-700 capitalize">{diet}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Timing & Servings Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Timing & Servings</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2" htmlFor="prep_time">
                  Prep Time (minutes)
                </label>
                <input
                  type="number"
                  id="prep_time"
                  {...register('prep_time', {
                    min: { value: 0, message: 'Prep time must be 0 or greater' },
                    validate: (value) => {
                      if (value && cookTime && Number(value) + Number(cookTime) >= 1440) {
                        return 'Total time must be less than 24 hours';
                      }
                      return true;
                    },
                  })}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                    errors.prep_time ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="30"
                  min="0"
                />
                {errors.prep_time && (
                  <p className="text-red-500 text-sm mt-1">{errors.prep_time.message}</p>
                )}
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2" htmlFor="cook_time">
                  Cook Time (minutes)
                </label>
                <input
                  type="number"
                  id="cook_time"
                  {...register('cook_time', {
                    min: { value: 0, message: 'Cook time must be 0 or greater' },
                    validate: (value) => {
                      if (value && prepTime && Number(value) + Number(prepTime) >= 1440) {
                        return 'Total time must be less than 24 hours';
                      }
                      return true;
                    },
                  })}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                    errors.cook_time ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="45"
                  min="0"
                />
                {errors.cook_time && (
                  <p className="text-red-500 text-sm mt-1">{errors.cook_time.message}</p>
                )}
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2" htmlFor="servings">
                  Servings
                </label>
                <input
                  type="number"
                  id="servings"
                  {...register('servings', {
                    min: { value: 1, message: 'Servings must be at least 1' },
                  })}
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                    errors.servings ? 'border-red-500' : 'border-gray-300'
                  }`}
                  placeholder="4"
                  min="1"
                />
                {errors.servings && (
                  <p className="text-red-500 text-sm mt-1">{errors.servings.message}</p>
                )}
              </div>
            </div>

            {totalTime > 0 && (
              <div className="mt-3 text-gray-600">
                <span className="font-medium">Total Time:</span> {totalTime} minutes
              </div>
            )}
          </div>

          {/* Ingredients Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Ingredients <span className="text-red-500">*</span>
            </h2>

            <div className="space-y-3">
              {ingredientFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
                    <div className="md:col-span-5">
                      <input
                        type="text"
                        {...register(`ingredients.${index}.name`, {
                          required: index === 0 ? 'At least one ingredient is required' : false,
                        })}
                        className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                          errors.ingredients?.[index]?.name ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Ingredient name *"
                      />
                      {errors.ingredients?.[index]?.name && (
                        <p className="text-red-500 text-sm mt-1">
                          {errors.ingredients[index]?.name?.message}
                        </p>
                      )}
                    </div>

                    <div className="md:col-span-2">
                      <input
                        type="number"
                        {...register(`ingredients.${index}.quantity`, {
                          min: { value: 0, message: 'Quantity must be 0 or greater' },
                        })}
                        className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                          errors.ingredients?.[index]?.quantity ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="Qty"
                        min="0"
                        step="0.01"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <input
                        type="text"
                        {...register(`ingredients.${index}.unit`, {
                          maxLength: { value: 50, message: 'Unit must be at most 50 characters' },
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                        placeholder="Unit"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <input
                        type="text"
                        {...register(`ingredients.${index}.notes`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                        placeholder="Notes"
                      />
                    </div>

                    <div className="md:col-span-1 flex items-start">
                      {ingredientFields.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeIngredient(index)}
                          className="w-full md:w-auto px-3 py-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
                          title="Remove ingredient"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={() => appendIngredient({ name: '', quantity: undefined, unit: '', notes: '' })}
              className="mt-3 px-4 py-2 border border-teal-500 text-teal-500 rounded-lg hover:bg-teal-50 transition"
            >
              + Add Ingredient
            </button>
          </div>

          {/* Instructions Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Instructions <span className="text-red-500">*</span>
            </h2>

            <div className="space-y-3">
              {stepFields.map((field, index) => (
                <div key={field.id} className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-teal-500 text-white rounded-full flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <textarea
                      {...register(`instructions.steps.${index}`, {
                        required: index === 0 ? 'At least one instruction step is required' : false,
                      })}
                      rows={2}
                      className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 ${
                        errors.instructions?.steps?.[index] ? 'border-red-500' : 'border-gray-300'
                      }`}
                      placeholder={`Step ${index + 1}...`}
                    />
                    {errors.instructions?.steps?.[index] && (
                      <p className="text-red-500 text-sm mt-1">
                        {errors.instructions.steps[index]?.message}
                      </p>
                    )}
                  </div>
                  {stepFields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeStep(index)}
                      className="flex-shrink-0 px-3 py-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
                      title="Remove step"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={() => appendStep('')}
              className="mt-3 px-4 py-2 border border-teal-500 text-teal-500 rounded-lg hover:bg-teal-50 transition"
            >
              + Add Step
            </button>
          </div>

          {/* Nutritional Information Section (Collapsible) */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-800">Nutritional Information</h2>
              <button
                type="button"
                onClick={() => setShowNutrition(!showNutrition)}
                className="text-teal-500 hover:text-teal-600 font-medium"
              >
                {showNutrition ? 'Hide' : 'Show'}
              </button>
            </div>

            {showNutrition && (
              <div className="border border-gray-200 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-4">All values are per serving (optional)</p>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="calories">
                      Calories
                    </label>
                    <input
                      type="number"
                      id="calories"
                      {...register('nutritional_info.calories', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="protein_g">
                      Protein (g)
                    </label>
                    <input
                      type="number"
                      id="protein_g"
                      {...register('nutritional_info.protein_g', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                      step="0.1"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="carbohydrates_g">
                      Carbs (g)
                    </label>
                    <input
                      type="number"
                      id="carbohydrates_g"
                      {...register('nutritional_info.carbohydrates_g', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                      step="0.1"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="fat_g">
                      Fat (g)
                    </label>
                    <input
                      type="number"
                      id="fat_g"
                      {...register('nutritional_info.fat_g', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                      step="0.1"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="fiber_g">
                      Fiber (g)
                    </label>
                    <input
                      type="number"
                      id="fiber_g"
                      {...register('nutritional_info.fiber_g', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                      step="0.1"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="sugar_g">
                      Sugar (g)
                    </label>
                    <input
                      type="number"
                      id="sugar_g"
                      {...register('nutritional_info.sugar_g', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                      step="0.1"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="sodium_mg">
                      Sodium (mg)
                    </label>
                    <input
                      type="number"
                      id="sodium_mg"
                      {...register('nutritional_info.sodium_mg', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor="cholesterol_mg">
                      Cholesterol (mg)
                    </label>
                    <input
                      type="number"
                      id="cholesterol_mg"
                      {...register('nutritional_info.cholesterol_mg', {
                        min: { value: 0, message: 'Must be 0 or greater' },
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
                      placeholder="0"
                      min="0"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleCancel}
              disabled={isCreating || isUpdating}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating || isUpdating}
              className="px-6 py-2 bg-teal-500 hover:bg-teal-600 text-white font-bold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCreating || isUpdating
                ? (isEditMode ? 'Updating...' : 'Creating...')
                : (isEditMode ? 'Update Recipe' : 'Create Recipe')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RecipeFormPage;
