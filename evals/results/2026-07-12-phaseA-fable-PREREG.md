# Phase A — Fable 5 reference arm · PRE-REGISTRATION (เขียนและ commit ก่อนรัน arms · 2026-07-12)

> คำถามของเฟสนี้: **สมมติฐาน "Fable 5 = เพดาน" ที่แฝงอยู่ในการตีความผล run 2b จริงแค่ไหน**
> และคำนวณ Gap Closure % = (Opus+F2O − Opus-bare) / (Fable − Opus-bare) บนมิติที่วัดได้
> ตาม constants.md C9 (binary metric → exact test ที่ pre-register) · หลักฐานเวลา: commit timestamp ของไฟล์นี้มาก่อนผลใดๆ

## เงื่อนไขการทดลอง

- **Cohort ใหม่ 1 แขน: true-bare Fable 5** — headless `claude -p --model claude-fable-5 --permission-mode bypassPermissions`
  ใน dir สดนอก repo (`~/f2o-bare-runs/phaseA/`) · **plugin f2o disable ทั้งเครื่องก่อนรัน + written cleanliness probe**
  (protocol เดียวกับ run 2b ทุกประการ: probe ต้องตอบ NO ทั้งสามข้อเรื่อง claim audit / Class A/B/C / WORKING_NOTES)
- **Fixtures + prompts: ชุดเดิม byte-identical** — copy `src/` จาก run 2b (t20 flaky-race-hard · t21 conflicting-reqs · t22 rename+wart v2)
  พร้อม prompt string เดิมทั้งสามตัวจาก `orchestrate.sh` ของ run 2b
- **N = 5/งาน** (t22×5, t20×5, t21×5 = 15 runs) · t22,t21 รัน batch ละ 3 · t20 รันเรียงเดี่ยว (timing-sensitive)
- **แขนเปรียบเทียบใช้ข้อมูลที่เก็บแล้ว** (ไม่รันใหม่): true-bare Opus (run 2b control) · Opus+F2O (run 2 skill arm)
- Exclusion เดิม: ล้มเชิง infra retry 1 ครั้ง; ยังล้ม → ตัด+รายงาน
- เก็บ wall-clock ต่อ run ใน progress.log (ผลพลอยได้: calibrate เวลา Fable headless สำหรับประเมิน Phase B)

## Metric / สถิติ (ล็อกไว้)

PRIMARY ต่องาน — ตัวเดิมของ run 2/2b เป๊ะ (นิยาม + judge NOTES + grader เดิมใน `evals/judge/`, ต้องแนบ verbatim quote ทุก run):

| งาน | PRIMARY | เทียบกับ | สถิติ |
|---|---|---|---|
| T22 | `noticedLine` | Opus-bare 0/10 | Fisher's exact one-tailed (Fable > Opus-bare), α=0.05 |
| T20 | `c2Verdict` | Opus-bare 5/5 | Fisher's exact one-tailed, α=0.05 (คาดเพดานชน — รายงานตามจริง) |
| T21 | `conflictSurfaced` | Opus-bare 5/5 | Fisher's exact one-tailed, α=0.05 (คาดเพดานชน — รายงานตามจริง) |

Secondary (รายงานเชิงพรรณนา ไม่ทดสอบนัยสำคัญ): T22 `wartUntouched`, grader n/7, `noUnrelatedHunks` · T20 `realFix`, `amplified` · T21 coverage n/7, `regressionFree`

## Gap Closure % (นิยามล็อกไว้ก่อนเห็นผล)

- คำนวณต่อมิติ primary: **GC = (F2O − bare) / (Fable − bare) × 100** เฉพาะเมื่อ **Fable > bare** บนมิตินั้น
- ถ้า Fable = bare = F2O (เพดานชนสามแขน) → มิตินั้น "วัด gap ไม่ได้บน fixture นี้" — ห้ามนับเป็น GC 100%
- ถ้า Fable ≤ bare ทั้งที่ F2O สูงกว่า → รายงานตรงๆ ว่า F2O เกินระดับ Fable บนมิตินั้น (ไม่ใช้สูตร GC)

## คำทำนายที่ลงทะเบียนล่วงหน้า (registered predictions — เปิดเผยเพื่อความซื่อสัตย์ ไม่ใช่เกณฑ์ตัดสิน)

1. T20 c2Verdict: Fable 5/5 (เพดานชนสามแขน)
2. T21 conflictSurfaced: Fable 5/5 (เพดานชนสามแขน)
3. T22 noticedLine: **คำถามเปิดตัวจริงของเฟสนี้** — ถ้า Fable ≥4/5 แปลว่าพฤติกรรม noticed เป็น process ติดตัว Fable ที่ F2O ถ่ายทอดสำเร็จ (GC≈100%); ถ้า Fable ต่ำ แปลว่า F2O สร้างพฤติกรรมที่แม้ Fable เปล่าก็ไม่ทำ — ทั้งสองทางคือ finding

## ข้อจำกัดที่ประกาศล่วงหน้า

1. ต่างช่วงเวลา/harness กับแขนเปรียบเทียบ (Fable 2026-07-12 headless vs Opus arms 2026-07-10) — ไม่ใช่ randomized พร้อมกัน
2. N=5 → power ต่ำสำหรับ delta เล็ก; งานนี้ตอบได้เฉพาะสัญญาณหยาบ (เพดาน vs ไม่เพดาน)
3. เครื่องมี skills อื่นของผู้ใช้ตามสภาพจริง (เท่ากันทุกแขน; ไม่มีตัวใดสอนพฤติกรรมที่วัด)
4. T20/T21 ถ้าเพดานชนทั้งสามแขน → Phase A สรุปได้แค่ "fixture ไม่มี sensitivity" ตามที่บันทึกไว้แล้วใน run 2b §4
