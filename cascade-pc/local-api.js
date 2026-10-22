// Local read-only API (port 7432). Kept out of main.js so it can be tested without Electron.
// Localhost binding alone does not stop a web page: DNS rebinding points a page's own hostname
// at 127.0.0.1 and reads the reply as same-origin. So the Host header must name this server,
// and a request made by a browser page must come from a local origin.

const PORT = 7432
const ENDPOINTS = ['/status', '/pyramids', '/files', '/blocks', '/layers', '/audit', '/search']
const LOCAL_HOSTS = new Set([`127.0.0.1:${PORT}`, `localhost:${PORT}`])

function isLocalOrigin(origin) {
  try {
    const { protocol, hostname } = new URL(origin)
    return protocol === 'http:' && (hostname === 'localhost' || hostname === '127.0.0.1')
  } catch { return false }
}

function refusal(req) {
  if (req.method !== 'GET') return [405, 'Read-only API: GET only']
  if (!LOCAL_HOSTS.has(req.headers.host || '')) return [403, 'Host must be 127.0.0.1 or localhost']
  const origin = req.headers.origin
  if (origin !== undefined && !isLocalOrigin(origin)) return [403, 'Cross-origin request refused']
  return null
}

function createApiHandler(getDb) {
  return (req, res) => {
    res.setHeader('Content-Type', 'application/json')
    const refused = refusal(req)
    if (refused) {
      res.statusCode = refused[0]
      res.end(JSON.stringify({ error: refused[1] }))
      return
    }
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost')

    const db = getDb()
    const url = new URL(req.url, `http://localhost:${PORT}`)
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
        res.end(JSON.stringify({ error: 'Not found', endpoints: ENDPOINTS }))
      }
    } catch (e) {
      res.statusCode = 500
      res.end(JSON.stringify({ error: e.message }))
    }
  }
}

module.exports = { PORT, ENDPOINTS, createApiHandler }
