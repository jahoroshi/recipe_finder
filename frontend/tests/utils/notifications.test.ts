/**
 * Notification Service Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { toast } from 'react-toastify';
import {
  notifySuccess,
  notifyError,
  notifyInfo,
  notifyWarning,
  notifyLoading,
  updateNotification,
  dismissNotification,
  recipeNotifications,
  importNotifications,
  searchNotifications,
  networkNotifications,
  validationNotifications,
  notifyPromise,
} from '@/utils/notifications';

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    loading: vi.fn(),
    update: vi.fn(),
    dismiss: vi.fn(),
    promise: vi.fn(),
  },
}));

describe('Notification Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Core Notification Functions', () => {
    it('should display success notification', () => {
      const message = 'Operation successful!';
      notifySuccess(message);

      expect(toast.success).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          position: 'top-right',
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        })
      );
    });

    it('should display success notification with custom duration', () => {
      const message = 'Quick success!';
      notifySuccess(message, { duration: 1000 });

      expect(toast.success).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: 1000,
        })
      );
    });

    it('should display error notification', () => {
      const message = 'Operation failed!';
      notifyError(message);

      expect(toast.error).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          position: 'top-right',
          autoClose: 5000,
          closeButton: true,
        })
      );
    });

    it('should display error notification with retry option', () => {
      const message = 'Operation failed!';
      const onRetry = vi.fn();
      notifyError(message, { onRetry, retryLabel: 'Try Again' });

      expect(toast.error).toHaveBeenCalled();
      const callArgs = (toast.error as any).mock.calls[0];
      expect(callArgs[0]).toBeDefined();
    });

    it('should display info notification', () => {
      const message = 'Information message';
      notifyInfo(message);

      expect(toast.info).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: 4000,
        })
      );
    });

    it('should display warning notification', () => {
      const message = 'Warning message';
      notifyWarning(message);

      expect(toast.warning).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: 4000,
        })
      );
    });

    it('should display loading notification', () => {
      const message = 'Loading...';
      notifyLoading(message);

      expect(toast.loading).toHaveBeenCalledWith(
        message,
        expect.objectContaining({
          autoClose: false,
          closeButton: false,
        })
      );
    });

    it('should update an existing notification', () => {
      const toastId = 'test-toast-id';
      updateNotification(toastId, {
        type: 'success',
        message: 'Updated message',
        autoClose: 2000,
      });

      expect(toast.update).toHaveBeenCalledWith(
        toastId,
        expect.objectContaining({
          render: 'Updated message',
          type: 'success',
          isLoading: false,
          autoClose: 2000,
          closeButton: true,
        })
      );
    });

    it('should dismiss specific notification', () => {
      const toastId = 'test-toast-id';
      dismissNotification(toastId);

      expect(toast.dismiss).toHaveBeenCalledWith(toastId);
    });

    it('should dismiss all notifications when no ID provided', () => {
      dismissNotification();

      expect(toast.dismiss).toHaveBeenCalledWith();
    });
  });

  describe('Recipe Notifications', () => {
    it('should show recipe created notification', () => {
      recipeNotifications.created('Pasta Carbonara');

      expect(toast.success).toHaveBeenCalledWith(
        'Recipe "Pasta Carbonara" created successfully!',
        expect.any(Object)
      );
    });

    it('should show recipe updated notification', () => {
      recipeNotifications.updated('Pasta Carbonara');

      expect(toast.success).toHaveBeenCalledWith(
        'Recipe "Pasta Carbonara" updated successfully!',
        expect.any(Object)
      );
    });

    it('should show recipe deleted notification', () => {
      recipeNotifications.deleted('Pasta Carbonara');

      expect(toast.success).toHaveBeenCalledWith(
        'Recipe "Pasta Carbonara" deleted successfully!',
        expect.any(Object)
      );
    });

    it('should show recipe create failed notification', () => {
      const onRetry = vi.fn();
      recipeNotifications.createFailed('Validation error', onRetry);

      expect(toast.error).toHaveBeenCalled();
    });

    it('should show recipe not found notification', () => {
      recipeNotifications.notFound();

      expect(toast.error).toHaveBeenCalledWith(
        'Recipe not found. It may have been deleted.',
        expect.objectContaining({
          autoClose: 4000,
        })
      );
    });
  });

  describe('Import Notifications', () => {
    it('should show import started notification', () => {
      importNotifications.started(10, 'job-123');

      expect(toast.info).toHaveBeenCalledWith(
        'Bulk import started! Processing 10 recipe(s). Job ID: job-123',
        expect.objectContaining({
          duration: 6000,
        })
      );
    });

    it('should show import success notification', () => {
      importNotifications.success('recipes.json');

      expect(toast.success).toHaveBeenCalledWith(
        'Successfully imported recipes from recipes.json',
        expect.any(Object)
      );
    });

    it('should show import failed notification with retry', () => {
      const onRetry = vi.fn();
      importNotifications.failed('Invalid JSON format', onRetry);

      expect(toast.error).toHaveBeenCalled();
    });

    it('should show invalid file notification', () => {
      importNotifications.invalidFile();

      expect(toast.warning).toHaveBeenCalledWith(
        'Please upload a valid JSON file',
        expect.objectContaining({
          duration: 4000,
        })
      );
    });

    it('should show processing notification', () => {
      importNotifications.processing();

      expect(toast.loading).toHaveBeenCalledWith(
        'Importing recipes... This may take a moment.',
        expect.any(Object)
      );
    });
  });

  describe('Search Notifications', () => {
    it('should show no results notification', () => {
      searchNotifications.noResults('pasta');

      expect(toast.info).toHaveBeenCalledWith(
        'No recipes found for "pasta". Try a different search.',
        expect.objectContaining({
          duration: 4000,
        })
      );
    });

    it('should show search failed notification', () => {
      searchNotifications.failed('Network error');

      expect(toast.error).toHaveBeenCalledWith(
        'Search failed: Network error',
        expect.objectContaining({
          autoClose: 5000,
        })
      );
    });

    it('should show query too short notification', () => {
      searchNotifications.tooShort();

      expect(toast.warning).toHaveBeenCalledWith(
        'Search query too short. Please enter at least 2 characters.',
        expect.objectContaining({
          duration: 3000,
        })
      );
    });
  });

  describe('Network Notifications', () => {
    it('should show offline notification', () => {
      networkNotifications.offline();

      expect(toast.error).toHaveBeenCalled();
    });

    it('should show reconnected notification', () => {
      networkNotifications.reconnected();

      expect(toast.success).toHaveBeenCalledWith(
        'Connection restored!',
        expect.objectContaining({
          duration: 2000,
        })
      );
    });

    it('should show timeout notification with retry', () => {
      const onRetry = vi.fn();
      networkNotifications.timeout(onRetry);

      expect(toast.error).toHaveBeenCalled();
    });

    it('should show server error notification', () => {
      networkNotifications.serverError();

      expect(toast.error).toHaveBeenCalledWith(
        'Server error. Please try again later.',
        expect.objectContaining({
          autoClose: 5000,
        })
      );
    });
  });

  describe('Validation Notifications', () => {
    it('should show required field notification', () => {
      validationNotifications.required('Recipe Name');

      expect(toast.warning).toHaveBeenCalledWith(
        'Recipe Name is required.',
        expect.objectContaining({
          duration: 3000,
        })
      );
    });

    it('should show invalid field notification', () => {
      validationNotifications.invalid('Email', 'must be a valid email address');

      expect(toast.warning).toHaveBeenCalledWith(
        'Invalid Email: must be a valid email address',
        expect.objectContaining({
          duration: 3000,
        })
      );
    });

    it('should show form success notification', () => {
      validationNotifications.success();

      expect(toast.success).toHaveBeenCalledWith(
        'Form submitted successfully!',
        expect.objectContaining({
          duration: 2000,
        })
      );
    });
  });

  describe('Promise Notifications', () => {
    it('should handle promise with success', async () => {
      const successPromise = Promise.resolve('Success data');
      const messages = {
        pending: 'Processing...',
        success: 'Done!',
        error: 'Failed!',
      };

      await notifyPromise(successPromise, messages);

      expect(toast.promise).toHaveBeenCalledWith(
        successPromise,
        expect.objectContaining({
          pending: 'Processing...',
          success: expect.any(Object),
          error: expect.any(Object),
        }),
        expect.any(Object)
      );
    });

    it('should handle promise with function messages', async () => {
      const successPromise = Promise.resolve({ count: 5 });
      const messages = {
        pending: 'Processing...',
        success: (data: any) => `Processed ${data.count} items`,
        error: (error: any) => `Error: ${error.message}`,
      };

      await notifyPromise(successPromise, messages);

      expect(toast.promise).toHaveBeenCalled();
    });
  });
});
