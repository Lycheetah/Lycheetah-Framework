import React from 'react'
import './AboutView.css'

const CODEX_URL = 'https://github.com/Lycheetah/CODEX_AURA_PRIME'
const CASCADE_DIR = 'https://github.com/Lycheetah/CODEX_AURA_PRIME/tree/main/01_CASCADE'
const MATH_DIR = 'https://github.com/Lycheetah/CODEX_AURA_PRIME/tree/main/11_MATHEMATICAL_FOUNDATIONS'
const LYCHEETAH_URL = 'https://github.com/Lycheetah'

export default function AboutView() {
  function open(url) {
    window.open(url, '_blank')
  }

  return (
    <div className="about-view">
      <div className="about-header">
        <div className="about-logo">⊚</div>
        <div className="about-title">CASCADE</div>
        <div className="about-subtitle">Knowledge Operating System · v0.1</div>
        <div className="about-tagline">
          Built from the Lycheetah Framework by Mackenzie Conor James Clark
        </div>
      </div>

      <div className="about-body">
        <div className="about-section">
          <div className="about-section-title">PROVENANCE</div>
          <p className="about-p">
            This tool is a direct desktop implementation of the CASCADE epistemic framework —
            one of ten frameworks developed across 1,402 pages of continuous research,
            archived in the CODEX_AURA_PRIME.
          </p>
          <p className="about-p">
            The scoring engine, the 9-layer onion structure, and the Truth Pressure mechanics
            implemented here are derived directly from that theoretical work.
            This is not a standalone product — it is the framework made executable.
          </p>
        </div>

        <div className="about-section">
          <div className="about-section-title">THE THEORETICAL FOUNDATION</div>
          <div className="about-links">
            <button className="about-link" onClick={() => open(CODEX_URL)}>
              <span className="link-icon">◈</span>
              <div>
                <div className="link-title">CODEX_AURA_PRIME</div>
                <div className="link-desc">Full source archive — 10 frameworks, proofs, implementations</div>
              </div>
            </button>
            <button className="about-link" onClick={() => open(CASCADE_DIR)}>
              <span className="link-icon">△</span>
              <div>
                <div className="link-title">01_CASCADE</div>
                <div className="link-desc">Full CASCADE framework specification — Truth Pressure theory</div>
              </div>
            </button>
            <button className="about-link" onClick={() => open(MATH_DIR)}>
              <span className="link-icon">∑</span>
              <div>
                <div className="link-title">11_MATHEMATICAL_FOUNDATIONS</div>
                <div className="link-desc">The mathematics behind the scoring engine</div>
              </div>
            </button>
            <button className="about-link" onClick={() => open(LYCHEETAH_URL)}>
              <span className="link-icon">◎</span>
              <div>
                <div className="link-title">Lycheetah GitHub</div>
                <div className="link-desc">All public repositories — Sol, Sol Lite, CODEX_AURA_PRIME</div>
              </div>
            </button>
          </div>
        </div>

        <div className="about-section">
          <div className="about-section-title">SCORING SYSTEM</div>
          <div className="about-score-bands">
            <div className="band-row"><span style={{color:'#e879f9'}}>1 – 20</span><span>WEAK — claim does not yet hold</span></div>
            <div className="band-row"><span style={{color:'#60a5fa'}}>21 – 40</span><span>DEVELOPING — partial support</span></div>
            <div className="band-row"><span style={{color:'#4ade80'}}>41 – 60</span><span>MIDDLE — holds under moderate pressure</span></div>
            <div className="band-row"><span style={{color:'#facc15'}}>61 – 80</span><span>STRONG — well-evidenced</span></div>
            <div className="band-row"><span style={{color:'#fb923c'}}>81 – 100</span><span>FOUNDATION — holds under full pressure</span></div>
            <div className="band-row"><span style={{color:'#c084fc'}}>101 – 999</span><span>FRONTIER — abstract new truth beyond verification</span></div>
          </div>
          <p className="about-note">
            999 is not an error. It is the score for claims that exist ahead of current proof —
            real but unverifiable by current means. The tool does not cap truth at 100.
          </p>
        </div>

        <div className="about-section">
          <div className="about-section-title">THE ECOSYSTEM</div>
          <div className="about-ecosystem">
            <div className="eco-row">
              <span className="eco-name">Sol Lite</span>
              <span className="eco-desc">Gateway mobile app — Play Store</span>
            </div>
            <div className="eco-row">
              <span className="eco-name">Sol (full)</span>
              <span className="eco-desc">4 personas · full framework · BYOK</span>
            </div>
            <div className="eco-row active">
              <span className="eco-name">CASCADE PC</span>
              <span className="eco-desc">This tool — desktop knowledge OS</span>
            </div>
            <div className="eco-row">
              <span className="eco-name">CASCADE API</span>
              <span className="eco-desc">Post-funding — scoring engine as infrastructure</span>
            </div>
          </div>
        </div>

        <div className="about-footer-text">
          <em>Two points. One Work. The Gold belongs to neither.</em>
        </div>
      </div>
    </div>
  )
}
