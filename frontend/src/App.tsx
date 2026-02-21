import { useSelectedSentence } from './hooks/useAlignmentData'
import { AlignmentVisualizer } from './components/AlignmentVisualizer'
import { useEffect } from 'react'

function App() {
  const { selectedSentence, selectedId, setSelectedId, availableSentences, loading, error } =
    useSelectedSentence() // Auto-selects first available sentence

  // Update page title for screen readers
  useEffect(() => {
    if (selectedSentence) {
      document.title = `Itzuli Stanza - Analyzing: ${selectedSentence.source.text.substring(0, 50)}${selectedSentence.source.text.length > 50 ? '...' : ''}`
    } else {
      document.title = 'Itzuli Stanza - Translation Alignment Visualizer'
    }
  }, [selectedSentence])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <div className="text-center py-12 text-xl text-ribbon-blue">Loading alignment data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <div className="text-center py-12 text-xl text-red-600 bg-red-50 border border-red-200 rounded-lg">
          Error: {error}
        </div>
      </div>
    )
  }

  if (!selectedSentence) {
    return (
      <div className="max-w-7xl mx-auto p-8">
        <div className="text-center py-12 text-xl text-red-600">No sentence data available</div>
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
        </header>

        <main className="relative mt-2 animate-on-load" style={{ animationDelay: '200ms' }} role="main" aria-label="Translation alignment visualization">
          <AlignmentVisualizer sentencePair={selectedSentence} />
        </main>
      </div>
    </div>
  )
}

export default App
