import React from 'react';
import AppRouter from './routes';

/**
 * Main Application Component
 *
 * Now uses React Router for navigation and page routing.
 * All page components are located in the /pages directory.
 *
 * Route structure:
 * - / - Home/Recipe List
 * - /recipes/:id - Recipe Detail
 * - /recipes/new - Create Recipe
 * - /recipes/:id/edit - Edit Recipe
 * - /search - Search Results
 * - /import - Bulk Import
 * - /404 - Not Found
 */
const App: React.FC = () => {
  return <AppRouter />;
};

export default App;
