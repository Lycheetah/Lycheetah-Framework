# GitHub Placement Suggestions

## Creative story

**Suggested destination:** `The-Mystery-School/stories/earned-light/THE_LAST_LIGHTHOUSE_OF_ETERNITY_EXPANDED.md`

Alternative if that folder structure does not exist: a new `stories/earned-light/` or `lore/` directory in whichever Lycheetah repository currently holds narrative work. Keep the short original alongside it as an archived early edition rather than silently replacing it.

## Earned Light research

**Suggested destination:** the `Lycheetah-Framework` repository, within an existing Earned Light research branch or under a clearly separate `research/earned-light/forges/` directory. Use the extracted `research_archive/Earned_Light_Full_Handoff/` contents and preserve original subfolders for Forges 02–07. Inspect existing tree and avoid duplicating or overwriting already-published research. The prior pass 01 is at `Earned_Light_Research_Pass_01.md`.

## Recommended manual Git workflow

1. Inspect the relevant repositories and their existing README, directory conventions, and licensing.
2. Create a topic branch in each repository, e.g. `docs/earned-light-lighthouse` and `research/earned-light-forges-snapshot`.
3. Copy story file(s) into the narrative repo and link the technical research without conflating fictional exposition and tested claims.
4. Copy only the research files not already in the target repository; retain existing history and avoid overwriting newer work.
5. Review file changes (`git diff --check`, diffs), test code in a clean environment, and commit with meaningful messages.

**No remote repository tree was verified during this packaging step**, so destinations are suggestions rather than established existing paths.
