import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <h1>Itzuli Stanza MCP</h1>
        <h2>Text Alignment Visualization</h2>
      </div>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Frontend placeholder for text alignment visualization.
        </p>
      </div>
      <p className="read-the-docs">
        Connect to backend API at <code>http://localhost:8000</code>
      </p>
    </>
  )
}

export default App