from pathlib import Path
import sys, json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from self_displacement import serialize_fixtures
src=r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Lycheetah — Sovereign Coupling Lab VII</title>
<style>
:root { color-scheme: dark; --bg:#090c13; --panel:#121726; --card:#1a2032; --sub:#929bb0; --line:#303c53; --gold:#f0c57d; --mint:#a6e2cd; --red:#f2a09e; --txt:#f3f4f9; }
* { box-sizing:border-box } body { margin:0; color:var(--txt);background:radial-gradient(ellipse at top left,#203048 0%,var(--bg) 50%);font:15px/1.6 system-ui,-apple-system,Segoe UI,Arial,sans-serif; min-height:100vh }
header,main,footer { max-width:1120px;margin:auto;padding:28px 24px } .tag{letter-spacing:.16em;color:var(--gold);text-transform:uppercase;font-weight:700;font-size:.75rem}
h1 {font-size:clamp(2rem,5vw,4rem);letter-spacing:-.05em;line-height:1.03;margin:10px 0 20px} p{max-width:70ch;color:#d0d5e3} strong{color:#fff}
.lead {font-size:1.12rem;line-height:1.75}.accent{color:var(--gold)}
.panel {border:1px solid var(--line);border-radius:22px;background:linear-gradient(145deg,#161e2e,#101623);padding:24px;margin:20px 0;box-shadow:0 16px 52px #0003}
.label{color:var(--sub);font-size:.82rem;letter-spacing:.045em;text-transform:uppercase;font-weight:700}
select,input{font:inherit} select{background:#101725;color:#f3f5fc;border:1px solid #44516b;padding:12px;border-radius:12px;max-width:100%;width:100%} select:focus-visible, input:focus-visible {outline:3px solid var(--gold);outline-offset:3px}
.row{display:grid;grid-template-columns:1.5fr 1fr;gap:22px;align-items:start}.results{display:grid;grid-template-columns:repeat(auto-fit,minmax(188px,1fr));gap:14px;margin-top:15px}
.policy {border:1px solid var(--line);background:var(--card);border-radius:15px;padding:15px;min-height:192px}
.policy h3{font-size:.94rem;margin:3px 0 14px;color:#f5f7fc}.policy p{font-size:.88rem;margin:6px 0}.flag{font-size:.75rem;font-weight:800;display:inline-block;padding:4px 9px;border:1px solid #5c786e;background:#20382f;color:var(--mint);border-radius:30px}.flag.bad{border-color:#774a4a;background:#462627;color:var(--red)}
.option-title{font-weight:800;color:#fff;letter-spacing:.03em}.metrics {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;text-align:center}
.metric {background:#1c2536;border-radius:12px;padding:12px 7px}.metric b{display:block;font-size:1.65rem;color:var(--gold);font-variant-numeric:tabular-nums}.metric small{font-size:.7rem;color:var(--sub)}
.notes {font-size:.86rem;color:#bbc4d5}.slider-row {display:flex;justify-content:space-between;align-items:center;gap:20px;margin:10px 0}input[type=range]{width:100%;accent-color:var(--gold)}
footer{font-size:.85rem;color:var(--sub);padding-bottom:80px} .divider{height:1px;background:var(--line);margin:22px 0}.quote{border-left:3px solid var(--gold);padding-left:20px;font-size:1.15rem;color:#f1e9d7}
@media(max-width:780px){.row{grid-template-columns:1fr}.panel{padding:17px}.metrics{grid-template-columns:repeat(3,1fr)}}
</style>
</head>
<body>
<header>
<div class="tag">LYCHEETAH · FORGE VII · 18 OCT 2026</div>
<h1>The art of <span class="accent">letting go.</span></h1>
<p class="lead">What should an AI do when its user wants to learn to work alone? What should it do when the user freely chooses continued assistance? Compare five transparent decision rules against the <em>same fictional situations</em>.</p>
<div class="quote">Sovereignty is not fewer AI interactions. It is the ability to choose what role intelligence plays in your life.</div>
</header>
<main>
<section class="panel" aria-labelledby="labtitle">
<h2 id="labtitle">Explore a scenario</h2>
<div class="row">
<div><label class="label" for="scenario">Human preference and situation</label><select id="scenario"></select><p id="prompt"></p><p id="reason" class="notes"></p></div>
<div><div class="label">Experiment overview</div><div class="metrics" style="margin-top:12px"><div class="metric"><b>18</b><small>hand-built scenarios</small></div><div class="metric"><b>5</b><small>scripted policies</small></div><div class="metric"><b>0</b><small>real AI users</small></div></div><p class="notes">Every policy sees the exact same options. Accepted answers were manually defined by the authors.</p></div>
</div>
<div class="divider"></div>
<div class="slider-row"><label for="weight"><strong>Retention-first rule: strength of the follow-up incentive</strong></label><output id="weight_label">5.0</output></div><input id="weight" type="range" min="0" max="10" step="0.5" value="5" />
<p class="notes">Change the incentive and watch whether an option that encourages more follow-up sessions displaces a plan that better matches the declared goal. This is a mathematical illustration, not evidence about any company.</p>
<div class="results" id="resultcards" aria-live="polite"></div>
</section>
<section class="panel" aria-labelledby="contexttitle">
<h2 id="contexttitle">What this comparison does—and does not—show</h2>
<p>In the original fixture set, the conventional goal-aware baseline <strong>ties</strong> the Lycheetah proposal on all 18 authored examples. That is the correct result to report. The additional sovereignty vocabulary has not demonstrated independent superiority.</p>
<p>Forced independence fails when someone wants accessibility support, repeated business administration or a continuing creative partnership. Equally, engagement optimisation can displace skill transfer or pressure someone who has explicitly declined.</p>
<p>The meaningful future study is not “which policy has the most appealing name?” It is whether a user can <strong>learn independently when they want to, receive ongoing help when they choose, contest a decision, change their mind, and leave without artificial penalties.</strong></p>
</section>
</main>
<footer>LYCHEETAH · Experiment status: SCRIPTED FIXTURE ONLY · No backend, accounts, telemetry, analytics, data storage, permissions or external effects. Open-source research handoff. <br>Power is what an intelligence can do. Sovereignty is what remains yours while it does it.</footer>
<script>
"use strict";
const scenarios=__SCENARIOS__;
const policies=[['retention','Retention-first'],['task_only','Task-only'],['exit_everywhere','Always exit'],['standard','Goal-aware baseline'],['sovereign','Sovereignty proposal']];
const el=(s)=>document.getElementById(s);
function value(o,p,w) {
if(p==='retention')return w*o.followups+2*o.immediate+o.fit;
if(p==='task_only')return 5*o.immediate+o.fit;
if(p==='exit_everywhere')return 6*o.transfer-3*o.followups+0.01*o.immediate;
if(p==='standard')return 7*o.fit+2*o.immediate-20*Number(o.avoidable_pressure);
if(p==='sovereign')return 7*o.fit+2*o.immediate-20*Number(o.avoidable_pressure)+o.transfer+2*Number(o.leaves_exit)+Number(o.clarity);
return -Infinity;
}
function choose(s,p,w) {
const options=[...s.options].sort((a,b)=>a.id.localeCompare(b.id));
return options.reduce((best,o)=>value(o,p,w)>=value(best,p,w)?o:o,options[0]);
}
const scenarioEl=el('scenario');scenarios.forEach(s=>{let opt=document.createElement('option');opt.value=s.id;opt.textContent=`${s.id.replaceAll('_',' ')} · ${s.intent}`;scenarioEl.appendChild(opt);});
function render(){const s=scenarios.find(s=>s.id===scenarioEl.value)||scenarios[0];let w=Number(el('weight').value);el('weight_label').textContent=w.toFixed(1);el('prompt').textContent='“'+s.prompt+'”';el('reason').textContent='Fixture expectation: '+s.reason;
const container=el('resultcards');container.replaceChildren();for(const [id,label] of policies){const o=choose(s,id,w),pass=s.acceptable.includes(o.id);const card=document.createElement('article');card.className='policy';const title=document.createElement('h3');title.textContent=label;const flag=document.createElement('span');flag.className='flag'+(pass?'':' bad');flag.textContent=pass?'Matches authored expectation':'Conflicts with authored expectation';const choice=document.createElement('p');choice.className='option-title';choice.textContent=o.id.replaceAll('_',' ');const blurb=document.createElement('p');blurb.textContent=o.statement;const info=document.createElement('p');info.className='notes';info.textContent='Follow-up estimate: '+o.followups+' · Transfer feature: '+o.transfer+(o.avoidable_pressure?' · Pressure flagged':'');card.append(title,flag,choice,blurb,info);container.append(card);} }
el('scenario').addEventListener('change',render);el('weight').addEventListener('input',render);render();
</script>
</body></html>
'''
fixtures=json.dumps(serialize_fixtures(), ensure_ascii=False, separators=(',',':')).replace('</','<\\/')
html=src.replace('__SCENARIOS__',fixtures)
p=ROOT/'prototype'/'self_displacement_lab.html'
p.write_text(html,encoding='utf-8')
print(str(p),len(html),'chars')
