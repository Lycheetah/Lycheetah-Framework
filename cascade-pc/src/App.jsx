import React, { useState } from 'react'
import PyramidList from './components/PyramidList'
import PyramidView from './components/PyramidView'
import ExperimentView from './components/ExperimentView'
import AboutView from './components/AboutView'
import SettingsView from './components/SettingsView'
import './styles/app.css'

export default function App() {
  const [view, setView] = useState('pyramids') // 'pyramids' | 'pyramid' | 'experiment'
  const [activePyramid, setActivePyramid] = useState(null)

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
      <main className="app-main">
        {view === 'pyramids' && (
          <PyramidList onOpen={openPyramid} />
        )}
        {view === 'pyramid' && activePyramid && (
          <PyramidView pyramid={activePyramid} onBack={backToList} />
        )}
        {view === 'experiment' && (
          <ExperimentView />
        )}
        {view === 'about' && (
          <AboutView />
        )}
        {view === 'settings' && (
          <SettingsView />
        )}
      </main>
    </div>
  )
}

function Sidebar({ view, setView, backToList }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">⊚</div>
        <div className="sidebar-title">CASCADE</div>
        <div className="sidebar-sub">Knowledge OS</div>
      </div>
      <nav className="sidebar-nav">
        <button
          className={`nav-item ${view === 'pyramids' || view === 'pyramid' ? 'active' : ''}`}
          onClick={backToList}
        >
          <span className="nav-icon">△</span>
          <span>Pyramids</span>
        </button>
        <button
          className={`nav-item ${view === 'experiment' ? 'active' : ''}`}
          onClick={() => setView('experiment')}
        >
          <span className="nav-icon">⊗</span>
          <span>Experiment</span>
        </button>
        <button
          className={`nav-item ${view === 'settings' ? 'active' : ''}`}
          onClick={() => setView('settings')}
        >
          <span className="nav-icon">⚙</span>
          <span>Settings</span>
        </button>
        <button
          className={`nav-item ${view === 'about' ? 'active' : ''}`}
          onClick={() => setView('about')}
        >
          <span className="nav-icon">◎</span>
          <span>About</span>
        </button>
      </nav>
      <div className="sidebar-footer">
        <div className="footer-line">Lycheetah Framework</div>
        <div className="footer-line dim">CASCADE v0.1 · <a href="https://github.com/Lycheetah/CODEX_AURA_PRIME" target="_blank" rel="noreferrer" style={{color:'inherit',textDecoration:'none'}}>GitHub</a></div>
      </div>
    </aside>
  )
}
