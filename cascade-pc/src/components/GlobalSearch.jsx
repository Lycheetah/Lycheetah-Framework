import React, { useState, useEffect, useRef } from 'react'
import { getScoreBand } from '../scoring/cascade'
import './GlobalSearch.css'

/**
 * Global search across all pyramids, files, and blocks.
 * Loads all data on mount and filters client-side.
 */
export default function GlobalSearch({ onOpenPyramid }) {
  const [query, setQuery]       = useState('')
  const [results, setResults]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [allData, setAllData]   = useState([]) // flat list of { pyramid, file, block, type }
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
    loadAll()
  }, [])

  async function loadAll() {
    setLoading(true)
    const pyramids = await window.cascade.pyramids.list()
    const flat = []
    for (const pyramid of pyramids) {
      flat.push({ type: 'pyramid', pyramid, label: pyramid.name, sub: pyramid.description || '', score: pyramid.score_aggregate || 0 })
      const files = await window.cascade.files.list(pyramid.id)
      for (const file of files) {
        flat.push({ type: 'file', pyramid, file, label: file.name, sub: `in ${pyramid.name}`, score: file.score_aggregate || 0 })
        const blocks = await window.cascade.blocks.list(file.id)
        for (const block of blocks) {
          flat.push({
            type: 'block', pyramid, file, block,
            label: block.title,
            sub: `${file.name} · ${pyramid.name}`,
            score: block.score_aggregate || 0,
            content: block.content || '',
            is_synthesis: block.is_synthesis,
            pinned: block.pinned,
          })
        }
      }
    }
    setAllData(flat)
    setLoading(false)
  }

  function search(q) {
    setQuery(q)
    if (!q.trim()) { setResults([]); return }
    const lower = q.toLowerCase()
    const hits = allData.filter(item => {
      const haystack = [item.label, item.sub, item.content || ''].join(' ').toLowerCase()
      return haystack.includes(lower)
    })
    // Sort: pyramids first, then files, then blocks; within each, scored > unscored
    const order = { pyramid: 0, file: 1, block: 2 }
    hits.sort((a, b) => {
      if (order[a.type] !== order[b.type]) return order[a.type] - order[b.type]
      return (b.score || 0) - (a.score || 0)
    })
    setResults(hits.slice(0, 60))
  }

  function highlight(text, q) {
    if (!q) return text
    const idx = text.toLowerCase().indexOf(q.toLowerCase())
    if (idx === -1) return text.slice(0, 80)
    const start = Math.max(0, idx - 20)
    const end = Math.min(text.length, idx + q.length + 40)
    const before = (start > 0 ? '…' : '') + text.slice(start, idx)
    const match = text.slice(idx, idx + q.length)
    const after = text.slice(idx + q.length, end) + (end < text.length ? '…' : '')
    return <>{before}<mark>{match}</mark>{after}</>
  }

  const grouped = { pyramid: [], file: [], block: [] }
  results.forEach(r => grouped[r.type]?.push(r))

  return (
    <div className="gsearch-root">
      <div className="gsearch-header">
        <span className="gsearch-title">⊚ GLOBAL SEARCH</span>
      </div>
      <div className="gsearch-input-wrap">
        <input
          ref={inputRef}
          type="text"
          className="gsearch-input"
          placeholder="Search across all pyramids, files, and blocks…"
          value={query}
          onChange={e => search(e.target.value)}
          onKeyDown={e => e.key === 'Escape' && setQuery('')}
        />
        {query && <button className="gsearch-clear" onClick={() => search('')}>✕</button>}
      </div>

      {loading && <div className="gsearch-status">Loading all data…</div>}
      {!loading && !query && (
        <div className="gsearch-status">
          {allData.filter(d => d.type === 'block').length} blocks across {allData.filter(d => d.type === 'pyramid').length} pyramids indexed.
        </div>
      )}
      {!loading && query && results.length === 0 && (
        <div className="gsearch-status">No results for "{query}"</div>
      )}

      {results.length > 0 && (
        <div className="gsearch-results">
          {grouped.pyramid.length > 0 && (
            <div className="gsearch-section">
              <div className="gsearch-section-title">PYRAMIDS · {grouped.pyramid.length}</div>
              {grouped.pyramid.map((r, i) => (
                <div key={i} className="gsearch-item gsearch-pyramid" onClick={() => onOpenPyramid(r.pyramid)}>
                  <span className="gsi-glyph">△</span>
                  <div className="gsi-body">
                    <div className="gsi-label">{highlight(r.label, query)}</div>
                    {r.sub && <div className="gsi-sub">{r.sub}</div>}
                  </div>
                  {r.score > 0 && <span className="gsi-score" style={{ color: getScoreBand(r.score).textColor }}>{r.score}</span>}
                </div>
              ))}
            </div>
          )}
          {grouped.file.length > 0 && (
            <div className="gsearch-section">
              <div className="gsearch-section-title">FILES · {grouped.file.length}</div>
              {grouped.file.map((r, i) => (
                <div key={i} className="gsearch-item gsearch-file" onClick={() => onOpenPyramid(r.pyramid)}>
                  <span className="gsi-glyph">▪</span>
                  <div className="gsi-body">
                    <div className="gsi-label">{highlight(r.label, query)}</div>
                    <div className="gsi-sub">{r.sub}</div>
                  </div>
                  {r.score > 0 && <span className="gsi-score" style={{ color: getScoreBand(r.score).textColor }}>{r.score}</span>}
                </div>
              ))}
            </div>
          )}
          {grouped.block.length > 0 && (
            <div className="gsearch-section">
              <div className="gsearch-section-title">BLOCKS · {grouped.block.length}</div>
              {grouped.block.map((r, i) => (
                <div key={i} className="gsearch-item gsearch-block" onClick={() => onOpenPyramid(r.pyramid)}>
                  <span className="gsi-glyph">{r.is_synthesis ? '◎' : r.pinned ? '⊙' : '○'}</span>
                  <div className="gsi-body">
                    <div className="gsi-label">{highlight(r.label, query)}</div>
                    <div className="gsi-sub">{r.sub}</div>
                    {r.content && <div className="gsi-excerpt">{highlight(r.content, query)}</div>}
                  </div>
                  {r.score > 0 && <span className="gsi-score" style={{ color: getScoreBand(r.score).textColor }}>{r.score}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
