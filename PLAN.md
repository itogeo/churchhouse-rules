# Churchhouse Rules — PLAN

## State (2026-09-29)
- 44 games in `games/`, built by `build.py` (stdlib only) into `site/`.
- Friends edit by GitHub pull request; `check.yml` runs `build.py --check` on every PR.
- Hosting: Cloudflare Pages project `churchhouse-rules`, Git-connected. Build `python3 build.py`, output `site` (set via API 2026-09-29).

## Open
- Choose and attach the custom domain.
- Later, maybe: a web form so people can suggest games without a GitHub account.
