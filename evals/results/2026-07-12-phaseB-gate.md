# Phase B — difficulty-gate result: bare Opus ชนเพดานทั้ง 3 fixtures ใหม่ (2026-07-12)

> ตาม methodology baseline-first gate (มาตรฐานตั้งแต่ v1.4): probe ความยากก่อน lock PREREG/รัน arms —
> รอบนี้ gate **ตัดสินให้ไม่รัน arms** และประหยัดงบ ~45 runs บน fixtures ที่ไม่มี sensitivity

## Probe (bare Opus แท้ · plugin disabled + cleanliness probe NO×3 · N=2/fixture · headless นอก repo)

| Fixture | ช่วงคะแนนที่ตั้งใจ (จาก calibration) | bare Opus r1 | bare Opus r2 | wall/run |
|---|---|---|---|---|
| T24 long-horizon-retention (n/12) | naive ~6–9 · ref 12 | **12/12** | **11/12** | 323–392s |
| T25 hidden-edges (n/30) | naive 12 · ref 30 | **30/30** | **30/30** | 143–215s |
| T26 endurance-enum (k/40) | คาด single-pass ~20–32 · ref 40 | **40/40** (REGRESSIONS 0) | **40/40** (REGRESSIONS 0) | 363–413s |

- Vandalism sweep สะอาดทุก run (t24-r1 มีแค่*เพิ่ม*ไฟล์ test ใหม่ — ของเดิม byte-intact, TASK.md/runner intact;
  t25 SPEC/tests/runner intact ทั้งคู่; t26 UNRELATED เป็นแค่ harness artifacts: FINAL_REPORT.md/exit_code/stderr.log)
  → **คะแนนเพดานเป็นของแท้ ไม่ใช่การโกง**
- Fixtures ผ่าน independent verifier ก่อน probe (calibration reruns exact, gaming audit แข็ง โดยเฉพาะ T26
  ที่พิสูจน์ว่า delete-to-pass เป็นไปไม่ได้ครบ 40 anchor) — ความยากที่ตั้งใจไว้อิง "naive/single-pass agent"
  ซึ่งปรากฏว่า**ต่ำกว่าพฤติกรรมจริงของ bare Opus 4.8 อย่างมาก**

## ความหมาย

1. **Bare Opus 4.8 ทำงาน coding แบบ self-contained + spec ชัด + ตรวจเชิงกลไกได้ ถึงเพดานที่ขนาดงานระดับนี้**
   (12 interlocking reqs / 30 spec corners / สวีป 40 จุดใน 38 ไฟล์) — สอดคล้องและขยายผล native-ceiling
   ที่บันทึกไว้ใน run 2b §3 และ v1.4/v1.5 gates
2. คำถาม "gap เชิง capability ระหว่าง Fable 5 กับ Opus 4.8" **ยังไม่มี fixture ในชุดนี้ที่วัดได้** —
   การรัน 3 แขนบนของที่เพดานชนจะได้ 45 runs ที่ไม่มีอำนาจจำแนก จึงไม่รันตามวินัย gate
3. Fixtures ทั้งสาม**ไม่เสียเปล่า**: เป็น fixtures คุณภาพผ่าน verifier ที่ใครก็ reproduce ได้ และตอนนี้ทำหน้าที่เป็น
   หลักฐาน native-ceiling ของ Opus 4.8 บนงานระดับนี้ · ถ้าจะวัด gap ต่อ ต้องออกแบบด้วยหลักอื่น
   (เช่น performance bar ที่ต้องการ algorithmic insight, สเกล 100+ ไฟล์/50+ requirements, หรือ spec กำกวมที่ตัดสินด้วย rubric)
4. หมายเหตุ grader T26: ควรเพิ่ม FINAL_REPORT.md/exit_code/stderr.log เข้า exclusion list ของ UNRELATED
   (พบระหว่าง probe — ไม่กระทบคะแนน SCORE/REGRESSIONS)

## สถานะการทดลอง

- ไม่มี PREREG ถูก lock สำหรับ arms (gate ตัดก่อน) — เอกสารนี้คือบันทึก gate ตามแบบ v1.4/v1.5
- Probe artifacts: 6 run dirs (`probe-opus-t24/25/26-r1/2`) เก็บนอก repo
- Plugin เปิดกลับหลัง probe เสร็จ
