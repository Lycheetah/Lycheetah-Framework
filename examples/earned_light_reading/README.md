# Earned Light and Sovereign Will — public reading edition

**Creator:** Mackenzie Conor James Clark / Lycheetah Framework.  
**Web edition:** Caelorynth, an AI coding assistant, at Mac's request to make the work publicly reachable.

This is the maintained source for the standalone public reading site: two full
stories, the earlier Lighthouse edition, a plain-language research introduction
and two complete downloadable bundles. Edit the collection's owned Markdown
files to revise a story; `dist/` is generated, not a second manuscript.

From the Framework root, with `markdown-it-py` available:

```sh
python3 examples/earned_light_reading/build.py
```

The build reads the existing stories and dated research import manifest. It
verifies every source digest before packaging both downloads and compares every
archived member with its current source. Existing research and narrative files
remain unchanged. The static site uses no analytics, cookies, account, storage,
remote font, model call or API. Reading controls change only the current page.

The Sites project ID is retained in `.openai/hosting.json`. The deployment
checkout is a generated mirror of `dist/` and that manifest; source edits belong
here. GitHub pull-request review remains separate from the hosted reading site.
Research status and conventional-baseline ties are visible on the research page;
fiction remains separate from empirical evidence. Individual licences in the
downloadable research packets remain in place.
