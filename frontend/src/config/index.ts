/**
 * Application configuration loaded from environment variables
 * 
 * Vite automatically loads VITE_ prefixed environment variables
 * and makes them available via import.meta.env
 */

export const config = {
  useFixtures: import.meta.env.VITE_USE_FIXTURES === 'true',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
} as const
