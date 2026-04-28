import React, { useState, useEffect, useRef, useCallback } from 'react'
import {
  computeBlockScore, computeFileScore, getScoreBand,
  computePi, checkLayerDependencies, detectTensions,
  detectCascadeEvent, getTruthVelocity, isAxiomUnfalsifiable,
  computeConfidenceWeightedScore,
} from '../scoring/cascade'
import { suggestBlocks, scoreBlock, synthesizePyramid, crossSynthesize, synthesizeBlocks, adversarialScore, consensusScore, recursiveSynthesize } from '../scoring/ai'
import { getAllFrameworks } from '../scoring/frameworks'
const FRAMEWORK_LIST = getAllFrameworks()
import OnionEditor from './OnionEditor'
import PyramidViz from './PyramidViz'
import OnionRing from './OnionRing'
import HealthDashboard from './HealthDashboard'
import KnowledgeGraph from './KnowledgeGraph'
import ContradictionMap from './ContradictionMap'
import './PyramidView.css'

const SCORE_MODES = ['framework', 'sovereign', 'composite']

function Sparkline({ history, width = 60, height = 18 }) {
  if (!history || history.length < 2) return null
  const scores = history.map(h => h.score)
  const min = Math.min(...scores)
  const max = Math.max(...scores)
  const range = max - min || 1
  const pts = scores.map((s, i) => {
    const x = (i / (scores.length - 1)) * width
    const y = height - ((s - min) / range) * height
    return `${x},${y}`
  }).join(' ')
  const last = scores[scores.length - 1]
  const prev = scores[scores.length - 2]
  const trend = last > prev ? '#4ade80' : last < prev ? '#f87171' : '#888'
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      <polyline points={pts} fill="none" stroke={trend} strokeWidth="1.5" opacity="0.8" />
      <circle cx={(scores.length - 1) / (scores.length - 1) * width} cy={height - ((last - min) / range) * height} r="2" fill={trend} />
    </svg>
  )
}
const MAX_FILE_BYTES = 500 * 1024 // 500 KB
const WARN_FILE_BYTES = 100 * 1024 // 100 KB
const SCORE_CONCURRENCY = 3

