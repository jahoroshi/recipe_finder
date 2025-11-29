import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

/**
 * Authentication Context (Placeholder)
 * Will be implemented with actual auth in future phases
 */
interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
}

// Placeholder auth state - will be replaced with actual auth context
const useAuth = (): AuthContextType => {
  // TODO: Implement actual authentication in future phase
  // For now, all users are "authenticated"
  return {
    isAuthenticated: true,
    user: null
  };
};

/**
 * ProtectedRoute Component
 * Guards routes that require authentication
 *
 * Usage:
 * <ProtectedRoute>
 *   <YourComponent />
 * </ProtectedRoute>
 */
export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    // Redirect to login page (when implemented)
    // Store the attempted location for redirect after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

/**
 * AdminRoute Component
 * Guards routes that require admin privileges
 *
 * Usage:
 * <AdminRoute>
 *   <AdminComponent />
 * </AdminRoute>
 */
export const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user has admin role
  // TODO: Implement actual role checking when user model is available
  const isAdmin = user?.role === 'admin';

  if (!isAdmin) {
    // Redirect to unauthorized page or home
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

/**
 * GuestRoute Component
 * Guards routes that should only be accessible to non-authenticated users
 * (e.g., login, register pages)
 *
 * Usage:
 * <GuestRoute>
 *   <LoginPage />
 * </GuestRoute>
 */
export const GuestRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    // If already authenticated, redirect to home
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

/**
 * RoleBasedRoute Component
 * Guards routes based on specific roles
 *
 * Usage:
 * <RoleBasedRoute allowedRoles={['admin', 'editor']}>
 *   <EditorComponent />
 * </RoleBasedRoute>
 */
export const RoleBasedRoute: React.FC<{
  children: React.ReactNode;
  allowedRoles: string[];
}> = ({ children, allowedRoles }) => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user has one of the allowed roles
  // TODO: Implement actual role checking when user model is available
  const userRole = user?.role;
  const hasPermission = userRole && allowedRoles.includes(userRole);

  if (!hasPermission) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default {
  ProtectedRoute,
  AdminRoute,
  GuestRoute,
  RoleBasedRoute
};
