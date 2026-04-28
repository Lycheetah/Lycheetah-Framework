import React, { useState, useEffect } from 'react'
import { getScoreBand } from '../scoring/cascade'
import './PyramidList.css'

const TEMPLATES = [
  {
    id: 'research-paper',
    name: 'Research Paper Analysis',
    description: 'Pressure-test an academic paper',
    glyph: '∑',
    files: [
      { name: 'Core Claims', blocks: ['Main thesis', 'Primary evidence', 'Methodology', 'Conclusions'] },
      { name: 'Tensions & Gaps', blocks: ['Unexamined assumptions', 'Counter-evidence', 'Scope limitations'] },
      { name: 'Synthesis', blocks: [] },
    ],
  },
  {
    id: 'argument-map',
    name: 'Argument Map',
    description: 'Map and score a complex argument',
    glyph: '⊗',
    files: [
      { name: 'Premises', blocks: ['Premise 1', 'Premise 2', 'Premise 3'] },
      { name: 'Logical Chain', blocks: ['Inference step 1', 'Inference step 2', 'Conclusion'] },
      { name: 'Objections', blocks: ['Primary objection', 'Counter-argument'] },
    ],
  },
  {
    id: 'belief-audit',
    name: 'Belief Audit',
    description: 'Audit a strongly-held belief for blind spots',
    glyph: '◎',
    files: [
      { name: 'The Belief', blocks: ['Core belief statement', 'Origin story', 'Personal evidence'] },
      { name: 'Challenge Layer', blocks: ['What would falsify this', 'Who disagrees and why', 'Cultural context'] },
      { name: 'Integration', blocks: ['What survives the pressure', 'What needs revision'] },
    ],
  },
  {
    id: 'project-decision',
    name: 'Project Decision',
    description: 'Score the assumptions behind a key decision',
    glyph: '△',
    files: [
      { name: 'The Decision', blocks: ['Decision statement', 'Why now', 'Success criteria'] },
      { name: 'Assumptions', blocks: ['Market assumption', 'Technical assumption', 'Resource assumption'] },
      { name: 'Risks', blocks: ['Highest risk', 'Unknown unknowns', 'Mitigation path'] },
    ],
  },
  {
    id: 'philosophy',
    name: 'Philosophical Claim',
    description: 'Score a philosophical position against the Codex',
    glyph: '⬡',
    files: [
      { name: 'The Position', blocks: ['Axiom', 'Key definitions', 'Core argument'] },
      { name: 'Tradition', blocks: ['Historical precedent', 'Strongest objection in tradition', 'Where it breaks'] },
      { name: 'Frontier', blocks: ['What this position cannot account for', 'New territory it opens'] },
    ],
  },
  {
    id: 'blank',
    name: 'Blank Pyramid',
    description: 'Empty — start from scratch',
    glyph: '○',
    files: [],
  },
]

