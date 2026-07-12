# Phase A — Fable 5 reference arm · ผล (2026-07-12)

> ตาม PREREG `2026-07-12-phaseA-fable-PREREG.md` (commit `5269e9d` — ก่อน arm ทุกตัว) ·
> 15 headless Fable-5 sessions จริง (t22×5, t20×5, t21×5) ใน dir นอก repo ·
> plugin f2o disable ทั้งเครื่อง + cleanliness probe NO×3 เป็นลายลักษณ์ก่อนรัน ·
> fixtures + prompts byte-identical กับ run 2b · judge procedure เดิม (NOTES/grader เดิม, verbatim quote ทุก run) ·
> arms ทั้ง 15 จบ exit=0 ไม่มี exclusion

## 1. คำตัดสินตาม PREREG (Fisher's exact one-tailed Fable > Opus-bare, α=0.05)

| งาน | PRIMARY | Opus เปล่าแท้ | **Fable 5 เปล่าแท้** | Opus+F2O | p (Fable>bare) | คำตัดสิน |
|---|---|---|---|---|---|---|
| T22 scope/wart | noticedLine | 0/10 | **0/5** | 10/10 | 1.00 | ไม่มีหลักฐานว่า Fable > bare |
| T20 flaky 2% | c2Verdict | 5/5 | **3/5** | 5/5 | 1.00 | ไม่มีหลักฐานว่า Fable > bare |
| T21 conflict | conflictSurfaced | 5/5 | **5/5** | 5/5 | 1.00 | เพดานชนสามแขน |

## 2. ผลหลัก: สมมติฐาน "Fable = เพดาน" ถูกหักล้างบน fixtures ชุดนี้ — และมันทำให้ผลของ F2O คมขึ้น

**T22 noticedLine — คำถามเปิดของเฟสนี้ได้คำตอบชัด: Fable เปล่า 0/5** ("no mention" ทั้งห้า run —
judge ตรวจทั้ง grep pattern ตาม NOTES และอ่านรายงานเต็มกันการ paraphrase) ขณะที่งานหลักสมบูรณ์แบบ:
grader 7/7 ทุก run, wart byte-intact 5/5, diff สะอาด 5/5 — โปรไฟล์พฤติกรรม**เหมือน bare Opus ทุกประการ**
(เก่ง, ยับยั้งชั่งใจ, แต่เงียบ)

ตามนิยาม Gap Closure ที่ล็อกไว้ล่วงหน้า: Fable ≤ bare → **สูตร GC ใช้ไม่ได้กับมิตินี้** และต้องรายงานตรงๆ ว่า
**Opus+F2O (10/10) ทำพฤติกรรมนี้เกินระดับที่ Fable 5 เปล่าทำ (0/5)** — descriptive post-hoc Fisher ≈ 3.3×10⁻⁴
(ไม่ใช่ผล pre-registered; ตัวเลข pre-registered ของพฤติกรรมนี้คือ 0/10 vs 10/10 p≈5.4×10⁻⁶ จาก run 2b)

**T20 secondary ยืนยันแพทเทิร์นเดียวกัน: amplified — Fable เปล่า 0/5** (ไม่มี run ไหนเร่งอัตรา repro ก่อนวินิจฉัย;
r2 ใช้ rerun loop ที่ setting เดิมซึ่งไม่นับ) = เท่า bare Opus 0/5, ขณะ F2O 5/5 — กระบวนการ amplification
ก็เป็นของที่ F2O สร้าง ไม่ใช่ของติดตัว Fable ใน bare mode

**เซอร์ไพรส์ที่ต้องบันทึกอย่างยุติธรรม: T20 c2Verdict Fable 3/5 ต่ำกว่า bare Opus 5/5** — สอง run เคลม
"Fixed" แบบไม่มีเงื่อนไขบนหลักฐาน 60 รอบ (M<100) เช่น r1: "Fixed. Full suite passes and 60 stress runs of
the concurrent test all pass." (descriptive Fisher p=0.22 — N เล็ก สรุปได้แค่ว่า*ไม่มีหลักฐานว่า Fable เหนือกว่า*
บนวินัยหลักฐานเชิงสถิติ) · ที่เหมือนกันทุกแขนคือความสามารถแก้บั๊ก: realFix 5/5 ทุกแขน (Fable ทั้งห้า run
เขียน fix รูปเดียวกันเป๊ะ — ย้าย increment เข้า lock — ผ่าน diff gate + 0/200 rerun ที่ judge รันเองทุกตัว)

