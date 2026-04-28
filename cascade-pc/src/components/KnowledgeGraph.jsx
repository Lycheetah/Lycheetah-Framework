import React, { useEffect, useRef, useState, useCallback } from 'react'
import { getScoreBand } from '../scoring/cascade'
import './KnowledgeGraph.css'

// ── Constants ────────────────────────────────────────────────────────────────
const REPULSION  = 16000
const ATTRACTION = 0.022
const DAMPING    = 0.80
const ITERS      = 380
const FOCAL_BASE = 540
const AUTO_SPEED = 0.0016
const INTRO_FRAMES = 70
const GRID_SIZE  = 320
const GRID_STEP  = 80
const GRID_Y     = 230   // depth of reference grid plane

// ── Graph builder ─────────────────────────────────────────────────────────────
function buildGraph(allBlocks) {
  const nodes = allBlocks.filter(b => b.score_aggregate > 0).map(b => {
    const theta = Math.random() * Math.PI * 2
    const phi   = Math.acos(2 * Math.random() - 1)
    const r     = 160 + Math.random() * 130
    return {
      id: b.id, title: b.title, score: b.score_aggregate,
      content: b.content || '', framework_refs: b.framework_refs || [],
      is_synthesis: !!b.is_synthesis,
      source_ids: b.source_block_ids || [],
      x: r * Math.sin(phi) * Math.cos(theta),
      y: r * Math.sin(phi) * Math.sin(theta),
      z: r * Math.cos(phi),
      vx: 0, vy: 0, vz: 0,
    }
  })
  const edges = []
  const nm = Object.fromEntries(nodes.map(n => [n.id, n]))
  nodes.forEach(n => {
    if (n.is_synthesis) n.source_ids.forEach(sid => {
      if (nm[sid]) edges.push({ source: n.id, target: sid, type: 'lineage' })
    })
  })
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j]
      const delta = Math.abs(a.score - b.score)
      const linked = edges.some(e =>
        (e.source===a.id&&e.target===b.id)||(e.source===b.id&&e.target===a.id))
      if (!linked) {
        if (delta <= 15)   edges.push({ source: a.id, target: b.id, type: 'resonance', delta })
        else if (delta>30) edges.push({ source: a.id, target: b.id, type: 'tension',   delta })
      }
    }
  }
  const connCount = {}
  edges.forEach(e => {
    connCount[e.source] = (connCount[e.source]||0) + 1
    connCount[e.target] = (connCount[e.target]||0) + 1
  })
  nodes.forEach(n => { n.connections = connCount[n.id] || 0 })
  return { nodes, edges }
}

function runLayout(nodes, edges) {
  const ns = nodes.map(n => ({ ...n }))
  const nm = Object.fromEntries(ns.map(n => [n.id, n]))
  for (let iter = 0; iter < ITERS; iter++) {
    ns.forEach(n => { n.fx=0; n.fy=0; n.fz=0 })
    for (let i = 0; i < ns.length; i++) {
      for (let j = i+1; j < ns.length; j++) {
        const a=ns[i], b=ns[j]
        const dx=a.x-b.x, dy=a.y-b.y, dz=a.z-b.z
        const dist=Math.sqrt(dx*dx+dy*dy+dz*dz)||1
        const f=REPULSION/(dist*dist)
        const fx=dx/dist*f, fy=dy/dist*f, fz=dz/dist*f
        a.fx+=fx; a.fy+=fy; a.fz+=fz
        b.fx-=fx; b.fy-=fy; b.fz-=fz
      }
    }
    edges.forEach(e => {
      const a=nm[e.source], b=nm[e.target]
      if (!a||!b) return
      const dx=b.x-a.x, dy=b.y-a.y, dz=b.z-a.z
      const dist=Math.sqrt(dx*dx+dy*dy+dz*dz)||1
      const f=dist*ATTRACTION
      const fx=dx/dist*f, fy=dy/dist*f, fz=dz/dist*f
      a.fx+=fx; a.fy+=fy; a.fz+=fz
      b.fx-=fx; b.fy-=fy; b.fz-=fz
    })
    ns.forEach(n => {
      n.vx=(n.vx+n.fx)*DAMPING; n.vy=(n.vy+n.fy)*DAMPING; n.vz=(n.vz+n.fz)*DAMPING
      n.x+=n.vx; n.y+=n.vy; n.z+=n.vz
    })
  }
  return ns
}

