import React, { useEffect, useState } from 'react'
import { computeBlockScore, getScoreBand, detectTensions } from '../scoring/cascade'
import { analyzeGaps } from '../scoring/ai'
import './HealthDashboard.css'

export default function HealthDashboard({ pyramid, files }) {
  const [stats, setStats] = useState(null)
  const [gapAnalysis, setGapAnalysis] = useState(null)
  const [gapLoading, setGapLoading] = useState(false)
  const [gapError, setGapError] = useState('')
  const [allBlocksCache, setAllBlocksCache] = useState([])

  useEffect(() => {
    if (!files || files.length === 0) return
    buildStats()
  }, [files])

  async function buildStats() {
    let allBlocks = []
    const fileStats = []

    for (const file of files) {
      const blocks = await window.cascade.blocks.list(file.id)
      const scored = blocks.filter(b => b.score_aggregate > 0)
      fileStats.push({
        name: file.name,
        total: blocks.length,
        scored: scored.length,
        avg: scored.length ? Math.round(scored.reduce((a, b) => a + b.score_aggregate, 0) / scored.length) : 0,
        fileScore: file.score_aggregate || 0,
      })
      allBlocks = allBlocks.concat(blocks)
    }

    const scoredBlocks = allBlocks.filter(b => b.score_aggregate > 0)
    const totalBlocks = allBlocks.length
    const scoredPct = totalBlocks > 0 ? Math.round((scoredBlocks.length / totalBlocks) * 100) : 0

    // CI average — from adversarial data stored in blocks (if any)
    const avgScore = scoredBlocks.length
      ? Math.round(scoredBlocks.reduce((a, b) => a + b.score_aggregate, 0) / scoredBlocks.length)
      : 0

    const strongest = scoredBlocks.reduce((max, b) => b.score_aggregate > (max?.score_aggregate || 0) ? b : max, null)
    const weakest = scoredBlocks.length > 1
      ? scoredBlocks.reduce((min, b) => b.score_aggregate < (min?.score_aggregate || 999) ? b : min, null)
      : null

    const tensions = detectTensions(scoredBlocks)

    // Score distribution
    const dist = { WEAK: 0, DEVELOPING: 0, MIDDLE: 0, STRONG: 0, FOUNDATION: 0, FRONTIER: 0 }
    scoredBlocks.forEach(b => {
      const band = getScoreBand(b.score_aggregate)
      if (dist[band.label] !== undefined) dist[band.label]++
    })

    // Synthesis ratio
    const synthBlocks = allBlocks.filter(b => b.is_synthesis)

    setAllBlocksCache(allBlocks)
    setStats({
      totalBlocks, scoredBlocks: scoredBlocks.length, scoredPct,
      avgScore, strongest, weakest, tensions,
      fileStats, dist, synthBlocks: synthBlocks.length,
      filesCount: files.length,
    })
  }

  if (!stats) return <div className="health-empty">Loading diagnostics…</div>

  const scoreColor = (s) => getScoreBand(s).textColor

  return (
    <div className="health-dashboard">
      <div className="health-header">◈ PYRAMID HEALTH DASHBOARD</div>

      {/* Top metrics */}
      <div className="health-metrics">
        <div className="health-metric">
          <div className="hm-value" style={{ color: stats.scoredPct === 100 ? '#4ade80' : stats.scoredPct > 50 ? '#facc15' : '#f87171' }}>
            {stats.scoredPct}%
          </div>
          <div className="hm-label">SCORED</div>
          <div className="hm-sub">{stats.scoredBlocks} / {stats.totalBlocks} blocks</div>
        </div>
        <div className="health-metric">
          <div className="hm-value" style={{ color: scoreColor(stats.avgScore) }}>{stats.avgScore || '—'}</div>
          <div className="hm-label">AVG SCORE</div>
          <div className="hm-sub">{getScoreBand(stats.avgScore).label}</div>
        </div>
        <div className="health-metric">
          <div className="hm-value" style={{ color: stats.tensions.length > 0 ? '#fb923c' : '#4ade80' }}>
            {stats.tensions.length}
          </div>
          <div className="hm-label">TENSIONS</div>
          <div className="hm-sub">cross-block conflicts</div>
        </div>
        <div className="health-metric">
          <div className="hm-value" style={{ color: '#60a5fa' }}>{stats.synthBlocks}</div>
          <div className="hm-label">SYNTHESES</div>
          <div className="hm-sub">◎ lineage blocks</div>
        </div>
        <div className="health-metric">
          <div className="hm-value">{stats.filesCount}</div>
          <div className="hm-label">FILES</div>
          <div className="hm-sub">knowledge sources</div>
        </div>
      </div>

      {/* Score distribution */}
      <div className="health-section">
        <div className="health-section-title">SCORE DISTRIBUTION</div>
        <div className="dist-bars">
          {Object.entries(stats.dist).map(([label, count]) => {
            const band = getScoreBand({ WEAK: 10, DEVELOPING: 30, MIDDLE: 50, STRONG: 70, FOUNDATION: 90, FRONTIER: 150 }[label] || 10)
            const pct = stats.scoredBlocks > 0 ? (count / stats.scoredBlocks) * 100 : 0
            return (
              <div key={label} className="dist-row">
                <span className="dist-label" style={{ color: band.textColor }}>{label}</span>
                <div className="dist-bar-wrap">
                  <div className="dist-bar-fill" style={{ width: `${pct}%`, background: band.textColor }} />
                </div>
                <span className="dist-count">{count}</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Strongest / Weakest */}
      <div className="health-row-2">
        {stats.strongest && (
          <div className="health-section half">
            <div className="health-section-title">STRONGEST BLOCK</div>
            <div className="health-block-card" style={{ borderColor: scoreColor(stats.strongest.score_aggregate) }}>
              <div className="hbc-score" style={{ color: scoreColor(stats.strongest.score_aggregate) }}>
                {stats.strongest.score_aggregate}
              </div>
              <div className="hbc-title">{stats.strongest.title}</div>
            </div>
          </div>
        )}
        {stats.weakest && (
          <div className="health-section half">
            <div className="health-section-title">WEAKEST BLOCK</div>
            <div className="health-block-card" style={{ borderColor: scoreColor(stats.weakest.score_aggregate) }}>
              <div className="hbc-score" style={{ color: scoreColor(stats.weakest.score_aggregate) }}>
                {stats.weakest.score_aggregate}
              </div>
              <div className="hbc-title">{stats.weakest.title}</div>
            </div>
          </div>
        )}
      </div>

      {/* File breakdown */}
      <div className="health-section">
        <div className="health-section-title">FILE BREAKDOWN</div>
        <div className="file-breakdown">
          {stats.fileStats.map((f, i) => (
            <div key={i} className="fb-row">
              <span className="fb-name">{f.name}</span>
              <div className="fb-bar-wrap">
                <div className="fb-bar-fill"
                  style={{ width: `${f.scored > 0 ? (f.scored / f.total) * 100 : 0}%`, background: scoreColor(f.avg) }} />
              </div>
              <span className="fb-score" style={{ color: scoreColor(f.avg) }}>{f.avg || '—'}</span>
              <span className="fb-count">{f.scored}/{f.total}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tensions */}
      {stats.tensions.length > 0 && (
        <div className="health-section">
          <div className="health-section-title">ACTIVE TENSIONS</div>
          {stats.tensions.map((t, i) => (
            <div key={i} className="health-tension">
              <span className="ht-strong" style={{ color: scoreColor(t.stronger.score_aggregate) }}>
                {t.stronger.title.slice(0, 30)}
              </span>
              <span className="ht-delta">Δ{t.delta}</span>
              <span className="ht-weak" style={{ color: scoreColor(t.weaker.score_aggregate) }}>
                {t.weaker.title.slice(0, 30)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* AI Gap Analysis */}
      <div className="health-section">
        <div className="health-section-title">AI GAP ANALYSIS</div>
        {!gapAnalysis ? (
          <div className="gap-cta">
            <p className="gap-desc">
              AI examines your pyramid and identifies missing knowledge — what would most strengthen it.
            </p>
            {gapError && <div className="gap-error">{gapError}</div>}
            <button className="btn gap-btn" onClick={async () => {
              setGapLoading(true); setGapError('')
              try {
                const result = await analyzeGaps(pyramid.name, allBlocksCache)
                setGapAnalysis(result)
              } catch (e) { setGapError(e.message) }
              setGapLoading(false)
            }} disabled={gapLoading || allBlocksCache.length === 0}>
              {gapLoading ? '⊚ Analysing…' : '⊚ Find gaps'}
            </button>
          </div>
        ) : (
          <div className="gap-results">
            <div className="gap-priority">
              <span className="gap-label">NEXT PRIORITY</span>
              <span className="gap-priority-text">{gapAnalysis.next_priority}</span>
            </div>
            <div className="gap-health">
              <span className="gap-label">COVERAGE</span>
              <span className="gap-health-val" style={{
                color: gapAnalysis.structural_health > 70 ? '#4ade80' : gapAnalysis.structural_health > 40 ? '#facc15' : '#f87171'
              }}>{gapAnalysis.structural_health}/100</span>
            </div>
            {gapAnalysis.weakest_area && (
              <div className="gap-row">
                <span className="gap-label">WEAKEST AREA</span>
                <span className="gap-val">{gapAnalysis.weakest_area}</span>
              </div>
            )}
            {gapAnalysis.critical_gaps?.length > 0 && (
              <div className="gap-list-section">
                <span className="gap-label">CRITICAL GAPS</span>
                <ul className="gap-list">
                  {gapAnalysis.critical_gaps.map((g, i) => <li key={i}>{g}</li>)}
                </ul>
              </div>
            )}
            {gapAnalysis.suggested_blocks?.length > 0 && (
              <div className="gap-list-section">
                <span className="gap-label">SUGGESTED BLOCKS</span>
                {gapAnalysis.suggested_blocks.map((s, i) => (
                  <div key={i} className="gap-suggestion">
                    <span className="gap-sug-title">{s.title}</span>
                    <span className="gap-sug-reason">{s.reason}</span>
                  </div>
                ))}
              </div>
            )}
            {gapAnalysis.unexamined_assumptions?.length > 0 && (
              <div className="gap-list-section">
                <span className="gap-label">UNEXAMINED ASSUMPTIONS</span>
                <ul className="gap-list">
                  {gapAnalysis.unexamined_assumptions.map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              </div>
            )}
            <button className="btn" style={{marginTop:12}} onClick={() => setGapAnalysis(null)}>↻ Re-analyse</button>
          </div>
        )}
      </div>
    </div>
  )
}
