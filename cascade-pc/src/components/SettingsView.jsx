import React, { useState, useEffect } from 'react'
import { getCustomFrameworks, saveCustomFrameworks, isNakedMode, setNakedMode, isPersonalFilterOn, setPersonalFilter, FRAMEWORK_LIST } from '../scoring/frameworks'
import './SettingsView.css'

const PROVIDERS = [
  { id: 'deepseek',  label: 'DeepSeek',        note: 'platform.deepseek.com — ~$0.14/M tokens. Scoring a full pyramid costs pennies.' },
  { id: 'anthropic', label: 'Anthropic Claude', note: 'console.anthropic.com — Uses claude-sonnet-4-6. Excellent reasoning quality.' },
  { id: 'openai',    label: 'OpenAI GPT-4o',    note: 'platform.openai.com — Uses gpt-4o. Strong general scoring.' },
  { id: 'ollama',    label: 'Ollama (local)',    note: 'Runs locally at localhost:11434. No API key needed. Install Ollama + pull a model.' },
]

const GLYPHS = ['◆', '◇', '○', '●', '△', '▲', '□', '■', '◈', '⊗', '⊕', '∑', '∞', '⊛', '◎', '⬡']
const COLORS = ['#facc15', '#60a5fa', '#c084fc', '#34d399', '#f87171', '#fb923c', '#a78bfa', '#e879f9']

const blankFw = () => ({ id: `custom_${Date.now()}`, name: '', glyph: '◆', color: '#60a5fa', tagline: '', essentials: '' })

