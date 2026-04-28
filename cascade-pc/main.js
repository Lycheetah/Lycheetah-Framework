const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const http = require('http')
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

ipcMain.handle('blocks:create', (_, { fileId, pyramidId, title, content, position, frameworkRefs, sourceBlockIds, lineageScore }) => {
  const block = {
    id: uuidv4(), file_id: fileId, pyramid_id: pyramidId,
    title, content: content || '',
    score_aggregate: 0, sovereign_score_aggregate: 0,
    position: position || 0,
    framework_refs: frameworkRefs || ['cascade'],
    created_at: now(),
    // Synthesis lineage
    source_block_ids: sourceBlockIds || null,
    lineage_score: lineageScore || null,
    is_synthesis: !!(sourceBlockIds && sourceBlockIds.length > 0),
  }
  db.blocks.push(block)
  LAYERS.forEach((name, i) => {
    db.onion_layers.push({
      id: uuidv4(), block_id: block.id, layer_index: i, layer_name: name,
      // Framework track — seed AXIOM with lineage score if synthesis
      framework_score: (i === 0 && lineageScore) ? Math.round(lineageScore) : 0,
      framework_reasoning: (i === 0 && lineageScore) ? `Lineage score: earned from ${(sourceBlockIds || []).length} source block(s)` : '',
      framework_refs: [],
      // Sovereign track
      sovereign_score: 0, sovereign_notes: '',
      // Legacy
      content: '', score: 0, notes: '',
    })
  })
  saveDB(); return block
})

ipcMain.handle('blocks:updatePosition', (_, { id, position }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) { b.position = position; b.updated_at = now(); saveDB() }
  return { ok: true }
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

// Block versioning — save a snapshot of title+content
ipcMain.handle('blocks:saveVersion', (_, { id }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) {
    if (!b.versions) b.versions = []
    b.versions.push({ title: b.title, content: b.content, score: b.score_aggregate, ts: now() })
    if (b.versions.length > 20) b.versions = b.versions.slice(-20)
    saveDB()
  }
  return { ok: true }
})

ipcMain.handle('blocks:getVersions', (_, id) => {
  const b = db.blocks.find(x => x.id === id)
  return b?.versions || []
})

// Block tags
ipcMain.handle('blocks:setTags', (_, { id, tags }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) { b.tags = Array.isArray(tags) ? tags : []; b.updated_at = now(); saveDB() }
  return { ok: true }
})

// Block pin/star
ipcMain.handle('blocks:pin', (_, { id, pinned }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) { b.pinned = !!pinned; b.updated_at = now(); saveDB() }
  return { ok: true }
})

// Session audit log — append event
ipcMain.handle('audit:log', (_, { action, blockId, blockTitle, detail }) => {
  if (!db.audit_log) db.audit_log = []
  db.audit_log.push({ ts: now(), action, blockId, blockTitle, detail })
  if (db.audit_log.length > 500) db.audit_log = db.audit_log.slice(-500)
  saveDB()
  return { ok: true }
})

