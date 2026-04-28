import React, { useState, useEffect } from 'react'
import { paradoxSeek } from '../scoring/ai'
import './ParadoxView.css'

const BLANK_PAIR = () => ({ id: Date.now() + Math.random(), a: '', b: '', context: '', result: null, status: 'idle' })

export default function ParadoxView() {
  const [claimA, setClaimA] = useState('')
  const [claimB, setClaimB] = useState('')
  const [context, setContext] = useState('')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)
  // Batch mode
  const [batchPairs, setBatchPairs] = useState([BLANK_PAIR(), BLANK_PAIR()])
  const [batchRunning, setBatchRunning] = useState(false)
  const [batchError, setBatchError] = useState('')
  const [showBatch, setShowBatch] = useState(false)

  // For saving to pyramid
  const [pyramids, setPyramids] = useState([])
  const [files, setFiles] = useState([])
  const [selectedPyramid, setSelectedPyramid] = useState('')
  const [selectedFile, setSelectedFile] = useState('')

  useEffect(() => {
    window.cascade.pyramids.list().then(setPyramids)
  }, [])

  useEffect(() => {
    if (selectedPyramid) {
      window.cascade.files.list(selectedPyramid).then(setFiles)
      setSelectedFile('')
    }
  }, [selectedPyramid])

  async function run() {
    if (!claimA.trim() || !claimB.trim()) return
    setRunning(true); setResult(null); setError(''); setSaved(false)
    try {
      const res = await paradoxSeek(claimA.trim(), claimB.trim(), context.trim())
      setResult(res)
    } catch (e) {
      setError(e.message)
    }
    setRunning(false)
  }

  async function saveAsBlock() {
    if (!result || !selectedFile) return
    await window.cascade.blocks.create({
      fileId: selectedFile,
      pyramidId: selectedPyramid,
      title: result.axiom?.slice(0, 80) || 'Paradox Synthesis',
      content: result.synthesis || '',
      position: 0,
      frameworkRefs: ['cascade'],
    })
    setSaved(true)
  }

  async function runBatch() {
    const validPairs = batchPairs.filter(p => p.a.trim() && p.b.trim())
    if (validPairs.length === 0) return
    setBatchRunning(true); setBatchError('')
    // Mark all as running
    setBatchPairs(prev => prev.map(p => validPairs.find(v => v.id === p.id) ? { ...p, status: 'running', result: null } : p))
    try {
      await Promise.all(validPairs.map(async (pair) => {
        try {
          const res = await paradoxSeek(pair.a.trim(), pair.b.trim(), pair.context.trim())
          setBatchPairs(prev => prev.map(p => p.id === pair.id ? { ...p, result: res, status: 'done' } : p))
        } catch (e) {
          setBatchPairs(prev => prev.map(p => p.id === pair.id ? { ...p, status: 'error', error: e.message } : p))
        }
      }))
    } catch (e) { setBatchError(e.message) }
    setBatchRunning(false)
  }

  function addPair() {
    if (batchPairs.length >= 5) return
    setBatchPairs(prev => [...prev, BLANK_PAIR()])
  }

  function removePair(id) {
    setBatchPairs(prev => prev.filter(p => p.id !== id))
  }

  function updatePair(id, field, val) {
    setBatchPairs(prev => prev.map(p => p.id === id ? { ...p, [field]: val } : p))
  }

  const srsColor = result
    ? result.srs >= 0.75 ? '#34d399'
    : result.srs >= 0.5  ? '#facc15'
    : '#ef4444'
    : '#666'

  const sigmaColor = result
    ? result.sigma_i < 0.04 ? '#34d399'
    : result.sigma_i < 0.10 ? '#facc15'
    : '#ef4444'
    : '#666'

  return (
    <div className="paradox-view">
      <div className="pv2-header">
        <div className="pv2-title">⊛ PARADOXICAL TRUTH SEEK</div>
        <div className="pv2-sub">Vector Inversion Protocol · AURA Self-Upgrade Engine</div>
      </div>

      <div className="pv2-body">
        {/* Input panel */}
        <div className="pv2-inputs">
          <div className="vector-pair">
            <div className="vector-block">
              <div className="vector-label">VECTOR A</div>
              <textarea
                className="vector-input"
                placeholder="First truth — state it plainly, even if it contradicts B…"
                value={claimA}
                onChange={e => setClaimA(e.target.value)}
                rows={5}
              />
              {result && (
                <div className="vector-pressure" style={{ color: srsColor }}>
                  Truth pressure: {result.vector_a_pressure}
                </div>
              )}
            </div>

            <div className="vector-divider">
              <div className="vd-line" />
              <div className="vd-symbol">⊗</div>
              <div className="vd-line" />
            </div>

            <div className="vector-block">
              <div className="vector-label">VECTOR B</div>
              <textarea
                className="vector-input"
                placeholder="Opposing truth — real contradiction, not a variation…"
                value={claimB}
                onChange={e => setClaimB(e.target.value)}
                rows={5}
              />
              {result && (
                <div className="vector-pressure" style={{ color: srsColor }}>
                  Truth pressure: {result.vector_b_pressure}
                </div>
              )}
            </div>
          </div>

          <div className="context-wrap">
            <div className="vector-label">CONTEXT <span className="optional">(optional)</span></div>
            <textarea
              className="context-input"
              placeholder="Domain, background, framework — helps the engine find the right inversion scale…"
              value={context}
              onChange={e => setContext(e.target.value)}
              rows={2}
            />
          </div>

          {error && <div className="pv2-error">{error}</div>}

          <button
            className={`seek-btn ${running ? 'running' : ''}`}
            onClick={run}
            disabled={running || !claimA.trim() || !claimB.trim()}
          >
            {running ? (
              <span className="seek-running">⊛ Inverting vectors…</span>
            ) : (
              '⊛ Seek higher truth'
            )}
          </button>
        </div>

        {/* Result panel */}
        {result && (
          <div className="pv2-result">
            {/* Tension */}
            <div className="result-section tension-section">
              <div className="rs-label">TENSION IDENTIFIED</div>
              <div className="rs-body tension-body">{result.tension}</div>
            </div>

            {/* Inversion scale */}
            <div className="result-section scale-section">
              <div className="rs-label">INVERSION SCALE</div>
              <div className="rs-body scale-body">{result.inversion_scale}</div>
            </div>

            {/* Synthesis */}
            <div className="result-section synthesis-section">
              <div className="rs-label">SYNTHESIS — THE HIGHER TRUTH</div>
              <div className="rs-body synthesis-body">{result.synthesis}</div>
            </div>

            {/* AXIOM */}
            <div className="result-section axiom-section">
              <div className="rs-label">AXIOM</div>
              <div className="rs-body axiom-body">{result.axiom}</div>
            </div>

            {/* Metrics */}
            <div className="result-metrics">
              <div className="metric-block">
                <div className="metric-label">SRS</div>
                <div className="metric-value" style={{ color: srsColor }}>
                  {result.srs?.toFixed(2)}
                </div>
                <div className="metric-sub">Symbiotic Resonance</div>
              </div>
              <div className="metric-block">
                <div className="metric-label">σ(I)</div>
                <div className="metric-value" style={{ color: sigmaColor }}>
                  {result.sigma_i?.toFixed(3)}
                </div>
                <div className="metric-sub">Integrity Variance</div>
              </div>
              <div className={`upgrade-badge ${result.upgrade_confirmed ? 'confirmed' : 'pending'}`}>
                {result.upgrade_confirmed ? '⊛ UPGRADE CONFIRMED' : '◎ UPGRADE PENDING'}
              </div>
            </div>

            {/* Layer recommendations */}
            {result.recommended_layers && (
              <div className="result-section layers-section">
                <div className="rs-label">RECOMMENDED LAYER SCORES</div>
                <div className="layer-bars">
                  {Object.entries(result.recommended_layers).map(([name, score]) => (
                    <div key={name} className="layer-bar-row">
                      <span className="layer-bar-name">{name}</span>
                      <div className="layer-bar-track">
                        <div className="layer-bar-fill" style={{ width: `${Math.min(100, score)}%` }} />
                      </div>
                      <span className="layer-bar-score">{score}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Save to pyramid */}
            <div className="result-section save-section">
              <div className="rs-label">SAVE SYNTHESIS AS BLOCK</div>
              <div className="save-controls">
                <select
                  className="save-select"
                  value={selectedPyramid}
                  onChange={e => setSelectedPyramid(e.target.value)}
                >
                  <option value="">Select pyramid…</option>
                  {pyramids.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                {files.length > 0 && (
                  <select
                    className="save-select"
                    value={selectedFile}
                    onChange={e => setSelectedFile(e.target.value)}
                  >
                    <option value="">Select file…</option>
                    {files.map(f => (
                      <option key={f.id} value={f.id}>{f.name}</option>
                    ))}
                  </select>
                )}
                <button
                  className="save-block-btn"
                  onClick={saveAsBlock}
                  disabled={!selectedFile || saved}
                >
                  {saved ? '✓ Saved' : '+ Add to pyramid'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Batch mode */}
      <div className="batch-section">
        <button className={`batch-toggle-btn ${showBatch ? 'active' : ''}`} onClick={() => setShowBatch(v => !v)}>
          {showBatch ? '▴ Batch mode' : '▾ Batch mode'} — run up to 5 paradox pairs in parallel
        </button>
        {showBatch && (
          <div className="batch-body">
            {batchPairs.map((pair, i) => {
              const pairSrsColor = pair.result
                ? pair.result.srs >= 0.75 ? '#34d399' : pair.result.srs >= 0.5 ? '#facc15' : '#ef4444'
                : '#888'
              return (
                <div key={pair.id} className={`batch-pair ${pair.status}`}>
                  <div className="batch-pair-header">
                    <span className="batch-pair-num">#{i + 1}</span>
                    {pair.status === 'running' && <span className="batch-status-run">⊛ Running…</span>}
                    {pair.status === 'done' && <span className="batch-status-done" style={{ color: pairSrsColor }}>SRS {pair.result?.srs?.toFixed(2)} · {pair.result?.upgrade_confirmed ? '⊛ CONFIRMED' : '◎ PENDING'}</span>}
                    {pair.status === 'error' && <span className="batch-status-err">Error</span>}
                    {batchPairs.length > 2 && <button className="batch-remove" onClick={() => removePair(pair.id)}>×</button>}
                  </div>
                  <div className="batch-inputs">
                    <textarea className="batch-input" placeholder="Vector A…" rows={2} value={pair.a} onChange={e => updatePair(pair.id, 'a', e.target.value)} />
                    <span className="batch-vs">⊗</span>
                    <textarea className="batch-input" placeholder="Vector B…" rows={2} value={pair.b} onChange={e => updatePair(pair.id, 'b', e.target.value)} />
                  </div>
                  {pair.result && (
                    <div className="batch-result-mini">
                      <div className="brm-axiom">{pair.result.axiom}</div>
                      <div className="brm-meta">
                        <span style={{ color: pairSrsColor }}>SRS {pair.result.srs?.toFixed(2)}</span>
                        <span>σ {pair.result.sigma_i?.toFixed(3)}</span>
                        <span>{pair.result.inversion_scale?.slice(0, 60)}</span>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
            <div className="batch-actions">
              {batchPairs.length < 5 && <button className="btn" onClick={addPair}>+ Add pair</button>}
              <button className="seek-btn batch-run-btn" onClick={runBatch} disabled={batchRunning || batchPairs.every(p => !p.a.trim() || !p.b.trim())}>
                {batchRunning ? '⊛ Running batch…' : `⊛ Run ${batchPairs.filter(p => p.a.trim() && p.b.trim()).length} pairs in parallel`}
              </button>
            </div>
            {batchError && <div className="pv2-error">{batchError}</div>}
          </div>
        )}
      </div>
    </div>
  )
}