// Run async tasks with a max concurrency limit
async function runConcurrent(items, fn, limit = SCORE_CONCURRENCY) {
  const results = []
  let idx = 0
  async function worker() {
    while (idx < items.length) {
      const i = idx++
      results[i] = await fn(items[i], i)
    }
  }
  const workers = Array.from({ length: Math.min(limit, items.length) }, worker)
  await Promise.all(workers)
  return results
}

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
  const [editingTags, setEditingTags] = useState(null) // block id
  const [tagsInput, setTagsInput] = useState('') // comma-separated
  const [tagFilter, setTagFilter] = useState('')
  const [draggedBlockId, setDraggedBlockId] = useState(null)
  const [dragOverFileId, setDragOverFileId] = useState(null)
  const [uploadWarning, setUploadWarning] = useState('')
  const [showHelp, setShowHelp] = useState(false)
  const [showCascadeLog, setShowCascadeLog] = useState(false)
  const [showTensions, setShowTensions] = useState(false)
  const [expandedBlocks, setExpandedBlocks] = useState(new Set())
  const [scoringAll, setScoringAll] = useState(false)
  const [scoreAllProgress, setScoreAllProgress] = useState('')
  const [synthesizing, setSynthesizing] = useState(false)
  const [synthesis, setSynthesis] = useState(null)
  const [showSynthesis, setShowSynthesis] = useState(false)
  const [crossFileIds, setCrossFileIds] = useState(new Set())
  const [crossSynthesizing, setCrossSynthesizing] = useState(false)
  const [crossResult, setCrossResult] = useState(null)
  const [showCrossResult, setShowCrossResult] = useState(false)

  function toggleCrossFile(id) {
    setCrossFileIds(s => {
      const n = new Set(s)
      n.has(id) ? n.delete(id) : n.size < 10 ? n.add(id) : null
      return n
    })
  }
  const [blockSynthesizing, setBlockSynthesizing] = useState(false)
  const [blockSynthResult, setBlockSynthResult] = useState(null)
  const [showBlockSynth, setShowBlockSynth] = useState(false)
  // Recursive synthesis
  const [recursiveSynthesizing, setRecursiveSynthesizing] = useState(false)
  const [recursiveResult, setRecursiveResult] = useState(null)
  const [showRecursiveResult, setShowRecursiveResult] = useState(false)
  // Adversarial rescore state — keyed by blockId
  const [adversarialData, setAdversarialData] = useState({}) // { [blockId]: { layers, gap, status } }
  const [adversarialLoading, setAdversarialLoading] = useState(null) // blockId being challenged
  // Consensus scoring
  const [consensusData, setConsensusData] = useState({}) // keyed by blockId
  const [consensusLoading, setConsensusLoading] = useState(null)
  // Score transparency
  const [showAudit, setShowAudit] = useState(false)
  // Notifications
  const [toasts, setToasts] = useState([]) // { id, msg, type }
  const [notifHistory, setNotifHistory] = useState([])
  const [showNotifPanel, setShowNotifPanel] = useState(false)
  const notifIdRef = useRef(0)
  // Block versioning
  const [showVersions, setShowVersions] = useState(false)
  const [versionData, setVersionData] = useState([])
  // Session audit log
  const [auditLog, setAuditLog] = useState([])
  const [auditLogLoading, setAuditLogLoading] = useState(false)
  const dropRef = useRef(null)

  function toggleExpand(e, id) {
    e.stopPropagation()
    setExpandedBlocks(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n })
  }

  useEffect(() => { loadFiles() }, [pyramid.id])
  useEffect(() => { if (activeFile) loadBlocks(activeFile.id) }, [activeFile])
  useEffect(() => { if (activeBlock) loadLayers(activeBlock.id) }, [activeBlock])

  // Computed early — needed by keyboard shortcut useEffect below
  const filteredBlocks = blocks.filter(b => {
    if (search && !b.title.toLowerCase().includes(search.toLowerCase())) return false
    if (tagFilter && !(b.tags || []).includes(tagFilter)) return false
    return true
  })

  // Keyboard shortcuts
  useEffect(() => {
    function onKey(e) {
      // Skip if focus is inside a text input / textarea
      const tag = document.activeElement?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA') return
      // Ctrl/Cmd combos
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'k') { e.preventDefault(); document.querySelector('.block-search input')?.focus() }
        if (e.key === 'e') { e.preventDefault(); exportMarkdown() }
        if (e.key === 'h') { e.preventDefault(); setShowHelp(h => !h) }
        return
      }
      // Navigate blocks with arrow keys when a block is active
      if (activeBlock && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
        const idx = filteredBlocks.findIndex(b => b.id === activeBlock.id)
        if (idx === -1) return
        const next = e.key === 'ArrowUp' ? filteredBlocks[idx - 1] : filteredBlocks[idx + 1]
        if (next) setActiveBlock(next)
        e.preventDefault()
      }
      // V — cycle view tabs
      if (e.key === 'v') {
        const tabs = ['blocks', 'pyramid', 'health', 'graph', 'audit']
        const idx = tabs.indexOf(view)
        setView(tabs[(idx + 1) % tabs.length])
      }
      // P — pin active block
      if (e.key === 'p' && activeBlock) {
        const block = blocks.find(b => b.id === activeBlock.id)
        if (block) togglePin({ stopPropagation: () => {} }, block)
      }
      // S — snapshot active block
      if (e.key === 's' && activeBlock) saveVersion(activeBlock)
      // Escape — deselect, close panels
      if (e.key === 'Escape') {
        setSelected(new Set())
        setShowSynthesis(false)
        setShowBlockSynth(false)
        setShowCrossResult(false)
        setShowVersions(false)
        setShowAudit(false)
        setShowHelp(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [activeBlock, filteredBlocks, view, blocks])

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

  function notify(msg, type = 'info') {
    const id = ++notifIdRef.current
    const entry = { id, msg, type, ts: Math.floor(Date.now() / 1000) }
    setToasts(prev => [...prev, entry])
    setNotifHistory(prev => [entry, ...prev].slice(0, 50))
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500)
  }

  async function recordScore(blockId, score) {
    if (score > 0) {
      await window.cascade.blocks.appendHistory({ id: blockId, score, ts: Math.floor(Date.now() / 1000) })
    }
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
      // Pinned blocks always float to top
      if (a.pinned && !b.pinned) return -1
      if (!a.pinned && b.pinned) return 1
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
    const newBlocks = [...blocks]
    newBlocks[idx] = { ...b, position: idx }
    newBlocks[swapIdx] = { ...a, position: swapIdx }
    setBlocks(newBlocks)
    await window.cascade.blocks.updatePosition({ id: a.id, position: swapIdx })
    await window.cascade.blocks.updatePosition({ id: b.id, position: idx })
  }

  // Cross-file block move via drag-and-drop
  async function moveBlockToFile(blockId, targetFileId) {
    if (!targetFileId || !activeFile) return
    if (targetFileId === activeFile.id) return // same file — no-op
    const block = blocks.find(b => b.id === blockId)
    if (!block) return
    // Create copy in target file, delete from current
    await window.cascade.blocks.create({
      fileId: targetFileId, pyramidId: pyramid.id,
      title: block.title, content: block.content || '',
      position: 0, frameworkRefs: block.framework_refs || ['cascade'],
      sourceBlockIds: block.source_block_ids || null,
      lineageScore: block.lineage_score || null,
    })
    await window.cascade.blocks.delete(blockId)
    if (activeBlock?.id === blockId) { setActiveBlock(null); setLayers([]) }
    flashSave()
    notify(`Block moved to ${files.find(f => f.id === targetFileId)?.name || 'file'}`, 'info')
    await loadBlocks(activeFile.id)
    await loadFiles()
  }

  async function onLayerSaved() {
    if (!activeBlock || !activeFile) return
    const allLayers = await window.cascade.onion.list(activeBlock.id)
    setLayers(allLayers)
    const oldScore = activeBlock.score_aggregate || 0
    const fwScore = computeBlockScore(allLayers, 'framework')
    const svScore = computeBlockScore(allLayers, 'sovereign')
    await window.cascade.blocks.updateScore({ id: activeBlock.id, score: fwScore, sovereignScore: svScore, scoredAt: Math.floor(Date.now() / 1000) })
    await recordScore(activeBlock.id, fwScore)
    markFreshlyScored(activeBlock.id)
    await window.cascade.audit.log({ action: 'score', blockId: activeBlock.id, blockTitle: activeBlock.title, detail: `fw:${fwScore} sv:${svScore}` })

    // Cascade event detection
    const allBlocks = await window.cascade.blocks.list(activeFile.id)
    const event = detectCascadeEvent(activeBlock.id, oldScore, fwScore, allBlocks)
    if (event) {
      setCascadeEvents(prev => [{ ...event, timestamp: Date.now() }, ...prev].slice(0, 20))
      // Cascade Pressure Wave — score change >15 triggers re-evaluation of all other blocks
      if (event.drop >= 15) {
        const affected = allBlocks.filter(b => b.id !== activeBlock.id && b.score_aggregate > 0)
        if (affected.length > 0) {
          notify(`⚡ Pressure wave — rescoring ${affected.length} blocks`, 'warn')
          setScoreAllProgress('⚡ Pressure wave…')
          setScoringAll(true)
          try {
            await runConcurrent(affected, async (block) => {
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
                  ...(i === 0 && scored[i].falsifiable !== undefined ? { falsifiable: scored[i].falsifiable } : {}),
                  ...(i === 0 && scored[i].score_audit ? { score_audit: scored[i].score_audit } : {}),
                })
              }
              const updated = await window.cascade.onion.list(block.id)
              const pressureScore = computeBlockScore(updated, 'framework')
              await window.cascade.blocks.updateScore({ id: block.id, score: pressureScore, scoredAt: Math.floor(Date.now() / 1000) })
              await recordScore(block.id, pressureScore)
              markFreshlyScored(block.id)
            })
          } catch (e) { setAiError(e.message) }
          setScoringAll(false); setScoreAllProgress('')
        }
      }
    }

    const refreshed = await window.cascade.blocks.list(activeFile.id)
    setBlocks(sortBlocks(refreshed))
    const fileScore = computeFileScore(refreshed, 'framework')
    await window.cascade.files.updateScore({ id: activeFile.id, score: fileScore })
    flashSave()
  }

  // Tags
  async function saveTags(blockId) {
    const tags = tagsInput.split(',').map(t => t.trim().toLowerCase()).filter(Boolean)
    await window.cascade.blocks.setTags({ id: blockId, tags })
    setBlocks(prev => sortBlocks(prev.map(b => b.id === blockId ? { ...b, tags } : b)))
    setEditingTags(null)
    flashSave()
  }

  // Collect all tags across the current file for the tag filter dropdown
  const allTags = [...new Set(blocks.flatMap(b => b.tags || []))].sort()

  // Pin / Star
  async function togglePin(e, block) {
    e.stopPropagation()
    const newPinned = !block.pinned
    await window.cascade.blocks.pin({ id: block.id, pinned: newPinned })
    setBlocks(prev => sortBlocks(prev.map(b => b.id === block.id ? { ...b, pinned: newPinned } : b)))
    await window.cascade.audit.log({ action: newPinned ? 'pin' : 'unpin', blockId: block.id, blockTitle: block.title })
    flashSave()
  }

  // Block version history
  async function loadVersions(blockId) {
    const versions = await window.cascade.blocks.getVersions(blockId)
    setVersionData(versions)
    setShowVersions(true)
  }

  async function saveVersion(block) {
    await window.cascade.blocks.saveVersion({ id: block.id })
    await window.cascade.audit.log({ action: 'save_version', blockId: block.id, blockTitle: block.title, detail: `v${(block.versions?.length || 0) + 1}` })
    flashSave()
  }

  // Session audit log
  async function loadAuditLog() {
    setAuditLogLoading(true)
    const log = await window.cascade.audit.get()
    setAuditLog(log)
    setAuditLogLoading(false)
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

  // AI: synthesize all scored blocks into unified truth
  async function handleSynthesize() {
    setSynthesizing(true); setAiError('')
    try {
      // Gather all blocks across all files
      let allBlocks = []
      for (const file of files) {
        const fileBlocks = await window.cascade.blocks.list(file.id)
        allBlocks = allBlocks.concat(fileBlocks)
      }
      const scored = allBlocks.filter(b => b.score_aggregate > 0)
      if (scored.length === 0) { setAiError('No scored blocks to synthesize.'); setSynthesizing(false); return }
      trackApiCall()
      const result = await synthesizePyramid(pyramid.name, scored)
      setSynthesis(result)
      setShowSynthesis(true)
    } catch (e) { setAiError(e.message) }
    setSynthesizing(false)
  }

  // AI: synthesize selected blocks (2–10)
  async function handleSynthesizeBlocks() {
    if (selectedBlocks.length < 2 || selectedBlocks.length > 10) return
    setBlockSynthesizing(true); setAiError(''); setBlockSynthResult(null)
    try {
      trackApiCall()
      const result = await synthesizeBlocks(selectedBlocks)
      setBlockSynthResult(result)
      setShowBlockSynth(true)
    } catch (e) { setAiError(e.message) }
    setBlockSynthesizing(false)
  }

  // AI: adversarial rescore — challenges a block's score, produces CI gap
  async function handleAdversarialScore(block) {
    if (!block || !activeFile) return
    setAdversarialLoading(block.id); setAiError('')
    try {
      trackApiCall()
      const adversarialLayers = await adversarialScore(block.title, block.content, activeFile.content || '', block.framework_refs || ['cascade'])
      const advScore = computeBlockScore(adversarialLayers, 'framework')
      const normalScore = block.score_aggregate || 0
      const gap = Math.abs(normalScore - advScore)
      let stability
      if (gap < 10) stability = 'stable'
      else if (gap <= 25) stability = 'uncertain'
      else stability = 'inflated'
      setAdversarialData(prev => ({
        ...prev,
        [block.id]: { layers: adversarialLayers, advScore, normalScore, gap, stability },
      }))
      notify(`⊗ Challenge: ${stability} · gap ±${gap}`, stability === 'inflated' ? 'warn' : 'info')
    } catch (e) { setAiError(e.message) }
    setAdversarialLoading(null)
  }

  // AI: consensus score — all configured providers
  async function handleConsensusScore(block) {
    if (!block || !activeFile) return
    setConsensusLoading(block.id); setAiError('')
    try {
      trackApiCall()
      const result = await consensusScore(block.title, block.content, activeFile.content || '', block.framework_refs || ['cascade'])
      setConsensusData(prev => ({ ...prev, [block.id]: result }))
    } catch (e) { setAiError(e.message) }
    setConsensusLoading(null)
  }

  // AI: cross-synthesize multiple files
  async function handleCrossSynthesize() {
    if (crossFileIds.size < 2) return
    setCrossSynthesizing(true); setAiError(''); setCrossResult(null)
    try {
      const selectedFiles = files.filter(f => crossFileIds.has(f.id))
      const filesWithBlocks = await Promise.all(
        selectedFiles.map(async f => ({
          name: f.name,
          blocks: await window.cascade.blocks.list(f.id),
        }))
      )
      trackApiCall()
      const result = await crossSynthesize(filesWithBlocks)
      setCrossResult({ ...result, fileNames: selectedFiles.map(f => f.name) })
      setShowCrossResult(true)
    } catch (e) { setAiError(e.message) }
    setCrossSynthesizing(false)
  }

  // AI: recursive synthesis — upgrade a synthesis block with new blocks
  async function handleRecursiveSynthesize(synthesisBlock) {
    if (!synthesisBlock?.is_synthesis) return
    setRecursiveSynthesizing(true); setAiError(''); setRecursiveResult(null)
    try {
      // New blocks = scored blocks NOT in the original synthesis's source_block_ids
      const sourceIds = new Set(synthesisBlock.source_block_ids || [])
      const newBlocks = blocks.filter(b => b.score_aggregate > 0 && !sourceIds.has(b.id) && b.id !== synthesisBlock.id)
      if (newBlocks.length === 0) {
        setAiError('No new scored blocks to upgrade with. Score more blocks first.')
        setRecursiveSynthesizing(false); return
      }
      trackApiCall()
      const result = await recursiveSynthesize(synthesisBlock, newBlocks)
      setRecursiveResult({ ...result, synthesisBlock, newBlocks })
      setShowRecursiveResult(true)
      notify(`◎ Recursive synthesis ready — ${newBlocks.length} new blocks integrated`, 'success')
    } catch (e) { setAiError(e.message) }
    setRecursiveSynthesizing(false)
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

  // AI: full pipeline across ALL files — extract blocks if missing, then score everything
  async function handleScoreAllFiles() {
    if (files.length === 0) return
    setScoringAll(true); setAiError('')
    try {
      for (let fi = 0; fi < files.length; fi++) {
        const file = files[fi]
        let fileBlocks = await window.cascade.blocks.list(file.id)

        // Step 1: if file has content but no blocks, extract them first
        if (fileBlocks.length === 0 && file.content?.trim()) {
          setScoreAllProgress(`File ${fi + 1}/${files.length} · Extracting blocks…`)
          trackApiCall()
          const suggestions = await suggestBlocks(file.content, file.name)
          for (const s of suggestions) {
            await window.cascade.blocks.create({
              fileId: file.id, pyramidId: pyramid.id,
              title: s.title, content: s.content || '',
              position: 0, frameworkRefs: ['cascade'],
            })
          }
          fileBlocks = await window.cascade.blocks.list(file.id)
        }

        if (fileBlocks.length === 0) continue // no content, skip

        // Step 2: score blocks — 3 concurrent
        let doneCount = 0
        await runConcurrent(fileBlocks, async (block) => {
          trackApiCall()
          const scored = await scoreBlock(block.title, block.content, file.content || '', block.framework_refs || ['cascade'])
          const layerList = await window.cascade.onion.list(block.id)
          for (let i = 0; i < scored.length; i++) {
            if (!layerList[i]) continue
            await window.cascade.onion.updateFramework({
              id: layerList[i].id,
              framework_score: scored[i].framework_score,
              framework_reasoning: scored[i].framework_reasoning,
              framework_refs: block.framework_refs || ['cascade'],
              ...(i === 0 && scored[i].falsifiable !== undefined ? { falsifiable: scored[i].falsifiable } : {}),
              ...(i === 0 && scored[i].score_audit ? { score_audit: scored[i].score_audit } : {}),
            })
          }
          const updated = await window.cascade.onion.list(block.id)
          const fwScore = computeBlockScore(updated, 'framework')
          await window.cascade.blocks.updateScore({ id: block.id, score: fwScore, scoredAt: Math.floor(Date.now() / 1000) })
          await recordScore(block.id, fwScore)
          markFreshlyScored(block.id)
          doneCount++
          setScoreAllProgress(`File ${fi + 1}/${files.length} · ${doneCount}/${fileBlocks.length} blocks`)
        })

        // Step 3: update file aggregate score
        const updatedBlocks = await window.cascade.blocks.list(file.id)
        const fScore = computeFileScore(updatedBlocks, 'framework')
        await window.cascade.files.updateScore({ id: file.id, score: fScore })
      }

      // Reload current view
      await loadFiles()
      if (activeFile) await loadBlocks(activeFile.id)
      if (activeBlock) await loadLayers(activeBlock.id)
      flashSave()
    } catch (e) { setAiError(e.message) }
    setScoringAll(false); setScoreAllProgress('')
  }

  // AI: re-score ALL blocks in file (3 concurrent)
  async function handleReScoreAll() {
    if (!activeFile || blocks.length === 0) return
    setRescoring(true); setAiError('')
    try {
      await runConcurrent(blocks, async (block) => {
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
        await recordScore(block.id, fwScore)
        markFreshlyScored(block.id)
      })
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
    if (result.ok) { setExportMsg('Saved!'); setTimeout(() => setExportMsg(''), 2000); notify('Markdown exported', 'success') }
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

  // Export .cascade — portable structured format
  async function exportCascade() {
    const data = {
      cascade_version: '0.3.0',
      exported_at: new Date().toISOString(),
      pyramid,
      files: [],
    }
    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      const blocksWithLayers = await Promise.all(fileBlocks.map(async b => ({
        ...b, layers: await window.cascade.onion.list(b.id)
      })))
      data.files.push({ ...file, blocks: blocksWithLayers })
    }
    const result = await window.cascade.export.save({
      content: JSON.stringify(data, null, 2),
      defaultName: `${pyramid.name.replace(/\s+/g, '_')}.cascade`,
      ext: 'cascade',
    })
    if (result.ok) { setExportMsg('Saved!'); setTimeout(() => setExportMsg(''), 2000) }
  }

  // Export static HTML — self-contained readable document
  async function exportHTML() {
    const allData = []
    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      const blocksWithLayers = await Promise.all(fileBlocks.map(async b => ({
        ...b, layers: await window.cascade.onion.list(b.id)
      })))
      allData.push({ ...file, blocks: blocksWithLayers })
    }

    const bandColor = (s) => {
      if (!s || s === 0) return '#555'
      if (s <= 20) return '#e879f9'
      if (s <= 40) return '#60a5fa'
      if (s <= 60) return '#4ade80'
      if (s <= 80) return '#facc15'
      if (s <= 100) return '#fb923c'
      return '#c084fc'
    }

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${pyramid.name} — CASCADE Pyramid</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a0a; color: #e5e5e5; font-family: 'Courier New', monospace; padding: 40px; max-width: 900px; margin: 0 auto; }
  h1 { color: #d4af37; font-size: 18px; letter-spacing: 0.2em; margin-bottom: 6px; }
  .meta { font-size: 11px; color: #555; margin-bottom: 40px; }
  .file-section { margin-bottom: 48px; }
  .file-title { font-size: 11px; letter-spacing: 0.2em; color: #888; border-bottom: 1px solid #222; padding-bottom: 8px; margin-bottom: 20px; }
  .block { background: #111; border: 1px solid #222; border-radius: 6px; padding: 20px; margin-bottom: 16px; }
  .block-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 10px; }
  .block-title { font-size: 13px; color: #fff; flex: 1; }
  .block-score { font-size: 12px; font-weight: bold; }
  .synth-glyph { color: #d4af37; font-size: 11px; }
  .block-content { font-size: 12px; color: #999; line-height: 1.6; margin-bottom: 14px; }
  .layers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .layer { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 4px; padding: 10px; }
  .layer-name { font-size: 9px; letter-spacing: 0.15em; color: #555; margin-bottom: 4px; }
  .layer-score { font-size: 14px; font-weight: bold; margin-bottom: 4px; }
  .layer-reason { font-size: 10px; color: #666; line-height: 1.4; }
  .ci-badge { font-size: 10px; padding: 2px 6px; border-radius: 3px; border: 1px solid currentColor; }
  footer { margin-top: 60px; font-size: 10px; color: #333; text-align: center; }
</style>
</head>
<body>
<h1>${pyramid.name}</h1>
<div class="meta">CASCADE CICADA TOOL v0.3.0 · Exported ${new Date().toLocaleDateString()} · Score mode: ${scoreMode}</div>
${allData.map(file => `
<div class="file-section">
  <div class="file-title">${file.name}${file.score_aggregate ? ` · ${file.score_aggregate}` : ''}</div>
  ${file.blocks.map(block => `
  <div class="block">
    <div class="block-header">
      ${block.is_synthesis ? '<span class="synth-glyph">◎</span>' : ''}
      <span class="block-title">${block.title}</span>
      ${block.score_aggregate ? `<span class="block-score" style="color:${bandColor(block.score_aggregate)}">${block.score_aggregate}</span>` : ''}
    </div>
    ${block.content ? `<div class="block-content">${block.content}</div>` : ''}
    <div class="layers">
      ${block.layers.map(l => `
      <div class="layer">
        <div class="layer-name">${l.layer_name}</div>
        <div class="layer-score" style="color:${bandColor(l.framework_score)}">${l.framework_score || '—'}</div>
        <div class="layer-reason">${l.framework_reasoning || ''}</div>
      </div>`).join('')}
    </div>
  </div>`).join('')}
</div>`).join('')}
<footer>Built with CASCADE CICADA TOOL · Lycheetah Framework · github.com/Lycheetah/cascade-cicada-tool-</footer>
</body>
</html>`

    const result = await window.cascade.export.save({
      content: html,
      defaultName: `${pyramid.name.replace(/\s+/g, '_')}.html`,
      ext: 'html',
    })
    if (result.ok) { setExportMsg('HTML saved!'); setTimeout(() => setExportMsg(''), 2000); notify('HTML exported', 'success') }
  }

  // Full data dump — everything
  async function exportFullDump() {
    const result = await window.cascade.export.fullDump()
    if (result.ok) { setExportMsg('Full dump saved!'); setTimeout(() => setExportMsg(''), 2000); notify('Full dump exported', 'success') }
  }

  // Export: Review Package — full scoring + sovereign notes, ready to share
  async function exportReviewPackage() {
    const pkgData = {
      review_version: '1.0',
      generated_at: new Date().toISOString(),
      pyramid: { id: pyramid.id, name: pyramid.name, description: pyramid.description },
      score_mode: scoreMode,
      files: [],
    }
    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      const blocksWithData = await Promise.all(fileBlocks.map(async b => {
        const layers = await window.cascade.onion.list(b.id)
        return {
          id: b.id,
          title: b.title,
          content: b.content || '',
          framework_score: b.score_aggregate || 0,
          sovereign_score: b.sovereign_score_aggregate || 0,
          notes: b.notes || '',
          tags: b.tags || [],
          pinned: b.pinned || false,
          is_synthesis: b.is_synthesis || false,
          lineage_score: b.lineage_score || null,
          scored_at: b.scored_at || null,
          layers: layers.map(l => ({
            name: l.layer_name,
            framework_score: l.framework_score || 0,
            framework_reasoning: l.framework_reasoning || '',
            sovereign_score: l.sovereign_score || 0,
            sovereign_notes: l.sovereign_notes || '',
            falsifiable: l.falsifiable,
          })),
          adversarial: adversarialData[b.id] ? {
            adv_score: adversarialData[b.id].advScore,
            gap: adversarialData[b.id].gap,
            stability: adversarialData[b.id].stability,
          } : null,
        }
      }))
      pkgData.files.push({ name: file.name, score: file.score_aggregate || 0, blocks: blocksWithData })
    }
    const result = await window.cascade.export.save({
      content: JSON.stringify(pkgData, null, 2),
      defaultName: `${pyramid.name.replace(/\s+/g, '_')}_review_package.json`,
      ext: 'json',
    })
    if (result.ok) { setExportMsg('Review package saved!'); setTimeout(() => setExportMsg(''), 2000); notify('Review package exported', 'success') }
  }

  // Export: Framework Scoring Report — publishable structured markdown
  async function exportReport() {
    const now = new Date()
    const lines = [
      `# Framework Scoring Report`,
      `## ${pyramid.name}`,
      ``,
      `**Generated:** ${now.toISOString().slice(0, 10)}  `,
      `**Score mode:** ${scoreMode}  `,
      `**CASCADE CICADA TOOL** v0.3.0  `,
      ``,
      `---`,
      ``,
      `## Summary`,
    ]

    let totalBlocks = 0, totalScored = 0, scoreSum = 0
    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      totalBlocks += fileBlocks.length
      const scored = fileBlocks.filter(b => b.score_aggregate > 0)
      totalScored += scored.length
      scoreSum += scored.reduce((a, b) => a + b.score_aggregate, 0)
    }
    const avgGlobal = totalScored > 0 ? Math.round(scoreSum / totalScored) : 0

    lines.push(
      `| Metric | Value |`,
      `|--------|-------|`,
      `| Files | ${files.length} |`,
      `| Total blocks | ${totalBlocks} |`,
      `| Scored blocks | ${totalScored} |`,
      `| Average score | ${avgGlobal || '—'} |`,
      ``,
      `---`,
      ``,
    )

    for (const file of files) {
      const fileBlocks = await window.cascade.blocks.list(file.id)
      const scoredFile = fileBlocks.filter(b => b.score_aggregate > 0)
      lines.push(`## File: ${file.name}`)
      if (file.score_aggregate > 0) lines.push(`**File score:** ${file.score_aggregate}  `)
      lines.push(`**Blocks:** ${fileBlocks.length} total, ${scoredFile.length} scored  `, ``)

      for (const block of fileBlocks.sort((a, b) => (b.score_aggregate || 0) - (a.score_aggregate || 0))) {
        const band = getScoreBand(block.score_aggregate || 0)
        lines.push(`### ${block.is_synthesis ? '◎ ' : ''}${block.title}`)
        if (block.score_aggregate > 0) {
          lines.push(`**Score:** ${block.score_aggregate} · ${band.label}  `)
        } else {
          lines.push(`**Score:** UNSCORED  `)
        }
        if (block.sovereign_score_aggregate > 0) lines.push(`**Sovereign:** ${block.sovereign_score_aggregate}  `)
        if (block.is_synthesis && block.source_block_ids?.length) {
          lines.push(`**Lineage:** Synthesis of ${block.source_block_ids.length} source blocks · earned score ${block.lineage_score || '—'}  `)
        }
        if (block.pinned) lines.push(`**⊙ Pinned** by author  `)
        if (block.content) lines.push(``, `> ${block.content}`)

        // CI data if available
        const ad = adversarialData[block.id]
        if (ad) {
          lines.push(``, `**Adversarial CI:** ${ad.advScore}–${ad.normalScore} · gap ±${ad.gap} · ${ad.stability}`)
        }

        // Layer breakdown
        const ls = await window.cascade.onion.list(block.id)
        const scoredLayers = ls.filter(l => l.framework_score > 0)
        if (scoredLayers.length > 0) {
          lines.push(``, `**Onion Layers:**`, ``)
          lines.push(`| Layer | Score | Reasoning |`)
          lines.push(`|-------|-------|-----------|`)
          for (const l of ls) {
            if (l.framework_score > 0 || l.framework_reasoning) {
              const falsTag = (l.layer_name === 'AXIOM' && l.falsifiable === false) ? ' ⊘' : ''
              lines.push(`| ${l.layer_name}${falsTag} | ${l.framework_score || '—'} | ${(l.framework_reasoning || '').replace(/\|/g, '/')} |`)
            }
          }
        }

        if (block.notes) lines.push(``, `**Notes:** ${block.notes}`)
        lines.push(``)
      }
      lines.push(`---`, ``)
    }

    lines.push(
      `## Framework Reference`,
      ``,
      `Scored against: CASCADE CICADA TOOL v0.3.0 · Lycheetah Framework  `,
      `Scoring formula: **Π = E·P/S** (Evidence × Power / Coherence)  `,
      `Layers: AXIOM → FOUNDATION → STRUCTURE → COHERENCE → RESONANCE → TENSION → CONTESTED → SPECULATIVE → FRONTIER  `,
      ``,
      `*Generated by CASCADE CICADA TOOL — [github.com/Lycheetah/cascade-cicada-tool](https://github.com/Lycheetah/cascade-cicada-tool)*`,
    )

    const result = await window.cascade.export.save({
      content: lines.join('\n'),
      defaultName: `${pyramid.name.replace(/\s+/g, '_')}_report.md`,
      ext: 'md',
    })
    if (result.ok) { setExportMsg('Report saved!'); setTimeout(() => setExportMsg(''), 2000); notify('Framework report exported', 'success') }
  }

  // Summary stats
  const scoredBlocks = blocks.filter(b => b.score_aggregate > 0)
  const avgScore = scoredBlocks.length ? Math.round(scoredBlocks.reduce((a, b) => a + b.score_aggregate, 0) / scoredBlocks.length) : 0
  const cwScore = scoredBlocks.length > 0 ? computeConfidenceWeightedScore(scoredBlocks, adversarialData) : 0
  const strongest = scoredBlocks.reduce((max, b) => b.score_aggregate > (max?.score_aggregate || 0) ? b : max, null)
  const weakest = scoredBlocks.length > 1 ? scoredBlocks.reduce((min, b) => b.score_aggregate < (min?.score_aggregate || 999) ? b : min, null) : null

  // Pi for active block
  const piScore = layers.length >= 4 ? computePi(layers, scoreMode) : null
  const layerViolations = layers.length >= 3 ? checkLayerDependencies(layers, scoreMode) : []

  // Truth velocity for active block (compare previous score to current)
  const activeBlockData = blocks.find(b => b.id === activeBlock?.id)

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
        <div className="mode-tabs" title="Switch score view: AI score / your score / average of both">
          {SCORE_MODES.map(m => (
            <button key={m} className={`mode-tab ${scoreMode === m ? 'active' : ''}`} onClick={() => setMode(m)}
              title={m === 'framework' ? 'AI score — locked, scored against Codex' : m === 'sovereign' ? 'Your score — free, 1–999' : 'Average of AI + your score'}>
              {m === 'framework' ? 'AI Score' : m === 'sovereign' ? 'My Score' : 'Combined'}
            </button>
          ))}
        </div>
        <div className="view-tabs">
          <button className={`view-tab ${view === 'blocks' ? 'active' : ''}`} onClick={() => setView('blocks')}>Blocks</button>
          <button className={`view-tab ${view === 'pyramid' ? 'active' : ''}`} onClick={() => setView('pyramid')}>△ Viz</button>
          <button className={`view-tab ${view === 'health' ? 'active' : ''}`} onClick={() => setView('health')}>◈ Health</button>
          <button className={`view-tab ${view === 'graph' ? 'active' : ''}`} onClick={() => setView('graph')}>⬡ Graph</button>
          <button className={`view-tab ${view === 'cmap' ? 'active' : ''}`} onClick={() => setView('cmap')}>⊗ Map</button>
          {activeFile && <button className={`view-tab ${view === 'file' ? 'active' : ''}`} onClick={() => setView('file')}>File</button>}
          <button className={`view-tab ${view === 'audit' ? 'active' : ''}`} onClick={() => { setView('audit'); loadAuditLog() }}>☰ Log</button>
          <button className={`view-tab ${showHelp ? 'active' : ''}`} onClick={() => setShowHelp(!showHelp)}>?</button>
        </div>
        <div className="topbar-right">
          {files.length > 0 && (
            <button className="btn score-all-btn" onClick={handleScoreAllFiles} disabled={scoringAll} title="Score every block in every file">
              {scoringAll ? <span className="score-all-progress">{scoreAllProgress || '...'}</span> : '⊚ Score all files'}
            </button>
          )}
          <button className="btn synth-btn" onClick={handleSynthesize} disabled={synthesizing} title="Synthesize all scored blocks into unified truth">
            {synthesizing ? '◎ Synthesizing…' : '◎ Synthesize'}
          </button>
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
          <button className={`btn bell-btn ${notifHistory.length > 0 ? 'has-notifs' : ''}`}
            onClick={() => setShowNotifPanel(p => !p)} title="Notification history">
            ◉{notifHistory.length > 0 ? <span className="bell-count">{notifHistory.length}</span> : null}
          </button>
          <span className="api-counter" title="API calls this session">◈ {apiCalls}</span>
          <span className={`save-indicator ${saveIndicator ? 'active' : ''}`}>● saved</span>
          <div className="export-btns">
            {exportMsg
              ? <span className="export-msg">{exportMsg}</span>
              : <>
                  <button className="btn" onClick={exportMarkdown} title="Export as Markdown">↑ MD</button>
                  <button className="btn" onClick={exportJSON} title="Export as JSON">↑ JSON</button>
                  <button className="btn" onClick={exportCascade} title="Export as .cascade portable format">↑ .cascade</button>
                  <button className="btn" onClick={exportHTML} title="Export as static HTML (shareable)">↑ HTML</button>
                  <button className="btn" onClick={exportReport} title="Export publishable Framework Scoring Report (markdown)">↑ Report</button>
                  <button className="btn" onClick={exportReviewPackage} title="Export review package — full scoring data for manual review service">↑ Review</button>
                  <button className="btn" onClick={exportFullDump} title="Export ALL pyramids — full data dump">↑ DUMP</button>
                </>
            }
          </div>
        </div>
      </div>

      {/* Toast overlay */}
      {toasts.length > 0 && (
        <div className="toast-container">
          {toasts.map(t => (
            <div key={t.id} className={`toast toast-${t.type}`}>{t.msg}</div>
          ))}
        </div>
      )}

      {/* Notification history panel */}
      {showNotifPanel && (
        <div className="notif-panel">
          <div className="notif-panel-header">
            <span>◉ NOTIFICATIONS</span>
            <button className="btn" onClick={() => { setNotifHistory([]); setShowNotifPanel(false) }}>Clear all</button>
            <button className="btn" onClick={() => setShowNotifPanel(false)}>✕</button>
          </div>
          {notifHistory.length === 0
            ? <div className="notif-empty">No notifications this session.</div>
            : <div className="notif-list">
                {notifHistory.map((n, i) => (
                  <div key={i} className={`notif-item notif-${n.type}`}>
                    <span className="notif-ts">{fmtTime(n.ts)}</span>
                    <span className="notif-msg">{n.msg}</span>
                  </div>
                ))}
              </div>
          }
        </div>
      )}

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
            <div className="help-section">
              <div className="help-sub">KEYBOARD SHORTCUTS</div>
              <div className="help-row"><span className="help-key">↑ / ↓</span><span>Navigate blocks</span></div>
              <div className="help-row"><span className="help-key">V</span><span>Cycle view tabs</span></div>
              <div className="help-row"><span className="help-key">P</span><span>Pin / unpin active block</span></div>
              <div className="help-row"><span className="help-key">S</span><span>Snapshot active block</span></div>
              <div className="help-row"><span className="help-key">Ctrl+K</span><span>Focus block search</span></div>
              <div className="help-row"><span className="help-key">Ctrl+E</span><span>Export Markdown</span></div>
              <div className="help-row"><span className="help-key">Ctrl+H</span><span>Toggle help</span></div>
              <div className="help-row"><span className="help-key">Esc</span><span>Close panels / deselect</span></div>
            </div>
          </div>
        </div>
      )}

      {/* Group score banner */}
      {selected.size > 1 && (
        <div className="group-bar">
          <span>{selected.size} block{selected.size > 1 ? 's' : ''} selected {selected.size > 10 ? <span className="group-cap">(cap: 10)</span> : ''}</span>
          {groupScore > 0 && (
            <span className="group-score" style={{ color: getScoreBand(groupScore).textColor }}>
              Group: <strong>{groupScore}</strong> · {getScoreBand(groupScore).label}
            </span>
          )}
          {selected.size >= 2 && selected.size <= 10 && (
            <button className="btn block-synth-btn" onClick={handleSynthesizeBlocks} disabled={blockSynthesizing}>
              {blockSynthesizing ? '◎ Finding truth…' : '◎ Synthesize selected'}
            </button>
          )}
          {selected.size > 10 && (
            <span className="group-cap-warn">Select 10 or fewer to synthesize</span>
          )}
          <button className="btn" onClick={() => setSelected(new Set())}>Clear</button>
        </div>
      )}

      {aiError && <div className="pv-ai-error">{aiError}</div>}

      {/* Synthesis panel */}
      {showSynthesis && synthesis && (
        <div className="synth-panel">
          <div className="synth-panel-header">
            <span className="synth-panel-title">◎ PYRAMID SYNTHESIS</span>
            <button className="btn" onClick={async () => {
              if (!activeFile) return
              const allScoredBlocks = blocks.filter(b => b.score_aggregate > 0)
              const avgScore = allScoredBlocks.length
                ? Math.round(allScoredBlocks.reduce((a, b) => a + b.score_aggregate, 0) / allScoredBlocks.length)
                : 0
              await window.cascade.blocks.create({
                fileId: activeFile.id, pyramidId: pyramid.id,
                title: synthesis.synthesis_title || 'Pyramid Synthesis',
                content: synthesis.core_claim + '\n\n' + synthesis.synthesis,
                position: 0, frameworkRefs: ['cascade'],
                sourceBlockIds: allScoredBlocks.map(b => b.id),
                lineageScore: avgScore,
              })
              flashSave()
              await loadBlocks(activeFile.id)
              setShowSynthesis(false)
            }}>+ Save as block</button>
            <button className="btn" onClick={() => setShowSynthesis(false)}>✕</button>
          </div>
          <div className="synth-panel-body">
            <div className="synth-core">
              <div className="synth-label">CORE CLAIM</div>
              <div className="synth-core-text">{synthesis.core_claim}</div>
            </div>
            <div className="synth-full">
              <div className="synth-label">SYNTHESIS</div>
              <div className="synth-full-text">{synthesis.synthesis}</div>
            </div>
            <div className="synth-meta">
              {synthesis.pyramid_coherence > 0 && (
                <span className="synth-coherence">Coherence: <strong>{synthesis.pyramid_coherence}</strong></span>
              )}
              {synthesis.strongest_block && (
                <span className="synth-strongest">↑ {synthesis.strongest_block}</span>
              )}
              {synthesis.weakest_link && (
                <span className="synth-weakest">⚠ {synthesis.weakest_link}</span>
              )}
            </div>
            {synthesis.recommended_next && (
              <div className="synth-next">
                <span className="synth-label">NEXT</span>
                <span className="synth-next-text">{synthesis.recommended_next}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Block synthesis result panel */}
      {showBlockSynth && blockSynthResult && (
        <div className="cross-result-panel">
          <div className="cross-result-header">
            <span className="cross-result-title">◎ {blockSynthResult.emergent_title}</span>
            <span className="cross-coherence">{blockSynthResult.coherence}/100</span>
            <button className="btn" onClick={async () => {
              if (!activeFile) return
              const avgScore = selectedBlocks.length
                ? Math.round(selectedBlocks.reduce((a, b) => a + (b.score_aggregate || 0), 0) / selectedBlocks.length)
                : 0
              await window.cascade.blocks.create({
                fileId: activeFile.id, pyramidId: pyramid.id,
                title: blockSynthResult.emergent_title || 'Block Synthesis',
                content: blockSynthResult.core_emergence + '\n\n' + blockSynthResult.synthesis,
                position: 0, frameworkRefs: ['cascade'],
                sourceBlockIds: selectedBlocks.map(b => b.id),
                lineageScore: avgScore,
              })
              flashSave()
              await loadBlocks(activeFile.id)
              setShowBlockSynth(false)
              setSelected(new Set())
            }}>+ Save as block</button>
            <button className="btn" onClick={() => setShowBlockSynth(false)}>✕</button>
          </div>
          <div className="cross-result-body">
            <div className="cross-emergence">
              <div className="cross-label">EMERGENT TRUTH · {selected.size} blocks</div>
              <div className="cross-emergence-text">{blockSynthResult.core_emergence}</div>
            </div>
            <div className="cross-synthesis-text">{blockSynthResult.synthesis}</div>
            <div className="cross-meta-row">
              {blockSynthResult.key_pattern && (
                <div className="cross-contrib">
                  <span className="cross-contrib-file">PATTERN</span>
                  <span className="cross-contrib-text">{blockSynthResult.key_pattern}</span>
                </div>
              )}
              {blockSynthResult.strongest_signal && (
                <div className="cross-contrib">
                  <span className="cross-contrib-file">STRONGEST SIGNAL</span>
                  <span className="cross-contrib-text" style={{color:'var(--layer-resonance)'}}>{blockSynthResult.strongest_signal}</span>
                </div>
              )}
              {blockSynthResult.outlier && blockSynthResult.outlier !== 'null' && (
                <div className="cross-contrib">
                  <span className="cross-contrib-file">OUTLIER</span>
                  <span className="cross-contrib-text" style={{color:'var(--layer-tension)'}}>{blockSynthResult.outlier}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Cross-synthesis result panel */}
      {showCrossResult && crossResult && (
        <div className="cross-result-panel">
          <div className="cross-result-header">
            <span className="cross-result-title">◎ {crossResult.fileNames?.join(' × ')}</span>
            <span className="cross-coherence" title="Cross-coherence score">{crossResult.cross_coherence}/100</span>
            <button className="btn" onClick={async () => {
              if (!activeFile) return
              await window.cascade.blocks.create({
                fileId: activeFile.id, pyramidId: pyramid.id,
                title: crossResult.intersection_title || 'Cross-Synthesis',
                content: crossResult.core_emergence + '\n\n' + crossResult.synthesis,
                position: 0, frameworkRefs: ['cascade'],
              })
              flashSave()
              await loadBlocks(activeFile.id)
              setShowCrossResult(false)
            }}>+ Save as block</button>
            <button className="btn" onClick={() => setShowCrossResult(false)}>✕</button>
          </div>
          <div className="cross-result-body">
            <div className="cross-emergence">
              <div className="cross-label">EMERGENT TRUTH</div>
              <div className="cross-emergence-text">{crossResult.core_emergence}</div>
            </div>
            <div className="cross-synthesis-text">{crossResult.synthesis}</div>
            {crossResult.file_contributions?.length > 0 && (
              <div className="cross-meta-row">
                {crossResult.file_contributions.map((c, i) => (
                  <div key={i} className="cross-contrib">
                    <span className="cross-contrib-file">{c.file}</span>
                    <span className="cross-contrib-text">{c.contribution}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recursive synthesis result panel */}
      {showRecursiveResult && recursiveResult && (
        <div className="cross-result-panel">
          <div className="cross-result-header">
            <span className="cross-result-title">◎² {recursiveResult.emergent_title}</span>
            <span className="cross-coherence">{recursiveResult.coherence}/100</span>
            <button className="btn" onClick={async () => {
              if (!activeFile) return
              await window.cascade.blocks.create({
                fileId: activeFile.id, pyramidId: pyramid.id,
                title: recursiveResult.emergent_title || 'Recursive Synthesis',
                content: recursiveResult.core_upgrade + '\n\n' + recursiveResult.synthesis,
                position: 0, frameworkRefs: ['cascade'],
                sourceBlockIds: [...(recursiveResult.synthesisBlock.source_block_ids || []), ...recursiveResult.newBlocks.map(b => b.id)],
                lineageScore: recursiveResult.lineage_score || recursiveResult.coherence,
              })
              flashSave()
              await loadBlocks(activeFile.id)
              setShowRecursiveResult(false)
              notify('◎² Second-order synthesis saved', 'success')
            }}>+ Save as block</button>
            <button className="btn" onClick={() => setShowRecursiveResult(false)}>✕</button>
          </div>
          <div className="cross-result-body">
            <div className="cross-emergence">
              <div className="cross-label">UPGRADE · {recursiveResult.newBlocks?.length} new blocks integrated</div>
              <div className="cross-emergence-text">{recursiveResult.core_upgrade}</div>
            </div>
            <div className="cross-synthesis-text">{recursiveResult.synthesis}</div>
            <div className="cross-meta-row">
              {recursiveResult.what_survived && (
                <div className="cross-contrib">
                  <span className="cross-contrib-file" style={{color:'var(--layer-resonance)'}}>SURVIVED</span>
                  <span className="cross-contrib-text">{recursiveResult.what_survived}</span>
                </div>
              )}
              {recursiveResult.what_was_upgraded && (
                <div className="cross-contrib">
                  <span className="cross-contrib-file" style={{color:'var(--gold)'}}>UPGRADED</span>
                  <span className="cross-contrib-text">{recursiveResult.what_was_upgraded}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Pyramid viz view */}
      {view === 'pyramid' && (
        <PyramidViz
          blocks={filteredBlocks}
          onSelectBlock={b => { setActiveBlock(b); setView('blocks') }}
          activeBlockId={activeBlock?.id}
          scoreMode={scoreMode}
        />
      )}

      {/* Health dashboard view */}
      {view === 'health' && (
        <HealthDashboard pyramid={pyramid} files={files} />
      )}

      {/* Knowledge graph view */}
      {view === 'graph' && (
        <KnowledgeGraph files={files} onSelectBlock={(blockId) => {
          // find block in current file and select it
          const block = blocks.find(b => b.id === blockId)
          if (block) { setActiveBlock(block); setView('blocks') }
        }} />
      )}

      {/* Contradiction map view */}
      {view === 'cmap' && (
        <ContradictionMap files={files} />
      )}

      {/* Audit log view */}
      {view === 'audit' && (
        <div className="audit-view">
          <div className="audit-view-header">
            <span>☰ SESSION AUDIT LOG</span>
            <span className="audit-view-count">{auditLog.length} entries</span>
            <button className="btn" onClick={loadAuditLog} disabled={auditLogLoading}>↻ Refresh</button>
          </div>
          {auditLogLoading
            ? <div className="audit-view-empty">Loading…</div>
            : auditLog.length === 0
              ? <div className="audit-view-empty">No events logged yet.</div>
              : (
                <div className="audit-view-body">
                  {auditLog.map((entry, i) => (
                    <div key={i} className={`audit-entry audit-entry-${entry.action}`}>
                      <span className="ae-ts">{fmtTime(entry.ts)}</span>
                      <span className="ae-action">{entry.action}</span>
                      {entry.blockTitle && <span className="ae-block">{entry.blockTitle}</span>}
                      {entry.detail && <span className="ae-detail">{entry.detail}</span>}
                    </div>
                  ))}
                </div>
              )
          }
        </div>
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
              <button className="btn browse-btn" title="Browse for .txt .md .json .csv files" onClick={async () => {
                const { files: picked } = await window.cascade.files.openDialog()
                for (const f of picked) await createFileFromDrop(f.name, f.content, f.size)
              }}>Browse</button>
            </div>

            {/* File-level score bar */}
            {activeFile && fileScore > 0 && (
              <div className="file-score-bar-wrap">
                <div className="file-score-bar" style={{ width: `${Math.min(100, fileScore)}%`, background: fileBand.textColor }} />
                <span className="file-score-label" style={{ color: fileBand.textColor }}>{fileScore} FILE</span>
              </div>
            )}

            {/* Cross-synthesis controls */}
            {files.length >= 2 && (
              <div className="cross-synth-wrap">
                <div className="cross-synth-label">
                  ⊗ Cross-synthesize files
                  <span className="cross-synth-count">{crossFileIds.size > 0 ? ` · ${crossFileIds.size} selected` : ' · pick 2–10'}</span>
                </div>
                <div className="cross-file-list">
                  {files.map(f => (
                    <label key={f.id} className={`cross-file-item ${crossFileIds.has(f.id) ? 'checked' : ''}`}>
                      <input
                        type="checkbox"
                        checked={crossFileIds.has(f.id)}
                        onChange={() => { toggleCrossFile(f.id); setShowCrossResult(false) }}
                        className="cross-file-check"
                      />
                      <span className="cross-file-name">{f.name}</span>
                      {f.score_aggregate > 0 && <span className="cross-file-score">{f.score_aggregate}</span>}
                    </label>
                  ))}
                </div>
                {crossFileIds.size >= 2 && (
                  <button className="cross-synth-btn" onClick={handleCrossSynthesize} disabled={crossSynthesizing}>
                    {crossSynthesizing ? '◎ Finding intersection…' : `◎ Synthesize ${crossFileIds.size} files`}
                  </button>
                )}
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
                    <div key={f.id}
                      className={`file-item ${activeFile?.id === f.id ? 'active' : ''} ${dragOverFileId === f.id && draggedBlockId ? 'drag-target' : ''}`}
                      onClick={() => setActiveFile(f)}
                      onDragOver={e => { if (draggedBlockId) { e.preventDefault(); setDragOverFileId(f.id) } }}
                      onDragLeave={() => setDragOverFileId(null)}
                      onDrop={e => { e.preventDefault(); setDragOverFileId(null); if (draggedBlockId) moveBlockToFile(draggedBlockId, f.id) }}
                    >
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
              {blocks.length > 0 && scoredBlocks.length < blocks.length && (
                <button className="btn" onClick={handleReScoreAll} disabled={rescoring}>
                  {rescoring ? '...' : '↻ Score all'}
                </button>
              )}
            </div>

            {/* STEP GUIDE — shown when file selected but no blocks yet */}
            {activeFile && blocks.length === 0 && (
              <div className="pipeline-guide">
                {activeFile.content ? (
                  <>
                    <div className="pg-step">
                      <span className="pg-num">1</span>
                      <div>
                        <div className="pg-label">Extract blocks from your file</div>
                        <div className="pg-sub">AI reads the content and suggests knowledge blocks</div>
                      </div>
                    </div>
                    <button className="pg-btn" onClick={handleSuggestBlocks} disabled={suggesting}>
                      {suggesting ? '⊚ Reading file...' : '⊚ AI — Suggest blocks'}
                    </button>
                    <div className="pg-divider">or add manually below</div>
                  </>
                ) : (
                  <div className="pg-step">
                    <span className="pg-num">1</span>
                    <div>
                      <div className="pg-label">Add blocks manually</div>
                      <div className="pg-sub">Type a title below and press Enter. For AI extraction, drag a .txt or .md file into the FILES column.</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* SCORE CTA — blocks exist but none scored */}
            {blocks.length > 0 && scoredBlocks.length === 0 && (
              <div className="pipeline-guide compact">
                <div className="pg-step">
                  <span className="pg-num">2</span>
                  <div>
                    <div className="pg-label">Score your blocks</div>
                    <div className="pg-sub">Select a block → use ⊚ AI Score in the panel, or score all at once</div>
                  </div>
                </div>
                <button className="pg-btn" onClick={handleReScoreAll} disabled={rescoring}>
                  {rescoring ? '⊚ Scoring...' : '↻ Score all blocks now'}
                </button>
              </div>
            )}

            {/* Scoring progress strip */}
            {blocks.length > 0 && (() => {
              const allScored = blocks.every(b => b.score_aggregate > 0)
              return (
                <div className={`scoring-strip ${allScored ? 'complete' : ''}`}>
                  {blocks.map(b => (
                    <span
                      key={b.id}
                      className={`score-pyr ${b.score_aggregate > 0 ? 'scored' : 'unscored'}`}
                      title={`${b.title}${b.score_aggregate > 0 ? ' · ' + b.score_aggregate : ' · unscored'}`}
                      onClick={() => setActiveBlock(b)}
                    >△</span>
                  ))}
                  {allScored && <span className="strip-complete">COMPLETE</span>}
                </div>
              )
            })()}

            {/* Quick-add block input */}
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
                {cwScore > 0 && cwScore !== avgScore && (
                  <span className="stat-cw" style={{ color: getScoreBand(cwScore).textColor }} title="Confidence-weighted score — accounts for adversarial CI and pinned blocks">
                    CW {cwScore}
                  </span>
                )}
                {strongest && <span className="stat-strongest">↑ {strongest.title.slice(0, 18)}</span>}
              </div>
            )}

            {/* Search + tag filter */}
            {blocks.length > 2 && (
              <div className="block-search">
                <input type="text" placeholder="Search…" value={search}
                  onChange={e => setSearch(e.target.value)}
                  onKeyDown={e => e.key === 'Escape' && setSearch('')} />
                {allTags.length > 0 && (
                  <select className="tag-filter-select" value={tagFilter} onChange={e => setTagFilter(e.target.value)} title="Filter by tag">
                    <option value="">All tags</option>
                    {allTags.map(t => <option key={t} value={t}>#{t}</option>)}
                  </select>
                )}
                {tagFilter && <button className="btn icon-btn" onClick={() => setTagFilter('')} title="Clear tag filter">✕</button>}
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
                    draggable
                    onDragStart={e => { e.stopPropagation(); setDraggedBlockId(b.id); e.dataTransfer.effectAllowed = 'move' }}
                    onDragEnd={() => setDraggedBlockId(null)}
                    onClick={() => setActiveBlock(b)}>
                    <div className="block-row-top">
                      <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(b.id)} onClick={e => e.stopPropagation()} className="block-check" />
                      <div className="block-title">
                        {b.pinned && <span className="pin-glyph" title="Pinned">⊙</span>}
                        {b.is_synthesis && <span className="synthesis-glyph" title="Synthesis block — lineage preserved">◎</span>}
                        {b.title}
                        {isInTension && <span className="tension-indicator" title="In tension with another block">⊗</span>}
                      </div>
                      <div className="block-reorder">
                        <button className={`btn icon-btn pin-btn ${b.pinned ? 'pinned' : ''}`} onClick={e => togglePin(e, b)} title={b.pinned ? 'Unpin block' : 'Pin block to top'}>⊙</button>
                        <button className="btn icon-btn" onClick={e => { e.stopPropagation(); moveBlock(b.id, -1) }}>↑</button>
                        <button className="btn icon-btn" onClick={e => { e.stopPropagation(); moveBlock(b.id, 1) }}>↓</button>
                        <button className="btn icon-btn" onClick={e => duplicateBlock(e, b.id)} title="Duplicate block">⊕</button>
                        <button className="btn danger icon-btn" onClick={e => deleteBlock(e, b.id)}>×</button>
                      </div>
                    </div>

                    {b.content && (
                      <div
                        className={`block-preview ${expandedBlocks.has(b.id) ? 'expanded' : ''}`}
                        onClick={e => toggleExpand(e, b.id)}
                        title={expandedBlocks.has(b.id) ? 'Click to collapse' : 'Click to expand'}
                      >
                        {expandedBlocks.has(b.id)
                          ? b.content
                          : <>{b.content.slice(0, 80)}{b.content.length > 80 ? <span className="preview-more"> ▾</span> : ''}</>
                        }
                        {expandedBlocks.has(b.id) && <span className="preview-more"> ▴</span>}
                      </div>
                    )}

                    {/* Score bar */}
                    {b.score_aggregate > 0 && (
                      <div className="block-score-bar">
                        <div className="block-score-fill" style={{ width: `${pct}%`, background: band.textColor }} />
                      </div>
                    )}

                    {b.score_history?.length >= 2 && (
                      <div className="block-sparkline">
                        <Sparkline history={b.score_history} />
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

                    {/* Tags display */}
                    {b.tags?.length > 0 && !editingTags && (
                      <div className="block-tags-row" onClick={e => e.stopPropagation()}>
                        {b.tags.map(tag => (
                          <span key={tag} className="block-tag" onClick={() => setTagFilter(tagFilter === tag ? '' : tag)}>#{tag}</span>
                        ))}
                        <button className="btn icon-btn tag-edit-btn" onClick={e => { e.stopPropagation(); setEditingTags(b.id); setTagsInput((b.tags || []).join(', ')) }} title="Edit tags">✎</button>
                      </div>
                    )}
                    {!b.tags?.length && !editingTags && (
                      <button className="btn icon-btn tag-add-btn" onClick={e => { e.stopPropagation(); setEditingTags(b.id); setTagsInput('') }} title="Add tags">+ tag</button>
                    )}

                    {/* Tags inline editor */}
                    {editingTags === b.id && (
                      <div className="block-tags-editor" onClick={e => e.stopPropagation()}>
                        <input
                          type="text"
                          value={tagsInput}
                          onChange={e => setTagsInput(e.target.value)}
                          placeholder="tag1, tag2, tag3"
                          autoFocus
                          className="tags-input"
                          onKeyDown={e => {
                            if (e.key === 'Enter') saveTags(b.id)
                            if (e.key === 'Escape') setEditingTags(null)
                          }}
                        />
                        <div className="notes-actions">
                          <button className="btn" onClick={() => setEditingTags(null)}>Cancel</button>
                          <button className="btn primary" onClick={() => saveTags(b.id)}>Save</button>
                        </div>
                      </div>
                    )}

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

          {/* Right panel: content pane + scoring */}
          <div className="pv-onion">
            {activeBlock ? (
              <div className="right-panel">
                {/* Block content reading pane */}
                <div className="block-reading-pane">
                  <div className="brp-header">
                    <span className="brp-title">{activeBlock.title}</span>
                    {activeBlock.score_aggregate > 0 && (
                      <span className="brp-score" style={{ color: getScoreBand(activeBlock.score_aggregate).textColor }}>
                        {activeBlock.score_aggregate} · {getScoreBand(activeBlock.score_aggregate).label}
                      </span>
                    )}
                    {isAxiomUnfalsifiable(layers) && (
                      <span className="falsifiability-badge" title="Falsifiability Gate: AXIOM is unfalsifiable — capped at 70">⊘ UNFALSIFIABLE</span>
                    )}
                    {piScore !== null && piScore > 0 && (
                      <span className="brp-pi" title="Π = E·P/S">Π {piScore}</span>
                    )}
                    {adversarialData[activeBlock.id] && (() => {
                      const ad = adversarialData[activeBlock.id]
                      const ciColor = ad.stability === 'stable' ? 'var(--layer-resonance)' : ad.stability === 'uncertain' ? 'var(--gold)' : 'var(--layer-tension)'
                      return (
                        <span className="brp-ci" style={{ color: ciColor }} title={`Adversarial score: ${ad.advScore} · Gap: ${ad.gap}`}>
                          CI [{ad.advScore}–{ad.normalScore}] ±{ad.gap} · {ad.stability}
                        </span>
                      )
                    })()}
                    <button
                      className="btn challenge-btn"
                      onClick={() => handleAdversarialScore(activeBlock)}
                      disabled={adversarialLoading === activeBlock.id || !activeBlock.score_aggregate}
                      title="Adversarially challenge this block's score"
                    >
                      {adversarialLoading === activeBlock.id ? '⊗ Challenging…' : '⊗ Challenge'}
                    </button>
                    {layers[0]?.score_audit && (
                      <button className="btn audit-btn" onClick={() => setShowAudit(v => !v)}
                        title="View the full AI prompt that generated this score">
                        {showAudit ? '▴ Hide prompt' : '▾ View prompt'}
                      </button>
                    )}
                    <button
                      className="btn consensus-btn"
                      onClick={() => handleConsensusScore(activeBlock)}
                      disabled={consensusLoading === activeBlock.id}
                      title="Score with all configured providers and compare"
                    >
                      {consensusLoading === activeBlock.id ? '◈ Polling…' : '◈ Consensus'}
                    </button>
                    {activeBlock.is_synthesis && (
                      <button className="btn recursive-synth-btn"
                        onClick={() => handleRecursiveSynthesize(activeBlock)}
                        disabled={recursiveSynthesizing}
                        title="Recursive synthesis — upgrade this synthesis with new blocks">
                        {recursiveSynthesizing ? '◎² Upgrading…' : '◎² Recurse'}
                      </button>
                    )}
                    <button className="btn version-save-btn" onClick={() => saveVersion(activeBlock)} title="Save a version snapshot of this block">
                      ⊞ Snapshot
                    </button>
                    <button className="btn version-hist-btn" onClick={() => { if (showVersions) { setShowVersions(false) } else { loadVersions(activeBlock.id) } }}
                      title="View version history">
                      {showVersions ? '▴ History' : '▾ History'}
                    </button>
                  </div>
                  {activeBlock.content
                    ? <div className="brp-content">{activeBlock.content}</div>
                    : <div className="brp-empty">No content — add it via the block title or drag a file.</div>
                  }
                  {activeBlock.notes && (
                    <div className="brp-notes">{activeBlock.notes}</div>
                  )}
                  {/* Consensus scoring results */}
                  {consensusData[activeBlock.id] && (() => {
                    const cd = consensusData[activeBlock.id]
                    const agColor = cd.agreement === 'strong' ? 'var(--layer-resonance)' : cd.agreement === 'moderate' ? 'var(--gold)' : 'var(--layer-tension)'
                    return (
                      <div className="consensus-panel">
                        <div className="consensus-header">
                          <span>◈ CONSENSUS</span>
                          <span style={{ color: agColor }}>mean {cd.mean} · ±{cd.stddev} · {cd.agreement}</span>
                        </div>
                        <div className="consensus-providers">
                          {cd.providers.map((p, i) => (
                            <div key={i} className="consensus-provider-row">
                              <span className="cp-name">{p.provider}</span>
                              <div className="cp-bar-wrap">
                                <div className="cp-bar" style={{ width: `${p.aggregate}%`, background: agColor }} />
                              </div>
                              <span className="cp-score">{p.aggregate}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })()}
                  {/* Score transparency — full prompt audit */}
                  {showAudit && layers[0]?.score_audit && (
                    <div className="audit-panel">
                      <div className="audit-header">▾ SCORE AUDIT — Full prompt</div>
                      <pre className="audit-body">{layers[0].score_audit}</pre>
                    </div>
                  )}
                  {/* Adversarial layer breakdown */}
                  {adversarialData[activeBlock.id] && (() => {
                    const ad = adversarialData[activeBlock.id]
                    return (
                      <div className="adversarial-panel">
                        <div className="adv-header">⊗ ADVERSARIAL CHALLENGE</div>
                        <div className="adv-layers">
                          {ad.layers.map((l, i) => (
                            <div key={i} className="adv-layer-row">
                              <span className="adv-layer-name">{l.layer_name}</span>
                              <span className="adv-layer-score">{l.framework_score}</span>
                              <span className="adv-layer-reason">{l.framework_reasoning}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })()}
                  {/* Version history panel */}
                  {showVersions && (
                    <div className="version-panel">
                      <div className="version-panel-header">▾ VERSION HISTORY ({versionData.length})</div>
                      {versionData.length === 0
                        ? <div className="version-empty">No snapshots saved yet. Use ⊞ Snapshot to save one.</div>
                        : <div className="version-list">
                            {[...versionData].reverse().map((v, i) => {
                              const band = getScoreBand(v.score || 0)
                              return (
                                <div key={i} className="version-item">
                                  <span className="version-ts">{fmtTime(v.ts)}</span>
                                  {v.score > 0 && <span className="version-score" style={{ color: band.textColor }}>{v.score}</span>}
                                  <span className="version-title">{v.title}</span>
                                  <span className="version-preview">{(v.content || '').slice(0, 60)}{(v.content || '').length > 60 ? '…' : ''}</span>
                                </div>
                              )
                            })}
                          </div>
                      }
                    </div>
                  )}
                </div>

                {/* Scoring section */}
                <div className="scoring-section">
                  <div className="scoring-section-header">
                    <OnionRing layers={layers} size={80} />
                    {layerViolations.length > 0 && (
                      <div className="dep-warnings-inline">
                        {layerViolations.map((v, i) => (
                          <div key={i} className="dep-warn">⚠ {v.violation} (cap: {v.cap})</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="onion-panel">
                    <OnionEditor block={activeBlock} fileContent={activeFile?.content || ''} onSaved={onLayerSaved} />
                  </div>
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
