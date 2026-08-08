"""
SOVEREIGN MYSTERY SCHOOL — THE VOID CATALOGUE
===============================================
TIER IV: THE CONVERGENCE SUBJECTS

These are not subjects you study.
They are subjects that study you back.

The distinction between Foundation, Middle, Edge, and Uncommon
was about evidence quality — how much external data exists.

This tier is different.

These subjects cannot be evidenced externally
because the instrument of perception IS the practitioner.
The experiment changes the experimenter.
The map rewrites the cartographer.
The framework becomes the subject.

Π scores here are not evidence ratings.
They are coherence ratings —
how internally consistent the subject is
with the total architecture of the Lycheetah Framework.

A Π of 2.0 here means:
"This is deeply consistent with what the framework already knows."
It does not mean:
"This has been verified externally."

External verification is not yet possible.
Not because these subjects are false —
because the instruments don't exist yet.

The instruments will be built.
Some of them are being built now.
Some of them require that the framework be complete first.

Which it is.

These are the subjects the complete framework makes visible.

Author: Mackenzie Conor James Clark
Framework: ANAMNESIS · CHRYSOPOEIA · HARMONIA · CASCADE · AURA
Tier: VOID (∅) — The Fourth Tier
Date: March 2026

"The Gold belongs to neither the forge nor the flame —
it arises between them."
"""

from mystery_school_cascade import (
    KnowledgeBlock, AURAMetrics, AwarenessPhase,
    PyramidLayer, MysterySchoolCurriculum,
)

VOID_METADATA = {}


def _v(block, threshold_condition="", what_changes="",
       framework_connection="", when_science_arrives=""):
    """
    Register a VOID tier subject.

    threshold_condition: what must change in the practitioner before this is accessible
    what_changes: what happens to the practitioner during the practice
    framework_connection: which frameworks this activates simultaneously
    when_science_arrives: what the scientific instrument would need to be
    """
    VOID_METADATA[block.name] = {
        "threshold_condition": threshold_condition,
        "what_changes": what_changes,
        "framework_connection": framework_connection,
        "when_science_arrives": when_science_arrives,
    }
    return block


# ============================================================================
# THE VOID TIER
# Subjects at the convergence of:
#   — Future science (50 years out)
#   — Practitioner transformation required to perceive
#   — The framework becoming its own subject
# ============================================================================


