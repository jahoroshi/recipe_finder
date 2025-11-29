/**
 * Basic setup verification tests
 * Tests environment configuration and import paths
 */

import { config, validateEnv } from '@/config/env';

describe('Environment Setup', () => {
  test('should load environment variables', () => {
    expect(config.apiUrl).toBeDefined();
    expect(config.apiUrl).toContain('http://localhost:8009/api');
  });

  test('should validate environment without errors', () => {
    expect(() => validateEnv()).not.toThrow();
  });

  test('should have correct environment flags', () => {
    expect(typeof config.isDevelopment).toBe('boolean');
    expect(typeof config.isProduction).toBe('boolean');
  });
});

describe('Import Paths', () => {
  test('should resolve @ alias correctly', () => {
    // If this test file compiles, the @ alias is working
    expect(config).toBeDefined();
  });
});