export default function SettingsView() {
  const [provider, setProvider]       = useState('deepseek')
  const [keys, setKeys]               = useState({ deepseek: '', anthropic: '', openai: '' })
  const [ollamaModel, setOllamaModel] = useState('llama3')
  const [visible, setVisible]         = useState({})
  const [saved, setSaved]             = useState(false)
  const [nakedMode, setNakedModeState]       = useState(false)
  const [personalFilter, setPersonalFilterState] = useState(false)
  const [theme, setThemeState]               = useState('dark')
  const [customFws, setCustomFws]     = useState([])
  const [editingFw, setEditingFw]     = useState(null) // framework being edited
  const [fwDraft, setFwDraft]         = useState(null)
  const [apiRunning, setApiRunning]   = useState(false)
  const [apiLoading, setApiLoading]   = useState(false)

  useEffect(() => {
    window.cascade.api?.status().then(s => setApiRunning(s.running)).catch(() => {})
    setProvider(localStorage.getItem('cascade_provider') || 'deepseek')
    setKeys({
      deepseek:  localStorage.getItem('cascade_deepseek_key')  || '',
      anthropic: localStorage.getItem('cascade_anthropic_key') || '',
      openai:    localStorage.getItem('cascade_openai_key')    || '',
    })
    setOllamaModel(localStorage.getItem('cascade_ollama_model') || 'llama3')
    setNakedModeState(isNakedMode())
    setPersonalFilterState(isPersonalFilterOn())
    const savedTheme = localStorage.getItem('cascade_theme') || 'dark'
    setThemeState(savedTheme)
    document.documentElement.setAttribute('data-theme', savedTheme === 'dark' ? '' : savedTheme)
    setCustomFws(getCustomFrameworks())
  }, [])

  function save() {
    localStorage.setItem('cascade_provider',      provider)
    localStorage.setItem('cascade_deepseek_key',  keys.deepseek.trim())
    localStorage.setItem('cascade_anthropic_key', keys.anthropic.trim())
    localStorage.setItem('cascade_openai_key',    keys.openai.trim())
    localStorage.setItem('cascade_ollama_model',  ollamaModel.trim() || 'llama3')
    setNakedMode(nakedMode)
    setPersonalFilter(personalFilter)
    localStorage.setItem('cascade_theme', theme)
    document.documentElement.setAttribute('data-theme', theme === 'dark' ? '' : theme)
    saveCustomFrameworks(customFws)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  function setKey(p, val) { setKeys(k => ({ ...k, [p]: val })) }
  function clearKey(p) { setKey(p, ''); localStorage.removeItem(`cascade_${p}_key`) }
  function toggleVisible(p) { setVisible(v => ({ ...v, [p]: !v[p] })) }

  // Custom framework ops
  function startNew() {
    const fw = blankFw()
    setFwDraft(fw)
    setEditingFw('__new__')
  }

  function startEdit(fw) {
    setFwDraft({ ...fw })
    setEditingFw(fw.id)
  }

  function cancelEdit() { setEditingFw(null); setFwDraft(null) }

  function saveFwDraft() {
    if (!fwDraft.name.trim() || !fwDraft.essentials.trim()) return
    const fw = { ...fwDraft, name: fwDraft.name.trim(), tagline: fwDraft.tagline.trim() }
    if (editingFw === '__new__') {
      setCustomFws(prev => [...prev, fw])
    } else {
      setCustomFws(prev => prev.map(f => f.id === editingFw ? fw : f))
    }
    setEditingFw(null)
    setFwDraft(null)
  }

  function deleteFw(id) {
    if (!confirm('Delete this framework?')) return
    setCustomFws(prev => prev.filter(f => f.id !== id))
  }

  const activeProviderInfo = PROVIDERS.find(p => p.id === provider)

  return (
    <div className="settings-view">
      <div className="settings-header">
        <div className="settings-title">⚙ SETTINGS</div>
      </div>

      <div className="settings-body">

        {/* Provider selector */}
        <div className="settings-section">
          <div className="settings-section-title">AI PROVIDER</div>
          <p className="settings-p">
            All scoring, synthesis, and paradox analysis routes through the selected provider.
          </p>
          <div className="provider-grid">
            {PROVIDERS.map(p => (
              <button
                key={p.id}
                className={`provider-btn${provider === p.id ? ' active' : ''}`}
                onClick={() => setProvider(p.id)}
              >
                {provider === p.id && <span className="provider-dot">●</span>}
                {p.label}
              </button>
            ))}
          </div>
          {activeProviderInfo && (
            <div className="settings-note" style={{ marginTop: 14 }}>{activeProviderInfo.note}</div>
          )}
        </div>

        {/* DeepSeek key */}
        <div className="settings-section">
          <div className="settings-section-title">DEEPSEEK API KEY</div>
          <div className="key-field">
            <label>API Key</label>
            <div className="key-input-row">
              <input type={visible.deepseek ? 'text' : 'password'} value={keys.deepseek}
                onChange={e => setKey('deepseek', e.target.value)} placeholder="sk-..."
                onKeyDown={e => e.key === 'Enter' && save()} />
              <button className="btn" onClick={() => toggleVisible('deepseek')}>{visible.deepseek ? 'hide' : 'show'}</button>
            </div>
            <div className="key-actions">
              {keys.deepseek.trim() && <span className="key-status">● key stored</span>}
              <button className="btn" onClick={() => clearKey('deepseek')}>Clear</button>
            </div>
          </div>
        </div>

        {/* Anthropic key */}
        <div className="settings-section">
          <div className="settings-section-title">ANTHROPIC API KEY</div>
          <div className="key-field">
            <label>API Key</label>
            <div className="key-input-row">
              <input type={visible.anthropic ? 'text' : 'password'} value={keys.anthropic}
                onChange={e => setKey('anthropic', e.target.value)} placeholder="sk-ant-..."
                onKeyDown={e => e.key === 'Enter' && save()} />
              <button className="btn" onClick={() => toggleVisible('anthropic')}>{visible.anthropic ? 'hide' : 'show'}</button>
            </div>
            <div className="key-actions">
              {keys.anthropic.trim() && <span className="key-status">● key stored</span>}
              <button className="btn" onClick={() => clearKey('anthropic')}>Clear</button>
            </div>
          </div>
        </div>

        {/* OpenAI key */}
        <div className="settings-section">
          <div className="settings-section-title">OPENAI API KEY</div>
          <div className="key-field">
            <label>API Key</label>
            <div className="key-input-row">
              <input type={visible.openai ? 'text' : 'password'} value={keys.openai}
                onChange={e => setKey('openai', e.target.value)} placeholder="sk-..."
                onKeyDown={e => e.key === 'Enter' && save()} />
              <button className="btn" onClick={() => toggleVisible('openai')}>{visible.openai ? 'hide' : 'show'}</button>
            </div>
            <div className="key-actions">
              {keys.openai.trim() && <span className="key-status">● key stored</span>}
              <button className="btn" onClick={() => clearKey('openai')}>Clear</button>
            </div>
          </div>
        </div>

        {/* Ollama */}
        <div className="settings-section">
          <div className="settings-section-title">OLLAMA (LOCAL)</div>
          <p className="settings-p">No API key needed. Requires Ollama running at localhost:11434.</p>
          <div className="key-field">
            <label>Model name</label>
            <div className="key-input-row">
              <input type="text" value={ollamaModel} onChange={e => setOllamaModel(e.target.value)}
                placeholder="llama3" onKeyDown={e => e.key === 'Enter' && save()} />
            </div>
          </div>
        </div>

        {/* Theme */}
        <div className="settings-section">
          <div className="settings-section-title">THEME</div>
          <p className="settings-p">Visual theme for the entire interface.</p>
          <div className="theme-grid">
            {[
              { id: 'dark',          label: 'Dark',          note: 'Default — deep black' },
              { id: 'light',         label: 'Light',         note: 'Warm paper tones' },
              { id: 'high-contrast', label: 'High Contrast', note: 'Maximum legibility' },
            ].map(t => (
              <button key={t.id} className={`theme-btn${theme === t.id ? ' active' : ''}`}
                onClick={() => { setThemeState(t.id); document.documentElement.setAttribute('data-theme', t.id === 'dark' ? '' : t.id) }}>
                {theme === t.id && <span className="provider-dot">●</span>}
                <span className="theme-label">{t.label}</span>
                <span className="theme-note">{t.note}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Naked Mode */}
        <div className="settings-section">
          <div className="settings-section-title">NAKED MODE</div>
          <p className="settings-p">
            Strips all Codex framework references from scoring prompts. The AI scores purely on internal
            truth pressure — logical consistency, evidence quality, epistemic honesty. Your epistemology, not the Codex.
          </p>
          <div className="naked-toggle-row">
            <button
              className={`naked-toggle-btn${nakedMode ? ' active' : ''}`}
              onClick={() => setNakedModeState(v => !v)}
            >
              <span className="naked-indicator">{nakedMode ? '⊛' : '○'}</span>
              {nakedMode ? 'NAKED MODE ON — No Codex references' : 'NAKED MODE OFF — Codex-referenced scoring'}
            </button>
          </div>
          {nakedMode && (
            <div className="settings-note" style={{ borderColor: 'var(--gold)', marginTop: 8 }}>
              Active: scoring uses pure epistemic logic, no framework essentials injected.
            </div>
          )}
        </div>

        {/* Personal Content Filter */}
        <div className="settings-section">
          <div className="settings-section-title">PERSONAL CONTENT FILTER</div>
          <p className="settings-p">
            When on, AI is instructed to skip scoring blocks that appear to contain personal emotional content,
            grief, trauma, or vulnerable self-disclosure. Prevents the tool from measuring your pain.
          </p>
          <div className="naked-toggle-row">
            <button
              className={`naked-toggle-btn${personalFilter ? ' active' : ''}`}
              onClick={() => setPersonalFilterState(v => !v)}
            >
              <span className="naked-indicator">{personalFilter ? '⊛' : '○'}</span>
              {personalFilter ? 'FILTER ON — Personal content will not be scored' : 'FILTER OFF — All content scored equally'}
            </button>
          </div>
          {personalFilter && (
            <div className="settings-note" style={{ borderColor: 'var(--layer-resonance)', marginTop: 8 }}>
              Active: AI will redirect instead of scoring personal/emotional blocks.
            </div>
          )}
        </div>

        {/* Custom frameworks */}
        <div className="settings-section">
          <div className="settings-section-title">CUSTOM FRAMEWORKS</div>
          <p className="settings-p">
            Define your own scoring frameworks. Each framework is injected into the AI's scoring context
            the same way CASCADE, AURA, and LAMAGUE are. Your epistemology, operationalized.
          </p>

          {/* Built-in list (read-only) */}
          <div className="fw-list">
            {FRAMEWORK_LIST.map(fw => (
              <div key={fw.id} className="fw-item builtin">
                <span className="fw-glyph" style={{ color: fw.color }}>{fw.glyph}</span>
                <div className="fw-info">
                  <span className="fw-name">{fw.name}</span>
                  <span className="fw-tagline">{fw.tagline}</span>
                </div>
                <span className="fw-badge">built-in</span>
              </div>
            ))}

            {customFws.map(fw => (
              <div key={fw.id} className="fw-item custom">
                <span className="fw-glyph" style={{ color: fw.color }}>{fw.glyph}</span>
                <div className="fw-info">
                  <span className="fw-name">{fw.name}</span>
                  <span className="fw-tagline">{fw.tagline || '—'}</span>
                </div>
                <div className="fw-actions">
                  <button className="btn" onClick={() => startEdit(fw)}>Edit</button>
                  <button className="btn danger" onClick={() => deleteFw(fw.id)}>×</button>
                </div>
              </div>
            ))}
          </div>

          {editingFw ? (
            <div className="fw-editor">
              <div className="fw-editor-title">{editingFw === '__new__' ? 'New framework' : 'Edit framework'}</div>

              <div className="fw-field">
                <label>Name</label>
                <input type="text" value={fwDraft.name} onChange={e => setFwDraft(f => ({ ...f, name: e.target.value }))}
                  placeholder="MY FRAMEWORK" />
              </div>

              <div className="fw-field">
                <label>Tagline</label>
                <input type="text" value={fwDraft.tagline} onChange={e => setFwDraft(f => ({ ...f, tagline: e.target.value }))}
                  placeholder="One line: what this framework measures" />
              </div>

              <div className="fw-field">
                <label>Glyph</label>
                <div className="glyph-picker">
                  {GLYPHS.map(g => (
                    <button key={g} className={`glyph-btn${fwDraft.glyph === g ? ' active' : ''}`}
                      onClick={() => setFwDraft(f => ({ ...f, glyph: g }))}>{g}</button>
                  ))}
                </div>
              </div>

              <div className="fw-field">
                <label>Color</label>
                <div className="color-picker">
                  {COLORS.map(c => (
                    <button key={c} className={`color-btn${fwDraft.color === c ? ' active' : ''}`}
                      style={{ background: c }} onClick={() => setFwDraft(f => ({ ...f, color: c }))} />
                  ))}
                </div>
              </div>

              <div className="fw-field">
                <label>Framework essentials <span className="fw-field-hint">(injected into scoring prompt)</span></label>
                <textarea
                  value={fwDraft.essentials}
                  onChange={e => setFwDraft(f => ({ ...f, essentials: e.target.value }))}
                  placeholder={`Describe your framework's scoring criteria.\n\nWhat makes a claim strong under this framework?\nWhat makes it weak?\nWhat are the key principles?\n\nThis text is injected directly into the AI's scoring context.`}
                  rows={10}
                  className="fw-essentials-textarea"
                />
              </div>

              <div className="fw-editor-actions">
                <button className="btn" onClick={cancelEdit}>Cancel</button>
                <button className="btn primary" onClick={saveFwDraft}
                  disabled={!fwDraft.name.trim() || !fwDraft.essentials.trim()}>
                  {editingFw === '__new__' ? 'Create Framework' : 'Save Changes'}
                </button>
              </div>
            </div>
          ) : (
            <button className="btn fw-add-btn" onClick={startNew}>+ New framework</button>
          )}
        </div>

        {/* Local API Server */}
        <div className="settings-section">
          <div className="settings-section-title">LOCAL API SERVER</div>
          <p className="settings-p">
            Exposes a read-only HTTP server at <code style={{color:'var(--gold-dim)',fontSize:11}}>localhost:7432</code>.
            Lets external tools (scripts, Obsidian plugins, automations) query your pyramids, blocks, and scores.
            Starts automatically with the app.
          </p>
          <div className="naked-toggle-row">
            <button
              className={`naked-toggle-btn${apiRunning ? ' active' : ''}`}
              disabled={apiLoading}
              onClick={async () => {
                setApiLoading(true)
                try {
                  if (apiRunning) { await window.cascade.api.stop(); setApiRunning(false) }
                  else { await window.cascade.api.start(); setApiRunning(true) }
                } finally { setApiLoading(false) }
              }}
            >
              <span className="naked-indicator">{apiRunning ? '⊛' : '○'}</span>
              {apiLoading ? 'Working…' : apiRunning ? 'API SERVER RUNNING — port 7432' : 'API SERVER STOPPED'}
            </button>
          </div>
          {apiRunning && (
            <div className="settings-note" style={{ borderColor: 'var(--layer-resonance)', marginTop: 8 }}>
              <div style={{marginBottom:6,fontWeight:600}}>Endpoints (GET, read-only):</div>
              {[
                ['/status',   'Server status + version'],
                ['/pyramids', 'All pyramids with aggregate scores'],
                ['/files',    'All files (query: ?pyramidId=…)'],
                ['/blocks',   'All blocks (query: ?fileId=… or ?pyramidId=…)'],
                ['/layers',   'All onion-layer scores (query: ?blockId=…)'],
                ['/audit',    'Session audit log (last 500 entries)'],
                ['/search',   'Search blocks by content (query: ?q=…)'],
              ].map(([ep, desc]) => (
                <div key={ep} style={{display:'flex',gap:12,alignItems:'baseline',marginBottom:4}}>
                  <code style={{color:'var(--gold)',fontSize:10,minWidth:100}}>{ep}</code>
                  <span style={{fontSize:10,color:'var(--text-secondary)'}}>{desc}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Save button */}
        <div className="settings-section">
          <button className="btn primary save-all-btn" onClick={save}>
            {saved ? '✓ Saved' : 'Save All Settings'}
          </button>
        </div>

      </div>
    </div>
  )
}
