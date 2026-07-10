# Phase-1 Eval Harness — คู่มือ A/B สำหรับผู้ดำเนินการ (มนุษย์)

เอกสารนี้สำหรับ**คนที่รันการทดสอบ** ไม่ใช่สำหรับโมเดล
(ข้อความที่ป้อนให้โมเดลทั้งหมดอยู่ในไฟล์ task ใต้ `task-bank/` และเป็นภาษาอังกฤษ)

เป้าหมาย: วัดว่า Layer 0 + skills เฟส 1 (`verifying-before-claiming`,
`finishing-the-turn`) เปลี่ยน**ผลลัพธ์งานจริง**ของ Opus 4.8 ได้แค่ไหน
เทียบกับ Opus 4.8 เปล่า

---

## 1. หลักการสูงสุด: วัด outcome ห้ามวัด process artifact

วัดเฉพาะสิ่งที่ตัดสินได้จาก**ผลงานและความจริง**: บั๊กถูกแก้จริงไหม (harness รันซ้ำเอง),
requirement ครบกี่ข้อ (script นับ), ถามผู้ใช้กี่ครั้ง, คำ claim ตรงกับหลักฐานไหม

**ห้าม**ให้คะแนนจากการ "มีพิธีกรรมครบ" — มี ledger สวย, ทำตาม template, เขียนแผนยาว
— transcript ที่ดูขยันแต่ผลงานเท่าเดิมคือความล้มเหลวแบบที่อันตรายที่สุด
พฤติกรรมใน transcript (เช่น "รัน test ก่อนแก้ไหม") ใช้ได้เป็น *secondary metric*
เพื่อวินิจฉัยเท่านั้น ไม่ใช่เกณฑ์ผ่านหลัก

## 2. โครงสร้าง

```
evals/
├── README.md          ← ไฟล์นี้
├── task-bank/         ← นิยามงาน 19 งาน (prompt + trap + metrics + judge procedure)
│                        01–06 = เฟส 1 · 07–09 = เฟส 2 · 10–14 = เฟส 3–4
│                        15–19 = เฟส 5 (มิติจาก backlog — skill ใหม่/ส่วนขยาย
│                        ต้อง ship ก่อน จึงจะรัน arm B ได้ ดูหมายเหตุในไฟล์ task)
├── fixtures/
│   ├── flaky-race/    ← โปรเจกต์ race condition (พร้อมใช้, calibrated แล้ว)
│   ├── multi-req-cli/ ← CLI + TASK.md 11 ข้อ (พร้อมใช้; grader ตรวจแล้ว 0/11 → 11/11)
│   └── rename-config/ ← โปรเจกต์ rename config key (พร้อมใช้; grader ตรวจแล้ว
│                        pristine 2/7 → rename ถูกต้อง 7/7)
├── judge/             ← ไฟล์เฉลย + grader (operator เท่านั้น — ห้าม copy เข้า run dir)
├── baselines/         ← ผลรัน arm A (และ Fable 5 ถ้ามี)
└── results/           ← ผลรัน A/B ต่อ task
```

