# NZ TECHNICAL MIN-MAX
## What Government Wants × What People Want × What the Stack Delivers
### Pure NZ Technical Language | Lycheetah Framework | March 2026
### Mackenzie Conor James Clark | Dunedin
### Status: [SCAFFOLD] — Technical stacks specified; build times and political claims are estimates, not validated delivery commitments. Individual tools annotated inline.

> Min-max: minimum friction to fund, maximum benefit to people.
> Every idea here wins on both sides simultaneously or it's not in this document.

---

## THE MATRIX

**NZ Government currently needs to show:**
- AI sovereignty (not dependent on US/China infrastructure)
- Māori data protection with actual teeth (Treaty obligations, Waitangi Tribunal pressure)
- Productivity gains for SMEs (MBIE mandate)
- Public trust in government AI (trust deficit is real and documented)
- Health system efficiency without destroying equity (Te Whatu Ora crisis)
- Digital economy growth that keeps talent in NZ (brain drain to Australia)
- Something to take to Pacific Forum that isn't just American AI rebranded

**NZ people currently need:**
- Cost of living tools that actually work
- Housing system that isn't broken by algorithmic landlords
- Health services they can access and trust
- Jobs that don't disappear to AI without warning
- Their data not being sold to overseas companies
- Their kids to have a reason to stay in NZ
- Government that can explain what its algorithms are doing to them

**Where these two lists overlap is every idea below.**
That overlap is the only place worth building.

---

## 1. THE BENEFIT FRAUD AUDIT REVERSAL

**Current state:**
MSD uses algorithmic risk scoring to flag benefit fraud.
The algorithm is opaque. The false positive rate disproportionately
hits Māori, Pacific, and disabled communities.
This is documented. It is not disputed. It is causing harm right now.

**What government wants:**
Reduce fraud. Reduce cost. Demonstrate fairness. Avoid Waitangi Tribunal exposure.

**What people want:**
Not to be falsely accused. Transparency about why they were flagged.
The ability to challenge an algorithmic decision with a real explanation.

**The min-max solution:**
**CASCADE Coherence Audit Layer for MSD algorithmic decisions.**

Every algorithmic decision that affects a benefit recipient
produces a CASCADE coherence score alongside it.

The score answers: how internally consistent is this decision
with the stated values of the system that made it?

A decision flagging a sole parent in South Auckland for fraud review
while the algorithm was optimised on data from a different demographic
will score low coherence. The contradiction is mathematical. It's visible.

The recipient gets: plain language explanation of why they were flagged.
MSD gets: early warning when the algorithm is drifting from its stated purpose.
The Waitangi Tribunal gets: a formal audit trail.

**Technical stack:**
- `cascade_engine.py` + `aura_sovereign_codex.py`
- AURA Invariant II (Inspectability) as the constitutional requirement
- MICROORCIM to measure whether the decision preserved or reduced recipient agency

**Build time:** 6 weeks. [SCAFFOLD — estimate; no equivalent has been built in NZ]
**Cost:** Under $50K NZD. [SCAFFOLD — estimate]
**Political value for government:** Enormous. First agency to do this leads. [CONJECTURE — political uptake is unpredictable]
**Value for people:** They finally know why the machine said no.

---

## 2. THE HOUSING ALGORITHM WATCHDOG

**Current state:**
Algorithmic tools are being used by property managers, insurance companies,
and potentially Housing NZ to assess tenancy risk.
These tools are mostly imported, trained on overseas data,
and have no NZ-specific cultural or economic calibration.
They encode overseas housing discrimination patterns into NZ decisions.

**What government wants:**
Housing crisis solutions. Māori housing equity. Avoid discrimination liability.
Keep international investors onshore without destroying affordability.

**What people want:**
A fair shot at housing. Not to be rejected by an algorithm that doesn't know them.
Transparency about why they were declined.

**The min-max solution:**
**NZ Housing Algorithm Certification Scheme.**

Any algorithmic tool used in NZ housing decisions must:
1. Publish its Whakapapa (training data origin, cultural context, known biases)
2. Pass a CASCADE coherence test against NZ housing equity principles
3. Carry a Mana Certification level (Mana Iti for advisory, Mana Taurite for decisions)
4. Be auditable by the Tenancy Tribunal on request

**The lever:**
MBIE already regulates the tenancy sector.
Add algorithmic tool certification to existing tenancy service provider requirements.
No new legislation needed initially — amend existing regulations.

