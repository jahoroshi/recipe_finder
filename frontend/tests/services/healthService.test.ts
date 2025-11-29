/**
 * Health Service Tests
 * Unit tests for health check API service
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { healthService } from '@/services/healthService';

// Mock axios client
const mockApiClient = {
  get: vi.fn(),
  defaults: {
    baseURL: 'http://localhost:8009/api',
  },
};

vi.mock('@/services/api.config', () => ({
  apiClient: mockApiClient,
}));

describe('Health Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('check', () => {
    it('should check basic health status', async () => {
      const mockResponse = {
        data: {
          status: 'healthy' as const,
          version: '1.0.0',
          service: 'Recipe Management API',
        },
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await healthService.check();

      expect(mockApiClient.get).toHaveBeenCalledWith('/health', {
        baseURL: 'http://localhost:8009',
      });
      expect(result.status).toBe('healthy');
      expect(result.version).toBe('1.0.0');
    });

    it('should handle unhealthy status', async () => {
      const mockResponse = {
        data: {
          status: 'unhealthy' as const,
          version: '1.0.0',
          service: 'Recipe Management API',
        },
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await healthService.check();

      expect(result.status).toBe('unhealthy');
    });
  });

  describe('checkDetailed', () => {
    it('should check detailed health status', async () => {
      const mockResponse = {
        data: {
          status: 'healthy' as const,
          version: '1.0.0',
          service: 'Recipe Management API',
          components: {
            redis: {
              status: 'healthy' as const,
              message: 'Connected',
            },
            database: {
              status: 'healthy' as const,
              message: 'Connection pool available',
            },
          },
        },
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await healthService.checkDetailed();

      expect(mockApiClient.get).toHaveBeenCalledWith('/health/detailed', {
        baseURL: 'http://localhost:8009',
      });
      expect(result.status).toBe('healthy');
      expect(result.components.redis.status).toBe('healthy');
      expect(result.components.database.status).toBe('healthy');
    });

    it('should handle degraded status', async () => {
      const mockResponse = {
        data: {
          status: 'degraded' as const,
          version: '1.0.0',
          service: 'Recipe Management API',
          components: {
            redis: {
              status: 'unhealthy' as const,
              message: 'Connection failed',
            },
            database: {
              status: 'healthy' as const,
              message: 'Connection pool available',
            },
          },
        },
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await healthService.checkDetailed();

      expect(result.status).toBe('degraded');
      expect(result.components.redis.status).toBe('unhealthy');
    });
  });

  describe('ping', () => {
    it('should ping the API', async () => {
      const mockResponse = {
        data: {
          status: 'healthy' as const,
          version: '1.0.0',
          service: 'Recipe Management API',
        },
      };

      mockApiClient.get.mockResolvedValueOnce(mockResponse);

      const result = await healthService.ping();

      expect(result.status).toBe('healthy');
    });
  });
});
