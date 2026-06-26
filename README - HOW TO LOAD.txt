================================================================================
CHAIN NETWORK WEBSITE - STAGING BUILD (clean, one-go upload)
================================================================================
PURPOSE: this folder is the COMPLETE, FLAT, SELF-CONTAINED website. Everything an
AI crawler needs to read the catalogue in one pass, plus a clean human view.

HOW TO LOAD (your workflow):
  1. Delete everything in the GitHub "staging" branch.
  2. Upload EVERY file in this folder (keep the same names, root level).
  3. View the staging URL, confirm it looks right.
  4. Push staging -> Main.

WHAT IS IN HERE (the output files you upload):
  index.html        - the human site: search, filter, levels, 4 languages, brand.
  videos.json       - the machine feed (AI reads this first). One record per video.
  llms.txt          - the AI-inference index (emerging standard, markdown).
  sitemap.xml       - lists every page/deep-link for crawlers.
  robots.txt        - allows AI + search crawlers, points to sitemap + llms.txt.
  styles.css        - embedded-friendly stylesheet (rainbow/whiteboard palette).
  teachers.html     - teacher downloads, email-gated (worksheets / lesson packs).
  /downloads/       - the PDF worksheets + lesson packs (added as produced).

HOW IT IS BUILT (ongoing production, not a one-off):
  build_site.py is the GENERATOR. It reads:
    - "TCN VIDEO LINKS - paste here.txt"  (the link source of truth)
    - the per-language script files (titles + descriptions)
  and regenerates ALL the output files above.
  WHEN YOU ADD LINKS OR NEW SUBJECTS: paste links, then re-run the generator,
  then reload this folder. The catalogue scales 01-28 (EN 01-31) automatically.

DESIGN RULES BAKED IN:
  - AI-FIRST: catalogue is real static semantic HTML + videos.json + llms.txt.
    (Research shows LLMs tokenise JSON-LD and lose structure, so the content is
    ALSO visible HTML text, not a JavaScript app - readable in one pass.)
  - Auto language by visitor location, with manual override (EN/ES/PT/HI).
  - Brand palette: rainbow accents, whiteboard feel, red=bad, green=good,
    black/dark-grey=text. Happy, inclusive, serious educational resource.
  - Channel handle: @thechainnetwork_1. Website: thechainnetwork.com.
  - Funnel: AI/site -> YouTube. TikTok is advertising only (not a funnel).
================================================================================
