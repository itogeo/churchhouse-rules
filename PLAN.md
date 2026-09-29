# Churchhouse Rules — PLAN

## State (2026-09-29)
- 44 games in `games/`, built by `build.py` (stdlib only) into `site/`.
- Friends edit by GitHub pull request; `check.yml` runs `build.py --check` on every PR.
- Hosting: Cloudflare Pages, Git integration (not GitHub Pages). Build `python3 build.py`, output `site`.

## Open
- Connect the Pages project to the repo in the Cloudflare dashboard (one-time, Ian).
- Choose and attach the custom domain.
- Later, maybe: a web form so people can suggest games without a GitHub account.
