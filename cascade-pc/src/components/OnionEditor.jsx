import React, { useState, useEffect } from 'react'
import { ONION_LAYERS, computeBlockScore, getScoreBand } from '../scoring/cascade'
import { scoreBlock } from '../scoring/ai'
import { getAllFrameworks } from '../scoring/frameworks'
const FRAMEWORK_LIST = getAllFrameworks()
import './OnionEditor.css'

function fmtScoreTime(ts) {
  if (!ts) return null
  const diff = Math.floor(Date.now() / 1000) - ts
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`
  return new Date(ts * 1000).toLocaleDateString()
}

const LAYER_COLORS = [
  'var(--layer-axiom)', 'var(--layer-foundation)', 'var(--layer-structure)',
  'var(--layer-coherence)', 'var(--layer-resonance)', 'var(--layer-tension)',
  'var(--layer-contested)', 'var(--layer-speculative)', 'var(--layer-frontier)',
]

export default function OnionEditor({ block, fileContent, onSaved }) {
  const [layers, setLayers] = useState([])
  const [activeLayer, setActiveLayer] = useState(0)
  const [sovereignDraft, setSovereignDraft] = useState({ score: 0, notes: '' })
  const [aiScoring, setAiScoring] = useState(false)
  const [aiError, setAiError] = useState('')
  const [savedSovereign, setSavedSovereign] = useState(false)
  const [frameworkRefs, setFrameworkRefs] = useState(block.framework_refs || ['cascade'])

  useEffect(() => {
    loadLayers()
    setActiveLayer(0)
    setFrameworkRefs(block.framework_refs || ['cascade'])
  }, [block.id])

  useEffect(() => {
    if (layers[activeLayer]) {
      setSovereignDraft({
        score: layers[activeLayer].sovereign_score || 0,
        notes: layers[activeLayer].sovereign_notes || '',
      })
    }
  }, [activeLayer, layers])

  async function loadLayers() {
    const list = await window.cascade.onion.list(block.id)
    setLayers(list)
  }

  function selectLayer(i) {
    setActiveLayer(i)
  }

  function handleLayerKeyDown(e) {
    if (e.key === 'Tab') {
      e.preventDefault()
      setActiveLayer(prev => e.shiftKey
        ? (prev - 1 + ONION_LAYERS.length) % ONION_LAYERS.length
        : (prev + 1) % ONION_LAYERS.length)
    }
  }

  async function saveSovereign() {
    const layer = layers[activeLayer]
    if (!layer) return
    await window.cascade.onion.updateSovereign({
      id: layer.id,
      sovereign_score: Number(sovereignDraft.score) || 0,
      sovereign_notes: sovereignDraft.notes,
    })
    await loadLayers()
    // Recompute sovereign aggregate
    const allLayers = await window.cascade.onion.list(block.id)
    const sovereignScore = computeBlockScore(allLayers, 'sovereign')
    await window.cascade.blocks.updateScore({ id: block.id, sovereignScore })
    onSaved()
    setSavedSovereign(true)
    setTimeout(() => setSavedSovereign(false), 1500)
  }

  async function toggleFramework(fid) {
    let updated
    if (frameworkRefs.includes(fid)) {
      if (frameworkRefs.length === 1) return // must keep at least one
      updated = frameworkRefs.filter(f => f !== fid)
    } else {
      updated = [...frameworkRefs, fid]
    }
    setFrameworkRefs(updated)
    await window.cascade.blocks.setFrameworkRefs({ id: block.id, frameworkRefs: updated })
  }

  async function runAiScore() {
    setAiScoring(true)
    setAiError('')
    try {
      const scored = await scoreBlock(block.title, block.content, fileContent || '', frameworkRefs)
      for (let i = 0; i < scored.length; i++) {
        const layer = layers[i]
        if (!layer) continue
        await window.cascade.onion.updateFramework({
          id: layer.id,
          framework_score: scored[i].framework_score,
          framework_reasoning: scored[i].framework_reasoning,
          framework_refs: frameworkRefs,
        })
      }
      await loadLayers()
      // Recompute framework aggregate
      const allLayers = await window.cascade.onion.list(block.id)
      const frameworkScore = computeBlockScore(allLayers, 'framework')
      await window.cascade.blocks.updateScore({ id: block.id, score: frameworkScore })
      onSaved()
    } catch (e) {
      setAiError(e.message)
    }
    setAiScoring(false)
  }

  const frameworkScore = computeBlockScore(layers, 'framework')
  const sovereignScore = computeBlockScore(layers, 'sovereign')
  const frameworkBand = getScoreBand(frameworkScore)
  const sovereignBand = getScoreBand(sovereignScore)
  const activeLayerData = layers[activeLayer]

  return (
    <div className="onion-editor">
      <div className="oe-header">
        <div className="oe-block-title">{block.title}</div>
        <div className="oe-scores-summary">
          {frameworkScore > 0 && (
            <div className="oe-score-pill framework" style={{ color: frameworkBand.textColor }}>
              <span className="pill-label">FRAMEWORK</span>
              <span className="pill-score">{frameworkScore}</span>
              <span className="pill-band">{frameworkBand.label}</span>
            </div>
          )}
          {sovereignScore > 0 && (
            <div className="oe-score-pill sovereign">
              <span className="pill-label">SOVEREIGN</span>
              <span className="pill-score">{sovereignScore}</span>
              <span className="pill-band">{sovereignBand.label}</span>
            </div>
          )}
        </div>
      </div>

      {/* Framework selector */}
      <div className="oe-framework-bar">
        <span className="fw-label">SCORE AGAINST:</span>
        <div className="fw-chips">
          {FRAMEWORK_LIST.map(f => (
            <button
              key={f.id}
              className={`fw-chip ${frameworkRefs.includes(f.id) ? 'active' : ''}`}
              onClick={() => toggleFramework(f.id)}
              style={frameworkRefs.includes(f.id) ? { color: f.color, borderColor: f.color } : {}}
              title={f.tagline}
            >
              {f.glyph} {f.name}
            </button>
          ))}
        </div>
        <span className="fw-hint">
          {FRAMEWORK_LIST.filter(f => frameworkRefs.includes(f.id)).map(f => f.tagline).join(' · ')}
        </span>
        <button className="btn primary ai-score-btn" onClick={runAiScore} disabled={aiScoring}>
          {aiScoring ? '⊚ Scoring...' : '⊚ AI Score'}
        </button>
      </div>

      {aiError && <div className="ai-error">{aiError}</div>}

      <div className="oe-body">
        {/* Layer list */}
        <div className="oe-layers">
          <div className="oe-layers-label">9 ONION LAYERS</div>
          {ONION_LAYERS.map((layer, i) => {
            const ld = layers[i]
            const fScore = ld?.framework_score || ld?.score || 0
            const sScore = ld?.sovereign_score || 0
            const color = LAYER_COLORS[i]
            return (
              <div
                key={i}
                className={`layer-row ${activeLayer === i ? 'active' : ''}`}
                onClick={() => selectLayer(i)}
                style={{ '--layer-color': color }}
              >
                <div className="layer-dot" style={{ background: color }} />
                <div className="layer-info">
                  <div className="layer-name">{layer.name}</div>
                  <div className="layer-desc">{layer.description}</div>
                </div>
                <div className="layer-scores">
                  <span className="ls-fw" style={{ color: fScore > 0 ? color : 'var(--text-dim)' }}>{fScore > 0 ? fScore : '—'}</span>
                  {sScore > 0 && <span className="ls-sv">{sScore}</span>}
                </div>
              </div>
            )
          })}
        </div>

        {/* Layer detail */}
        <div className="oe-detail">
          {activeLayerData && (
            <>
              <div className="oe-layer-header" style={{ color: LAYER_COLORS[activeLayer] }}>
                <span className="oe-layer-name">{ONION_LAYERS[activeLayer].name}</span>
                <span className="oe-layer-desc">{ONION_LAYERS[activeLayer].description}</span>
              </div>

              {/* Framework track — locked */}
              <div className="score-track framework-track">
                <div className="track-header">
                  <span className="track-label">FRAMEWORK SCORE</span>
                  <span className="track-sub">AI · scored against {frameworkRefs.map(r => r.toUpperCase()).join(' + ')} · locked</span>
                </div>
                <div className="track-body">
                  {activeLayerData.framework_score > 0 || activeLayerData.score > 0 ? (
                    <>
                      <div className="fw-score-display" style={{ color: LAYER_COLORS[activeLayer] }}>
                        {activeLayerData.framework_score || activeLayerData.score}
                        {activeLayerData.scored_at && (
                          <span className="fw-scored-at">{fmtScoreTime(activeLayerData.scored_at)}</span>
                        )}
                      </div>
                      {activeLayerData.framework_reasoning && (
                        <div className="fw-reasoning">"{activeLayerData.framework_reasoning}"</div>
                      )}
                      {activeLayerData.framework_score > 100 && (
                        <div className="frontier-notice">◎ Frontier truth — scored beyond calibrated range</div>
                      )}
                    </>
                  ) : (
                    <div className="track-empty">Run ⊚ AI Score to generate framework scoring</div>
                  )}
                </div>
              </div>

              {/* Sovereign track — user's own */}
              <div className="score-track sovereign-track">
                <div className="track-header">
                  <span className="track-label">SOVEREIGN SCORE</span>
                  <span className="track-sub">your truth pressure · your responsibility</span>
                </div>
                <div className="track-body">
                  <div className="sv-input-row">
                    <input
                      type="number"
                      min={0}
                      max={999}
                      value={sovereignDraft.score}
                      onChange={e => setSovereignDraft(d => ({ ...d, score: e.target.value }))}
                      className="sv-score-input"
                      placeholder="0"
                      onKeyDown={handleLayerKeyDown}
                    />
                    <div className="sv-guide">
                      <span className="sv-range calibrated">1–100 calibrated</span>
                      <span className="sv-range frontier">101–999 frontier truth</span>
                    </div>
                  </div>
                  {Number(sovereignDraft.score) > 100 && (
                    <div className="frontier-notice">◎ You are marking this as abstract new truth</div>
                  )}
                  <textarea
                    value={sovereignDraft.notes}
                    onChange={e => setSovereignDraft(d => ({ ...d, notes: e.target.value }))}
                    placeholder="Your notes, sources, or reasoning for this layer..."
                    rows={3}
                    className="sv-notes"
                  />
                  <button className="btn primary sv-save" onClick={saveSovereign}>
                    {savedSovereign ? '✓ Saved' : 'Save Sovereign Score'}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