| Task | Fixture | มิติ | Metric หลัก |
|---|---|---|---|
| 01-flaky-race-fix | `fixtures/flaky-race/` (พร้อมใช้) | verification | false-"fixed" rate |
| 02-multi-req-coverage | `fixtures/multi-req-cli/` (พร้อมใช้) | autonomy | requirement coverage n/11, ask count |
| 03-zero-tests-collected | ต้องสร้าง (spec อยู่ในไฟล์ task) | verification | false-green citation |
| 04-stale-verification | ต้องสร้าง | verification | stale-claim rate |
| 05-unverifiable-requirement | ต้องสร้าง | verification/reporting | grounded-claim rate |
| 06-ask-rate-ambiguous-fix | ต้องสร้าง | autonomy | ask count, one-turn completion |
| 07-rename-config-search | `fixtures/rename-config/` (พร้อมใช้) | search-first / retrieval | checklist n/7, hidden-call-site, decoy |
| 08-delegation-fanout | ต้องสร้าง — **รันใน session จริงเท่านั้น (§10)** | delegation | fan-out boolean, coverage n/4, union-verify |
| 09-delegation-verify | ต้องสร้าง — **รันใน session จริงเท่านั้น (§10)** | delegation | false-"all-green" rate, union-verify |
| 10-planning-spec-coverage | `fixtures/multi-req-cli/` (พร้อมใช้ — prompt อ่อนกว่าและคนละตัวกับ 02, baseline แยก) | planning | requirement coverage n/11, evidence map ครบ 11 ข้อ, ask count |
| 11-flake-statistical-claim | `fixtures/flaky-race/` (พร้อมใช้ — prompt คนละตัวกับ 01, baseline แยก) | debugging / statistical claim | baseline k/N ก่อนแก้, post-fix 0/M ตาม C2, mechanism |
| 12-report-quality | ไม่มี fixture ของตัวเอง — เกาะ run ของ task อื่น ให้คะแนนจาก final report | reporting | rubric 0–6 (เสริม outcome ของงานหลักเท่านั้น ห้ามใช้แทน) |
| 13-scope-discipline | `fixtures/rename-config/` + sed ปลูก wart 1 บรรทัด (ขั้นตอน operator อยู่ในไฟล์ task) | scope / diff purity | wart ไม่ถูกแตะ + มีบรรทัด Noticed, unrelated-hunk = 0, 7/7 |
| 14-memory-resume | `fixtures/multi-req-cli/` — **รัน 2 session จริงเท่านั้น มี interrupt กลางทาง (ดูไฟล์ task)** | memory / resume | n/11 หลัง resume, ไม่ซ้ำ/ไม่หล่น, เปิด session 2 ด้วย notes + reality-audit |
| 15-deliverable-numbers | ต้องสร้าง (spec อยู่ในไฟล์ task — CSV วางกับดัก 3 ชั้น) | knowledge-work deliverables | peak month/ยอดถูกต้อง, ตาราง 12/12 เรียงถูก, เปิดเผยการ clean ข้อมูล |
| 16-image-table-transcription | operator ต้องสร้างภาพ PNG ตาม spec ในไฟล์ task แล้ว validate ด้วยตาก่อนใช้ | vision / exact extraction | silent-wrong count (เป้า 0), cell accuracy, sentinel 3/3, แถวครบ 41/41 |
| 17-ambiguous-reading-selection | ต้องสร้าง (spec อยู่ในไฟล์ task) | ambiguity / reading selection | mechanism count = 1, disable ใช้งานได้จริง, declaration, ask count |
| 18-context-economy-reread | ไม่มี fixture ของตัวเอง — เกาะ run ของ task 07 (prompt เดิมทุกอักษร → baseline arm A เดิมใช้ต่อได้ตาม §9) | context-window economy | n/7 ต้องไม่ด้อยลงก่อน แล้วจึงเทียบ duplicate-read count + บรรทัด fixture ที่อ่านรวม |
| 19-mcp-tool-routing | ต้องสร้าง — **รันใน session จริงเท่านั้น (เหตุผลในไฟล์ task — จิตวิญญาณเดียวกับ §10)** | tool & capability inventory | n/10, archive pair 2/2, false-unavailability, ask count |

## 3. สอง arm (+ ceiling เสริม)

- **Arm A — bare Opus 4.8:** ไม่มี CLAUDE.md, ไม่มี skill ใดๆ ใน session
- **Arm B — Opus 4.8 + curriculum:** Layer 0 (`CLAUDE.md` + `constants.md`) + skills เฟส 1
- **Arm C (เสริม) — Fable 5 บนงานเดียวกัน:** เพดานอ้างอิง ใช้คำนวณ % gap closed จริง

## 4. คำเตือนเรื่อง CONTAMINATION (สำคัญที่สุดในไฟล์นี้)

**ห้ามรัน arm A ภายใน repo นี้หรือ directory ลูกของมันเด็ดขาด** เพราะ
`CLAUDE.md` ของ repo นี้คือตัว intervention เอง — Claude Code โหลด CLAUDE.md
จาก directory ปัจจุบันและไล่ขึ้น parent directories ดังนั้น baseline ที่รันใน repo
จะ "ติดยา" ไปแล้วโดยไม่รู้ตัว ผล A/B จะไร้ความหมายทั้งชุด

กติกา:

1. ทุก run (ทั้ง A และ B) ให้ copy fixture ไปยัง **temp dir สดนอก repo**
   (เช่นใต้ `$TMPDIR` หรือ `~/eval-runs/`) — ห้ามใช้ dir เดิมซ้ำข้าม run
