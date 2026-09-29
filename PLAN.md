# Churchhouse Rules — PLAN

## State (2026-09-29)
- 44 games in `games/`, built by `build.py` (stdlib only) into `site/`.
- Friends edit on the site (edit.html → functions/api/save.js → commit straight to main). No password yet, only a hidden bot trap; Ian will add one later.
- GitHub pull requests still work; `check.yml` runs `build.py --check` on every PR.
- Hosting: Cloudflare Pages project `churchhouse-rules`, Git-connected. Build `python3 build.py`, output `site` (set via API 2026-09-29).

## Open
- Custom domain churchhouserules.itogeospatial.com attached 2026-09-29 (Pages domain + proxied CNAME).
- GITHUB_TOKEN (fine-grained, this repo only, Contents RW, expires ~2027-09) set on Pages production 2026-09-29; add+edit tested live and the test game removed.
- Add a house password (or Turnstile) before sharing widely.
- Not supported from the site: deleting or renaming a game's file.

## Notes (2026-09-29, end of session)
- Type order on the page: Card, Word, Dice, Board, Outdoor, Trail, Indoor, Party, Icebreaker, Drinking (Drinking last on purpose). Order lives in TYPES in build.py and lib/game.js; keep them the same.
- Footer on every page: GitHub mark + "Contribute on GitHub". itogeo is the only collaborator.
- Workers usage: only Save counts (static views are free). ~12 function calls on launch day; account total ~1,900/day of 100k.
- Site saves show as itogeo in history (no per-person name). Optional later: "Your name" field, notification on new saves.
