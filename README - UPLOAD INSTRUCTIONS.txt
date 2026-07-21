================================================================================
WEBSITE 21.07.2026 - CLEAN REPLACE PACKAGE FOR github.com/TheChainNetwork/thechainnetwork.com
Built 21-22 Jul 2026 from: repo build_site.py (canonical) + corrected
catalog_data.json (released subjects 01-14) + TCN VIDEO LINKS file (56 live links).
================================================================================

WHY THIS REBUILD WAS NEEDED (found during review, 21 Jul)
The live site was serving THREE different generations at once:
  index.html   56 records (subjects 01-14)  <- correct
  videos.json  40 records (subjects 01-10)  <- STALE, regressed
  llms.txt     60 records including subject 15 <- LEAKING unreleased subject 15
                 video IDs (all four languages) while 15 is still private
Root cause: the repo's catalog_data.json is the old 3-Jul TRIMMED version
(subjects 01-10 only, missing the advanced level). DANGER: the release bot
rebuilds the links file from the repo's videos.json at release time. If
subject 15 had been flipped public before this fix, the rebuilt site would
have DROPPED subjects 11-14 entirely. This package fixes all of it.

UPLOAD THESE 9 FILES to the repo root (replace existing):
  index.html          56 records, all subjects 01-14, four languages
  videos.json         count 56, matches the links file exactly
  llms.txt            56 links, subject 15 leak REMOVED
  sitemap.xml         61 urls (5 pages + 56 videos)
  robots.txt          unchanged content, regenerated
  teachers.html       unchanged content, regenerated
  catalog_data.json   CORRECTED: subjects 01-14, five level labels
                      (released subjects only, no unreleased titles)
  build_site.py       identical to the repo copy (included for completeness)
  CNAME               thechainnetwork.com (GitHub Pages custom domain,
                      byte-identical to the repo copy, upload is optional
                      but harmless)

DO NOT DELETE OR TOUCH in the repo:
  .github/workflows/release.yml   (the armed release bot)
  release_bot.py                  (the bot script)
  RELEASES.json                   (bot progress, currently {"14": "announced"})
  catalog_data.backup-19subj-20260703.json (trimmed public backup, harmless)
  Any Actions secrets. Secrets by name only: RELEASE_QUEUE,
  TELEGRAM_BOT_API, BLOTATO_API.

AFTER UPLOAD, VERIFY LIVE (allow a few minutes for Pages + cache):
  https://thechainnetwork.com/videos.json  -> "count": 56
  https://thechainnetwork.com/llms.txt     -> no "chain network 15" lines
  https://thechainnetwork.com/             -> footer "56 guides and growing"

NOTES
- Strapline: this build keeps "Transparent by design. Honest by default."
  because the strapline sweep is a standing hold awaiting Mike's explicit go.
  When the sweep is approved, edit build_site.py (footer lines in
  _append_index_footer_js and write_teachers) and rebuild.
- The teachers.html email form is still a front-end stub (localStorage only,
  no backend). See the teacher portal plan in this folder's parent for the
  build-out proposal.
- Verified before packaging: every URL matches the TCN VIDEO LINKS file,
  no holding-pen (unreleased) video IDs in any file, subjects exactly
  01-14 x 4 languages, sitemap well-formed, JSON-LD valid at 56 items,
  QR codes embedded.
================================================================================
