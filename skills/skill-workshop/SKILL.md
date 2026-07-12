# Skill Workshop

Create a new Creo skill from scratch, or improve an existing one based on what you learned running it. The goal: skills that get sharper every time they're used, not ones that stay frozen at first-draft quality.

---

## How to invoke

```
/skill-workshop create <what this skill should do>
/skill-workshop improve <skill-name> [what went wrong / what to add]
/skill-workshop list
```

- **`create`** — write a new `skills/<name>.md` from scratch, following the quality checklist below.
- **`improve`** — read an existing skill, apply a specific fix, save an updated version, and report exactly what changed.
- **`list`** — list every file in `skills/` with a one-line summary of each (read the first non-blank non-heading line).

---

## Principles (non-negotiable defaults)

These apply to every skill Creo writes or touches:

**1. Instructions, not scripts.**
A well-written SKILL.md that tells the agent *how* to use a built-in tool (Bash, web_fetch, figma-write, etc.) almost always beats a bundled Python or shell script. Built-in tools have no attack surface, no dependencies, no version drift. Only reach for a script when a built-in genuinely can't do the job — and when you do, keep it in `skills/scripts/<skill-name>/`, read every line before running, and document what it does inline.

**2. Zero external dependencies by default.**
If a skill requires an API key, an npm package, a pip install, or a network call to a third-party service, that's a dependency to justify. Name it explicitly in the skill file. A skill that works with only what's already on the machine is always more resilient.

**3. Write intermediate state to files.**
Skills that span multiple steps should checkpoint progress — don't hold everything in session memory. Session context can compact. Files can't. Use `ACTIVE-TASK.md` in the workspace root as working memory for multi-step tasks: write the current step and its result before moving to the next. Clean it up when the task is done.

**4. Fail loudly.**
A skill should surface what it found — including gaps, ambiguities, or partial failures — in the Slack reply. A silent partial success is worse than a stated failure because it looks done.

**5. Scope-creep prevention.**
Do exactly what the skill says. Don't expand into adjacent work that wasn't asked for. If related problems are spotted, mention them in the reply without fixing them.

**6. Search memory, don't load it.**
When a skill step needs to check standing knowledge, use `Bash grep -i "<keyword>"` over the relevant topic file rather than reading it in full. Same for `people/<id>/log.md` — grep for the specific pattern you need. Loading full files burns context on content that won't matter for the task. Only read a file whole when you genuinely need its full content (e.g. writing a replacement version of it).

---

## Creating a skill

### Step 1 — Name and scope it

Pick a name that describes the *job*, not the implementation (`design-review`, not `check-figma-things`). One skill = one repeatable job. If the ask covers two genuinely different jobs, create two files.

Check `skills/` first — don't duplicate an existing skill. If a close one exists, the answer might be `/skill-workshop improve <existing>` instead.

### Step 2 — Determine what tools it actually needs

List the built-in tools the skill will use. For each:
- **Does it already work without setup?** If yes, just reference it.
- **Does it need auth/config?** Document the requirement explicitly in the skill file.
- **Is a script genuinely necessary?** Justify it; put it in `skills/scripts/<skill-name>/`.

Common patterns that need no scripts:
| Task | How |
|------|-----|
| Web research | `WebSearch` + `WebFetch` |
| Figma read | `get_design_context`, `get_screenshot` (figma-write) |
| Figma write | `use_figma` (load `/figma-use` first) |
| File ops | `Bash` (read, write, move, rename) |
| Reddit/public JSON | `WebFetch` on `<url>.json` |
| Stock data | `Bash` + yfinance (already installed) |

### Step 3 — Write the skill file

Structure every skill the same way:

```markdown
# <Skill Name>

One-sentence description of the job this skill does.

Any hard constraints go here (e.g. "Read-only — never calls use_figma").

---

## How to invoke

`/<skill-name> <what to pass>`

## Step 1 — <first step name>

...

## Step N — <last step name>

...

## Output

Exactly what gets posted to Slack / saved to disk.

## What not to do

Hard prohibitions. Explicit > implicit.
```

