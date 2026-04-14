import React, { useState, useEffect, useRef, useCallback } from 'react'
import { computeBlockScore, computeFileScore, getScoreBand } from '../scoring/cascade'
import { suggestBlocks, scoreBlock } from '../scoring/ai'
import { FRAMEWORK_LIST } from '../scoring/frameworks'
import OnionEditor from './OnionEditor'
import PyramidViz from './PyramidViz'
import OnionRing from './OnionRing'
import './PyramidView.css'

const SCORE_MODES = ['framework', 'sovereign', 'composite']

export default function PyramidView({ pyramid, onBack }) {
  const [files, setFiles] = useState([])
  const [activeFile, setActiveFile] = useState(null)
  const [blocks, setBlocks] = useState([])
  const [activeBlock, setActiveBlock] = useState(null)
  const [layers, setLayers] = useState([])
  const [addingFile, setAddingFile] = useState(false)
  const [addingBlock, setAddingBlock] = useState(false)
  const [fileName, setFileName] = useState('')
  const [fileContent, setFileContent] = useState('')
  const [blockTitle, setBlockTitle] = useState('')
  const [blockContent, setBlockContent] = useState('')
  const [blockFrameworks, setBlockFrameworks] = useState(['cascade'])
  const [dragging, setDragging] = useState(false)
  const [suggesting, setSuggesting] = useState(false)
  const [rescoring, setRescoring] = useState(false)
  const [aiError, setAiError] = useState('')
  const [scoreMode, setScoreMode] = useState(pyramid.score_display_mode || 'framework')
  const [view, setView] = useState('blocks') // 'blocks' | 'pyramid' | 'file'
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(new Set()) // group scoring
  const [exportMsg, setExportMsg] = useState('')
  const dropRef = useRef(null)

  useEffect(() => { loadFiles() }, [pyramid.id])
  useEffect(() => { if (activeFile) loadBlocks(activeFile.id) }, [activeFile])
  useEffect(() => { if (activeBlock) loadLayers(activeBlock.id) }, [activeBlock])

  async function loadFiles() {
    const list = await window.cascade.files.list(pyramid.id)
    setFiles(list)
    if (list.length > 0 && !activeFile) setActiveFile(list[0])
  }

  async function loadBlocks(fileId) {
    const list = await window.cascade.blocks.list(fileId)
    setBlocks(list)
  }

  async function loadLayers(blockId) {
    const list = await window.cascade.onion.list(blockId)
    setLayers(list)
  }

  async function createFile() {
    if (!fileName.trim()) return
    const file = await window.cascade.files.create({ pyramidId: pyramid.id, name: fileName.trim(), content: fileContent.trim() })
    setFileName(''); setFileContent(''); setAddingFile(false)
    await loadFiles(); setActiveFile(file)
  }

  async function createFileFromDrop(name, content) {
    const file = await window.cascade.files.create({ pyramidId: pyramid.id, name, content })
    await loadFiles(); setActiveFile(file)
  }

  async function deleteFile(e, id) {
    e.stopPropagation()
    if (!confirm('Delete this file and all its blocks?')) return
    await window.cascade.files.delete(id)
    setActiveFile(null); setBlocks([]); setActiveBlock(null)
    loadFiles()
  }

  async function createBlock(title, content, fwRefs) {
    if (!title?.trim() || !activeFile) return null
    const block = await window.cascade.blocks.create({
      fileId: activeFile.id, pyramidId: pyramid.id,
      title: title.trim(), content: content?.trim() || '',
      position: blocks.length, frameworkRefs: fwRefs || blockFrameworks,
    })
    setBlockTitle(''); setBlockContent(''); setAddingBlock(false)
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
    loadBlocks(activeFile.id)
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
    const fwScore = computeBlockScore(allLayers, 'framework')
    const svScore = computeBlockScore(allLayers, 'sovereign')
    await window.cascade.blocks.updateScore({ id: activeBlock.id, score: fwScore, sovereignScore: svScore })
    const allBlocks = await window.cascade.blocks.list(activeFile.id)
    setBlocks(allBlocks)
    const fileScore = computeFileScore(allBlocks, 'framework')
    await window.cascade.files.updateScore({ id: activeFile.id, score: fileScore })
  }

  // Drag & drop
  function onDragOver(e) { e.preventDefault(); setDragging(true) }
  function onDragLeave() { setDragging(false) }
  function onDrop(e) {
    e.preventDefault(); setDragging(false)
    Array.from(e.dataTransfer.files).forEach(file => {
      if (!file.name.match(/\.(txt|md|markdown|json|csv)$/i)) return
      const reader = new FileReader()
      reader.onload = (ev) => createFileFromDrop(file.name, ev.target.result)
      reader.readAsText(file)
    })
  }

  // AI: suggest blocks
  async function handleSuggestBlocks() {
    if (!activeFile) return
    setSuggesting(true); setAiError('')
    try {
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
        await window.cascade.blocks.updateScore({ id: block.id, score: fwScore })
      }
      await loadBlocks(activeFile.id)
      if (activeBlock) await loadLayers(activeBlock.id)
    } catch (e) { setAiError(e.message) }
    setRescoring(false)
  }

  // Group scoring
  function toggleSelect(id) {
    setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n })
  }

  const groupScore = selected.size > 1
    ? Math.round(blocks.filter(b => selected.has(b.id)).reduce((a, b) => a + (b.score_aggregate || 0), 0) / selected.size)
    : null

  // Score mode toggle
  async function setMode(mode) {
    setScoreMode(mode)
    await window.cascade.pyramids.setDisplayMode({ id: pyramid.id, mode })
  }

  // Export markdown
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
    const md = lines.join('\n')
    await navigator.clipboard.writeText(md)
    setExportMsg('Markdown copied!')
    setTimeout(() => setExportMsg(''), 2000)
  }

  // Export JSON
  async function exportJSON() {
    const data = { pyramid, files: [] }
    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      const blocksWithLayers = await Promise.all(fileBlocks.map(async b => ({
        ...b, layers: await window.cascade.onion.list(b.id)
      })))
      data.files.push({ ...file, blocks: blocksWithLayers })
    }
    await navigator.clipboard.writeText(JSON.stringify(data, null, 2))
    setExportMsg('JSON copied!')
    setTimeout(() => setExportMsg(''), 2000)
  }

  const filteredBlocks = blocks.filter(b =>
    !search || b.title.toLowerCase().includes(search.toLowerCase())
  )
  const pyramidBand = getScoreBand(pyramid.score_aggregate || 0)

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
        {/* Score mode */}
        <div className="mode-tabs">
          {SCORE_MODES.map(m => (
            <button key={m} className={`mode-tab ${scoreMode === m ? 'active' : ''}`} onClick={() => setMode(m)}>
              {m}
            </button>
          ))}
        </div>
        {/* View toggle */}
        <div className="view-tabs">
          <button className={`view-tab ${view === 'blocks' ? 'active' : ''}`} onClick={() => setView('blocks')}>Blocks</button>
          <button className={`view-tab ${view === 'pyramid' ? 'active' : ''}`} onClick={() => setView('pyramid')}>△ Viz</button>
          {activeFile && <button className={`view-tab ${view === 'file' ? 'active' : ''}`} onClick={() => setView('file')}>File</button>}
        </div>
        {/* Export */}
        <div className="export-btns">
          {exportMsg
            ? <span className="export-msg">{exportMsg}</span>
            : <>
                <button className="btn" onClick={exportMarkdown} title="Copy pyramid as Markdown">↑ MD</button>
                <button className="btn" onClick={exportJSON} title="Copy pyramid as JSON">↑ JSON</button>
              </>
          }
        </div>
      </div>

      {/* Group score banner */}
      {selected.size > 1 && (
        <div className="group-bar">
          <span>{selected.size} blocks selected</span>
          {groupScore > 0 && (
            <span className="group-score" style={{ color: getScoreBand(groupScore).textColor }}>
              Group score: <strong>{groupScore}</strong> · {getScoreBand(groupScore).label}
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
          <div className="fcv-header">{activeFile.name}</div>
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
            <div className="col-header">
              <span>FILES</span>
              <button className="btn" onClick={() => setAddingFile(true)}>+</button>
            </div>

            {dragging ? (
              <div className="drop-overlay">
                <div>Drop file</div>
                <div className="drop-sub">.txt · .md · .json</div>
              </div>
            ) : (
              <>
                {addingFile && (
                  <div className="inline-form">
                    <input type="text" placeholder="File name..." value={fileName} onChange={e => setFileName(e.target.value)} autoFocus onKeyDown={e => { if (e.key === 'Enter') createFile(); if (e.key === 'Escape') { setAddingFile(false); setFileName('') }}} />
                    <textarea placeholder="Paste content..." value={fileContent} onChange={e => setFileContent(e.target.value)} rows={3} />
                    <div className="form-actions">
                      <button className="btn" onClick={() => { setAddingFile(false); setFileName('') }}>Cancel</button>
                      <button className="btn primary" onClick={createFile}>Add</button>
                    </div>
                  </div>
                )}
                {files.length === 0 && !addingFile && (
                  <div className="col-empty drop-hint">Drop .txt/.md<br/>or press + to add</div>
                )}
                <div className="file-list">
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
              </>
            )}
          </div>

          {/* Blocks column */}
          <div className="pv-blocks">
            <div className="col-header">
              <span>BLOCKS</span>
              <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                {activeFile?.content && <button className="btn" onClick={handleSuggestBlocks} disabled={suggesting} title="AI suggest blocks">{suggesting ? '...' : '⊚ AI'}</button>}
                {blocks.length > 0 && <button className="btn" onClick={handleReScoreAll} disabled={rescoring} title="Re-score all blocks">{rescoring ? '...' : '↻ All'}</button>}
                {activeFile && <button className="btn" onClick={() => setAddingBlock(true)}>+</button>}
              </div>
            </div>

            {/* Search */}
            {blocks.length > 2 && (
              <div className="block-search">
                <input type="text" placeholder="Search blocks..." value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Escape' && setSearch('')} />
              </div>
            )}

            {/* Framework selector for new blocks */}
            {addingBlock && (
              <div className="inline-form">
                <input type="text" placeholder="Block title..." value={blockTitle} onChange={e => setBlockTitle(e.target.value)} autoFocus
                  onKeyDown={e => { if (e.key === 'Enter') createBlock(blockTitle, blockContent, blockFrameworks); if (e.key === 'Escape') { setAddingBlock(false); setBlockTitle('') }}} />
                <textarea placeholder="Block content..." value={blockContent} onChange={e => setBlockContent(e.target.value)} rows={2} />
                <div className="fw-selector">
                  <span className="fw-sel-label">Score against:</span>
                  {FRAMEWORK_LIST.map(f => (
                    <button key={f.id}
                      className={`fw-chip-sm ${blockFrameworks.includes(f.id) ? 'active' : ''}`}
                      onClick={() => setBlockFrameworks(prev => prev.includes(f.id) ? prev.filter(x => x !== f.id) || ['cascade'] : [...prev, f.id])}
                      style={blockFrameworks.includes(f.id) ? { color: f.color, borderColor: f.color } : {}}>
                      {f.glyph} {f.name}
                    </button>
                  ))}
                </div>
                <div className="form-actions">
                  <button className="btn" onClick={() => { setAddingBlock(false); setBlockTitle('') }}>Cancel</button>
                  <button className="btn primary" onClick={() => createBlock(blockTitle, blockContent, blockFrameworks)}>Add</button>
                </div>
              </div>
            )}

            <div className="block-list">
              {filteredBlocks.map((b, idx) => {
                const band = getScoreBand(b.score_aggregate || 0)
                const isSelected = selected.has(b.id)
                return (
                  <div key={b.id} className={`block-item ${activeBlock?.id === b.id ? 'active' : ''} ${isSelected ? 'selected' : ''}`}
                    onClick={() => setActiveBlock(b)}>
                    <div className="block-row-top">
                      <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(b.id)} onClick={e => e.stopPropagation()} className="block-check" />
                      <div className="block-title">{b.title}</div>
                      <div className="block-reorder">
                        <button className="btn icon-btn" onClick={e => { e.stopPropagation(); moveBlock(b.id, -1) }}>↑</button>
                        <button className="btn icon-btn" onClick={e => { e.stopPropagation(); moveBlock(b.id, 1) }}>↓</button>
                        <button className="btn danger icon-btn" onClick={e => deleteBlock(e, b.id)}>×</button>
                      </div>
                    </div>
                    {b.content && <div className="block-preview">{b.content.slice(0, 70)}{b.content.length > 70 ? '...' : ''}</div>}
                    <div className="block-meta">
                      {b.score_aggregate > 0
                        ? <span className="block-score" style={{ color: band.textColor }}>{b.score_aggregate} · {band.label}</span>
                        : <span className="dim">unscored</span>}
                      {b.framework_refs?.length > 0 && (
                        <span className="block-refs">{b.framework_refs.map(r => FRAMEWORK_LIST.find(f => f.id === r)?.glyph || r).join(' ')}</span>
                      )}
                    </div>
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
                </div>
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