ipcMain.handle('audit:get', () => [...(db.audit_log || [])].reverse().slice(0, 100))

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
ipcMain.handle('onion:updateFramework', (_, { id, framework_score, framework_reasoning, framework_refs, falsifiable, score_audit }) => {
  const l = db.onion_layers.find(x => x.id === id)
  if (l) {
    l.framework_score = framework_score
    l.framework_reasoning = framework_reasoning || ''
    l.framework_refs = framework_refs || []
    l.scored_at = now()
    if (falsifiable !== undefined) l.falsifiable = falsifiable
    if (score_audit !== undefined) l.score_audit = score_audit
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

// ── Import adapter — parse Obsidian/Zotero/Notion formats ────────────────────
function adaptImport(name, content) {
  // Zotero RDF/JSON export — array of items with title, abstractNote
  if (name.endsWith('.json')) {
    try {
      const data = JSON.parse(content)
      const items = Array.isArray(data) ? data : (data.items || [data])
      if (items.length > 0 && (items[0].title || items[0].abstractNote)) {
        const adapted = items.map(item => {
          const title = item.title || item.shortTitle || 'Untitled'
          const body = [item.abstractNote, item.note, item.extra].filter(Boolean).join('\n\n')
          return `# ${title}\n\n${body}`
        }).join('\n\n---\n\n')
        return { name: name.replace('.json', '-zotero.md'), content: adapted }
      }
    } catch {}
  }
  // Obsidian markdown — strip frontmatter YAML, keep the rest
  if (name.endsWith('.md') || name.endsWith('.markdown')) {
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n/)
    if (frontmatterMatch) {
      const cleaned = content.slice(frontmatterMatch[0].length)
      return { name, content: cleaned }
    }
  }
  return { name, content }
}

// ── File Import (open dialog) ─────────────────────────────────────────────────
ipcMain.handle('files:openDialog', async () => {
  const win = BrowserWindow.getFocusedWindow()
  const { canceled, filePaths } = await dialog.showOpenDialog(win, {
    title: 'Import files into CASCADE',
    properties: ['openFile', 'multiSelections'],
    filters: [{ name: 'Text & Export files', extensions: ['txt', 'md', 'markdown', 'json', 'csv', 'bib'] }],
  })
  if (canceled || !filePaths.length) return { files: [] }
  const result = filePaths.map(fp => {
    const raw = fs.readFileSync(fp, 'utf8')
    const adapted = adaptImport(path.basename(fp), raw)
    return { name: adapted.name, content: adapted.content, size: Buffer.byteLength(adapted.content, 'utf8') }
  })
  return { files: result }
})

// ── File Export (save dialog) ─────────────────────────────────────────────────
ipcMain.handle('export:save', async (_, { content, defaultName, ext }) => {
  const win = BrowserWindow.getFocusedWindow()
  const filterMap = {
    json:    [{ name: 'JSON', extensions: ['json'] }],
    md:      [{ name: 'Markdown', extensions: ['md'] }],
    cascade: [{ name: 'CASCADE Pyramid', extensions: ['cascade'] }],
    html:    [{ name: 'HTML', extensions: ['html'] }],
  }
  const { canceled, filePath } = await dialog.showSaveDialog(win, {
    defaultPath: defaultName,
    filters: filterMap[ext] || [{ name: 'All Files', extensions: ['*'] }],
  })
  if (canceled || !filePath) return { ok: false }
  fs.writeFileSync(filePath, content, 'utf8')
  return { ok: true, filePath }
})

// ── Full data export (entire DB dump) ────────────────────────────────────────
ipcMain.handle('export:fullDump', async () => {
  const win = BrowserWindow.getFocusedWindow()
  const { canceled, filePath } = await dialog.showSaveDialog(win, {
    defaultPath: `cascade_full_export_${new Date().toISOString().slice(0,10)}.json`,
    filters: [{ name: 'JSON', extensions: ['json'] }],
  })
  if (canceled || !filePath) return { ok: false }
  const dump = {
    exported_at: new Date().toISOString(),
    cascade_version: '0.3.0',
    pyramids: db.pyramids,
    files: db.files,
    blocks: db.blocks,
    onion_layers: db.onion_layers,
  }
  fs.writeFileSync(filePath, JSON.stringify(dump, null, 2), 'utf8')
  return { ok: true, filePath }
})

// ── Score history append ──────────────────────────────────────────────────────
ipcMain.handle('blocks:appendHistory', (_, { id, score, ts }) => {
  const b = db.blocks.find(x => x.id === id)
  if (b) {
    if (!b.score_history) b.score_history = []
    b.score_history.push({ score, ts: ts || now() })
    if (b.score_history.length > 50) b.score_history = b.score_history.slice(-50)
    saveDB()
  }
  return { ok: true }
})

// ── Local API server (port 7432) — optional plugin/scripting hook ─────────────
// Exposes read-only endpoints. No auth needed — localhost only, no write ops.
let apiServer = null

function startApiServer() {
  if (apiServer) return
  apiServer = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json')
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost')

    const url = new URL(req.url, 'http://localhost:7432')
    const p = url.pathname

    try {
      if (p === '/status') {
        res.end(JSON.stringify({ ok: true, version: '0.3.0', pyramids: db.pyramids.length, blocks: db.blocks.length }))
      } else if (p === '/pyramids') {
        res.end(JSON.stringify(db.pyramids))
      } else if (p === '/files') {
        const pyramidId = url.searchParams.get('pyramidId')
        res.end(JSON.stringify(pyramidId ? db.files.filter(f => f.pyramid_id === pyramidId) : db.files))
      } else if (p === '/blocks') {
        const fileId = url.searchParams.get('fileId')
        const pyramidId = url.searchParams.get('pyramidId')
        let blocks = db.blocks
        if (fileId) blocks = blocks.filter(b => b.file_id === fileId)
        else if (pyramidId) {
          const fileIds = db.files.filter(f => f.pyramid_id === pyramidId).map(f => f.id)
          blocks = blocks.filter(b => fileIds.includes(b.file_id))
        }
        res.end(JSON.stringify(blocks))
      } else if (p === '/layers') {
        const blockId = url.searchParams.get('blockId')
        if (!blockId) { res.statusCode = 400; res.end(JSON.stringify({ error: 'blockId required' })); return }
        res.end(JSON.stringify(db.onion_layers.filter(l => l.block_id === blockId).sort((a, b) => a.layer_index - b.layer_index)))
      } else if (p === '/audit') {
        res.end(JSON.stringify([...(db.audit_log || [])].reverse().slice(0, 100)))
      } else if (p === '/search') {
        const q = (url.searchParams.get('q') || '').toLowerCase()
        if (!q) { res.end(JSON.stringify([])); return }
        const hits = db.blocks.filter(b =>
          b.title?.toLowerCase().includes(q) || b.content?.toLowerCase().includes(q)
        ).slice(0, 50)
        res.end(JSON.stringify(hits))
      } else {
        res.statusCode = 404
        res.end(JSON.stringify({ error: 'Not found', endpoints: ['/status', '/pyramids', '/files', '/blocks', '/layers', '/audit', '/search'] }))
      }
    } catch (e) {
      res.statusCode = 500
      res.end(JSON.stringify({ error: e.message }))
    }
  })

  apiServer.on('error', (e) => {
    if (e.code !== 'EADDRINUSE') console.error('API server error:', e)
  })

  apiServer.listen(7432, '127.0.0.1', () => {
    console.log('CASCADE local API running at http://127.0.0.1:7432')
  })
}

ipcMain.handle('api:status', () => ({
  running: apiServer?.listening || false,
  port: 7432,
  endpoints: ['/status', '/pyramids', '/files', '/blocks', '/layers', '/audit', '/search'],
}))

ipcMain.handle('api:start', () => { startApiServer(); return { ok: true } })
ipcMain.handle('api:stop', () => {
  if (apiServer) { apiServer.close(); apiServer = null }
  return { ok: true }
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
  startApiServer()
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow() })
})

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit() })
