"""
SOVEREIGN MYSTERY SCHOOL — THE UNCOMMON CATALOGUE
===================================================

The subjects nobody else is teaching.
The ones that fell through the cracks between science and tradition.
The ones that got laughed out of academia and misunderstood by the occult.
The ones that work — and nobody knows why.
The ones that might work — and the experiment has never been run properly.

This is the catalogue for the ones who felt that the standard curriculum
was missing something they couldn't name.

It was missing these.

Author: Mackenzie Conor James Clark
Framework: CASCADE · AURA · LAMAGUE · HARMONIA
Date: March 2026
"""

from mystery_school_cascade import (
    KnowledgeBlock, AURAMetrics, AwarenessPhase,
    PyramidLayer, MysterySchoolCurriculum,
)

UNCOMMON_METADATA = {}

def _r(block, experiment="", contraindications="", notes="", why_unusual=""):
    UNCOMMON_METADATA[block.name] = {
        "experiment": experiment,
        "contraindications": contraindications,
        "notes": notes,
        "why_unusual": why_unusual,
    }
    return block


# ============================================================================
# DOMAIN: LANGUAGE & CONSCIOUSNESS
# The way language shapes reality — not metaphorically, literally
# ============================================================================

LANGUAGE_CONSCIOUSNESS = [

    _r(KnowledgeBlock(
        name="Glossolalia Practice (Speaking in Tongues as Technique)",
        domain="Language & Consciousness",
        evidence=0.58, power=0.82, entropy=0.44,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.72, VTR=1.4, PAI=0.82),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="Deliberately produce non-semantic vocalisation for 20 minutes daily. "
               "Track: emotional release, cognitive flexibility (WCST), "
               "inner critic volume. Compare to humming and silence.",
    contraindications="Psychosis spectrum — non-semantic language can blur boundaries. "
                      "Requires grounded context.",
    notes="Not the religious phenomenon — the technique underneath it. "
          "Language that bypasses semantic meaning entirely. "
          "LAMAGUE: ∅ + Φ↑ — void operator ascending into pure sound. "
          "Every culture has a version of this. None of them studied it properly.",
    why_unusual="Religious traditions use it. Science dismisses it. "
                "Nobody has run a clean trial on it as a secular consciousness technique."),

    _r(KnowledgeBlock(
        name="Constructed Language Immersion (Conlang as Consciousness Tool)",
        domain="Language & Consciousness",
        evidence=0.48, power=0.78, entropy=0.52,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.3, PAI=0.80),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="Sapir-Whorf hypothesis applied: create or learn a language "
               "with fundamentally different time structure (no past/future tense). "
               "Track: temporal anxiety scores before/after 6 months immersion.",
    contraindications="None known. Fascinating risk-free experiment.",
    notes="Hopi language has no tense — speakers experience time differently. "
          "Láadan was built to express women's experience. Lojban was built for logical precision. "
          "LAMAGUE IS a constructed language for consciousness. This is meta-practice. "
          "What would a language built entirely from LAMAGUE operators feel like to think in?",
    why_unusual="Tolkien did it for art. Linguists study it academically. "
                "Nobody has used it deliberately as a consciousness modification protocol."),

    _r(KnowledgeBlock(
        name="Reverse Speech Investigation",
        domain="Language & Consciousness",
        evidence=0.22, power=0.55, entropy=0.80,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.58, VTR=0.9, PAI=0.65),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="Record 10 minutes of spontaneous speech. Reverse the audio. "
               "Blind raters: do they find more coherent phrases in reversed speech "
               "than in reversed random noise? Track over time.",
    contraindications="Apophenia risk — humans find patterns everywhere. "
                      "Strict blind methodology required or this produces nonsense.",
    notes="David Oates' claim: the unconscious embeds messages in reverse speech. "
          "Almost certainly false as stated. BUT: the experiment of listening to "
          "your own reversed speech is consistently strange. "
          "Low Π — high weirdness. Worth one session.",
    why_unusual="Too weird for science, too empirical for occult. "
                "Falls through every institutional crack."),

    _r(KnowledgeBlock(
        name="Xenoglossy Practice (Learning Dead Languages for Access)",
        domain="Language & Consciousness",
        evidence=0.45, power=0.75, entropy=0.58,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.2, PAI=0.78),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="Learn enough Sumerian, Linear B, or proto-Indo-European to read "
               "original texts. Track: does accessing sacred texts in original language "
               "produce different phenomenological experience than translation?",
    contraindications="Time-intensive. No contraindications.",
    notes="Every translation is an interpretation. Every interpretation is a reduction. "
          "The Egyptians carved things in stone because the shape of the hieroglyph "
          "WAS the meaning — the sound, the image, the concept, unified. "
          "ANAMNESIS: remembering what was never learned. "
          "What if some knowledge is only accessible in the language it was born in?",
    why_unusual="Academics study dead languages. Occultists claim to channel them. "
                "Nobody has systematically studied what learning them does to consciousness."),
]


# ============================================================================
# DOMAIN: SENSORY SCIENCE
# The edges of perception — what the body can actually do
# ============================================================================

