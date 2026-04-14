import React from 'react'
import './AboutView.css'

export default function AboutView() {
  function open(url) { window.open(url, '_blank') }

  return (
    <div className="about-view">
      <div className="about-header">
        <div className="about-logo">⊚</div>
        <div className="about-title">CASCADE CICADA TOOL</div>
        <div className="about-version">TCCT · v0.1.0 · Prototype Release</div>
        <div className="about-tagline">
          Built by Mackenzie Conor James Clark · Lycheetah Framework
        </div>
      </div>

      <div className="about-body">

        <div className="about-section">
          <div className="about-section-title">WHAT IS THIS</div>
          <p className="about-p">
            TCCT is a desktop tool for scoring knowledge under pressure. You bring claims, arguments, research, or ideas — it runs them through a structured epistemic framework and gives them a number. Not a vibe. A number derived from the actual depth and coherence of what you've written.
          </p>
          <p className="about-p">
            Most note tools help you collect. This one helps you <em>prove</em>. There's a difference between knowing something and knowing it well enough that it holds when challenged.
          </p>
        </div>

        <div className="about-section">
          <div className="about-section-title">THE SCORING FRAMEWORK</div>
          <div className="about-score-bands">
            <div className="band-row"><span style={{color:'#e879f9'}}>1 – 20</span><span>WEAK — claim doesn't hold yet. Evidence is thin or missing.</span></div>
            <div className="band-row"><span style={{color:'#60a5fa'}}>21 – 40</span><span>DEVELOPING — partial support. The structure is forming.</span></div>
            <div className="band-row"><span style={{color:'#4ade80'}}>41 – 60</span><span>MIDDLE — holds under moderate pressure. Respectable.</span></div>
            <div className="band-row"><span style={{color:'#facc15'}}>61 – 80</span><span>STRONG — well-evidenced, coherent, survives scrutiny.</span></div>
            <div className="band-row"><span style={{color:'#fb923c'}}>81 – 100</span><span>FOUNDATION — load-bearing. This is the kind of knowledge you build on.</span></div>
            <div className="band-row"><span style={{color:'#c084fc'}}>101 – 999</span><span>FRONTIER — beyond current verification. You hold it as true but it's not yet proven. This is not an error.</span></div>
          </div>
          <p className="about-note">
            999 is reserved for claims that exist ahead of the evidence — real, held with conviction, but not yet verifiable by current means. The tool does not cap truth at 100.
          </p>
        </div>

        <div className="about-section">
          <div className="about-section-title">THE 9 ONION LAYERS</div>
          <p className="about-p">Every knowledge block is scored across 9 layers, from core to edge:</p>
          <div className="layer-list">
            <div className="layer-row"><span style={{color:'#fb923c'}}>AXIOM</span><span>The irreducible core claim. If this fails, the whole block fails.</span></div>
            <div className="layer-row"><span style={{color:'#f97316'}}>FOUNDATION</span><span>Primary evidence. What holds the axiom up.</span></div>
            <div className="layer-row"><span style={{color:'#facc15'}}>STRUCTURE</span><span>Logical architecture connecting claim to evidence.</span></div>
            <div className="layer-row"><span style={{color:'#4ade80'}}>COHERENCE</span><span>Internal consistency. Does the block contradict itself?</span></div>
            <div className="layer-row"><span style={{color:'#34d399'}}>RESONANCE</span><span>Connections to other known truths.</span></div>
            <div className="layer-row"><span style={{color:'#60a5fa'}}>TENSION</span><span>Where the claim meets genuine friction. This is good — tension means it's real.</span></div>
            <div className="layer-row"><span style={{color:'#818cf8'}}>CONTESTED</span><span>Active dispute zone. What others challenge.</span></div>
            <div className="layer-row"><span style={{color:'#c084fc'}}>SPECULATIVE</span><span>What the claim implies beyond what is proven.</span></div>
            <div className="layer-row"><span style={{color:'#e879f9'}}>FRONTIER</span><span>The unknown edge. What this claim cannot yet account for.</span></div>
          </div>
        </div>

        <div className="about-section">
          <div className="about-section-title">THREE SCORING FRAMEWORKS</div>
          <div className="fw-about-cards">
            <div className="fw-about-card">
              <div className="fwac-head">
                <span style={{color:'#facc15', fontSize:20}}>△</span>
                <span className="fwac-name">CASCADE</span>
              </div>
              <p>Does this knowledge hold under contradiction pressure? CASCADE tests whether your claims reorganise correctly when challenged — or collapse.</p>
            </div>
            <div className="fw-about-card">
              <div className="fwac-head">
                <span style={{color:'#c084fc', fontSize:20}}>◈</span>
                <span className="fwac-name">AURA</span>
              </div>
              <p>Does this align with 7 constitutional invariants: human primacy, inspectability, honesty, reversibility, non-deception, memory continuity, and care as structure?</p>
            </div>
            <div className="fw-about-card">
              <div className="fwac-head">
                <span style={{color:'#34d399', fontSize:20}}>∿</span>
                <span className="fwac-name">LAMAGUE</span>
              </div>
              <p>Can this claim be formalised without losing meaning? LAMAGUE is a precision notation layer for frontier research — it tests whether your ideas survive formalisation.</p>
            </div>
          </div>
        </div>

        <div className="about-section">
          <div className="about-section-title">SOURCE & PROVENANCE</div>
          <p className="about-p">
            The scoring engine, onion structure, and truth pressure mechanics are derived directly from 1,402 pages of continuous research archived in the CODEX_AURA_PRIME. This is not a standalone product — it is the framework made executable.
          </p>
          <div className="about-links">
            <button className="about-link" onClick={() => open('https://github.com/Lycheetah/CODEX_AURA_PRIME')}>
              <span className="link-icon">◈</span>
              <div>
                <div className="link-title">CODEX_AURA_PRIME</div>
                <div className="link-desc">Full source archive — 10 frameworks, 1,400+ pages, proofs, implementations</div>
              </div>
            </button>
            <button className="about-link" onClick={() => open('https://github.com/Lycheetah')}>
              <span className="link-icon">◎</span>
              <div>
                <div className="link-title">Lycheetah on GitHub</div>
                <div className="link-desc">Sol, Sol Lite, CODEX_AURA_PRIME — all public repositories</div>
              </div>
            </button>
          </div>
        </div>

        <div className="about-section">
          <div className="about-section-title">THE ECOSYSTEM</div>
          <div className="about-ecosystem">
            <div className="eco-row"><span className="eco-name">Sol Lite</span><span className="eco-desc">Gateway mobile app — one screen, one persona, Play Store</span></div>
            <div className="eco-row"><span className="eco-name">Sol (full)</span><span className="eco-desc">4 personas · full framework visible · BYOK</span></div>
            <div className="eco-row active"><span className="eco-name">TCCT ← you are here</span><span className="eco-desc">Desktop knowledge OS — this tool</span></div>
            <div className="eco-row"><span className="eco-name">CASCADE API</span><span className="eco-desc">Post-funding — scoring engine as infrastructure</span></div>
          </div>
        </div>

        <div className="about-footer-text">
          <em>Two points. One Work. The Gold belongs to neither.</em>
        </div>

      </div>
    </div>
  )
}