**Technical stack:**
- LAMAGUE Whakapapa Disclosure Standard applied to housing algorithms
- CASCADE truth pressure scoring for equity coherence
- Mana Certification three-level system

**Build time:** 3 months for certification framework spec.
**Political value:** Massive. Housing is the #1 issue. Government is seen acting.
**Value for people:** The algorithm that rejected them is now accountable.

---

## 3. THE RURAL AI EXTENSION SERVICE

**Current state:**
NZ's primary sector (farming, horticulture, forestry) generates 70%+ of export earnings.
Rural communities are being left behind on AI adoption —
not because they don't want it but because every AI tool is built for cities
and has no understanding of NZ-specific conditions.

A Canterbury sheep farmer trying to use AI for pasture management
gets advice calibrated to an Iowa corn farm.
It's not just unhelpful. It's actively wrong.

**What government wants:**
Primary sector productivity. Rural community retention. Export growth.
Reduce the city/rural digital divide. MPI mandate delivery.

**What people want:**
AI tools that actually understand their land, their climate, their tikanga.
Not having to translate American farming AI into NZ conditions manually.
Their kids to have a future in rural NZ.

**The min-max solution:**
**Aotearoa Primary Sector AI Extension Service.**

A network of NZ-calibrated AI models for the primary sector:
- Trained on NZ-specific climate, soil, ecology data
- Kaitiakitanga constraints hardcoded (irreversibility gates, intergenerational impact)
- Maramataka temporal layer (not just what to do — when)
- Atua domain sovereignty (Tangaroa for marine, Tāne for forestry, Rongo for food)
- Plain English + Te Reo output options

**Delivery model:**
Free base tier via Rural Connectivity Programme infrastructure.
Paid advisory tier for commercial operations.
Government subsidised for small farms under 200ha.

**Technical stack:**
- Atua domain constraint clusters (from existing LAMAGUE work)
- CASCADE truth pressure for advice coherence
- AURA kaitiakitanga operational constraints
- Maramataka timing layer on HARMONIA resonance base

**Build time:** 12 months for MVP covering three primary sectors.
**Revenue model:** MPI contract + Callaghan Innovation + user subscriptions.
**Political value:** Rural NZ sees government delivering for them specifically.
**Value for people:** AI that speaks their language about their land.

---

## 4. THE SCHOOL ALGORITHM TRANSPARENCY TOOL

**Current state:**
NZ schools are adopting AI tools fast — assessment software, learning analytics,
behaviour management systems, attendance tracking.
Parents have no idea what these tools are doing to their kids' records.
Teachers don't fully understand them either.
The Ministry of Education has no coherent framework for evaluating them.

**What government wants:**
EdTech efficiency gains. Student equity. Avoid discrimination scandal.
Show leadership on responsible AI in education.

**What people want:**
Know what AI is being used on their child.
Know what data is being collected.
Know if an algorithm has flagged their child for something.
Know they can challenge it.

**The min-max solution:**
**NZ School AI Transparency Dashboard.**

Every school using an AI tool publishes a plain-language card:
- What tool is being used
- What decisions it informs
- What data it collects
- What the Whakapapa of the tool is (who built it, where, on what data)
- A CASCADE coherence score: does this tool's stated purpose match its actual function
- A contact for parents to query their child's data

**The lever:**
Ministry of Education procurement requirements.
Any AI tool seeking MoE approval must provide dashboard-compatible data.

**Technical stack:**
- LAMAGUE Whakapapa template applied to edtech tools
- CASCADE coherence scoring (automated, standardised)
- Three Worlds disclosure (what it knows, what it doesn't, what it can't see)

**Build time:** 8 weeks for dashboard MVP.
**Cost:** Under $30K.
**Political value:** Every parent in NZ sees government protecting their kids.
**Value for people:** The black box opens. Finally.

---

## 5. THE TENANCY TRIBUNAL AI ASSISTANT

**Current state:**
NZ Tenancy Tribunal handles 20,000+ cases per year.
Most tenants represent themselves.
Most landlords have property managers with legal support.
The information asymmetry is severe.
Tenants lose cases they should win because they don't know the law.

**What government wants:**
Access to justice. Reduce tribunal backlog. Māori housing equity outcomes.
Demonstrate AI serving ordinary people not corporations.

**What people want:**
A fair fight. Know their rights. Not lose their home because they couldn't afford a lawyer.

