import { useState } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [agentResult, setAgentResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [backendMsg, setBackendMsg] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setAgentResult(null)
    setBackendMsg('')
    try {
      const res = await fetch('http://localhost:8000/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      if (!res.ok) throw new Error('Network response was not ok')
      const data = await res.json()
      setAgentResult(data)
    } catch (error) {
      setAgentResult({ error: 'Error contacting agent backend' })
      setBackendMsg('Backend is not reachable')
    }
    setLoading(false)
  }

  return (
    <div className="agent-container">
      <h1>Developer Research Agent</h1>
      <div className="backend-status">{backendMsg}</div>
      <form onSubmit={handleSubmit} className="agent-form">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask the agent..."
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? 'Asking...' : 'Ask Agent'}
        </button>
      </form>
      {loading && (
        <div className="loader">
          <div className="loader-spinner"></div>
        </div>
      )}
      {agentResult && !loading && (
        <div className="agent-response">
          {agentResult.error && (
            <div style={{ color: 'red' }}><strong>Error:</strong> {agentResult.error}</div>
          )}
          {agentResult.analysis && (
            <div>
              <strong>Analysis:</strong>
              <div>{agentResult.analysis}</div>
            </div>
          )}
          {agentResult.companies && agentResult.companies.length > 0 && (
            <div style={{ marginTop: '1em' }}>
              <strong>Companies:</strong>
              <ul>
                {agentResult.companies.map((c, idx) => (
                  <li key={idx} style={{ marginBottom: '1em', textAlign: 'left' }}>
                    <div><strong>Name:</strong> {c.name}</div>
                    {c.website && <div><strong>Website:</strong> <a href={c.website} target="_blank" rel="noopener noreferrer">{c.website}</a></div>}
                    {c.pricing_model && <div><strong>Pricing:</strong> {c.pricing_model}</div>}
                    {c.is_open_source !== null && <div><strong>Open Source:</strong> {c.is_open_source ? 'Yes' : 'No'}</div>}
                    {c.tech_stack && c.tech_stack.length > 0 && <div><strong>Tech Stack:</strong> {c.tech_stack.join(', ')}</div>}
                    {c.language_support && c.language_support.length > 0 && <div><strong>Language Support:</strong> {c.language_support.join(', ')}</div>}
                    {c.api_available !== null && <div><strong>API:</strong> {c.api_available ? 'Available' : 'Not Available'}</div>}
                    {c.integration_capabilities && c.integration_capabilities.length > 0 && <div><strong>Integrations:</strong> {c.integration_capabilities.join(', ')}</div>}
                    {c.description && <div><strong>Description:</strong> {c.description}</div>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
