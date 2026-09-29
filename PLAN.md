# Churchhouse Rules — PLAN

## State (2026-09-29)
- 44 games in `games/`, built by `build.py` (stdlib only) into `site/`.
- Friends edit by GitHub pull request; `check.yml` runs `build.py --check` on every PR.
- Hosting: Cloudflare Worker `churchhouse-rules`, static assets only (wrangler.jsonc), Workers Builds connected to the repo. Build `python3 build.py`, deploy `npx wrangler deploy`.

## Open
- Set the build command to `python3 build.py` in the Worker's Build settings (one-time, Ian).
- Choose and attach the custom domain.
- Later, maybe: a web form so people can suggest games without a GitHub account.
