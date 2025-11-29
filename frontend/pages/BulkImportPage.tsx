import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRecipeContext } from '@/contexts/RecipeContext';
import { importNotifications } from '@/utils/notifications';

const BulkImportPage: React.FC = () => {
  const navigate = useNavigate();
  const { bulkImport, isImporting } = useRecipeContext();
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const droppedFile = files[0];
      if (droppedFile.type === 'application/json') {
        setFile(droppedFile);
      } else {
        importNotifications.invalidFile();
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setFile(files[0]);
    }
  };

  const handleImport = async () => {
    if (!file) return;

    try {
      await bulkImport(file);

      // Clear file after successful import
      setFile(null);

      // Navigate to home to see imported recipes
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (error) {
      // Error notification is handled by RecipeContext
      console.error('Import error:', error);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Bulk Import Recipes</h1>
        <p className="text-gray-600">
          Import multiple recipes at once from a JSON file
        </p>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <h2 className="font-semibold text-blue-900 mb-3">File Format Requirements</h2>
        <div className="text-sm text-blue-800 space-y-2">
          <p>Your JSON file should be an array of recipe objects with the following structure:</p>
          <pre className="bg-blue-100 p-3 rounded mt-2 overflow-x-auto text-xs">
{`[
  {
    "name": "Recipe Name",
    "description": "Recipe description",
    "instructions": {
      "steps": ["Step 1", "Step 2", "Step 3"]
    },
    "difficulty": "easy",
    "cuisine_type": "Italian",
    "prep_time": 15,
    "cook_time": 30,
    "servings": 4,
    "diet_types": ["vegetarian"],
    "ingredients": [
      {
        "name": "Ingredient 1",
        "quantity": 2,
        "unit": "cups"
      }
    ]
  }
]`}
          </pre>
        </div>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragging
            ? 'border-teal-500 bg-teal-50'
            : 'border-gray-300 bg-white hover:border-gray-400'
        }`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="mb-4">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>

        {file ? (
          <div className="space-y-2">
            <p className="text-green-600 font-semibold">{file.name}</p>
            <p className="text-gray-500 text-sm">
              {(file.size / 1024).toFixed(2)} KB
            </p>
            <button
              onClick={() => setFile(null)}
              className="text-red-500 hover:text-red-700 text-sm underline"
            >
              Remove file
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-gray-600">
              Drag and drop your JSON file here, or
            </p>
            <label className="cursor-pointer">
              <span className="text-teal-500 hover:text-teal-600 font-semibold">
                browse to upload
              </span>
              <input
                type="file"
                accept=".json"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex justify-end gap-4">
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
        >
          Cancel
        </button>
        <button
          onClick={handleImport}
          disabled={!file || isImporting}
          className={`px-6 py-2 rounded-lg font-bold transition ${
            !file || isImporting
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-teal-500 hover:bg-teal-600 text-white'
          }`}
        >
          {isImporting ? (
            <span className="flex items-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Importing...
            </span>
          ) : (
            'Import Recipes'
          )}
        </button>
      </div>

      {/* Implementation Note */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-yellow-900 mb-2">Coming Soon</h3>
        <p className="text-yellow-800">
          Full bulk import functionality with backend API integration will be implemented in Phase 2.
          The import will validate recipes and generate AI embeddings for semantic search.
        </p>
      </div>
    </div>
  );
};

export default BulkImportPage;
