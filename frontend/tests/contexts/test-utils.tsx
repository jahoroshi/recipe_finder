/**
 * Test Utilities for Context Testing
 *
 * Provides helper functions and wrappers for testing React contexts.
 */

import React, { ReactNode } from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

/**
 * Create a fresh QueryClient for each test to avoid state pollution
 */
export const createTestQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
    logger: {
      log: console.log,
      warn: console.warn,
      error: () => {}, // Suppress error logs in tests
    },
  });
};

/**
 * Wrapper component that provides QueryClient context
 */
export const createQueryWrapper = (queryClient?: QueryClient) => {
  const client = queryClient || createTestQueryClient();

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>
      {children}
    </QueryClientProvider>
  );
};

/**
 * Mock localStorage for testing
 */
export const mockLocalStorage = () => {
  const store: { [key: string]: string } = {};

  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: vi.fn((index: number) => {
      const keys = Object.keys(store);
      return keys[index] || null;
    }),
  };
};

/**
 * Wait for async operations to complete
 */
export const waitForAsync = () => {
  return new Promise((resolve) => setTimeout(resolve, 0));
};
