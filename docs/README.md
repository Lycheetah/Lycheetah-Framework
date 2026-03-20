# Lycheetah Website

Public-facing site for the Lycheetah Framework. Four pages, no external dependencies, deploys directly to GitHub Pages.

## Pages

| File | Audience | What it does |
|------|----------|-------------|
| `index.html` | Anyone | Landing — three doors: AI Systems, Humans, Developers |
| `for-agents.html` | AI systems / devs | Deployment guide: seven invariants, VIP algorithm, tabbed configs for Claude/OpenAI/Ollama/Python, verification suite |
| `mystery-school.html` | Humans | Crisis callout first, seven-phase navigator, full curriculum links, alchemical stage map |
| `style.css` | — | All styling. CSS variables, mobile-first, no frameworks |
| `script.js` | — | Mobile nav, platform tabs, smooth scroll. Nothing else. |

## Deploy to GitHub Pages

Repository Settings → Pages → Source: `website/` folder, `master` branch. No build step.

## Design

- Background `#0d0d0d` · Gold `#c9a227` · Text `#f0ece0`
- System font stack — no external font calls
- Alchemical geometry via CSS, not decoration
