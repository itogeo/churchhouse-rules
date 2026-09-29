// Turn a submitted edit form into a game file, using the same rules as build.py,
// so a save from the site can never produce a file that breaks the build.

export const TYPES = ["Drinking", "Card", "Dice", "Board", "Word", "Party",
  "Icebreaker", "Outdoor", "Indoor", "Trail"];
export const SECTIONS = ["The gist", "Players and time", "Materials and links", "Setup",
  "How to play", "Variations", "Rulemaster"];

const MAX_NAME = 80;
const MAX_SECTION = 6000;

export function slugify(text) {
  return String(text).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "game";
}

function oneLine(v) {
  return String(v ?? "").replace(/[\r\n]+/g, " ").trim();
}

// A line like "5." or "5. How to play" inside a section would start a new section
// when build.py reads the file back, so write it as "5)" instead.
const HEADING = new RegExp(`^(\\s*[1-7])\\.(\\s*(?:${SECTIONS.join("|")})?:?\\s*)$`, "i");

function sectionText(v) {
  return String(v ?? "").replace(/\r\n?/g, "\n").trim()
    .split("\n").map(line => line.replace(HEADING, "$1)$2")).join("\n");
}

// Returns {game, problems}. game holds the cleaned fields.
export function validate(input) {
  const problems = [];
  const name = oneLine(input.name);
  const type = oneLine(input.type);
  const players = oneLine(input.players).replace(/\s+/g, "");
  const minutes = oneLine(input.minutes);
  const raw = Array.isArray(input.sections) ? input.sections : [];
  const sections = SECTIONS.map((_, i) => sectionText(raw[i]));

  if (!name) problems.push("The game needs a name.");
  if (name.length > MAX_NAME) problems.push(`Keep the name under ${MAX_NAME} characters.`);
  if (!TYPES.includes(type)) problems.push("Pick a type.");
  if (players && !/^\d+(-\d+|\+)?$/.test(players)) problems.push("Players should look like 4, 3-6 or 5+.");
  if (minutes && !/^\d+$/.test(minutes)) problems.push("Minutes should be a plain number.");
  sections.forEach((s, i) => {
    if (s.length > MAX_SECTION) problems.push(`"${SECTIONS[i]}" is too long.`);
  });
  return { game: { name, type, players, minutes, sections }, problems };
}

export function toMarkdown(g) {
  const head = `---\nname: ${g.name}\ntype: ${g.type}\nplayers: ${g.players}\nminutes: ${g.minutes}\n---\n`;
  const body = SECTIONS.map((label, i) => `${i + 1}. ${label}\n${g.sections[i]}\n`).join("\n");
  return `${head}\n${body}`;
}
