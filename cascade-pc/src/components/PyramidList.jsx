import React, { useState, useEffect } from 'react'
import { computePyramidScore, getScoreBand } from '../scoring/cascade'
import './PyramidList.css'

export default function PyramidList({ onOpen }) {
  const [pyramids, setPyramids] = useState([])
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  useEffect(() => { load() }, [])

  async function load() {
    const list = await window.cascade.pyramids.list()
    setPyramids(list)
  }

  async function create() {
    if (!name.trim()) return
    await window.cascade.pyramids.create({ name: name.trim(), description: description.trim() })
    setName(''); setDescription(''); setCreating(false)
    load()
  }

  async function deletePyramid(e, id) {
    e.stopPropagation()
    if (!confirm('Delete this pyramid and all its contents?')) return
    await window.cascade.pyramids.delete(id)
    load()
  }

  return (
    <div className="pyramid-list">
      <div className="list-header">
        <div className="list-title">
          <span className="list-icon">△</span>
          YOUR PYRAMIDS
        </div>
        <button className="btn primary" onClick={() => setCreating(true)}>+ New Pyramid</button>
      </div>

      {creating && (
        <div className="create-card">
          <div className="create-title">NEW PYRAMID</div>
          <input
            type="text"
            placeholder="Pyramid name..."
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && create()}
            autoFocus
          />
          <textarea
            placeholder="Description (optional)..."
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={2}
          />
          <div className="create-actions">
            <button className="btn" onClick={() => { setCreating(false); setName(''); setDescription('') }}>Cancel</button>
            <button className="btn primary" onClick={create}>Create</button>
          </div>
        </div>
      )}

      {pyramids.length === 0 && !creating && (
        <div className="empty-state">
          <div className="empty-icon">△</div>
          <div className="empty-text">No pyramids yet.</div>
          <div className="empty-sub">Create your first knowledge pyramid to begin.</div>
        </div>
      )}

      <div className="pyramid-grid">
        {pyramids.map(p => (
          <PyramidCard
            key={p.id}
            pyramid={p}
            onOpen={() => onOpen(p)}
            onDelete={(e) => deletePyramid(e, p.id)}
          />
        ))}
      </div>
    </div>
  )
}

function PyramidCard({ pyramid, onOpen, onDelete }) {
  const score = pyramid.score_aggregate || 0
  const band = getScoreBand(score)
  const date = new Date(pyramid.created_at * 1000).toLocaleDateString()

  return (
    <div className="pyramid-card" onClick={onOpen}>
      <div className="card-header">
        <div className="card-name">{pyramid.name}</div>
        <button className="btn danger icon-btn" onClick={onDelete} title="Delete">×</button>
      </div>
      {pyramid.description && (
        <div className="card-desc">{pyramid.description}</div>
      )}
      <div className="card-footer">
        <div className="card-score" style={{ color: band.color === '#0a0a0a' ? '#888' : band.textColor }}>
          {score > 0 ? (
            <>
              <span className="score-num">{score}</span>
              <span className="score-band">{band.label}</span>
            </>
          ) : (
            <span className="score-empty">— unscored</span>
          )}
        </div>
        <div className="card-date">{date}</div>
      </div>
    </div>
  )
}