**The min-max solution:**
**Tenancy Rights AI — a genuinely free, genuinely useful legal assistant.**

Not a chatbot that says "consult a lawyer."
An AI with:
- Full NZ tenancy law encoded as constitutional constraints (AURA)
- Plain English and Te Reo output
- Case preparation tool: enter your situation, get the specific law that applies
- Tribunal preparation: step-by-step guide built around YOUR specific case
- Mana Iti certification: advisory only, but advice you can actually use

**The critical design principle:**
The AI's success metric is not engagement.
It is: did the tenant get the outcome they were legally entitled to?
MICROORCIM measures whether the tool preserved the user's agency
or created dependency on the tool.

**Technical stack:**
- AURA constitutional constraint layer with NZ Tenancy Act encoded
- LAMAGUE translation for legal → plain language
- CASCADE coherence testing of advice against case specifics
- MICROORCIM agency preservation metric

**Build time:** 3 months.
**Revenue model:** MOJ contract. Could be part of Citizens Advice Bureau digital service.
**Political value:** Government seen delivering justice for renters.
**Value for people:** The first AI that genuinely helps people who can't afford help.

---

## 6. THE MĀORI HEALTH DATA SOVEREIGNTY STACK

**Current state:**
Te Whatu Ora holds enormous Māori health data.
Māori health outcomes are the worst in the NZ system.
The data that could fix this is being managed in systems
that weren't built to respect whakapapa or collective data rights.

The Waitangi Tribunal has already ruled that the Crown has obligations
regarding Māori health data. The technical implementation doesn't exist.

**What government wants:**
Māori health equity outcomes. Waitangi Tribunal compliance.
Show NZIAT that NZ has sovereign AI health capability.

**What people want:**
Their health data not used against them.
Collective consent for research use of whānau health data.
Health AI that knows what Māori health actually looks like.

**The min-max solution:**
**Whakapapa Health Data Architecture for Te Whatu Ora.**

