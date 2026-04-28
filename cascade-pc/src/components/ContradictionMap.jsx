import React, { useState, useEffect } from 'react'
import { getScoreBand } from '../scoring/cascade'
import './ContradictionMap.css'

/**
 * Contradiction Map — visual matrix of block tensions across the pyramid.
 * Shows how each pair of scored blocks relates: resonance, tension, or neutral.
 * Delta > 30 = contradiction. Delta 15–30 = tension. Delta < 15 = resonance.
 */

function classifyPair(a, b) {
  const delta = Math.abs((a.score_aggregate || 0) - (b.score_aggregate || 0))
  if (delta > 35) return { type: 'contradiction', delta, color: '#f87171' }
  if (delta > 20) return { type: 'tension',       delta, color: '#facc15' }
  if (delta < 12 && a.score_aggregate > 0 && b.score_aggregate > 0)
                  return { type: 'resonance',     delta, color: '#4ade80' }
  return           { type: 'neutral',             delta, color: '#333' }
}

export default function ContradictionMap({ files }) {
  const [allBlocks, setAllBlocks] = useState([])
  const [selected, setSelected]   = useState(null) // { a, b, rel }
  const [fileFilter, setFileFilter] = useState('all')

  useEffect(() => {
    async function load() {
      if (!files || files.length === 0) return
      let blocks = []
      for (const f of files) {
        const fb = await window.cascade.blocks.list(f.id)
        blocks = blocks.concat(fb.map(b => ({ ...b, _fileName: f.name })))
      }
      setAllBlocks(blocks.filter(b => b.score_aggregate > 0))
    }
    load()
  }, [files])

  const displayed = fileFilter === 'all'
    ? allBlocks
    : allBlocks.filter(b => b._fileName === fileFilter)

  // Limit to 20 blocks for readability
  const blocks = displayed.slice(0, 20)

  const contradictions = []
  const tensions = []
  const resonances = []

  for (let i = 0; i < blocks.length; i++) {
    for (let j = i + 1; j < blocks.length; j++) {
      const rel = classifyPair(blocks[i], blocks[j])
      if (rel.type === 'contradiction') contradictions.push({ a: blocks[i], b: blocks[j], ...rel })
      if (rel.type === 'tension')       tensions.push({ a: blocks[i], b: blocks[j], ...rel })
      if (rel.type === 'resonance')     resonances.push({ a: blocks[i], b: blocks[j], ...rel })
    }
  }

  contradictions.sort((x, y) => y.delta - x.delta)
  resonances.sort((x, y) => x.delta - y.delta)

  return (
    <div className="cmap-root">
      <div className="cmap-header">
        <span className="cmap-title">⊗ CONTRADICTION MAP</span>
        <select className="cmap-filter" value={fileFilter} onChange={e => setFileFilter(e.target.value)}>
          <option value="all">All files</option>
          {files.map(f => <option key={f.id} value={f.name}>{f.name}</option>)}
        </select>
        <span className="cmap-counts">
          <span className="cmap-count-c">{contradictions.length} contradictions</span>
          <span className="cmap-count-t">{tensions.length} tensions</span>
          <span className="cmap-count-r">{resonances.length} resonances</span>
        </span>
      </div>

      {blocks.length === 0 && (
        <div className="cmap-empty">No scored blocks found. Score some blocks first.</div>
      )}

      {/* Matrix grid */}
      {blocks.length > 1 && (
        <div className="cmap-matrix-wrap">
          <div className="cmap-matrix" style={{ '--n': blocks.length }}>
            {/* Row labels */}
            <div className="cmap-corner" />
            {blocks.map((b, i) => (
              <div key={i} className="cmap-col-label" title={b.title}>
                <span>{b.title.slice(0, 10)}{b.title.length > 10 ? '…' : ''}</span>
              </div>
            ))}
            {blocks.map((a, i) => (
              <React.Fragment key={i}>
                <div className="cmap-row-label" title={a.title}>
                  <span className="cmap-row-score" style={{ color: getScoreBand(a.score_aggregate).textColor }}>{a.score_aggregate}</span>
                  <span>{a.title.slice(0, 14)}{a.title.length > 14 ? '…' : ''}</span>
                </div>
                {blocks.map((b, j) => {
                  if (i === j) return <div key={j} className="cmap-cell cmap-self" />
                  const rel = classifyPair(a, b)
                  return (
                    <div
                      key={j}
                      className={`cmap-cell cmap-${rel.type}`}
                      style={{ background: rel.color + '22', borderColor: rel.color + '66' }}
                      title={`${a.title} ↔ ${b.title} · Δ${rel.delta} · ${rel.type}`}
                      onClick={() => setSelected({ a, b, ...rel })}
                    >
                      <span className="cmap-delta">{rel.delta}</span>
                    </div>
                  )
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Selected pair detail */}
      {selected && (
        <div className="cmap-detail">
          <div className="cmap-detail-header">
            <span style={{ color: selected.color }}>{selected.type.toUpperCase()} · Δ{selected.delta}</span>
            <button className="cmap-close" onClick={() => setSelected(null)}>✕</button>
          </div>
          <div className="cmap-pair">
            <div className="cmap-block-card" style={{ borderColor: getScoreBand(selected.a.score_aggregate).textColor + '66' }}>
              <div className="cmap-block-score" style={{ color: getScoreBand(selected.a.score_aggregate).textColor }}>{selected.a.score_aggregate}</div>
              <div className="cmap-block-title">{selected.a.title}</div>
              <div className="cmap-block-file">{selected.a._fileName}</div>
            </div>
            <div className="cmap-pair-arrow" style={{ color: selected.color }}>
              {selected.type === 'resonance' ? '⟷' : selected.type === 'tension' ? '⊗' : '✕'}
            </div>
            <div className="cmap-block-card" style={{ borderColor: getScoreBand(selected.b.score_aggregate).textColor + '66' }}>
              <div className="cmap-block-score" style={{ color: getScoreBand(selected.b.score_aggregate).textColor }}>{selected.b.score_aggregate}</div>
              <div className="cmap-block-title">{selected.b.title}</div>
              <div className="cmap-block-file">{selected.b._fileName}</div>
            </div>
          </div>
        </div>
      )}

      {/* Lists */}
      <div className="cmap-lists">
        {contradictions.length > 0 && (
          <div className="cmap-list-section">
            <div className="cmap-list-title" style={{ color: '#f87171' }}>⊗ CONTRADICTIONS</div>
            {contradictions.slice(0, 8).map((r, i) => (
              <div key={i} className="cmap-list-row" onClick={() => setSelected(r)}>
                <span className="cmap-lr-delta" style={{ color: '#f87171' }}>Δ{r.delta}</span>
                <span className="cmap-lr-a">{r.a.title.slice(0, 22)}</span>
                <span className="cmap-lr-sep">vs</span>
                <span className="cmap-lr-b">{r.b.title.slice(0, 22)}</span>
              </div>
            ))}
          </div>
        )}
        {resonances.length > 0 && (
          <div className="cmap-list-section">
            <div className="cmap-list-title" style={{ color: '#4ade80' }}>◈ RESONANCES</div>
            {resonances.slice(0, 6).map((r, i) => (
              <div key={i} className="cmap-list-row" onClick={() => setSelected(r)}>
                <span className="cmap-lr-delta" style={{ color: '#4ade80' }}>Δ{r.delta}</span>
                <span className="cmap-lr-a">{r.a.title.slice(0, 22)}</span>
                <span className="cmap-lr-sep">≈</span>
                <span className="cmap-lr-b">{r.b.title.slice(0, 22)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