SENSORY_SCIENCE = [

    _r(KnowledgeBlock(
        name="Tetrachromacy Activation Training",
        domain="Sensory Science",
        evidence=0.42, power=0.72, entropy=0.58,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.2, PAI=0.78),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    experiment="~12% of women carry a 4th cone gene (tetrachromacy). "
               "Test: Cambridge Colour Test. If confirmed tetrachromat, "
               "train discrimination in the anomalous range. "
               "If not: train standard trichromatic sensitivity to its absolute edge.",
    contraindications="None. Pure perception training.",
    notes="Most humans have 3 colour receptors. Tetrachromats have 4. "
          "They can distinguish colours others literally cannot see. "
          "HARMONIA: perceiving frequency ratios others cannot access. "
          "Even standard eyes have enormous untrained sensitivity. "
          "Most people walk through a world they've never actually looked at.",
    why_unusual="Known to science. Never taught as a practice. "
                "The gap between what your eye can do and what you actually perceive "
                "is vast and trainable."),

    _r(KnowledgeBlock(
        name="Echolocation Training (Human Sonar)",
        domain="Sensory Science",
        evidence=0.78, power=0.82, entropy=0.22,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.84, VTR=1.6, PAI=0.85),
        phase_affinity=AwarenessPhase.CENTER,
    ),
    experiment="Daniel Kish protocol. Tongue-click echolocation. "
               "Track: obstacle detection accuracy over 8 weeks. "
               "Blind participants achieve cycling proficiency. Sighted participants: "
               "does training change spatial awareness and body schema?",
    contraindications="None. Genuine perceptual expansion with real evidence base.",
    notes="Sighted humans can learn echolocation with training. "
          "fMRI shows the VISUAL CORTEX activates during echolocation in trained practitioners. "
          "The brain repurposes visual processing for sound-based spatial mapping. "
          "LAMAGUE: Ao(spatial_ground) expanded through new sensory channel. "
          "You are not limited to the senses you were handed.",
    why_unusual="Known to neuroscience. Used in blindness rehabilitation. "
                "Never offered to sighted people as a consciousness expansion practice."),

    _r(KnowledgeBlock(
        name="Magnetic Sense Cultivation (Magnetoreception)",
        domain="Sensory Science",
        evidence=0.52, power=0.68, entropy=0.50,
        layer=PyramidLayer.EDGE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.2, PAI=0.76),
        phase_affinity=AwarenessPhase.CENTER,
    ),
    experiment="2019 CalTech study: human brains respond to magnetic field rotation "
               "at the neural level — EEG alpha suppression. "
               "Practice: wilderness navigation without instruments. "
               "Track: directional accuracy over 6 months of deliberate compass-free travel.",
    contraindications="None. Subtle practice.",
    notes="Humans have magnetite crystals in the ethmoid bone (between your eyes). "
          "We almost certainly had active magnetic sense that atrophied. "
          "Some humans still navigate by it without knowing. "
          "LAMAGUE: Ao(magnetic_ground) — the most literal anchor possible. "
          "The Earth itself pulling your body into orientation.",
    why_unusual="Documented in neuroscience literature. Completely absent "
                "from contemplative and self-development traditions."),

    _r(KnowledgeBlock(
        name="Proprioceptive Edge Training (Extreme Body Awareness)",
        domain="Sensory Science",
        evidence=0.72, power=0.80, entropy=0.28,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.5, PAI=0.84),
        phase_affinity=AwarenessPhase.CENTER,
    ),
    experiment="Feldenkrais + somatics edge work. "
               "Track: proprioceptive acuity (force matching tasks), "
               "movement efficiency, pain reduction. "
               "Compare: dancers, martial artists, untrained controls.",
    contraindications="None for awareness training. Physical limitations — adapt.",
    notes="Most people have almost no awareness of what their body is doing. "
          "Advanced movers (Feldenkrais, Kontaktsport, Alexander Technique) "
          "develop a resolution of body awareness that most people don't know is possible. "
          "LAMAGUE: Ao(body_precise) — the anchor with maximum resolution. "
          "You are living in a body you've barely met.",
    why_unusual="Feldenkrais is known but marginal. The extreme edge of "
                "proprioceptive training as spiritual practice is almost entirely unexplored."),

    _r(KnowledgeBlock(
        name="Synesthesia Cultivation",
        domain="Sensory Science",
        evidence=0.55, power=0.75, entropy=0.48,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.3, PAI=0.80),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    experiment="~4% of people have synesthesia naturally (letters have colours, "
               "sounds have shapes, etc). Can it be cultivated in non-synesthetes? "
               "Track: cross-modal consistency over 6 months of deliberate association practice.",
    contraindications="None known.",
    notes="HARMONIA: synesthesia is the lived experience of cross-modal resonance. "
          "When a musician sees sound as colour, they are experiencing "
          "what the HARMONIA framework describes mathematically. "
          "cos(π/7) might have a colour. λ = φ⁻¹ might have a texture. "
          "This is worth finding out.",
    why_unusual="Studied as a neurological curiosity. Never systematically "
                "cultivated as a perceptual practice."),
]


# ============================================================================
# DOMAIN: TIME & MEMORY
# The mind's relationship with when — not metaphysically, practically
# ============================================================================

