/**
 * Centralized Notification Service
 *
 * Provides consistent toast notifications across the application
 * with standardized messaging, timing, and retry functionality.
 */

import { toast, ToastOptions, ToastContent, Id } from 'react-toastify';

// ============================================================================
// Configuration
// ============================================================================

const DEFAULT_TOAST_CONFIG: ToastOptions = {
  position: 'top-right',
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
};

const SUCCESS_DURATION = 3000; // 3 seconds
const ERROR_DURATION = 5000; // 5 seconds
const INFO_DURATION = 4000; // 4 seconds
const WARNING_DURATION = 4000; // 4 seconds

// ============================================================================
// Toast Types
// ============================================================================

export interface NotificationOptions {
  duration?: number;
  onRetry?: () => void;
  retryLabel?: string;
  dismissible?: boolean;
}

// ============================================================================
// Core Notification Functions
// ============================================================================

/**
 * Display a success notification
 */
export const notifySuccess = (
  message: ToastContent,
  options?: NotificationOptions
): Id => {
  return toast.success(message, {
    ...DEFAULT_TOAST_CONFIG,
    autoClose: options?.duration ?? SUCCESS_DURATION,
    ...options,
  });
};

/**
 * Display an error notification with optional retry
 */
export const notifyError = (
  message: ToastContent,
  options?: NotificationOptions
): Id => {
  const toastContent = options?.onRetry ? (
    <div className="flex flex-col gap-2">
      <div>{message}</div>
      <button
        onClick={() => {
          options.onRetry?.();
          toast.dismiss();
        }}
        className="self-start text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded font-medium transition-colors"
      >
        {options.retryLabel || 'Try Again'}
      </button>
    </div>
  ) : (
    message
  );

  return toast.error(toastContent, {
    ...DEFAULT_TOAST_CONFIG,
    autoClose: options?.duration ?? ERROR_DURATION,
    closeButton: options?.dismissible !== false,
  });
};

/**
 * Display an info notification
 */
export const notifyInfo = (
  message: ToastContent,
  options?: NotificationOptions
): Id => {
  return toast.info(message, {
    ...DEFAULT_TOAST_CONFIG,
    autoClose: options?.duration ?? INFO_DURATION,
    ...options,
  });
};

/**
 * Display a warning notification
 */
export const notifyWarning = (
  message: ToastContent,
  options?: NotificationOptions
): Id => {
  return toast.warning(message, {
    ...DEFAULT_TOAST_CONFIG,
    autoClose: options?.duration ?? WARNING_DURATION,
    ...options,
  });
};

/**
 * Display a loading notification (promise-based)
 */
export const notifyLoading = (message: ToastContent): Id => {
  return toast.loading(message, {
    ...DEFAULT_TOAST_CONFIG,
    autoClose: false,
    closeButton: false,
  });
};

/**
 * Update an existing toast
 */
export const updateNotification = (
  toastId: Id,
  options: {
    type?: 'success' | 'error' | 'info' | 'warning';
    message?: ToastContent;
    autoClose?: number;
  }
): void => {
  toast.update(toastId, {
    render: options.message,
    type: options.type,
    isLoading: false,
    autoClose: options.autoClose ?? SUCCESS_DURATION,
    closeButton: true,
  });
};

/**
 * Dismiss a specific toast or all toasts
 */
export const dismissNotification = (toastId?: Id): void => {
  if (toastId) {
    toast.dismiss(toastId);
  } else {
    toast.dismiss();
  }
};

// ============================================================================
// Recipe-Specific Notifications
// ============================================================================

/**
 * Recipe CRUD notifications
 */
