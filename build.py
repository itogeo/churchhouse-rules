"""Build the Churchhouse Rule$ site from the plain text files in games/.

    python build.py           # build into site/
    python build.py --check   # only validate the game files (used on pull requests)

Standard library only. No installs needed.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAMES = ROOT / "games"
SITE = ROOT / "site"

TITLE = "Churchhouse Rule$"
REPO_URL = "https://github.com/itogeo/churchhouse-rules"
GITHUB_MARK = ('<svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')
TYPES = ["Drinking", "Card", "Dice", "Board", "Word", "Party",
         "Icebreaker", "Outdoor", "Indoor", "Trail"]
SECTIONS = ["The gist", "Players and time", "Materials and links", "Setup",
            "How to play", "Variations", "Rulemaster"]
TIMES = [("any", "Any"), ("15", "15 min or less"), ("30", "30 or less"),
         ("60", "An hour or less"), ("long", "Over an hour")]


# ---------- reading ----------

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "game"


def parse_game(path):
    """Return (game dict, list of problems)."""
    problems = []
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    if not m:
        return None, ["needs the --- header block at the top (copy games/_TEMPLATE.md)"]
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    body = m.group(2)

    name = meta.get("name", "")
    if not name:
        problems.append("name is empty")
    gtype = meta.get("type", "").strip().title()
    if gtype not in TYPES:
        problems.append(f"type '{meta.get('type', '')}' should be one of: {', '.join(TYPES)}")

    lo = hi = None
    players = meta.get("players", "")
    if players:
        pm = re.fullmatch(r"(\d+)\s*(?:-\s*(\d+)|(\+))?", players)
        if not pm:
            problems.append(f"players '{players}' should look like 4, 3-6 or 5+")
        else:
            lo = int(pm.group(1))
            hi = int(pm.group(2)) if pm.group(2) else (None if pm.group(3) else lo)
            if hi is not None and hi < lo:
                lo, hi = hi, lo

    minutes = None
    if meta.get("minutes"):
        if meta["minutes"].isdigit():
            minutes = int(meta["minutes"])
        else:
            problems.append(f"minutes '{meta['minutes']}' should be a plain number")

    # split body into the seven numbered sections
    sections = [""] * 7
    current = None
    for line in body.splitlines():
        hm = re.match(r"^\s*([1-7])\.\s*(.*)$", line)
        if hm and hm.group(2).strip().lower().rstrip(":") in [s.lower() for s in SECTIONS] + [""]:
            current = int(hm.group(1)) - 1
            continue
        if current is not None:
            sections[current] += line + "\n"
    sections = [s.strip() for s in sections]

    game = {
        "slug": path.stem, "name": name, "type": gtype,
        "lo": lo, "hi": hi, "minutes": minutes, "sections": sections,
        "incomplete": not sections[4],
    }
    return game, problems


def load_games():
    games, errors = [], []
    for p in sorted(GAMES.glob("*.md")):
        if p.name.startswith("_"):
            continue
        g, probs = parse_game(p)
        for pr in probs:
            errors.append(f"games/{p.name}: {pr}")
        if g and not probs:
            games.append(g)
    return games, errors


# ---------- rendering ----------

def esc(s):
    return html.escape(str(s or ""), quote=True)


def rich(text):
    """Plain text -> HTML: keep line breaks, turn links into links."""
    out = []
    for para in re.split(r"\n\s*\n", text.strip()):
        line_html = []
        for line in para.splitlines():
            parts, last = [], 0
            for m in re.finditer(r"\[([^\]]+)\]\((https?://[^)\s]+)\)|(https?://\S+)", line):
                parts.append(esc(line[last:m.start()]))
                label, url = (m.group(1), m.group(2)) if m.group(2) else (m.group(3), m.group(3))
                parts.append(f'<a href="{esc(url)}" rel="noopener">{esc(label)}</a>')
                last = m.end()
            parts.append(esc(line[last:]))
            line_html.append("".join(parts))
        out.append("<p>" + "<br>".join(line_html) + "</p>")
    return "\n".join(out)


def players_time(g):
    bits = []
    lo, hi = g["lo"], g["hi"]
    if lo and hi:
        bits.append(f"{lo} players" if lo == hi else f"{lo} to {hi} players")
    elif lo:
        bits.append(f"{lo} or more players")
    if g["minutes"]:
        bits.append(f"about {g['minutes']} minutes")
    return ", ".join(bits)


CSS = """
:root{--paper:#fff;--ink:#000;--faint:#6b6b6b;--line:#000;--hush:#f0f0f0;
  --type:"Courier Prime","Courier New",Courier,ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root{--paper:#000;--ink:#fff;--faint:#9a9a9a;--line:#fff;--hush:#1a1a1a;color-scheme:dark}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 var(--type);padding:0 16px}
.wrap{max-width:700px;margin:0 auto;padding-block:36px 72px;display:flex;flex-direction:column;gap:26px}
a{color:var(--ink)}
button,input,select,textarea{font:inherit;color:var(--ink)}
button{cursor:pointer}
header{display:flex;flex-wrap:wrap;align-items:end;justify-content:space-between;gap:14px;border-bottom:3px double var(--line);padding-bottom:12px}
h1{font:700 clamp(2.1rem,8vw,3rem)/1 var(--type);letter-spacing:.04em;text-transform:uppercase;margin:0}
h1 a{text-decoration:none}
.btn{display:inline-block;background:var(--ink);color:var(--paper);border:1.5px solid var(--ink);padding:7px 12px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;font-size:.85rem;text-decoration:none}
.btn.ghost{background:transparent;color:var(--ink)}
.btn:hover{text-decoration:underline}
:focus-visible{outline:2px dashed var(--ink);outline-offset:3px}
.tools{display:flex;flex-direction:column;gap:12px;border:1.5px solid var(--line);padding:14px}
.tline{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px}
.tl{font-weight:700;text-transform:uppercase;font-size:.78rem;letter-spacing:.08em;min-width:5.5em}
#q{flex:1;min-width:0;border:0;border-bottom:1.5px solid var(--line);background:transparent;padding:4px 2px;border-radius:0}
.chip{background:transparent;border:1px solid transparent;padding:2px 5px;font-size:.9rem}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.chip[aria-pressed="true"] small{color:var(--paper)}
.chip small{color:var(--faint)}
.num-in{display:inline-flex;align-items:center;border:1.5px solid var(--line)}
.num-in button{background:transparent;border:0;width:2rem;height:1.9rem;font-weight:700}
.num-in output{min-width:3.2em;text-align:center;font-variant-numeric:tabular-nums;border-inline:1.5px solid var(--line);line-height:1.9rem}
.note{font-size:.82rem;color:var(--faint)}
.groups{display:flex;flex-direction:column;gap:28px}
.group h2{font:700 1.5rem/1.1 var(--type);text-transform:uppercase;letter-spacing:.1em;margin:0 0 4px;display:flex;justify-content:space-between;border-bottom:1.5px solid var(--line);padding-bottom:6px}
.group h2 small{font-weight:400;letter-spacing:0;color:var(--faint);font-size:1rem}
.list{list-style:none;margin:0;padding:0}
.row{display:block;padding:9px 2px;border-bottom:1px dotted var(--faint);text-decoration:none;font-weight:700;font-size:1.05rem}
.row:hover{background:var(--hush)}
.stub{font-size:.7rem;color:var(--faint);margin-left:8px;text-transform:uppercase;letter-spacing:.06em;font-weight:400}
.empty{border:1.5px dashed var(--line);padding:24px;text-align:center}
.sheet{border:1.5px solid var(--line);padding:22px 20px;display:flex;flex-direction:column;gap:14px}
.top{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px;align-items:start}
.sheet h2{font:700 clamp(1.6rem,6vw,2.1rem)/1.1 var(--type);text-transform:uppercase;margin:0;text-wrap:balance}
.cat{font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;color:var(--faint)}
ol.seven{list-style:none;margin:0;padding:0}
ol.seven li{display:grid;grid-template-columns:2rem 1fr;gap:8px;padding:12px 0;border-top:1px solid var(--line)}
.num{font-weight:700;font-size:1.2rem;line-height:1.3}
.lbl{font-weight:700;font-size:.74rem;text-transform:uppercase;letter-spacing:.1em;display:block;margin-bottom:3px}
.val{min-width:0;overflow-wrap:anywhere}
.val p{margin:0 0 .6em}.val p:last-child{margin:0}
.blank{color:var(--faint);font-style:italic}
.actions{display:flex;flex-wrap:wrap;gap:8px}
.form{display:flex;flex-direction:column;gap:14px}
.field{display:flex;flex-direction:column;gap:4px}
.field input,.field select,.field textarea{background:transparent;border:1.5px solid var(--line);border-radius:0;padding:6px 8px;width:100%}
.field textarea{min-height:5.5em;resize:vertical}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.trap{position:absolute;left:-9999px}
.msg{border:1.5px solid var(--line);padding:10px 12px}
footer{border-top:1.5px solid var(--line);padding-top:12px;font-size:.85rem;color:var(--faint)}
footer a{color:var(--faint);display:inline-flex;align-items:center;gap:8px}
"""

JS = """
(function(){
  var people=0,time='any',type='All',query='';
  var rows=[].slice.call(document.querySelectorAll('.row'));
  var groups=[].slice.call(document.querySelectorAll('.group'));
  var TIME={any:function(){return true},'15':function(m){return m<=15},'30':function(m){return m<=30},'60':function(m){return m<=60},long:function(m){return m>60}};
  function num(v){return v===''?null:+v}
  function apply(){
    var hidden=0,counts={All:0};
    rows.forEach(function(r){
      var lo=num(r.dataset.lo),hi=num(r.dataset.hi),m=num(r.dataset.min),t=r.dataset.type;
      var okP=!people||(lo!==null&&people>=lo&&(hi===null||people<=hi));
      var okT=time==='any'||(m!==null&&TIME[time](m));
      var okQ=!query||r.dataset.text.indexOf(query)>-1;
      if(okQ&&(!okP||!okT)&&((people&&lo===null)||(time!=='any'&&m===null)))hidden++;
      var base=okP&&okT&&okQ;
      if(base){counts.All++;counts[t]=(counts[t]||0)+1}
      r.parentNode.hidden=!(base&&(type==='All'||t===type));
    });
    groups.forEach(function(g){g.hidden=!g.querySelector('li:not([hidden])');var c=g.querySelector('h2 small');c.textContent=g.querySelectorAll('li:not([hidden])').length});
    document.querySelectorAll('[data-f]').forEach(function(b){b.querySelector('small').textContent=counts[b.dataset.f]||0;b.setAttribute('aria-pressed',b.dataset.f===type)});
    document.querySelectorAll('[data-t]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.t===time)});
    document.getElementById('pv').textContent=people||'any';
    var n=document.getElementById('hiddenNote');n.hidden=!hidden;n.textContent=hidden+' incomplete game'+(hidden>1?'s':'')+' hidden';
    document.getElementById('none').hidden=rows.some(function(r){return !r.parentNode.hidden});
  }
  document.getElementById('pm').onclick=function(){people=Math.max(0,people-1);apply()};
  document.getElementById('pp').onclick=function(){people=Math.min(50,people+1);apply()};
  document.querySelectorAll('[data-f]').forEach(function(b){b.onclick=function(){type=b.dataset.f;apply()}});
  document.querySelectorAll('[data-t]').forEach(function(b){b.onclick=function(){time=b.dataset.t;apply()}});
  var qs=document.getElementById('qs'),q=document.getElementById('q'),qx=document.getElementById('qx');
  qs.onclick=function(){qs.hidden=true;q.hidden=false;qx.hidden=false;q.focus()};
  qx.onclick=function(){qs.hidden=false;q.hidden=true;qx.hidden=true;q.value='';query='';apply()};
  q.oninput=function(){query=q.value.toLowerCase().trim();apply()};
  document.querySelector('.tools').hidden=false;
  apply();
})();
"""


EDIT_JS = """
(function(){
  var f=document.getElementById('form'),msg=document.getElementById('msg'),save=document.getElementById('save');
  var slug=new URLSearchParams(location.search).get('game')||'';
  function show(t){msg.textContent=t;msg.hidden=false;msg.scrollIntoView({block:'nearest'})}
  function players(g){if(!g.lo)return '';if(g.hi===null)return g.lo+'+';return g.lo===g.hi?''+g.lo:g.lo+'-'+g.hi}
  if(slug){
    document.getElementById('heading').textContent='Edit game';
    fetch('games.json').then(function(r){return r.json()}).then(function(games){
      var g=games.filter(function(x){return x.slug===slug})[0];
      if(!g){show('Could not find that game.');save.disabled=true;return}
      document.title='Edit '+g.name;
      document.getElementById('back').href='games/'+slug+'.html';
      f.name.value=g.name;f.type.value=g.type;f.players.value=players(g);f.minutes.value=g.minutes||'';
      g.sections.forEach(function(s,i){f['s'+i].value=s});
    }).catch(function(){show('Could not load the game. Reload to try again.')});
  }
  f.onsubmit=function(e){
    e.preventDefault();save.disabled=true;msg.hidden=true;
    var body={slug:slug,name:f.name.value,type:f.type.value,players:f.players.value,minutes:f.minutes.value,
      website:f.website.value,sections:[0,1,2,3,4,5,6].map(function(i){return f['s'+i].value})};
    fetch('/api/save',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)})
      .then(function(r){return r.json().catch(function(){return {error:'Could not save right now.'}})})
      .then(function(res){
        if(res.error){show(res.error);save.disabled=false;return}
        f.hidden=true;
        show('Saved. The site updates in a minute or two.');
        var a=document.createElement('a');a.className='btn ghost';a.textContent='All games';a.href='./';
        msg.appendChild(document.createElement('br'));msg.appendChild(a);
      })
      .catch(function(){show('Could not save right now. Check your connection and try again.');save.disabled=false});
  };
})();
"""


def page(title, body, script=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap">
<style>{CSS}[hidden]{{display:none!important}}</style>
</head>
<body>
<div class="wrap">
{body}
<footer><a href="{REPO_URL}">{GITHUB_MARK}Contribute on GitHub</a></footer>
</div>
{f"<script>{script}</script>" if script else ""}
</body>
</html>
"""


def render_index(games):
    counts = {t: sum(g["type"] == t for g in games) for t in TYPES}
    type_chips = [f'<button type="button" class="chip" data-f="All" aria-pressed="true">All <small>{len(games)}</small></button>']
    type_chips += [f'<button type="button" class="chip" data-f="{t}" aria-pressed="false">{t} <small>{counts[t]}</small></button>'
                   for t in TYPES if counts[t]]
    time_chips = [f'<button type="button" class="chip" data-t="{k}" aria-pressed="{str(k == "any").lower()}">{v}</button>'
                  for k, v in TIMES]
    groups = []
    for t in TYPES:
        items = sorted((g for g in games if g["type"] == t), key=lambda g: g["name"].lower())
        if not items:
            continue
        lis = []
        for g in items:
            text = " ".join([g["name"], g["type"]] + g["sections"]).lower()
            lis.append(
                f'<li><a class="row" href="games/{g["slug"]}.html" data-type="{t}" '
                f'data-lo="{g["lo"] or ""}" data-hi="{g["hi"] or ""}" data-min="{g["minutes"] or ""}" '
                f'data-text="{esc(text)}">{esc(g["name"])}'
                f'{"<span class=stub>incomplete</span>" if g["incomplete"] else ""}</a></li>')
        groups.append(f'<section class="group"><h2>{t}<small>{len(items)}</small></h2>'
                      f'<ul class="list">{"".join(lis)}</ul></section>')
    body = f"""<header>
  <h1>{esc(TITLE)}</h1>
  <a class="btn" href="edit.html">Add a game</a>
</header>
<div class="tools" hidden>
  <div class="tline"><button type="button" class="btn ghost" id="qs">Search</button><input id="q" type="search" aria-label="Search" hidden><button type="button" class="btn ghost" id="qx" hidden>Close</button></div>
  <div class="tline"><span class="tl">People</span><span class="num-in"><button type="button" id="pm" aria-label="Fewer people">-</button><output id="pv">any</output><button type="button" id="pp" aria-label="More people">+</button></span></div>
  <div class="tline"><span class="tl">Time</span>{"".join(time_chips)}</div>
  <div class="tline"><span class="tl">Type</span>{"".join(type_chips)}</div>
  <span class="note" id="hiddenNote" hidden></span>
</div>
<main class="groups">
{"".join(groups)}
<div class="empty" id="none" hidden>No games fit those filters.</div>
</main>"""
    return page(TITLE, body, JS)


def render_game(g):
    lines = []
    for i, label in enumerate(SECTIONS):
        text = g["sections"][i]
        if i == 1:
            text = "\n".join(x for x in [players_time(g), text] if x)
        val = rich(text) if text else '<p class="blank">Not written down yet</p>'
        lines.append(f'<li><span class="num">{i + 1}</span><div class="val"><span class="lbl">{label}</span>{val}</div></li>')
    body = f"""<header>
  <h1><a href="../">{esc(TITLE)}</a></h1>
</header>
<article class="sheet">
  <div class="top">
    <div><div class="cat">{esc(g["type"])}</div><h2>{esc(g["name"])}</h2></div>
    <div class="actions"><a class="btn ghost" href="../">All games</a><a class="btn" href="../edit.html?game={esc(g['slug'])}">Edit</a></div>
  </div>
  <ol class="seven">{"".join(lines)}</ol>
</article>"""
    return page(f"{g['name']} | {TITLE}", body)


def render_edit():
    types = "".join(f'<option>{t}</option>' for t in TYPES)
    hints = ["What makes this game different from every other game.",
             "Anything like \"best with 4\" or \"teams of 2\".",
             "What you need. Links on their own line.",
             "How to deal, seat, or split into teams.",
             "The actual rules.",
             "House rules and other versions.",
             "Who invented it, taught it, or settles arguments."]
    fields = "".join(
        f'<label class="field"><span class="lbl">{i + 1}. {label}</span>'
        f'<textarea name="s{i}" placeholder="{esc(hints[i])}"></textarea></label>'
        for i, label in enumerate(SECTIONS))
    body = f"""<header>
  <h1><a href="./">{esc(TITLE)}</a></h1>
</header>
<article class="sheet">
  <div class="top"><h2 id="heading">Add a game</h2><a class="btn ghost" id="back" href="./">Cancel</a></div>
  <div class="msg" id="msg" role="status" hidden></div>
  <form class="form" id="form">
    <label class="field"><span class="lbl">Name</span><input name="name" required maxlength="80" autocomplete="off"></label>
    <label class="field"><span class="lbl">Type</span><select name="type" required><option value="">Pick one</option>{types}</select></label>
    <div class="pair">
      <label class="field"><span class="lbl">Players</span><input name="players" placeholder="4, 3-6 or 5+" autocomplete="off"></label>
      <label class="field"><span class="lbl">Minutes</span><input name="minutes" inputmode="numeric" placeholder="30" autocomplete="off"></label>
    </div>
    {fields}
    <label class="trap" aria-hidden="true">Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label>
    <div class="actions"><button class="btn" id="save" type="submit">Save</button></div>
  </form>
</article>"""
    return page(f"Edit | {TITLE}", body, EDIT_JS)


def main():
    games, errors = load_games()
    slugs = {}
    for g in games:
        s = slugify(g["name"])
        if s in slugs:
            errors.append(f"games/{g['slug']}.md and games/{slugs[s]}.md look like the same game")
        slugs[s] = g["slug"]
    if errors:
        print("Some game files need fixing:\n  " + "\n  ".join(errors))
        sys.exit(1)
    print(f"{len(games)} games look good.")
    if "--check" in sys.argv:
        return
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "games").mkdir(parents=True)
    (SITE / "index.html").write_text(render_index(games), encoding="utf-8")
    (SITE / "edit.html").write_text(render_edit(), encoding="utf-8")
    for g in games:
        (SITE / "games" / f"{g['slug']}.html").write_text(render_game(g), encoding="utf-8")
    (SITE / "games.json").write_text(json.dumps(games, indent=1), encoding="utf-8")
    cname = ROOT / "CNAME"
    if cname.exists():
        shutil.copy(cname, SITE / "CNAME")
    print(f"Built site/ with {len(games)} game pages.")


if __name__ == "__main__":
    main()
