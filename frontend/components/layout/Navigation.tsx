import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { PlusIcon } from '@/components/icons/PlusIcon';

const Navigation: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-200">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo/Brand */}
          <Link to="/" className="flex items-center" onClick={closeMobileMenu}>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-800 tracking-tight">
              Recipe<span className="text-teal-500">Finder</span>
            </h1>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`text-gray-700 hover:text-teal-500 font-medium transition ${
                isActive('/') ? 'text-teal-500' : ''
              }`}
            >
              Browse
            </Link>
            <Link
              to="/search"
              className={`text-gray-700 hover:text-teal-500 font-medium transition ${
                isActive('/search') ? 'text-teal-500' : ''
              }`}
            >
              Search
            </Link>
            <Link
              to="/import"
              className={`text-gray-700 hover:text-teal-500 font-medium transition ${
                isActive('/import') ? 'text-teal-500' : ''
              }`}
            >
              Import
            </Link>
          </nav>

          {/* Desktop Action Button */}
          <Link
            to="/recipes/new"
            className="hidden md:flex items-center justify-center bg-teal-500 hover:bg-teal-600 text-white font-bold py-2 px-4 rounded-lg shadow-md transition-all duration-300 ease-in-out transform hover:scale-105"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Recipe
          </Link>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
          >
            <svg
              className="w-6 h-6 text-gray-700"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Dropdown Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-2">
              <Link
                to="/"
                onClick={closeMobileMenu}
                className={`px-4 py-3 rounded-lg font-medium transition ${
                  isActive('/')
                    ? 'bg-teal-50 text-teal-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Browse Recipes
              </Link>
              <Link
                to="/search"
                onClick={closeMobileMenu}
                className={`px-4 py-3 rounded-lg font-medium transition ${
                  isActive('/search')
                    ? 'bg-teal-50 text-teal-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Search
              </Link>
              <Link
                to="/import"
                onClick={closeMobileMenu}
                className={`px-4 py-3 rounded-lg font-medium transition ${
                  isActive('/import')
                    ? 'bg-teal-50 text-teal-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Import Recipes
              </Link>
              <Link
                to="/recipes/new"
                onClick={closeMobileMenu}
                className="flex items-center justify-center bg-teal-500 hover:bg-teal-600 text-white font-bold py-3 px-4 rounded-lg shadow-md transition-all mt-2"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Add New Recipe
              </Link>
            </nav>
          </div>
        )}

      </div>
    </header>
  );
};

export default Navigation;
