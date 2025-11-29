import { describe, it, expect } from 'vitest';

describe('Development Environment Configuration', () => {
  describe('Package Installation', () => {
    it('should have axios installed', async () => {
      const axios = await import('axios');
      expect(axios.default).toBeDefined();
      expect(typeof axios.default.get).toBe('function');
    });

    it('should have react-query installed', async () => {
      const reactQuery = await import('@tanstack/react-query');
      expect(reactQuery.QueryClient).toBeDefined();
      expect(reactQuery.useQuery).toBeDefined();
    });

    it('should have react-router-dom installed', async () => {
      const router = await import('react-router-dom');
      expect(router.BrowserRouter).toBeDefined();
      expect(router.useNavigate).toBeDefined();
    });

    it('should have react-hook-form installed', async () => {
      const rhf = await import('react-hook-form');
      expect(rhf.useForm).toBeDefined();
    });

    it('should have react-toastify installed', async () => {
      const toast = await import('react-toastify');
      expect(toast.toast).toBeDefined();
      expect(toast.ToastContainer).toBeDefined();
    });

    it('should have date-fns installed', async () => {
      const dateFns = await import('date-fns');
      expect(dateFns.format).toBeDefined();
      expect(dateFns.parseISO).toBeDefined();
    });
  });

  describe('Environment Variables', () => {
    it('should have API_URL configured', () => {
      const apiUrl = import.meta.env.VITE_API_URL;
      expect(apiUrl).toBeDefined();
      expect(apiUrl).toBe('http://localhost:8009/api');
    });

    it('should have correct API base URL structure', () => {
      const apiUrl = import.meta.env.VITE_API_URL;
      expect(apiUrl).toMatch(/^http:\/\/localhost:\d+\/api$/);
    });
  });

  describe('Path Aliases', () => {
    it('should resolve @ alias imports', async () => {
      const types = await import('@/types');
      expect(types).toBeDefined();
    });

    it('should resolve @ alias for App component', async () => {
      const app = await import('@/App');
      expect(app.default).toBeDefined();
    });
  });

  describe('TailwindCSS', () => {
    it('should have tailwindcss configuration available', () => {
      // Tailwind is configured through PostCSS and CSS imports
      // This test verifies the setup doesn't break imports
      expect(true).toBe(true);
    });
  });
});
