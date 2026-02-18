# ==========================================================
# ⚖️ HISTORICAL MOCK COURT SYSTEM (FULL MARK VERSION)
# ==========================================================

import os
from datetime import datetime
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.models import Gemini
from google.adk.tools import exit_loop
from google.genai import types

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()

MODEL_NAME = os.getenv("MODEL", "gemini-1.5-pro-preview-0409")
RETRY = types.HttpRetryOptions(initial_delay=1, attempts=6)


# ==========================================================
# WIKIPEDIA TOOL
# ==========================================================

api_wrapper = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=5000)
wiki_tool = LangchainTool(tool=WikipediaQueryRun(api_wrapper=api_wrapper))


# ==========================================================
# CUSTOM TOOLS
# ==========================================================

def set_topic(tool_context: ToolContext, official_topic: str):
    if not official_topic.strip():
        return {"status": "error", "message": "Invalid topic"}

    tool_context.state["topic"] = official_topic
    tool_context.state["pos_data"] = []
    tool_context.state["neg_data"] = []
    return {"status": "ok"}


def append_state(tool_context: ToolContext, key: str, content: str):
    data = tool_context.state.get(key, [])

    # Prevent duplicate entries
    if content not in data:
        data.append(content)

    tool_context.state[key] = data
    return {"status": "ok"}


def write_report(tool_context: ToolContext, content: str):
    topic = tool_context.state.get("topic", "Report")
    pos = tool_context.state.get("pos_data", [])
    neg = tool_context.state.get("neg_data", [])

    folder = "court_reports"
    os.makedirs(folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(folder, filename)

    header = f"""
=========================================
HISTORICAL MOCK COURT REPORT
Topic: {topic}
Generated at: {timestamp}
Positive Evidence Count: {len(pos)}
Negative Evidence Count: {len(neg)}
=========================================
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n" + content)

    return {"status": "saved", "path": path}


# ==========================================================
# STEP 1 – INQUIRY
# ==========================================================

inquiry_agent = Agent(
    name="inquiry_agent",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY),
    instruction="""
    1. ใช้ wiki_tool ตรวจสอบชื่ออย่างเป็นทางการจาก Wikipedia
    2. หากไม่พบข้อมูล ให้แจ้ง error
    3. หากพบ ให้เรียก set_topic
    """,
    tools=[wiki_tool, set_topic]
)


# ==========================================================
# STEP 2 – INVESTIGATION (Parallel)
# ==========================================================

admirer = Agent(
    name="admirer",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY),
    instruction="""
    บทบาท: The Admirer

    วิเคราะห์หัวข้อ: "{topic}"

    ค้นหาด้านบวกโดยใช้คำค้น:
    - "{topic} achievements"
    - "{topic} major accomplishments"
    - "{topic} impact on history"

    สรุปเป็น bullet ภาษาไทย
    บันทึกลง pos_data
    """,
    tools=[wiki_tool, append_state]
)

critic = Agent(
    name="critic",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY),
    instruction="""
    บทบาท: The Critic

    วิเคราะห์หัวข้อ: "{topic}"

    ค้นหาด้านลบโดยใช้คำค้น:
    - "{topic} controversy"
    - "{topic} criticism"
    - "{topic} historical debate"

    สรุปเป็น bullet ภาษาไทย
    บันทึกลง neg_data
    """,
    tools=[wiki_tool, append_state]
)

investigation_team = ParallelAgent(
    name="investigation_team",
    sub_agents=[admirer, critic]
)


# ==========================================================
# STEP 3 – TRIAL & REVIEW (Loop)
# ==========================================================

judge = Agent(
    name="judge",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY),
    instruction="""
    ตรวจสอบข้อมูล:

    pos_data = {pos_data?}
    neg_data = {neg_data?}

    เงื่อนไข:
    1. แต่ละฝั่ง ≥ 2 รายการ
    2. ความยาวรวมต่างกันไม่เกิน 2 เท่า

    หากไม่ครบ:
        ให้ดำเนินการค้นหาเพิ่ม (loop ต่อ)

    หากครบ:
        ต้องเรียก exit_loop เท่านั้น
    """,
    tools=[exit_loop]
)

trial_session = LoopAgent(
    name="trial_session",
    sub_agents=[investigation_team, judge],
    max_iterations=6
)


# ==========================================================
# STEP 4 – VERDICT
# ==========================================================

clerk = Agent(
    name="clerk",
    model=Gemini(model=MODEL_NAME, retry_options=RETRY),
    instruction="""
    เขียนรายงานศาลจำลองแบบเป็นทางการ

    โครงสร้าง:
    1. บทนำ
    2. หลักฐานฝ่ายสนับสนุน
    3. หลักฐานฝ่ายค้าน
    4. วิเคราะห์เปรียบเทียบ
    5. คำตัดสินเป็นกลาง

    ใช้ข้อมูล:
    - {pos_data?}
    - {neg_data?}

    สำนวนเชิงวิชาการ
    ห้ามเอนเอียง
    แล้วเรียก write_report
    """,
    tools=[write_report]
)


# ==========================================================
# SYSTEM ASSEMBLY
# ==========================================================

historical_court_system = SequentialAgent(
    name="historical_court_system",
    sub_agents=[
        inquiry_agent,
        trial_session,
        clerk
    ]
)

# ADK Web Entry
root_agent = historical_court_system
