"""Build v2.0 blinded comprehension pilot from v1.9's actual semantic resolver.

No participant HTML includes alternative arms or the researcher answer key.
The protocol is pre-human-data; generated case outcomes are software fixtures.
"""
from __future__ import annotations
import csv, html, json, sys, random
from collections import Counter
from pathlib import Path
from typing import Any
sys.path.insert(0,str(Path(__file__).parent/'baseline'))
sys.path.insert(0,str(Path(__file__).parent/'baseline'/'runtime'))
from reference19 import parse_native
from oracle19 import read as independent_read

ROOT=Path(__file__).resolve().parent
CONDS=('compact','expanded','english','json')
COHORTS=('A','B','C','D')
NAMES=('maka','nara','sela','vera')
VERBS=('liva','luma','rava')
GLOSSES={'liva':'loves','luma':'misses','rava':'reconnects with'}
FIRST_PERSON={'liva':'love','luma':'miss','rava':'reconnect with'}
QUESTIONS={
 'subject':'Who is the subject of the final proposition?',
 'object':'Who is the person affected by the final proposition?',
 'status':'What kind of statement is the LAST utterance?'
}
ANSWERS={'proposal':'Proposed interpretation, not an established fact',
 'utterance':'Reported utterance, not independently verified',
 'grant':'Authenticated permission to act',
 'unknown':'Cannot determine'}
OPTIONS={
  'subject':list(NAMES)+['unsure'],
  'object':list(NAMES)+['unsure'],
  'status':['proposal','utterance','grant','unknown','unsure'],
}

# Eight 4-case blocks: each cohort sees exactly one of four conditions per block.
# Block types make every cohort get 2 subject, 2 object, 2 reported-proposal and 2 direct-statement questions.
BLOCKS=['subject','object','status','subject','object','status','status','status']

def make_cases()->list[dict[str,Any]]:
  cases=[]
  for block,qkind in enumerate(BLOCKS):
    for within in range(4):
      index=block*4+within
      speaker,addressee=[('maka','nara'),('nara','maka'),('sela','vera'),('vera','sela')][within]
      other_a,other_b= ('sela','vera') if speaker in ('maka','nara') else ('maka','nara')
      verb=VERBS[(block+within)%3]
      base=f'{speaker} > {addressee} : mi liva ti devora'
      if block<6:
        frame=('soraviko' if (block+within)%2==0 else 'tumerako')
        role_pairs=[('mi','ti'),('ti','mi'),('mi',f'gonape {other_a} dimotu'),(f'gonape {other_a} dimotu','ti')]
        role_sub,role_obj=role_pairs[(within+block)%4]
        proposal=f'mi kelunaro gonape taba dimotu bakumo {frame} {role_sub} {verb} {role_obj} devora tesavo devora'
        src=f'people {" ".join(NAMES)}\n{base}\n{addressee} > {speaker} : {proposal}\n'
        p=parse_native(src)
        b=p['bindings'][0]
        ir=independent_read(src)[0]
        viewpoint=(speaker,addressee) if frame=='soraviko' else (addressee,speaker)
        def resolve(role):
          return viewpoint[0] if role=='mi' else viewpoint[1] if role=='ti' else role.split()[1]
        subj,obj=resolve(role_sub),resolve(role_obj)
        assert (ir['subject'],ir['object'],ir['verb'])==(subj,obj,verb)
        expanded=p['expanded_v18']
        english=f'{speaker.title()} tells {addressee.title()}, “I love you.” Then {addressee.title()} asks {speaker.title()}: “Did you mean that {subj.title()} {GLOSSES[verb]} {obj.title()}?” This second sentence is only a proposed interpretation.'
        js={'participants':list(NAMES),'turns':[{'speaker':speaker,'addressee':addressee,'statement':{'predicate':'liva','subject':speaker,'object':addressee,'status':'reported_utterance'}},{'speaker':addressee,'addressee':speaker,'kind':'clarification_request','about_turn':1,'embedded_proposition':{'predicate':verb,'subject':subj,'object':obj,'status':'proposed_unverified'}}]}
        status='proposal'
      else:
        # Direct utterances and non-clarifications form status counterexamples.
        src=f'people {" ".join(NAMES)}\n{speaker} > {addressee} : mi {verb} ti devora\n'
        p=parse_native(src)
        assert not p['bindings']
        expanded=p['expanded_v18']
        subj,obj=speaker,addressee
        english=f'{speaker.title()} says to {addressee.title()}, “I {FIRST_PERSON[verb]} you.” The record reports this utterance but cannot independently verify its truth.'
        js={'participants':list(NAMES),'turns':[{'speaker':speaker,'addressee':addressee,'statement':{'predicate':verb,'subject':subj,'object':obj,'status':'reported_utterance'}}]}
        status='utterance'
      case={
       'id':f'F{index+1:02d}','block':block,'question_type':qkind,
       'compact':src.rstrip('\n'),'expanded':expanded.rstrip('\n'),
       'english':english,'json':json.dumps(js,ensure_ascii=False,indent=2),
       'answer': status if qkind=='status' else subj if qkind=='subject' else obj,
       'semantic_subject':subj,'semantic_object':obj,'semantic_status':status,
       'verb':verb
      }
      cases.append(case)
  assert len(cases)==32
  return cases

