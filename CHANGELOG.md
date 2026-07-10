# Changelog

รูปแบบตาม [Keep a Changelog](https://keepachangelog.com) · เวอร์ชันตาม [SemVer](https://semver.org)
(นโยบายฉบับเต็ม: [VERSIONING.md](VERSIONING.md))

## [Unreleased]

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
