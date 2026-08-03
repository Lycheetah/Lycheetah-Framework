# LIVING COMIC MOTION WEAVE V0.1
## Subtle animation without sacrificing the illustrated page

**Story:** *The Testament of Three Shadows*  
**Status:** PROPOSED ADAPTER CONTRACT · based on measured Sol app capabilities  
**Boundary:** design only; no writes made to Sol's app or active game-engine lane

## 1. Honest capability finding

### Measured in `/home/guestpc/0sol-by-lycheetah`

- `components/parallax/ParallaxLayer.tsx` moves registered image layers at distinct depth
  using shared camera values.
- `components/parallax/ParallaxStage.tsx` composes far, actor and foreground layers.
- `components/DescentThreshold.tsx` proves one shared Reanimated progress value can drive
  timed strata, camera-depth motion, gesture progress and tap-to-complete.
- React Native Reanimated 4.1.1 is installed and already used for restrained loops,
  transitions, ceremonies, particles and reduced-motion alternatives.
- React Native Skia 2.2.12 is installed for effects beyond ordinary transformed views.
- Audio, speech and haptics packages are already present.

### Scaffold, not yet measured implementation

The `P7F — TIMELINE AND MOMENT FORGE` contract exists in
`SOL-MOBILE-VAULT/LYCPIXEL_ENGINE_GENESIS_SPEC.md`, but the promised
`lib/pixel-engine/timeline.ts` is not currently present in the live app tree. It must not
be described as finished tooling.

### Decision

Build the comic motion layer as a small declarative adapter over the working Parallax and
Reanimated components. Later it may adopt the deterministic Moment Forge if Sol lands it.

## 2. Motion principle

> **The page remains an illustration. Motion reveals attention; it does not perform the
> whole action for the reader.**

Use motion for:

- slow camera arrival and guided panel focus;
- two-to-four-layer parallax;
- breathing light, dust, ash, rain, water and cloth;
- a blink, hand tremor or shadow divergence at a decisive moment;
- palette transitions tied to story consequence;
- sound and narration cues;
- stillness as an authored event.

Avoid:

- constant puppet movement;
- synthetic lip-sync;
- every panel panning and zooming;
- loops that make grief, wounds or sacred choices look decorative;
- camera motion while the reader is trying to read dense text;
- autoplay audio;
- motion without a static or reduced-motion equivalent.

## 3. Proposed page data

```text
LivingComicPage
  id
  pageNumber
  durationTicks
  holdLastFrame
  layers[]
    id
    asset
    depth
    role: far | mid | actor | foreground | light | shadow
    transformRange
  moments[]
    atTick
    durationTicks
    cameraTarget?
    layerActions[]
    paletteCue?
    soundCue?
    hapticCue?
    textCueIds[]
  reducedMotion
    stillAsset
    orderedTextCueIds[]
  completion
    requiredFinalState
```

The app renders dialogue and captions separately. A skipped or reduced-motion page lands
the exact same text, unlock and progress state.

## 4. Motion intensity tiers

### Tier 0 — Sacred stillness

No automatic motion. Used when the reader must hold an image: Pages 12, 34, 40 and 50.
A single tap may reveal the next caption.

### Tier 1 — Living page

Three-to-six seconds of barely perceptible depth, atmosphere or light. Default tier for
most pages.

### Tier 2 — Guided sequence

Camera focus moves across two or three panel regions as narration advances. Used for
complex ensemble events, always skippable.

### Tier 3 — Consequence moment

One short authored event: route-glass wakes, shadows open, crown separates or river
arrives. Limited to a small number of earned pages.

## 5. The eleven motion anchors

1. **Page 1 — Awakening:** slow descent through black palace stone; Amethyst underlight
   breathes once; First's cloth shifts; Second's water trembles; Third's hand-script gains
   one faint line. No eye-glow.
2. **Page 6 — Same face:** camera crosses the three related faces; the drought bell makes
   dust fall in each chamber at slightly different times.
3. **Page 12 — Removed memories:** paper strips lift in a silent air current while the
   people remain still. Reader controls the pace.
4. **Page 17 — Three shadows:** body remains almost motionless while the three shadows
   adopt springing, grieving and guarding postures independently.
5. **Page 23 — Armour:** pieces land one at a time; glass reeds respond with thin light.
6. **Page 25 — Missed beat:** shield rhythm crosses the page; one delayed pulse wakes a
   cutting line through the reeds.
7. **Page 33 — Witnesses:** silhouettes become visible along the quarry rim only as the
   camera's darkness adapts; no dramatic materialisation.
8. **Page 40 — Crossing shadows:** Crimson, Bone and Amethyst remain distinct; three
   shadows cross; Pale Gold appears only at their intersection.
9. **Page 41 — River:** a held second of nothing, one withdrawing bolt, then water crosses
   the page. This is the largest motion event in the comic.
10. **Page 46 — Crown opens:** the chisel strikes once; three seams answer with restrained
    haptic feedback; the arcs separate without explosion.
11. **Page 50 — Hands:** writing appears only as the reader advances each final sentence;
    shadows cross and the empty centre remains perfectly still.

## 6. Audio and voice

- narration remains opt-in;
- music begins only after explicit user action;
- spatial sound is restrained: drought bell, paper, glass tone, chisel and river;
- character dialogue can be voiced later, but the first witness needs narrator plus key
  sounds only;
- no audio is required to understand story state;
- leaving the room stops and releases all audio ownership.

## 7. Accessibility and sovereignty

- global Reduced Motion converts Tier 1–3 pages into still images with ordered reveals;
- every page remains navigable without swiping;
- animation can be paused and restarted;
- no essential information lives only in movement, colour, haptic or sound;
- alt text describes the final meaningful state rather than every decorative particle;
- the user controls narration, automatic progression and guided camera;
- completed pages remain revisit-able without replaying animation.

## 8. First implementation witness

Do not build all fifty motion pages first.

Build Pages **1, 17, 40, 41 and 50** as the five-motion vertical slice:

- ensemble awakening;
- independent three-shadow grammar;
- relational colour intersection;
- maximal river consequence;
- quiet hand-written ending.

This slice exercises the full range from subtle life to stillness and climax. It passes
only when normal, reduced-motion and skipped playback land identical reading progress and
unlock state on a real phone.
