# นโยบายเวอร์ชันและการปล่อยอัพเดต (Versioning & Release Policy)

> ระบบอ้างอิง: [Semantic Versioning](https://semver.org) — `MAJOR.MINOR.PATCH` เช่น `1.2.0`
> กลไกสำคัญของ Claude Code: **ผู้ใช้จะได้รับอัพเดตก็ต่อเมื่อเลข `version` ใน `plugin.json` ถูก bump เท่านั้น** —
> push commit ลง main โดยไม่ bump = ผู้ใช้ไม่ได้รับอะไรเลย (นี่คือฟีเจอร์ ไม่ใช่บั๊ก)

## 1. เมื่อไหร่ bump อะไร

| ระดับ | เมื่อไหร่ | ตัวอย่าง |
|---|---|---|
| **MAJOR** `2.0.0` | ของเดิมพัง/เปลี่ยนความหมาย: เปลี่ยน-ลบชื่อ skill หรือคำสั่ง, เปลี่ยนชื่อ plugin/marketplace, เปลี่ยนกฎแกนจนพฤติกรรมเดิมไม่เหมือนเดิมอย่างมีนัย | rename `fable2opus`→`f2o` (ถ้าเกิดหลังมีผู้ใช้จริง) |
| **MINOR** `1.2.0` | เพิ่มความสามารถโดยของเดิมไม่พัง: skill ใหม่, คำสั่งใหม่, กฎใหม่, hook ใหม่ | เพิ่ม `/f2o:update` |
| **PATCH** `1.1.3` | แก้บั๊ก/ปรับคำ/แก้ false-positive โดยพฤติกรรมที่ตั้งใจไม่เปลี่ยน | เพิ่ม `curl` เข้า verify regex |

**กติกาสำคัญ — ห้าม bump ทุก commit:** งานเล็กๆ ให้สะสมบน `main` เฉยๆ (ผู้ใช้ไม่โดนกระทบ)
แล้ว**ปล่อยเป็นรอบ (release train)** เมื่อสมเหตุสมผล เช่น สะสม patch หลายตัวค่อยปล่อย `x.y.Z+1` ทีเดียว
· bump เฉพาะใน commit ปล่อยจริงเท่านั้น

## 2. ขั้นตอนปล่อยเวอร์ชัน (release checklist)

1. งานทั้งหมดอยู่บน `main` แล้ว และ `bash hooks/tests/run_hook_tests.sh` เขียว
2. อัพเดต `CHANGELOG.md` — ย้ายรายการจาก `[Unreleased]` เข้า section เวอร์ชันใหม่ (รูปแบบ [Keep a Changelog](https://keepachangelog.com))
3. Bump `version` ใน `.claude-plugin/plugin.json`
4. Commit เดียว: `release: vX.Y.Z` → **`git tag vX.Y.Z`** → `git push && git push --tags`
5. (แนะนำ) `gh release create vX.Y.Z --notes-file <changelog section>` — ผู้ใช้ที่กด **Watch → Releases** บน GitHub จะได้อีเมลแจ้งอัตโนมัติ
6. ตรวจรับบนเครื่องตัวเอง: `claude plugin marketplace update f2o && claude plugin update f2o@f2o` → เห็นเลขใหม่

## 3. ฝั่งผู้ใช้: อัพเดต / เช็ค / ย้อนเวอร์ชัน

**อัพเดต (manual — ค่าเริ่มต้น):**
```
claude plugin marketplace update f2o
claude plugin update f2o@f2o        # แล้ว /reload-plugins หรือเปิด session ใหม่
```
**เช็คว่ามีเวอร์ชันใหม่ไหม:** พิมพ์ `/f2o:update` ใน session (ยิง request เดียวไป GitHub *เฉพาะตอนผู้ใช้สั่ง* —
ไม่มี phone-home อัตโนมัติ ตามสัญญา no-telemetry) หรือกด Watch → Releases ที่ repo

**Auto-update:** Claude Code มีระบบอัพเดตอัตโนมัติตอนเปิดโปรแกรม แต่ marketplace บุคคลทั่วไป
**ปิดเป็นค่าเริ่มต้น** — ผู้ใช้เปิดเองได้ที่ `/plugin` → Marketplaces → `f2o` → Enable auto-update
(เหมาะกับสายชอบของใหม่; สายระวังใช้ manual + อ่าน changelog ก่อน)

**ย้อนเวอร์ชัน (rollback) — ใช้ git tag เป็นหมุด:**
```
claude plugin uninstall f2o@f2o
claude plugin marketplace remove f2o
claude plugin marketplace add Work-in-Problem/F2O@v1.1.2   # ← tag เวอร์ชันที่ต้องการ
claude plugin install f2o@f2o
```
catalog ที่ pin ด้วย tag จะ**ค้างที่เวอร์ชันนั้น**จนกว่าผู้ใช้จะ re-add แบบไม่ pin — นี่คือพฤติกรรมที่ต้องการ
· ทดสอบชั่วคราวแบบไม่ติดตั้ง: `git clone -b vX.Y.Z … && claude --plugin-dir ./F2O` (มีผลเฉพาะ session นั้น)
· สาย npx skills: ไม่มีระบบ pin — ย้อนโดย clone ที่ tag แล้ว copy มือตามทาง C

## 4. สาย npx skills

`npx skills update` = อัพเดตเป็น latest เท่านั้น (ไม่มี pin/แจ้งเตือน) — สายนี้ควรถูกชี้มาที่ GitHub Releases
เป็นช่องทางติดตามเวอร์ชัน
