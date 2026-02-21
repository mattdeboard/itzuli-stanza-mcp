/**
 * API service for loading alignment data from backend or fixtures.
 * Designed to easily switch between fixture data and backend API.
 */

import type { AlignmentData, DataSourceConfig } from '../types/alignment'
import { config } from '../config'

/**
 * Default configuration loaded from environment variables
 */
const DEFAULT_CONFIG: DataSourceConfig = {
  useFixtures: config.useFixtures,
  apiBaseUrl: config.apiBaseUrl,
}

/**
 * Load alignment data from fixtures (JSON file)
 */
async function loadFixtureData(): Promise<AlignmentData> {
  const response = await fetch('/resources/fixtures.json')
  if (!response.ok) {
    throw new Error(`Failed to load fixture data: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Load alignment data from backend API
 * Matches the backend alignment server endpoints
 */
async function loadApiData(config: DataSourceConfig): Promise<AlignmentData> {
  const url = `${config.apiBaseUrl}/sentences`
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })
  
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`)
  }
  
  return response.json()
}

/**
 * Main function to fetch alignment data based on configuration
 */
export async function fetchAlignmentData(
  config: DataSourceConfig = DEFAULT_CONFIG
): Promise<AlignmentData> {
  if (config.useFixtures) {
    return loadFixtureData()
  } else {
    return loadApiData(config)
  }
}

/**
 * Get current data source configuration
 */
export function getDataSourceConfig(): DataSourceConfig {
  return DEFAULT_CONFIG
}

/**
 * Utility to create a configuration for API mode
 */
export function createApiConfig(apiBaseUrl: string = '/api'): DataSourceConfig {
  return {
    useFixtures: false,
    apiBaseUrl,
  }
}

/**
 * Utility to create a configuration for fixture mode
 */
export function createFixtureConfig(): DataSourceConfig {
  return {
    useFixtures: true,
  }
}