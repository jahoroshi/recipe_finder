/**
 * UI Context
 *
 * Provides global state management for UI-related states.
 * Manages loading states, error states, modals, and toasts.
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface LoadingState {
  [key: string]: boolean;
}

export interface ErrorState {
  message: string;
  title?: string;
  details?: string;
}

export interface ModalState {
  isOpen: boolean;
  type?: string;
  data?: any;
}

interface UIContextValue {
  // Loading States
  loadingStates: LoadingState;
  isLoading: (key: string) => boolean;
  setLoading: (key: string, isLoading: boolean) => void;
  clearLoading: (key: string) => void;
  clearAllLoading: () => void;

  // Error States
  error: ErrorState | null;
  setError: (error: ErrorState | string) => void;
  clearError: () => void;

  // Modal States
  modal: ModalState;
  openModal: (type: string, data?: any) => void;
  closeModal: () => void;

  // Sidebar/Navigation
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;

  // Mobile Filter Panel
  isMobileFilterOpen: boolean;
  toggleMobileFilter: () => void;
  setMobileFilterOpen: (isOpen: boolean) => void;

  // Confirmation Dialog
  confirmationDialog: {
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm?: () => void;
    onCancel?: () => void;
  };
  showConfirmation: (
    title: string,
    message: string,
    onConfirm?: () => void,
    onCancel?: () => void
  ) => void;
  closeConfirmation: () => void;
}

interface UIProviderProps {
  children: ReactNode;
}

// ============================================================================
// Default State
// ============================================================================

const defaultModalState: ModalState = {
  isOpen: false,
  type: undefined,
  data: undefined,
};

const defaultConfirmationDialog = {
  isOpen: false,
  title: '',
  message: '',
  onConfirm: undefined,
  onCancel: undefined,
};

// ============================================================================
// Context
// ============================================================================

const UIContext = createContext<UIContextValue | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

export const UIProvider: React.FC<UIProviderProps> = ({ children }) => {
  // ============================================================================
  // State
  // ============================================================================

  const [loadingStates, setLoadingStates] = useState<LoadingState>({});
  const [error, setErrorState] = useState<ErrorState | null>(null);
  const [modal, setModal] = useState<ModalState>(defaultModalState);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState<boolean>(false);
  const [confirmationDialog, setConfirmationDialog] = useState(defaultConfirmationDialog);

  // ============================================================================
  // Loading State Management
  // ============================================================================

  const isLoading = useCallback((key: string): boolean => {
    return loadingStates[key] === true;
  }, [loadingStates]);

  const setLoading = useCallback((key: string, loading: boolean) => {
    setLoadingStates((prev) => ({
      ...prev,
      [key]: loading,
    }));
  }, []);

  const clearLoading = useCallback((key: string) => {
    setLoadingStates((prev) => {
      const newState = { ...prev };
      delete newState[key];
      return newState;
    });
  }, []);

  const clearAllLoading = useCallback(() => {
    setLoadingStates({});
  }, []);

  // ============================================================================
  // Error State Management
  // ============================================================================

  const setError = useCallback((errorInput: ErrorState | string) => {
    if (typeof errorInput === 'string') {
      setErrorState({
        message: errorInput,
      });
    } else {
      setErrorState(errorInput);
    }
  }, []);

  const clearError = useCallback(() => {
    setErrorState(null);
  }, []);

  // ============================================================================
  // Modal Management
  // ============================================================================

  const openModal = useCallback((type: string, data?: any) => {
    setModal({
      isOpen: true,
      type,
      data,
    });
  }, []);

  const closeModal = useCallback(() => {
    setModal(defaultModalState);
  }, []);

  // ============================================================================
  // Sidebar Management
  // ============================================================================

  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen((prev) => !prev);
  }, []);

  const setSidebarOpen = useCallback((isOpen: boolean) => {
    setIsSidebarOpen(isOpen);
  }, []);

  // ============================================================================
  // Mobile Filter Management
  // ============================================================================

  const toggleMobileFilter = useCallback(() => {
    setIsMobileFilterOpen((prev) => !prev);
  }, []);

  const setMobileFilterOpen = useCallback((isOpen: boolean) => {
    setIsMobileFilterOpen(isOpen);
  }, []);

  // ============================================================================
  // Confirmation Dialog Management
  // ============================================================================

  const showConfirmation = useCallback(
    (
      title: string,
      message: string,
      onConfirm?: () => void,
      onCancel?: () => void
    ) => {
      setConfirmationDialog({
        isOpen: true,
        title,
        message,
        onConfirm,
        onCancel,
      });
    },
    []
  );

  const closeConfirmation = useCallback(() => {
    // Call onCancel if it exists before closing
    if (confirmationDialog.onCancel) {
      confirmationDialog.onCancel();
    }
    setConfirmationDialog(defaultConfirmationDialog);
  }, [confirmationDialog]);

  // ============================================================================
  // Context Value
  // ============================================================================

  const value: UIContextValue = {
    // Loading States
    loadingStates,
    isLoading,
    setLoading,
    clearLoading,
    clearAllLoading,

    // Error States
    error,
    setError,
    clearError,

    // Modal States
    modal,
    openModal,
    closeModal,

    // Sidebar/Navigation
    isSidebarOpen,
    toggleSidebar,
    setSidebarOpen,

    // Mobile Filter Panel
    isMobileFilterOpen,
    toggleMobileFilter,
    setMobileFilterOpen,

    // Confirmation Dialog
    confirmationDialog,
    showConfirmation,
    closeConfirmation,
  };

  return (
    <UIContext.Provider value={value}>
      {children}
    </UIContext.Provider>
  );
};

// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access UI context
 * @throws {Error} If used outside UIProvider
 */
export const useUIContext = (): UIContextValue => {
  const context = useContext(UIContext);

  if (context === undefined) {
    throw new Error('useUIContext must be used within UIProvider');
  }

  return context;
};

// Export context for testing purposes
export { UIContext };
