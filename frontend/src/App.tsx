import classNames from 'classnames'
import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useState, useTransition } from 'react'
import { AlignmentVisualizer } from './components/AlignmentVisualizer'
import { CompactHeader } from './components/CompactHeader'
import { FullHeader } from './components/FullHeader'
import { LoadingIndicator } from './components/LoadingIndicator'
import { TranslationInput } from './components/TranslationInput'
import { TryAgainButton } from './components/TryAgainButton'
import { useSelectedSentence } from './hooks/useAlignmentData'
import { useTranslationRequest } from './hooks/useTranslationRequest'
import { useI18n } from './i18n'
import type { LanguageCode } from './types/alignment'

function App() {
  const { t } = useI18n()
  const [mode, setMode] = useState<'input' | 'examples'>('input')
  const [, startTransition] = useTransition()

  const {
    selectedSentence,
    selectedId,
    setSelectedId,
    availableSentences,
    loading: fixtureLoading,
    error: fixtureError,
  } = useSelectedSentence()

  const {
    data: translationData,
    loading: translationLoading,
    loadingStage,
    error: translationError,
    lastRequest,
    submitRequest,
    reset,
    clearError,
  } = useTranslationRequest()

  const currentData = mode === 'input' && translationData ? translationData : null
  const currentSentence =
    currentData?.sentences[0] || (mode === 'examples' ? selectedSentence : null)
  const isLoading = mode === 'input' ? translationLoading : fixtureLoading
  const currentError = mode === 'input' ? translationError : fixtureError
  const isCompact = !!currentSentence

  const handleTranslationSubmit = async (
    text: string,
    sourceLang: LanguageCode,
    targetLang: LanguageCode
  ) => {
    setMode('input')
    await submitRequest(text, sourceLang, targetLang)
  }

  const switchToExamples = () => {
    startTransition(() => {
      setMode('examples')
      reset()
    })
  }

  useEffect(() => {
    if (currentSentence) {
      document.title = `Xingolak - Analyzing: ${currentSentence.source.text.substring(0, 50)}${currentSentence.source.text.length > 50 ? '...' : ''}`
    } else {
      document.title = 'Xingolak - Translation Alignment Visualizer'
    }
  }, [currentSentence])

  if (isLoading) {
    return <LoadingIndicator mode={mode} loadingStage={loadingStage} />
  }

  if (currentError) {
    return (
      <div className={classNames('max-w-7xl', 'mx-auto', 'p-8')}>
        <div
          className={classNames(
            'text-center',
            'py-12',
            'text-xl',
            'text-red-600',
            'bg-red-50',
            'border',
            'border-red-200',
            'rounded-lg'
          )}
        >
          {t('error.prefix')}{' '}
          {currentError === 'rate_limited' ? t('error.rate_limited') : currentError}
          <div className="mt-4">
            <TryAgainButton
              onTryAgain={() => {
                setMode('input')
                clearError()
              }}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={classNames(
        'min-h-screen',
        'bg-gradient-to-br',
        'from-tan-25',
        'via-tan-50',
        'to-tan-100'
      )}
    >
      <div
        className={classNames(
          'max-w-7xl',
          'mx-auto',
          'px-4',
          'sm:px-6',
          'lg:px-8',
          'pb-4',
          'sm:pb-6',
          'lg:pb-8',
          'font-sans',
          'animate-fade-in-opacity',
          isCompact ? 'pt-0' : 'pt-4 sm:pt-6 lg:pt-8'
        )}
      >
        <AnimatePresence initial={false}>
          {isCompact ? (
            <motion.div
              key="compact-header"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <CompactHeader
                mode={mode}
                onSwitchToInput={() => setMode('input')}
                onSwitchToExamples={switchToExamples}
                selectedId={selectedId}
                availableSentences={availableSentences}
                onSelectSentence={setSelectedId}
              />
            </motion.div>
          ) : (
            <motion.div
              key="full-header"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <FullHeader
                mode={mode}
                onSwitchToInput={() => setMode('input')}
                onSwitchToExamples={switchToExamples}
                translationLoading={translationLoading}
                onSubmit={handleTranslationSubmit}
                initialText={lastRequest?.text || ''}
                initialSourceLang={lastRequest?.sourceLang as LanguageCode | undefined}
                initialTargetLang={lastRequest?.targetLang as LanguageCode | undefined}
                selectedId={selectedId}
                availableSentences={availableSentences}
                onSelectSentence={setSelectedId}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* FAB: rendered outside the header swap so it persists independently.
            No wrapper div — fixed-position children must not be inside a stacking context. */}
        {isCompact && mode === 'input' && (
          <TranslationInput
            onSubmit={handleTranslationSubmit}
            loading={translationLoading}
            compact={true}
            initialText={lastRequest?.text || ''}
            initialSourceLang={lastRequest?.sourceLang as LanguageCode | undefined}
            initialTargetLang={lastRequest?.targetLang as LanguageCode | undefined}
          />
        )}

        {currentSentence && (
          <main
            className={classNames('relative', 'mt-2', 'animate-on-load')}
            style={{ animationDelay: '200ms' }}
            aria-label="Translation alignment visualization"
          >
            <AlignmentVisualizer sentencePair={currentSentence} />
          </main>
        )}

        {!currentSentence && !isLoading && !currentError && (
          <div className={classNames('text-center', 'py-12', 'text-lg', 'text-slate-600')}>
            {mode === 'input' ? null : t('help.select_example')}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