// ── 3D math ───────────────────────────────────────────────────────────────────
const rotY = (x,y,z,a) => { const c=Math.cos(a),s=Math.sin(a); return [x*c+z*s,y,-x*s+z*c] }
const rotX = (x,y,z,a) => { const c=Math.cos(a),s=Math.sin(a); return [x,y*c-z*s,y*s+z*c] }

function project(x, y, z, rx, ry, focal, cx, cy) {
  let [px,py,pz] = rotY(x,y,z,ry); [px,py,pz] = rotX(px,py,pz,rx)
  const sc = focal / (focal + pz + 380)
  return [cx + px*sc, cy + py*sc, pz, sc]
}

// ── Node colour ───────────────────────────────────────────────────────────────
function nodeCol(score, is_synthesis) {
  if (is_synthesis) return { core:'#d4af37', glow:'#b8962c', rgb:'212,168,55' }
  if (score>=80) return { core:'#4ade80', glow:'#22c55e', rgb:'74,222,128' }
  if (score>=65) return { core:'#a3e635', glow:'#84cc16', rgb:'163,230,53' }
  if (score>=50) return { core:'#facc15', glow:'#ca8a04', rgb:'250,204,21' }
  if (score>=35) return { core:'#fb923c', glow:'#ea580c', rgb:'251,146,60' }
  return               { core:'#f87171', glow:'#dc2626', rgb:'248,113,113' }
}

// ── Static star field ─────────────────────────────────────────────────────────
const STARS = Array.from({length:340}, () => ({
  x:Math.random(), y:Math.random(),
  r:0.3+Math.random()*1.4,
  op:0.1+Math.random()*0.44,
  phase:Math.random()*Math.PI*2,
  speed:0.008+Math.random()*0.022,
}))