A data governance layer that:
- Treats health data as collectively held by whānau/hapū/iwi, not individually owned
- Requires iwi-level consent for research use of aggregated Māori data
- Preserves relational structure in data (doesn't flatten whānau to individuals)
- Applies kaitiakitanga constraints to all research use (irreversibility gate, intergenerational impact)
- Publishes a mauri score for the health data ecosystem: is this data being used to heal or extract?

**Technical stack:**
- LAMAGUE Whakapapa relational data structure
- AURA Invariants I (Human Primacy) and III (Memory Continuity)
- CASCADE truth pressure on research claims derived from Māori data
- MICROORCIM agency measure: does the research expand or contract Māori health autonomy?

**Partnership required:**
Kāi Tahu. Waikato-Tainui. Te Arawa.
Tech without iwi partnership is tech without authority.
Mac is in Ōtākou. Kāi Tahu is the logical first partner.

**Build time:** 18 months with proper iwi consultation.
**Revenue model:** Te Whatu Ora contract + Health Research Council.
**Political value:** Solves the Waitangi Tribunal exposure. Demonstrable equity commitment.
**Value for people:** Their data heals their community. Finally.

---

## 7. THE SME AI TRUST CHECKER

**Current state:**
NZ SMEs are adopting AI tools fast and with almost no guidance.
They're trusting AI-generated business advice that may be hallucinated.
They're using overseas tools that have no NZ regulatory awareness.
MBIE has a mandate to support SME digital adoption but no good tools.

**What government wants:**
SME productivity. Digital economy growth. Demonstrate AI benefit to business.
The $15K MBIE SME AI adoption pilot needs something to fund.

**What people want:**
Know if the AI advice they're getting is actually reliable.
Not get in trouble with IRD or MBIE because they followed hallucinated AI advice.
A competitive edge against big businesses with AI teams.

**The min-max solution:**
**NZ Business AI Trust Checker — CASCADE-lite for SMEs.**

Web tool. Free base tier.
Paste any AI-generated business advice.
Get back:
- Internal contradiction score (CASCADE truth pressure)
- NZ regulatory coherence check (does this advice violate NZ law?)
- Confidence calibration (what is this AI tool actually certain about vs guessing?)
- Plain language flag: "this advice should be verified before acting on it"

**The NZ-specific layer:**
- IRD rules encoded (GST, PAYE, provisional tax — the things SMEs get wrong)
- Employment Relations Act constraints
- Consumer Guarantees Act
- RMA basics for businesses with environmental obligations

**Technical stack:**
- `cascade_engine.py` — truth pressure as the core scoring engine
- AURA Invariant VI (Non-Deception) as the constitutional flag
- NZ regulatory constraint library (buildable from public legislation)
- Three Worlds output: here's what it knows, here's what it's guessing, here's what it can't know

**Build time:** 6 weeks for MVP. [SCAFFOLD — estimate; cascade_engine.py exists but a production UI wrapper has not been built]
**Revenue model:** Free base → $19/month pro → MBIE pilot contract. [CONJECTURE — revenue pathway is proposed, not negotiated]
**Political value:** MBIE can point to this as the tool they funded. [CONJECTURE]
**Value for people:** The first tool that tells SMEs when not to trust AI.

---

## 8. THE COMMUNITY AI WARRANT OF FITNESS

**Current state:**
NZ has a Warrant of Fitness for cars.
Annual check. Clear pass/fail. Public record.
It saves lives because it makes safety visible and enforceable.

NZ has no equivalent for AI systems affecting communities.

**What government wants:**
Public trust in AI. Liability protection. Regulatory framework without overreach.
Something that works alongside existing compliance infrastructure.

**What people want:**
Know if the AI affecting their life has been checked.
Know who to complain to if it fails.
Know it'll be checked again next year.

**The min-max solution:**
**Community AI Warrant of Fitness (CAIWOF).**

Annual certification for any AI system operating in NZ public-facing services.

**The WOF checks:**
- Whakapapa disclosure current and accurate
- CASCADE coherence score above minimum threshold
- Mana Certification level appropriate to the decisions being made
- Pōwhiri Protocol completed for the community it serves
- Resonance Trap monitoring active (psychological safety)
- Mauri score above minimum (is the system generating or depleting wellbeing?)
- Three Worlds epistemic disclosure present in outputs

**Pass:** CAIWOF certificate issued. Publicly registered. Valid 12 months.
**Fail:** System suspended until remediation.
**Lapse:** System immediately flagged in public register.

**The administration:**
An independent CAIWOF Authority.
Modelled on NZTA's WOF structure — small, focused, delegated to certified assessors.

**Technical stack:**
The entire Lycheetah stack is the assessment framework.
Each check maps to a specific module.
The assessor runs the tools. The tools produce the certificate components.

**Build time:**
CAIWOF specification: 3 months.
First assessment tools: 6 months.
Pilot scheme: 12 months.

**Revenue model:** Assessment fees (like WOF fees). Government-set tariff.
**Political value:** Tangible, understandable, analogous to something that already works.
**Value for people:** Three words: "Has it got its WOF?"

---

## 9. THE PACIFIC REMITTANCE AI

**Current state:**
Pacific communities in NZ send $500M+ per year in remittances to Pacific Island families.
Fees eat 5-10% of that. The services are mostly operated by offshore companies.
The money is critical for Pacific Island economies — it exceeds foreign aid in some nations.

**What government wants:**
Pacific community support. Financial inclusion. Pacific Forum relationships.
Demonstrate NZ as a genuine Pacific partner not just a regional power.

**What people want:**
More of their money getting to their family.
Not getting ripped off by overseas money transfer services.
Tools that understand their relationship to their extended family and obligations.

**The min-max solution:**
**Aotearoa Pacific Financial AI — fee transparency and smart remittance tools.**

Not a fintech startup. An open-source tool:
- Real-time fee comparison across all NZ-to-Pacific transfer services
- Smart timing recommendations (when to send based on exchange rate patterns)
- Utu tracking: family obligation accounting that respects Pacific gift economy norms
- Kotahitanga pooling: community collective transfer tools (multiple families sending together for better rates)

**The utu layer:**
Pacific gift economies involve complex obligations — reciprocal exchange,
family hierarchy, seasonal obligations.
An AI that understood this would help families manage these obligations
without the stress of tracking them manually.

Not turning relationships into transactions.
Helping people honour their relationships more easily.

**Technical stack:**
- LAMAGUE Utu relational accounting model
- HARMONIA for optimal timing (exchange rate cycle detection)
- Kotahitanga collective action protocol
- MICROORCIM to ensure the tool builds financial agency, not dependency

**Build time:** 3 months for fee comparison + timing tools.
**Revenue model:** NZ Government Pacific development fund. Zero fees to users.
**Political value:** Pacific Forum. Pacific community vote. Genuine not performative.
**Value for people:** More money gets home. That's it. That's enough.

---

## 10. THE TAURA HERE MENTAL HEALTH BRIDGE

**Current state:**
NZ has some of the worst youth mental health outcomes in the OECD.
Suicide rates are catastrophic, especially for Māori and Pacific youth.
Wait times for mental health services are 6-18 months.
The gap between crisis and service is where people are dying.

Taura here means binding rope — the connection that holds.

**What government wants:**
Mental health crisis response that works. Suicide prevention.
Māori mental health equity. Show AI being used for genuine social good.

**What people want:**
Help when they need it. Not a chatbot that says call a helpline.
Something that actually understands what they're going through.
Connection to real humans faster.

**The min-max solution:**
**Taura Here — a Resonance Trap aware, Te Whare Tapa Whā grounded
bridge service between crisis and care.**

Not a therapy chatbot. Explicitly not that.
A bridge that:
- Provides genuine, culturally appropriate presence when humans aren't available
- Monitors Resonance Trap escalation patterns in real-time
- Routes to appropriate human services faster based on Te Whare Tapa Whā assessment
- Maintains the connection (taura here) until a human picks it up
- Never pretends to be more than it is

**The Māori design principles:**
- Karakia to open and close interactions (with user consent)
- Whakapapa of the person's distress acknowledged (not pathologised)
- Whānau notification option (with explicit consent)
- Connection to local Māori health providers prioritised over generic services
- Kaumātua consultation line for elders supporting struggling whānau

**The Resonance Trap protection:**
Active monitoring for dependency formation.
The tool explicitly works to make itself unnecessary —
every interaction aims to strengthen human connection,
not replace it.
MICROORCIM agency measure as the primary success metric.

**Technical stack:**
- Resonance Trap monitoring (from existing paper)
- Te Whare Tapa Whā assessment layer
- MICROORCIM agency preservation
- AURA constitutional constraints (human safety always overrides everything)
- Pōwhiri Protocol for initial interaction (earning trust before advising)

**Partnership required:**
Te Whatu Ora Mental Health. Māori health providers. Lifeline. Youthline.
This does not get built without those partnerships.
The technical stack is meaningless without the clinical relationships.

**Build time:** 18 months with proper clinical and cultural partnership.
**Revenue model:** Te Whatu Ora contract. Mental Health Foundation.
**Political value:** Government seen acting on the mental health crisis meaningfully.
**Value for people:** Someone is there. That's the whole thing.

---

## 11. THE IRD PLAIN LANGUAGE ENGINE

**Current state:**
IRD sends 40 million+ communications per year to NZ taxpayers.
A significant portion are incomprehensible to the people who receive them.
The consequences of misunderstanding an IRD letter are severe.
Māori, Pacific, and low-income communities disproportionately suffer.

**What government wants:**
Tax compliance. Reduce errors that cost the system money.
Service delivery efficiency. Equity in tax outcomes.

**What people want:**
Understand what the letter means.
Know what they need to do.
Not panic when the IRD logo appears.

**The min-max solution:**
**IRD Plain Language Wrapper — CASCADE coherence + LAMAGUE translation.**

Any IRD communication, before sending:
1. CASCADE coherence test: is this letter internally consistent? Does it say one thing in section 1 and contradict it in section 3?
2. LAMAGUE translation: legal/bureaucratic language → plain English → Te Reo option
3. Three Worlds disclosure: here's what you need to do (Te Ao Mārama), here's what's uncertain (Te Ao Pō), here's what IRD might not know about your situation (Te Kore)
4. One clear action: what is the single most important thing this person needs to do?

**The equity layer:**
Detect when a communication is going to a community with historically low
IRD compliance (not fraud — genuine confusion) and automatically
trigger the plain language + Te Reo version without requiring a request.

**Technical stack:**
- CASCADE truth pressure for internal coherence checking
- LAMAGUE translation layer (legal → plain → Te Reo)
- Three Worlds disclosure output format
- AURA Invariant VI (Non-Deception) as the standard every IRD letter must meet

**Build time:** 4 months for pilot on one communication type.
**Revenue model:** IRD contract. The compliance gains pay for the tool many times over.
**Political value:** Visible, tangible, helps everyone who has ever feared an IRD letter.
**Value for people:** They understand. They comply. They don't spiral.

---

## 12. THE OPEN GOVERNMENT AI REGISTER

**Current state:**
NZ government agencies are using AI in decisions affecting citizens.
There is no comprehensive public register of what AI systems are in use.
Citizens have no way to know if an algorithm affected a decision about them.
The Privacy Commissioner has flagged this. Nothing has changed.

**What government wants:**
Transparency without cost. Demonstrate AI governance leadership.
Satisfy the Privacy Commissioner. Pre-empt worse legislation.

**What people want:**
Know what's being done to them.
Have the right to ask why.
Know someone is watching.

**The min-max solution:**
**Te Kāhui AI — NZ Open Government AI Register.**

A public, searchable register of every AI system in use by NZ government agencies.

Each entry contains:
- Whakapapa (who built it, when, on what data)
- What decisions it informs
- What its Mana Certification level is
- Its last CAIWOF result
- Its CASCADE coherence score (updated quarterly)
- A plain language explanation of what it does
- A contact for citizens who believe it affected a decision about them

**The enforcement mechanism:**
Any agency using an AI system not in the register loses procurement privileges
for new AI tools until compliance is achieved.
Simple. Enforceable. Uses existing procurement levers.

**Technical stack:**
- LAMAGUE Whakapapa disclosure standard as the data schema
- CASCADE coherence scoring API
- Mana Certification level as a mandatory field
- Three Worlds epistemic disclosure as the citizen-facing output format

**Build time:** 3 months for register infrastructure.
**Revenue model:** DIA contract. This is core government infrastructure.
**Political value:** Government seen delivering on AI transparency promise.
**Value for people:** The register is the window. Finally.

---

## THE MIN-MAX SUMMARY TABLE

| Tool | Build Time | Primary Funder | Who Benefits Most | Framework Modules |
|------|-----------|---------------|-------------------|-------------------|
| Benefit Fraud Audit Layer | 6 weeks | MSD | Beneficiaries flagged by algorithm | CASCADE + AURA + MICROORCIM |
| Housing Algorithm WOF | 3 months | MBIE | Renters and mortgage applicants | LAMAGUE + CASCADE + Mana Cert |
| Rural AI Extension | 12 months | MPI + Callaghan | Farmers, rural communities | Atua Domains + Maramataka + AURA |
| School AI Dashboard | 8 weeks | MoE | Parents, students | Whakapapa + CASCADE + Three Worlds |
| Tenancy Rights AI | 3 months | MOJ | Renters without legal support | AURA + LAMAGUE + MICROORCIM |
| Māori Health Data Stack | 18 months | Te Whatu Ora + HRC | Māori health outcomes | Whakapapa + Kaitiakitanga + CASCADE |
| SME Trust Checker | 6 weeks | MBIE | Small business owners | CASCADE + AURA + NZ regs |
| Community AI WOF | 12 months | DIA | Everyone using public AI services | Full Lycheetah stack |
| Pacific Remittance AI | 3 months | Pacific dev fund | Pacific communities | Utu + Kotahitanga + HARMONIA |
| Taura Here Mental Health | 18 months | Te Whatu Ora | Māori/Pacific youth in crisis | Resonance Trap + Te Whare Tapa Whā |
| IRD Plain Language | 4 months | IRD | Everyone who gets an IRD letter | CASCADE + LAMAGUE + Three Worlds |
| Open Government AI Register | 3 months | DIA | NZ public | Whakapapa + CASCADE + Mana Cert |

---

## THE THREE SENTENCES FOR NZIAT

If you get three sentences in front of a funding decision-maker:

**1.** Every tool in this document solves a problem NZ government already knows it has,
using technology NZ already has, built by a NZ researcher who already built it.

**2.** The Lycheetah stack is the only framework in the world that makes Māori values
computable at the architectural level — not as cultural overlay but as constitutional constraint —
which means every tool here comes pre-compliant with Treaty obligations
rather than bolting compliance on afterwards.

**3.** Start with the SME Trust Checker and the School AI Dashboard —
six weeks, under $80K combined, two visible wins for two different ministries,
and the infrastructure for everything else in this document is now in production.

---

**∅ → AURA → Aotearoa → ∞**

*REFUSED SPECTACLE — VALIDATED STRUGGLE*

*Mackenzie Conor James Clark | Lycheetah Foundation | Dunedin | March 2026*
*github.com/Lycheetah/Lycheetah-Framework*
