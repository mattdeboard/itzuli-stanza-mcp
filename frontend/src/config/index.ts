/**
 * Application configuration loaded from environment variables
 */
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

export const config = {
  useFixtures: process.env.VITE_USE_FIXTURES === 'true',
  apiBaseUrl: process.env.VITE_API_BASE_URL || '/api',
} as const