# Churchhouse Rule$

Every game we play, written down. Drinking games, card games, dice, trail games, party games, icebreakers.

Each game is one plain text file in [`games/`](games/), and each file has seven numbered lines:

1. The gist
2. Players and time
3. Materials and links
4. Setup
5. How to play
6. Variations
7. Rulemaster

## Add a game

You need a free GitHub account. Nothing to install.

1. On the site, click **Add a game**. (Or open [`games/`](games/) here and choose **Add file > Create new file**.)
2. GitHub opens a copy of the template. Name the file after the game, like `kings-cup.md`.
3. Fill in what you know. Only `name` and `type` are required. Leave the rest blank if you're not sure.
4. Click **Commit changes**, then **Propose changes**, then **Create pull request**.

Once it's approved, the site updates itself within a couple of minutes.

## Fix or add to a game

Open the game on the site and click **Edit**. That opens its file on GitHub. Make your changes and propose them the same way.

## The file format

```
---
name: Hearts
type: Card
players: 3-6
minutes: 45
---

1. The gist
Trick-taking where you avoid points...

2. Players and time
Best with 4

3. Materials and links
One standard deck
Werewolf app https://example.com

4. Setup
...

5. How to play
...

6. Variations
...

7. Rulemaster
Traditional
```

- **type** is one of: Drinking, Card, Dice, Board, Word, Party, Icebreaker, Outdoor, Indoor, Trail
- **players** is a number (`4`), a range (`3-6`) or a minimum (`5+`)
- **minutes** is a plain number
- A game with nothing under **5. How to play** shows as *incomplete*
- Links become clickable. Write them as a bare URL or as `[Werewolf app](https://...)`

No brand-name board games, please. Games you can play with a deck, dice, cups, or nothing at all.

## Run it yourself

```
python build.py          # builds the site into site/
python build.py --check  # just checks the game files
```

Python 3 only, no packages. Open `site/index.html` in a browser to look at it.

## Hosting

A Cloudflare Worker (`churchhouse-rules`, static files only) builds the site from this repo on every merge to `main`: build command `python3 build.py`, deploy command `npx wrangler deploy`. Settings are in `wrangler.jsonc`.
