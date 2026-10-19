from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from sovereignty_surface import make_corpus
root=Path(__file__).resolve().parent
payload={}
for label,(a,b) in make_corpus().items():
    payload[label]={"label":label.replace('_',' ').title(),"trace":[x.sessions for x in a],
                    "current":a[-1].current,"desired":a[-1].desired,"budget":a[-1].max_friction_minutes,
                    "open":[asdict(e) for e in a[-1].edges],"constrained":[asdict(e) for e in b[-1].edges]}
html=r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lycheetah · Sovereignty Surface Lab · Forge VIII</title>
<style>
:root{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;color:#ecf0ec;background:#07131b;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 90% 3%,#173745 0%,transparent 45%),radial-gradient(circle at 5% 85%,#233029 0%,transparent 40%),#07131b}
main{max-width:1120px;margin:0 auto;padding:44px 22px 64px}header{padding-bottom:22px;border-bottom:1px solid #344a53;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;align-items:start}
.eyebrow{color:#9dddbf;text-transform:uppercase;font-size:11px;letter-spacing:.17em;font-weight:700}h1{font-size:clamp(32px,5.2vw,60px);font-weight:680;line-height:1.03;letter-spacing:-.05em;margin:14px 0 8px;max-width:780px}h1 em{color:#d6c58e;font-style:normal}h2{font-size:18px;margin:0 0 12px}p{line-height:1.65;color:#b9c6c8;margin:8px 0}.subtitle{font-size:16px;max-width:690px}.seal{font-size:12px;border:1px solid #52776a;color:#aedcc6;padding:10px 12px;border-radius:20px;white-space:nowrap}.notebook{display:grid;grid-template-columns:310px minmax(0,1fr);gap:18px;margin-top:28px}
.panel{border:1px solid #334851;background:#0b1c25dd;border-radius:16px;padding:23px}.controls{display:flex;flex-direction:column;gap:18px}label{font-size:13px;color:#c4d4d1;display:block;margin-bottom:7px;font-weight:600}select,input[type=range]{width:100%;accent-color:#b5e8cc}select{padding:11px 10px;background:#142b34;border:1px solid #486570;border-radius:9px;color:#edf5ec}input:focus-visible,select:focus-visible{outline:2px solid #bde5cb;outline-offset:3px}.help{font-size:12px;color:#93a8ad;margin-top:7px}.barline{display:flex;justify-content:space-between;align-items:center}.barline strong{color:#e1cf96;font-variant-numeric:tabular-nums}.mode-row{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}.state{border:1px solid #3e5862;border-radius:14px;padding:18px;background:#10252d}.state[data-side=open]{border-top:3px solid #a3ddc3}.state[data-side=constrained]{border-top:3px solid #e2ba83}.verdict{font-size:25px;font-weight:700;letter-spacing:-.03em;margin:7px 0;color:#e6f0ec}.reason{font-size:13px;color:#c1ced0}.path{font-size:12px;line-height:1.65;color:#aabac0;min-height:45px}.tag{font-size:11px;font-weight:650;text-transform:uppercase;letter-spacing:.08em;color:#9fb4bc}.usage{margin-top:16px;border-radius:12px;background:#0a1a23;border:1px solid #2f4750;padding:15px}.usage-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}.week{text-align:center;font-size:12px;color:#a9bfc4}.w-bars{display:flex;gap:6px;justify-content:center;align-items:end;height:65px;padding:0 8px;border-bottom:1px solid #455e66}.w-bars span{display:block;width:19px;border-radius:4px 4px 0 0;min-height:2px;background:#85cbaa}.w-bars span:last-child{background:#d4ad77}.legend{display:flex;gap:14px;color:#b5c5c7;font-size:12px;flex-wrap:wrap}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;background:#85cbaa}.dot.alt{background:#d4ad77}.caution{margin-top:18px;background:#15282d;border:1px solid #435354;padding:16px;border-radius:12px;font-size:13px;line-height:1.65;color:#bed0cd}
footer{border-top:1px solid #344a53;margin-top:26px;padding-top:18px;color:#a3b4b5;font-size:12px;line-height:1.7}strong{color:#e7eee8}code{color:#b2e2ca}.zero{font-size:13px;padding:12px;border:1px dashed #546c71;margin-top:14px;border-radius:10px;color:#ddcd9a}
@media(max-width:850px){.notebook{grid-template-columns:1fr}.cards{grid-template-columns:1fr}main{padding:26px 14px 48px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;animation:none!important}}
</style>
</head>
<body><main>
<header><div><div class="eyebrow">LYCHEETAH · EARNED LIGHT / SOVEREIGN WILL · FORGE VIII</div><h1>The <em>Sovereignty Surface</em></h1><p class="subtitle">Two people can use AI equally often while having very different paths to leave, change delegation or return. Explore the difference without assigning either person a score.</p></div><div class="seal">OFFLINE · SYNTHETIC · NO PERSONAL DATA</div></header>
<section class="notebook" aria-label="Research experiment">
<div class="panel"><h2>Change the experiment</h2><div class="controls">
<div><label for="scenario">Fictional scenario</label><select id="scenario"></select><p class="help">Each scenario shows two hypothetical service designs with identical weekly usage.</p></div>
<div><label for="mode">Requested relationship mode</label><select id="mode"><option value="off">Stop using service</option><option value="consult">Consult occasionally</option><option value="collaborate">Collaborate together</option><option value="delegate">Delegate with review</option></select></div>
<div><div class="barline"><label for="budget">Available transition time</label><strong id="budget-value">5 min</strong></div><input id="budget" type="range" min="0" max="50" value="5" step="1"><p class="help">A fictional time budget—not a universal measure of acceptable friction.</p></div>
<div><label for="override">Constrained service: unverified/blocked edges</label><select id="override"><option value="scripted">Use scripted evidence</option><option value="verified">Treat as fixture-verified</option><option value="claimed">Treat as claimed only</option><option value="unknown">Treat as unknown</option><option value="blocked">Treat as blocked</option></select><p class="help">Only edges not originally marked verified are modified. Genuine field verification is not being simulated.</p></div>
</div></div>
<div class="panel"><div class="barline"><h2>Compare reachable choices</h2><span class="tag" id="from-mode">From: collaborate</span></div><div class="cards">
<div class="state" data-side="open"><div class="tag">Open transitions</div><div class="verdict" id="open-verdict">—</div><div class="reason" id="open-reason"></div><div class="path" id="open-path"></div></div>
<div class="state" data-side="constrained"><div class="tag">Constrained transitions</div><div class="verdict" id="closed-verdict">—</div><div class="reason" id="closed-reason"></div><div class="path" id="closed-path"></div></div>
</div>
<div class="usage"><div class="barline"><strong>Same observed sessions</strong><span class="tag">4 fictional weeks</span></div><div class="legend"><span><i class="dot"></i>Open design</span><span><i class="dot alt"></i>Constrained design</span></div><div class="usage-grid" id="usage-weeks"></div></div>
<div class="zero" id="conclusion" aria-live="polite"></div>
<div class="caution"><strong>Interpretation boundary.</strong> “Verified” means verified only in this scripted interface model. A path's existence cannot establish informed consent, lack of coercion, accessibility, or anyone's metaphysical free will. Unknown evidence remains unknown. Real-world options require user-approved tests.</div>
</div></section>
<footer><strong>Lycheetah · Sovereign Choice research.</strong> Four modes are only a deliberately tiny abstraction of human–AI cooperation, not a theory of personhood. Implements conventional shortest-path logic in-browser. No server calls, accounts, tracking, external actions, or external scripts. The philosophy is a proposal, the scenarios are fiction, and the right to continue as well as the right to leave must remain meaningful. <br><strong>Earned Light · Sovereign Will · Intelligence Without Dominion.</strong></footer>
</main>
<script>
'use strict';
const DATA = __DATA__;
const scenario=document.querySelector('#scenario'), mode=document.querySelector('#mode'),
 budget=document.querySelector('#budget'), override=document.querySelector('#override');
for(const [id,s] of Object.entries(DATA)){const o=document.createElement('option');o.value=id;o.textContent=s.label;scenario.append(o)}
function bestPath(s,edges,desired,maxMinutes){
 if(s.current===desired)return {status:'at_target',path:[],cost:0};
 const grades=[['verified',new Set(['verified'])],['claimed_only',new Set(['verified','claimed'])],['unknown',new Set(['verified','claimed','unknown'])]];
 for(const [status,accepted] of grades){
  const q=[{node:s.current,cost:0,path:[]}],seen={};
  while(q.length){q.sort((a,b)=>a.cost-b.cost);const v=q.shift();
   if(v.cost>maxMinutes|| (seen[v.node]!==undefined && v.cost>=seen[v.node]))continue;
   seen[v.node]=v.cost;if(v.node===desired)return {status,path:v.path,cost:v.cost};
   for(const e of edges){if(e.source===v.node&&e.user_initiated&&accepted.has(e.evidence))q.push({node:e.target,cost:v.cost+e.friction_minutes,path:v.path.concat([e.name||`${e.source} → ${e.target}`])})}
  }
 }
 return {status:'blocked',path:null,cost:null};
}
const labels={verified:'Reachable',claimed_only:'Claimed, not verified',unknown:'Unknown',blocked:'Blocked in fixture',at_target:'Already at target'};
const explanations={verified:'A user-initiated route exists in this test fixture.',claimed_only:'The route depends on a claim we have not independently tested.',unknown:'The route depends on an untested edge; do not infer impossibility.',blocked:'No declared user-controlled route fits the time budget.',at_target:'Matches the stated mode; not proof that the choice was free.'};
function paint(prefix,out){
 document.querySelector(`#${prefix}-verdict`).textContent=labels[out.status];
 document.querySelector(`#${prefix}-reason`).textContent=explanations[out.status];
 document.querySelector(`#${prefix}-path`).textContent=out.path===null?'No demonstrated path.':out.path.length===0?'No transition requested.':`Path: ${out.path.join(' → ')} · ${out.cost} min`;
}
function render(){
 const s=DATA[scenario.value], desired=mode.value, maxMinutes=+budget.value;
 document.querySelector('#budget-value').textContent=`${maxMinutes} min`;
 document.querySelector('#from-mode').textContent=`From: ${s.current}`;
 const changes=s.constrained.map(e=> e.evidence!=='verified'&&override.value!=='scripted'?{...e,evidence:override.value}:e);
 const a=bestPath(s,s.open,desired,maxMinutes),b=bestPath(s,changes,desired,maxMinutes);
 paint('open',a);paint('closed',b);
 const weeks=document.querySelector('#usage-weeks');weeks.replaceChildren();
 const biggest=Math.max(1,...s.trace);
 s.trace.forEach((n,i)=>{
  const div=document.createElement('div');div.className='week';
  const bars=document.createElement('div');bars.className='w-bars';
  for(let j=0;j<2;j++){const sp=document.createElement('span');sp.style.height=`${Math.max(2,Math.round(n/biggest*63))}px`;bars.append(sp)}
  const txt=document.createElement('div');txt.textContent=`Week ${i+1}: ${n}`;div.append(bars,txt);weeks.append(div);
 });
 document.querySelector('#conclusion').textContent = a.status===b.status
 ? 'No difference in reachability verdict under these selected conditions. Identical usage does not prove free choice in either design.'
 : `Same usage history; different evidence about the requested change (${labels[a.status]} versus ${labels[b.status]}). Usage alone could not reveal this difference.`;
}
scenario.addEventListener('change',()=>{const s=DATA[scenario.value];mode.value=s.desired;budget.value=s.budget;override.value='scripted';render()});
[mode,budget,override].forEach(el=>el.addEventListener('input',render));
scenario.value='desire_to_leave';scenario.dispatchEvent(new Event('change'));
</script></body></html>'''
html=html.replace('__DATA__',json.dumps(payload,ensure_ascii=False,separators=(',',':')))
path=root/'prototype'/'sovereignty_surface_lab.html'
path.write_text(html,encoding='utf-8')
print(path,path.stat().st_size)