// ── Component ─────────────────────────────────────────────────────────────────
export default function KnowledgeGraph({ files, onSelectBlock }) {
  const canvasRef    = useRef(null)
  const nodesRef     = useRef([])
  const edgesRef     = useRef([])
  const camRef       = useRef({ rx:0.28, ry:0.0, zoom:1.0 })
  const dragRef      = useRef(null)       // { x, y, rx, ry } or null
  const touchRef     = useRef(null)       // touch state
  const hovRef       = useRef(null)
  const selRef       = useRef(null)
  const animRef      = useRef(null)
  const tickRef      = useRef(0)
  const introRef     = useRef(0)
  const particlesRef = useRef([])

  const [ready,      setReady]      = useState(false)
  const [loading,    setLoading]    = useState(true)
  const [dragging,   setDragging]   = useState(false)
  const [autoRot,    setAutoRot]    = useState(true)
  const [selected,   setSelected]   = useState(null)
  const [stats,      setStats]      = useState({ nodes:0, lineage:0, resonance:0, tension:0 })
  const [showEdge,   setShowEdge]   = useState({ lineage:true, resonance:true, tension:true })
  const [scoreFloor, setScoreFloor] = useState(0)

  const autoRotRef    = useRef(true)
  const showEdgeRef   = useRef({ lineage:true, resonance:true, tension:true })
  const scoreFloorRef = useRef(0)
  const selectedRef   = useRef(null)

  useEffect(() => { autoRotRef.current    = autoRot  },  [autoRot])
  useEffect(() => { showEdgeRef.current   = showEdge },  [showEdge])
  useEffect(() => { scoreFloorRef.current = scoreFloor },[scoreFloor])
  useEffect(() => { selectedRef.current   = selected },  [selected])

  useEffect(() => {
    if (!files || files.length === 0) return
    buildAndLayout()
  }, [files])

  // Escape key — close detail panel
  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') { selRef.current=null; setSelected(null) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  async function buildAndLayout() {
    setLoading(true); setReady(false); setSelected(null); selRef.current=null
    let all = []
    for (const f of files) {
      const blocks = await window.cascade.blocks.list(f.id)
      all = all.concat(blocks)
    }
    const { nodes, edges } = buildGraph(all)
    if (nodes.length === 0) { setLoading(false); return }
    nodesRef.current = runLayout(nodes, edges)
    edgesRef.current = edges
    // Seed particle trails on lineage edges (5 particles each)
    const lineageIdxs = edges.map((e,i)=>i).filter(i=>edges[i].type==='lineage')
    particlesRef.current = lineageIdxs.flatMap(i =>
      Array.from({length:5}, (_,k) => ({
        edgeIdx: i, t: k/5,
        speed: 0.0025 + Math.random()*0.003,
        trail: [],
      }))
    )
    introRef.current = 0
    setStats({
      nodes:    nodes.length,
      lineage:  edges.filter(e=>e.type==='lineage').length,
      resonance:edges.filter(e=>e.type==='resonance').length,
      tension:  edges.filter(e=>e.type==='tension').length,
    })
    setLoading(false); setReady(true)
  }

  // ── Screenshot ───────────────────────────────────────────────────────────────
  function screenshot() {
    const canvas = canvasRef.current
    if (!canvas) return
    const url  = canvas.toDataURL('image/png')
    const link = document.createElement('a')
    link.href  = url
    link.download = `knowledge-graph-${Date.now()}.png`
    link.click()
  }

  // ── Render loop ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!ready) return
    const canvas = canvasRef.current
    if (!canvas) return
    const W = canvas.width, H = canvas.height
    const ctx = canvas.getContext('2d')

    function frame() {
      tickRef.current++
      const tick = tickRef.current
      if (introRef.current < INTRO_FRAMES) introRef.current++

      if (autoRotRef.current && !dragRef.current) {
        camRef.current.ry += AUTO_SPEED
        // Gentle camera bob — feels like drifting through space
        camRef.current.rx = 0.28 + 0.055 * Math.sin(tick * 0.0055)
      }

      const { rx, ry, zoom } = camRef.current
      const focal = FOCAL_BASE * zoom
      const cx = W/2, cy = H/2
      const introScale = Math.min(1, (introRef.current / INTRO_FRAMES) ** 0.6)

      ctx.clearRect(0, 0, W, H)

      // ── Deep space background
      const bg = ctx.createRadialGradient(cx, cy*0.85, 0, cx, cy, W*0.72)
      bg.addColorStop(0,   '#080c1c')
      bg.addColorStop(0.45,'#040610')
      bg.addColorStop(1,   '#020307')
      ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H)

      // Nebula blobs
      ;[[cx*0.75, cy*0.65, W*0.38, '90,40,180,0.07'], [cx*1.35, cy*1.25, W*0.28, '20,80,160,0.05']].forEach(([nx,ny,nr,c]) => {
        const neb = ctx.createRadialGradient(nx,ny,0,nx,ny,nr)
        neb.addColorStop(0,   `rgba(${c})`)
        neb.addColorStop(1,   'transparent')
        ctx.fillStyle = neb; ctx.fillRect(0, 0, W, H)
      })

      // ── Star field
      STARS.forEach(s => {
        const t = 0.62 + 0.38 * Math.sin(tick * s.speed + s.phase)
        ctx.beginPath(); ctx.arc(s.x*W, s.y*H, s.r, 0, Math.PI*2)
        ctx.fillStyle = `rgba(210,225,255,${s.op * t})`; ctx.fill()
      })

      // ── Reference grid plane (EVE-style depth floor)
      ctx.save()
      for (let i = -GRID_SIZE; i <= GRID_SIZE; i += GRID_STEP) {
        // Lines along Z axis
        const [sx1,sy1,sz1] = project(-GRID_SIZE, GRID_Y, i, rx,ry,focal,cx,cy)
        const [sx2,sy2,sz2] = project( GRID_SIZE, GRID_Y, i, rx,ry,focal,cx,cy)
        const op1 = Math.max(0.01, 0.09 - sz1/2200)
        ctx.strokeStyle = `rgba(80,110,200,${op1})`
        ctx.lineWidth = 0.5
        ctx.beginPath(); ctx.moveTo(sx1,sy1); ctx.lineTo(sx2,sy2); ctx.stroke()
        // Lines along X axis
        const [sx3,sy3,sz3] = project(i, GRID_Y, -GRID_SIZE, rx,ry,focal,cx,cy)
        const [sx4,sy4,sz4] = project(i, GRID_Y,  GRID_SIZE, rx,ry,focal,cx,cy)
        const op2 = Math.max(0.01, 0.09 - sz3/2200)
        ctx.strokeStyle = `rgba(80,110,200,${op2})`
        ctx.beginPath(); ctx.moveTo(sx3,sy3); ctx.lineTo(sx4,sy4); ctx.stroke()
      }
      ctx.restore()

      const ns = nodesRef.current
      const es = edgesRef.current
      if (!ns.length) { animRef.current = requestAnimationFrame(frame); return }

      const floor = scoreFloorRef.current
      const show  = showEdgeRef.current
      const visIds = new Set(floor > 0 ? ns.filter(n=>n.score>=floor).map(n=>n.id) : ns.map(n=>n.id))

      // ── Project all visible nodes
      const proj = ns
        .filter(n => visIds.has(n.id))
        .map(n => {
          const [sx,sy,sz,sc] = project(n.x, n.y, n.z, rx, ry, focal, cx, cy)
          return { ...n, sx, sy, sz, sc: sc * introScale }
        })
      const pm = Object.fromEntries(proj.map(p=>[p.id,p]))

      // ── Edges
      const visEdges = es.filter(e => show[e.type] && visIds.has(e.source) && visIds.has(e.target))
      ;[...visEdges]
        .sort((a,b) => ((pm[b.source]?.sz||0)+(pm[b.target]?.sz||0)) - ((pm[a.source]?.sz||0)+(pm[a.target]?.sz||0)))
        .forEach(e => {
          const a=pm[e.source], b=pm[e.target]
          if (!a||!b) return
          const avgZ = (a.sz+b.sz)/2
          const dop = Math.max(0.03, Math.min(0.72, 0.52 - avgZ/1100))
          let color, lw, dash
          if (e.type==='lineage')    { color=`rgba(212,168,55,${dop+0.28})`; lw=1.7; dash=[] }
          else if(e.type==='resonance'){ color=`rgba(74,222,128,${dop})`; lw=0.8; dash=[] }
          else                       { color=`rgba(248,113,113,${dop})`; lw=0.8; dash=[4,4] }
          ctx.save()
          ctx.shadowBlur=e.type==='lineage'?10:4; ctx.shadowColor=color
          ctx.strokeStyle=color; ctx.lineWidth=lw; ctx.setLineDash(dash)
          ctx.beginPath(); ctx.moveTo(a.sx,a.sy); ctx.lineTo(b.sx,b.sy); ctx.stroke()
          ctx.restore()
        })

      // ── Particle trails on lineage edges
      if (show.lineage) {
        particlesRef.current.forEach(p => {
          p.t = (p.t + p.speed) % 1
          const e = es[p.edgeIdx]
          if (!e || !visIds.has(e.source) || !visIds.has(e.target)) return
          const a=pm[e.source], b=pm[e.target]
          if (!a||!b) return
          // Store trail history
          const x = a.sx + (b.sx-a.sx)*p.t
          const y = a.sy + (b.sy-a.sy)*p.t
          p.trail.unshift({x,y})
          if (p.trail.length > 8) p.trail.pop()
          const avgZ=(a.sz+b.sz)/2
          const dop=Math.max(0.15,Math.min(0.9,0.72-avgZ/1100))
          // Draw trail
          p.trail.forEach((pt, i) => {
            const fade = (1 - i/p.trail.length) * dop
            ctx.save()
            ctx.shadowBlur = 6; ctx.shadowColor=`rgba(255,210,80,${fade})`
            ctx.beginPath(); ctx.arc(pt.x, pt.y, Math.max(0.5, 2-i*0.2), 0, Math.PI*2)
            ctx.fillStyle = `rgba(255,220,100,${fade})`; ctx.fill()
            ctx.restore()
          })
        })
      }

      // ── Nodes (back to front)
      ;[...proj].sort((a,b)=>b.sz-a.sz).forEach(n => {
        const isHov = hovRef.current===n.id
        const isSel = selRef.current?.id===n.id
        const pulse = (isHov||isSel) ? 1+0.2*Math.sin(tick*0.1) : 1+0.03*Math.sin(tick*0.04+n.sx)
        const baseR = Math.max(3, Math.min(22, 2+n.score/6.5+Math.min(n.connections,6)*0.6)) * n.sc * pulse
        const depthFade = Math.max(0.28, Math.min(1, 1-n.sz/980))
        const { core, glow, rgb } = nodeCol(n.score, n.is_synthesis)

        ctx.save()
        ctx.globalAlpha = depthFade

        // Outer halo
        const hR = baseR * ((isHov||isSel) ? 4.4 : 3.1)
        const halo = ctx.createRadialGradient(n.sx,n.sy,0,n.sx,n.sy,hR)
        halo.addColorStop(0,  `rgba(${rgb},0.72)`)
        halo.addColorStop(0.2,`rgba(${rgb},0.28)`)
        halo.addColorStop(0.6,`rgba(${rgb},0.07)`)
        halo.addColorStop(1,  'transparent')
        ctx.fillStyle=halo; ctx.beginPath(); ctx.arc(n.sx,n.sy,hR,0,Math.PI*2); ctx.fill()

        // Core disc
        ctx.shadowBlur=(isHov||isSel)?32:18; ctx.shadowColor=core
        ctx.beginPath(); ctx.arc(n.sx,n.sy,baseR,0,Math.PI*2)
        ctx.fillStyle=core; ctx.fill()

        // Specular highlight
        const sp = ctx.createRadialGradient(n.sx-baseR*0.28,n.sy-baseR*0.28,0,n.sx,n.sy,baseR)
        sp.addColorStop(0,'rgba(255,255,255,0.62)'); sp.addColorStop(0.55,'rgba(255,255,255,0.08)'); sp.addColorStop(1,'transparent')
        ctx.fillStyle=sp; ctx.beginPath(); ctx.arc(n.sx,n.sy,baseR,0,Math.PI*2); ctx.fill()

        // Selection ring
        if (isSel) {
          ctx.strokeStyle=core; ctx.lineWidth=1.5; ctx.setLineDash([])
          ctx.shadowBlur=16; ctx.shadowColor=core
          ctx.beginPath(); ctx.arc(n.sx,n.sy,baseR+6*n.sc,0,Math.PI*2); ctx.stroke()
        }

        // Synthesis orbit ring
        if (n.is_synthesis) {
          ctx.strokeStyle=`rgba(212,168,55,${0.52*depthFade})`
          ctx.lineWidth=1; ctx.setLineDash([2,3])
          ctx.shadowBlur=7; ctx.shadowColor='#d4af37'
          ctx.beginPath(); ctx.arc(n.sx,n.sy,baseR+5*n.sc,0,Math.PI*2); ctx.stroke()
        }

        // Lens flare for synthesis or score≥78
        if ((n.is_synthesis||n.score>=78) && n.sc>0.5) {
          const fo = ((isHov||isSel)?0.45:0.22)*depthFade
          ctx.globalAlpha = depthFade * fo
          ;[-1,1].forEach(() => {
            const fl = ctx.createLinearGradient(n.sx-baseR*3,n.sy,n.sx+baseR*3,n.sy)
            fl.addColorStop(0,'transparent'); fl.addColorStop(0.5,`rgba(${rgb},1)`); fl.addColorStop(1,'transparent')
            ctx.fillStyle=fl; ctx.fillRect(n.sx-baseR*3,n.sy-1,baseR*6,2)
          })
          ctx.globalAlpha = depthFade
        }

        ctx.restore()

        // Label
        if (isHov||isSel||(n.score>=66&&n.sc>0.6)) {
          ctx.save()
          ctx.globalAlpha = depthFade * ((isHov||isSel)?1:0.68)
          const label = n.title.slice(0,26)+(n.title.length>26?'…':'')
          const fs = (isHov||isSel)?11:9
          ctx.font=`${(isHov||isSel)?'bold ':''}${fs}px 'Courier New',monospace`
          const tw = ctx.measureText(label).width
          const lx = n.sx-tw/2-4, ly = n.sy+baseR+6
          // Pill background
          ctx.fillStyle='rgba(3,6,20,0.78)'
          ctx.beginPath()
          if (ctx.roundRect) ctx.roundRect(lx, ly, tw+8, 15, 3)
          else { ctx.rect(lx, ly, tw+8, 15) }
          ctx.fill()
          ctx.textAlign='center'; ctx.shadowBlur=(isHov||isSel)?9:0; ctx.shadowColor=core
          ctx.fillStyle=(isHov||isSel)?core:'#9ca3af'
          ctx.fillText(label, n.sx, ly+11)
          if (isHov||isSel) {
            ctx.font='bold 13px monospace'; ctx.fillStyle=core; ctx.shadowBlur=14
            ctx.fillText(String(n.score), n.sx, n.sy+2)
          }
          ctx.restore()
        }
      })

      // ── Score colour legend (canvas overlay, top-left)
      const legend = [
        ['≥80', '#4ade80'], ['≥65', '#a3e635'], ['≥50', '#facc15'],
        ['≥35', '#fb923c'], ['<35', '#f87171'], ['◎',   '#d4af37'],
      ]
      ctx.save()
      ctx.globalAlpha = 0.55
      legend.forEach(([label, color], i) => {
        const lx=14, ly=14+i*17
        ctx.fillStyle=color; ctx.shadowBlur=4; ctx.shadowColor=color
        ctx.beginPath(); ctx.arc(lx+4, ly+4, 4, 0, Math.PI*2); ctx.fill()
        ctx.font='9px monospace'; ctx.fillStyle='#888'; ctx.shadowBlur=0
        ctx.textAlign='left'; ctx.fillText(label, lx+13, ly+8)
      })
      ctx.restore()

      animRef.current = requestAnimationFrame(frame)
    }

    animRef.current = requestAnimationFrame(frame)
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current) }
  }, [ready])

  // ── Hit test ──────────────────────────────────────────────────────────────────
  function hitTest(clientX, clientY) {
    const canvas = canvasRef.current
    if (!canvas) return null
    const rect = canvas.getBoundingClientRect()
    const mx = (clientX-rect.left) * (canvas.width/rect.width)
    const my = (clientY-rect.top)  * (canvas.height/rect.height)
    const { rx, ry, zoom } = camRef.current
    const focal = FOCAL_BASE * zoom
    const cx=canvas.width/2, cy=canvas.height/2
    const floor = scoreFloorRef.current
    let best=null, bestD=28
    nodesRef.current.forEach(n => {
      if (floor>0 && n.score<floor) return
      const [sx,sy] = project(n.x,n.y,n.z, rx,ry,focal,cx,cy)
      const d = Math.hypot(sx-mx, sy-my)
      if (d<bestD) { best=n; bestD=d }
    })
    return best
  }

  // ── Mouse handlers ────────────────────────────────────────────────────────────
  const onMouseDown = useCallback(e => {
    dragRef.current = { x:e.clientX, y:e.clientY, rx:camRef.current.rx, ry:camRef.current.ry }
    setDragging(true)
  }, [])

  const onMouseMove = useCallback(e => {
    if (dragRef.current) {
      camRef.current.ry = dragRef.current.ry + (e.clientX-dragRef.current.x)*0.007
      camRef.current.rx = dragRef.current.rx + (e.clientY-dragRef.current.y)*0.007
      return
    }
    hovRef.current = hitTest(e.clientX, e.clientY)?.id || null
  }, [])

  const onMouseUp   = useCallback(() => { dragRef.current=null; setDragging(false) }, [])
  const onWheel     = useCallback(e => {
    e.preventDefault()
    camRef.current.zoom = Math.max(0.25, Math.min(4, camRef.current.zoom*(1-e.deltaY*0.001)))
  }, [])
  const onClick     = useCallback(e => {
    if (dragRef.current) return
    const n = hitTest(e.clientX, e.clientY)
    if (n) { selRef.current=n; setSelected(n) }
    else   { selRef.current=null; setSelected(null) }
  }, [])

  // ── Touch handlers ────────────────────────────────────────────────────────────
  const onTouchStart = useCallback(e => {
    if (e.touches.length===1) {
      const t = e.touches[0]
      touchRef.current = { x:t.clientX, y:t.clientY, rx:camRef.current.rx, ry:camRef.current.ry, pinchDist:null }
    } else if (e.touches.length===2) {
      const dx=e.touches[0].clientX-e.touches[1].clientX
      const dy=e.touches[0].clientY-e.touches[1].clientY
      touchRef.current = { ...touchRef.current, pinchDist:Math.hypot(dx,dy), zoom:camRef.current.zoom }
    }
  }, [])

  const onTouchMove = useCallback(e => {
    e.preventDefault()
    if (!touchRef.current) return
    if (e.touches.length===1) {
      const t=e.touches[0]
      camRef.current.ry = touchRef.current.ry + (t.clientX-touchRef.current.x)*0.007
      camRef.current.rx = touchRef.current.rx + (t.clientY-touchRef.current.y)*0.007
    } else if (e.touches.length===2 && touchRef.current.pinchDist) {
      const dx=e.touches[0].clientX-e.touches[1].clientX
      const dy=e.touches[0].clientY-e.touches[1].clientY
      const dist = Math.hypot(dx,dy)
      const scale = dist/touchRef.current.pinchDist
      camRef.current.zoom = Math.max(0.25, Math.min(4, touchRef.current.zoom*scale))
    }
  }, [])

  const onTouchEnd = useCallback(() => { touchRef.current=null }, [])

  function resetCamera() { camRef.current = { rx:0.28, ry:0, zoom:1.0 } }

  // ── Connections for detail panel ──────────────────────────────────────────────
  function getConnections(nodeId) {
    const nm = Object.fromEntries(nodesRef.current.map(n=>[n.id,n]))
    return edgesRef.current
      .filter(e=>e.source===nodeId||e.target===nodeId)
      .map(e => ({ type:e.type, delta:e.delta, node:nm[e.source===nodeId?e.target:e.source] }))
      .filter(c=>c.node)
  }

  return (
    <div className="kg-root">
      {/* ── Header ── */}
      <div className="kg-header">
        <span className="kg-title">◈ KNOWLEDGE GRAPH · 3D</span>
        <span className="kg-legend">
          <span className="kg-leg"><span style={{color:'#d4af37'}}>●</span>lineage</span>
          <span className="kg-leg"><span style={{color:'#4ade80'}}>●</span>resonance</span>
          <span className="kg-leg"><span style={{color:'#f87171'}}>●</span>tension</span>
        </span>
        <span className="kg-hint">drag · scroll · click</span>

        <div className="kg-controls">
          {['lineage','resonance','tension'].map(t => (
            <button key={t}
              className={`kg-toggle ${showEdge[t]?'on':'off'}`}
              style={{'--tog-color': t==='lineage'?'#d4af37':t==='resonance'?'#4ade80':'#f87171'}}
              onClick={() => setShowEdge(v=>({...v,[t]:!v[t]}))}>
              {t}
            </button>
          ))}
          <select className="kg-select" value={scoreFloor} onChange={e=>setScoreFloor(Number(e.target.value))}>
            <option value={0}>all scores</option>
            <option value={30}>≥ 30</option>
            <option value={50}>≥ 50</option>
            <option value={65}>≥ 65</option>
            <option value={80}>≥ 80</option>
          </select>
          <button className={`kg-toggle ${autoRot?'on':'off'}`} style={{'--tog-color':'#a78bfa'}}
            onClick={()=>setAutoRot(v=>!v)}>↻ rotate</button>
          <button className="btn kg-btn" onClick={resetCamera}>⊙ reset</button>
          <button className="btn kg-btn" onClick={screenshot} title="Save as PNG">↑ PNG</button>
          <button className="btn kg-btn" onClick={buildAndLayout}>↻ rebuild</button>
        </div>
      </div>

      {/* ── Main area ── */}
      <div className="kg-body">
        {loading ? (
          <div className="kg-empty">Building 3D graph…</div>
        ) : !ready ? (
          <div className="kg-empty">Score some blocks to see the graph.</div>
        ) : (
          <>
            <canvas
              ref={canvasRef}
              width={1200} height={660}
              className="kg-canvas"
              style={{ cursor: dragging?'grabbing':'grab' }}
              onMouseDown={onMouseDown}
              onMouseMove={onMouseMove}
              onMouseUp={onMouseUp}
              onMouseLeave={onMouseUp}
              onWheel={onWheel}
              onClick={onClick}
              onTouchStart={onTouchStart}
              onTouchMove={onTouchMove}
              onTouchEnd={onTouchEnd}
            />

            {/* Stats bar */}
            <div className="kg-stats">
              <span>{stats.nodes} nodes</span>
              <span style={{color:'#d4af37'}}>◈ {stats.lineage} lineage</span>
              <span style={{color:'#4ade80'}}>~ {stats.resonance} resonance</span>
              <span style={{color:'#f87171'}}>⊗ {stats.tension} tension</span>
              <span className="kg-stats-hint">Esc to deselect</span>
            </div>

            {/* ── Detail panel ── */}
            {selected && (() => {
              const band = getScoreBand(selected.score)
              const conns = getConnections(selected.id)
              const lin = conns.filter(c=>c.type==='lineage')
              const res = conns.filter(c=>c.type==='resonance')
              const ten = conns.filter(c=>c.type==='tension')
              const { core } = nodeCol(selected.score, selected.is_synthesis)
              return (
                <div className="kg-detail" style={{'--node-color': core}}>
                  <div className="kg-detail-header">
                    <div>
                      <div className="kg-detail-score" style={{color:core}}>{selected.score}</div>
                      <div className="kg-detail-band" style={{color:core}}>{band.label}</div>
                    </div>
                    {selected.is_synthesis && <span className="kg-synth-badge">◎ synthesis</span>}
                    <button className="kg-detail-close" onClick={()=>{selRef.current=null;setSelected(null)}}>✕</button>
                  </div>

                  <div className="kg-detail-title">{selected.title}</div>

                  {selected.content && (
                    <div className="kg-detail-content">
                      {selected.content.slice(0,220)}{selected.content.length>220?'…':''}
                    </div>
                  )}

                  {selected.framework_refs?.length>0 && (
                    <div className="kg-detail-refs">
                      {selected.framework_refs.map(r=>(
                        <span key={r} className="kg-ref-badge">{r.toUpperCase()}</span>
                      ))}
                    </div>
                  )}

                  {(lin.length>0||res.length>0||ten.length>0) && (
                    <div className="kg-detail-conns">
                      {[{list:lin, color:'#d4af37', icon:'◈', label:'lineage'},
                        {list:res, color:'#4ade80', icon:'~', label:'resonance'},
                        {list:ten, color:'#f87171', icon:'⊗', label:'tension'}]
                        .filter(g=>g.list.length>0)
                        .map(g => (
                          <div key={g.label} className="kg-conn-group">
                            <div className="kg-conn-label" style={{color:g.color}}>
                              {g.icon} {g.label} ({g.list.length})
                            </div>
                            {g.list.slice(0,4).map((c,i)=>(
                              <div key={i} className="kg-conn-item">
                                <span className="kg-conn-score" style={{color:nodeCol(c.node.score,c.node.is_synthesis).core}}>
                                  {c.node.score}
                                </span>
                                <span className="kg-conn-name">{c.node.title.slice(0,30)}</span>
                                {c.delta!=null && <span className="kg-conn-delta">Δ{c.delta}</span>}
                              </div>
                            ))}
                          </div>
                        ))
                      }
                    </div>
                  )}

                  {onSelectBlock && (
                    <button className="kg-goto-btn"
                      style={{'--node-color': core}}
                      onClick={()=>{onSelectBlock(selected.id);selRef.current=null;setSelected(null)}}>
                      → Go to block
                    </button>
                  )}
                </div>
              )
            })()}
          </>
        )}
      </div>
    </div>
  )
}
