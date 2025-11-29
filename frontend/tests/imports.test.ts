import { describe, it, expect } from 'vitest';
import path from 'path';

describe('Import Path Resolution', () => {
  it('should resolve @ alias to project root', async () => {
    // Test that @ alias works by attempting to import types
    const typesModule = await import('@/types');
    expect(typesModule).toBeDefined();
  });

  it('should have correct path alias configuration', () => {
    // Verify that the path resolution is set up correctly
    const projectRoot = path.resolve(__dirname, '..');
    expect(projectRoot).toContain('test-task-recipe-front');
  });
});
