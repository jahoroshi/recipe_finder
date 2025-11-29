/**
 * UIContext Tests
 *
 * Unit tests for UIContext provider and hook.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { UIProvider, useUIContext } from '@/contexts/UIContext';
import type { ErrorState } from '@/contexts/UIContext';

// ============================================================================
// Tests
// ============================================================================

describe('UIContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ============================================================================
  // Hook Tests
  // ============================================================================

  describe('useUIContext hook', () => {
    it('should throw error when used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useUIContext());
      }).toThrow('useUIContext must be used within UIProvider');

      consoleSpy.mockRestore();
    });

    it('should provide context value when used inside provider', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      expect(result.current).toHaveProperty('loadingStates');
      expect(result.current).toHaveProperty('error');
      expect(result.current).toHaveProperty('modal');
      expect(result.current).toHaveProperty('isSidebarOpen');
      expect(result.current).toHaveProperty('isMobileFilterOpen');
      expect(result.current).toHaveProperty('confirmationDialog');
    });

    it('should initialize with default state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      expect(result.current.loadingStates).toEqual({});
      expect(result.current.error).toBeNull();
      expect(result.current.modal).toEqual({
        isOpen: false,
        type: undefined,
        data: undefined,
      });
      expect(result.current.isSidebarOpen).toBe(false);
      expect(result.current.isMobileFilterOpen).toBe(false);
      expect(result.current.confirmationDialog.isOpen).toBe(false);
    });
  });

  // ============================================================================
  // Loading State Tests
  // ============================================================================

  describe('loading state management', () => {
    it('should set loading state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setLoading('fetchRecipes', true);
      });

      expect(result.current.isLoading('fetchRecipes')).toBe(true);
      expect(result.current.loadingStates.fetchRecipes).toBe(true);
    });

    it('should handle multiple loading states', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setLoading('fetchRecipes', true);
        result.current.setLoading('createRecipe', true);
      });

      expect(result.current.isLoading('fetchRecipes')).toBe(true);
      expect(result.current.isLoading('createRecipe')).toBe(true);
    });

    it('should clear specific loading state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setLoading('fetchRecipes', true);
        result.current.setLoading('createRecipe', true);
      });

      act(() => {
        result.current.clearLoading('fetchRecipes');
      });

      expect(result.current.isLoading('fetchRecipes')).toBe(false);
      expect(result.current.isLoading('createRecipe')).toBe(true);
    });

    it('should clear all loading states', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setLoading('fetchRecipes', true);
        result.current.setLoading('createRecipe', true);
        result.current.setLoading('deleteRecipe', true);
      });

      act(() => {
        result.current.clearAllLoading();
      });

      expect(result.current.loadingStates).toEqual({});
      expect(result.current.isLoading('fetchRecipes')).toBe(false);
      expect(result.current.isLoading('createRecipe')).toBe(false);
      expect(result.current.isLoading('deleteRecipe')).toBe(false);
    });

    it('should return false for non-existent loading state', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      expect(result.current.isLoading('nonExistent')).toBe(false);
    });
  });

  // ============================================================================
  // Error State Tests
  // ============================================================================

  describe('error state management', () => {
    it('should set error with string', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setError('Something went wrong');
      });

      expect(result.current.error).toEqual({
        message: 'Something went wrong',
      });
    });

    it('should set error with ErrorState object', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      const errorState: ErrorState = {
        message: 'Failed to load',
        title: 'Error',
        details: 'Network timeout',
      };

      act(() => {
        result.current.setError(errorState);
      });

      expect(result.current.error).toEqual(errorState);
    });

    it('should clear error', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setError('Something went wrong');
      });

      expect(result.current.error).not.toBeNull();

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  // ============================================================================
  // Modal State Tests
  // ============================================================================

  describe('modal management', () => {
    it('should open modal', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.openModal('createRecipe');
      });

      expect(result.current.modal).toEqual({
        isOpen: true,
        type: 'createRecipe',
        data: undefined,
      });
    });

    it('should open modal with data', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      const modalData = { recipeId: '123' };

      act(() => {
        result.current.openModal('editRecipe', modalData);
      });

      expect(result.current.modal).toEqual({
        isOpen: true,
        type: 'editRecipe',
        data: modalData,
      });
    });

    it('should close modal', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.openModal('createRecipe', { test: 'data' });
      });

      expect(result.current.modal.isOpen).toBe(true);

      act(() => {
        result.current.closeModal();
      });

      expect(result.current.modal).toEqual({
        isOpen: false,
        type: undefined,
        data: undefined,
      });
    });
  });

  // ============================================================================
  // Sidebar Tests
  // ============================================================================

  describe('sidebar management', () => {
    it('should toggle sidebar', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      expect(result.current.isSidebarOpen).toBe(false);

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.isSidebarOpen).toBe(true);

      act(() => {
        result.current.toggleSidebar();
      });

      expect(result.current.isSidebarOpen).toBe(false);
    });

    it('should set sidebar state directly', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setSidebarOpen(true);
      });

      expect(result.current.isSidebarOpen).toBe(true);

      act(() => {
        result.current.setSidebarOpen(false);
      });

      expect(result.current.isSidebarOpen).toBe(false);
    });
  });

  // ============================================================================
  // Mobile Filter Tests
  // ============================================================================

  describe('mobile filter management', () => {
    it('should toggle mobile filter', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      expect(result.current.isMobileFilterOpen).toBe(false);

      act(() => {
        result.current.toggleMobileFilter();
      });

      expect(result.current.isMobileFilterOpen).toBe(true);

      act(() => {
        result.current.toggleMobileFilter();
      });

      expect(result.current.isMobileFilterOpen).toBe(false);
    });

    it('should set mobile filter state directly', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.setMobileFilterOpen(true);
      });

      expect(result.current.isMobileFilterOpen).toBe(true);

      act(() => {
        result.current.setMobileFilterOpen(false);
      });

      expect(result.current.isMobileFilterOpen).toBe(false);
    });
  });

  // ============================================================================
  // Confirmation Dialog Tests
  // ============================================================================

  describe('confirmation dialog management', () => {
    it('should show confirmation dialog', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.showConfirmation('Delete Recipe', 'Are you sure?');
      });

      expect(result.current.confirmationDialog).toEqual({
        isOpen: true,
        title: 'Delete Recipe',
        message: 'Are you sure?',
        onConfirm: undefined,
        onCancel: undefined,
      });
    });

    it('should show confirmation with callbacks', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      const onConfirm = vi.fn();
      const onCancel = vi.fn();

      act(() => {
        result.current.showConfirmation(
          'Delete Recipe',
          'Are you sure?',
          onConfirm,
          onCancel
        );
      });

      expect(result.current.confirmationDialog.isOpen).toBe(true);
      expect(result.current.confirmationDialog.onConfirm).toBe(onConfirm);
      expect(result.current.confirmationDialog.onCancel).toBe(onCancel);
    });

    it('should close confirmation dialog', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.showConfirmation('Delete Recipe', 'Are you sure?');
      });

      expect(result.current.confirmationDialog.isOpen).toBe(true);

      act(() => {
        result.current.closeConfirmation();
      });

      expect(result.current.confirmationDialog.isOpen).toBe(false);
      expect(result.current.confirmationDialog.title).toBe('');
      expect(result.current.confirmationDialog.message).toBe('');
    });

    it('should call onCancel when closing confirmation', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      const onCancel = vi.fn();

      act(() => {
        result.current.showConfirmation('Delete Recipe', 'Are you sure?', undefined, onCancel);
      });

      act(() => {
        result.current.closeConfirmation();
      });

      expect(onCancel).toHaveBeenCalled();
    });

    it('should not throw when closing without onCancel', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <UIProvider>{children}</UIProvider>
      );

      const { result } = renderHook(() => useUIContext(), { wrapper });

      act(() => {
        result.current.showConfirmation('Delete Recipe', 'Are you sure?');
      });

      expect(() => {
        act(() => {
          result.current.closeConfirmation();
        });
      }).not.toThrow();
    });
  });
});
