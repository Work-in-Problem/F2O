# Fable2Opus (F2O)

**Teach Opus-tier models the working processes of stronger models.**
สอน Claude Opus 4.8 ให้ทำงานด้วย "กระบวนการ" ระดับ Fable 5 — 13 process skills + กฎแกน always-on + hook กันหลอกว่าเสร็จ

> The honest tagline: *"Opus at its own ceiling, reliably — not Fable at half price."*
> Skills transfer **discipline**, not raw intelligence. ~50–60% of the observable behavior gap
> on short/medium tasks is process-shaped — that's the part this closes.

## ติดตั้ง / Install

**ช่องทาง A — Claude Code plugin (แนะนำ · ครบทุกชั้น: skills + กฎแกนฉีดอัตโนมัติ + hook):**

```
claude plugin marketplace add Work-in-Problem/F2O
claude plugin install f2o@f2o
```

หรือพิมพ์ `/plugin` ในแอปแล้วเลือก marketplace `Work-in-Problem/F2O` — เปิดใช้แล้วกฎ Layer 0 ถูกฉีดเข้า**ทุก** session
อัตโนมัติผ่าน SessionStart hook (ไม่ต้อง copy CLAUDE.md ลงโปรเจกต์) · ปิดชั่วคราว: disable plugin หรือ `FABLE2OPUS_HOOKS_OFF=1`

**ช่องทาง B — npx skills (เฉพาะ skills 13 ตัว, สำหรับสาย [skills.sh](https://www.skills.sh)):**

```
npx skills add Work-in-Problem/F2O --all -y -g
```

⚠️ ช่องทางนี้ไม่พกกฎแกน (Layer 0) กับ hook ไปด้วย — skills อ้างอิงกฎแกนอยู่ ต้อง copy `core/CLAUDE-core.md` + `core/constants.md`
เข้าโปรเจกต์เองตาม [USAGE.md](USAGE.md) §2.5

**คำสั่งควบคุม / Commands** (หลังติดตั้ง plugin — เปิดอัตโนมัติ):
`/f2o:off` soft-off (hooks เงียบ, สกิลยังใช้ได้) · `/f2o:on` เปิดกลับ · `/f2o:status` ดูสถานะ ·
hard-off: `claude plugin disable f2o@f2o`

**Shorthands** — เรียกสกิลเจาะจงเป็น primary ได้ทันที (ชื่อเต็มยังใช้ได้เสมอ):
`/f2o:vbc` verifying-before-claiming · `/f2o:ftt` finishing-the-turn · `/f2o:sfc` search-first-context ·
`/f2o:ptd` planning-to-done · `/f2o:scc` scoping-code-changes · `/f2o:rcb` root-causing-bugs ·
`/f2o:rvc` reviewing-code · `/f2o:dpw` delegating-parallel-work · `/f2o:mwm` managing-working-memory ·
`/f2o:ofr` outcome-first-reporting · `/f2o:pdv` producing-deliverables · `/f2o:efi` extracting-from-images ·
`/f2o:ivc` inventorying-capabilities
(สาย manual/npx: `cp -R "$SRC/aliases/." ~/.claude/skills/` → ได้ `/vbc` แบบไม่มี prefix)

**คู่มือเต็ม:** [USAGE.md](USAGE.md)

## What's inside / ส่วนประกอบ

| Layer | What | Where |
|---|---|---|
| **0 — Core rules** (always-on) | Claim audit — no "done" without tool-result evidence · autonomy triage (Class A/B/C) · single working-notes file · canonical constants C1–C18 · skill router | [core/CLAUDE-core.md](core/CLAUDE-core.md) + [core/constants.md](core/constants.md) — injected automatically by the plugin's SessionStart hook |
| **1 — Skills** (load on demand) | 13 process skills, each a distilled working process with trigger conditions, escape hatches, and cross-references | [skills/](skills/) |
| **2 — Enforcement** | `claim_gate.py` Stop hook — blocks "done/fixed/passes" messages whose last edit postdates the last verification, and promise-shaped endings ("I'll now…") · 28 tests | [hooks/](hooks/) |

## The 13 skills

| Skill | One line |
|---|---|
| `verifying-before-claiming` | Reproduce before fixing, drive the real flow, read output not exit codes, re-verify after every edit |
| `finishing-the-turn` | Decide small things silently, park real questions at turn end, never end on a promise |
| `search-first-context` | Volatile facts go to web/disk first; read the file and grep every call site before editing |
| `planning-to-done` | Extract every requirement into one checklist before the first edit; close with per-item evidence |
| `scoping-code-changes` | Surgical diffs, no drive-by refactors; adjacent issues get a "Noticed" line, not a fix |
| `root-causing-bugs` | Hypothesis ledger, one-variable experiments, statistical flake protocol, upstream root-cause walk |
| `reviewing-code` | Enumerate all findings first, filter only at reporting time; verify each finding against source |
| `delegating-parallel-work` | Fan out genuinely independent workstreams to sub-agents; trust-but-verify the union |
| `managing-working-memory` | One notes file that survives compaction; memory sweep at start, lesson harvest at end |
| `outcome-first-reporting` | Verdict first, "Not done" section early, every claim carries its evidence |
| `producing-deliverables` | Profile data before computing, cross-foot every headline number, reopen the file before "done" |
| `extracting-from-images` | Crop/zoom before reading dense regions, transcribe-then-verify, never guess an illegible cell |
| `inventorying-capabilities` | Inventory the actual tool surface before saying "can't" or improvising with bash |

## How it was built

Designed by Claude Fable 5 from Anthropic's own Fable 5 ↔ Opus 4.8 migration guidance: 10 capability
dimensions analyzed, skill specs drafted and adversarially critiqued (transferability skeptic +
completeness critic), authored under an ownership map (one owner per behavior — zero rule duplication
across ~120 rules), reviewed, and smoke-tested A/B on real Opus 4.8 runs. Full plan and honest
limitations: [PLAN.md](PLAN.md).

**Requirements:** Claude Code · Python 3 (hooks, stdlib only) · optional: pandas for one deliverables
script, an image tool (sips/ImageMagick/Pillow) for one vision script.

## License

[MIT](LICENSE) © 2026 Work in Problem