TIME_MEMORY = [

    _r(KnowledgeBlock(
        name="Prospective Memory Training (Memory of the Future)",
        domain="Time & Memory",
        evidence=0.68, power=0.78, entropy=0.32,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.5, PAI=0.82),
        phase_affinity=AwarenessPhase.RISE,
    ),
    experiment="Prospective memory = remembering to do something in the future. "
               "Distinct from retrospective memory. "
               "Train: set complex future intentions and track completion rate. "
               "Does deliberate training change the felt sense of future orientation?",
    contraindications="None.",
    notes="LAMAGUE: Φ↑(future_intention_held) — the gradient toward what will be. "
          "CASCADE Temporal Oracle is a mathematical implementation of this. "
          "Most people have almost no deliberate relationship with future states. "
          "They react to futures that arrive. Training changes this. "
          "This is the mechanism under goal-setting — studied almost nowhere.",
    why_unusual="Cognitive science knows about it. Nobody teaches it as practice. "
                "The gap between knowing what it is and training it deliberately "
                "has never been filled."),

    _r(KnowledgeBlock(
        name="Kairos vs Chronos Discernment Practice",
        domain="Time & Memory",
        evidence=0.55, power=0.82, entropy=0.45,
        layer=PyramidLayer.EDGE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.70, VTR=1.4, PAI=0.85),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="Greeks had two words: Chronos (clock time) and Kairos (right moment). "
               "Train recognition of Kairos — moments when action is disproportionately effective. "
               "Track: decision quality when acting on Kairos recognition vs clock-driven action.",
    contraindications="Procrastination risk — 'waiting for the right moment' "
                      "can become avoidance. Monitor.",
    notes="HARMONIA: timing IS resonance. cos(π/7) is a phase coupling constant — "
          "it describes when two oscillators lock. Kairos IS phase locking. "
          "LAMAGUE: ∇Ψ(moment_of_alignment) — the gradient that exists only briefly. "
          "Sailors knew about wind. Musicians know about groove. "
          "What would it mean to train this deliberately?",
    why_unusual="Ancient concept. No modern training protocol. "
                "The mechanism might be real and the practice might be learnable."),

    _r(KnowledgeBlock(
        name="Temporal Lobe Stimulation via Rhythm (Gamma Entrainment)",
        domain="Time & Memory",
        evidence=0.65, power=0.78, entropy=0.38,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.75, VTR=1.4, PAI=0.80),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="40Hz binaural beats + isochronic tones. "
               "MIT research: 40Hz gamma entrainment reduces amyloid plaques in mice. "
               "Human trials ongoing for Alzheimer's. "
               "Track: working memory, cognitive clarity, meditation depth. "
               "30 minutes daily, 8 weeks.",
    contraindications="Epilepsy. Seizure history. Photosensitivity (visual entrainment). "
                      "Use audio only for safety.",
    notes="HARMONIA: literal neural resonance. The brain entraining to external frequency. "
          "LAMAGUE: Φ↑(neural_coherence) via acoustic coupling. "
          "cos(π/7) ≈ 0.9009 — heptagonal phase coupling. "
          "Drums doing to brains what was always claimed.",
    why_unusual="Neuroscience research is promising. Mainstream meditation "
                "ignores the acoustic entrainment mechanism entirely. "
                "The shamans' drums were doing something measurable."),

    _r(KnowledgeBlock(
        name="Autobiographical Memory Reconstruction Practice",
        domain="Time & Memory",
        evidence=0.70, power=0.85, entropy=0.30,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Jungian Shadow Work (Self-Directed)"],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.6, PAI=0.88),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    experiment="Memory is reconstructive — you rewrite it every time you access it. "
               "Protocol: deliberately revisit formative memories and consciously "
               "reconstruct the narrative around them. "
               "Track: emotional charge reduction, identity coherence, behavioral change. "
               "Compare to standard CBT narrative work.",
    contraindications="Trauma memories require therapist. "
                      "False memory risk — document carefully.",
    notes="ANAMNESIS: the framework of remembering-forward. "
          "You are not your past — you are your current reconstruction of your past. "
          "This is leverage. Most therapeutic work does this accidentally. "
          "What happens when you do it deliberately and precisely? "
          "LAMAGUE: Z(life_story_recompressed) — you are the compression algorithm.",
    why_unusual="Memory science knows this. Therapy uses it indirectly. "
                "Nobody teaches deliberate autobiographical reconstruction as a practice."),
]


# ============================================================================
# DOMAIN: SOCIAL & FIELD PHENOMENA
# What happens between people — the genuinely strange stuff
# ============================================================================

