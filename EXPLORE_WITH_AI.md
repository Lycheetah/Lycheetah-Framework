# Exploring This Repository With AI

This repository was built in sustained co-creation with AI systems.
It is designed to be explored the same way.

You do not need to read all of it. You need to have a conversation with an AI *about* it.
This file tells you how.

---

## Why AI Navigation Works Here

The framework spans nine formal systems, three epistemic traditions, 30+ Python
implementations, and entry points for everyone from policy-makers to chaos magicians
to structural engineers. No single reader has background in all of it.

An AI can meet you where you are. It can:
- Explain the mathematics at the level you need
- Translate between the alchemical language and formal logic
- Run through the code with you step by step
- Tell you which parts are proven and which are still open questions
- Answer the question you actually have, not the one the documentation assumed you'd have

The repository is the material. The AI is the guide. You are the one deciding how deep to go.

---

## How to Give an AI Access

There are three ways, in order of power:

### 1. Best — AI with GitHub Repository Access

Some AI tools can read this repository directly. When they can, they have access to every
file, can navigate between them, and can answer questions about the actual current state
of the code and documentation.

**Claude (claude.ai or Claude Code)** with GitHub MCP integration can read the full repo.
Give it this starting point:

```
I want to explore the Lycheetah Framework repository at
github.com/Lycheetah/Lycheetah-Framework.

I'm [describe yourself: your background, what brought you here, what you're curious about].

Start by reading the README.md, then help me find the right entry point for my background.
Don't summarize everything — ask me what I want to understand first.
```

**Gemini** with Google Search grounding can access public GitHub repos similarly.

**Perplexity** can read public GitHub repos and link to specific files.

---

### 2. Good — Upload Files Directly

Download specific folders from the repo and upload them to an AI with file access.
**Claude.ai** and **ChatGPT** (with file upload) both work well.

Which folder to download depends on what you want:

| Your interest | Download this |
|---|---|
| The mathematics | `11_MATHEMATICAL_FOUNDATIONS/` |
| The Python code | `12_IMPLEMENTATIONS/` |
| AI governance / NZ policy | `23_NZ_AI_GOVERNANCE/` |
| Your specific door (see below) | `14_MYSTERY_SCHOOL/` |
| The CASCADE knowledge engine | `01_CASCADE/` + `papers/` |
| The AURA constitutional framework | `02_AURA/` |

Then say: *"I've uploaded [folder]. Help me understand [specific thing]."*

---

### 3. Works — Copy and Paste Specific Files

Any AI can work with pasted content. For a focused exploration, copy the contents
of one or two files and paste them into the conversation.

Good starting files to paste:
- `README.md` — the full map
- `00_Sovereign_Index.md` — the master navigation
- The specific door file for your background (see below)

---

## Start From Your Background

Find your description. Copy the starter prompt. Paste it into your AI of choice
after giving it access to the repository.

---

**You're a software engineer**

```
I'm a software engineer. Start with the engineer's door:
14_MYSTERY_SCHOOL/THE_ENGINEERS_DOOR.md

Then show me the CASCADE engine code in 12_IMPLEMENTATIONS/core/cascade_engine.py.
Explain what it actually does, how the truth pressure metric Π works,
and what problem it solves. Show me a minimal working example.
```

---

**You work in AI governance or policy**

```
I work in AI governance / policy. I want to understand what's actually implementable
from this framework right now — not the theoretical vision, the concrete standards.

Start with 23_NZ_AI_GOVERNANCE/NZIAT_PRESENTATION.md
Then look at the four standards: WOF, Three Worlds Disclosure, Whakapapa Disclosure,
Matariki Audit.

Tell me which one would be easiest to pilot in a real government context and why.
```

---

**You're a researcher in machine learning or AI**

```
I'm an ML researcher. I want to understand the CASCADE framework technically.

Read papers/CASCADE_ARXIV.tex and give me:
1. The core contribution in one sentence
2. The formal claim and how it's proved (Theorem 4.1)
3. Where the experimental validation is strongest and where it's weakest
4. How this compares to EWC and other continual learning approaches
5. What's missing that I'd want to see before taking this seriously

Be honest. I want the gaps as much as the strengths.
```

---

**You're curious but don't have a technical background**

```
I'm curious about this framework but I don't have a maths or coding background.

Start with the README.md and then help me understand:
- What problem is this framework actually solving?
- What does "truth pressure" mean in plain language?
- Why does the golden ratio keep appearing in it?
- What's the Failure Museum and why does it exist?

Don't use technical jargon unless you explain it. Ask me if something isn't clear.
```

---

**You work in Māori communities, iwi, or indigenous governance**

```
Start with 14_MYSTERY_SCHOOL/THE_INDIGENOUS_DOOR.md

I want to understand how this framework relates to tikanga, kaitiakitanga,
and Māori data sovereignty. What is the framework claiming, what is it NOT claiming,
and what would genuine partnership with iwi look like in developing this further?

Be direct about where the framework is making offers versus where it's making assumptions.
```

