import React from 'react'
import { ONION_LAYERS } from '../scoring/cascade'

const COLORS = [
  '#fb923c','#f97316','#facc15','#4ade80','#34d399',
  '#60a5fa','#818cf8','#c084fc','#e879f9'
]

export default function OnionRing({ layers, size = 180 }) {
  if (!layers || layers.length === 0) return null

  const cx = size / 2
  const cy = size / 2
  const maxR = size / 2 - 4
  const minR = 12
  const step = (maxR - minR) / 9

  function getScore(layer, i) {
    return layer?.framework_score || layer?.score || 0
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <svg width={size} height={size} style={{ overflow: 'visible' }}>
        {[...ONION_LAYERS].reverse().map((layer, ri) => {
          const i = 8 - ri
          const layerData = layers[i]
          const score = getScore(layerData, i)
          const r = maxR - ri * step
          const opacity = score > 0 ? Math.max(0.15, score / 100) : 0.06
          const strokeW = score > 0 ? 1.5 : 0.5
          return (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={r}
              fill={score > 0 ? `${COLORS[i]}${Math.round(opacity * 255).toString(16).padStart(2,'0')}` : 'transparent'}
              stroke={COLORS[i]}
              strokeWidth={strokeW}
              opacity={score > 0 ? 1 : 0.2}
            >
              <title>{layer.name}: {score || '—'}</title>
            </circle>
          )
        })}
        {/* Center dot */}
        <circle cx={cx} cy={cy} r={4} fill={COLORS[0]} opacity={0.8} />
      </svg>
      <div style={{ fontSize: 9, color: '#555', letterSpacing: '0.1em', textAlign: 'center' }}>
        AXIOM → FRONTIER
      </div>
    </div>
  )
}
