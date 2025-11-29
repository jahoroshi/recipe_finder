
import React, { useState, useEffect, useCallback } from 'react';
import type { NewRecipe } from '../types';

interface AddRecipeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAddRecipe: (recipe: NewRecipe) => void;
}

const AddRecipeModal: React.FC<AddRecipeModalProps> = ({ isOpen, onClose, onAddRecipe }) => {
    const [name, setName] = useState('');
    const [ingredients, setIngredients] = useState('');
    const [instructions, setInstructions] = useState('');
    const [image, setImage] = useState('');
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

    const resetForm = useCallback(() => {
        setName('');
        setIngredients('');
        setInstructions('');
        setImage('');
        setErrors({});
    }, []);

    useEffect(() => {
        if (isOpen) {
            resetForm();
        }
    }, [isOpen, resetForm]);

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImage(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };
    
    const validateForm = () => {
        const newErrors: { [key: string]: string } = {};
        if (!name.trim()) newErrors.name = "Recipe name is required.";
        if (!ingredients.trim()) newErrors.ingredients = "Ingredients are required.";
        if (!instructions.trim()) newErrors.instructions = "Instructions are required.";
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };


    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!validateForm()) return;
        
        onAddRecipe({
            name,
            ingredients: ingredients.split('\n').filter(line => line.trim() !== ''),
            instructions,
            image: image || `https://picsum.photos/seed/${name.replace(/\s+/g, '-')}/600/400`,
        });
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex justify-center items-center p-4" onClick={onClose}>
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                <form onSubmit={handleSubmit}>
                    <div className="p-6 sm:p-8">
                        <div className="flex justify-between items-start">
                            <h2 className="text-2xl font-bold text-gray-800">Add a New Recipe</h2>
                            <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-600">&times;</button>
                        </div>
                        <div className="mt-6 space-y-6">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-700">Recipe Name</label>
                                <input type="text" id="name" value={name} onChange={e => setName(e.target.value)} className={`mt-1 block w-full border ${errors.name ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2`} />
                                {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                            </div>
                            <div>
                                <label htmlFor="ingredients" className="block text-sm font-medium text-gray-700">Ingredients (one per line)</label>
                                <textarea id="ingredients" rows={5} value={ingredients} onChange={e => setIngredients(e.target.value)} className={`mt-1 block w-full border ${errors.ingredients ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2`}></textarea>
                                {errors.ingredients && <p className="text-red-500 text-xs mt-1">{errors.ingredients}</p>}
                            </div>
                            <div>
                                <label htmlFor="instructions" className="block text-sm font-medium text-gray-700">Instructions</label>
                                <textarea id="instructions" rows={7} value={instructions} onChange={e => setInstructions(e.target.value)} className={`mt-1 block w-full border ${errors.instructions ? 'border-red-500' : 'border-gray-300'} rounded-md shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2`}></textarea>
                                {errors.instructions && <p className="text-red-500 text-xs mt-1">{errors.instructions}</p>}
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Recipe Image</label>
                                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                                    <div className="space-y-1 text-center">
                                        {image ? <img src={image} alt="Preview" className="mx-auto h-32 w-auto rounded-md" /> : <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true"><path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 4v.01M28 8l-6-6-6 6M28 8v12a4 4 0 01-4 4H12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>}
                                        <div className="flex text-sm text-gray-600">
                                            <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-teal-600 hover:text-teal-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-teal-500">
                                                <span>Upload a file</span>
                                                <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" onChange={handleImageUpload} />
                                            </label>
                                            <p className="pl-1">or drag and drop</p>
                                        </div>
                                        <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 px-6 py-4 flex justify-end space-x-3">
                        <button type="button" onClick={onClose} className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500">
                            Cancel
                        </button>
                        <button type="submit" className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500">
                            Save Recipe
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddRecipeModal;
