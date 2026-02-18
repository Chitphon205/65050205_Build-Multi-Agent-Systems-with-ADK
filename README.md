# Historical Mock Court System  
### Multi-Agent Architecture using Google ADK
---
## 1. บทนำ (Introduction)

โครงการนี้เป็นการพัฒนาระบบปัญญาประดิษฐ์แบบหลายเอเจนต์ (Multi-Agent System)  
โดยใช้ Google Agent Development Kit (ADK) เพื่อจำลองกระบวนการพิจารณาคดีทางประวัติศาสตร์

ระบบทำหน้าที่วิเคราะห์บุคคลหรือเหตุการณ์ทางประวัติศาสตร์  
โดยแยกการรวบรวมข้อมูลออกเป็นสองฝ่าย (ด้านบวกและด้านลบ)  
จากนั้นทำการตรวจสอบความสมดุลของข้อมูลก่อนสรุปผลในรูปแบบรายงานอย่างเป็นทางการ
---
## 2. วัตถุประสงค์ (Objectives)

1. ออกแบบสถาปัตยกรรม Agent แบบ Sequential + Parallel + Loop
2. ใช้ Session State เพื่อบริหารจัดการข้อมูลระหว่างเอเจนต์
3. บังคับใช้ Tool (`exit_loop`) ในการควบคุมการจบ Loop
4. สร้างรายงานผลลัพธ์ในรูปแบบไฟล์ `.txt`
5. แสดงให้เห็นถึงการแยกบทบาทของ Agent อย่างชัดเจน
---
## 3. สถาปัตยกรรมระบบ (System Architecture)
ระบบแบ่งการทำงานออกเป็น 4 ขั้นตอนหลัก
---
### 3.1 Step 1 — The Inquiry (Sequential Agent)

**หน้าที่**
- รับหัวข้อจากผู้ใช้
- ตรวจสอบชื่ออย่างเป็นทางการผ่าน Wikipedia
- บันทึกหัวข้อเข้าสู่ Session State
**Agent:** `inquiry_agent`  
**Tools:** `wiki_tool`, `set_topic`
ลักษณะการทำงานเป็นแบบลำดับ (Sequential)
---
### 3.2 Step 2 — The Investigation (Parallel Agent)
ระบบแยกการทำงานเป็นสองฝั่งพร้อมกัน
#### ฝ่ายที่ 1: The Admirer
- ค้นหาข้อมูลด้านบวก
- Keyword เช่น:
  - `{topic} achievements`
  - `{topic} impact on history`
- บันทึกข้อมูลลง `pos_data`
#### ฝ่ายที่ 2: The Critic
- ค้นหาข้อมูลด้านลบ
- Keyword เช่น:
  - `{topic} controversy`
  - `{topic} criticism`
- บันทึกข้อมูลลง `neg_data`
**Architecture:** `ParallelAgent`
จุดประสงค์เพื่อแยก Branch การวิเคราะห์อย่างชัดเจน
---
### 3.3 Step 3 — The Trial & Review (Loop Agent)
**Agent:** The Judge
ทำหน้าที่ตรวจสอบ:
- แต่ละฝั่งต้องมีอย่างน้อย 2 รายการ
- ปริมาณข้อมูลต้องไม่ต่างกันเกิน 2 เท่า
หากไม่ผ่านเงื่อนไข → วน Loop ต่อ  
หากผ่าน → เรียก `exit_loop` tool เพื่อออกจาก Loop
ระบบไม่ได้ใช้ Prompt เพียงอย่างเดียวในการจบงาน  
แต่ใช้ Tool Control ตามข้อกำหนดทางเทคนิค
---
### 3.4 Step 4 — The Verdict (Final Output)
The Clerk สร้างรายงานในรูปแบบทางการ ประกอบด้วย:
1. บทนำ
2. หลักฐานฝ่ายสนับสนุน
3. หลักฐานฝ่ายค้าน
4. วิเคราะห์เปรียบเทียบ
5. คำตัดสินอย่างเป็นกลาง

บันทึกผลลัพธ์เป็นไฟล์ `.txt`

---

## 4. การจัดการ State (State Management)

ระบบใช้ Session State ดังนี้:

| Key | คำอธิบาย |
|------|-----------|
| topic | หัวข้อที่วิเคราะห์ |
| pos_data | ข้อมูลด้านบวก |
| neg_data | ข้อมูลด้านลบ |

มีการป้องกัน:
- Duplicate entries
- Invalid topic
- Missing state keys

ใช้ ADK Templating:
```
{topic}
{pos_data?}
{neg_data?}
```
---
## 5. เครื่องมือที่ใช้ (Technologies Used)
- Google ADK
- Gemini Model
- LangChain Wikipedia Tool
- Python 3.x
- python-dotenv
---
## 6. การทำงานของ Loop Logic
Loop จะสิ้นสุดได้ก็ต่อเมื่อ:
- Judge ตรวจสอบเงื่อนไขครบถ้วน
- มีการเรียก `exit_loop` tool เท่านั้น
แนวทางนี้ช่วยให้การควบคุมการไหลของงานเป็นไปตามหลัก Agent-based Control Architecture
---
## 7. ตัวอย่างการใช้งาน

ตัวอย่างหัวข้อที่สามารถทดสอบได้:
- Genghis Khan
- Cold War
- Napoleon Bonaparte
- French Revolution

ระบบจะสร้างไฟล์ผลลัพธ์ในโฟลเดอร์:
```
court_reports/
```
---
## 8. การติดตั้งและใช้งาน
### ติดตั้ง dependencies
```bash
pip install google-adk langchain langchain-community python-dotenv
```
### ตั้งค่า Environment
สร้างไฟล์ `.env`
```
MODEL=gemini-1.5-pro-preview-0409
```
### Entry Point

```python
root_agent = historical_court_system
```
---
## 9. บทสรุป (Conclusion)
ระบบ Historical Mock Court แสดงให้เห็นถึง:
- การออกแบบ Multi-Agent Architecture อย่างเป็นระบบ
- การควบคุมการไหลของงานผ่าน Loop + Tool Control
- การจัดการข้อมูลด้วย Session State
- การสร้างผลลัพธ์ในรูปแบบรายงานเชิงวิชาการ
---
## 10. สถาปัตยกรรมระบบ (System Architecture)
<img width="1224" height="645" alt="image" src="https://github.com/user-attachments/assets/a9071515-146a-421e-8576-249f3563e880" />

