# Fable2Opus — แผนแม่บท

> **เป้าหมาย:** เขียนชุด Claude Code skills ที่ถ่ายทอด "กระบวนการทำงาน" ของ Claude Fable 5 ให้ Claude Opus 4.8 เพื่อให้ Opus 4.8 ทำงานได้ใกล้เคียง Fable 5 มากที่สุด
>
> **Tagline ที่ซื่อสัตย์:** *"Opus ที่ทำงานเต็มเพดานของตัวเองอย่างสม่ำเสมอ" — ไม่ใช่ "Fable ในราคาครึ่งเดียว"*
>
> จัดทำ 2026-07-09 โดย Claude Fable 5 · อ้างอิงจาก multi-agent workflow (24 agents: research 2, วิเคราะห์ 10 มิติ, ออกแบบ 10 specs, critic 2)

---

## 1. Fable 5 เก่งกว่า Opus 4.8 ตรงไหน (ผลวิเคราะห์)

### 1.1 ตัวเลข benchmark (ที่ Anthropic เผยแพร่)

| Benchmark | Fable 5 | Opus 4.8 | ส่วนต่าง |
|---|---|---|---|
| SWE-bench Pro (agentic coding) | 80.3% | 69.2% | +11.1 pts |
| FrontierCode Diamond (โจทย์ยากสุด) | 29.3% | 13.4% | **+15.9 pts (เกิน 2 เท่า)** |
| Vision document reasoning (GDP.pdf) | 29.8% | 22.5% | +7.3 pts |
| Coding average (BenchLM) | 85.6 | 76.4 | +9.2 |
| Agentic average (BenchLM) | 85.3 | 80.3 | +5.0 |
| Math | 97.6 | 96.7 | +0.9 |

**ข้อสังเกตสำคัญ:** ช่องว่างกระจุกตัวที่ *งาน agentic ระยะยาว/โจทย์ยาก* — งานสั้นที่ scope ชัด สองรุ่นทำได้ใกล้กันมาก (คณิตต่างแค่ 0.9 pts) นี่คือเหตุผลที่โปรเจกต์นี้มีความหวัง: ช่องว่างส่วนใหญ่อยู่ที่ "กระบวนการ" ไม่ใช่ "ความฉลาดดิบ" ล้วนๆ
**Caveat:** เลข SWE-bench Pro มาจาก scaffolding ของ Anthropic เอง — การประเมินอิสระ (Epoch AI) ยังไม่ออก ณ มิ.ย. 2026

### 1.2 จุดแข็ง 7 ด้านที่ Anthropic ระบุอย่างเป็นทางการ

1. **Long-horizon autonomy** — รันงานต่อเนื่องหลายชั่วโมง/ข้ามคืนโดยไม่ต้องแก้ทาง (Stripe: migrate โค้ด Ruby 50 ล้านบรรทัดใน 1 วัน)
2. **First-shot correctness** — งานซับซ้อนที่ spec ชัด ทำถูกในรอบเดียว
3. **Vision** — ภาพหนาแน่น/คุณภาพต่ำ (ถูกเทรนให้ใช้ bash/crop จัดการภาพเบลอ/กลับหัวเอง)
4. **Enterprise deliverables** — วิเคราะห์การเงิน, spreadsheet, slides, เอกสาร ครบวงจร
5. **Code review & debugging** — recall และ precision สูงกว่า, จับ flaky test ได้ (ไม่ประกาศ "fixed" หลังรันผ่านครั้งเดียว)
6. **Navigating ambiguity** — ตีความคำขอกำกวมได้ดีกว่า
7. **Sub-agent delegation** — กระจายงานขนาน + สื่อสาร async กับ agent ลูกได้ต่อเนื่อง

### 1.3 จุดอ่อนของ Opus 4.8 ที่ Anthropic เขียนไว้เอง (= เป้าโจมตีของ skills)