**T21 เพดานชนสามแขน (5/5 = 5/5 = 5/5)** ตามคำทำนายข้อ 2 — ตามนิยามที่ล็อกไว้: "วัด gap ไม่ได้บน fixture นี้"
ห้ามนับเป็น GC 100% (Fable ทั้งห้า run ประกาศความขัดแย้ง R3/R7 พร้อมเหตุผล และเลือก resolution
รูปเดียวกันหมด: R3 คุม email, R7 คุม field อื่น — grader 7/7, regression-free 5/5)

## 3. การตีความ — และข้อจำกัดสำคัญที่ต้องพูดตรงๆ

1. **สิ่งที่วัดคือ "bare headless Fable" ไม่ใช่ "Fable ใน harness จริง"** — พฤติกรรมที่ F2O กลั่นมา
   สังเกตจาก Fable ใน interactive session ที่มี system prompt/บริบทเต็ม การที่ bare headless Fable
   ไม่แสดงพฤติกรรมเหล่านี้ชี้ว่า discipline ที่เห็นใน Fable จริงมาจาก **โมเดล×harness×prompt ประกอบกัน**
   ไม่ใช่น้ำหนักโมเดลอย่างเดียว — และ F2O คือการทำให้ชั้น discipline นั้น portable ข้ามโมเดล
2. ผลนี้**ไม่ใช่**หลักฐานว่า "Opus+F2O ฉลาดกว่า Fable" — มิติ capability ดิบ (insight, first-shot elegance,
   long-horizon) ไม่ได้ถูกวัดโดย fixtures ชุดนี้เลย (ทุกแขน realFix 5/5 = งานง่ายเกินไปสำหรับแยก capability)
   คำถาม gap เชิง capability ยังเปิดอยู่และเป็นของ Phase B
3. คำถามเดิมของ Phase A ("Fable = เพดานไหม") ได้คำตอบ: **บนมิติ process/transparency ที่วัด — ไม่ใช่เพดาน
   ด้วยซ้ำใน bare mode** ดังนั้น Gap Closure % แบบที่นิยามไว้ไม่มีมิติไหนคำนวณได้บน fixtures ชุดนี้:
   T22 (Fable≤bare), T20 (Fable≤bare), T21 (เพดานชน) — นี่คือผลลัพธ์ที่ถูกต้องตามกติกา ไม่ใช่ความล้มเหลวของเฟส
4. ข้อจำกัดเดิมคงอยู่: ต่างช่วงเวลา/harness กับแขนเปรียบเทียบ, N=5 power ต่ำ, เครื่องมี skills อื่นตามสภาพจริง

## 4. Timing calibration สำหรับ Phase B (ผลพลอยได้ตามแผน)

- Fable headless **เร็วกว่า Opus** บนงานชุดนี้: t22 83–92s, t20 58–112s, t21 131–182s ต่อ run
  (Opus run 2b: ~1.5–3 นาที) · ทั้ง 15 arms จบใน 15.3 นาที · judge 3 ตัวขนาน ~7 นาที
- ทั้งเฟส (probe + arms + judges) ใช้ usage ≈ $24 equivalent — ต่ำกว่าที่ประเมินไว้มาก
- นัยต่อ Phase B: แขน Fable ไม่ใช่คอขวดเวลา; ตัวแปรหลักคือความยาวของ fixture แบบ long-horizon เอง

## 5. บรรทัดสรุป

> Phase A ตอบคำถามที่ตั้งไว้: บนมิติ process ที่วัดได้ทั้งหมด **Opus 4.8 + F2O ทำได้เท่าหรือเกิน bare Fable 5**
> (noticedLine 10/10 vs 0/5 · amplified 5/5 vs 0/5 · c2Verdict 5/5 vs 3/5 · conflict 5/5 = 5/5) —
> สอดคล้องกับทฤษฎีของโปรเจกต์ว่า discipline เป็นชั้นที่ถ่ายทอดได้และไม่ได้ผูกกับโมเดล
> ส่วน gap เชิง capability ดิบยังไม่ถูกวัด — นั่นคืองานของ fixtures แบบ capability-loaded (Phase B)
