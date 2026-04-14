import React, { useState, useEffect } from 'react'
import PyramidList from './components/PyramidList'
import PyramidView from './components/PyramidView'
import ExperimentView from './components/ExperimentView'
import AboutView from './components/AboutView'
import SettingsView from './components/SettingsView'
import AuraTest from './components/AuraTest'
import './styles/app.css'

const TIPS = [
  'Drop a .txt or .md file into the FILES column — AI will extract knowledge blocks from it.',
  'AXIOM is your core claim. Everything else in the onion must support it.',
  'Framework score is AI-locked, scored against real Codex documents. Sovereign score is yours — up to 999.',
  'Score 101–999 for truths you hold with high conviction but can\'t yet prove. 999 = frontier.',
  'Π = E·P/S — Evidence × Power ÷ Coherence. Visible in the ring panel when a block is scored.',
  'The Experiment tab lets you run two pyramids against each other: resonance, contradiction, or synthesis.',
  'FOUNDATION cannot score higher than AXIOM × 1.1 — the evidence cannot outrank the claim.',
  'Select multiple blocks with the checkbox to see a group score.',
  'AURA Test: paste any text — AI scores it against 7 constitutional invariants.',
  'Tab through onion layers in the sovereign score input. Shift+Tab goes back.',
  'Tension detector: two blocks with a score gap >25 are flagged ⊗ — genuine friction in your knowledge.',
  'Export your pyramid as .md or .json — save dialog lets you choose the folder.',
  'The △ Viz tab shows your blocks arranged as a visual pyramid, strongest at the top.',
  'Block duplication: click ⊕ to clone a block with all 9 layers intact.',
  'Add notes to any block — they save separately from the scoring tracks.',
]

export default function App() {
  const [view, setView] = useState('pyramids')
  const [activePyramid, setActivePyramid] = useState(null)
  const [tipIndex, setTipIndex] = useState(0)
  const [tipVisible, setTipVisible] = useState(true)

  // Rotate tips every 6 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setTipVisible(false)
      setTimeout(() => {
        setTipIndex(i => (i + 1) % TIPS.length)
        setTipVisible(true)
      }, 400)
    }, 6000)
    return () => clearInterval(interval)
  }, [])

  function openPyramid(pyramid) {
    setActivePyramid(pyramid)
    setView('pyramid')
  }

  function backToList() {
    setActivePyramid(null)
    setView('pyramids')
  }

  return (
    <div className="app">
      <Sidebar view={view} setView={setView} backToList={backToList} />
      <div className="app-right">
        <main className="app-main">
          {view === 'pyramids' && <PyramidList onOpen={openPyramid} />}
          {view === 'pyramid' && activePyramid && <PyramidView pyramid={activePyramid} onBack={backToList} />}
          {view === 'experiment' && <ExperimentView />}
          {view === 'about' && <AboutView />}
          {view === 'settings' && <SettingsView />}
          {view === 'aura' && <AuraTest />}
        </main>

        {/* Rotating tip bar */}
        <div className="tip-bar">
          <span className="tip-icon">◎</span>
          <span className={`tip-text ${tipVisible ? 'visible' : ''}`}>{TIPS[tipIndex]}</span>
          <span className="tip-counter">{tipIndex + 1}/{TIPS.length}</span>
        </div>
      </div>
    </div>
  )
}

function Sidebar({ view, setView, backToList }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">⊚</div>
        <div className="sidebar-title">TCCT</div>
        <div className="sidebar-sub">CASCADE CICADA TOOL</div>
      </div>
      <nav className="sidebar-nav">
        <button className={`nav-item ${view === 'pyramids' || view === 'pyramid' ? 'active' : ''}`} onClick={backToList}>
          <span className="nav-icon">△</span>
          <span>Pyramids</span>
        </button>
        <button className={`nav-item ${view === 'experiment' ? 'active' : ''}`} onClick={() => setView('experiment')}>
          <span className="nav-icon">⊗</span>
          <span>Experiment</span>
        </button>
        <button className={`nav-item ${view === 'aura' ? 'active' : ''}`} onClick={() => setView('aura')}>
          <span className="nav-icon">◈</span>
          <span>AURA Test</span>
        </button>
        <button className={`nav-item ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
          <span className="nav-icon">⚙</span>
          <span>Settings</span>
        </button>
        <button className={`nav-item ${view === 'about' ? 'active' : ''}`} onClick={() => setView('about')}>
          <span className="nav-icon">◎</span>
          <span>About</span>
        </button>
      </nav>
      <div className="sidebar-footer">
        <div className="footer-line">Lycheetah Framework</div>
        <div className="footer-line dim">TCCT v0.1 · <a href="https://github.com/Lycheetah/CODEX_AURA_PRIME" target="_blank" rel="noreferrer" style={{color:'inherit',textDecoration:'none'}}>GitHub</a></div>
      </div>
    </aside>
  )
}
