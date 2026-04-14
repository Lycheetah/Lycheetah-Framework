import React, { useState } from 'react'
import { getScoreBand, SCORE_BANDS } from '../scoring/cascade'
import './PyramidViz.css'

export default function PyramidViz({ blocks, onSelectBlock, activeBlockId, scoreMode = 'framework' }) {
  const [hoveredId, setHoveredId] = useState(null)

  function getBlockScore(block) {
    if (scoreMode === 'sovereign') return block.sovereign_score_aggregate || 0
    if (scoreMode === 'composite') {
      const f = block.score_aggregate || 0
      const s = block.sovereign_score_aggregate || 0
      if (f && s) return Math.round((f + s) / 2)
      return f || s || 0
    }
    return block.score_aggregate || 0
  }

  const scored = blocks
    .map(b => ({ ...b, displayScore: getBlockScore(b) }))
    .sort((a, b) => b.displayScore - a.displayScore)

  const maxScore = Math.max(...scored.map(b => b.displayScore), 1)

  return (
    <div className="pyramid-viz">
      <div className="pviz-label">PYRAMID VIEW · {scoreMode.toUpperCase()}</div>
      <div className="pviz-triangle">
        {scored.length === 0 && (
          <div className="pviz-empty">Add and score blocks to see the pyramid</div>
        )}
        {scored.map((block, i) => {
          const band = getScoreBand(block.displayScore)
          const widthPct = block.displayScore > 0
            ? Math.max(20, (block.displayScore / maxScore) * 100)
            : 30
          const isActive = block.id === activeBlockId
          const isHovered = block.id === hoveredId

          return (
            <div
              key={block.id}
              className={`pviz-block ${isActive ? 'active' : ''} ${isHovered ? 'hovered' : ''}`}
              style={{
                width: `${widthPct}%`,
                borderColor: band.textColor,
                background: isActive
                  ? `${band.textColor}22`
                  : block.displayScore > 0 ? `${band.textColor}0d` : 'transparent',
              }}
              onClick={() => onSelectBlock(block)}
              onMouseEnter={() => setHoveredId(block.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              <div className="pviz-block-score" style={{ color: band.textColor }}>
                {block.displayScore > 0 ? block.displayScore : '—'}
              </div>
              <div className="pviz-block-title">{block.title}</div>
              {block.displayScore > 0 && (
                <div className="pviz-block-band" style={{ color: band.textColor }}>{band.label}</div>
              )}
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="pviz-legend">
        {SCORE_BANDS.slice(1).map(band => (
          <div key={band.label} className="legend-item">
            <div className="legend-dot" style={{ background: band.textColor }} />
            <span style={{ color: band.textColor }}>{band.label}</span>
            <span className="legend-range">{band.min}–{band.max}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
