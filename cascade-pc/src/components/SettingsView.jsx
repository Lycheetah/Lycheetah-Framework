import React, { useState, useEffect } from 'react'
import './SettingsView.css'

export default function SettingsView() {
  const [key, setKey] = useState('')
  const [saved, setSaved] = useState(false)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('cascade_deepseek_key') || ''
    setKey(stored)
  }, [])

  function save() {
    localStorage.setItem('cascade_deepseek_key', key.trim())
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  function clear() {
    localStorage.removeItem('cascade_deepseek_key')
    setKey('')
  }

  const hasKey = key.trim().length > 0

  return (
    <div className="settings-view">
      <div className="settings-header">
        <div className="settings-title">⚙ SETTINGS</div>
      </div>

      <div className="settings-body">
        <div className="settings-section">
          <div className="settings-section-title">AI SCORING — DEEPSEEK</div>
          <p className="settings-p">
            CASCADE uses DeepSeek to suggest blocks and auto-score onion layers.
            Your key is stored locally — never sent anywhere except DeepSeek's API.
          </p>

          <div className="key-field">
            <label>DeepSeek API Key</label>
            <div className="key-input-row">
              <input
                type={visible ? 'text' : 'password'}
                value={key}
                onChange={e => setKey(e.target.value)}
                placeholder="sk-..."
                onKeyDown={e => e.key === 'Enter' && save()}
              />
              <button className="btn" onClick={() => setVisible(v => !v)}>
                {visible ? 'hide' : 'show'}
              </button>
            </div>
            <div className="key-actions">
              {hasKey && (
                <span className="key-status">● key stored</span>
              )}
              <button className="btn" onClick={clear}>Clear</button>
              <button className="btn primary" onClick={save}>
                {saved ? '✓ Saved' : 'Save Key'}
              </button>
            </div>
          </div>

          <div className="settings-note">
            Get a key at <strong>platform.deepseek.com</strong> — pricing is ~$0.14 per million tokens.
            Scoring a full pyramid costs pennies.
          </div>
        </div>
      </div>
    </div>
  )
}
