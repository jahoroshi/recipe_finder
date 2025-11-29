import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path: string;
}

const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(x => x);

  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Home', path: '/' }
    ];

    let currentPath = '';

    pathnames.forEach((segment, index) => {
      currentPath += `/${segment}`;

      // Skip ID segments (UUIDs)
      if (segment.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
        return;
      }

      let label = segment.charAt(0).toUpperCase() + segment.slice(1);

      // Customize labels
      if (segment === 'recipes') {
        if (pathnames[index + 1] === 'new') {
          return; // Skip 'recipes' when showing 'new'
        }
        label = 'Recipes';
      } else if (segment === 'new') {
        label = 'Create Recipe';
      } else if (segment === 'edit') {
        label = 'Edit Recipe';
      } else if (segment === 'search') {
        label = 'Search Results';
      } else if (segment === 'import') {
        label = 'Bulk Import';
      }

      breadcrumbs.push({ label, path: currentPath });
    });

    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  // Don't show breadcrumbs on home page
  if (location.pathname === '/') {
    return null;
  }

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <ol className="flex items-center space-x-2 text-sm">
          {breadcrumbs.map((breadcrumb, index) => (
            <li key={breadcrumb.path} className="flex items-center">
              {index > 0 && (
                <svg
                  className="w-4 h-4 text-gray-400 mx-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              )}
              {index === breadcrumbs.length - 1 ? (
                <span className="text-gray-700 font-medium">{breadcrumb.label}</span>
              ) : (
                <Link
                  to={breadcrumb.path}
                  className="text-teal-500 hover:text-teal-600 transition"
                >
                  {breadcrumb.label}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </div>
    </nav>
  );
};

export default Breadcrumbs;
