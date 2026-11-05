# Lycheetah AI for New Zealand business — writing, summaries, local logistics

**PROPOSED · 2026-11-06 · for Mackenzie Conor James Clark.** Plain-language plan. Research sources
are linked; anything marked *verify* came from a secondary source.

## Why these three

Mac's call, and the evidence backs it:

- **Businesses are using AI but don't govern it.** Small-business AI use is somewhere between 36%
  ([MYOB, via IT Brief](https://itbrief.co.nz/story/new-zealand-smes-widen-ai-adoption-gap-myob-finds))
  and 59% ([Prospa, via IT Brief](https://itbrief.co.nz/story/new-zealand-small-businesses-adopt-ai-as-hold-outs-shrink)),
  depending on the survey. Only **13%** have an AI policy ([EMA, via Scoop](https://m.scoop.co.nz/stories/BU2607/S00119/ai-adoption-surges-among-smes-but-businesses-risk-falling-behind-on-workforce-readiness-ema-survey-finds.htm)),
  and roughly four in ten non-adopters cite a lack of in-house expertise. A tool that enforces approvals
  and keeps receipts gives a small business something close to an AI policy without writing one.
- **No official number yet:** Stats NZ's survey that asks about AI had not published 2026 results as of
  October ([newswire](https://newswire.co.nz/2026/07/most-new-zealand-businesses-now-use-ai-so-why-has-productivity-gone-backwards/)).
  An honest, measured benchmark from us would be one of very few NZ-specific numbers.

| Job | What the small model does | What Lycheetah adds | Biggest risk |
|---|---|---|---|
| **Writing** | drafts replies, quotes, ads, notices in a Kiwi tone | nothing is sent without approval; drafts stay on the device | sounding generic; fixed by the business's own examples |
| **Summaries** | condenses contracts, notices, meetings, complaints | sensitive documents never leave the laptop; receipts of what was summarised | **dropping or inventing a key fact**, so we measure exactly that |
| **Local logistics** | talks to the owner, explains options, drafts customer messages | **the gateway is the product here**: bookings and notifications only with approval, no double-booking after a timeout | the model is bad at optimising routes, so it calls proper tools rather than guessing |

## How each one works

**Writing.** Prompt with the business's tone examples (a handful of real emails, with consent).
Tune later only if the benchmark shows a gap.

**Summaries.** Retrieval over the business's own documents on the device. Every summary ends with
"what I might have missed," and every figure links back to its source line. The benchmark plants
five key facts per document and counts what survives.

**Local logistics.** The model never plans routes itself. It calls tools:
- **Road closures:** NZTA's road-events API is open data with no account required, under NZTA's terms
  ([data.govt.nz](https://catalogue.data.govt.nz/dataset/road-events2),
  [NZTA](https://nzta2.cwp.govt.nz/traffic-and-travel-information/use-our-data)). It covers notable
  verified events on the state highway network only, not every local road.
- **Routes:** a proper routing engine, not the language model.
- **Addresses:** LINZ address data is the obvious source (*verify licence and API*; not confirmed today).
- **Actions** such as booking a courier or texting a customer always go through the gateway.

Rural delivery is a real pain point: NZ Post stopped Saturday rural delivery
([Parcel & Postal Technology](https://www.parcelandpostaltechnologyinternational.com/news/delivery/nz-post-stops-saturday-newspaper-and-parcel-delivery-for-rural-addresses.html)),
and remote rural addresses can take four to five business days through a rural agent
([NZ Couriers](https://blog.nzcouriers.co.nz/?p=3164)). An assistant that tells a rural business the
truth about timing, and rebooks around a closure with the owner's yes, solves something people feel.

## Build order

1. **Summaries + writing (weeks).** Same skeleton, plus document retrieval. Lowest risk, fastest demo.
2. **Run the verticals benchmark** (`BENCHMARK_PREREG_VERTICALS_2026-11-06.md`) and publish the result.
3. **Logistics (months).** Add the road-events tool on recorded data first, then live, then one real
   courier integration behind the gateway.
4. **Pilot:** three to five NZ small businesses, with consent, for four weeks, at no charge.

## Applying now: funding (verify everything at funds.business.govt.nz)

- Callaghan Innovation was disestablished and its grants moved to MBIE's Innovation Services
  ([guide](https://whatfounderswant.com/expert-editions/how-to-efficiently-unlock-nz-government-support-a-step-by-step-execution-guide/part-5-grant-by-grant-execution-tips),
  [Wikipedia](https://en.wikipedia.org/wiki/Callaghan_Innovation)) — *verify the current status*.
- **New to R&D Grant:** co-funding for a first significant R&D project, reportedly up to $400K
  ([Callaghan announcement](https://www.callaghaninnovation.govt.nz/stories/the-refreshed-more-accessible-new-to-r-and-d-grant-is-now-open/),
  [guide](https://businessloans.org.nz/guides/new-to-r-and-d-grant/)) — *verify terms; it is co-funding,
  so you put money in too.*
- **R&D Tax Incentive** still exists (*verify the rate*); the **R&D Career / Experience Grants** help
  hire a graduate ([directory](https://whatfounderswant.com/government-support-for-startups-smes-in-new-zealand-2025)).
- Grants go to companies. **Set up the company properly first**, with a lawyer and an accountant;
  that is also what protects you if your boss invests.

## What "leading" honestly means here

Being first in New Zealand to **publish a measured, pre-registered benchmark of on-device AI on real
NZ business jobs, with a trust layer that provably stops unapproved actions** is achievable this year.
That's a real claim to leadership, and it's checkable. Everything bigger comes from customers.