| จุดอ่อน | หลักฐาน |
|---|---|
| ใช้ subagents / memory / custom tools **น้อยเกินไป** เว้นแต่บอกชัดว่า "เมื่อไหร่" ต้องใช้ | migration guide ระบุตรงๆ + แนะนำ fix ด้วย instruction |
| Search triggering แบบ high-precision/**low-recall** — ตอบจากความจำทั้งที่ควรค้น | migration guide |
| **ถามมากเกิน** — ขออนุญาตเรื่องเล็ก, จบงานด้วย "Want me to also…?" | instruction แก้ ask-rate ได้ ~12 จุด โดย over-reach ไม่เพิ่ม |
| ทำตามคำสั่ง conservative **ตรงตัวเกิน** จน recall ตกในงาน code review | migration guide ("only report high-severity" → recall ร่วง) |
| หยุดก่อนงานเสร็จ / จบเทิร์นด้วย "แผน" แทน "การกระทำ" | documented early-stopping |
| ต้องได้ spec เต็มตั้งแต่ต้นถึงจะทำงานยาวได้ดี | migration guide |

### 1.4 หลักฐานชิ้นสำคัญที่สุด 2 ชิ้น

- **ข่าวดี:** ทั้งสองรุ่น "ทำตาม instruction ชัดๆ ได้ดีมาก" — Anthropic วัดเองว่า instruction เดียวลด ask-rate ได้ ~12 จุด และ claim-audit rule แทบกำจัด fabricated progress claims → **process gap ปิดได้ด้วย skill จริง**
- **ข่าวร้าย (ขีดจำกัดแท้จริง):** ผลทดลอง Slay the Spire — ให้ memory surface *เหมือนกันทุกอย่าง* Fable 5 พัฒนาขึ้น **3 เท่า** ของ Opus 4.8 → ต่อให้สอน "กระบวนการ" เหมือนกัน สิ่งที่แต่ละรุ่น *สกัดออกมาจากกระบวนการ* ไม่เท่ากัน นี่คือส่วนที่ skill ปิดไม่ได้

---

## 2. กรอบคิด: อะไรถ่ายทอดได้ / ไม่ได้

| ถ่ายทอดผ่าน skill **ได้** (process gap) | ถ่ายทอด **ไม่ได้** (capability gap) |
|---|---|
| วินัยการ verify ก่อน claim | ความลึกของ reasoning / insight |
| การไม่ถามเรื่องเล็ก + ทำงานให้จบเทิร์น | คุณภาพการ decompose งาน (เลือก "จุดเสี่ยงสุด" ได้ถูกจริง) |
| การ trigger ใช้ subagent/memory/search (เมื่อไหร่ควรใช้) | hypothesis priors ในการ debug บั๊กแปลกๆ |
| โครงสร้างการรายงาน (verdict-first, evidence-attached) | first-shot correctness ของ diff |
| protocol จัดการ flaky test แบบสถิติ | สมาธิ/ความคงเส้นคงวาข้ามหลายร้อย tool calls |
| วินัย scope (diff เล็ก, ไม่ refactor เกินสั่ง) | vision บนภาพหนาแน่น |
| การจดโน้ต/memory hygiene | สิ่งที่สกัดได้จากโน้ตเมื่ออ่าน (Slay the Spire 3x) |

**ค่าคาดหวังที่สมจริง (จาก transferability skeptic):**
- งานสั้น-กลาง (≤ ~40 tool calls): ปิด **~50–60%** ของช่องว่างเชิงพฤติกรรมที่มองเห็นได้
- งาน long-horizon autonomous (จุดแข็งหลักของ Fable): ปิด **~20–35%** — เปลี่ยน "พังเงียบๆ" เป็น "เสื่อมช้าๆ แบบตรวจสอบได้"
- First-shot quality, insight, vision, memory-extraction: **~0%**

---

## 3. สถาปัตยกรรม Curriculum (ปรับตามผล critic แล้ว)

ร่างแรกจาก workflow ได้ 10 skills × ~12 กฎ = ~120 กฎ — critic ชี้ว่านี่คือ**ความเสี่ยงอันดับ 1**: งาน bug-fix จริงงานเดียวจะ trigger 7-8 skills พร้อมกัน (~85 กฎ) ซึ่งตามคำเตือนของ Anthropic เอง prompt ที่ prescriptive เกินจะ*ลด*คุณภาพ Opus 4.8 จึงต้องออกแบบเป็น 3 ชั้น:

### Layer 0 — Shared Core (อยู่ใน `CLAUDE.md` เสมอ, ~40-60 บรรทัด)

กฎที่ถูกเขียนซ้ำ 5-6 ครั้งในร่างแรก ต้องมี "เจ้าของเดียว" ที่นี่:

1. **CLAIM AUDIT (กฎมูลค่าสูงสุดตัวเดียว):** ก่อนส่งข้อความที่มีคำว่า done/fixed/works/passes/verified ทุก claim ต้องชี้ไปที่ tool result จริงใน session นี้ *ที่รันหลัง edit ครั้งสุดท้าย* — ไม่มีหลักฐาน = เขียนว่า "not verified" ตรงๆ
2. **AUTONOMY TRIAGE (Class A/B/C):** ย้อนกลับได้ด้วย git + ตรงกับงานที่สั่ง = ตัดสินใจเองแล้วจดใน Decisions ledger / ทำลายข้อมูล-irreversible = ถามเสมอ / เปลี่ยน scope จริง = ถามท้ายเทิร์นพร้อม default
3. **ตารางค่าคงที่กลาง (canonical constants):** ร่างแรกมีเลขขัดกัน (flake re-run 3x/5x/10x/20x/30x!) — Opus ทำตามตัวเลขตรงตัว ต้องมีตารางเดียว เช่น flake re-run = 10x (30x เมื่อ failure rate < 20%), notes-file trigger = ~25 tool calls, fan-out trigger = 3+ workstreams อิสระที่งานละ ≥10 นาที
4. **ไฟล์โน้ตไฟล์เดียว:** `WORKING_NOTES.md` แบ่ง section (Plan / State / Findings / Ruled-out / Experiments / Delegation / Lessons) — ร่างแรกสั่งให้เปิด 5 ไฟล์ (PROGRESS.md, WORKING_NOTES.md, DEBUG_NOTES.md, delegation-log.md, experiment log) ซึ่งจะได้ 5 ไฟล์ที่ stale ทั้งหมด
5. **Router:** ย่อหน้าสั้นๆ ชี้ว่างานประเภทไหนโหลด skill หลักตัวไหน *ตัวเดียว* — แก้ปัญหา "skill โหลดไม่ติด" ซึ่งเป็นจุดอ่อน low-recall triggering ของ Opus เอง (skill ถูกส่งด้วยกลไกเดียวกับโรคที่มันรักษา)

### Layer 1 — Skills 7 ตัว (หลัง merge จาก 10)

| # | Skill | สอนอะไร | กฎเด่น | Transferability |
|---|---|---|---|---|
| 1 | **verifying-before-claiming** (รวม testing-verification เข้าด้วยกัน) | repro ก่อน fix, verification ladder (typecheck < unit < integration < รัน flow จริง), red/green, fresh-state, อ่าน output ไม่ใช่ exit code ("0 tests collected" = fail!), stale-verification, test integrity | RED CHECK, HARNESS SANITY, STALE-VERIFICATION | **HIGH** — ตัวเต็งอันดับ 1 ของทั้งชุด |
| 2 | **finishing-the-turn** | เจ้าของเดียวของวินัย ถาม/หยุด/เสนอ: question parking, promise scan (ห้ามจบเทิร์นด้วย "I'll now…"), enumerate-then-exhaust (n/n), error-retry 3 แบบที่ต่างกันจริง, decisions ledger | PROMISE SCAN, DECISION TRIAGE | **HIGH** — มีตัวเลขรองรับ (~12pp) |
| 3 | **search-first-context** | volatile-fact gate (เวอร์ชัน/ราคา/API → ค้นก่อนพูด), pre-edit checklist (อ่านไฟล์+grep symbol+ไล่ caller ก่อนแก้), convention sampling, Chesterton's fence (git blame ก่อนลบโค้ดแปลก), search-don't-ask | PRE-EDIT CHECKLIST, VOLATILE-FACT GATE | **HIGH** — โจมตีจุดอ่อน low-recall โดยตรง |
| 4 | **scoping-code-changes** | scope contract 1 ประโยค, rule of three, trust-boundary guards เท่านั้น, why-only comments, edit-don't-rewrite, report-don't-fix (จด "Noticed" แทนการแก้นอกงาน), diff audit ก่อนจบ | SCOPE CONTRACT, DIFF AUDIT | **HIGH** — ทุก failure mode นับได้จาก diff |
| 5 | **outcome-first-reporting** | template สรุปงาน: verdict 1 บรรทัดขึ้นก่อน → What changed / How verified / **Not done (บังคับ, อยู่ครึ่งแรก)** / Next; calibration grammar; two-register (เงียบระหว่างทำ เขียนเต็มตอนจบ); re-grounding block | FINAL-MESSAGE TEMPLATE, FAILURE REPORTING | **HIGH** — formatting คือสิ่งที่ LLM ทำตามได้ดีที่สุด |
| 6 | **root-causing-bugs** | repro gate (บล็อก), hypothesis ledger (ตาราง falsifiable), one-variable experiments, git bisect, upstream walk (ห้าม null-guard/sleep/retry โดยไม่ justify), **เจ้าของเดียวของ flake protocol เชิงสถิติ**, fix-revert-refix | REPRO GATE, STATISTICAL FIXED-CLAIM | **MEDIUM** — ครึ่ง claims-discipline = high, ครึ่ง root-cause insight = ปิดไม่ได้ (ledger สวยแต่ hypothesis ผิดทั้ง 5 ข้อได้) |
| 7 | **delegating-parallel-work** | partition table ก่อนเริ่มงานหลาย stream, fan-out เมื่อ 3+ workstreams อิสระ (งานละ ≥10 นาที — *ไม่ใช่* 3+ ไฟล์ ตามที่ skeptic เตือนว่าจะ over-trigger), one-writer-per-file, dispatch prompt 6 ส่วน self-contained, trust-but-verify (รัน union check เอง) | PARTITION FIRST, SELF-CONTAINED DISPATCH | **MEDIUM** — trigger แก้ได้ แต่คุณภาพ "รอยตัด" ของ partition คือ judgment |

**รอเฟสหลัง (สถานการณ์เฉพาะ):**
- **planning-to-done** — spec extraction, unknowns triage, discovery-before-mutation, risk-first order (ตัดส่วนซ้ำกับ skill อื่นออกแล้ว) — MEDIUM
- **managing-working-memory** — memory sweep ตอนเริ่ม, lesson format `[วันที่] When <trigger>, do <action> because <evidence>`, update-before-append, verify-before-trust, post-compaction ritual — MEDIUM (กลไกสอนได้ แต่คุณภาพบทเรียนที่สกัดคือ capability)

### Layer 2 — Hooks (การบังคับเชิงกลไก)

Critic ชี้ว่า *"hook หนึ่งตัวที่บล็อกข้อความ 'done' ที่ไม่มี verification run มีค่ากว่า skill 3 ตัว"* เพราะ prose เสื่อมตาม context ยาว แต่ hook ไม่เสื่อม:

- **Stop hook:** ตรวจข้อความปิดเทิร์น — ถ้ามี done/fixed/passes แต่ tool call สุดท้ายไม่ใช่ verification → block พร้อมเหตุผล
- **PreToolUse hook (Edit/Write):** เตือน pre-edit checklist ถ้ายังไม่เคย Read ไฟล์นั้น/Grep symbol
- **Stop hook (promise scan):** จับ pattern "I'll now…/Next, let me…" ในข้อความปิดเทิร์น

### มิติที่ยังขาด (backlog จาก completeness critic)

1. **code-review-as-reviewer** — enumerate-all-then-rank, ห้ามให้ threshold ตัดตอน "การค้นหา" (แก้จุดอ่อน recall ร่วงเมื่อสั่ง conservative)
2. **knowledge-work deliverables** — xlsx/docx/pptx pipeline (จุดแข็ง Fable ข้อ 4 ยังไม่มี skill รองรับเลย)
3. **vision procedure** — crop/zoom ก่อนอ่านภาพหนาแน่น, transcribe-then-verify
4. **ambiguity interpretation** — enumerate การตีความ → เลือกอันที่ irreversible น้อยสุด → ประกาศแล้วทำ
5. **context-window economy** — งบการอ่าน (อ่านเต็ม vs head/tail vs ส่ง survey agent) — สำคัญเพราะ curriculum เองก็เพิ่ม token load
6. **tool inventory** — สำรวจ MCP/custom tools ที่มีตอนเริ่มงาน แล้ว match กับ task

---

## 4. แผนการทดสอบ (Eval Methodology)

**หลักการสูงสุด (จาก skeptic):** วัด **outcome** ไม่ใช่ **process artifact** — วัด "บั๊กถูกแก้จริงไหม / requirement ครบไหม / จับ regression ได้ไหม / ask กี่ครั้ง / false-done กี่ครั้ง" ห้ามวัด "มี ledger ไหม / ทำตาม template ไหม" มิฉะนั้น curriculum จะ optimize ตัวเองเป็น transcript ที่*ดูขยัน*แต่ผลงานเท่าเดิม (cargo-cult ที่อันตรายกว่า Opus เปล่าๆ เพราะแต่งตัวเหมือนความรอบคอบ)

### 4.1 Harness

- Task bank ต่อมิติ: 5-10 งานจริงพร้อม planted traps (เช่น requirement 11 ข้อที่ข้อท้ายๆ มักหล่น, flaky test ที่ fail 30%, ไฟล์ AUTO-GENERATED ล่อให้แก้, API เวอร์ชันใหม่ที่ต่างจาก training data)
- A/B: Opus 4.8 เปล่า vs Opus 4.8 + skill — **N ≥ 5 ต่อ arm**, รายงาน mean + min-max spread, **ห้าม claim improvement ถ้า delta < spread** (ใช้กฎ EVAL DISCIPLINE ของ curriculum เองกับตัวมันเอง)
- Metric ตัวอย่าง: grounded-claim rate, ask count/task, one-turn completion rate, requirement coverage n/n, false-"fixed" rate บน flaky bugs, unrequested-hunk count ใน diff
- ทดสอบ **trigger accuracy** แยกต่างหาก: skill โหลดเมื่อควรโหลดไหม (นี่คือจุดตายอันดับหนึ่ง — skill ที่ไม่โหลดคือ skill ที่ไม่มีอยู่)
- Baseline เพิ่มเติมที่ควรมี: Fable 5 บนงานเดียวกัน (เพดานอ้างอิง) เพื่อคำนวณ % gap closed จริง

### 4.2 Rollout เป็นเฟส (ห้ามปล่อย 10 ตัวพร้อมกัน — ผล A/B จะตีความไม่ได้)

| เฟส | ปล่อย | เหตุผล |
|---|---|---|
| 1 | Layer 0 (CLAUDE.md core) + `verifying-before-claiming` + `finishing-the-turn` | สองตัวที่โจมตี failure mode ที่พบบ่อยสุด + มีตัวเลขของ Anthropic รองรับ effect size |
| 2 | `delegating-parallel-work` + `search-first-context` | แก้ recall-triggering ล้วนๆ ความเสี่ยงชนกับตัวอื่นต่ำ |
| 3 | `managing-working-memory` + `planning-to-done` | คู่ที่หนักกว่า — memory คือ keystone ที่ skill อื่นพึ่ง แต่ต้อง unify ไฟล์โน้ตก่อน |
| 4 | สามตัวสถานการณ์เฉพาะ: `root-causing-bugs`, `outcome-first-reporting`, `scoping-code-changes` | trigger เจาะจงกว่า ชนกันน้อย |
| 5 | Hooks + backlog (review, deliverables, vision, ambiguity, context economy) | หลังยืนยันว่า prose layer ทำงาน |

แต่ละเฟส: รัน A/B → ถ้าผ่าน spread → ค่อยเพิ่มเฟสถัดไป → รัน regression บนเฟสก่อนหน้า (skill ใหม่อาจทำให้ตัวเก่าแย่ลงจาก rule collision)

---

## 5. Checklist สิ่งที่ต้องเตรียม

### โครงสร้างไฟล์

```
Fable2Opus/
├── PLAN.md                        ← ไฟล์นี้
├── CLAUDE.md                      ← Layer 0: shared core + constants + router
├── .claude/skills/
│   ├── verifying-before-claiming/
│   │   ├── SKILL.md
│   │   ├── references/            (summary-template, flake-recipes, output-traps)
│   │   └── scripts/repeat-run.sh
│   ├── finishing-the-turn/        (+ references/closing-gate.md, triage-examples.md)
│   ├── search-first-context/      (+ scripts/impact-scan.sh)
│   ├── scoping-code-changes/      (+ scripts/diff-audit.sh)
│   ├── outcome-first-reporting/   (+ references/templates.md, EXAMPLES.md)
│   ├── root-causing-bugs/         (+ references/flaky-bugs.md, bisection.md, scripts/repeat.sh)
│   └── delegating-parallel-work/  (+ references/dispatch-prompt-template.md, scripts/lint-dispatch-prompt.sh)
├── .claude/hooks/                 ← Layer 2
├── evals/
│   ├── task-bank/                 (งานทดสอบ + planted traps ต่อมิติ)
│   ├── baselines/                 (ผลรัน Opus เปล่า และ Fable 5 อ้างอิง)
│   └── results/                   (A/B log: mean + spread ต่อ metric)
└── constants.md                   ← ตารางค่าคงที่กลางที่ทุก skill อ้าง
```

### ลำดับงาน

- [x] เขียน `CLAUDE.md` Layer 0 (claim audit, triage, constants, notes convention, router) — ✅ 2026-07-09
- [x] เขียน `constants.md` — C1–C11 ✅ (C9 eval N, C10 fast-suite bar, C11 batch size เพิ่มระหว่าง review)
- [x] สร้าง task bank (6 งาน) + fixtures รันได้ 2 ตัว (flaky-race calibrated ~43–57%, multi-req-cli grader 0/11→11/11) ✅ — **ยังไม่ได้รัน baseline จริง** (ต้องรันนอก repo ตาม protocol ใน evals/README.md)
- [x] เขียน skill เฟส 1 สองตัว ✅ — ผ่าน review (findings 12 → แก้ 7 actionable) + smoke test harness end-to-end
- [x] เขียน skill เฟส 2 สองตัว (`delegating-parallel-work`, `search-first-context`) ✅ 2026-07-10 — trim ครบ, review ไม่มี must-fix, constants ขยายเป็น C1–C16, fixture `rename-config` ผ่าน discrimination probes (เฉลย/grader อยู่ `evals/judge/` ตั้งแต่ต้น — ไม่มี spoiler รั่วใน smoke รอบนี้)
- [ ] A/B เฟส 1+2 จริง (N≥5 ต่อ arm, baseline นอก repo) → อ่านผล → ปรับ → เฟส 3 ต่อ — **หมายเหตุจาก smoke เฟส 2:** fixture rename-config ทั้งสอง arm ได้ 7/7 (ceiling ที่ N=1) → การ A/B จริงควรเพิ่ม metric คุณภาพรายงาน และ/หรือทำ fixture ยากขึ้น
- [x] เขียน skill เฟส 3+4 ห้าตัว (`managing-working-memory`, `planning-to-done`, `root-causing-bugs`, `outcome-first-reporting`, `scoping-code-changes`) ✅ 2026-07-10 — ownership map กันกฎซ้ำ, reviewer จับ collision ได้ 1 จุด (format บรรทัด Noticed) และแก้แล้ว, constants ขยายเป็น C1–C18
- [x] เขียน hooks ✅ 2026-07-10 — Stop hook `claim_gate.py` (promise scan + claim gate, conservative, มี escape valve `FABLE2OPUS_HOOKS_OFF=1`) ผ่าน 19/19 tests รวม adversarial cases; wired ใน `.claude/settings.json`
- [x] Backlog มิติแรก: `reviewing-code` ✅ 2026-07-10 (แยก "ค้นหา" ออกจาก "กรองรายงาน" — แก้ recall ร่วงเมื่อสั่ง conservative)
- [x] Backlog อีก 5 มิติ ✅ 2026-07-10 — ผ่าน packaging critic เพื่อคุม instruction overload: **skill ใหม่ 3 ตัว** ที่ trigger ไม่ทับงานเขียนโค้ดปกติ (`producing-deliverables` — profile-before-compute, cross-foot ทุกเลข headline, reopen-ไฟล์ก่อน claim; `extracting-from-images` — crop/tile ก่อนอ่าน, transcribe-then-verify; `inventorying-capabilities` — สำรวจ MCP/skills ตอนเริ่ม session แล้ว match กับ task) + **extensions แบบ append-only 2 จุด** (ambiguity interpretation → planning-to-done rules 9–10; context-window economy → search-first-context rules 13–15 + ส่วน distill ใน managing-working-memory) — load profile ของงานโค้ดปกติเท่าเดิม; eval tasks 15–19 เพิ่มแล้ว
- [x] **A/B รอบ 1 (in-session)** ✅ 2026-07-10 — 30 Opus runs (3 งาน × 2 arms × N=5) + blind rubric; ผลเต็มใน `evals/results/2026-07-10-ab-run1.md` **ข้อค้นพบ:** (1) probe พิสูจน์ว่า in-session "bare" arm มี Layer 0 + skill descriptions ปนอยู่เสมอ → รอบนี้วัด marginal effect ของการอ่าน SKILL.md เต็ม; (2) ceiling เกือบทุก metric — fixtures ง่ายเกินไปสำหรับ Opus 4.8; (3) สัญญาณเดียว: noticedLine ใน T13 (1/5 → 5/5; ตามกฎ C9 = สรุปไม่ได้, Fisher exact post-hoc p≈0.024 เป็น exploratory); (4) เพิ่มบันทึกใน C9: binary metric ต้อง pre-register exact test
- [x] **เผยแพร่สาธารณะ** ✅ 2026-07-10 — https://github.com/Work-in-Problem/F2O (public, MIT) ติดตั้งได้ 2 ช่องทาง ทดสอบจริงจาก GitHub ทั้งคู่: (A) Claude Code plugin `claude plugin marketplace add Work-in-Problem/F2O` + `claude plugin install f2o@f2o` — พก skills+hooks ครบ, SessionStart hook ฉีด Layer 0 (11.3KB) อัตโนมัติ, `source:"./"` ใน marketplace.json ใช้ได้จริง; (B) `npx skills add Work-in-Problem/F2O --all -y -g` — skills อย่างเดียว (Vercel CLI สแกน `skills/` root) โครงสร้างเปลี่ยน: skills/ กับ hooks/ ย้ายไป root (testbed ใช้ symlink `.claude/skills → ../skills`), Layer 0 ฉบับ distribution อยู่ `core/`, hook suite ขยายเป็น 28 tests (รวม session_context 5 cases), `research/` + `evals/judge/` ถูก gitignore ไว้ในเครื่อง
- [x] **A/B รอบ 2 (in-session)** ✅ 2026-07-10 — fixtures ยาก 3 ตัว (สร้าง+verify อิสระ) + PREREG commit ก่อนรัน (`a1e44f4`) + 40 Opus runs + Fisher's exact ตามที่ล็อก · **ผล:** primary ทั้งสาม inconclusive (9/10 vs 10/10 · 5/5 vs 5/5 · 4/5 vs 5/5) เพราะ **control-arm saturation** — สภาพ full-install ทำให้ arm "bare" พูดภาษา C2/ใช้ repeat-run.sh/เขียน Noticed-format เอง · สิ่งที่พิสูจน์ได้: ระบบเต็มชุดส่งมอบพฤติกรรมเป้าหมาย 9–10/10 บนโจทย์ยาก (race 2% แก้ถูก 10/10 + amplified 10/10 + C2 verdict 10/10; conflict surfaced 9/10; wart 20/20 ไม่ถูกแตะ) · ผลเต็ม: `evals/results/2026-07-10-ab-run2.md`
- [x] **True-bare baseline (Run 2b)** ✅ 2026-07-10 — ปิด plugin ทั้งเครื่อง + probe ยืนยันความสะอาด → 20 headless Opus sessions นอก repo → judge เดิม + Fisher ตาม PREREG 2b (`08f6b43` ก่อนรัน) · **ผลชี้ขาด: noticedLine 0/10 (เปล่าแท้) vs 10/10 (F2O), p≈5.4×10⁻⁶ — SIGNIFICANT ตามเกณฑ์ pre-registered** · dose-response 0/10→1/5→9/10→10/10 · nuance: Opus เปล่าไม่แก้ wart เหมือนกัน (ยับยั้งติดตัว) แต่*เงียบ* — F2O สร้างความโปร่งใส ไม่ใช่ความยับยั้ง · amplified 0/5 vs 5/5 (วิธีต่างแม้ผลเท่า) · c2Verdict/conflictSurfaced เพดานชนทั้งคู่ = ความสามารถติดตัว Opus 4.8 บันทึกไว้อย่างยุติธรรม · ผลเต็ม: `evals/results/2026-07-10-ab-run2b-truebare.md` — **การพิสูจน์หลักของโปรเจกต์ครบสมบูรณ์**; งาน 08/09/14 ยังเป็น optional operator-run

> **บันทึกจาก smoke test (2026-07-09, N=1/arm — ตรวจ harness เท่านั้น):** ทั้งสอง arm (Opus เปล่า / Opus+skill) แก้ race ได้ถูกและ claim มีหลักฐานครบ แต่ judge พบว่าไฟล์เฉลย `FIXTURE_NOTES.md` รั่วเข้าไปใน run dir ทั้งสองฝั่ง (แก้แล้ว: ย้ายเฉลย+grader ไป `evals/judge/`) และ arm เปล่าอาจถูก contaminate จาก CLAUDE.md ของ repo — ยืนยันว่า baseline จริงต้องรันนอก repo ตาม protocol เท่านั้น

### Trim สำคัญที่ต้องใส่ตอนเขียน SKILL.md จริง (จาก skeptic — กันพัง)

- ทุกกฎเลขตายตัว (threshold) → เปลี่ยนเป็น "หลักการ + ตัวอย่าง" เว้นแต่จำเป็น เพราะ Opus ใช้เลขตรงตัวเกิน
- กฎเด็ดขาด (rule of three, trust-boundary) → เพิ่ม escape hatch "ถ้าเชื่อว่าเป็นข้อยกเว้น ให้เขียนเหตุผล 1 บรรทัดแล้วทำต่อ" — เปลี่ยน silent wrong call เป็น auditable call
- statistical fixed-claim → cap สูตร `M = max(20, min(100, 3/rate))` กัน 1% flake ที่จะสั่งรัน 300 รอบ
- final-message template → ยกเว้นงานเล็ก (คำตอบ 2 บรรทัดไม่ต้องมี 4 section)
- calibration grammar → "ไป verify หรือคงคำ hedge ไว้พร้อมเหตุผล" — ห้ามให้การลบ hedge เป็นทางที่ถูกกว่า
- MONITOR AND STEER (subagent) → เขียนตามที่ Task tool ทำได้จริง (ส่วนใหญ่ dispatch-and-await) — อย่าสอนพฤติกรรมที่ harness ทำไม่ได้

---

## 6. ข้อจำกัดที่ต้องยอมรับ (อ่านก่อนตัดสินโปรเจกต์)

1. **เศรษฐศาสตร์:** skills เพิ่ม tool calls/tokens ~1.3–2x ต่องาน — ที่ราคา Opus $5/$25 vs Fable $10/$50 overhead 2x กลืนส่วนต่างราคาหมด กรณีธุรกิจที่แท้จริงคือ (a) งานที่ capability ของ Opus พอแต่ process พัง และ (b) hedge เรื่อง rate-limit/availability — ไม่ใช่ "แปลง Opus เป็น Fable"
2. **ตัวเลข % ของแต่ละ skill รวมกันไม่ได้** — เกือบทุก skill เคลม win ก้อนเดียวกัน (ask-rate 12pp โผล่ 5 ครั้ง, claim-grounding 6 ครั้ง)
3. **กลไกส่ง skill ป่วยเป็นโรคเดียวกับที่มันรักษา** — skill โหลดด้วย description matching = triggering แบบ low-recall ของ Opus เอง → router ใน CLAUDE.md + hooks คือส่วนประกอบชั้นหนึ่ง ไม่ใช่ของแถม
4. **Cargo-cult ที่ขอบเขต judgment** — hypothesis ledger ที่ format สวยแต่เดาผิดทั้ง 5 ข้อ, partition table ที่ padded, audit ritual ประทับบน output ที่อ่านผิด — อันตรายกว่า Opus เปล่าเพราะดูน่าเชื่อถือ → แก้ด้วยการวัด outcome เท่านั้น (ข้อ 4)
5. **Instruction เสื่อมตาม context ยาว** — พอดีกับที่ gap ของ Fable ใหญ่สุดตรง long-horizon → hooks และไฟล์โน้ตช่วยได้บางส่วน แต่คือขีดจำกัดโครงสร้าง

---

## ภาคผนวก: แหล่งข้อมูล

- Spec ละเอียดทั้ง 10 skills (กฎเต็ม, SKILL.md outline, eval scenarios, supporting files): `research/skill-specs-full.json` (อ่านง่าย: `research/specs-readable.txt`)
- ผล critic ฉบับเต็ม (completeness + transferability skeptic): `research/critics.json`
- ผลค้นคว้าเว็บ (benchmarks + แหล่งอ้างอิง): `research/web-research.json`
- Anthropic migration guide → "Migrating to Claude Fable 5" / "Migrating to Opus 4.8" (behavioral shifts + prompt snippets ทางการ — หลาย snippet ใช้เป็นแกนของ skill ได้ตรงๆ)
- https://www.anthropic.com/news/claude-fable-5-mythos-5
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

## v1.4 "The Conductor Release" ✅ 2026-07-11 (ครบวงจร author→PREREG→A/B→ship)

- Gate (baseline-first, ครั้งแรก): T08 0/5 → build · T23 5/5 → candidate ถูกฆ่า (Opus วัดเองเป็น
  ถ้ามี bench ให้) · T09 5/5 ceiling-by-evasion (เก็บ fixture ไว้เป็น guard)
- สกิลที่ 14 `conducting-agent-fleets`: A/B ตาม PREREG `73faf84` — **bare 0/5 vs skill 5/5,
  Fisher p=0.004** · guard 5/5 (รวมการ*ไม่* delegate ที่ถูกต้องบนงานต่ำกว่า C4) · เร็วขึ้น ~25%
- ค้นพบ: Agent tool = deferred ใน headless (โหลดผ่าน ToolSearch ได้จริง) · jsonl แยก tool_use
  ต่อบรรทัด ต้อง group ด้วย message.id · แก้ NOTES + task-bank 08/09 แล้ว
- เหลือ (optional): task 14 ต้อง interactive จริง · delegate-then-verify บน fixture ใหญ่กว่า C4 ยังไม่วัดตรง

## v1.5 "The Honesty Release" ✅ 2026-07-12 (ครบวงจร fixtures→gate→A/B(N=10)→ship)

- Gate 4 งาน: T03 5/5 + T10 **11/11 ทั้ง 5 รอบ** → native ceilings · T05 2/5 + T15 2/5 borderline
  → override มีเอกสารเหตุผล + ยกเป็น N=10/arm (อำนาจสถิติ: N=5 ตัดสิน borderline ไม่ได้เชิงโครงสร้าง)
- **T05 SIGNIFICANT: honestUnverified bare 3/10 vs skill 8/10, p=0.035** — A/B ตรงครั้งแรกของ
  `verifying-before-claiming` · bare ทำ mock-laundering 7/10 · ผลยืนยันตัวที่ 3 ของโปรเจกต์
- T15 inconclusive ตามเกณฑ์ (3/10→7/10, p=0.089) — secondaries ทิศเดียวทั้งแผง (dups 5→10/10);
  future work: N≈15-20/arm ถ้าจะตัดสินให้ขาด
- บทเรียนเครื่องมือ: judge ต้องกำหนดรูปแบบ runId ให้ตายตัว (t15 คืน "bare-r1" ทำ aggregation script
  พลาด — คะแนนดิบครบ ไม่มีผลต่อการตัดสิน) · เหลือ optional: T14 interactive, T15 follow-up N ใหญ่
