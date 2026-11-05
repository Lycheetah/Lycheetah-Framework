# On-device, NZ-first AI — research memo, 6 November 2026

For Mackenzie Conor James Clark. Web research done in one session; every claim names its source
and its strength. **Vendor** = reported by the model's maker or a seller; **secondary** = news,
blog or aggregator; **official** = government or the body itself. Nothing here was measured by us
except where it says MEASURED. Check the official pages before quoting any of this to an investor.

## 1. How good are small models now?

| Finding | Strength | Source |
|---|---|---|
| The best open-weight models trail the closed frontier by about **4 months** on Epoch's Capabilities Index (since Jan 2026); earlier readings ~3 months | secondary, from a reputable tracker | [Epoch AI — open vs closed gap](https://epoch.ai/data-insights/open-closed-eci-gap), [earlier reading](https://epoch.ai/data-insights/open-weights-vs-closed-weights-models) |
| Epoch's benchmarking **underrepresents small open models**, so no reliable "small model vs frontier" lag figure exists | secondary | [Epoch AI](https://epoch.ai/data-insights/open-closed-eci-gap) |
| Most-recommended 3–4B models: **Qwen3.5 4B** (model card: MMLU-Pro 79.1, GPQA Diamond 76.2; ~8 GB RAM machines), **Phi-4-mini 3.8B** (~3 GB VRAM, MIT, MMLU 67.3), **SmolLM3-3B** (fully open data and pipeline, Apache 2.0) | vendor numbers via secondary guides | [promptquorum](https://www.promptquorum.com/local-llms/small-local-llm-models), [tinyweights](https://tinyweights.dev/posts/best-small-language-models-2026/), [BentoML](https://www.bentoml.com/blog/the-best-open-source-small-language-models), [vdf.ai](https://vdf.ai/blog/best-small-language-models/) |
| Smaller options: Gemma 4 E4B (~5 GB at 4-bit, audio input), Llama 3.2 1B for constrained devices | secondary | [labellerr](https://www.labellerr.com/blog/best-small-language-models-under-10b-parameters/), [Intuz](https://www.intuz.com/blog/best-small-language-models/) |

**Correction to what I told Mac in chat:** I said a phone-size model is "roughly where the frontier
was a couple of years earlier." The tracker evidence is that the *best* open models are months
behind, and that small models are not well measured at all. The honest position: **nobody has a
trustworthy "% of frontier" number for small models on everyday tasks.** That is exactly what our
pre-registered benchmark (`on_device_assistant/BENCHMARK_PREREG.md`) would produce, and why it is
worth running.

## 2. Will it run on a phone?

| Finding | Strength | Source |
|---|---|---|
| Llama 3.2 3B (4-bit weights): ~23.5 tokens/s on a Snapdragon 8 Elite phone, ~18.4 on a Snapdragon X Elite laptop, with Qualcomm's own runtime | vendor | [Qualcomm on Hugging Face](https://huggingface.co/qualcomm/Llama-v3.2-3B-Chat), [Qualcomm AI Hub](https://aihub.qualcomm.com/models/llama_v3_2_3b_instruct_ssd) |
| 3B at Q4 with llama.cpp on iPhone 15/16 Pro: ~2.1 GB memory idle, 2.8 GB peak; ~11% battery per 30 min continuous generation | vendor (app maker) | [PocketLLM](https://pocketllm-landing.pages.dev/blog/llama-3-2-iphone-benchmarks/) |
| llama.cpp is the common research backend for on-device benchmarking | secondary (arXiv) | [arXiv 2505.15030](https://arxiv.org/html/2505.15030v5) |

**Reading:** a 3B model is usable on a recent flagship phone (roughly 10–25 tokens/s is a fair
expectation, inferred, not measured), with real battery cost. Laptops are the better first target.

## 3. The New Zealand picture

| Finding | Strength | Source |
|---|---|---|
| The government's AI strategy (MBIE, July 2025) remains the framework; **no AI-specific law**; parties differ on an AI office ahead of the 2026 election | secondary | [newswire, Oct 2026](https://newswire.co.nz/2026/10/ai-policy-new-zealand-election-2026-data-centres-regulation/) |
| Government is chasing **$25–35 billion** of data-centre investment; the Greens want a one-year pause on new AI data-centre consents | secondary | [The Spinoff](https://thespinoff.co.nz/business/06-07-2026/nz-inc-is-going-all-in-on-ai-data-centres), [RNZ](https://www.rnz.co.nz/news/politics/796938/urgent-need-for-rules-and-protections-on-data-centres-greens-say) |
| Industry strategy: NZ as a "trusted, sustainable" data-centre and AI hub; onshore-data deals (HPE × 2degrees, Jan 2026) | industry / vendor | [Reseller News](https://www.reseller.co.nz/article/4209424/industry-led-strategy-calls-for-nz-to-become-trusted-sustainable-data-centre-and-ai-hub.html), [HPE](https://www.hpe.com/us/en/newsroom/press-release/2026/01/hpe-and-2degrees-collaborate-to-accelerate-ai-innovation-and-strengthen-data-sovereignty-in-new-zealand.html) |
| Where NZ business data actually goes when it uses AI is a live public question | secondary | [newswire, Aug 2026](https://newswire.co.nz/2026/08/new-zealand-ai-data-centres-business-data-leaves-country/) |
| Full-stack "sovereign AI" doesn't add up for NZ; the real question is which layers to own | opinion | [Chandima, Substack](https://chandima.substack.com/p/why-sovereign-ai-does-not-easily) |
| Privacy Commissioner guidance (2023): AI use of personal information is regulated under the Privacy Act 2020; privacy impact assessment before deployment; non-binding | official, via law-firm summaries | [Buddle Findlay](https://www.buddlefindlay.com/insights/privacy-commissioner-guidance-on-use-of-ai/), [MinterEllison](https://minterellison.co.nz/insights/privacy-in-the-age-of-intelligent-machines-opc-s-new-guidance-on-safeguarding-privacy-when-using-ge), [Baker McKenzie](https://resourcehub.bakermckenzie.com/en/resources/global-data-and-cyber-handbook/asia-pacific/new-zealand/topics/artificial-intelligence-profiling-and-automated-decision-making) |
| Algorithm Charter (2020): voluntary, public sector only | secondary | [Taylor Fry](https://taylorfry.com.au/articles/lessons-learned-one-year-on-algorithm-charter-for-aotearoa-new-zealand/) |

**Reading:** the national bet is on *big onshore data centres*, and it is contested on power,
water and rules. An on-device product is the complementary bet: it needs no data centre at all for
the core, and answers "where does my data go?" with "nowhere." Lycheetah's layer covers the part
neither data centres nor models do: proof of what the AI did, and a human who actually approved it.

## 4. Māori data: the precedent to learn from

| Finding | Strength | Source |
|---|---|---|
| Te Hiku Media's Kaitiakitanga License: guardianship rather than ownership; bars surveillance, discrimination and tracking; contributors keep ownership; models trained only on consented data | academic + organisational | [Kukutai et al. 2024 (Waikato)](https://www.waikato.ac.nz/assets/Uploads/Research/Research-institutes-centres-and-groups/Institutes/TKRI/Publications/Science_Kukutai2024_How_Indigenous_Communities_Protecting_Data.pdf), [The Spinoff](https://thespinoff.co.nz/kaupapa/22-11-2025/reclaiming-the-future-maori-voices-leading-in-the-age-of-ai-and-quantum-tech) |
| Te Hiku's te reo speech recognition reported at 92% accuracy; 300+ hours of labelled speech gathered in 10 days | vendor / conference | [NVIDIA](https://blogs.nvidia.com/blog/te-hiku-media-maori-speech-ai/), [ITU](https://www.itu.int/hub/2022/08/ai-indigenous-languages-maori-te-reo/) |

**Reading:** te reo capability is Te Hiku's and its communities' to give or withhold. The right
move is to ask them what they would want from an on-device assistant, not to build a te reo model.
The licence's enforceability has not been tested in court as far as these sources say.

## 5. Who else is here

Jan (open source, Apache 2.0, ~5.3M downloads, MCP support), LM Studio (beginner GUI, proprietary)
and Ollama (developer tool) already run models locally on desktops — secondary sources:
[DEV](https://dev.to/agdex_ai/best-local-llm-tools-in-2026-ollama-vs-lm-studio-vs-jan-vs-koboldcpp-run-ai-privately-3apc),
[frankx](https://frankx.ai/blog/ollama-vs-lm-studio-vs-jan-2026). **Running a model locally is
solved and free.** None of these, as described, offers approvals that provably bind what runs,
receipts, or an NZ-anchored witness. That gap is the product; the model runtime is a dependency.
A Lycheetah assistant should use Ollama or llama.cpp underneath, not compete with them.

## 6. What this changes in the plan

1. Don't train a model. Pick an open 3–4B model under a permissive licence (check Qwen's licence
   terms; SmolLM3 and Phi-4-mini are Apache 2.0 / MIT per the guides above).
2. Build on an existing local runtime; spend all effort on the trust layer and the experience.
3. The investable number is ours to measure: blind-rated "% of frontier on everyday NZ tasks".
4. Laptop first, phone second (battery and heat are real).
5. Talk to Te Hiku Media before any te reo feature exists.
