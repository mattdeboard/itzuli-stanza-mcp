import './App.css'
import { useSelectedSentence } from './hooks/useAlignmentData'

function App() {
  const {
    selectedSentence,
    selectedId,
    setSelectedId,
    availableSentences,
    loading,
    error,
  } = useSelectedSentence() // Auto-selects first available sentence

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading alignment data...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  if (!selectedSentence) {
    return (
      <div className="app-container">
        <div className="error">No sentence data available</div>
      </div>
    )
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Itzuli Stanza MCP</h1>
        <h2>Translation Alignment Visualizer</h2>
        
        <div className="sentence-selector">
          <label htmlFor="sentence-select">Example:</label>
          <select
            id="sentence-select"
            value={selectedId || ''}
            onChange={(e) => setSelectedId(e.target.value)}
          >
            {availableSentences.map((sentence) => (
              <option key={sentence.id} value={sentence.id}>
                {sentence.id}: {sentence.source.text}
              </option>
            ))}
          </select>
        </div>
      </header>

      <main className="visualization-container">
        <div className="sentence-pair">
          <div className="source-sentence">
            <div className="language-label">{selectedSentence.source.lang.toUpperCase()}</div>
            <div className="sentence-text">{selectedSentence.source.text}</div>
            <div className="tokens">
              {selectedSentence.source.tokens.map((token) => (
                <span key={token.id} className="token" data-token-id={token.id}>
                  {token.form}
                </span>
              ))}
            </div>
          </div>

          <div className="alignment-space">
            {/* SVG ribbons will go here */}
            <div className="ribbon-container">
              <p className="placeholder">
                Ribbons connecting "{selectedSentence.source.text}" to "{selectedSentence.target.text}"
              </p>
              <p className="lexical-count">
                Lexical alignments: {selectedSentence.layers.lexical.length}
              </p>
            </div>
          </div>

          <div className="target-sentence">
            <div className="language-label">{selectedSentence.target.lang.toUpperCase()}</div>
            <div className="sentence-text">{selectedSentence.target.text}</div>
            <div className="tokens">
              {selectedSentence.target.tokens.map((token) => (
                <span key={token.id} className="token" data-token-id={token.id}>
                  {token.form}
                </span>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App