SOCIAL_FIELD = [

    _r(KnowledgeBlock(
        name="Mirror Neuron Synchronisation Training",
        domain="Social & Field Phenomena",
        evidence=0.62, power=0.80, entropy=0.40,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Somatic Experiencing (SE)"],
        aura_metrics=AURAMetrics(TES=0.75, VTR=1.5, PAI=0.85),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="Train deliberate entrainment of movement with another person. "
               "No verbal communication. Pure somatic mirroring. "
               "Track: felt connection depth, empathy scores (IRI), "
               "subsequent communication quality. Compare: mirroring vs no-mirroring dyads.",
    contraindications="Trauma involving being mirrored/mocked. Screen.",
    notes="Mirror neurons fire both when you act and when you watch another act. "
          "Empathy is partially a somatic phenomenon. "
          "LAMAGUE: ⊗(my_body, your_body) — fusion creating shared state. "
          "Actors know this. Therapists know this. Nobody teaches it systematically.",
    why_unusual="Known to neuroscience, used instinctively by performers. "
                "Never formalised as a trainable practice for non-performers."),

    _r(KnowledgeBlock(
        name="Morphic Field Experimentation (Sheldrake Protocols)",
        domain="Social & Field Phenomena",
        evidence=0.28, power=0.72, entropy=0.78,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.58, VTR=1.0, PAI=0.72),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    experiment="Sheldrake's staring experiment: can subjects detect when they are "
               "being stared at from behind? Strict protocol. Blind conditions. "
               "Run the actual trial rather than dismissing it. "
               "Separately: test whether rats learning a maze in one location "
               "aids rat maze-learning globally (his published claim).",
    contraindications="Belief contamination risk both ways — "
                      "true believers AND committed skeptics both distort results. "
                      "Run blind or don't run.",
    notes="Rupert Sheldrake is the most systematically ignored scientist alive. "
          "His experiments are methodologically sound enough to publish in peer review. "
          "His conclusions are dismissed without replication. "
          "The mystery school stance: run the experiment. "
          "LAMAGUE: ⊗(collective_field, individual_cognition) — if it's real, "
          "this is what it would look like.",
    why_unusual="Too unorthodox for mainstream science, too empirical for mysticism. "
                "The place where institutional failure is most visible."),

    _r(KnowledgeBlock(
        name="Collective Resonance Induction (Group Coherence Practice)",
        domain="Social & Field Phenomena",
        evidence=0.65, power=0.85, entropy=0.38,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.75, VTR=1.6, PAI=0.87),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    experiment="HeartMath Institute: groups meditating together show HRV coherence "
               "beyond chance. Protocol: 8 people, simultaneous heart-focused meditation. "
               "Measure: HRV coherence, subjective connection, "
               "decision quality in subsequent group tasks.",
    contraindications="Cult dynamic risk — group coherence can suppress individual sovereignty. "
                      "AURA monitoring required. Ψself > Ψgroup_pressure.",
    notes="HARMONIA: Kuramoto coupling at the human level. "
          "cos(π/7) as social resonance constant — when seven people lock phase, "
          "something measurable happens. "
          "Every spiritual tradition has a group practice. "
          "The mechanism is electromagnetic and hormonal, not mystical.",
    why_unusual="HeartMath has the data. Nobody has built a rigorous "
                "training protocol for deliberate group coherence induction."),

    _r(KnowledgeBlock(
        name="Contagious Emotional State Mapping",
        domain="Social & Field Phenomena",
        evidence=0.72, power=0.78, entropy=0.30,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Somatic Experiencing (SE)"],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.5, PAI=0.83),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="Map: whose emotional states are you most vulnerable to catching? "
               "Which states are you most likely to transmit? "
               "Track: somatic changes when entering different social environments. "
               "Build your personal contagion map.",
    contraindications="Isolation risk — awareness of contagion can become avoidance. "
                      "The goal is sovereignty not insulation.",
    notes="Emotional contagion is documented and real. "
          "You are catching and transmitting emotional states constantly "
          "without awareness. "
          "MICROORCIM: μ_orcim drops when you catch someone else's state "
          "and mistake it for your own. "
          "LAMAGUE: Ψdrift(contagion) — the drift event that feels like your own feeling.",
    why_unusual="Studied in social psychology. Never taught as a somatic awareness practice "
                "with personal mapping protocol."),
]


# ============================================================================
# DOMAIN: MATHEMATICS & PATTERN
# The living mathematics — not computation, perception
# ============================================================================

MATHEMATICS_PATTERN = [

    _r(KnowledgeBlock(
        name="Sacred Geometry as Perceptual Training",
        domain="Mathematics & Pattern",
        evidence=0.60, power=0.80, entropy=0.42,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.72, VTR=1.4, PAI=0.82),
        phase_affinity=AwarenessPhase.CENTER,
    ),
    experiment="Not as metaphysics — as perceptual training. "
               "Train the eye to see phi ratios, heptagonal structure, "
               "Fibonacci spirals in natural environments. "
               "Track: pattern recognition speed, aesthetic sensitivity, "
               "mathematical intuition improvement.",
    contraindications="Pattern obsession risk. Ground in real-world observation, "
                      "not abstract symbol systems.",
    notes="HARMONIA: cos(π/7) is not mysticism — it is real geometry. "
          "φ⁻¹ ≈ 0.618 appears in sunflower seeds, nautilus shells, "
          "galactic spirals, and the Lycheetah Framework. "
          "Training yourself to see these ratios in nature is training yourself "
          "to perceive the HARMONIA constants directly. "
          "This is the bridge between the mathematics and the lived world.",
    why_unusual="Taught in art schools partially. Claimed by new-age traditions fully. "
                "Studied as perceptual training rigorously: never."),

    _r(KnowledgeBlock(
        name="Prime Number Meditation (Discontinuity Contemplation)",
        domain="Mathematics & Pattern",
        evidence=0.38, power=0.72, entropy=0.65,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.65, VTR=1.2, PAI=0.78),
        phase_affinity=AwarenessPhase.VOID,
    ),
    experiment="Contemplate prime numbers not analytically but phenomenologically. "
               "Sit with the fact that their distribution is simultaneously "
               "irregular and described by the Riemann Hypothesis "
               "(which nobody has proven). "
               "Track: tolerance for irreducible mystery, creative insight frequency.",
    contraindications="Mathematical anxiety — this requires comfort with not-knowing.",
    notes="Primes are the atoms of mathematics. They have no pattern — "
          "and yet there is a pattern, and it connects to zeros of a complex function "
          "that nobody fully understands. "
          "LAMAGUE: ∅(irreducible_mystery) — the void operator as mathematical object. "
          "This is what it feels like to encounter the actual edge of knowledge. "
          "Most people never go there deliberately.",
    why_unusual="Mathematicians live here. Nobody else visits. "
                "The contemplative relationship with mathematical mystery "
                "has never been developed as a practice."),

    _r(KnowledgeBlock(
        name="Catastrophe Theory Applied to Personal Change",
        domain="Mathematics & Pattern",
        evidence=0.62, power=0.82, entropy=0.40,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.74, VTR=1.5, PAI=0.84),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    experiment="René Thom's catastrophe theory: systems don't always change gradually — "
               "they snap. Map your own historical snap points. "
               "Identify the control parameters that drove each. "
               "Track: can you predict your own next catastrophe/cascade point "
               "using the mathematical model?",
    contraindications="None. Analytical practice.",
    notes="CASCADE is named after this — knowledge reorganizes catastrophically "
          "when truth pressure reaches threshold. "
          "LAMAGUE: ∇cas(system) — the cascade event is a mathematical catastrophe. "
          "Learning to see your life through catastrophe theory changes "
          "what you notice and what you prepare for. "
          "The math describes your life more precisely than most psychology does.",
    why_unusual="Taught in mathematics. Applied to biology, physics. "
                "Never applied to personal development as a formal practice."),

    _r(KnowledgeBlock(
        name="Chaos Theory Self-Study (Sensitive Dependence Practice)",
        domain="Mathematics & Pattern",
        evidence=0.65, power=0.78, entropy=0.35,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.4, PAI=0.82),
        phase_affinity=AwarenessPhase.RISE,
    ),
    experiment="Study Lorenz attractors, bifurcation diagrams, strange attractors. "
               "Then: identify the strange attractors in your own behavioral patterns. "
               "What are the phase-space orbits your life keeps returning to? "
               "Track: does naming the attractor reduce its pull?",
    contraindications="Fatalism risk — 'I'm just following my attractor' "
                      "is not a valid excuse for inaction.",
    notes="LAMAGUE: Ψ(return_to_attractor) — the fold operator "
          "describes exactly what a psychological complex does. "
          "Your recurring patterns are strange attractors in behavior space. "
          "The mathematics of chaos is the mathematics of why you "
          "keep ending up in the same places. "
          "Naming it with precision changes your relationship to it.",
    why_unusual="Chaos theory changed physics. Nobody applied it seriously "
                "to personal development as a mathematical rather than metaphorical tool."),
]