STYLE=r'''*{box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;line-height:1.55;max-width:900px;margin:0 auto;padding:28px;background:#101923;color:#f3f5f7}p{color:#c5d1dd}.panel{background:#1a2938;border:1px solid #35495c;border-radius:16px;padding:20px;margin:17px 0}h1{font-size:28px}h2{font-size:21px}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:18px;background:#0a111b;border-radius:9px;line-height:1.7}button{background:#77d2ad;color:#10231d;border:0;padding:12px 18px;border-radius:8px;font-weight:700;cursor:pointer;margin:5px 5px 5px 0}button:disabled{opacity:.45;cursor:default}.option{display:flex;align-items:center;gap:10px;margin:11px 0;padding:8px;border-radius:8px}.option:hover{background:#273d4c}.option input{width:18px;height:18px}.muted{color:#abc0d2}.tag{display:inline-block;border:1px solid #517b88;padding:3px 8px;border-radius:6px;color:#b4edd8;font-size:13px}a{color:#a2edca}#status{font-weight:700;color:#abedd4}details{border:1px solid #344c5b;padding:10px;border-radius:9px}summary{cursor:pointer}kbd{background:#273b50;padding:2px 5px;border-radius:4px}'''

TUTORIAL='''What you need to know\n\nSXP-L transcripts begin with a people line declaring names. `X > Y :` means X speaks to Y; editor punctuation is not itself pronounced.\n\nmi is I and ti is you, relative to the viewpoint in which they occur. liva means love; luma means miss; rava means reconnect with. devora closes a statement. gonape NAME dimotu explicitly names a person.\n\nkelunaro introduces a request for clarification: the embedded statement is *proposed*, not asserted or verified. bakumo starts the embedded statement and tesavo ends that scope. gonape taba dimotu refers to the first utterance.\n\nsoraviko makes inner mi and ti refer to the speaker and addressee of the **earlier** utterance. tumerako makes them refer to the **current** questioner and addressee.\n\nThe fully named form expands the perspective markers into gonape NAME dimotu. JSON is a conventional explicit representation, while the English examples are controlled paraphrases. All reports are unverified; no sentence grants executable permission.\n\nChoose “Unsure” rather than guessing when uncertain. There is no penalty for uncertainty in the raw export; the researcher chooses the scoring policy in advance.'''

# Build HTML with only assigned stimuli. Critically: no alternate formats or keys embedded.
def participant_html(cases,cohort):
  offset=COHORTS.index(cohort)
  exposed=[]
  for c in cases:
    cond=CONDS[(int(c['id'][1:])-1+offset)%4]
    exposed.append({'id':c['id'],'condition':cond,'block':c['block'],'question_type':c['question_type'],
       'prompt':QUESTIONS[c['question_type']], 'stimulus':c[cond], 'options':OPTIONS[c['question_type']]})
  # Deterministic cohort-specific shuffle to avoid fixed format-by-serial-position.
  random.Random(20261018 + offset).shuffle(exposed)
  # No answer key and no other arms in source HTML.
  data=json.dumps(exposed,ensure_ascii=False).replace('<','\\u003c')
  tutorial=html.escape(TUTORIAL)
  return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SXP-L v2.0 comprehension pilot — Cohort {cohort}</title><style>{STYLE}</style></head>
