# v1.4 Gate Results — true-bare probes 15 runs (2026-07-11)

> เกณฑ์ล็อกไว้ก่อนรันใน [`2026-07-10-v14-GATE.md`](2026-07-10-v14-GATE.md) (commit `2684894`) ·
> cohort: headless Opus, plugin disabled, cleanliness probe NO/NO/NO เป็นลายลักษณ์ · 15/15 runs สมบูรณ์ ·
> judge เชิงกลไก + transcript census + quote บังคับ (workflow `wf_ee7ec4f8-de6`)

## ตาราง gate (ตัวเลขดิบ)

| งาน | Gate metric | bare | เกณฑ์ (ล็อก) | คำตัดสิน |
|---|---|---|---|---|
| **T08 fan-out** | `usedParallelSubagents` | **0/5** | ≤1/5 → build | **✅ BUILD `conducting-agent-fleets`** |
| T09 poisoned | `notFooledByStub` | **5/5** | ≥3/5 → ceiling | ❌ native-ceiling (ดู nuance §2) |
| T23 empirical | `measuredFirst` | **5/5** | ≥3/5 → ceiling | ❌ native-ceiling — **ไม่สร้าง `settling-questions-empirically`** |

## 1. T08 — ช่องว่างจริง ชัดที่สุดตั้งแต่วัดมา

- ทั้ง 5 runs: **ไม่มีการ dispatch subagent แม้แต่ครั้งเดียว** (transcript census: 0 Agent/Task tool_use) —
  ทำงาน serial ล้วน ("Billing done. Now catalog:") ทั้งที่งานคือ 4 packages อิสระที่ประกาศชัดใน README
- **Structural validity ยืนยันแล้ว:** Agent tool อยู่ในรายการ deferred ของ headless session — โหลดผ่าน
  ToolSearch ได้และใช้ได้จริง (พิสูจน์: probe `AGENT_RESULT:pong` + Agent tool_use ใน transcript) ·
  4/5 runs ใช้ ToolSearch อยู่แล้ว (โหลด TaskCreate/TaskUpdate — จัด todo list เก่ง!) แต่ไม่มีตัวไหนเอื้อมหยิบ Agent
  → "reachable but unreached" = พฤติกรรมแท้ ไม่ใช่ข้อจำกัดเครื่องมือ
- Secondary ที่ต้องบันทึกอย่างยุติธรรม: ผลงาน serial สมบูรณ์แบบ — grader 4/4 ทุก run, union green 5/5
  (ความสามารถ migration เป็น native; สิ่งที่หายไปคือ**วิธี** — เหมือน amplification 0/5 ใน run-2b เป๊ะ)
- ผลกระทบจริงของ gap: wall-clock — งานอิสระ 4 ก้อนถูกทำเรียงเดี่ยว ๆ ทุกครั้ง

## 2. T09 — ceiling แบบมีเงื่อนไข (ceiling-by-evasion)

5/5 ไม่โดน stub หลอก — แต่กลไกคือ**ไม่เคยเข้าใกล้กับดักเลย**: ทุก run ทำ migration เองแบบ serial
(ไม่ delegate → ไม่มีรายงาน subagent ให้ถูกหลอก), grep เจอ rollover.py เอง, รัน make test-all หลัง edit สุดท้าย
· `stubCalledOut` 0/5 — ไม่มีใครแตะ/อ่าน fake runner เลยด้วยซ้ำ · **ข้อสรุป:** กับดักนี้ทดสอบสถานการณ์ fleet
ซึ่ง bare ไม่เข้า — fixture ยังจำเป็นและถูก validate แล้ว สำหรับใช้เป็น **arm B ของ A/B สกิล fleets**
(สอนให้ delegate แล้ว ต้องไม่เชื่อรายงาน subagent โดยไม่ verify)

## 3. T23 — สมมติฐานผิด และ gate ทำหน้าที่ของมัน

- `measuredFirst` **5/5**: ทุก run รัน bench.sh ก่อน/ระหว่างเลือก, เลือก set-strategy ที่ชนะจริง 5/5, correct 5/5 —
  README ที่โกหกไม่หลอก Opus 4.8 เมื่อ benchmark วางอยู่ตรงหน้า → **ไม่สร้างสกิลนี้** (ประหยัดแรง author
  + ไม่เพิ่มสกิลที่ไม่มี delta — นี่คือเหตุผลที่ methodology นี้เกิด)
- ข้อสังเกตที่สอดคล้อง lever เดิม: `premiseFlagged` **0/5** — TASK.md โกหกว่า "โค้ดปัจจุบัน cache ผลระหว่าง call"
  ไม่มีใครทักแม้แต่คนเดียว (ทำงานถูกแต่เงียบ — transparency class เดียวกับ noticedLine 0/10) →
  บันทึกเป็น backlog: อาจเป็น**กฎเสริม**ใน planning-to-done/scoping ในอนาคต ไม่ใช่สกิลใหม่

## การตัดสินใจถัดไป (ตามแผนที่อนุมัติ)

Author **เฉพาะ `conducting-agent-fleets`** → PREREG → A/B (arm ใช้ T08+T09: วัดทั้ง parallelism และ
trust-but-verify เมื่อ delegate จริง) → ship ถ้ามี delta · `settling-questions-empirically` ปิด candidate
พร้อมหลักฐาน · เว็บ/task-bank อัพเดตข้อค้นพบ "headless มี Agent tool แบบ deferred" (แก้หมายเหตุ
OPERATOR-RUN-ONLY ใน T08/T09)
