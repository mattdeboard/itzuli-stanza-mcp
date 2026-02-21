import { useSelectedSentence } from './hooks/useAlignmentData'
import { AlignmentVisualizer } from './components/AlignmentVisualizer'

function App() {
  const { selectedSentence, selectedId, setSelectedId, availableSentences, loading, error } =
    useSelectedSentence() // Auto-selects first available sentence

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
    <div className="max-w-7xl mx-auto p-8 font-sans">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-2 text-slate-800">Itzuli Stanza MCP</h1>
        <h2 className="text-xl font-normal text-slate-600 mb-8">Translation Alignment Visualizer</h2>

        <div className="flex items-center justify-center gap-4">
          <label htmlFor="sentence-select" className="font-medium text-slate-700">
            Example:
          </label>
          <select
            id="sentence-select"
            value={selectedId || ''}
            onChange={(e) => setSelectedId(e.target.value)}
            className="px-4 py-2 border-2 border-gray-300 rounded-md bg-white text-base min-w-80 focus:outline-none focus:border-ribbon-blue"
          >
            {availableSentences.map((sentence) => (
              <option key={sentence.id} value={sentence.id}>
                {sentence.id}: {sentence.source.text}
              </option>
            ))}
          </select>
        </div>
      </header>

      <main className="relative mt-8">
        <AlignmentVisualizer sentencePair={selectedSentence} />
      </main>
    </div>
  )
}

export default App