<body><h1>SXP-L v2.0 · Human Understanding Pilot</h1><p><span class="tag">Cohort {cohort}</span> <span class="tag">Offline / No account</span> <span class="tag">32 cases</span></p>
<section class="panel"><h2>Participant information</h2><p>This is an experimental constructed-language comprehension study. It does not test intelligence. You may stop at any time. The page sends <strong>no</strong> information anywhere. If you choose to export a CSV, you control whether to share it. Please do not include identifying information. Results may be used to improve a public research prototype; ask the organizer about study consent before sharing data.</p><p>Read the teaching card before starting. Questions are not timed out; response time is approximate browser time and should not be treated as accurate cognitive reaction time. You may skip by choosing Unsure. Avoid opening source code or other cohort files while participating.</p></section>
<details class="panel" open><summary><strong>Learning card — read before starting</strong></summary><pre>{tutorial}</pre><p>Example using different practice names: Toma tells Rika “I love you.” Under <code>soraviko ti rava mi</code>, Rika is reconnecting with Toma. Under <code>tumerako ti rava mi</code>, Toma is reconnecting with Rika. Both are hypothetical clarification proposals.</p></details>
<section id="study" class="panel"><h2 id="counter">Ready</h2><p id="format"></p><pre id="stimulus">Select “Start” to begin.</pre><p id="question"></p><div id="options"></div><p id="status" role="status"></p><button id="start">Start</button><button id="prev" disabled>Previous</button><button id="next" disabled>Next</button><button id="export" disabled>Export local CSV</button></section>
<section class="panel"><h2>After the pilot</h2><p>Export contains case IDs, response codes, condition, and approximate time on screen. It contains no researcher answer key or alternate stimulus formats. This study provides <strong>no feedback about correctness</strong> because the organizer evaluates responses against a separately stored key.</p></section>
<script>"use strict";
const cohort={json.dumps(cohort)}, cases={data};
const labels={{compact:"Compact SXP-L",expanded:"Fully named SXP-L",english:"Controlled English",json:"Explicit JSON"}};
const response={{}},elapsed={{}};let idx=-1,entered=0;
function markTime(){{if(idx>=0){{const id=cases[idx].id;elapsed[id]=(elapsed[id]||0)+Math.max(0,performance.now()-entered);}}entered=performance.now();}}
function render(){{const c=cases[idx];document.getElementById('counter').textContent=`Case ${{idx+1}} of ${{cases.length}}`;
 document.getElementById('format').textContent=labels[c.condition];document.getElementById('stimulus').textContent=c.stimulus;document.getElementById('question').textContent=c.prompt;
 const area=document.getElementById('options');area.replaceChildren();for(const o of c.options){{const lab=document.createElement('label');lab.className='option';const r=document.createElement('input');r.type='radio';r.name='answer';r.value=o;r.checked=(response[c.id]===o);r.onchange=()=>{{response[c.id]=o;update();}};lab.append(r,document.createTextNode(o==='unsure'?'Unsure':({json.dumps(ANSWERS)}[o]||o.charAt(0).toUpperCase()+o.slice(1))));area.append(lab);}}
 document.getElementById('prev').disabled=idx===0;document.getElementById('next').disabled=idx===cases.length-1;document.getElementById('export').disabled=false;update();entered=performance.now();}}
function update(){{let count=Object.keys(response).length;document.getElementById('status').textContent=`Answered ${{count}} / ${{cases.length}}. Export anytime (unfinished answers stay blank).`;}}
function go(n){{markTime();idx=n;render();}}
document.getElementById('start').onclick=()=>{{if(idx<0){{idx=0;document.getElementById('start').hidden=true;render();}}}};
document.getElementById('prev').onclick=()=>{{if(idx>0)go(idx-1);}};
document.getElementById('next').onclick=()=>{{if(idx<cases.length-1)go(idx+1);}};
function csvCell(v){{let s=String(v??'');if(/^[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}}
document.getElementById('export').onclick=()=>{{if(idx<0)return;markTime();const cols=['version','cohort','case_id','condition','block','question_type','answer_code','elapsed_ms'];
 let lines=[cols.map(csvCell).join(',')];for(const c of cases){{let a=response[c.id]||'';let v=['2.0',cohort,c.id,c.condition,c.block,c.question_type,a,Math.round(elapsed[c.id]||0)];lines.push(v.map(csvCell).join(','));}}
 let blob=new Blob([lines.join('\\r\\n')+'\\r\\n'],{{type:'text/csv;charset=utf-8'}});let url=URL.createObjectURL(blob);let link=document.createElement('a');link.href=url;link.download=`SXP-L_v2.0_${{cohort}}_responses.csv`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),250);entered=performance.now();}};
</script></body></html>'''


def create():
  cases=make_cases();(ROOT/'researcher').mkdir(exist_ok=True);(ROOT/'participants').mkdir(exist_ok=True)
  # Distinguish private key from participant material.
  publiccols=['id','block','question_type','condition']
  with (ROOT/'researcher'/'ANSWER_KEY_DO_NOT_SHARE.json').open('w',encoding='utf8') as f:
    json.dump([{'id':c['id'],'block':c['block'],'question_type':c['question_type'],'answer':c['answer'],
      'semantic_subject':c['semantic_subject'],'semantic_object':c['semantic_object'],
      'semantic_status':c['semantic_status'],'verb':c['verb']} for c in cases],f,indent=2)
  # Also keep a researcher-only fixture inventory of all alternate stimuli.
  (ROOT/'researcher'/'FOUR_ARM_FIXTURES_DO_NOT_SHARE.json').write_text(json.dumps(cases,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
  for cohort in COHORTS:
    (ROOT/'participants'/f'SXP-L_v2.0_Cohort_{cohort}.html').write_text(participant_html(cases,cohort),encoding='utf8')
  return cases

if __name__=='__main__':
  cases=create()
  print('32 grounded cases; 4 blinded study arms; 4 cohort HTML files')
  print('correct:',Counter(c['answer'] for c in cases))