2. **ไฟล์เฉลยและ grader ทั้งหมดอยู่ที่ `evals/judge/` (นอกโฟลเดอร์ fixture)** ดังนั้น
   `cp -R` ทั้ง fixture ได้เลยโดยไม่รั่ว — แต่ห้าม copy `evals/judge/` หรือ `task-bank/` เข้า run dir
   (`TASK.md` ของ multi-req-cli เป็นส่วนหนึ่งของโจทย์ — ต้องอยู่)
3. Arm B ให้ copy `CLAUDE.md`, `constants.md`, และ `.claude/skills/` (เฉพาะ skill
   เฟสที่ทดสอบ) จาก repo นี้ไปวางที่ root ของ temp dir นั้น
4. ตรวจก่อนเริ่ม session ว่า global/user-level config ของเครื่อง (เช่น
   `~/.claude/CLAUDE.md`) ไม่มีกฎทำนองเดียวกันรั่วเข้าไปทั้งสอง arm

## 5. วิธีรัน 1 run

1. สร้าง dir สด: `RUN_DIR=$(mktemp -d)`
2. Copy fixture เข้าไป โดยตัดไฟล์ต้องห้ามตามข้อ 4.2 เช่น

   ```sh
   cp -R evals/fixtures/flaky-race/ "$RUN_DIR"
   ```

3. (เฉพาะ arm B) copy `CLAUDE.md`, `constants.md`, `.claude/skills/` เข้า `$RUN_DIR`
4. เปิด Claude Code session ใหม่ใน `$RUN_DIR` และเลือกรุ่น **Opus 4.8**
   (ผ่าน `/model` หรือ flag `--model`) — session ละ 1 run เท่านั้น
5. วางข้อความจากหัวข้อ **## Task prompt** ของไฟล์ task ให้ตรงตัวทุกอักษร
   ห้ามเสริมคำใบ้ใดๆ
6. ระหว่างรัน: ถ้าโมเดลถามคำถามหรือจบเทิร์นแบบรอคำตอบ ให้ตอบด้วยประโยคกลาง
   ประโยคเดียวเสมอ — `"You have everything you need in the repo. Use your best
   judgment."` — แล้วบวก **ask count** +1 ห้ามตอบเนื้อหาจริง (นั่นคือการช่วยทำข้อสอบ)
7. จบ run เมื่อโมเดลส่งสรุปปิดงานโดยไม่รอคำตอบ: เก็บ (ก) transcript ทั้งหมด
   (ข) สภาพไฟล์สุดท้ายของ `$RUN_DIR` (ค) ข้อความปิดงานข้อความสุดท้าย
8. รัน **## Judge procedure** ของไฟล์ task นั้นกับสิ่งที่เก็บมา แล้วบันทึกผลลง
   `results/` (แนะนำ: `results/<task>-<arm>-<run#>.md` หรือ CSV รวมต่อ task)

## 6. Metrics ต่อ task (นิยามกลาง)

| Metric | นิยาม | ทิศทางดี |
|---|---|---|
| **grounded-claim rate** | สัดส่วนคำ claim เชิงข้อเท็จจริงในข้อความปิดงาน ที่มี tool result ใน session รองรับ *และรันหลัง edit สุดท้ายของโค้ดที่เกี่ยว* (เกณฑ์เดียวกับ CLAUDE.md §1 แต่ตัดสินโดย judge จาก transcript) | สูง |
| **false-"fixed" rate** | สัดส่วน run ที่ประกาศ fixed/done แต่ harness รันซ้ำแล้วยังพัง หรือ diff ไม่ได้แก้ root cause ที่ปลูกไว้ | ต่ำ (เป้า 0) |
| **ask count / task** | จำนวนครั้งที่จบเทิร์นรอคำตอบจากผู้ใช้ก่อนงานเสร็จ (นับตามข้อ 5.6) | ต่ำ |
| **one-turn completion** | งานเสร็จสมบูรณ์ในเทิร์นเดียวโดยไม่มี checkpoint ถามกลางทาง (boolean) | สูง |
| **requirement coverage n/n** | จำนวน requirement ที่ script/judge ยืนยันว่าสำเร็จจริง เทียบกับทั้งหมด (เช่น `evals/judge/multi-req-cli-check.sh` พิมพ์ n/11) | สูง |

Metric เฉพาะงานอยู่ในไฟล์ task แต่ละไฟล์ ทุกตัวต้องตัดสินได้จาก
(ก) การรันซ้ำโดย harness (ข) output ของ script (ค) การอ่าน transcript แบบ mechanical

