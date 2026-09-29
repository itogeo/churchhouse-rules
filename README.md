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

## Add or fix a game

On the site, click **Add a game**, or open a game and click **Edit**. Fill in what you know and press **Save**. Only the name and type are required. The site updates itself in a minute or two.

Saves go straight to the site, and every one is kept in this repo's history, so anything can be undone.

You can also edit the files here on GitHub if you'd rather: open [`games/`](games/), change a file, and propose the change.

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

- **type** is one of: Card, Word, Dice, Board, Outdoor, Trail, Indoor, Party, Icebreaker, Drinking
- **players** is a number (`4`), a range (`3-6`) or a minimum (`5+`)
- **minutes** is a plain number
- Links become clickable. Write them as a bare URL or as `[Werewolf app](https://...)`

No brand-name board games, please. Games you can play with a deck, dice, cups, or nothing at all.

## Run it yourself

```
python build.py          # builds the site into site/
python build.py --check  # just checks the game files
```

Python 3 only, no packages. Open `site/index.html` in a browser to look at it.

## Hosting

Cloudflare Pages (`churchhouse-rules`, served at churchhouserules.itogeospatial.com) builds the site from this repo on every change to `main`: build command `python3 build.py`, output folder `site`.

Saving from the site goes through `functions/api/save.js`, which runs only when someone presses Save. It checks the game with the same rules as `build.py` (`lib/game.js`) and commits the file to `main` with a GitHub token stored on the Pages project as `GITHUB_TOKEN` (fine-grained, this repo only, Contents: read and write).
