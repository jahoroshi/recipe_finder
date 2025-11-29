/**
 * API Configuration
 * Centralized axios instance with interceptors for error handling
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { config } from '@/config/env';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public data?: any,
    public requestId?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Create and configure axios instance
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: config.apiUrl,
    timeout: 30000, // 30 second timeout for AI operations
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  /**
   * Request interceptor
   * - Logs requests in development
   * - Adds authorization headers (future auth support)
   * - Adds request timestamp
   */
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Log request in development
      if (import.meta.env.DEV) {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          params: config.params,
          data: config.data,
        });
      }

      // Add request timestamp for performance monitoring
      config.headers['X-Request-Start'] = Date.now().toString();

      // Future: Add authorization token
      // const token = getAuthToken();
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`;
      // }

      return config;
    },
    (error: AxiosError) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  /**
   * Response interceptor
   * - Logs responses in development
   * - Handles common error scenarios
   * - Extracts error messages from API responses
   */
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Calculate and log response time in development
      if (import.meta.env.DEV) {
        const requestStart = response.config.headers['X-Request-Start'] as string;
        const duration = requestStart ? Date.now() - parseInt(requestStart) : 0;
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
          status: response.status,
          duration: `${duration}ms`,
          requestId: response.headers['x-request-id'],
        });
      }

      return response;
    },
    (error: AxiosError<any>) => {
      // Extract request ID for debugging
      const requestId = error.response?.headers['x-request-id'];

      // Handle different error scenarios
      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;
        const message = data?.message || data?.detail || getDefaultErrorMessage(status);

        console.error(`[API Error] ${status}:`, {
          message,
          requestId,
          url: error.config?.url,
          data: data,
        });

        // Throw custom API error
        throw new ApiError(message, status, data, requestId);
      } else if (error.request) {
        // Request made but no response received (network error)
        console.error('[API Network Error]', {
          message: error.message,
          url: error.config?.url,
        });

        throw new ApiError(
          'Network error. Please check your connection and try again.',
          undefined,
          undefined,
          requestId
        );
      } else {
        // Error in request configuration
        console.error('[API Configuration Error]', error.message);
        throw new ApiError(
          `Request configuration error: ${error.message}`,
          undefined,
          undefined,
          requestId
        );
      }
    }
  );

  return client;
};

/**
 * Get default error message based on status code
 */
function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return 'Invalid request. Please check your input.';
    case 401:
      return 'Unauthorized. Please log in.';
    case 403:
      return 'Forbidden. You do not have permission to perform this action.';
    case 404:
      return 'Resource not found.';
    case 409:
      return 'Conflict. This resource already exists.';
    case 422:
      return 'Validation error. Please check your input.';
    case 429:
      return 'Too many requests. Please try again later.';
    case 500:
      return 'Internal server error. Please try again later.';
    case 502:
      return 'Bad gateway. The server is temporarily unavailable.';
    case 503:
      return 'Service unavailable. Please try again later.';
    case 504:
      return 'Gateway timeout. The request took too long to process.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Singleton axios instance
 */
export const apiClient = createApiClient();

/**
 * Type-safe API request wrapper
 * Simplifies making API calls with TypeScript
 */
export const api = {
  /**
   * GET request
   */
  get: <T = any>(url: string, config?: any) => {
    return apiClient.get<T>(url, config).then((res) => res.data);
  },

  /**
   * POST request
   */
  post: <T = any>(url: string, data?: any, config?: any) => {
    return apiClient.post<T>(url, data, config).then((res) => res.data);
  },

  /**
   * PUT request
   */
  put: <T = any>(url: string, data?: any, config?: any) => {
    return apiClient.put<T>(url, data, config).then((res) => res.data);
  },

  /**
   * PATCH request
   */
  patch: <T = any>(url: string, data?: any, config?: any) => {
    return apiClient.patch<T>(url, data, config).then((res) => res.data);
  },

  /**
   * DELETE request
   */
  delete: <T = any>(url: string, config?: any) => {
    return apiClient.delete<T>(url, config).then((res) => res.data);
  },
};

/**
 * Export types for use in service files
 */
export type { AxiosRequestConfig, AxiosResponse } from 'axios';
