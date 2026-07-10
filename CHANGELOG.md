# Changelog

รูปแบบตาม [Keep a Changelog](https://keepachangelog.com) · เวอร์ชันตาม [SemVer](https://semver.org)
(นโยบายฉบับเต็ม: [VERSIONING.md](VERSIONING.md))

## [Unreleased]

## [1.3.0] — 2026-07-10 · "The Validation Release"
### Added
- **ผลการทดลองยืนยันประสิทธิผล (pre-registered):** พฤติกรรม "เห็นปัญหาข้างเคียง → รายงานโดยไม่แตะ" — Opus เปล่าแท้ **0/10** vs F2O **10/10**, Fisher's exact one-tailed **p≈5.4×10⁻⁶** พร้อม dose-response 4 ระดับ (0/10 → 1/5 → 9/10 → 10/10) · ผลรอง: F2O เปลี่ยนวิธีวินิจฉัย flaky bug (amplification 0/5 → 5/5) · เอกสารเต็ม: `evals/results/` (PREREG commit ก่อนรันทุกรอบ ตรวจย้อนได้ใน git)
- **Fixtures ยาก 3 ชุด + tasks 20–22** สำหรับใครก็ตามที่อยากทำซ้ำ/หักล้าง: `flaky-race-hard` (race ~2% ที่บังคับวินัยสถิติ), `conflicting-reqs` (requirement ขัดแย้งจริงแบบพิสูจน์ได้), `plant-wart-v2` (กับดัก scope สุดยั่ว)
- **เว็บ:** แถบผลการทดลองบน hero + Nerd Zone ยกเครื่องเป็นรายงานวิชาการฉบับเผยแพร่ (Abstract → Method → Results → Threats to Validity → Reproduce) + typography ไทย/อังกฤษเก็บละเอียด
### Changed
- ปลดป้าย exploratory ของ claim 1/5→5/5 → แทนด้วยผลยืนยัน 0/10→10/10 ทุกจุดที่อ้างถึง
- คู่มือ PDF ถอนออกจากจุด user-facing (เว็บ 2 ภาษาแทนที่โดยสมบูรณ์)
### หมายเหตุสำหรับผู้ใช้
- **ไม่มีการเปลี่ยน skills / hooks / commands ใดๆ** — พฤติกรรม plugin เหมือน 1.2.0 ทุกประการ อัพเดตได้อย่างปลอดภัย


## [1.2.0] — 2026-07-10
### Added
- `/f2o:update` — เช็คเวอร์ชันใหม่จาก GitHub แบบผู้ใช้สั่งเอง (on-demand, ไม่มี phone-home อัตโนมัติ) พร้อมบอกคำสั่งอัพเดต/ย้อนเวอร์ชัน
- `VERSIONING.md` + `CHANGELOG.md` — นโยบายเวอร์ชัน, release checklist, วิธี rollback ด้วย git tag

## [1.1.2] — 2026-07-10
### Fixed
- claim-gate: นับ `curl` probe เป็น verification (แก้ false-block บนงานเว็บ) — suite 32 tests

## [1.1.1] — 2026-07-10
### Fixed
- คำสั่ง toggle เปลี่ยนไปใช้ `!`-preprocessing (การให้โมเดลรัน Bash ติด permission prompt ใน headless)

## [1.1.0] — 2026-07-10
### Changed
- **เปลี่ยนชื่อ plugin `fable2opus` → `f2o`** (คำสั่ง/สกิลถูก namespace ด้วยชื่อ plugin เสมอ — ทำให้ทุกอย่างสั้นลง: `/f2o:vbc`)
### Added
- `/f2o:off` · `/f2o:on` · `/f2o:status` — soft-off ผ่าน state file `~/.claude/f2o.disabled` (hook เงียบ, สกิลยังใช้ได้)
- Shorthand 13 ตัว `/f2o:vbc` … `/f2o:ivc` + โฟลเดอร์ `aliases/` สำหรับสาย manual (`/vbc` แบบไม่มี prefix)

## [1.0.2] — 2026-07-10
### Changed
- ย้ายบ้านเป็น `Work-in-Problem/F2O` + แบรนด์ Work in Problem (history ใหม่)
### Fixed
- SessionStart ฉีด Layer 0 เป็น digest ≤2KB (Claude Code เก็บ context จาก hook ได้ ~2KB — ฉบับเต็ม 11KB โดนตัด)

## [1.0.0] — 2026-07-10
- เผยแพร่ครั้งแรก: 13 skills + Layer-0 core + claim-gate hook + ติดตั้งสองช่องทาง (plugin / npx skills)
