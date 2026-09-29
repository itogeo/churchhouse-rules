// POST /api/save — write one game file straight to main on GitHub.
// Runs only when someone presses Save; page views never reach it.
// Needs GITHUB_TOKEN (fine-grained, this repo only, Contents: read and write)
// set as an encrypted variable on the Pages project.

import { validate, toMarkdown, slugify } from "../../lib/game.js";

const REPO = "itogeo/churchhouse-rules";
const BRANCH = "main";

function reply(status, body) {
  return new Response(JSON.stringify(body), {
    status, headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function github(env, path, init = {}) {
  return fetch(`https://api.github.com/repos/${REPO}/contents/${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      accept: "application/vnd.github+json",
      "user-agent": "churchhouse-rules-site",
      ...(init.body ? { "content-type": "application/json" } : {}),
    },
  });
}

function base64(text) {
  let bin = "";
  for (const b of new TextEncoder().encode(text)) bin += String.fromCharCode(b);
  return btoa(bin);
}

export async function onRequestPost({ request, env }) {
  if (!env.GITHUB_TOKEN) return reply(503, { error: "Saving isn't switched on yet." });

  let input;
  try {
    input = await request.json();
  } catch {
    return reply(400, { error: "That didn't come through. Try again." });
  }
  // Hidden field only bots fill in. Pretend it worked.
  if (input.website) return reply(200, { ok: true });

  const { game, problems } = validate(input);
  if (problems.length) return reply(400, { error: problems.join(" ") });

  const isNew = !input.slug;
  const slug = isNew ? slugify(game.name) : String(input.slug);
  if (!/^[a-z0-9-]+$/.test(slug)) return reply(400, { error: "Unknown game." });

  // build.py refuses two games whose names slug the same, so catch that here.
  const listed = await fetch(new URL("/games.json", request.url)).then(r => r.ok ? r.json() : []).catch(() => []);
  const clash = listed.find(g => (isNew || g.slug !== slug) && slugify(g.name) === slugify(game.name));
  if (clash) return reply(409, { error: `There's already a game called ${clash.name}.` });

  const path = `games/${slug}.md`;
  const current = await github(env, `${path}?ref=${BRANCH}`);
  if (!current.ok && current.status !== 404) return reply(502, { error: "Couldn't save right now. Try again in a minute." });
  if (isNew && current.ok) return reply(409, { error: `There's already a game called ${game.name}.` });
  if (!isNew && !current.ok) return reply(404, { error: "Couldn't find that game to edit." });
  const sha = current.ok ? (await current.json()).sha : undefined;

  const put = await github(env, path, {
    method: "PUT",
    body: JSON.stringify({
      message: `${isNew ? "Add" : "Edit"} ${game.name} from the site`,
      content: base64(toMarkdown(game)),
      branch: BRANCH,
      ...(sha ? { sha } : {}),
    }),
  });
  if (put.status === 409) return reply(409, { error: "Someone else just saved this game. Reload and try again." });
  if (!put.ok) return reply(502, { error: "Couldn't save right now. Try again in a minute." });
  return reply(200, { ok: true, slug });
}
