/**
 * React hook for loading alignment data with proper state management
 */

import { useState, useEffect, useCallback } from 'react'
import type { UseAlignmentDataResult, DataSourceConfig } from '../types/alignment'
import { fetchAlignmentData, getDataSourceConfig } from '../services/alignmentApi'

/**
 * Hook for loading alignment data with loading states and error handling
 * Abstracts whether data comes from fixtures or API
 */
export function useAlignmentData(config?: DataSourceConfig): UseAlignmentDataResult {
  const [data, setData] = useState<UseAlignmentDataResult['data']>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const effectiveConfig = config ?? getDataSourceConfig()

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await fetchAlignmentData(effectiveConfig)
      setData(result)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load alignment data'
      setError(errorMessage)
      console.error('Error loading alignment data:', err)
    } finally {
      setLoading(false)
    }
  }, [effectiveConfig])

  const refetch = useCallback(() => {
    loadData()
  }, [loadData])

  useEffect(() => {
    loadData()
  }, [loadData])

  return {
    data,
    loading,
    error,
    refetch,
  }
}

/**
 * Hook for managing selected sentence pair
 */
export function useSelectedSentence(initialId?: string) {
  const [selectedId, setSelectedId] = useState<string | null>(initialId ?? null)

  const { data, loading, error, refetch } = useAlignmentData()

  const selectedSentence = data?.sentences.find(s => s.id === selectedId) ?? null
  const availableSentences = data?.sentences ?? []

  // Auto-select first sentence if none selected and data is available
  useEffect(() => {
    if (!selectedId && availableSentences.length > 0) {
      setSelectedId(availableSentences[0].id)
    }
  }, [selectedId, availableSentences])

  return {
    selectedSentence,
    selectedId,
    setSelectedId,
    availableSentences,
    loading,
    error,
    refetch,
  }
}