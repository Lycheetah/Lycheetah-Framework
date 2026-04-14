import React, { useState, useEffect } from 'react'
import { runExperiment, getScoreBand } from '../scoring/cascade'
import './ExperimentView.css'

const MODES = [
  { key: 'resonance',    label: 'RESONANCE',    icon: '↔', desc: 'Where both pyramids agree and reinforce each other' },
  { key: 'contradiction',label: 'CONTRADICTION', icon: '⊗', desc: 'Where they clash — Nigredo applied to the intersection' },
  { key: 'synthesis',    label: 'SYNTHESIS',     icon: '+', desc: 'What emerges that neither pyramid contained alone' },
]

export default function ExperimentView() {
  const [pyramids, setPyramids] = useState([])
  const [pyramidA, setPyramidA] = useState('')
  const [pyramidB, setPyramidB] = useState('')
  const [mode, setMode] = useState('resonance')
  const [results, setResults] = useState(null)
  const [running, setRunning] = useState(false)
  const [experimentName, setExperimentName] = useState('')

  useEffect(() => {
    window.cascade.pyramids.list().then(setPyramids)
  }, [])

  async function run() {
    if (!pyramidA || !pyramidB || pyramidA === pyramidB) return
    setRunning(true)
    setResults(null)

    const [filesA, filesB] = await Promise.all([
      window.cascade.files.list(pyramidA),
      window.cascade.files.list(pyramidB),
    ])

    // Load all blocks for both pyramids
    const blocksA = (await Promise.all(filesA.map(f => window.cascade.blocks.list(f.id)))).flat()
    const blocksB = (await Promise.all(filesB.map(f => window.cascade.blocks.list(f.id)))).flat()

    const pairs = runExperiment(blocksA, blocksB, mode)

    const pA = pyramids.find(p => p.id === pyramidA)
    const pB = pyramids.find(p => p.id === pyramidB)

    const result = { mode, pyramidA: pA, pyramidB: pB, pairs, blocksACount: blocksA.length, blocksBCount: blocksB.length }
    setResults(result)

    // Save experiment
    if (experimentName.trim()) {
      const exp = await window.cascade.experiments.create({
        name: experimentName.trim(), pyramidAId: pyramidA, pyramidBId: pyramidB, mode,
      })
      await window.cascade.experiments.saveResult({ id: exp.id, resultData: result })
    }

    setRunning(false)
  }

  const activeMode = MODES.find(m => m.key === mode)

  return (
    <div className="experiment-view">
      <div className="exp-header">
        <div className="exp-title">
          <span className="exp-icon">⊗</span>
          EXPERIMENT PYRAMID
        </div>
        <div className="exp-sub">Combine two pyramids — find what emerges between them</div>
      </div>

      <div className="exp-body">
        {/* Setup panel */}
        <div className="exp-setup">
          <div className="setup-section">
            <div className="setup-label">PYRAMID A</div>
            <select value={pyramidA} onChange={e => setPyramidA(e.target.value)} className="select">
              <option value="">— select pyramid —</option>
              {pyramids.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>

          <div className="setup-operator">⊗</div>

          <div className="setup-section">
            <div className="setup-label">PYRAMID B</div>
            <select value={pyramidB} onChange={e => setPyramidB(e.target.value)} className="select">
              <option value="">— select pyramid —</option>
              {pyramids.filter(p => p.id !== pyramidA).map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>

          <div className="setup-section">
            <div className="setup-label">MODE</div>
            <div className="mode-tabs">
              {MODES.map(m => (
                <button
                  key={m.key}
                  className={`mode-tab ${mode === m.key ? 'active' : ''}`}
                  onClick={() => setMode(m.key)}
                >
                  <span className="mode-icon">{m.icon}</span>
                  <span>{m.label}</span>
                </button>
              ))}
            </div>
            <div className="mode-desc">{activeMode?.desc}</div>
          </div>

          <div className="setup-section">
            <div className="setup-label">EXPERIMENT NAME (optional)</div>
            <input type="text" placeholder="Name this experiment to save it..." value={experimentName} onChange={e => setExperimentName(e.target.value)} />
          </div>

          <button
            className="btn primary run-btn"
            onClick={run}
            disabled={!pyramidA || !pyramidB || pyramidA === pyramidB || running}
          >
            {running ? 'Running...' : `Run ${activeMode?.label}`}
          </button>
        </div>

        {/* Results */}
        <div className="exp-results">
          {!results && !running && (
            <div className="results-empty">
              <div className="results-empty-icon">⊗</div>
              <div>Select two pyramids and run an experiment</div>
            </div>
          )}

          {results && (
            <>
              <div className="results-header">
                <div className="results-title">
                  {results.pyramidA?.name} {activeMode?.icon} {results.pyramidB?.name}
                </div>
                <div className="results-meta">
                  {results.pairs.length} pairs found · {results.blocksACount + results.blocksBCount} total blocks
                </div>
              </div>

              {results.pairs.length === 0 && (
                <div className="no-pairs">No significant {mode} pairs found. Add more scored blocks to both pyramids.</div>
              )}

              <div className="pairs-list">
                {results.pairs.map((pair, i) => <PairCard key={i} pair={pair} mode={mode} rank={i + 1} />)}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function PairCard({ pair, mode, rank }) {
  if (mode === 'resonance') {
    const band = getScoreBand(pair.resonanceScore)
    return (
      <div className="pair-card resonance">
        <div className="pair-rank">#{rank}</div>
        <div className="pair-blocks">
          <div className="pair-block">{pair.blockA.title}</div>
          <div className="pair-connector" style={{ color: 'var(--layer-resonance)' }}>↔ resonance</div>
          <div className="pair-block">{pair.blockB.title}</div>
        </div>
        <div className="pair-score" style={{ color: band.textColor }}>
          {pair.resonanceScore} · {band.label}
          <div className="pair-delta">Δ {pair.delta}</div>
        </div>
      </div>
    )
  }

  if (mode === 'contradiction') {
    return (
      <div className="pair-card contradiction">
        <div className="pair-rank">#{rank}</div>
        <div className="pair-blocks">
          <div className="pair-block strong">{pair.stronger.title} ↑{pair.stronger.score_aggregate}</div>
          <div className="pair-connector" style={{ color: 'var(--layer-tension)' }}>⊗ contradiction</div>
          <div className="pair-block weak">{pair.weaker.title} ↑{pair.weaker.score_aggregate}</div>
        </div>
        <div className="pair-score" style={{ color: 'var(--layer-tension)' }}>
          Δ {pair.delta} tension
        </div>
      </div>
    )
  }

  if (mode === 'synthesis') {
    const band = getScoreBand(pair.synthesisScore)
    return (
      <div className="pair-card synthesis">
        <div className="pair-rank">#{rank}</div>
        <div className="pair-blocks">
          <div className="pair-block">{pair.blockA.title}</div>
          <div className="pair-connector" style={{ color: 'var(--layer-speculative)' }}>+ synthesis</div>
          <div className="pair-block">{pair.blockB.title}</div>
        </div>
        <div className="pair-score" style={{ color: band.textColor }}>
          {pair.synthesisScore}
          {pair.gain > 0 && <span className="pair-gain"> +{pair.gain} gain</span>}
        </div>
      </div>
    )
  }

  return null
}