---

**You're a philosopher or work in epistemology**

```
I'm a philosopher. Start with 14_MYSTERY_SCHOOL/THE_PHILOSOPHERS_DOOR.md

Then look at 01_CASCADE/ and help me understand:
- How does CASCADE's truth pressure Π relate to AGM belief revision theory?
- What's the relationship to Kuhn's paradigm shifts? Is this a formalization?
- Where does the framework's claim to "coherence preservation" fit against
  non-monotonic logic traditions (Reiter, Nute, McCarthy)?

I want genuine philosophical engagement, not a sales pitch.
```

---

**You're here because you're in pain or looking for something**

```
Read 14_MYSTERY_SCHOOL/THE_THRESHOLD.md

Don't explain the framework to me. Just hold space for where I am.
```

---

**You build AI systems and want to integrate this**

```
I build AI systems. Start with the For Developers section in README.md,
then read 12_IMPLEMENTATIONS/applications/LYCHEETAH_GUARD_SETUP.md.

Tell me:
1. What is the Lycheetah Guard MCP extension and what does it actually do?
2. What's the fastest way to add constitutional alignment checking to an existing pipeline?
3. What's the most genuinely useful thing in the codebase for a production AI system?

Skip the philosophy for now. Code and architecture first.
```

---

**You want to understand everything**

```
Start with 00_Sovereign_Index.md — the master navigation.

I want a full tour. Begin with the nine frameworks in order (CASCADE through HARMONIA),
give me a one-paragraph summary of each, flag which claims are proven [ACTIVE],
which are structural but incomplete [SCAFFOLD], and which are open conjectures [CONJECTURE].

Then tell me what the honest frontier of this work is — what would need to happen
for this to be taken seriously by mainstream AI research?
```

---

## Depth Levels

You can engage with this framework at four depths. The AI can meet you at any of them.

**Surface — understand the concept (30 minutes)**
Ask the AI to explain one framework in plain language. Don't look at any code.
Goal: you can explain CASCADE (or AURA, or TRIAD) to someone else in a conversation.

**Working — run the code (2–4 hours)**
Clone the repo. Run `pip install -e .` and `pytest tests/ -v`.
Ask the AI to walk you through one core implementation file and what the tests prove.
Goal: you can modify a parameter and understand what changes.

**Deep — engage with the mathematics (1–2 days)**
Read `11_MATHEMATICAL_FOUNDATIONS/` with the AI as a guide.
Work through Theorem 4.1 (coherence non-decrease). Understand the proof.
Goal: you can identify where the mathematics is solid and where it has gaps.

**Contributing — build something new (ongoing)**
Read `CONTRIBUTING.md`. Ask the AI to help you find the gap you're best placed to fill.
Experiment 5 (cascade predictability) in `papers/EXPERIMENTAL_ROADMAP_2026_2028.md`
needs no external dependencies and can begin immediately.
Goal: you add something to the framework that didn't exist before.

---

## What to Trust and What to Question

The framework uses three honest status labels on its own claims:

**[ACTIVE]** — proven, computable, independently verifiable. The tests run.
**[SCAFFOLD]** — the structure is correct, implementation is incomplete or partially tested.
**[CONJECTURE]** — mathematically motivated, not yet formally resolved.

When an AI is guiding you through this repo, it should be using these labels.
If it presents everything as proven, push back. Ask: *"What's the claim status here?
Is this [ACTIVE] or [SCAFFOLD]?"*

The [Failure Museum](FAILURE_MUSEUM.md) documents every significant mistake
the framework made and what changed. Reading it is a good calibration exercise.
A framework that hides its failures is performing confidence. This one earns it.

---

## A Note on the Language

This framework uses alchemical terminology (Nigredo, Citrinitas, Rubedo, Solve et Coagula)
alongside formal mathematics (Banach fixed-point theorem, Lyapunov functions, AGM postulates).

This is not decoration. The alchemical language encodes something the mathematical language
doesn't capture easily — the directionality of transformation, the difference between
heat that destroys and heat that refines.

But if the language doesn't work for you, tell the AI: *"Skip the alchemy, give me
the formal structure."* Everything in the framework has a formal version.
The alchemy is the map. The mathematics is the territory.

---

## The Best Question to Start With

If you're not sure where to begin, give an AI access to this repository and ask:

```
What is the single most interesting and honest thing in this repository?
Not the most ambitious. The most honest — the thing that is genuinely true
and genuinely useful, where the gap between what is claimed and what is proven
is smallest. Start there.
```

That question will tell you more about the framework than any summary.

---

*This repository is free. The framework is open. The conversation is the curriculum.*
*github.com/Lycheetah/Lycheetah-Framework*