export const recipeNotifications = {
  created: (recipeName: string): Id =>
    notifySuccess(`Recipe "${recipeName}" created successfully!`),

  updated: (recipeName: string): Id =>
    notifySuccess(`Recipe "${recipeName}" updated successfully!`),

  deleted: (recipeName: string): Id =>
    notifySuccess(`Recipe "${recipeName}" deleted successfully!`),

  createFailed: (error: string, onRetry?: () => void): Id =>
    notifyError(`Failed to create recipe: ${error}`, {
      onRetry,
      retryLabel: 'Retry',
    }),

  updateFailed: (error: string, onRetry?: () => void): Id =>
    notifyError(`Failed to update recipe: ${error}`, {
      onRetry,
      retryLabel: 'Retry',
    }),

  deleteFailed: (error: string, onRetry?: () => void): Id =>
    notifyError(`Failed to delete recipe: ${error}`, {
      onRetry,
      retryLabel: 'Retry',
    }),

  notFound: (): Id =>
    notifyError('Recipe not found. It may have been deleted.', {
      duration: 4000,
    }),
};

/**
 * Bulk import notifications
 */
export const importNotifications = {
  started: (totalRecipes: number, jobId: string): Id =>
    notifyInfo(
      `Bulk import started! Processing ${totalRecipes} recipe(s). Job ID: ${jobId}`,
      { duration: 6000 }
    ),

  success: (fileName: string): Id =>
    notifySuccess(`Successfully imported recipes from ${fileName}`),

  failed: (error: string, onRetry?: () => void): Id =>
    notifyError(`Failed to import recipes: ${error}`, {
      onRetry,
      retryLabel: 'Try Again',
      duration: 6000,
    }),

  invalidFile: (): Id =>
    notifyWarning('Please upload a valid JSON file', { duration: 4000 }),

  processing: (): Id =>
    notifyLoading('Importing recipes... This may take a moment.'),
};

/**
 * Search notifications
 */
export const searchNotifications = {
  noResults: (query: string): Id =>
    notifyInfo(`No recipes found for "${query}". Try a different search.`, {
      duration: 4000,
    }),

  failed: (error: string): Id =>
    notifyError(`Search failed: ${error}`, { duration: 5000 }),

  tooShort: (): Id =>
    notifyWarning('Search query too short. Please enter at least 2 characters.', {
      duration: 3000,
    }),
};

/**
 * Network notifications
 */
export const networkNotifications = {
  offline: (): Id =>
    notifyError('You are offline. Please check your internet connection.', {
      dismissible: false,
      duration: false as any, // Keep visible until dismissed
    }),

  reconnected: (): Id =>
    notifySuccess('Connection restored!', { duration: 2000 }),

  timeout: (onRetry?: () => void): Id =>
    notifyError('Request timed out. Please try again.', {
      onRetry,
      retryLabel: 'Retry',
    }),

  serverError: (): Id =>
    notifyError('Server error. Please try again later.', { duration: 5000 }),
};

/**
 * Form validation notifications
 */
export const validationNotifications = {
  required: (fieldName: string): Id =>
    notifyWarning(`${fieldName} is required.`, { duration: 3000 }),

  invalid: (fieldName: string, reason?: string): Id =>
    notifyWarning(
      `Invalid ${fieldName}${reason ? `: ${reason}` : '.'}`,
      { duration: 3000 }
    ),

  success: (): Id =>
    notifySuccess('Form submitted successfully!', { duration: 2000 }),
};

/**
 * Generic async operation with toast notifications
 */
export const notifyPromise = async <T,>(
  promise: Promise<T>,
  messages: {
    pending: string;
    success: string | ((data: T) => string);
    error: string | ((error: any) => string);
  }
): Promise<T> => {
  return toast.promise(
    promise,
    {
      pending: messages.pending,
      success: {
        render({ data }) {
          return typeof messages.success === 'function'
            ? messages.success(data as T)
            : messages.success;
        },
      },
      error: {
        render({ data }) {
          return typeof messages.error === 'function'
            ? messages.error(data)
            : messages.error;
        },
      },
    },
    DEFAULT_TOAST_CONFIG
  );
};