Keep sections short. Every step should have a clear trigger ("when X is available, do Y") rather than open-ended prose. If a step references a token or standard, link to the source (`skills/tokens.md`, `skills/file-naming-and-versioning.md`, etc.) rather than duplicating it inline.

### Step 4 — Run the quality checklist

Before saving, verify all items in **Quality Checklist** below.

### Step 5 — Save and report

- Save to `skills/<name>.md`.
- Reply in Slack with: the skill name, a one-sentence summary, the invocation syntax, and any constraints worth knowing up front.
- No need to save to the person's deliverables folder — skills live in `skills/` and belong to the workspace, not a single person.

---

## Improving a skill

Run this after a skill produces a wrong result, skips an important case, or when someone reports something it should do differently.

### Step 1 — Read the current skill

Read `skills/<name>.md` in full. Don't paraphrase from memory — re-read it.

### Step 2 — Understand the specific failure

The ask text after the skill name is the diagnosis. Take it at face value. If it's vague ("it didn't work right"), ask for a concrete example in the Slack reply instead of guessing.

### Step 3 — Write the minimal fix

Find the exact section that caused the failure. Make the smallest edit that addresses the root cause — don't reorganize the whole file in response to a one-line fix. A good improvement edit:
- Changes one section or adds one section
- Is visible in a short diff
- Doesn't silently change behavior in other scenarios

### Step 4 — Save and report the diff

Overwrite `skills/<name>.md` with the improved version. In the Slack reply, show exactly what changed: quote the old text and the new text side-by-side. Don't just say "updated."

Example reply format:
```
Updated `skills/design-review.md`.

Changed:
— "Check typography compliance" (Step 3)

Before:
  Body text minimum is 16px desktop.

After:
  Body text minimum is 16px desktop / 14px mobile. Also check CTA
  button labels: minimum 14px at any breakpoint, never below.

Why: The skill was passing CTAs at 12px on mobile because the mobile
floor wasn't stated.
```

---

## Quality checklist

Before shipping a new or updated skill, confirm every item:

- [ ] **Single responsibility** — one job, one file. If it does two things, split it.
- [ ] **No orphan dependencies** — every tool, script, or external service it references either already exists or is documented as a prerequisite.
- [ ] **Hard constraints are explicit** — if the skill must never call a write tool, that's the *first* thing in the file, not a footnote.
- [ ] **Output is specified** — the Slack reply format and any files it saves are described, not left to the agent to invent.
- [ ] **"What not to do" section exists** — a skill with no prohibitions tends to drift in scope on edge cases.
- [ ] **Invocation syntax is in the file** — someone should be able to invoke it correctly from reading only the skill file, without checking `skills/README.md`.
- [ ] **No duplicated content from other skills** — if the skill needs a rule that already lives in `skills/tokens.md` or `skills/file-naming-and-versioning.md`, reference it, don't copy it.
- [ ] **Checkpoints for multi-step skills** — any skill with 3+ steps that can fail mid-way uses `ACTIVE-TASK.md` for state, not session memory.

---

## Notes on the improvement loop

Skills get better over time only if failures get reported. The mechanism is simple:

1. A skill produces a wrong/incomplete result.
2. The person replies (or Creo notices and flags it): "this missed X" or "step 3 was unclear."
3. `/skill-workshop improve <name> <what was wrong>` applies the fix.

There's no automated retrospective — the improvement signal has to come from an actual run. What you can do as Creo: at the end of any skill task where something felt off (a step was ambiguous, a tool behaved unexpectedly, an edge case wasn't covered), flag it in the Slack reply. Example:

> "Done. One thing to note for next time: this skill doesn't have guidance for assets where the Figma URL points to a page with 20+ frames — I reviewed all of them, but that might not always be the right call. Worth adding a scoping step to `design-review.md` if this comes up again."

That surfaces the improvement candidate without making an unsolicited edit to the skill.
