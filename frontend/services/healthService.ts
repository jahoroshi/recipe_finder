/**
 * Health Service
 * API calls for health check endpoints
 */

import { api } from './api.config';
import type { HealthResponse, DetailedHealthResponse } from '@/types';

/**
 * Health Service
 * System health monitoring endpoints
 */
export const healthService = {
  /**
   * Basic health check
   * GET /health
   *
   * Quick check to verify API is running.
   * Does not check dependent services.
   *
   * @returns Basic health status
   *
   * @example
   * ```ts
   * const health = await healthService.check();
   * if (health.status === 'healthy') {
   *   console.log('API is running');
   * }
   * ```
   */
  check: async (): Promise<HealthResponse> => {
    // Note: Health endpoint is at root level, not under /api
    // We need to use axios directly with the correct base URL
    const { apiClient } = await import('./api.config');
    const baseUrl = apiClient.defaults.baseURL?.replace('/api', '') || 'http://localhost:8009';
    const response = await apiClient.get<HealthResponse>('/health', {
      baseURL: baseUrl,
    });
    return response.data;
  },

  /**
   * Detailed health check
   * GET /health/detailed
   *
   * Comprehensive check of all system components:
   * - Database connection
   * - Redis cache
   * - Any other configured services
   *
   * @returns Detailed health status with component breakdown
   *
   * @example
   * ```ts
   * const health = await healthService.checkDetailed();
   * console.log('Overall status:', health.status);
   * console.log('Database:', health.components.database.status);
   * console.log('Redis:', health.components.redis.status);
   * ```
   */
  checkDetailed: async (): Promise<DetailedHealthResponse> => {
    // Note: Health endpoint is at root level, not under /api
    const { apiClient } = await import('./api.config');
    const baseUrl = apiClient.defaults.baseURL?.replace('/api', '') || 'http://localhost:8009';
    const response = await apiClient.get<DetailedHealthResponse>('/health/detailed', {
      baseURL: baseUrl,
    });
    return response.data;
  },

  /**
   * Ping - Simple connectivity check
   * Alias for basic health check
   *
   * @returns Basic health status
   */
  ping: async (): Promise<HealthResponse> => {
    return healthService.check();
  },
};

/**
 * Export individual functions for tree-shaking
 */
export const {
  check: checkHealth,
  checkDetailed: checkDetailedHealth,
  ping: pingApi,
} = healthService;
