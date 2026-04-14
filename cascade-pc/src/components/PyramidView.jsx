import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  computeBlockScore, computeFileScore, getScoreBand,
  computePi, checkLayerDependencies, detectTensions,
  detectCascadeEvent, getTruthVelocity,
} from '../scoring/cascade'
import { suggestBlocks, scoreBlock } from '../scoring/ai'
import { FRAMEWORK_LIST } from '../scoring/frameworks'
import OnionEditor from './OnionEditor'
import PyramidViz from './PyramidViz'
import OnionRing from './OnionRing'
import './PyramidView.css'

const SCORE_MODES = ['framework', 'sovereign', 'composite']
const MAX_FILE_BYTES = 500 * 1024 // 500 KB
const WARN_FILE_BYTES = 100 * 1024 // 100 KB

function fmtTime(ts) {
  if (!ts) return null
  const d = new Date(ts * 1000)
  const now = Date.now() / 1000
  const diff = now - ts
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`
  if (diff < 86400) return `${Math.round(diff / 3600)}h ago`
  return d.toLocaleDateString()
}

function fmtBytes(n) {
  if (n < 1024) return `${n}B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)}KB`
  return `${(n / 1024 / 1024).toFixed(1)}MB`
}

export default function PyramidView({ pyramid, onBack }) {
  const [files, setFiles] = useState([])
  const [activeFile, setActiveFile] = useState(null)
  const [blocks, setBlocks] = useState([])
  const [activeBlock, setActiveBlock] = useState(null)
  const [layers, setLayers] = useState([])
  const [addingFile, setAddingFile] = useState(false)
  const [addingBlock, setAddingBlock] = useState(false)
  const [fileName, setFileName] = useState('')
  const [blockTitle, setBlockTitle] = useState('')
  const [blockFrameworks] = useState(['cascade'])
  const [dragging, setDragging] = useState(false)
  const [suggesting, setSuggesting] = useState(false)
  const [rescoring, setRescoring] = useState(false)
  const [aiError, setAiError] = useState('')
  const [scoreMode, setScoreMode] = useState(pyramid.score_display_mode || 'framework')
  const [view, setView] = useState('blocks')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(new Set())
  const [exportMsg, setExportMsg] = useState('')
  const [freshlyScored, setFreshlyScored] = useState(new Set()) // block IDs that just got scored
  const [cascadeEvents, setCascadeEvents] = useState([])
  const [tensions, setTensions] = useState([])
  const [apiCalls, setApiCalls] = useState(0)
  const [saveIndicator, setSaveIndicator] = useState(false)
  const [editingNotes, setEditingNotes] = useState(null) // block id
  const [notesValue, setNotesValue] = useState('')
  const [uploadWarning, setUploadWarning] = useState('')
  const [showHelp, setShowHelp] = useState(false)
  const [showCascadeLog, setShowCascadeLog] = useState(false)
  const [showTensions, setShowTensions] = useState(false)
  const dropRef = useRef(null)

  useEffect(() => { loadFiles() }, [pyramid.id])
  useEffect(() => { if (activeFile) loadBlocks(activeFile.id) }, [activeFile])
  useEffect(() => { if (activeBlock) loadLayers(activeBlock.id) }, [activeBlock])

  // Auto-detect tensions when blocks change
  useEffect(() => {
    if (blocks.length > 1) setTensions(detectTensions(blocks))
  }, [blocks])

  function flashSave() {
    setSaveIndicator(true)
    setTimeout(() => setSaveIndicator(false), 1200)
  }

  function markFreshlyScored(id) {
    setFreshlyScored(s => new Set(s).add(id))
    setTimeout(() => setFreshlyScored(s => { const n = new Set(s); n.delete(id); return n }), 3000)
  }

  function trackApiCall() {
    setApiCalls(n => n + 1)
  }

  async function loadFiles() {
    const list = await window.cascade.files.list(pyramid.id)
    setFiles(list)
    if (list.length > 0 && !activeFile) setActiveFile(list[0])
  }

  async function loadBlocks(fileId) {
    const list = await window.cascade.blocks.list(fileId)
    setBlocks(sortBlocks(list))
  }

  function sortBlocks(list) {
    return [...list].sort((a, b) => {
      const sa = a.score_aggregate || 0
      const sb = b.score_aggregate || 0
      if (sa === 0 && sb === 0) return a.position - b.position
      if (sa === 0) return 1
      if (sb === 0) return -1
      return sb - sa
    })
  }

  async function loadLayers(blockId) {
    const list = await window.cascade.onion.list(blockId)
    setLayers(list)
  }

  async function createFile() {
    if (!fileName.trim()) return
    const file = await window.cascade.files.create({ pyramidId: pyramid.id, name: fileName.trim(), content: '' })
    setFileName('')
    flashSave()
    await loadFiles(); setActiveFile(file)
  }

  async function createFileFromDrop(name, content, size) {
    if (size > MAX_FILE_BYTES) {
      setUploadWarning(`${name} exceeds 500KB limit (${fmtBytes(size)}) — skipped.`)
      setTimeout(() => setUploadWarning(''), 4000)
      return
    }
    let finalContent = content
    if (size > WARN_FILE_BYTES) {
      setUploadWarning(`${name} is large (${fmtBytes(size)}) — using first 100KB for AI context.`)
      setTimeout(() => setUploadWarning(''), 4000)
      finalContent = content.slice(0, WARN_FILE_BYTES)
    }
    const file = await window.cascade.files.create({ pyramidId: pyramid.id, name, content: finalContent })
    flashSave()
    await loadFiles(); setActiveFile(file)
  }

  async function deleteFile(e, id) {
    e.stopPropagation()
    if (!confirm('Delete this file and all its blocks?')) return
    await window.cascade.files.delete(id)
    setActiveFile(null); setBlocks([]); setActiveBlock(null)
    flashSave()
    loadFiles()
  }

  async function createBlock(title, content, fwRefs) {
    if (!title?.trim() || !activeFile) return null
    const block = await window.cascade.blocks.create({
      fileId: activeFile.id, pyramidId: pyramid.id,
      title: title.trim(), content: content?.trim() || '',
      position: blocks.length, frameworkRefs: fwRefs || blockFrameworks,
    })
    setBlockTitle('')
    flashSave()
    await loadBlocks(activeFile.id)
    setActiveBlock(block)
    return block
  }

  async function deleteBlock(e, id) {
    e.stopPropagation()
    if (!confirm('Delete this block?')) return
    await window.cascade.blocks.delete(id)
    if (activeBlock?.id === id) { setActiveBlock(null); setLayers([]) }
    setSelected(s => { const n = new Set(s); n.delete(id); return n })
    flashSave()
    loadBlocks(activeFile.id)
  }

  async function duplicateBlock(e, id) {
    e.stopPropagation()
    const newBlock = await window.cascade.blocks.duplicate(id)
    if (newBlock) {
      flashSave()
      await loadBlocks(activeFile.id)
      setActiveBlock(newBlock)
    }
  }

  async function moveBlock(id, dir) {
    const idx = blocks.findIndex(b => b.id === id)
    if (dir === -1 && idx === 0) return
    if (dir === 1 && idx === blocks.length - 1) return
    const swapIdx = idx + dir
    const a = blocks[idx], b = blocks[swapIdx]
    await window.cascade.blocks.updateScore({ id: a.id, score: a.score_aggregate })
    await window.cascade.blocks.updateScore({ id: b.id, score: b.score_aggregate })
    const newBlocks = [...blocks]
    newBlocks[idx] = { ...b, position: idx }
    newBlocks[swapIdx] = { ...a, position: swapIdx }
    setBlocks(newBlocks)
  }

  async function onLayerSaved() {
    if (!activeBlock || !activeFile) return
    const allLayers = await window.cascade.onion.list(activeBlock.id)
    setLayers(allLayers)
    const oldScore = activeBlock.score_aggregate || 0
    const fwScore = computeBlockScore(allLayers, 'framework')
    const svScore = computeBlockScore(allLayers, 'sovereign')
    await window.cascade.blocks.updateScore({ id: activeBlock.id, score: fwScore, sovereignScore: svScore, scoredAt: Math.floor(Date.now() / 1000) })
    markFreshlyScored(activeBlock.id)

    // Cascade event detection
    const allBlocks = await window.cascade.blocks.list(activeFile.id)
    const event = detectCascadeEvent(activeBlock.id, oldScore, fwScore, allBlocks)
    if (event) {
      setCascadeEvents(prev => [{ ...event, timestamp: Date.now() }, ...prev].slice(0, 20))
    }

    setBlocks(sortBlocks(allBlocks))
    const fileScore = computeFileScore(allBlocks, 'framework')
    await window.cascade.files.updateScore({ id: activeFile.id, score: fileScore })
    flashSave()
  }

  // Notes
  async function saveNotes(blockId) {
    await window.cascade.blocks.updateNotes({ id: blockId, notes: notesValue })
    setBlocks(prev => sortBlocks(prev.map(b => b.id === blockId ? { ...b, notes: notesValue } : b)))
    setEditingNotes(null)
    flashSave()
  }

  // Drag & drop
  function onDragOver(e) { e.preventDefault(); setDragging(true) }
  function onDragLeave() { setDragging(false) }
  function onDrop(e) {
    e.preventDefault(); setDragging(false)
    Array.from(e.dataTransfer.files).forEach(file => {
      if (!file.name.match(/\.(txt|md|markdown|json|csv)$/i)) return
      const reader = new FileReader()
      reader.onload = (ev) => createFileFromDrop(file.name, ev.target.result, file.size)
      reader.readAsText(file)
    })
  }

  // AI: suggest blocks
  async function handleSuggestBlocks() {
    if (!activeFile) return
    setSuggesting(true); setAiError('')
    try {
      trackApiCall()
      const suggestions = await suggestBlocks(activeFile.content || '', activeFile.name)
      for (const s of suggestions) await createBlock(s.title, s.content, blockFrameworks)
      await loadBlocks(activeFile.id)
    } catch (e) { setAiError(e.message) }
    setSuggesting(false)
  }

  // AI: re-score ALL blocks in file
  async function handleReScoreAll() {
    if (!activeFile || blocks.length === 0) return
    setRescoring(true); setAiError('')
    try {
      for (const block of blocks) {
        trackApiCall()
        const scored = await scoreBlock(block.title, block.content, activeFile.content || '', block.framework_refs || ['cascade'])
        const layerList = await window.cascade.onion.list(block.id)
        for (let i = 0; i < scored.length; i++) {
          if (!layerList[i]) continue
          await window.cascade.onion.updateFramework({
            id: layerList[i].id,
            framework_score: scored[i].framework_score,
            framework_reasoning: scored[i].framework_reasoning,
            framework_refs: block.framework_refs || ['cascade'],
          })
        }
        const updated = await window.cascade.onion.list(block.id)
        const fwScore = computeBlockScore(updated, 'framework')
        await window.cascade.blocks.updateScore({ id: block.id, score: fwScore, scoredAt: Math.floor(Date.now() / 1000) })
        markFreshlyScored(block.id)
      }
      const allBlocks = await window.cascade.blocks.list(activeFile.id)
      setBlocks(sortBlocks(allBlocks))
      if (activeBlock) await loadLayers(activeBlock.id)
      flashSave()
    } catch (e) { setAiError(e.message) }
    setRescoring(false)
  }

  // Group scoring
  function toggleSelect(id) {
    setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n })
  }

  const selectedBlocks = blocks.filter(b => selected.has(b.id))
  const groupScore = selected.size > 1
    ? Math.round(selectedBlocks.reduce((a, b) => a + (b.score_aggregate || 0), 0) / selected.size)
    : null

  // Score mode toggle
  async function setMode(mode) {
    setScoreMode(mode)
    await window.cascade.pyramids.setDisplayMode({ id: pyramid.id, mode })
  }

  // Export markdown — save dialog
  async function exportMarkdown() {
    const lines = [`# ${pyramid.name}`, `> Score mode: ${scoreMode}`, '']
    for (const file of files) {
      lines.push(`## ${file.name}  (score: ${file.score_aggregate || '—'})`, '')
      const fileBlocks = await window.cascade.blocks.list(file.id)
      for (const block of fileBlocks) {
        const band = getScoreBand(block.score_aggregate || 0)
        lines.push(`### ${block.title}`)
        lines.push(`**Framework Score:** ${block.score_aggregate || '—'} · ${band.label}`)
        if (block.sovereign_score_aggregate) lines.push(`**Sovereign Score:** ${block.sovereign_score_aggregate}`)
        const ls = await window.cascade.onion.list(block.id)
        ls.forEach(l => {
          if (l.framework_score || l.score) {
            lines.push(`- **${l.layer_name}** ${l.framework_score || l.score} — ${l.framework_reasoning || l.content || ''}`)
          }
        })
        lines.push('')
      }
    }
    const result = await window.cascade.export.save({
      content: lines.join('\n'),
      defaultName: `${pyramid.name.replace(/\s+/g, '_')}.md`,
      ext: 'md',
    })
    if (result.ok) { setExportMsg('Saved!'); setTimeout(() => setExportMsg(''), 2000) }
  }

  // Export JSON — save dialog
  async function exportJSON() {
    const data = { pyramid, files: [] }
    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      const blocksWithLayers = await Promise.all(fileBlocks.map(async b => ({
        ...b, layers: await window.cascade.onion.list(b.id)
      })))
      data.files.push({ ...file, blocks: blocksWithLayers })
    }
    const result = await window.cascade.export.save({
      content: JSON.stringify(data, null, 2),
      defaultName: `${pyramid.name.replace(/\s+/g, '_')}.json`,
      ext: 'json',
    })
    if (result.ok) { setExportMsg('Saved!'); setTimeout(() => setExportMsg(''), 2000) }
  }

  // Summary stats
  const scoredBlocks = blocks.filter(b => b.score_aggregate > 0)
  const avgScore = scoredBlocks.length ? Math.round(scoredBlocks.reduce((a, b) => a + b.score_aggregate, 0) / scoredBlocks.length) : 0
  const strongest = scoredBlocks.reduce((max, b) => b.score_aggregate > (max?.score_aggregate || 0) ? b : max, null)
  const weakest = scoredBlocks.length > 1 ? scoredBlocks.reduce((min, b) => b.score_aggregate < (min?.score_aggregate || 999) ? b : min, null) : null

  // Pi for active block
  const piScore = layers.length >= 4 ? computePi(layers, scoreMode) : null
  const layerViolations = layers.length >= 3 ? checkLayerDependencies(layers, scoreMode) : []

  // Truth velocity for active block (compare previous score to current)
  const activeBlockData = blocks.find(b => b.id === activeBlock?.id)

  const filteredBlocks = blocks.filter(b =>
    !search || b.title.toLowerCase().includes(search.toLowerCase())
  )
  const pyramidBand = getScoreBand(pyramid.score_aggregate || 0)
  const fileScore = activeFile?.score_aggregate || 0
  const fileBand = getScoreBand(fileScore)

  return (
    <div className="pyramid-view">
      {/* Top bar */}
      <div className="pv-topbar">
        <button className="btn" onClick={onBack}>← Pyramids</button>
        <div className="pv-title">
          <span className="pv-name">{pyramid.name}</span>
          {pyramid.score_aggregate > 0 && (
            <span className="pv-score" style={{ color: pyramidBand.textColor }}>
              {pyramid.score_aggregate} · {pyramidBand.label}
            </span>
          )}
        </div>
        <div className="mode-tabs">
          {SCORE_MODES.map(m => (
            <button key={m} className={`mode-tab ${scoreMode === m ? 'active' : ''}`} onClick={() => setMode(m)}>
              {m}
            </button>
          ))}
        </div>
        <div className="view-tabs">
          <button className={`view-tab ${view === 'blocks' ? 'active' : ''}`} onClick={() => setView('blocks')}>Blocks</button>
          <button className={`view-tab ${view === 'pyramid' ? 'active' : ''}`} onClick={() => setView('pyramid')}>△ Viz</button>
          {activeFile && <button className={`view-tab ${view === 'file' ? 'active' : ''}`} onClick={() => setView('file')}>File</button>}
          <button className={`view-tab ${showHelp ? 'active' : ''}`} onClick={() => setShowHelp(!showHelp)}>?</button>
        </div>
        <div className="topbar-right">
          {cascadeEvents.length > 0 && (
            <button className={`btn cascade-log-btn ${cascadeEvents.some(e => e.severity === 'critical') ? 'critical' : ''}`}
              onClick={() => setShowCascadeLog(!showCascadeLog)} title="Cascade event log">
              ⚡ {cascadeEvents.length}
            </button>
          )}
          {tensions.length > 0 && (
            <button className={`btn tension-btn`} onClick={() => setShowTensions(!showTensions)} title="Cross-block tensions">
              ⊗ {tensions.length}
            </button>
          )}
          <span className="api-counter" title="API calls this session">◈ {apiCalls}</span>
          <span className={`save-indicator ${saveIndicator ? 'active' : ''}`}>● saved</span>
          <div className="export-btns">
            {exportMsg
              ? <span className="export-msg">{exportMsg}</span>
              : <>
                  <button className="btn" onClick={exportMarkdown}>↑ MD</button>
                  <button className="btn" onClick={exportJSON}>↑ JSON</button>
                </>
            }
          </div>
        </div>
      </div>

      {/* Upload warning */}
      {uploadWarning && <div className="pv-upload-warn">{uploadWarning}</div>}

      {/* Cascade event log */}
      {showCascadeLog && (
        <div className="cascade-log">
          <div className="cascade-log-header">
            <span>⚡ CASCADE EVENT LOG</span>
            <button className="btn" onClick={() => { setCascadeEvents([]); setShowCascadeLog(false) }}>Clear</button>
          </div>
          {cascadeEvents.map((ev, i) => (
            <div key={i} className={`cascade-event ${ev.severity}`}>
              <span className="ev-severity">{ev.severity.toUpperCase()}</span>
              <span>Block score dropped {ev.drop} pts ({ev.oldScore} → {ev.newScore})</span>
              <span className="ev-time">{fmtTime(Math.floor(ev.timestamp / 1000))}</span>
            </div>
          ))}
        </div>
      )}

      {/* Tension detector */}
      {showTensions && tensions.length > 0 && (
        <div className="tension-panel">
          <div className="tension-header">⊗ CROSS-BLOCK TENSIONS</div>
          {tensions.map((t, i) => (
            <div key={i} className="tension-row">
              <span className="tension-block stronger">{t.stronger.title}</span>
              <span className="tension-delta">Δ{t.delta}</span>
              <span className="tension-block weaker">{t.weaker.title}</span>
            </div>
          ))}
        </div>
      )}

      {/* Help panel */}
      {showHelp && (
        <div className="help-panel">
          <div className="help-title">CASCADE HELP</div>
          <div className="help-grid">
            <div className="help-section">
              <div className="help-sub">SCORING</div>
              <div className="help-row"><span className="help-key">Π = E·P/S</span><span>Evidence × Power ÷ Coherence</span></div>
              <div className="help-row"><span className="help-key">1–100</span><span>Calibrated range</span></div>
              <div className="help-row"><span className="help-key">101–999</span><span>Abstract/frontier truth</span></div>
              <div className="help-row"><span className="help-key">999</span><span>Beyond current verification</span></div>
              <div className="help-row"><span className="help-key">Framework</span><span>AI-scored, locked, Codex-referenced</span></div>
              <div className="help-row"><span className="help-key">Sovereign</span><span>Your truth pressure, free 1–999</span></div>
            </div>
            <div className="help-section">
              <div className="help-sub">LAYERS (9 ONION)</div>
              <div className="help-row"><span className="help-key">AXIOM</span><span>Irreducible core claim</span></div>
              <div className="help-row"><span className="help-key">FOUNDATION</span><span>Primary evidence</span></div>
              <div className="help-row"><span className="help-key">STRUCTURE</span><span>Logical architecture</span></div>
              <div className="help-row"><span className="help-key">COHERENCE</span><span>Internal consistency</span></div>
              <div className="help-row"><span className="help-key">RESONANCE</span><span>Connections to known truths</span></div>
              <div className="help-row"><span className="help-key">TENSION</span><span>Genuine friction (Nigredo)</span></div>
              <div className="help-row"><span className="help-key">CONTESTED</span><span>Active dispute zone</span></div>
              <div className="help-row"><span className="help-key">SPECULATIVE</span><span>Implies beyond proof</span></div>
              <div className="help-row"><span className="help-key">FRONTIER</span><span>Unknown edge</span></div>
            </div>
            <div className="help-section">
              <div className="help-sub">CONSTRAINTS</div>
              <div className="help-row"><span className="help-key">FOUNDATION</span><span>≤ AXIOM × 1.1</span></div>
              <div className="help-row"><span className="help-key">STRUCTURE</span><span>≤ FOUNDATION × 1.2</span></div>
              <div className="help-row"><span className="help-key">Block cap</span><span>≤ AXIOM × 1.2</span></div>
              <div className="help-sub" style={{marginTop:8}}>FILES</div>
              <div className="help-row"><span className="help-key">Max size</span><span>500KB per file</span></div>
              <div className="help-row"><span className="help-key">AI context</span><span>First 100KB used</span></div>
              <div className="help-row"><span className="help-key">Formats</span><span>.txt .md .json .csv</span></div>
            </div>
          </div>
        </div>
      )}

      {/* Group score banner */}
      {selected.size > 1 && (
        <div className="group-bar">
          <span>{selected.size} blocks selected</span>
          {groupScore > 0 && (
            <span className="group-score" style={{ color: getScoreBand(groupScore).textColor }}>
              Group: <strong>{groupScore}</strong> · {getScoreBand(groupScore).label}
            </span>
          )}
          <button className="btn" onClick={() => setSelected(new Set())}>Clear</button>
        </div>
      )}

      {aiError && <div className="pv-ai-error">{aiError}</div>}

      {/* Pyramid viz view */}
      {view === 'pyramid' && (
        <PyramidViz
          blocks={filteredBlocks}
          onSelectBlock={b => { setActiveBlock(b); setView('blocks') }}
          activeBlockId={activeBlock?.id}
          scoreMode={scoreMode}
        />
      )}

      {/* File content view */}
      {view === 'file' && activeFile && (
        <div className="file-content-view">
          <div className="fcv-header">
            {activeFile.name}
            <span className="file-size-badge">{fmtBytes(new TextEncoder().encode(activeFile.content || '').length)}</span>
          </div>
          <pre className="fcv-body">{activeFile.content || '(no content)'}</pre>
        </div>
      )}

      {/* Main blocks view */}
      {view === 'blocks' && (
        <div className="pv-body">
          {/* Files column */}
          <div
            className={`pv-files ${dragging ? 'dragging' : ''}`}
            ref={dropRef}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            <div className="col-header"><span>FILES</span></div>

            {/* Quick-add file input — always visible */}
            <div className="quick-add-wrap">
              <input
                type="text"
                className="quick-add-input"
                placeholder="New file name… Enter to add"
                value={fileName}
                onChange={e => setFileName(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') createFile()
                  if (e.key === 'Escape') setFileName('')
                }}
              />
              <span className="quick-add-hint">or drop .txt .md .json</span>
            </div>

            {/* File-level score bar */}
            {activeFile && fileScore > 0 && (
              <div className="file-score-bar-wrap">
                <div className="file-score-bar" style={{ width: `${Math.min(100, fileScore)}%`, background: fileBand.textColor }} />
                <span className="file-score-label" style={{ color: fileBand.textColor }}>{fileScore} FILE</span>
              </div>
            )}

            {dragging ? (
              <div className="drop-overlay">
                <div>Drop file</div>
                <div className="drop-sub">.txt · .md · .json · max 500KB</div>
              </div>
            ) : (
              <div className="file-list">
                {files.length === 0 && (
                  <div className="col-empty">No files yet</div>
                )}
                {files.map(f => {
                  const band = getScoreBand(f.score_aggregate || 0)
                  return (
                    <div key={f.id} className={`file-item ${activeFile?.id === f.id ? 'active' : ''}`} onClick={() => setActiveFile(f)}>
                      <div className="file-name">{f.name}</div>
                      <div className="file-meta">
                        {f.score_aggregate > 0 ? <span style={{ color: band.textColor }}>{f.score_aggregate}</span> : <span className="dim">—</span>}
                        <button className="btn danger icon-btn" onClick={e => deleteFile(e, f.id)}>×</button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Blocks column */}
          <div className="pv-blocks">
            <div className="col-header">
              <span>BLOCKS</span>
              <div style={{ display: 'flex', gap: 4 }}>
                {activeFile?.content && <button className="btn" onClick={handleSuggestBlocks} disabled={suggesting} title="AI suggest blocks from file">{suggesting ? '...' : '⊚ AI'}</button>}
                {blocks.length > 0 && <button className="btn" onClick={handleReScoreAll} disabled={rescoring} title="Re-score all blocks">{rescoring ? '...' : '↻ All'}</button>}
              </div>
            </div>

            {/* Quick-add block input — always visible when file selected */}
            {activeFile && (
              <div className="quick-add-wrap">
                <input
                  type="text"
                  className="quick-add-input"
                  placeholder="New block title… Enter to add"
                  value={blockTitle}
                  onChange={e => setBlockTitle(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') createBlock(blockTitle, '', blockFrameworks)
                    if (e.key === 'Escape') setBlockTitle('')
                  }}
                />
              </div>
            )}

            {/* Summary stats */}
            {scoredBlocks.length > 0 && (
              <div className="block-stats">
                <span>{blocks.length} · {scoredBlocks.length} scored</span>
                {avgScore > 0 && <span style={{ color: getScoreBand(avgScore).textColor }}>avg {avgScore}</span>}
                {strongest && <span className="stat-strongest">↑ {strongest.title.slice(0, 18)}</span>}
              </div>
            )}

            {/* Search */}
            {blocks.length > 2 && (
              <div className="block-search">
                <input type="text" placeholder="Search…" value={search}
                  onChange={e => setSearch(e.target.value)}
                  onKeyDown={e => e.key === 'Escape' && setSearch('')} />
              </div>
            )}

            <div className="block-list">
              {filteredBlocks.map((b, idx) => {
                const band = getScoreBand(b.score_aggregate || 0)
                const isSelected = selected.has(b.id)
                const isFresh = freshlyScored.has(b.id)
                const pct = Math.min(100, b.score_aggregate || 0)
                const isInTension = tensions.some(t => t.blockA.id === b.id || t.blockB.id === b.id)
                const isEditingNotes = editingNotes === b.id
                return (
                  <div key={b.id}
                    className={`block-item ${activeBlock?.id === b.id ? 'active' : ''} ${isSelected ? 'selected' : ''} ${isFresh ? 'fresh-scored' : ''}`}
                    style={isFresh ? { '--glow-color': band.textColor } : {}}
                    onClick={() => setActiveBlock(b)}>
                    <div className="block-row-top">
                      <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(b.id)} onClick={e => e.stopPropagation()} className="block-check" />
                      <div className="block-title">
                        {b.title}
                        {isInTension && <span className="tension-indicator" title="In tension with another block">⊗</span>}
                      </div>
                      <div className="block-reorder">
                        <button className="btn icon-btn" onClick={e => { e.stopPropagation(); moveBlock(b.id, -1) }}>↑</button>
                        <button className="btn icon-btn" onClick={e => { e.stopPropagation(); moveBlock(b.id, 1) }}>↓</button>
                        <button className="btn icon-btn" onClick={e => duplicateBlock(e, b.id)} title="Duplicate block">⊕</button>
                        <button className="btn danger icon-btn" onClick={e => deleteBlock(e, b.id)}>×</button>
                      </div>
                    </div>

                    {b.content && <div className="block-preview">{b.content.slice(0, 70)}{b.content.length > 70 ? '...' : ''}</div>}

                    {/* Score bar */}
                    {b.score_aggregate > 0 && (
                      <div className="block-score-bar">
                        <div className="block-score-fill" style={{ width: `${pct}%`, background: band.textColor }} />
                      </div>
                    )}

                    <div className="block-meta">
                      {b.score_aggregate > 0
                        ? <span className="block-score" style={{ color: band.textColor }}>{b.score_aggregate} · {band.label}</span>
                        : <span className="dim">unscored</span>}
                      {b.scored_at && <span className="block-ts">{fmtTime(b.scored_at)}</span>}
                      {b.framework_refs?.length > 0 && (
                        <span className="block-refs">{b.framework_refs.map(r => FRAMEWORK_LIST.find(f => f.id === r)?.glyph || r).join(' ')}</span>
                      )}
                      <button className="btn icon-btn notes-btn" onClick={e => { e.stopPropagation(); setEditingNotes(b.id); setNotesValue(b.notes || '') }}
                        title={b.notes ? 'Edit notes' : 'Add notes'}>
                        {b.notes ? '✎' : '✎'}
                      </button>
                    </div>

                    {/* Notes inline editor */}
                    {isEditingNotes && (
                      <div className="block-notes-editor" onClick={e => e.stopPropagation()}>
                        <textarea
                          value={notesValue}
                          onChange={e => setNotesValue(e.target.value)}
                          placeholder="Block notes..."
                          rows={3}
                          autoFocus
                          className="notes-textarea"
                          onKeyDown={e => { if (e.key === 'Escape') setEditingNotes(null) }}
                        />
                        <div className="notes-actions">
                          <button className="btn" onClick={() => setEditingNotes(null)}>Cancel</button>
                          <button className="btn primary" onClick={() => saveNotes(b.id)}>Save</button>
                        </div>
                      </div>
                    )}

                    {/* Show existing notes preview */}
                    {b.notes && !isEditingNotes && (
                      <div className="block-notes-preview">{b.notes.slice(0, 80)}{b.notes.length > 80 ? '...' : ''}</div>
                    )}
                  </div>
                )
              })}
              {filteredBlocks.length === 0 && !addingBlock && activeFile && (
                <div className="col-empty">No blocks{search ? ' matching search' : ''}<br/>{!search && 'Press ⊚ AI or + to add'}</div>
              )}
              {!activeFile && <div className="col-empty">Select a file</div>}
            </div>
          </div>

          {/* Onion editor + ring */}
          <div className="pv-onion">
            {activeBlock ? (
              <div className="onion-with-ring">
                <div className="ring-panel">
                  <OnionRing layers={layers} size={160} />
                  {/* Π score display */}
                  {piScore !== null && piScore > 0 && (
                    <div className="pi-display">
                      <span className="pi-label">Π</span>
                      <span className="pi-value" style={{ color: getScoreBand(piScore).textColor }}>{piScore}</span>
                      <span className="pi-sub">E·P/S</span>
                    </div>
                  )}
                </div>

                {/* Layer dependency warnings */}
                {layerViolations.length > 0 && (
                  <div className="dep-warnings">
                    {layerViolations.map((v, i) => (
                      <div key={i} className="dep-warn">⚠ {v.violation} (cap: {v.cap})</div>
                    ))}
                  </div>
                )}

                <div className="onion-panel">
                  <OnionEditor block={activeBlock} fileContent={activeFile?.content || ''} onSaved={onLayerSaved} />
                </div>
              </div>
            ) : (
              <div className="onion-empty">
                <div className="onion-empty-icon">◎</div>
                <div className="onion-empty-text">Select a block</div>
                <div className="onion-empty-sub">9 layers · AXIOM → FRONTIER</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
