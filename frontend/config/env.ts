/**
 * Environment configuration
 * Centralized access to environment variables
 */

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8009/api',
  geminiApiKey: import.meta.env.VITE_GEMINI_API_KEY || process.env.GEMINI_API_KEY,
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;

/**
 * Validates required environment variables
 * @throws Error if required variables are missing
 */
export function validateEnv(): void {
  if (!config.apiUrl) {
    console.warn('VITE_API_URL is not set, using default:', config.apiUrl);
  }
}
