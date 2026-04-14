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
  const total = scored.length

  // SVG triangle dimensions
  const svgW = 600
  const svgH = 400
  const apex = { x: svgW / 2, y: 20 }
  const baseL = { x: 30, y: svgH - 20 }
  const baseR = { x: svgW - 30, y: svgH - 20 }

  return (
    <div className="pyramid-viz">
      <div className="pviz-label">△ PYRAMID VIEW · {scoreMode.toUpperCase()}</div>

      <div className="pviz-canvas">
        {/* SVG triangle backdrop */}
        <svg className="pviz-svg" viewBox={`0 0 ${svgW} ${svgH}`} preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="tri-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--gold)" stopOpacity="0.18" />
              <stop offset="100%" stopColor="var(--gold)" stopOpacity="0.03" />
            </linearGradient>
          </defs>
          <polygon
            points={`${apex.x},${apex.y} ${baseL.x},${baseL.y} ${baseR.x},${baseR.y}`}
            fill="url(#tri-grad)"
            stroke="var(--gold-dim)"
            strokeWidth="1"
            strokeOpacity="0.4"
          />
          {/* Score level lines */}
          {[0.25, 0.5, 0.75].map(t => {
            const lx = apex.x + (baseL.x - apex.x) * t
            const rx = apex.x + (baseR.x - apex.x) * t
            const y = apex.y + (baseL.y - apex.y) * t
            return (
              <line key={t} x1={lx} y1={y} x2={rx} y2={y}
                stroke="var(--border)" strokeWidth="0.5" strokeDasharray="4,4" />
            )
          })}
        </svg>

        {/* Block rows — positioned inside triangle */}
        <div className="pviz-blocks-overlay">
          {scored.length === 0 && (
            <div className="pviz-empty">Add and score blocks to see the pyramid</div>
          )}
          {scored.map((block, i) => {
            const band = getScoreBand(block.displayScore)
            // Width narrows toward apex: top blocks narrower
            const progress = total > 1 ? i / (total - 1) : 0.5 // 0 = top, 1 = bottom
            const triangleWidthAtRow = 0.18 + progress * 0.78 // 18% at top, 96% at base
            const widthPct = block.displayScore > 0
              ? Math.max(triangleWidthAtRow * 0.4, (block.displayScore / maxScore) * triangleWidthAtRow)
              : triangleWidthAtRow * 0.3
            const isActive = block.id === activeBlockId
            const isHovered = block.id === hoveredId

            return (
              <div key={block.id} className="pviz-row" style={{ maxWidth: `${triangleWidthAtRow * 100}%` }}>
                <div
                  className={`pviz-block ${isActive ? 'active' : ''} ${isHovered ? 'hovered' : ''}`}
                  style={{
                    width: `${(widthPct / triangleWidthAtRow) * 100}%`,
                    borderColor: block.displayScore > 0 ? band.textColor : 'var(--border)',
                    background: isActive
                      ? `${band.textColor}22`
                      : block.displayScore > 0 ? `${band.textColor}0d` : 'transparent',
                    boxShadow: isActive ? `0 0 8px ${band.textColor}44` : 'none',
                  }}
                  onClick={() => onSelectBlock(block)}
                  onMouseEnter={() => setHoveredId(block.id)}
                  onMouseLeave={() => setHoveredId(null)}
                >
                  <div className="pviz-block-score" style={{ color: block.displayScore > 0 ? band.textColor : 'var(--text-dim)' }}>
                    {block.displayScore > 0 ? block.displayScore : '—'}
                  </div>
                  <div className="pviz-block-title">{block.title}</div>
                  {block.displayScore > 0 && (
                    <div className="pviz-block-band" style={{ color: band.textColor }}>{band.label}</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="pviz-legend">
        {SCORE_BANDS.slice(1).map(band => (
          <div key={band.label} className="legend-item">
            <div className="legend-dot" style={{ background: band.textColor }} />
            <span style={{ color: band.textColor }}>{band.label}</span>
            <span className="legend-range">{band.min}–{band.max === 999 ? '∞' : band.max}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
