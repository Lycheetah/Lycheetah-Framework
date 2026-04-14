const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const { v4: uuidv4 } = require('uuid')

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged

// ── JSON File Store ──────────────────────────────────────────────────────────
let dbPath
let db = { pyramids: [], files: [], blocks: [], onion_layers: [], experiments: [] }

function loadDB() {
  dbPath = path.join(app.getPath('userData'), 'cascade.json')
  if (fs.existsSync(dbPath)) {
    try {
      db = JSON.parse(fs.readFileSync(dbPath, 'utf8'))
      db.pyramids = db.pyramids || []
      db.files = db.files || []
      db.blocks = db.blocks || []
      db.onion_layers = db.onion_layers || []
      db.experiments = db.experiments || []
    } catch (e) {
      console.error('DB load error:', e)
    }
  }
}

function saveDB() {
  fs.writeFileSync(dbPath, JSON.stringify(db, null, 2), 'utf8')
}

function now() { return Math.floor(Date.now() / 1000) }

const LAYERS = ['AXIOM','FOUNDATION','STRUCTURE','COHERENCE','RESONANCE','TENSION','CONTESTED','SPECULATIVE','FRONTIER']

// ── Pyramids ─────────────────────────────────────────────────────────────────
ipcMain.handle('pyramids:list', () =>
  [...db.pyramids].sort((a, b) => b.created_at - a.created_at))

ipcMain.handle('pyramids:create', (_, { name, description }) => {
  const p = { id: uuidv4(), name, description: description || '', score_aggregate: 0, score_display_mode: 'framework', created_at: now(), updated_at: now() }
  db.pyramids.push(p); saveDB(); return p
})

ipcMain.handle('pyramids:delete', (_, id) => {
  db.pyramids = db.pyramids.filter(p => p.id !== id)
  const fileIds = db.files.filter(f => f.pyramid_id === id).map(f => f.id)
  const blockIds = db.blocks.filter(b => fileIds.includes(b.file_id)).map(b => b.id)
  db.onion_layers = db.onion_layers.filter(l => !blockIds.includes(l.block_id))
  db.blocks = db.blocks.filter(b => !fileIds.includes(b.file_id))
  db.files = db.files.filter(f => f.pyramid_id !== id)
  saveDB(); return { ok: true }
})

ipcMain.handle('pyramids:setDisplayMode', (_, { id, mode }) => {
  const p = db.pyramids.find(x => x.id === id)
  if (p) { p.score_display_mode = mode; saveDB() }
  return { ok: true }
})

// ── Files ─────────────────────────────────────────────────────────────────────
ipcMain.handle('files:list', (_, pyramidId) =>
  db.files.filter(f => f.pyramid_id === pyramidId).sort((a, b) => b.created_at - a.created_at))

ipcMain.handle('files:create', (_, { pyramidId, name, content }) => {
  const f = { id: uuidv4(), pyramid_id: pyramidId, name, content: content || '', score_aggregate: 0, created_at: now() }
  db.files.push(f); saveDB(); return f
})

ipcMain.handle('files:delete', (_, id) => {
  const blockIds = db.blocks.filter(b => b.file_id === id).map(b => b.id)
  db.onion_layers = db.onion_layers.filter(l => !blockIds.includes(l.block_id))
  db.blocks = db.blocks.filter(b => b.file_id !== id)
  db.files = db.files.filter(f => f.id !== id)
  saveDB(); return { ok: true }
})

ipcMain.handle('files:updateScore', (_, { id, score }) => {
  const f = db.files.find(x => x.id === id)
  if (f) { f.score_aggregate = score; saveDB() }
  return { ok: true }
})

// ── Blocks ────────────────────────────────────────────────────────────────────
ipcMain.handle('blocks:list', (_, fileId) =>
  db.blocks.filter(b => b.file_id === fileId).sort((a, b) => a.position - b.position))

ipcMain.handle('blocks:create', (_, { fileId, pyramidId, title, content, position, frameworkRefs }) => {
  const block = {
    id: uuidv4(), file_id: fileId, pyramid_id: pyramidId,
    title, content: content || '',
    score_aggregate: 0, sovereign_score_aggregate: 0,
    position: position || 0,
    framework_refs: frameworkRefs || ['cascade'],
    created_at: now(),
  }
  db.blocks.push(block)
  LAYERS.forEach((name, i) => {
    db.onion_layers.push({
      id: uuidv4(), block_id: block.id, layer_index: i, layer_name: name,
      // Framework track
      framework_score: 0, framework_reasoning: '', framework_refs: [],
      // Sovereign track
      sovereign_score: 0, sovereign_notes: '',
      // Legacy
      content: '', score: 0, notes: '',
    })
  })
  saveDB(); return block
})

