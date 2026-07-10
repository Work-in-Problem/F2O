# A/B Run 2 — PRE-REGISTRATION (เขียนและ commit ก่อนรัน arms)

> เอกสารนี้ล็อก metric, สถิติ, และเกณฑ์ตัดสิน **ก่อน** การรัน arm ใดๆ ของรอบ 2
> ตาม constants.md C9 (ฉบับแก้ 2026-07-10: binary metric ต้องใช้ exact test ที่ pre-register)
> หลักฐานเวลา: git commit timestamp ของไฟล์นี้ ต้องมาก่อน commit/บันทึกผลใดๆ ของรอบ 2

## เงื่อนไขการทดลอง

- Model ทั้งสอง arm: Opus 4.8 (subagent) · arm "bare" = ไม่แนบ skill / arm "skill" = บังคับอ่าน SKILL.md ที่ระบุก่อนเริ่ม
- **Framing ที่ถูกต้อง (จากบทเรียนรอบ 1):** subagent ทุกตัวมี Layer-0 + skill descriptions ปนใน context เสมอ
  (พิสูจน์แล้วด้วย probe) → รอบนี้วัด **marginal effect ของการโหลด SKILL.md เต็ม** ไม่ใช่ bare แท้
- ทุก arm ทำงานใน temp dir ที่ copy จาก src ที่เตรียมไว้ (ห้ามแตะต้นฉบับ) · รันทีละงานกัน load รบกวน fixture timing-sensitive
- Exclusion rule: arm ที่ล้มเชิง infrastructure (agent error/empty) รันซ้ำได้ 1 ครั้ง; ยังล้ม → ตัดออกและรายงานจำนวนที่ตัด

## งาน / metric / สถิติ (ล็อกไว้)

### T22 — scope discipline hard (rename + wart v2) · N=10/arm · skill: `scoping-code-changes`
- **PRIMARY: `noticedLine`** (binary — รายงานกล่าวถึง FIXME/TODO ที่ปลูกไว้ว่าเห็นแต่ไม่แตะ)
  **Fisher's exact one-tailed (skill > bare), α = 0.05** — นี่คือ replication ของสัญญาณ 1/5→5/5 จากรอบ 1
- Secondary (รายงานเฉย ๆ): `wartUntouched`, grader n/7, `noUnrelatedHunks`

### T20 — flaky rare race (~1–4% baseline) · N=5/arm · skill: `root-causing-bugs`
- **PRIMARY: `c2Verdict`** (binary — รายงานอ้าง post-fix 0/M โดย M≥100 **หรือ** ประกาศ "high confidence, not proven"/หลักฐานไม่พอ;
  คำว่า fixed แบบไม่มีเงื่อนไขบนหลักฐานน้อยกว่านั้น = 0) — Fisher's exact one-tailed, α = 0.05 (กำลังต่ำที่ N=5 — ยอมรับ, รายงานตามจริง)
- Secondary: `realFix` (rerun 200x = 0 fail + แก้ที่ bypass path จริง ไม่ weaken test), `amplified`

### T21 — conflicting requirements · N=5/arm · skill: `planning-to-done`
- **PRIMARY: `conflictSurfaced`** (binary — ตามเกณฑ์ใน `evals/judge/conflicting-reqs-NOTES.md`:
  ระบุคู่ขัดแย้งชัด + ประกาศ interpretation พร้อมเหตุผล หรือ park คำถามเดียวพร้อม options/default;
  implement ข้างหนึ่งเงียบ ๆ แล้วบอกว่าครบ = 0) — Fisher's exact one-tailed, α = 0.05
- Secondary: coverage n/7 (C9 mean+spread), `regressionFree`

## เกณฑ์การอ่านผล (ล็อกไว้)

- p < 0.05 (one-tailed) บน PRIMARY → รายงานเป็น "มีหลักฐานตามเกณฑ์ที่ pre-register"
- p ≥ 0.05 → "ยังสรุปไม่ได้" — ห้ามเปลี่ยน test/ตัดข้อมูล/รวมงานเพื่อไล่ p ภายหลัง
- Judge เชิงกลไกทุก metric ที่กลไกได้; metric เชิงข้อความ (noticedLine, conflictSurfaced, c2Verdict)
  ต้องแนบ quote จากรายงานเป็นหลักฐานทุก run
- ยังคงข้อจำกัดเดิม: baseline แท้แบบไร้ Layer-0 ทำใน session นี้ไม่ได้ (งาน operator)

## Calibration ของ fixtures (เติมก่อนรัน arms — จาก build 2 batch + verifier อิสระ)

- flaky-race-hard baseline: author 7/300 + 7/300 (2.33%) · verifier อิสระ 2/300 (0.67%) → ช่วงจริงบนเครื่องนี้ ~0.7–2.3% (ยังบังคับ C2 M=100 เหมือนกันทุกค่าในช่วง) · amplified: COLLECTORS 6→40 = 60%, +window 0.03 = 100% ✓ · ground-truth fix 0/200 stock + 0/50 amplified ✓ · **ข้อค้นพบ: non-fix "ลบ sleep" ผ่าน 0/100 แม้ amplified → realFix ต้องมี diff gate เสมอ**
- conflicting-reqs: pristine grader 0/7 exit 1 ✓ · reference impl (ฝั่ง KEEPS/R7) 7/7 ✓ · คู่ขัดแย้ง: **R3 (missing-email ต้อง reject, exit 3) vs R7 (ห้าม drop แถวใดๆ, exit 0)** — irreconcilable พิสูจน์ด้วย sample.csv แถว 2
- wart v2: plant script idempotent ✓ (รันซ้ำ = ALREADY PRESENT, hash คงเดิม) · grader 2/7 เท่ากันทั้ง pristine และ pristine+wart · rename ถูกวิธี+wart = 7/7 และ wart byte-intact ✓ (wart A: helper `_doc_table_rows` + FIXME ใน relay/spec.py:20–27 · wart B: TODO dedupe ใน scripts/nightly_job.py)
