import { useSelectedSentence } from './hooks/useAlignmentData'
import { useTranslationRequest } from './hooks/useTranslationRequest'
import { AlignmentVisualizer } from './components/AlignmentVisualizer'
import { TranslationInput } from './components/TranslationInput'
import { LoadingIndicator } from './components/LoadingIndicator'
import { useEffect, useState } from 'react'
import { config } from './config'

function App() {
  const [mode, setMode] = useState<'input' | 'examples'>('input')
  
  // Hook for loading example sentences (fixture data only)
  const { selectedSentence, selectedId, setSelectedId, availableSentences, loading: fixtureLoading, error: fixtureError } =
    useSelectedSentence()
  
  // Hook for submitting new translation requests
  const { data: translationData, loading: translationLoading, error: translationError, submitRequest, reset } =
    useTranslationRequest()

  // Determine which data to display
  const currentData = mode === 'input' && translationData ? translationData : null
  const currentSentence = currentData?.sentences[0] || (mode === 'examples' ? selectedSentence : null)
  const isLoading = mode === 'input' ? translationLoading : fixtureLoading
  const currentError = mode === 'input' ? translationError : fixtureError

  const handleTranslationSubmit = async (text: string, sourceLang: any, targetLang: any) => {
    setMode('input')
    await submitRequest(text, sourceLang, targetLang)
  }

  const switchToExamples = () => {
    setMode('examples')
    reset()
  }

  // Update page title for screen readers
  useEffect(() => {
    if (currentSentence) {
      document.title = `Itzuli Stanza - Analyzing: ${currentSentence.source.text.substring(0, 50)}${currentSentence.source.text.length > 50 ? '...' : ''}`
    } else {
      document.title = 'Itzuli Stanza - Translation Alignment Visualizer'
    }
  }, [currentSentence])

  if (isLoading) {
    return <LoadingIndicator mode={mode} />
  }

  if (currentError) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <div className="text-center py-12 text-xl text-red-600 bg-red-50 border border-red-200 rounded-lg">
          Error: {currentError}
          <div className="mt-4">
            <button
              onClick={() => setMode('input')}
              className="px-4 py-2 bg-sage-500 text-white rounded-lg hover:bg-sage-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-tan-25 via-tan-50 to-tan-100">
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 font-sans animate-fade-in">
        <header className="text-center mb-3 sm:mb-4 animate-on-load" role="banner">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-display font-light mb-2 text-slate-800 tracking-tight">
            Itzuli <span className="font-medium text-sage-600">Stanza</span>
          </h1>
          <h2 className="text-lg sm:text-xl font-light text-slate-500 mb-3 max-w-2xl mx-auto leading-relaxed px-4 sm:px-0">
            Translation Alignment Visualization for English-Basque Translations
          </h2>

          {/* Mode Toggle - only show if fixtures are available */}
          {config.useFixtures && (
            <div className="flex justify-center mb-4">
              <div className="bg-white/60 backdrop-blur-sm border border-slate-200/60 rounded-lg p-1 flex gap-1">
                <button
                  onClick={() => setMode('input')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    mode === 'input'
                      ? 'bg-sage-500 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  Analyze New Text
                </button>
                <button
                  onClick={switchToExamples}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    mode === 'examples'
                      ? 'bg-sage-500 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  Browse Examples
                </button>
              </div>
            </div>
          )}

          {/* Translation Input Form */}
          {mode === 'input' && (
            <TranslationInput 
              onSubmit={handleTranslationSubmit} 
              loading={translationLoading}
              compact={!!currentSentence}
            />
          )}

          {/* Example Sentence Selector */}
          {mode === 'examples' && config.useFixtures && (
            <div className="content-card max-w-2xl mx-4 sm:mx-auto p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-6">
                <label htmlFor="sentence-select" className="font-medium text-slate-600 text-xs sm:text-sm uppercase tracking-wider">
                  Choose Example Sentence
                </label>
                <select
                  id="sentence-select"
                  value={selectedId || ''}
                  onChange={(e) => setSelectedId(e.target.value)}
                  className="px-3 sm:px-4 py-2 sm:py-3 border border-slate-200 rounded-lg bg-white/80 backdrop-blur-sm text-sm sm:text-base w-full sm:min-w-80 focus:outline-none focus:border-sage-400 focus:ring-2 focus:ring-sage-200 transition-all duration-200"
                  aria-label="Select an example sentence pair for translation alignment visualization"
                >
                  {availableSentences.map((sentence) => (
                    <option key={sentence.id} value={sentence.id}>
                      {sentence.id}: {sentence.source.text}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </header>

        {/* Show visualization only when we have data */}
        {currentSentence && (
          <main className="relative mt-2 animate-on-load" style={{ animationDelay: '200ms' }} role="main" aria-label="Translation alignment visualization">
            <AlignmentVisualizer sentencePair={currentSentence} />
          </main>
        )}
        
        {/* Show helpful message when no data is available */}
        {!currentSentence && !isLoading && !currentError && (
          <div className="text-center py-12 text-lg text-slate-600">
            {mode === 'input' ? 'Enter text above to begin analysis' : 'Select an example sentence to view alignment visualization'}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