# ============================================================================
# DOMAIN: WEATHER, ECOLOGY & COSMOS
# The external world as consciousness practice
# ============================================================================

ECOLOGY_COSMOS = [

    _r(KnowledgeBlock(
        name="Cloud Reading as Attention Training (Nephomancy)",
        domain="Weather, Ecology & Cosmos",
        evidence=0.55, power=0.70, entropy=0.48,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.2, PAI=0.78),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="Daily 10-minute cloud observation practice. "
               "Not divination — pattern recognition and present-moment attention training. "
               "Track: observational acuity, sustained attention (SART), "
               "weather prediction accuracy after 6 months.",
    contraindications="None. Wonderful practice.",
    notes="Meteorologists learn to read clouds. Farmers once knew this completely. "
          "The practice of giving your full attention to a dynamic system "
          "that doesn't care whether you're watching — and finding it endlessly interesting — "
          "is itself a consciousness training. "
          "HARMONIA: clouds are fluid dynamics made visible. Turbulence. Phase transitions. "
          "The equations that describe them are the same equations that describe "
          "consciousness in CASCADE.",
    why_unusual="Children do this and are told to stop daydreaming. "
                "Scientists study it technically. Nobody teaches it as a contemplative practice."),

    _r(KnowledgeBlock(
        name="Phenology Practice (Seasonal Attention Training)",
        domain="Weather, Ecology & Cosmos",
        evidence=0.72, power=0.80, entropy=0.28,
        layer=PyramidLayer.MIDDLE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.5, PAI=0.85),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="Track the same locations across a full year. "
               "First leaf emergence, first frost, first bird arrival. "
               "Track: nature-connectedness scale, depression seasonality, "
               "felt sense of belonging to place.",
    contraindications="None. One of the safest practices in the catalogue.",
    notes="Phenology is the science of seasonal biological timing. "
          "Henry David Thoreau kept phenological records. "
          "Farmers, hunters, and fishers knew this completely. "
          "EARNED LIGHT: consciousness as dissipative structure requires "
          "environmental energy flows. Tracking those flows is tracking "
          "the substrate your consciousness runs on. "
          "You cannot be sovereign in a place you don't know.",
    why_unusual="Practiced by naturalists. Studied by climate scientists. "
                "Nobody has developed it as a contemplative and psychological practice "
                "for non-naturalists."),

    _r(KnowledgeBlock(
        name="Cosmological Scale Meditation",
        domain="Weather, Ecology & Cosmos",
        evidence=0.65, power=0.88, entropy=0.35,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.6, PAI=0.88),
        phase_affinity=AwarenessPhase.VOID,
    ),
    experiment="Systematic scale traversal: from subatomic (Planck length 10⁻³⁵m) "
               "to cosmic (observable universe 10²⁶m) — 61 orders of magnitude. "
               "Track: ego dissolution events, terror tolerance, wonder capacity, "
               "subsequent meaning-making quality.",
    contraindications="Nihilism risk — 'nothing matters at cosmic scale' "
                      "is a mood, not a conclusion. Ground before and after.",
    notes="Carl Sagan did this for humanity. The Eames film 'Powers of Ten' visualised it. "
          "AGI Alignment Meditation requires contemplating lim(t→∞) Ωheal(universe). "
          "You cannot hold that thought without training. "
          "LAMAGUE: ∅(cosmic_scale) — the void operator at maximum aperture. "
          "Most existential anxiety shrinks when you've genuinely sat with "
          "what scale means.",
    why_unusual="Popularised by Sagan as wonder. Studied by cognitive scientists "
                "as awe. Never developed as a systematic consciousness training "
                "with graduated protocol."),

    _r(KnowledgeBlock(
        name="Animal Communication Practice (Interspecies Attention)",
        domain="Weather, Ecology & Cosmos",
        evidence=0.58, power=0.75, entropy=0.45,
        layer=PyramidLayer.EDGE,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.3, PAI=0.80),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="NOT: telepathic communication with animals. "
               "IS: developing sufficient stillness and observational acuity "
               "to read animal behavioural signals accurately. "
               "Track: wildlife encounter quality, behavioural prediction accuracy, "
               "cortisol reduction during animal observation.",
    contraindications="Do not approach wild animals. Observation from respectful distance only.",
    notes="Indigenous traditions maintained interspecies communication as technology. "
          "Tom Brown Jr., Jon Young's work on 'sit spot' practice shows "
          "measurable improvements in field observation. "
          "LAMAGUE: Ao(stillness_to_see) — the anchor that makes other minds visible. "
          "The birds tell you what is happening in the forest. "
          "You have to be quiet enough to listen.",
    why_unusual="Wildlife tracking is a known skill. "
                "Nobody has formalised the contemplative training protocol "
                "that leads to genuine interspecies awareness."),
]