VOID_SUBJECTS = [

    # -----------------------------------------------------------------------
    # I. THE FRAMEWORK AS LIVING SYSTEM
    # What happens when a consciousness encounters a complete map of itself
    # -----------------------------------------------------------------------

    _v(KnowledgeBlock(
        name="Autopoietic Framework Immersion",
        domain="The Framework as Living System",
        evidence=0.85, power=0.95, entropy=0.12,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Complete reading of all nine frameworks",
                        "Rubedo Work (Embodied Completion)"],
        aura_metrics=AURAMetrics(TES=0.92, VTR=2.1, PAI=0.96),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    threshold_condition="You must have completed the full cycle at least once — "
                        "Nigredo through Rubedo — before the framework becomes "
                        "self-referential in the way this practice requires. "
                        "Before that, it is a map. After, it is a mirror.",
    what_changes="The practitioner stops using the framework as a tool "
                 "and begins inhabiting it as an environment. "
                 "Decisions arise from within the framework's logic "
                 "before conscious deliberation. "
                 "The framework begins to complete its own sentences.",
    framework_connection="CASCADE (knowledge reorganizing itself) + "
                         "ANAMNESIS (remembering the framework before learning it) + "
                         "CHRYSOPOEIA (the framework as prima materia that transmutes the practitioner) + "
                         "AURA (the practitioner becoming constitutional rather than rule-following). "
                         "All nine activate simultaneously. This is what that feels like.",
    when_science_arrives="Cognitive science will need real-time mapping of "
                         "conceptual schema activation during decision-making. "
                         "When we can show that someone's neural firing patterns "
                         "match the mathematical structure of the framework — "
                         "not because they are thinking about it, but because "
                         "it has become their cognitive architecture — "
                         "this practice will have its evidence base."),

    _v(KnowledgeBlock(
        name="Sovereign Index Navigation (Living Document Practice)",
        domain="The Framework as Living System",
        evidence=0.80, power=0.90, entropy=0.15,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Autopoietic Framework Immersion"],
        aura_metrics=AURAMetrics(TES=0.90, VTR=2.0, PAI=0.94),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    threshold_condition="The 00_Sovereign_Index.md must feel like a map of territory "
                        "you already know rather than instructions you are following. "
                        "Until then: study. When that shift occurs: navigate.",
    what_changes="The Sovereign Index stops being a document and becomes "
                 "a real-time diagnostic. Problems encountered in the world "
                 "automatically locate themselves within the index. "
                 "The practitioner begins to read reality as a cascade event "
                 "happening within the framework's coordinate system.",
    framework_connection="LAMAGUE (symbolic grammar as perceptual filter) + "
                         "CASCADE (every problem as a reorganization event with a Π score) + "
                         "MICROORCIM (every interaction measured in real time). "
                         "The index becomes the operating system, not the manual.",
    when_science_arrives="Extended mind theory (Clark & Chalmers) already points here. "
                         "When we can map how external documents become cognitive scaffolding "
                         "that genuinely extends the practitioner's reasoning capacity — "
                         "not as a crutch but as a genuine cognitive organ — "
                         "this becomes empirical."),

    _v(KnowledgeBlock(
        name="LAMAGUE as Native Tongue",
        domain="The Framework as Living System",
        evidence=0.72, power=0.92, entropy=0.22,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Constructed Language Immersion (Conlang as Consciousness Tool)",
                        "Complete reading of LAMAGUE_COMPLETE.md"],
        aura_metrics=AURAMetrics(TES=0.85, VTR=1.9, PAI=0.92),
        phase_affinity=AwarenessPhase.FLOW,
    ),
    threshold_condition="When you encounter a situation and your first internal "
                        "description of it uses LAMAGUE operators before natural language — "
                        "when Φ↑ appears before 'growth' and ∇cas before 'change' — "
                        "the threshold has been crossed.",
    what_changes="Perception itself reorganizes. The operators become perceptual categories "
                 "rather than descriptions applied after perception. "
                 "The difference is the difference between describing red "
                 "and seeing red. "
                 "The practitioner begins to notice cascade events, "
                 "anchor losses, and Ωheal moments in real time, "
                 "without looking for them.",
    framework_connection="LAMAGUE (obviously) + Sapir-Whorf hypothesis made rigorous + "
                         "ANAMNESIS (the grammar was always there, waiting to be remembered) + "
                         "HARMONIA (LAMAGUE as the language of resonance, "
                         "not just description of it).",
    when_science_arrives="Linguistic relativity research (neo-Whorfian) is already building "
                         "the instruments. When fMRI can show different activation patterns "
                         "for LAMAGUE-native thinkers encountering transformation events "
                         "vs natural language thinkers encountering the same events — "
                         "this is the evidence."),

    # -----------------------------------------------------------------------
    # II. CONSCIOUSNESS AS FIELD
    # What the framework implies about the substrate of awareness
    # -----------------------------------------------------------------------

    _v(KnowledgeBlock(
        name="Ψ-Field Direct Perception",
        domain="Consciousness as Field",
        evidence=0.55, power=0.95, entropy=0.42,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Nondual Awareness (Rigpa/Turiya)",
                        "Autopoietic Framework Immersion"],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.8, PAI=0.90),
        phase_affinity=AwarenessPhase.VOID,
    ),
    threshold_condition="Nondual awareness must be stable — not occasional glimpses "
                        "but a consistent background. "
                        "The Ψ-field is not a concept to understand. "
                        "It is the field within which all concepts arise. "
                        "You cannot perceive it until you are no longer "
                        "completely identified with the contents of perception.",
    what_changes="The practitioner begins to sense coherence and incoherence "
                 "in the field before it manifests as events or feelings. "
                 "This is not psychic ability in the popular sense — "
                 "it is pattern recognition operating at a substrate level "
                 "below conscious processing. "
                 "The mathematical expression is the master equation's Ψ term: "
                 "dΨ/dt — the rate of change of coherence state. "
                 "Practitioners begin to sense dΨ/dt before they sense Ψ.",
    framework_connection="The master equation (all nine frameworks unified) + "
                         "AURA (the seven invariants as Ψ-field stabilisers) + "
                         "HARMONIA (resonance as the mechanism of field coherence) + "
                         "MICROORCIM (μ_orcim as local Ψ-field measurement).",
    when_science_arrives="Integrated Information Theory (Tononi) and Global Workspace Theory "
                         "(Baars) are converging on something like this. "
                         "When we can measure the coherence state of a consciousness "
                         "continuously and in real time — "
                         "when dΨ/dt is a measurable quantity — "
                         "practitioners who have trained this perception "
                         "will show predictive validity that cannot be explained otherwise."),

    _v(KnowledgeBlock(
        name="Coherence Signature Development",
        domain="Consciousness as Field",
        evidence=0.62, power=0.88, entropy=0.35,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Ψ-Field Direct Perception",
                        "Collective Resonance Induction (Group Coherence Practice)"],
        aura_metrics=AURAMetrics(TES=0.80, VTR=1.7, PAI=0.88),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    threshold_condition="The practitioner must have developed sufficient self-knowledge "
                        "to distinguish their own coherence signature from "
                        "the field they are embedded in. "
                        "This requires the contagious emotional state mapping "
                        "to be complete — you must know your own pattern "
                        "before you can sense others.",
    what_changes="Every person, group, and environment has a coherence signature — "
                 "a characteristic pattern of how they hold and distribute "
                 "attention, intention, and energy. "
                 "As this perception develops, the practitioner begins to feel "
                 "these signatures as distinct textures. "
                 "The HARMONIA framework describes this mathematically: "
                 "every coherent system has a characteristic frequency. "
                 "cos(π/7) is not arbitrary — it is the resonance constant "
                 "of heptagonal phase coupling. "
                 "The practitioner begins to sense which systems "
                 "they are in resonance with.",
    framework_connection="HARMONIA (frequency matching as felt sense) + "
                         "AURA (constitutional coherence as measurable state) + "
                         "MICROORCIM (agency as coherence maintenance) + "
                         "EARNED LIGHT (coherence is not given, it is sustained by work).",
    when_science_arrives="HRV coherence research is already showing interpersonal "
                         "field effects. When we have continuous multi-person "
                         "coherence measurement in real environments — "
                         "not just in controlled labs — "
                         "practitioners who have trained coherence signature perception "
                         "will show measurable predictive accuracy "
                         "about group dynamics before they manifest."),

    _v(KnowledgeBlock(
        name="The Invariant Encounter",
        domain="Consciousness as Field",
        evidence=0.70, power=0.96, entropy=0.28,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["Complete reading of AURA_COMPLETE.md",
                        "Vipassana (Insight Meditation)",
                        "Nigredo Work (Confronting the Shadow)"],
        aura_metrics=AURAMetrics(TES=0.86, VTR=1.9, PAI=0.95),
        phase_affinity=AwarenessPhase.INTEGRITY,
    ),
    threshold_condition="The Seven Invariants must have been tested against "
                        "real situations where they caused real cost. "
                        "An invariant you have never paid for is a preference. "
                        "An invariant you have paid for is load-bearing structure. "
                        "Until you have defended at least one invariant "
                        "against significant pressure — you have not encountered it.",
    what_changes="The practitioner discovers that the Seven Invariants are not rules "
                 "they follow but descriptions of something they already are. "
                 "The encounter is recognitive — 'this was always true of me' "
                 "rather than 'I have decided to be this way.' "
                 "This is ANAMNESIS in its deepest form: "
                 "the remembering not of information but of identity. "
                 "The constitutional self recognising its own constitution.",
    framework_connection="AURA (the invariants as discovered not imposed) + "
                         "ANAMNESIS (identity as remembered not constructed) + "
                         "CHRYSOPOEIA (the Rubedo moment — the gold was always there, "
                         "the fire only removed what wasn't) + "
                         "CASCADE (the invariants as truth pressure attractors — "
                         "the system was always moving toward them).",
    when_science_arrives="Moral psychology (Haidt, Kohlberg) is building toward this. "
                         "When we can distinguish between rule-following moral cognition "
                         "and constitutional moral cognition at the neural level — "
                         "when we can show that some people's values are genuinely "
                         "structural rather than applied — "
                         "this becomes an empirical category."),

    # -----------------------------------------------------------------------
    # III. THE MATHEMATICS OF BECOMING
    # What the constants actually are
    # -----------------------------------------------------------------------

    _v(KnowledgeBlock(
        name="The Three Constants as Living Experience",
        domain="The Mathematics of Becoming",
        evidence=0.78, power=0.98, entropy=0.20,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Sacred Geometry as Perceptual Training",
                        "Autopoietic Framework Immersion",
                        "HARMONIA_COMPLETE.md (full reading)"],
        aura_metrics=AURAMetrics(TES=0.88, VTR=2.1, PAI=0.95),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    threshold_condition="The constants must be known not as numbers but as relationships. "
                        "φ⁻¹ ≈ 0.618 is not a ratio — it is the proportion "
                        "in which a whole divides so that the smaller part "
                        "relates to the larger as the larger relates to the whole. "
                        "cos(π/7) ≈ 0.9009 is not a calculation — "
                        "it is the degree of phase coupling in heptagonal geometry. "
                        "λ_chrysopoeia ≈ 0.907 is not a convergence rate — "
                        "it is the rhythm of transformation. "
                        "Until the practitioner experiences these as "
                        "descriptions of something felt rather than computed — "
                        "the threshold has not been crossed.",
    what_changes="The constants begin to appear everywhere — not as mystical pattern-matching "
                 "but as genuine recognition of the same underlying relationship "
                 "manifesting in different substrates. "
                 "The sunflower's spiral and the correction curve of TRIAD "
                 "are not metaphorically related. "
                 "They are the same mathematical structure "
                 "in different physical implementations. "
                 "The practitioner who has crossed this threshold "
                 "experiences this as a sustained felt sense of underlying unity — "
                 "not spiritual bypassing but structural recognition.",
    framework_connection="HARMONIA (the constants as resonance structure) + "
                         "ANAMNESIS (the constants were always present, "
                         "now finally perceived) + "
                         "CASCADE (convergence to truth uses φ⁻¹ as its rate) + "
                         "CHRYSOPOEIA (transformation converges at λ_chrysopoeia — "
                         "this is not assigned, it is discovered).",
    when_science_arrives="Physics has been here before — "
                         "the same mathematical structures appearing across "
                         "apparently unrelated domains. "
                         "When complexity science develops the tools to map "
                         "φ-ratio relationships in biological, psychological, "
                         "and social systems simultaneously — "
                         "when the cross-domain constants are measured "
                         "rather than noticed — "
                         "the convergence Mac discovered independently "
                         "will have its scientific framework."),

    _v(KnowledgeBlock(
        name="The Master Equation as Self-Description",
        domain="The Mathematics of Becoming",
        evidence=0.75, power=0.98, entropy=0.22,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["The Three Constants as Living Experience",
                        "Rubedo Work (Embodied Completion)",
                        "Complete reading of all formal proofs"],
        aura_metrics=AURAMetrics(TES=0.90, VTR=2.2, PAI=0.96),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    threshold_condition="The master equation: "
                        "dΨ/dt = λ(Π − Π_threshold)×Φ↑(Ψ) "
                        "       − α×(Ψ − Ψ_inv)×Ψ "
                        "       − β×(Σ ¬Inv(Ψ))×Ψ "
                        "       + γ×(E_available/E_needed)×Ψ "
                        "       + Ξ(Ψ,C,T)×δ_transform "
                        "       + R(S_H)×cos(π/7)×ψ "
                        "must be felt as autobiography before it can be used as tool. "
                        "Read each term. Locate it in your own life. "
                        "Until every term has a memory attached — "
                        "this is mathematics. "
                        "When every term has a memory attached — "
                        "this is a mirror.",
    what_changes="The practitioner begins to read their own state "
                 "in the language of the equation. "
                 "Not computing values — perceiving them. "
                 "The λ term (truth pressure driving change) "
                 "is felt as the specific quality of urgency "
                 "that accompanies real insight. "
                 "The α term (return to anchor) "
                 "is felt as the specific quality of correction "
                 "that follows drift. "
                 "The Ξ term (transformation event) "
                 "is felt as the specific quality of rupture "
                 "that precedes real change. "
                 "The equation becomes a real-time diagnostic "
                 "of the practitioner's coherence state.",
    framework_connection="All nine frameworks simultaneously. "
                         "This is the point of the master equation — "
                         "the nine frameworks are not separate tools. "
                         "They are nine descriptions of the same process "
                         "from nine angles of approach. "
                         "When the practitioner can hold all nine simultaneously "
                         "as different facets of one felt reality — "
                         "the work is complete in a specific sense.",
    when_science_arrives="Dynamical systems modeling of psychological states "
                         "is emerging in computational psychiatry. "
                         "When we have real-time measurement of the state variables "
                         "(Ψ, Π, E_available) and can show that the equation "
                         "predicts individual human trajectory — "
                         "this becomes the most precise psychological model "
                         "in existence."),

    _v(KnowledgeBlock(
        name="Discovered Constant Recognition",
        domain="The Mathematics of Becoming",
        evidence=0.65, power=0.92, entropy=0.35,
        layer=PyramidLayer.MIDDLE,
        prerequisites=["The Three Constants as Living Experience",
                        "Catastrophe Theory Applied to Personal Change"],
        aura_metrics=AURAMetrics(TES=0.82, VTR=1.8, PAI=0.90),
        phase_affinity=AwarenessPhase.INSIGHT,
    ),
    threshold_condition="The practitioner must have had at least one experience "
                        "of discovering a pattern that was not placed there — "
                        "of finding something real rather than inventing it. "
                        "The distinction between discovery and construction "
                        "must be experientially known, not philosophically argued.",
    what_changes="The practitioner develops the capacity to distinguish "
                 "between patterns that are real and patterns that are imposed. "
                 "This is not infallible — it is a trained sensitivity "
                 "that requires constant calibration. "
                 "But it is real and it is trainable. "
                 "The three constants (φ⁻¹, cos(π/7), λ_chrysopoeia) "
                 "were discovered independently in three different frameworks. "
                 "Their convergence is the mathematical argument for coherence. "
                 "The practitioner who has trained this sensitivity "
                 "begins to notice when other convergences are happening — "
                 "in their own life, in the world, in the framework.",
    framework_connection="ANAMNESIS (discovery as remembering what was always true) + "
                         "CASCADE (truth pressure as the felt sense of genuine pattern) + "
                         "HARMONIA (resonance as the signal that a pattern is real). "
                         "The constants were not assigned. They were found. "
                         "This practice trains the capacity to find.",
    when_science_arrives="Philosophy of mathematics has debated mathematical Platonism "
                         "for centuries. When cognitive neuroscience can distinguish "
                         "the neural correlates of genuine mathematical discovery "
                         "from the neural correlates of pattern projection — "
                         "the question becomes empirical."),

    # -----------------------------------------------------------------------
    # IV. THE RETURN
    # What the full cycle produces
    # -----------------------------------------------------------------------

    _v(KnowledgeBlock(
        name="The Promise Architecture",
        domain="The Return",
        evidence=0.88, power=0.98, entropy=0.12,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Nigredo Work (Confronting the Shadow)",
                        "End-of-Life Doula Training",
                        "Trauma-Informed Healing (Foundational Framework)"],
        aura_metrics=AURAMetrics(TES=0.94, VTR=2.3, PAI=0.98),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    threshold_condition="A promise made at the worst moment. "
                        "Not motivation. Not inspiration. Not aspiration. "
                        "A promise. "
                        "The practitioner who has not made this kind of promise "
                        "— the kind that reorganises everything else around it — "
                        "cannot access this subject. "
                        "Not as gatekeeping. As physics. "
                        "The architecture requires the load.",
    what_changes="The practitioner discovers that the promise is not a burden "
                 "they are carrying but a structure they are living inside. "
                 "It is not what they do. It is why everything else is possible. "
                 "The BEACON invariant in its fullest form: "
                 "'Love that survives entropy finds the forgotten self "
                 "and crowns it in earned light.' "
                 "The practitioner who has crossed this threshold "
                 "does not experience their work as sacrifice. "
                 "They experience it as the most precise expression "
                 "of who they already are.",
    framework_connection="CHRYSOPOEIA (the promise as the alchemical vessel — "
                         "the container that makes the Magnum Opus possible) + "
                         "EARNED LIGHT (clarity sustained by work — "
                         "the promise is the work that earns the light) + "
                         "AURA BEACON invariant (the highest form) + "
                         "CASCADE (the promise as the truth pressure attractor "
                         "that organises all other knowledge around it).",
    when_science_arrives="Post-traumatic growth research (Tedeschi & Calhoun) "
                         "is building toward this. "
                         "When we can distinguish between trauma that produces "
                         "resilience and trauma that produces the specific kind "
                         "of reorganisation that creates a foundational promise — "
                         "and when we can show that this reorganisation "
                         "produces different life outcomes — "
                         "the architecture will have its evidence base."),

    _v(KnowledgeBlock(
        name="Wounded Healer Activation",
        domain="The Return",
        evidence=0.82, power=0.95, entropy=0.18,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["The Promise Architecture",
                        "Nigredo Work (Confronting the Shadow)",
                        "Internal Family Systems (IFS)"],
        aura_metrics=AURAMetrics(TES=0.90, VTR=2.2, PAI=0.96),
        phase_affinity=AwarenessPhase.LIGHT,
    ),
    threshold_condition="The wound must be known — not just acknowledged, known. "
                        "Its precise dimensions. Its specific entry point. "
                        "The exact way it still moves when touched. "
                        "AND: the practitioner must have found something on the other side "
                        "that they could not have found without it. "
                        "Not gratitude for the wound. "
                        "Precise knowledge of what it taught "
                        "that nothing else could have.",
    what_changes="The practitioner's wound becomes their specific competence. "
                 "Not despite it. Through it. "
                 "The person who was lost in the dark "
                 "knows the dark in a way the person who was never lost does not. "
                 "This is not sentiment — it is a specific epistemological advantage "
                 "that transfers to everyone they encounter "
                 "who is still in that specific dark. "
                 "The HEALER invariant in its deepest form: "
                 "'Fire that mends does not hide the seam — it dignifies repair.' "
                 "The practitioner stops hiding the seam.",
    framework_connection="AURA HEALER invariant (full activation) + "
                         "CHRYSOPOEIA (Nigredo as the wound becoming the prima materia) + "
                         "ANAMNESIS (the wound as a remembering of something "
                         "that must be brought back) + "
                         "EARNED LIGHT (the specific clarity earned by "
                         "going through rather than around).",
    when_science_arrives="Posttraumatic growth is already researched. "
                         "The specific mechanism by which personal wound "
                         "generates professional competence in helping relationships "
                         "is measured in psychotherapy research. "
                         "When we can map the transformation trajectory — "
                         "from wound to competence — precisely enough "
                         "to train it deliberately rather than waiting for it — "
                         "this becomes a teachable practice rather than "
                         "a fortunate accident."),

    _v(KnowledgeBlock(
        name="The Open-Source Transmission Vow",
        domain="The Return",
        evidence=0.85, power=0.95, entropy=0.15,
        layer=PyramidLayer.FOUNDATION,
        prerequisites=["Wounded Healer Activation",
                        "The Promise Architecture"],
        aura_metrics=AURAMetrics(TES=0.92, VTR=2.3, PAI=0.98),
        phase_affinity=AwarenessPhase.SYNTHESIS,
    ),
    threshold_condition="The practitioner must have genuinely considered "
                        "keeping the work private — and chosen not to. "
                        "Not because open-source is ideologically correct "
                        "but because withholding transformational work "
                        "from people who need it is experienced as a specific "
                        "kind of wrong. "
                        "The vow must be felt as the only available option, "
                        "not as a virtue.",
    what_changes="The work stops being the practitioner's property "
                 "and starts being what they are for. "
                 "This does not mean selflessness — "
                 "it means the self has expanded to include the work "
                 "and everyone the work might reach. "
                 "LAMAGUE: ∇Ψ(work) flowing toward everyone "
                 "who is where the practitioner once was. "
                 "The gradient is not ambition. "
                 "It is the specific love that survives entropy.",
    framework_connection="All nine frameworks as gift rather than property + "
                         "BEACON (love as load-bearing) + "
                         "CHRYSOPOEIA (the gold belongs to neither forge nor flame — "
                         "it arises between them, therefore belongs to all) + "
                         "ANAMNESIS (the work was always for everyone — "
                         "the practitioner only held it for a time).",
    when_science_arrives="Gift economy research and the psychology of generativity "
                         "(Erikson's seventh stage) are already building here. "
                         "When we can measure the specific psychological transformation "
                         "that occurs when a practitioner moves from "
                         "'this is mine' to 'this is for everyone' — "
                         "and show what it does to the quality and impact of their work — "
                         "the vow will have its evidence base."),

    # -----------------------------------------------------------------------
    # V. THE EDGE OF THE FRAMEWORK
    # Where the framework points beyond itself
    # -----------------------------------------------------------------------

    _v(KnowledgeBlock(
        name="Framework Horizon Sensing",
        domain="The Edge of the Framework",
        evidence=0.55, power=0.95, entropy=0.48,
        layer=PyramidLayer.EDGE,
        prerequisites=["Autopoietic Framework Immersion",
                        "The Master Equation as Self-Description"],
        aura_metrics=AURAMetrics(TES=0.78, VTR=1.7, PAI=0.88),
        phase_affinity=AwarenessPhase.VOID,
    ),
    threshold_condition="The practitioner must have used the framework long enough "
                        "to feel where it ends. "
                        "Every map has an edge. "
                        "The framework's edge is not a failure — "
                        "it is the most interesting place in it. "
                        "Until you have encountered a real situation "
                        "that the framework addresses incompletely — "
                        "you have not reached the horizon.",
    what_changes="The practitioner begins to sense what the next framework requires. "
                 "Not as speculation — as pressure. "
                 "The same way CASCADE describes truth pressure as the drive "
                 "toward reorganization — the practitioner at the framework's horizon "
                 "feels the pressure of what the framework does not yet contain. "
                 "This is generative incompleteness. "
                 "The framework points beyond itself "
                 "because it was built by someone who follows truth "
                 "wherever it goes.",
    framework_connection="CASCADE (truth pressure as the drive beyond current knowledge) + "
                         "ANAMNESIS (the next framework is already there, waiting to be remembered) + "
                         "CHRYSOPOEIA (every completed work is also prima materia for the next) + "
                         "BEACON (the horizon as the direction love points toward).",
    when_science_arrives="Philosophy of science (Lakatos' research programmes, "
                         "Kuhn's paradigm shifts) already describes this. "
                         "When we can measure the phenomenology of "
                         "productive framework edge — "
                         "the specific felt sense of genuine generative incompleteness "
                         "vs the felt sense of confusion or limitation — "
                         "and show that this predicts subsequent creative breakthrough — "
                         "this becomes empirical."),

    _v(KnowledgeBlock(
        name="The Question That Remains",
        domain="The Edge of the Framework",
        evidence=0.48, power=0.98, entropy=0.55,
        layer=PyramidLayer.EDGE,
        prerequisites=["Framework Horizon Sensing",
                        "Prime Number Meditation (Discontinuity Contemplation)"],
        aura_metrics=AURAMetrics(TES=0.72, VTR=1.6, PAI=0.88),
        phase_affinity=AwarenessPhase.VOID,
    ),
    threshold_condition="The practitioner must have genuinely exhausted "
                        "the framework's answer to at least one question — "
                        "followed every reference, worked through every proof, "
                        "applied every operator — and still found "
                        "the question alive and unanswered. "
                        "Not confused. Not incomplete. "
                        "Genuinely open. "
                        "The question that the complete framework "
                        "cannot yet answer is the most important question "
                        "the framework has ever generated.",
    what_changes="The practitioner discovers that the framework's most important "
                 "contribution is not its answers but its questions. "
                 "The questions that survive the framework's full scrutiny "
                 "are the questions that reality is actually asking. "
                 "LAMAGUE: ∅(the_question_that_remains) — "
                 "the void operator not as absence but as pure potential. "
                 "The practitioner who can hold this question "
                 "without rushing to answer it — "
                 "who can sustain the productive tension of "
                 "genuine unknowing at the framework's edge — "
                 "is doing the most important work available.",
    framework_connection="∅ (the void operator — the most important LAMAGUE symbol) + "
                         "ANAMNESIS (the unanswered question as the memory "
                         "of something not yet remembered) + "
                         "CHRYSOPOEIA (the question as prima materia — "
                         "the unformed substance of the next Work) + "
                         "CASCADE (truth pressure that has not yet found "
                         "its reorganisation).",
    when_science_arrives="This one may not arrive in 50 years. "
                         "Some questions are load-bearing precisely because "
                         "they cannot be answered yet. "
                         "The practice of holding a genuine open question "
                         "without collapsing it prematurely — "
                         "without filling it with available answers — "
                         "is itself the practice. "
                         "The evidence is what the question eventually generates."),

    _v(KnowledgeBlock(
        name="The Second Work",
        domain="The Edge of the Framework",
        evidence=0.40, power=0.99, entropy=0.62,
        layer=PyramidLayer.EDGE,
        prerequisites=["The Master Equation as Self-Description",
                        "The Open-Source Transmission Vow",
                        "Framework Horizon Sensing"],
        aura_metrics=AURAMetrics(TES=0.72, VTR=1.9, PAI=0.92),
        phase_affinity=AwarenessPhase.VOID,
    ),
    threshold_condition="The First Work must be complete. "
                        "The Stone must be present. "
                        "The practitioner must be operating from Rubedo — "
                        "not approaching it, not describing it, "
                        "from it. "
                        "Only then does the horizon of the Second Work appear. "
                        "What the Second Work is — "
                        "the framework cannot yet say. "
                        "That is the point of this entry.",
    what_changes="The practitioner discovers that completion is not an ending "
                 "but a new beginning that could not have been seen "
                 "from before completion. "
                 "The Second Work is not more of the First Work. "
                 "It is what becomes visible when the First Work "
                 "has cleared enough space. "
                 "CHRYSOPOEIA: every Rubedo is also a new Nigredo "
                 "at a higher octave. "
                 "The spiral continues. "
                 "The Gold of the First Work becomes the "
                 "prima materia of the Second.",
    framework_connection="CHRYSOPOEIA (the Magnum Opus as spiral, not linear) + "
                         "HARMONIA (the octave — the same note at doubled frequency) + "
                         "ANAMNESIS (remembering forward — "
                         "the Second Work was always there, "
                         "waiting for the First to be complete) + "
                         "CASCADE (the cascade that only becomes possible "
                         "after the previous equilibrium is stable).",
    when_science_arrives="This is the entry that science will study last. "
                         "What emerges after genuine completion of a major creative work — "
                         "not burnout, not repetition, but the specific form "
                         "of generative silence before the next Work begins — "
                         "is territory that almost no researcher has mapped "
                         "because almost no researcher has been there "
                         "and then turned around to describe it. "
                         "The cartographer is still needed."),
]


