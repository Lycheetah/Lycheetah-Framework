# APP COMIC PRODUCTION SPEC V0.1
## A native fifty-page Lycheetah story room

**Story:** *The Testament of Three Shadows*  
**Status:** ACTIVE COMIC PRODUCTION PIPELINE · visual direction crowned · no app code changed  
**Primary source:** `TESTAMENT_OF_THREE_SHADOWS_50_PAGE_SCRIPT_V0_1.md`

## Product promise

The comic is not a PDF hidden inside the app. It is a native story room with:

- portrait page reading and optional guided panel reading;
- swipe, tap-edge and accessible next/previous controls;
- crisp app-rendered captions and speech rather than baked-in image text;
- optional narrated audio with word or panel highlighting;
- alt text and a plain transcript for every page;
- progress saved locally;
- optional lore objects unlocked only after the relevant page;
- a “prose edition” doorway preserving the complete source tale;
- no compulsory account, streak, payment pressure or social sharing;
- export-ready page dimensions for a later A4 physical edition.
- optional restrained “Living Page” motion built from Sol's existing Parallax and
  Reanimated components, always pausable, skippable and reduced-motion safe.

## Visual covenant

### Base palette

- **Obsidian Void:** night, crownstone, negative space and the silence that lets living
  colour strike with impossible force. Void should often hold more area than pigment.
- **Bone:** burial cloth, paper, salt, ordinary bodies and readable light.
- **Crimson:** command, state power, wounds, army rhythm and consequential choice.
- **Ember Orange:** courage in motion, forged matter, danger and the First Inheritor's
  decision-pressure.
- **Electric / Celestial Blue:** water, grief, immense distance and the Second Inheritor's
  relation to promises; it may appear as restrained foreshadowing before its full river
  revelation.
- **Mystical Amethyst:** inherited knowledge, restoration, unrealised possibility and
  AIVOID depth.
- **Relational Pink:** tenderness, recognition and identities touching without merger;
  never used as generic softness.
- **Living Green:** creature agency, renewed passage and the wild answer that exists
  outside human classification.
- **Pale Gold:** appears where free relation creates a real path.

### Medium

Mature mythic graphic novel: expressive ink contours, painterly mineral colour, physical
stone/paper/cloth texture, strong readable silhouettes and restrained facial realism.
Ancient without copying one historical culture. Sacred scale balanced by worn tools,
dust, food, stitching and human imperfection.

**CROWNED VISUAL REFERENCE:** `ART/style-key-three-inheritors-v0-1.png`. Preserve its
mineral-ink surface, ensemble equality, tactile darkness, restrained palette and human
imperfection across every generated continuity asset and page.

**CROWNED COLOUR EXPANSION:** Mac clarified that Lycheetah's chaos-lit energy includes
vibrant blues, oranges, greens, mystical purples, reds and pinks. Preserve the reference's
ink, texture and void, but do not mistake its muted first scene for the whole comic's
chromatic range. Colour concentrates around character, creature, relation and consequence
so people and scenes blaze against void space in unreal ways.

### Hybrid World aesthetic compass

Mac crowned the Three Shadows' aesthetic as the clearest expression of Lycheetah's mythic
visual identity: dark mineral surfaces, strange elegance, carved tactile detail, immense
void and selective living colour. Carry that unearthly hybrid quality through people,
garments, tools, architecture, landscapes and creatures. The world must remain emotionally
legible while never reading as merely Earth-historical fantasy.

Do not add literal creatures, three-eye marks, antler motifs or three-shadow symbols where
the story does not call for them. The Three Shadows remain sovereign rather than decorative.

### Avoid

- generic superhero anatomy or posing;
- glossy game-concept armour;
- photoreal celebrity faces;
- one culture's sacred clothing or architecture used as fantasy costume;
- purple everywhere merely because Amethyst is in the palette;
- unreadable black-on-black forms;
- AI-generated lettering inside art;
- inconsistent ages, scars, handedness, clothing or creature anatomy;
- romanticising wounds or making sacrifice visually ecstatic.

## Character continuity sheets required before page generation

1. First Inheritor: related face structure, scarred adult woman, powerful but human build,
   abdominal scar, incomplete armour, later glass wounds.
2. Second Inheritor: same facial lineage, adult man, grief-carved expression, oath-writer's
   hands, names accumulating on sleeves.
3. Third Inheritor: same facial lineage, androgynous young adult, no scars, alert technical
   attention, hand script and Amethyst geometry.
4. Stonewright: old woman, copper leg brace, mason's apron over funeral cloth, crownstone
   braids, chisel and cane.
5. Singer of Omissions: small old woman, immense physical voice, practical layered cloth,
   dates and engraving tools.
6. River Physician: drought-worn adult, ordinary coat, wooden case of empty bottles,
   visibly practical hands.
7. Soot Child: eleven or twelve, furnace soot, stolen flatbread, unceremonious courage.
8. Keeper of Succession: controlled official silhouette, crown-ring geometry, increasing
   visual isolation.
9. Army General: travel-worn authority beneath a crimson canopy, not villain-coded.
10. Three-shadow creature: narrow feline-cervid body, smooth backward antlers, three eyes,
    shifting obsidian/pre-rain-stone surface, precisely three meaningful shadows.
11. Old mountain creature: related anatomy, lichen antlers, three scars, immense age
    without humanoid wisdom-signalling.

## Location continuity sheets required

1. three restoration chambers;
2. room of mistakes beneath the mint;
3. grain store and market quarter;
4. salt road and altered direction pillar;
5. route-glass field;
6. First Quarry and reservoir gate;
7. throne room before and after the crown opens;
8. later-age family departure room.

## Sequential generation method

1. Generate one style key without text.
2. Crown or revise its line, palette, faces and creature grammar.
3. Generate individual character sheets using the crowned style key as reference.
4. Generate location sheets.
5. Thumbnail all 50 pages as simple deterministic layouts before final art.
6. Produce pages in five ten-page batches, carrying the smallest sufficient reference set.
7. Validate every batch for character continuity, props, injuries, palette progression and
   spatial direction.
8. Add captions/dialogue in the app and print compositor, never in generated art.
9. Run mobile reading witness at 360, 390 and 430 CSS-pixel widths.
10. Export a ten-page physical proof before committing to all fifty final-resolution pages.

## App content schema proposal

Each page should be authored as data:

```text
ComicPage
  id
  pageNumber
  imageAsset
  aspectRatio
  panels[]
    id
    focusRect
    altText
    narrationCue
  textOverlays[]
    kind: caption | dialogue | sound
    speakerId?
    text
    anchor
  unlocks[]
  transcript
```

The schema is a proposed contract, not an authorised app implementation. Sol's engine and
Caelorynth's book forge remain separate write lanes unless Mac explicitly joins them.

## Honest production scale

A coherent fifty-page comic is not one image-generation call. It requires:

- one crowned visual style;
- eleven character/creature designs;
- eight location designs;
- roughly 190–220 panel compositions;
- five continuity-reviewed generation batches;
- lettering, accessibility, app integration and physical proof.

The efficient path is to create the **style key plus pages 1–5 as the first visual
witness**, then decide whether the medium has earned the remaining generation cost.

The separate `LIVING_COMIC_MOTION_WEAVE_V0_1.md` records which animation capabilities are
measured in Sol's current app and which deterministic Moment Forge capability remains a
specification rather than live tooling.