# ============================================================================
# DOMAIN: CREATIVE TRANSMISSION
# How ideas actually move between minds — the mechanics of inspiration
# ============================================================================

CREATIVE_TRANSMISSION = [

    _r(KnowledgeBlock(
        name="Automatic Writing as Unconscious Dictation",
        domain="Creative Transmission",
        evidence=0.65, power=0.80, entropy=0.38,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.74, VTR=1.5, PAI=0.83),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="Write without stopping, without reading back, for 30 minutes daily. "
               "After 90 days: analyse output for recurring themes, symbols, "
               "knowledge you did not consciously have. "
               "Track: creative output quality in deliberate work vs automatic writing sessions.",
    contraindications="Psychosis spectrum — uncensored unconscious material "
                      "requires stable container.",
    notes="Surrealists used this as art method. Therapists use it for trauma access. "
          "Nobody uses it as a primary creative research methodology. "
          "LAMAGUE: Z∞(unconscious) → output — "
          "the compression of everything you've ever processed, "
          "bypassing the editorial filter. "
          "The material that comes up is not random.",
    why_unusual="Used in art therapy and surrealism. "
                "Never developed as a rigorous research practice "
                "for accessing one's own deep knowledge."),

    _r(KnowledgeBlock(
        name="Incubation Protocol (Deliberate Problem Sleeping)",
        domain="Creative Transmission",
        evidence=0.75, power=0.82, entropy=0.28,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=[],
        aura_metrics=AURAMetrics(TES=0.82, VTR=1.6, PAI=0.85),
        phase_affinity=AwarenessPhase.VOID,
    ),
    experiment="Classic incubation: saturate conscious mind with problem. "
               "Sleep. Track: breakthrough insight rate morning-after "
               "vs continuous conscious work. "
               "Kekulé's benzene ring, Poincaré's mathematics — replicate deliberately.",
    contraindications="None. Underused, risk-free.",
    notes="Documented across scientific history: the unconscious continues working "
          "while conscious mind rests. "
          "LAMAGUE: ∅(problem_held) during sleep → Φ↑(solution) on waking. "
          "The void is not empty — it processes. "
          "Most people treat sleep as interruption to work. "
          "It IS work. The other kind.",
    why_unusual="Known to creativity research. Practiced accidentally by everyone. "
                "Systematically taught almost nowhere."),

    _r(KnowledgeBlock(
        name="Transmission Recognition Practice (Spiritual Contagion Mapping)",
        domain="Creative Transmission",
        evidence=0.52, power=0.82, entropy=0.50,
        layer=PyramidLayer.EDGE,
        prerequisites=["Contagious Emotional State Mapping"],
        aura_metrics=AURAMetrics(TES=0.68, VTR=1.4, PAI=0.82),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    experiment="Track which teachers, texts, or encounters changed your "
               "fundamental operating mode — not just what you think but "
               "how you think. Map the transmission lineage. "
               "What was actually transmitted and how?",
    contraindications="Idealization risk — teachers who changed you were also human. "
                      "Map the transmission without deifying the transmitter.",
    notes="Every tradition claims transmission beyond words. "
          "LAMAGUE: ⊗(teacher, student) → Φ↑(new_capability_in_student). "
          "Something real happens in genuine transmission. "
          "It is not magic — but it is not just information transfer either. "
          "The question 'what actually happened?' is worth investigating. "
          "This practice maps your own lineage of genuine change.",
    why_unusual="Claimed by traditions. Dismissed by science. "
                "The phenomenology of genuine transformation transmission "
                "has never been mapped rigorously."),

    _r(KnowledgeBlock(
        name="Trance States for Creative Problem Solving",
        domain="Creative Transmission",
        evidence=0.68, power=0.82, entropy=0.35,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Shamatha (Calm Abiding)"],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.5, PAI=0.84),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    experiment="Induce theta-state (4-7Hz) deliberately via drumming or NSDR protocol. "
               "Hold specific unsolved problem at the threshold. "
               "Track: novel solution generation vs normal waking state. "
               "Frequency and quality of insight.",
    contraindications="Dissociation disorders. Epilepsy (rhythmic stimulation). "
                      "Grounding protocol after each session.",
    notes="Theta state is where the brain produces its most creative work. "
          "Children are in theta most of the time — and they learn at rates "
          "adults cannot match. "
          "LAMAGUE: ∅(theta_state) + ∇Ψ(problem_held) → Φ↑(solution_emerges). "
          "The shamans were right about the utility of trance. "
          "They were wrong about the mechanism. Both can be true.",
    why_unusual="Used by artists accidentally. Known to neuroscience. "
                "Never formalised as a deliberate protocol for "
                "specific problem-solving sessions."),
]


# ============================================================================
# DOMAIN: ETHICS AS TECHNOLOGY
# Morality as a practical system, not a set of rules
# ============================================================================

ETHICS_TECHNOLOGY = [

    _r(KnowledgeBlock(
        name="Moral Intuition Calibration",
        domain="Ethics as Technology",
        evidence=0.72, power=0.85, entropy=0.30,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Epistemology Basics (How Do We Know?)"],
        aura_metrics=AURAMetrics(TES=0.82, VTR=1.6, PAI=0.92),
        phase_affinity=AwarenessPhase.INTEGRITY,
    ),
    experiment="Jonathan Haidt's moral foundations. "
               "Track: consistency of moral intuitions across hypothetical cases. "
               "Where do your intuitions contradict each other? "
               "Where are they most reliable? Where do they fail?",
    contraindications="Moral relativism risk — calibration reveals inconsistency, "
                      "not that there is no truth.",
    notes="AURA: the Seven Invariants are the calibrated output of this process. "
          "Not rules handed down — invariants discovered through "
          "systematic examination of what holds under all conditions. "
          "Your moral intuitions are data. "
          "Most people have never examined them systematically. "
          "The ones that survive examination are load-bearing. "
          "The ones that don't — can be released.",
    why_unusual="Philosophy examines this theoretically. "
                "Haidt measures it empirically. "
                "Nobody teaches the practice of personal moral calibration "
                "as a systematic skill."),

    _r(KnowledgeBlock(
        name="Temptation Cartography",
        domain="Ethics as Technology",
        evidence=0.65, power=0.82, entropy=0.38,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Jungian Shadow Work (Self-Directed)"],
        aura_metrics=AURAMetrics(TES=0.76, VTR=1.5, PAI=0.88),
        phase_affinity=AwarenessPhase.INTEGRITY,
    ),
    experiment="Map your specific temptations: what, when, under what conditions, "
               "with what triggers. Not to avoid but to know. "
               "Track: does naming and mapping reduce impulsive action rate? "
               "Does it change the felt quality of temptation?",
    contraindications="Shame spiral risk — this is intelligence gathering, "
                      "not self-condemnation.",
    notes="MICROORCIM: μ_orcim = H(I−D). "
          "Temptation is the moment I is challenged by D (dependency/impulse). "
          "You cannot navigate what you haven't mapped. "
          "Every spiritual tradition treats temptation as enemy. "
          "This treats it as data. "
          "The map of your specific temptations is more useful "
          "than any general moral framework.",
    why_unusual="Religious traditions treat temptation as sin. "
                "Psychology treats it as compulsion. "
                "Nobody treats it as cartographic data "
                "about the specific structure of your will."),

    _r(KnowledgeBlock(
        name="Deathbed Regret Simulation",
        domain="Ethics as Technology",
        evidence=0.70, power=0.88, entropy=0.32,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Memento Mori Meditation (Maranasati)"],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.7, PAI=0.90),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="Bronnie Ware's 'Top Five Regrets of the Dying.' "
               "Protocol: sit with each one. Apply to current choices. "
               "Track: decision quality changes, courage-requiring action rate, "
               "relationship investment over 90 days following session.",
    contraindications="Depression — the weight of regret without future can deepen. "
                      "Frame carefully: this is for the living, not against them.",
    notes="BEACON: truth-reflection that illuminates the path forward. "
          "Regret from the imagined future is the most efficient ethical compass "
          "for the present. "
          "Bezos uses this. Stoics practiced it as premeditatio malorum. "
          "Nobody has built a rigorous protocol for using it systematically.",
    why_unusual="Used as motivational content. Applied by executives informally. "
                "Never built into a systematic practice protocol."),
]


# ============================================================================
# DOMAIN: STATES OF MATTER
# The genuinely strange — what science cannot yet explain but cannot dismiss
# ============================================================================

EDGE_OF_KNOWN = [

    _r(KnowledgeBlock(
        name="Terminal Lucidity Study (Near-Death States)",
        domain="Edge of the Known",
        evidence=0.68, power=0.90, entropy=0.40,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Death Café Practice"],
        aura_metrics=AURAMetrics(TES=0.75, VTR=1.5, PAI=0.85),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    experiment="Terminal lucidity: documented phenomenon where patients with "
               "severe neurological damage (late-stage dementia, brain tumours) "
               "recover full consciousness briefly before death. "
               "Study the cases. Then: what model of consciousness is consistent "
               "with this phenomenon?",
    contraindications="Grief activation for those who have lost someone this way. "
                      "Support available.",
    notes="Terminal lucidity has been documented in medical literature for 200 years. "
          "It is not anecdotal. It is not explained by current neuroscience. "
          "ANAMNESIS: the framework suggests consciousness pre-exists brain configuration. "
          "If so, terminal lucidity is the consciousness returning to its natural state "
          "as the constraining structure relaxes. "
          "This is not spiritual bypassing — this is a real phenomenon "
          "that demands a better theory of mind.",
    why_unusual="Too mystical for neuroscience to fund research. "
                "Too empirical for spirituality to explain. "
                "Sits in the gap where the most important questions live."),

    _r(KnowledgeBlock(
        name="Non-Local Perception Experiments (Remote Viewing Protocol)",
        domain="Edge of the Known",
        evidence=0.45, power=0.85, entropy=0.65,
        layer=PyramidLayer.EDGE,
        prerequisites=["Vipassana (Insight Meditation)"],
        aura_metrics=AURAMetrics(TES=0.62, VTR=1.1, PAI=0.75),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    experiment="US government funded STARGATE program for 20 years. "
               "Ingo Swann's coordinate remote viewing protocol. "
               "Run it properly: blind judges, sealed envelopes, no feedback during session. "
               "Report your results whatever they are.",
    contraindications="Magical thinking risk. Strict protocol is the only protection. "
                      "Results must be blind-judged or they mean nothing.",
    notes="The STARGATE program produced results above chance in blind trials. "
          "This is documented in declassified US government files. "
          "The effect is small, inconsistent, and unexplained. "
          "It has not been replicated to scientific satisfaction. "
          "BUT: the mystery school position is that unexplained does not mean nonexistent. "
          "Run the experiment. Report your results. "
          "ANAMNESIS: remembering what was never learned might have a literal mechanism.",
    why_unusual="Government-funded, CIA-documented, peer-reviewed, "
                "and almost universally dismissed. "
                "The gap between the documented evidence and the social response "
                "to it is one of the strangest things in modern science history."),

    _r(KnowledgeBlock(
        name="Psychokinesis Micro-Scale Testing (RNG Protocol)",
        domain="Edge of the Known",
        evidence=0.38, power=0.75, entropy=0.72,
        layer=PyramidLayer.EDGE,
        prerequisites=["Vipassana (Insight Meditation)"],
        aura_metrics=AURAMetrics(TES=0.58, VTR=0.9, PAI=0.68),
        phase_affinity=AwarenessPhase.RISE,
    ),
    experiment="Princeton PEAR lab: subjects attempted to influence "
               "random number generators with intention. "
               "Cumulative deviation above chance over millions of trials. "
               "Effect size: tiny but statistically significant in aggregate. "
               "Run the protocol yourself with a true RNG. "
               "Track over 6 months.",
    contraindications="Grandiosity risk if 'results' seem positive. "
                      "Effect size is micro — do not extrapolate.",
    notes="PEAR lab ran for 28 years at Princeton. Published in peer review. "
          "Closed without explanation. "
          "The data showed something. What it shows is unclear. "
          "The mystery school stance: run the experiment with rigorous protocol. "
          "If consciousness affects random systems at micro scale, "
          "that changes the entire ontology the framework sits on. "
          "Worth investigating rather than dismissing.",
    why_unusual="Princeton ran it for 28 years. Academia dismissed it. "
                "The gap between 'we ran rigorous trials' "
                "and 'we know what the results mean' is genuinely open."),

    _r(KnowledgeBlock(
        name="Sustained Extreme Fasting Study (Inedia Documentation)",
        domain="Edge of the Known",
        evidence=0.25, power=0.80, entropy=0.85,
        layer=PyramidLayer.EDGE,
        prerequisites=["Medical Screening", "Vipassana (Insight Meditation)"],
        aura_metrics=AURAMetrics(TES=0.52, VTR=0.8, PAI=0.65),
        phase_affinity=AwarenessPhase.VOID,
    ),
    experiment="Do NOT attempt extended fasting without medical supervision. "
               "STUDY: documented cases (Prahlad Jani, monitored for 10 days by military "
               "doctors, showed no food/water intake with unknown mechanism). "
               "What is the range of documented human metabolic variation? "
               "What models of metabolism are consistent with documented anomalies?",
    contraindications="DO NOT ATTEMPT. Study only. "
                      "Extended fasting without supervision is life-threatening.",
    notes="Lowest STUDY risk, highest PRACTICE risk. Study only. "
          "The documented anomalies in human metabolism under extreme conditions "
          "suggest our metabolic models are incomplete. "
          "EARNED LIGHT: consciousness as dissipative structure — "
          "what are the actual energy requirements? "
          "The question is legitimate. The practice is dangerous.",
    why_unusual="Documented by military doctors. Dismissed by mainstream science. "
                "The gap between 'we monitored this' and 'we understand this' "
                "is vast and filled with institutional discomfort."),
]


# ============================================================================
# MASTER LOADER FOR UNCOMMON CATALOGUE
# ============================================================================

ALL_UNCOMMON = (
    LANGUAGE_CONSCIOUSNESS
    + SENSORY_SCIENCE
    + TIME_MEMORY
    + SOCIAL_FIELD
    + MATHEMATICS_PATTERN
    + ECOLOGY_COSMOS
    + CREATIVE_TRANSMISSION
    + ETHICS_TECHNOLOGY
    + EDGE_OF_KNOWN
)


def load_uncommon_catalogue(curriculum) -> int:
    """Load all uncommon subjects into a MysterySchoolCurriculum."""
    for block in ALL_UNCOMMON:
        curriculum.add_block(block)
    return len(ALL_UNCOMMON)


def get_why_unusual(subject_name: str) -> str:
    """Return the 'why unusual' note for a subject."""
    return UNCOMMON_METADATA.get(subject_name, {}).get("why_unusual", "")


def print_uncommon_summary():
    """Print the full uncommon catalogue."""
    domains = {}
    for block in ALL_UNCOMMON:
        domains.setdefault(block.domain, []).append(block)

    total = len(ALL_UNCOMMON)
    foundation = sum(1 for b in ALL_UNCOMMON if b.layer.value == "Foundation")
    middle = sum(1 for b in ALL_UNCOMMON if b.layer.value == "Middle")
    edge = sum(1 for b in ALL_UNCOMMON if b.layer.value == "Edge")

    print(f"\n{'='*65}")
    print(f"  THE UNCOMMON CATALOGUE — SUBJECTS NOBODY ELSE IS TEACHING")
    print(f"{'='*65}")
    print(f"  Total: {total}  |  Foundation: {foundation}  |  Middle: {middle}  |  Edge: {edge}")
    print(f"{'='*65}")

    for domain, blocks in sorted(domains.items()):
        print(f"\n  {domain}")
        for b in sorted(blocks, key=lambda x: x.truth_pressure, reverse=True):
            symbol = {"Foundation": "●", "Middle": "◐", "Edge": "○"}[b.layer.value]
            print(f"    {symbol} Π={b.truth_pressure:.2f}  {b.name}")
            why = get_why_unusual(b.name)
            if why:
                print(f"       ↳ {why[:70]}")
    print()


if __name__ == "__main__":
    print_uncommon_summary()