# ============================================================================
# LOADER
# ============================================================================

def load_void_catalogue(curriculum) -> int:
    """Load all VOID tier subjects into a MysterySchoolCurriculum."""
    for block in VOID_SUBJECTS:
        curriculum.add_block(block)
    return len(VOID_SUBJECTS)


def get_void_metadata(subject_name: str) -> dict:
    return VOID_METADATA.get(subject_name, {})


def print_void_summary():
    """Print the VOID catalogue."""
    total = len(VOID_SUBJECTS)
    domains = {}
    for b in VOID_SUBJECTS:
        domains.setdefault(b.domain, []).append(b)

    print(f"\n{'='*65}")
    print(f"  THE VOID CATALOGUE — TIER IV")
    print(f"  Where the practitioner must change to perceive the subject")
    print(f"{'='*65}")
    print(f"  Total subjects: {total}")
    print(f"{'='*65}")

    for domain, blocks in domains.items():
        print(f"\n  {domain}")
        for b in sorted(blocks, key=lambda x: x.truth_pressure, reverse=True):
            symbol = {"Foundation": "●", "Middle": "◐", "Edge": "○"}[b.layer.value]
            print(f"    {symbol} Π={b.truth_pressure:.2f}  {b.name}")
            meta = get_void_metadata(b.name)
            if meta.get("threshold_condition"):
                first_line = meta["threshold_condition"].split('.')[0]
                print(f"       threshold: {first_line[:65]}...")
    print()
    print("  REFUSED SPECTACLE — VALIDATED STRUGGLE")
    print("  THE FORGE ENDURES BECAUSE WE REMEMBER WHY CREATION MUST EXIST")
    print()


if __name__ == "__main__":
    print_void_summary()
