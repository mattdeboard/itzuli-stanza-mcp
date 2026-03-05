/**
 * Hook for managing translation requests to the backend
 */

import { useCallback, useState } from 'react'
import {
  type AlignmentData,
  type LanguageCode,
  TranslationRequestSchema,
} from '../schemas/validation'
import { type AnalysisRequest, type LoadingStage, submitTranslationRequest } from '../services/alignmentApi'

export type LastRequest = {
  text: string
  sourceLang: LanguageCode
  targetLang: LanguageCode
} | null

export type UseTranslationRequestResult = {
  data: AlignmentData | null
  loading: boolean
  loadingStage: LoadingStage | null
  error: string | null
  lastRequest: LastRequest
  submitRequest: (text: string, sourceLang: LanguageCode, targetLang: LanguageCode) => Promise<void>
  reset: () => void
  clearError: () => void
}

/**
 * Hook for submitting translation requests and managing their state
 */
export function useTranslationRequest(): UseTranslationRequestResult {
  const [data, setData] = useState<AlignmentData | null>(null)
  const [loading, setLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState<LoadingStage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastRequest, setLastRequest] = useState<LastRequest>(null)

  const submitRequest = useCallback(
    async (text: string, sourceLang: LanguageCode, targetLang: LanguageCode) => {
      // Store the request parameters for potential retry
      setLastRequest({ text, sourceLang, targetLang })

      try {
        setLoading(true)
        setLoadingStage('itzuli')
        setError(null)

        // Validate request with Zod before proceeding
        const validationResult = TranslationRequestSchema.safeParse({
          text,
          source_language: sourceLang,
          target_language: targetLang,
        })

        if (!validationResult.success) {
          const errorMessage = validationResult.error.issues
            .map((issue) => issue.message)
            .join(', ')
          throw new Error(`Validation failed: ${errorMessage}`)
        }

        const request: AnalysisRequest = {
          text,
          source_lang: sourceLang,
          target_lang: targetLang,
          sentence_id: crypto.randomUUID(),
        }

        const result = await submitTranslationRequest(request, setLoadingStage)
        setData(result)
        // Clear error and lastRequest on successful request
        setError(null)
        setLastRequest(null)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to analyze translation'
        setError(errorMessage)
        console.error('Translation request failed:', err)
      } finally {
        setLoading(false)
        setLoadingStage(null)
      }
    },
    []
  )

  const reset = useCallback(() => {
    setData(null)
    setError(null)
    setLoading(false)
    setLoadingStage(null)
    setLastRequest(null)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    data,
    loading,
    loadingStage,
    error,
    lastRequest,
    submitRequest,
    reset,
    clearError,
  }
}