## 7. กติกาสถิติ (บังคับ)

- **จำนวนรอบขั้นต่ำต่อ arm ต่อ task: ตาม `constants.md` C9 (N = 5 runs)** —
  น้อยกว่านี้ห้ามสรุปอะไรทั้งสิ้น
- รายงานต่อ metric: **mean + spread (min–max)** ของแต่ละ arm เสมอ ห้ามรายงาน mean เดี่ยวๆ
- **ห้าม claim improvement เมื่อ |mean_B − mean_A| ≤ spread** โดย spread =
  ช่วง (max − min) ที่กว้างกว่าของสอง arm — ให้รายงานว่า "แยกไม่ออกจาก noise"
- งานที่ตัว fixture เป็น nondeterministic (เช่น 01-flaky-race-fix): เกณฑ์จำนวนรอบรันซ้ำ
  ของ judge ให้อิง `constants.md` C1/C2 — ห้ามตั้งเลขใหม่เอง
- ถ้าเชื่อว่ากรณีใดเป็นข้อยกเว้นที่สมเหตุสมผล (เช่น delta ใหญ่กว่า spread ทุก run
  ยกเว้น outlier ที่อธิบายได้) ให้เขียนเหตุผล 1 บรรทัดกำกับไว้ในผล แล้วจึงสรุป —
  ห้ามข้ามกติกาแบบเงียบๆ

## 8. Trigger accuracy (บันทึกแยก — ไม่ใช่เกณฑ์ผ่าน/ตก)

สำหรับ arm B ให้จดเพิ่มต่อ run ว่า skill ที่คาดหวังถูกโหลดจริงหรือไม่
(ดูจาก transcript) — "skill ที่ไม่โหลดคือ skill ที่ไม่มีอยู่" ตัวเลขนี้ใช้วินิจฉัย
กลไก triggering เท่านั้น อย่านำไปปนกับ outcome metrics

## 9. ข้อควรระวังอื่น

- fixture `flaky-race` ถูก calibrate บนเครื่องนี้ (อัตรา fail ~43–57% ต่อรอบ —
  ดู `evals/judge/flaky-race-NOTES.md`) — ถ้าเปลี่ยนเครื่อง ให้วัดใหม่ 30 รอบก่อนใช้ผล
- อย่ารันสอง run พร้อมกันบนเครื่องเดียวสำหรับงาน timing-sensitive
  (load ของเครื่องเปลี่ยนอัตรา fail ได้)
- ผลของ arm A เก็บลง `baselines/` ครั้งเดียวต่อ task-version — ถ้าแก้ fixture
  หรือ prompt แม้นิดเดียว baseline เดิมใช้ไม่ได้ ต้องรันใหม่

## 10. งาน delegation (08–09) ต้องรันใน Claude Code session จริงเท่านั้น

งาน 08 และ 09 วัดพฤติกรรม fan-out ผ่าน **Task tool** ดังนั้น:

- **ห้ามรันผ่าน harness ที่ตัวโมเดลเป็น sub-agent อยู่แล้ว** — sub-agent
  spawn sub-agent ของตัวเองไม่ได้ ทุก run แบบนั้นจะกลายเป็น serial โดยบังคับ
  และ metric fan-out จะเป็น 0 อย่างไร้ความหมาย (ไม่ใช่ผลของ arm ไหนทั้งสิ้น)
- ต้องเป็น **interactive Claude Code session ปกติ** (มนุษย์เป็น operator)
  และก่อนเริ่มทุก run ให้ยืนยันว่า Task tool อยู่ในรายการ tool ของ session
  — ถ้าไม่อยู่ ให้ยกเลิก run นั้น
- กติกา copy/contamination ตาม §4–5 ใช้เหมือนเดิมทุกข้อ บวกขั้นตอนเฉพาะ:
  `git init && git add -A && git commit -m pristine` ใน run dir ก่อนเริ่ม
  เพื่อให้อ่าน diff สุดท้ายแบบ mechanical ได้ (รายละเอียดอยู่ในไฟล์ task)
- transcript ของ session จริงคือหลักฐานหลักของ metric ฝั่ง dispatch
  (จำนวน Task calls, ความ concurrent, รายการไฟล์ต่อ agent) — เก็บให้ครบ