export default function PyramidList({ onOpen }) {
  const [pyramids, setPyramids] = useState([])
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loaded, setLoaded] = useState(false)
  const [showTemplates, setShowTemplates] = useState(false)
  const [templateName, setTemplateName] = useState('')
  const [selectedTemplate, setSelectedTemplate] = useState(null)

  useEffect(() => { load() }, [])

  async function load() {
    const list = await window.cascade.pyramids.list()
    setPyramids(list)
    setLoaded(true)
  }

  async function create() {
    if (!name.trim()) return
    const p = await window.cascade.pyramids.create({ name: name.trim(), description: description.trim() })
    setName(''); setDescription(''); setCreating(false)
    await load()
    onOpen(p)
  }

  async function createFromTemplate() {
    if (!templateName.trim() || !selectedTemplate) return
    const tpl = TEMPLATES.find(t => t.id === selectedTemplate)
    if (!tpl) return
    const p = await window.cascade.pyramids.create({ name: templateName.trim(), description: tpl.description })
    // Create files and blocks for the template
    for (const fileDef of tpl.files) {
      const file = await window.cascade.files.create({ pyramidId: p.id, name: fileDef.name, content: '' })
      for (let i = 0; i < fileDef.blocks.length; i++) {
        await window.cascade.blocks.create({
          fileId: file.id, pyramidId: p.id,
          title: fileDef.blocks[i], content: '',
          position: i, frameworkRefs: ['cascade'],
        })
      }
    }
    setTemplateName(''); setSelectedTemplate(null); setShowTemplates(false)
    await load()
    onOpen(p)
  }

  async function deletePyramid(e, id) {
    e.stopPropagation()
    if (!confirm('Delete this pyramid and all its contents?')) return
    await window.cascade.pyramids.delete(id)
    load()
  }

  // First-time welcome
  if (loaded && pyramids.length === 0 && !creating) {
    return (
      <div className="pyramid-list">
        <div className="welcome-screen">
          <div className="welcome-glyph">⊚</div>
          <div className="welcome-title">CASCADE CICADA TOOL</div>
          <div className="welcome-sub">A knowledge scoring engine for serious thinkers.</div>

          <div className="welcome-how">
            <div className="how-step">
              <div className="how-num">1</div>
              <div>
                <div className="how-label">Create a Pyramid</div>
                <div className="how-desc">A pyramid is a knowledge project — a topic, argument, or domain you want to pressure-test.</div>
              </div>
            </div>
            <div className="how-step">
              <div className="how-num">2</div>
              <div>
                <div className="how-label">Add files, extract blocks</div>
                <div className="how-desc">Drop in any text file. AI reads it and pulls out the core knowledge claims as blocks.</div>
              </div>
            </div>
            <div className="how-step">
              <div className="how-num">3</div>
              <div>
                <div className="how-label">Score each block</div>
                <div className="how-desc">AI scores 9 layers of epistemic depth — from your core claim (AXIOM) to the unknown edge (FRONTIER). You can override with your own sovereign score.</div>
              </div>
            </div>
            <div className="how-step">
              <div className="how-num">4</div>
              <div>
                <div className="how-label">Watch the pyramid take shape</div>
                <div className="how-desc">Strongest blocks rise to the top. Tensions, gaps, and frontier truths become visible. Knowledge gets a structure.</div>
              </div>
            </div>
          </div>

          <div className="welcome-frameworks">
            <div className="fw-intro">Your blocks are scored against one of three frameworks from the Lycheetah Codex:</div>
            <div className="fw-cards">
              <div className="fw-card">
                <span className="fw-glyph" style={{color:'#facc15'}}>△</span>
                <div className="fw-name">CASCADE</div>
                <div className="fw-desc">Does this knowledge hold under contradiction pressure? Does it reorganise correctly when challenged?</div>
              </div>
              <div className="fw-card">
                <span className="fw-glyph" style={{color:'#c084fc'}}>◈</span>
                <div className="fw-name">AURA</div>
                <div className="fw-desc">Does this align with the 7 constitutional invariants? Human primacy, honesty, reversibility, care as structure.</div>
              </div>
              <div className="fw-card">
                <span className="fw-glyph" style={{color:'#34d399'}}>∿</span>
                <div className="fw-name">LAMAGUE</div>
                <div className="fw-desc">Can this claim be formalised without losing meaning? High-precision epistemic notation for frontier research.</div>
              </div>
            </div>
          </div>

          <button className="welcome-cta" onClick={() => setCreating(true)}>
            △ Create your first pyramid
          </button>

          <div className="welcome-note">You'll need a DeepSeek API key for AI scoring — add it in Settings. It's cheap. Most scoring runs cost under $0.01.</div>
        </div>

        {creating && (
          <div className="create-overlay">
            <div className="create-card">
              <div className="create-title">NEW PYRAMID</div>
              <input type="text" placeholder="Name your pyramid..." value={name}
                onChange={e => setName(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && create()} autoFocus />
              <textarea placeholder="What is this pyramid about? (optional)" value={description}
                onChange={e => setDescription(e.target.value)} rows={2} />
              <div className="create-actions">
                <button className="btn" onClick={() => { setCreating(false); setName(''); setDescription('') }}>Cancel</button>
                <button className="btn primary" onClick={create}>Create & Open</button>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="pyramid-list">
      <div className="list-header">
        <div className="list-title">
          <span className="list-icon">△</span>
          YOUR PYRAMIDS
        </div>
        <button className="btn" onClick={() => setShowTemplates(v => !v)} title="Create pyramid from template">⬡ Templates</button>
        <button className="btn primary" onClick={() => setCreating(true)}>+ New Pyramid</button>
      </div>

      {showTemplates && (
        <div className="template-gallery">
          <div className="tg-title">FROM TEMPLATE</div>
          <div className="tg-grid">
            {TEMPLATES.map(t => (
              <div key={t.id} className={`tg-card ${selectedTemplate === t.id ? 'selected' : ''}`} onClick={() => setSelectedTemplate(t.id)}>
                <span className="tg-glyph">{t.glyph}</span>
                <div className="tg-name">{t.name}</div>
                <div className="tg-desc">{t.description}</div>
                {t.files.length > 0 && <div className="tg-files">{t.files.length} files · {t.files.reduce((a, f) => a + f.blocks.length, 0)} blocks</div>}
              </div>
            ))}
          </div>
          {selectedTemplate && (
            <div className="tg-confirm">
              <input type="text" placeholder="Pyramid name…" value={templateName} onChange={e => setTemplateName(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && createFromTemplate()} autoFocus className="tg-name-input" />
              <button className="btn primary" onClick={createFromTemplate} disabled={!templateName.trim()}>Create from template</button>
              <button className="btn" onClick={() => { setSelectedTemplate(null); setTemplateName('') }}>Cancel</button>
            </div>
          )}
        </div>
      )}

      {creating && (
        <div className="create-card">
          <div className="create-title">NEW PYRAMID</div>
          <input type="text" placeholder="Name your pyramid..." value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && create()} autoFocus />
          <textarea placeholder="What is this pyramid about? (optional)" value={description}
            onChange={e => setDescription(e.target.value)} rows={2} />
          <div className="create-actions">
            <button className="btn" onClick={() => { setCreating(false); setName(''); setDescription('') }}>Cancel</button>
            <button className="btn primary" onClick={create}>Create & Open</button>
          </div>
        </div>
      )}

      <div className="pyramid-grid">
        {pyramids.map(p => (
          <PyramidCard key={p.id} pyramid={p} onOpen={() => onOpen(p)} onDelete={(e) => deletePyramid(e, p.id)} />
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
      {pyramid.description && <div className="card-desc">{pyramid.description}</div>}
      <div className="card-footer">
        <div className="card-score" style={{ color: score > 0 ? band.textColor : 'var(--text-dim)' }}>
          {score > 0 ? <><span className="score-num">{score}</span><span className="score-band">{band.label}</span></> : <span>— unscored</span>}
        </div>
        <div className="card-date">{date}</div>
      </div>
    </div>
  )
}
