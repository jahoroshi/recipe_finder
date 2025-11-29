import { describe, it, expect } from 'vitest';

describe('Environment Configuration', () => {
  it('should have VITE_API_URL environment variable configured', () => {
    // In Vite, environment variables are accessed via import.meta.env
    // During tests, we need to check the process.env fallback
    const apiUrl = import.meta.env.VITE_API_URL || process.env.VITE_API_URL;
    expect(apiUrl).toBeDefined();
    expect(apiUrl).toBe('http://localhost:8009/api');
  });

  it('should have correct API base URL format', () => {
    const apiUrl = import.meta.env.VITE_API_URL || process.env.VITE_API_URL;
    expect(apiUrl).toMatch(/^http:\/\/localhost:8009\/api$/);
  });
});