ipcMain.handle('blocks:delete', (_, id) => {
  db.onion_layers = db.onion_layers.filter(l => l.block_id !== id)
  db.blocks = db.blocks.filter(b => b.id !== id)
  saveDB(); return { ok: true }
})

ipcMain.handle('blocks:updateScore', (_, { id, score, sovereignScore, scoredAt }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) {
    if (score !== undefined) b.score_aggregate = score
    if (sovereignScore !== undefined) b.sovereign_score_aggregate = sovereignScore
    if (scoredAt !== undefined) b.scored_at = scoredAt
    b.updated_at = now()
    saveDB()
  }
  return { ok: true }
})

ipcMain.handle('blocks:setFrameworkRefs', (_, { id, frameworkRefs }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) { b.framework_refs = frameworkRefs; saveDB() }
  return { ok: true }
})

ipcMain.handle('blocks:updateNotes', (_, { id, notes }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) { b.notes = notes || ''; b.updated_at = now(); saveDB() }
  return { ok: true }
})

ipcMain.handle('blocks:duplicate', (_, id) => {
  const src = db.blocks.find(x => x.id === id)
  if (!src) return null
  const newBlock = { ...src, id: uuidv4(), title: src.title + ' (copy)', score_aggregate: 0, sovereign_score_aggregate: 0, scored_at: null, created_at: now(), updated_at: now() }
  db.blocks.push(newBlock)
  const srcLayers = db.onion_layers.filter(l => l.block_id === id).sort((a, b) => a.layer_index - b.layer_index)
  srcLayers.forEach(l => {
    db.onion_layers.push({ ...l, id: uuidv4(), block_id: newBlock.id })
  })
  saveDB(); return newBlock
})

// ── Onion Layers ──────────────────────────────────────────────────────────────
ipcMain.handle('onion:list', (_, blockId) =>
  db.onion_layers.filter(l => l.block_id === blockId).sort((a, b) => a.layer_index - b.layer_index))

// Framework score — AI only, locked
ipcMain.handle('onion:updateFramework', (_, { id, framework_score, framework_reasoning, framework_refs }) => {
  const l = db.onion_layers.find(x => x.id === id)
  if (l) {
    l.framework_score = framework_score
    l.framework_reasoning = framework_reasoning || ''
    l.framework_refs = framework_refs || []
    l.scored_at = now()
    saveDB()
  }
  return l
})

// Sovereign score — user only, free
ipcMain.handle('onion:updateSovereign', (_, { id, sovereign_score, sovereign_notes }) => {
  const l = db.onion_layers.find(x => x.id === id)
  if (l) {
    l.sovereign_score = Math.min(Math.max(Number(sovereign_score) || 0, 0), 999)
    l.sovereign_notes = sovereign_notes || ''
    saveDB()
  }
  return l
})

// Legacy — kept for backwards compat
ipcMain.handle('onion:update', (_, { id, content, score, notes }) => {
  const l = db.onion_layers.find(x => x.id === id)
  if (l) { l.content = content; l.score = score; l.notes = notes; saveDB() }
  return l
})

// ── Experiments ───────────────────────────────────────────────────────────────
ipcMain.handle('experiments:list', () =>
  [...db.experiments].sort((a, b) => b.created_at - a.created_at))

ipcMain.handle('experiments:create', (_, { name, pyramidAId, pyramidBId, mode }) => {
  const e = { id: uuidv4(), name, pyramid_a_id: pyramidAId, pyramid_b_id: pyramidBId, mode: mode || 'resonance', result_data: null, created_at: now() }
  db.experiments.push(e); saveDB(); return e
})

ipcMain.handle('experiments:saveResult', (_, { id, resultData }) => {
  const e = db.experiments.find(x => x.id === id)
  if (e) { e.result_data = JSON.stringify(resultData); saveDB() }
  return { ok: true }
})

// ── File Export (save dialog) ─────────────────────────────────────────────────
ipcMain.handle('export:save', async (_, { content, defaultName, ext }) => {
  const win = BrowserWindow.getFocusedWindow()
  const { canceled, filePath } = await dialog.showSaveDialog(win, {
    defaultPath: defaultName,
    filters: ext === 'json'
      ? [{ name: 'JSON', extensions: ['json'] }]
      : [{ name: 'Markdown', extensions: ['md'] }],
  })
  if (canceled || !filePath) return { ok: false }
  fs.writeFileSync(filePath, content, 'utf8')
  return { ok: true, filePath }
})

// ── Window ────────────────────────────────────────────────────────────────────
function createWindow() {
  const win = new BrowserWindow({
    width: 1400, height: 900, minWidth: 1000, minHeight: 700,
    backgroundColor: '#0a0a0a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })
  if (isDev) {
    win.loadURL('http://localhost:5173')
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(__dirname, 'dist', 'index.html'))
  }
}

app.whenReady().then(() => {
  loadDB()
  createWindow()
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow() })
})

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
