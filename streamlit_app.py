import streamlit as st
import re
import urllib.parse
from typing import List, Optional, Dict
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Mitra — HR Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

HANDBOOK    = "handbook_text.txt"
HR_EMAIL    = "payroll2.branch@orchids.edu.in"

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .sidebar-logo {
        font-size: 22px; font-weight: 700;
        color: #38bdf8 !important;
        letter-spacing: -0.5px;
        padding: 8px 0 4px 0;
    }
    [data-testid="stSidebar"] .sidebar-tagline {
        font-size: 11px; color: #64748b !important;
        margin-bottom: 20px;
    }
    [data-testid="stSidebar"] .nav-section {
        font-size: 10px; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.2px;
        color: #475569 !important; margin: 16px 0 8px 0;
    }
    [data-testid="stSidebar"] .contact-card {
        background: #1e3a5f; border: 1px solid #2563eb33;
        border-radius: 10px; padding: 12px 14px; margin-top: 12px;
    }
    [data-testid="stSidebar"] .contact-card p {
        font-size: 12px; margin: 2px 0; color: #93c5fd !important;
    }
    [data-testid="stSidebar"] .contact-card strong {
        color: #bfdbfe !important;
    }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        border-radius: 14px; padding: 24px 28px; margin-bottom: 24px;
        border: 1px solid #1e40af33;
    }
    .page-header h1 { color: #f0f9ff; margin: 0; font-size: 26px; font-weight: 700; }
    .page-header p  { color: #94a3b8; margin: 6px 0 0 0; font-size: 14px; }

    /* ── Step card ── */
    .step-card {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;
    }

    /* ── WhatsApp-style chat bubbles ── */
    .msg-bot  { display:flex; align-items:flex-start; gap:10px; margin:10px 0; }
    .msg-bot .avatar {
        width:36px; height:36px; border-radius:50%;
        background: linear-gradient(135deg,#1d4ed8,#3b82f6);
        display:flex; align-items:center; justify-content:center;
        font-size:17px; flex-shrink:0; margin-top:2px;
        box-shadow: 0 2px 8px rgba(59,130,246,0.3);
    }
    .msg-bot .bubble {
        background:#ffffff; border:1px solid #e2e8f0;
        border-radius:4px 16px 16px 16px;
        padding:12px 16px; max-width:82%;
        font-size:14px; line-height:1.65; color:#1e293b;
        box-shadow:0 1px 4px rgba(0,0,0,0.07);
    }
    .msg-user { display:flex; justify-content:flex-end; margin:10px 0; }
    .msg-user .bubble {
        background: linear-gradient(135deg,#1d4ed8,#2563eb);
        color:white; border-radius:16px 4px 16px 16px;
        padding:10px 16px; max-width:70%;
        font-size:14px; line-height:1.65;
        box-shadow:0 2px 8px rgba(37,99,235,0.25);
    }

    /* ── Email draft box ── */
    .draft-box {
        background:#f0f7ff; border:1.5px dashed #2563eb;
        border-radius:12px; padding:16px 20px; margin:12px 0;
        font-size:13px; color:#1e293b; white-space:pre-wrap;
        font-family:'Plus Jakarta Sans',sans-serif;
        line-height:1.7;
    }
    .draft-label {
        font-size:10px; font-weight:700; color:#2563eb;
        text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;
    }

    /* ── Closed banner ── */
    .closed-banner {
        background:#f0fdf4; border:1px solid #bbf7d0;
        border-radius:12px; padding:16px 22px;
        text-align:center; color:#166534;
        font-weight:700; font-size:15px; margin-top:16px;
    }

    /* ── Buttons ── */
    div[data-testid="stButton"] button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
    }

    /* ── Inputs ── */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #cbd5e1 !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }

    /* ── Success / Warning / Error boxes ── */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        font-size: 14px !important;
    }

    /* ── Divider ── */
    hr { border-color: #e2e8f0 !important; }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 14px 18px;
    }

    /* Target all Streamlit buttons */
.stButton > button {
    background-color: #ef4444;   /* light red */
    color: #ffffff;              /* white text */
    border-radius: 8px;
    height: 45px;
    width: 100%;
    border: none;
    transition: all 0.3s ease;
}

/* Hover effect */
.stButton > button:hover {
    background-color: #dc2626;   /* darker red */
    color: #ffffff;
    transform: scale(1.03);
}

/* Active (clicked) effect */
.stButton > button:active {
    background-color: #b91c1c;   /* deep red */
    transform: scale(0.98);
}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SHIFT DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
SHIFTS: Dict[str, dict] = {
    "09:00 - 17:30  (8.50 hrs)":      {"in":"09:00","out":"17:30","total":8.50,"part_time":False,"seven_day":False},
    "09:00 - 16:30  (7.50 hrs)":      {"in":"09:00","out":"16:30","total":7.50,"part_time":False,"seven_day":False},
    "09:00 - 15:45  (6.75 hrs)":      {"in":"09:00","out":"15:45","total":6.75,"part_time":False,"seven_day":False},
    "08:00 - 17:00  (9.00 hrs)":      {"in":"08:00","out":"17:00","total":9.00,"part_time":False,"seven_day":False},
    "08:15 - 17:00  (8.75 hrs)":      {"in":"08:15","out":"17:00","total":8.75,"part_time":False,"seven_day":False},
    "08:15 - 16:45  (8.50 hrs)":      {"in":"08:15","out":"16:45","total":8.50,"part_time":False,"seven_day":False},
    "08:15 - 16:30  (8.25 hrs)":      {"in":"08:15","out":"16:30","total":8.25,"part_time":False,"seven_day":False},
    "08:15 - 16:15  (8.00 hrs)":      {"in":"08:15","out":"16:15","total":8.00,"part_time":False,"seven_day":False},
    "08:15 - 14:30  (6.25 hrs)":      {"in":"08:15","out":"14:30","total":6.25,"part_time":False,"seven_day":False},
    "08:15 - 14:15  (6.00 hrs)":      {"in":"08:15","out":"14:15","total":6.00,"part_time":False,"seven_day":False},
    "08:30 - 15:30  (7.00 hrs)":      {"in":"08:30","out":"15:30","total":7.00,"part_time":False,"seven_day":False},
    "07:30 - 16:00  (8.50 hrs)":      {"in":"07:30","out":"16:00","total":8.50,"part_time":False,"seven_day":False},
    "07:40 - 15:40  (8.00 hrs)":      {"in":"07:40","out":"15:40","total":8.00,"part_time":False,"seven_day":False},
    "7D | 09:30 - 18:00  (8.50 hrs)": {"in":"09:30","out":"18:00","total":8.50,"part_time":False,"seven_day":True},
    "7D | 09:00 - 17:30  (8.50 hrs)": {"in":"09:00","out":"17:30","total":8.50,"part_time":False,"seven_day":True},
    "PT | 09:00 - 16:30  (7.50 hrs)": {"in":"09:00","out":"16:30","total":7.50,"part_time":True, "seven_day":False},
    "PT | 08:15 - 15:00  (6.75 hrs)": {"in":"08:15","out":"15:00","total":6.75,"part_time":True, "seven_day":False},
    "PT | 08:00 - 14:45  (6.75 hrs)": {"in":"08:00","out":"14:45","total":6.75,"part_time":True, "seven_day":False},
}
PUNCH_IN_BUFFER_MIN = 15


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — Attendance
# ══════════════════════════════════════════════════════════════════════════════
def get_shift_info(label): return SHIFTS.get(label, {})

def validate_time_format(t):
    try: datetime.strptime(t.strip(), "%H:%M"); return True
    except ValueError: return False

def calculate_working_hours(pi, po):
    try:
        return (datetime.strptime(po.strip(),"%H:%M") -
                datetime.strptime(pi.strip(),"%H:%M")).total_seconds()/3600
    except: return None

def is_late_punch_in(sched, actual):
    try:
        diff = (datetime.strptime(actual,"%H:%M") -
                datetime.strptime(sched, "%H:%M")).total_seconds()/60
        return diff > PUNCH_IN_BUFFER_MIN
    except: return False

def evaluate_attendance(hours, si):
    total = si.get("total",8.5); half = total/2
    pt    = si.get("part_time",False)
    lbl   = "Part-time half-day" if pt else "Half-day"
    if   hours >= total: return {"status":"FULL","color":"success",
        "message":f"✅ Full working day ({hours:.2f} / {total:.2f} hrs) — Valid attendance!"}
    elif hours >= half:  return {"status":"HALF","color":"warning",
        "message":f"⚠️ {lbl} ({hours:.2f} hrs worked, threshold {half:.2f} hrs). Apply regularization if needed."}
    else:                return {"status":"SHORT","color":"error",
        "message":f"❌ Insufficient hours ({hours:.2f} hrs, minimum {half:.2f} hrs). Please contact HR."}


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — Handbook
# ══════════════════════════════════════════════════════════════════════════════
def load_handbook_sections(path):
    sections = []
    pat = re.compile(r"^Section\s*\d+\s*(.+)$", re.IGNORECASE)
    try:
        with open(path,"r",encoding="utf-8") as f:
            for line in f:
                if pat.match(line.strip()): sections.append(line.strip())
    except FileNotFoundError: pass
    return sections

def get_section_detail(path, header):
    try:
        with open(path,"r",encoding="utf-8") as f: text = f.read()
        pat = re.compile(rf"(?ims)^{re.escape(header)}\s*(.*?)(?=^Section\s*\d+\s|\Z)")
        m = pat.search(text)
        return m.group(1).strip() if m else ""
    except FileNotFoundError: return ""

def summarize_section_text(text, max_lines=7):
    if not text: return []
    cleaned = re.sub(r"\s+"," ",text)
    sents   = re.split(r"(?<=[.!?])\s+",cleaned)
    out = []
    for s in sents:
        s = s.strip()
        if not s or len(s)<15 or s.lower().startswith("section"): continue
        if s.isupper() and len(s)<50: continue
        if s not in out: out.append(s)
        if len(out)>=max_lines: break
    return out

def is_within_two_months(d):
    today = datetime.now().date()
    return today - timedelta(days=60) <= d <= today

def reset_to_issue_select():
    for k in ["shift","punch_in","punch_out","leave_concern","leave_date",
              "lapsed_type","salary_concern","working_days","lop_days",
              "salary_component","salary_description"]:
        st.session_state.pop(k,None)
    st.session_state.selected_issue = None
    st.session_state.chat_state     = "select_issue"

def go_back(state):
    st.session_state.chat_state = state
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# FAQ DATA — HR Helpdesk chatbot
# ══════════════════════════════════════════════════════════════════════════════
FAQ = {
    "💰 Salary & Payslip": {
        "Salary not credited": {
            "explanation": (
                "Your salary is usually credited between the **1st–5th** of every month. "
                "Delays can happen due to bank processing, public holidays, or payroll cut-off issues.\n\n"
                "**What you should do:**\n"
                "- Check your bank statement for the exact date.\n"
                "- Confirm your bank account details are updated in HR records.\n"
                "- If it's past the 5th, raise it with payroll immediately."
            ),
            "subject": "Salary Not Credited – {month} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI am writing to bring to your attention that my salary "
                     "for the month of {month} has not been credited to my bank account as of today, {date}.\n\n"
                     "My details:\n- Name: {name}\n- Employee ID: {emp_id}\n- Department: {department}\n"
                     "- Bank Account No: {bank_account}\n\nKindly look into this at the earliest.\n\nThank you,\n{name}"),
        },
        "Wrong salary amount credited": {
            "explanation": (
                "A salary discrepancy can occur due to incorrect LOP calculation, wrong grade, or a missed revision.\n\n"
                "**What to check first:**\n"
                "- Download your payslip and compare Gross vs Net Pay.\n"
                "- Check if any LOP days were applied.\n- Verify if any increment was pending."
            ),
            "subject": "Salary Discrepancy – {month} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI noticed a discrepancy in my salary credited for {month}. "
                     "The amount received does not match my expected salary.\n\nMy Details:\n"
                     "- Name: {name}\n- Employee ID: {emp_id}\n- Department: {department}\n"
                     "- Expected Amount: ₹___________\n- Amount Received: ₹___________\n\n"
                     "Kindly review and revert at the earliest.\n\nThank you,\n{name}"),
        },
        "Payslip not received": {
            "explanation": (
                "Payslips are usually shared via email or the HR portal by the **5th of every month**.\n\n"
                "**Steps to try first:**\n"
                "- Check your registered email inbox and spam folder.\n"
                "- Log in to the HR portal if available.\n"
                "- If still not received, raise a request to payroll."
            ),
            "subject": "Payslip Not Received – {month} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI have not received my payslip for {month} as of {date}.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- Department: {department}\n"
                     "- Registered Email: ___________\n\nRequest you to share the payslip at the earliest.\n\n"
                     "Thank you,\n{name}"),
        },
        "LOP (Loss of Pay) dispute": {
            "explanation": (
                "LOP is applied when your leave balance is zero and you take additional leaves.\n\n"
                "**What to verify:**\n"
                "- Check your leave balance in the attendance system.\n"
                "- Confirm if your leave application was approved.\n"
                "- If LOP was applied incorrectly, share attendance records with HR."
            ),
            "subject": "LOP Deduction Dispute – {month} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI would like to raise a dispute regarding the LOP deduction "
                     "applied in my salary for {month}.\n\nMy Details:\n- Name: {name}\n- Employee ID: {emp_id}\n"
                     "- Department: {department}\n- LOP Days Deducted: ___________\n"
                     "- Reason for Dispute: ___________\n\nKindly review and revert.\n\nThank you,\n{name}"),
        },
        "Wrong deduction in payslip": {
            "explanation": (
                "Incorrect deductions can happen due to wrong PF amounts, double deduction, or incorrect tax.\n\n"
                "**Check:**\n- Compare payslip deductions with last month.\n"
                "- Verify PF is 12% of Basic.\n- Check Prof Tax is ₹200 (Karnataka)."
            ),
            "subject": "Incorrect Deduction in Payslip – {month} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI have noticed an incorrect deduction in my payslip for {month}.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- Department: {department}\n"
                     "- Deduction in Question: ___________\n- Amount Deducted: ₹___________\n"
                     "- Expected Amount: ₹___________\n\nKindly review and clarify.\n\nThank you,\n{name}"),
        },
    },
    "📅 Leave & Attendance": {
        "Leave not approved": {
            "explanation": (
                "Leave approval depends on your reporting manager and HR policy.\n\n"
                "**Steps:**\n- Check if leave was submitted correctly.\n"
                "- Follow up with your reporting manager first.\n"
                "- If manager approved but HR portal didn't update, contact HR."
            ),
            "subject": "Leave Approval Pending – {name} ({emp_id})",
            "body": ("Dear HR Team,\n\nI had applied for leave from [Start Date] to [End Date] "
                     "but the same has not been approved yet.\n\nMy Details:\n- Name: {name}\n"
                     "- Employee ID: {emp_id}\n- Department: {department}\n- Leave Type: ___________\n"
                     "- Leave Dates: ___________\n\nKindly process or advise on next steps.\n\nThank you,\n{name}"),
        },
        "Attendance mismatch": {
            "explanation": (
                "Attendance mismatches happen when biometric punches are missed or system errors occur.\n\n"
                "**What to do:**\n- Check your attendance record in the portal.\n"
                "- Identify specific dates with mismatch.\n"
                "- Submit a regularization request with proof."
            ),
            "subject": "Attendance Regularization Request – {name} ({emp_id})",
            "body": ("Dear HR / Attendance Team,\n\nI am writing to request regularization of my attendance "
                     "for the following dates due to a mismatch in records.\n\nMy Details:\n- Name: {name}\n"
                     "- Employee ID: {emp_id}\n- Department: {department}\n- Dates with Mismatch: ___________\n"
                     "- Reason: ___________\n\nKindly update the records.\n\nThank you,\n{name}"),
        },
        "Leave balance incorrect": {
            "explanation": (
                "Leave balances are updated at the start of the year or on your joining anniversary.\n\n"
                "**What to check:**\n- Verify your leave policy (EL, CL, SL).\n"
                "- Check if previous leaves were deducted correctly.\n"
                "- Confirm if carry-forward leaves were added."
            ),
            "subject": "Leave Balance Discrepancy – {name} ({emp_id})",
            "body": ("Dear HR Team,\n\nI noticed a discrepancy in my leave balance in the HR portal.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- Department: {department}\n"
                     "- Leave Type: ___________\n- Balance Shown: ___ days\n- Expected Balance: ___ days\n\n"
                     "Kindly review and correct.\n\nThank you,\n{name}"),
        },
        "Half day / WFH not updated": {
            "explanation": (
                "Half-day or WFH entries sometimes don't reflect if approval was not recorded.\n\n"
                "**Steps:**\n- Check if manager approved the WFH/half-day.\n"
                "- Verify entry exists in attendance system.\n"
                "- If missing, request manual update with approval proof."
            ),
            "subject": "WFH / Half Day Not Updated – {name} ({emp_id})",
            "body": ("Dear HR / Attendance Team,\n\nMy WFH / Half Day for [Date(s)] has not been updated "
                     "despite approval from my reporting manager.\n\nMy Details:\n- Name: {name}\n"
                     "- Employee ID: {emp_id}\n- Department: {department}\n- Date(s): ___________\n"
                     "- Type: [ ] WFH  [ ] Half Day\n\nKindly update the records.\n\nThank you,\n{name}"),
        },
    },
    "🏦 PF / ESI / Tax": {
        "PF not reflecting in EPFO": {
            "explanation": (
                "PF contributions take **45–60 days** to reflect on the EPFO portal.\n\n"
                "**What to check:**\n- Log in to epfindia.gov.in with your UAN.\n"
                "- Check if UAN is activated and linked to Aadhaar.\n"
                "- If older contributions are missing, raise with HR."
            ),
            "subject": "PF Contribution Not Reflecting – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nMy PF contributions are not reflecting on the EPFO portal.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- UAN Number: ___________\n"
                     "- Missing Months: ___________\n\nKindly verify and help resolve.\n\nThank you,\n{name}"),
        },
        "Wrong TDS deducted": {
            "explanation": (
                "TDS is calculated based on projected annual income and declared investments.\n\n"
                "**Common reasons for high TDS:**\n- Investment declarations not submitted.\n"
                "- HRA exemption not claimed (no rent receipts).\n"
                "- Previous employer TDS not considered.\n\n"
                "**Action:** Submit investment proof / Form 12B to HR immediately."
            ),
            "subject": "Incorrect TDS Deduction – {month} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI believe the TDS deducted in my salary for {month} is incorrect.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- Department: {department}\n"
                     "- TDS Deducted: ₹___________\n- Expected TDS: ₹___________\n- Reason: ___________\n\n"
                     "Kindly review and adjust TDS for upcoming months.\n\nThank you,\n{name}"),
        },
        "PF withdrawal help": {
            "explanation": (
                "You can withdraw PF after **2 months of unemployment** or partially during employment.\n\n"
                "**Steps:**\n1. Activate UAN on epfindia.gov.in.\n2. Link Aadhaar, PAN, and bank account.\n"
                "3. Submit Form 19 (full) or Form 31 (partial) online.\n"
                "4. HR needs to approve your KYC first."
            ),
            "subject": "PF Withdrawal Assistance – {name} ({emp_id})",
            "body": ("Dear HR Team,\n\nI would like to initiate a PF withdrawal and need assistance.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- UAN Number: ___________\n"
                     "- Withdrawal Type: [ ] Full  [ ] Partial\n- Reason (if partial): ___________\n\n"
                     "Kindly guide me or approve my KYC on the EPFO portal.\n\nThank you,\n{name}"),
        },
        "Form 16 not received": {
            "explanation": (
                "Form 16 is issued by your employer after the financial year ends (April–June).\n\n"
                "**What to know:**\n- Part A: TDS deposited by company.\n"
                "- Part B: Full salary breakup.\n- Mandatory for filing your ITR."
            ),
            "subject": "Form 16 Not Received – FY {year} – {name} ({emp_id})",
            "body": ("Dear HR / Payroll Team,\n\nI have not received my Form 16 for FY {year}.\n\n"
                     "My Details:\n- Name: {name}\n- Employee ID: {emp_id}\n- PAN: ___________\n"
                     "- Registered Email: ___________\n\nKindly share at the earliest for ITR filing.\n\n"
                     "Thank you,\n{name}"),
        },
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# HR HELPDESK — session helpers
# ══════════════════════════════════════════════════════════════════════════════
def _hd_init():
    defaults = {
        "hd_messages":  [], "hd_stage": "greeting",
        "hd_category":  None, "hd_issue": None,
        "hd_user_info": {}, "hd_info_step": 0,
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def _bot(text, buttons=None):
    st.session_state.hd_messages.append({"role":"bot","text":text,"buttons":buttons or []})

def _user(text):
    st.session_state.hd_messages.append({"role":"user","text":text})

def _hd_reset():
    for k in [k for k in st.session_state if k.startswith("hd_")]:
        del st.session_state[k]

def _show_categories():
    st.session_state.hd_stage = "category"
    _bot("Thank you! 😊 Please select the **category** of your issue:",
         buttons=list(FAQ.keys()) + ["✏️ Describe my own issue"])

def _hd_start():
    _bot("👋 Hi! I'm **Mitra**, your HR Helpdesk Assistant.\n\n"
         "I'll help you understand your issue and draft a ready-to-send email for HR.\n\n"
         "First, what is your **full name?**")
    st.session_state.hd_stage    = "collect_info"
    st.session_state.hd_info_step = 0

def _handle_collect_info(val):
    step = st.session_state.hd_info_step
    info = st.session_state.hd_user_info
    if step == 0:
        info["name"] = val; _user(val)
        _bot("Got it! What is your **Employee ID?**")
        st.session_state.hd_info_step = 1
    elif step == 1:
        info["emp_id"] = val; _user(val)
        _bot("Perfect. Which **Department** do you belong to?")
        st.session_state.hd_info_step = 2
    elif step == 2:
        info["department"] = val; _user(val)
        _show_categories()

def _handle_category(cat):
    _user(cat)
    if cat == "✏️ Describe my own issue":
        st.session_state.hd_stage = "custom_input"
        _bot("No problem! Please **type your issue** below and I'll draft an email for you. 👇")
    else:
        st.session_state.hd_category = cat
        st.session_state.hd_stage    = "sub_issue"
        _bot(f"You selected **{cat}**.\n\nPlease choose your specific issue:",
             buttons=list(FAQ[cat].keys()) + ["⬅️ Back to categories"])

def _handle_sub_issue(issue):
    if issue == "⬅️ Back to categories":
        _user(issue); _show_categories(); return
    _user(issue)
    cat  = st.session_state.hd_category
    data = FAQ[cat][issue]
    st.session_state.hd_issue = issue
    st.session_state.hd_stage = "resolution"
    _bot(f"**ℹ️ About: {issue}**\n\n{data['explanation']}")
    info  = st.session_state.hd_user_info
    today = datetime.now().strftime("%d %B %Y")
    month = datetime.now().strftime("%B %Y")
    fy    = f"{datetime.now().year-1}–{str(datetime.now().year)[2:]}"
    subj  = data["subject"].format(name=info.get("name","[Name]"),emp_id=info.get("emp_id","[EMP ID]"),
                                   department=info.get("department","[Dept]"),month=month,date=today,year=fy)
    body  = data["body"].format(name=info.get("name","[Name]"),emp_id=info.get("emp_id","[EMP ID]"),
                                department=info.get("department","[Dept]"),bank_account="[Bank Acc No]",
                                month=month,date=today,year=fy)
    st.session_state["hd_draft_subject"] = subj
    st.session_state["hd_draft_body"]    = body
    _bot(f"📧 **Your draft email is ready below.**\n\nFill in the blanks and send to **{HR_EMAIL}**",
         buttons=["✅ Issue resolved","❓ Need more clarity","🔄 I have another issue","❌ Close chat"])

def _handle_custom_input(text):
    _user(f'"{text}"')
    info  = st.session_state.hd_user_info
    today = datetime.now().strftime("%d %B %Y")
    subj  = f"HR Helpdesk Query – {info.get('name','[Name]')} ({info.get('emp_id','[EMP ID]')})"
    body  = (f"Dear HR / Payroll Team,\n\nI am writing to bring the following issue to your attention:\n\n"
             f"\"{text}\"\n\nMy Details:\n- Name: {info.get('name','[Name]')}\n"
             f"- Employee ID: {info.get('emp_id','[EMP ID]')}\n"
             f"- Department: {info.get('department','[Dept]')}\n- Date: {today}\n\n"
             f"Kindly look into this and revert at the earliest.\n\nThank you,\n{info.get('name','[Name]')}")
    st.session_state["hd_draft_subject"] = subj
    st.session_state["hd_draft_body"]    = body
    st.session_state.hd_stage            = "resolution"
    _bot(f"📧 **Your draft email is ready below.**\n\nSend it to **{HR_EMAIL}**",
         buttons=["✅ Issue resolved","❓ Need more clarity","🔄 I have another issue","❌ Close chat"])

def _handle_resolution(choice):
    _user(choice)
    if choice == "✅ Issue resolved":
        st.session_state.hd_stage = "closed"
        _bot("🎉 Great! Glad your issue is resolved.\n\nConversation is now **closed**. Come back anytime! 👋")
    elif choice == "❓ Need more clarity":
        cat = st.session_state.hd_category; issue = st.session_state.hd_issue
        if cat and issue:
            _bot(f"Sure! Here's more detail on **{issue}**:\n\n{FAQ[cat][issue]['explanation']}\n\n"
                 "If this still doesn't help, send the drafted email to HR — they'll give the most accurate answer.",
                 buttons=["✅ Issue resolved","🔄 I have another issue","❌ Close chat"])
        else:
            _bot("For custom issues, the best step is to send the drafted email and await HR's response.",
                 buttons=["✅ Issue resolved","🔄 I have another issue","❌ Close chat"])
    elif choice == "🔄 I have another issue":
        st.session_state.hd_stage = "category"
        st.session_state.hd_category = None; st.session_state.hd_issue = None
        st.session_state.pop("hd_draft_subject",None); st.session_state.pop("hd_draft_body",None)
        _show_categories()
    elif choice == "❌ Close chat":
        st.session_state.hd_stage = "closed"
        _bot("Thank you for using Mitra HR Helpdesk. 😊\n\nConversation **closed**. Come back anytime! 👋")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — HR HELPDESK CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
def hr_helpdesk_page():
    _hd_init()
    st.markdown("""
    <div class="page-header">
        <h1>💬 HR Helpdesk</h1>
        <p>Select your issue · Get explained · Draft & send email to HR</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("🔄 New Chat", use_container_width=True):
            _hd_reset(); st.rerun()

    if not st.session_state.hd_messages:
        _hd_start()

    # Render chat history
    for msg in st.session_state.hd_messages:
        if msg["role"] == "bot":
            st.markdown(f"""
            <div class="msg-bot">
                <div class="avatar">🤖</div>
                <div class="bubble">{msg['text'].replace(chr(10),'<br>')}</div>
            </div>""", unsafe_allow_html=True)

            if "draft email is ready" in msg["text"] and "hd_draft_subject" in st.session_state:
                subj = st.session_state.hd_draft_subject
                body = st.session_state.hd_draft_body
                st.markdown(f"""
                <div class="draft-box">
                    <div class="draft-label">📧 To: {HR_EMAIL}</div>
                    <div class="draft-label">Subject: {subj}</div>
                    <br>{body}
                </div>""", unsafe_allow_html=True)
                mailto = (f"mailto:{HR_EMAIL}?subject={urllib.parse.quote(subj)}"
                          f"&body={urllib.parse.quote(body)}")
                st.markdown(f'<a href="{mailto}" target="_blank"><button style="'
                    'background:#1d4ed8;color:white;border:none;padding:9px 22px;'
                    'border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;margin:6px 0;'
                    'box-shadow:0 2px 8px rgba(29,78,216,0.3);">📨 Open in Mail App</button></a>',
                    unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-user">
                <div class="bubble">{msg['text']}</div>
            </div>""", unsafe_allow_html=True)

    if st.session_state.hd_stage == "closed":
        st.markdown('<div class="closed-banner">✅ Conversation Closed · Thank you for using Mitra HR Helpdesk</div>',
                    unsafe_allow_html=True)
        return

    st.markdown("<br>", unsafe_allow_html=True)
    last_bot = next((m for m in reversed(st.session_state.hd_messages) if m["role"]=="bot"), None)
    stage    = st.session_state.hd_stage

    if last_bot and last_bot["buttons"]:
        st.markdown("**Choose an option:**")
        btns = last_bot["buttons"]
        cols = st.columns(min(len(btns), 3))
        for i, btn in enumerate(btns):
            with cols[i % min(len(btns),3)]:
                if st.button(btn, key=f"hd_{stage}_{i}_{btn}", use_container_width=True):
                    if   stage == "category":   _handle_category(btn)
                    elif stage == "sub_issue":  _handle_sub_issue(btn)
                    elif stage == "resolution": _handle_resolution(btn)
                    st.rerun()

    elif stage == "collect_info":
        with st.form("hd_info_form", clear_on_submit=True):
            val = st.text_input("Your response:", placeholder="Type here…")
            if st.form_submit_button("Send ➤") and val.strip():
                _handle_collect_info(val.strip()); st.rerun()

    elif stage == "custom_input":
        with st.form("hd_custom_form", clear_on_submit=True):
            val = st.text_area("Describe your issue:", placeholder="Type your issue here…", height=110)
            if st.form_submit_button("Send ➤") and val.strip():
                _handle_custom_input(val.strip()); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — HR CHATBOT (existing attendance / leave / salary flow)
# ══════════════════════════════════════════════════════════════════════════════
def hr_chatbot_page():
    st.markdown("""
    <div class="page-header">
        <h1>🤖 HR Assistant</h1>
        <p>Attendance validation · Leave eligibility · Salary discrepancy mail draft</p>
    </div>""", unsafe_allow_html=True)

    if "chat_state"     not in st.session_state: st.session_state.chat_state     = "get_erp"
    if "employee_erp"   not in st.session_state: st.session_state.employee_erp   = ""
    if "selected_issue" not in st.session_state: st.session_state.selected_issue = None

    # ── ERP ──────────────────────────────────────────────────────────────────
    if st.session_state.chat_state == "get_erp":
        with st.container():
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("**Step 1 of 3** — Verify Your Identity")
            erp = st.text_input("Enter your ERP / Employee Code:", placeholder="e.g., 20262002367_OIS", key="erp_input")
            if st.button("➡️ Continue", key="btn_erp_next", use_container_width=True):
                if erp.strip():
                    st.session_state.employee_erp = erp.strip()
                    st.session_state.chat_state   = "select_issue"
                    st.rerun()
                else:
                    st.error("❌ Please enter your ERP / Employee Code")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Issue Select ──────────────────────────────────────────────────────────
    elif st.session_state.chat_state == "select_issue":
        st.success(f"✓ Logged in as ERP: **{st.session_state.employee_erp}**")
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info("**Step 2 of 3** — Select Your Issue Type")
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("🕐 Attendance Issue", key="btn_attendance", use_container_width=True):
                st.session_state.selected_issue = "Attendance"
                st.session_state.chat_state     = "attendance_shift"; st.rerun()
        with c2:
            if st.button("🏖️ Leave Issue", key="btn_leave", use_container_width=True):
                st.session_state.selected_issue = "Leave"
                st.session_state.chat_state     = "leave_type"; st.rerun()
        with c3:
            if st.button("💰 Salary Issue", key="btn_salary", use_container_width=True):
                st.session_state.selected_issue = "Salary"
                st.session_state.chat_state     = "salary_type"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════ ATTENDANCE ════════════════════════════════════════════════════
    elif st.session_state.selected_issue == "Attendance":
        st.success(f"✓ ERP: **{st.session_state.employee_erp}** · Issue: **Attendance**")
        st.divider()

        if st.session_state.chat_state == "attendance_shift":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("**Step 3** — Select Your Shift")
            stype = st.radio("Shift category:", ["Regular","7-Day","Part-Time"],
                             key="shift_type_radio", horizontal=True)
            if stype == "Regular":  opts = [k for k,v in SHIFTS.items() if not v["part_time"] and not v["seven_day"]]
            elif stype == "7-Day":  opts = [k for k,v in SHIFTS.items() if v["seven_day"]]
            else:                   opts = [k for k,v in SHIFTS.items() if v["part_time"]]
            sel = st.selectbox("Select your shift:", opts, key="shift_select")
            si  = get_shift_info(sel)
            if si:
                lbl = "📋 Part-Time" if si["part_time"] else "🗓️ 7-Day" if si["seven_day"] else "👔 Regular"
                st.info(f"{lbl}  |  🕐 **{si['in']} → {si['out']}**  |  Total: **{si['total']:.2f} hrs**  |  Half-day: **{si['total']/2:.2f} hrs**")
            if st.button("➡️ Next", key="btn_shift", use_container_width=True):
                st.session_state.shift = sel; st.session_state.chat_state = "attendance_punch_in"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "attendance_punch_in":
            si = get_shift_info(st.session_state.shift)
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info(f"**Step 4** — Punch-In Time  |  Scheduled: **{si.get('in','?')}**")
            pi = st.text_input("Actual punch-in (HH:MM):", placeholder=si.get("in","08:15"), key="punch_in_input")
            st.caption(f"Up to **{PUNCH_IN_BUFFER_MIN} min** late allowed.")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_pi_back", use_container_width=True): go_back("attendance_shift")
            with cn:
                if st.button("➡️ Next", key="btn_punch_in", use_container_width=True):
                    if not pi.strip(): st.error("❌ Enter punch-in time")
                    elif not validate_time_format(pi): st.error("❌ Use HH:MM format")
                    else:
                        if is_late_punch_in(si.get("in","08:00"), pi.strip()):
                            st.warning(f"⚠️ Punch-in {pi.strip()} is late. This may be flagged.")
                        st.session_state.punch_in = pi.strip(); st.session_state.chat_state = "attendance_punch_out"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "attendance_punch_out":
            si = get_shift_info(st.session_state.shift)
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info(f"**Step 5** — Punch-Out Time  |  Scheduled: **{si.get('out','?')}**")
            po = st.text_input("Actual punch-out (HH:MM):", placeholder=si.get("out","17:00"), key="punch_out_input")
            st.caption(f"Full day ≥ **{si.get('total',8.5):.2f} hrs**  |  Half-day ≥ **{si.get('total',8.5)/2:.2f} hrs**")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_po_back", use_container_width=True): go_back("attendance_punch_in")
            with cn:
                if st.button("✅ Analyse Attendance", key="btn_validate", use_container_width=True):
                    if not po.strip(): st.error("❌ Enter punch-out time")
                    elif not validate_time_format(po): st.error("❌ Use HH:MM format")
                    else:
                        st.session_state.punch_out = po.strip(); st.session_state.chat_state = "attendance_result"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "attendance_result":
            si    = get_shift_info(st.session_state.shift)
            hours = calculate_working_hours(st.session_state.punch_in, st.session_state.punch_out)
            st.subheader("✓ Attendance Analysis")
            if hours is None:
                st.error("❌ Could not parse times. Please re-enter.")
                if st.button("← Re-enter", use_container_width=True): go_back("attendance_punch_in")
            elif hours < 0:
                st.error(f"❌ Punch-out is earlier than punch-in. Please correct.")
                if st.button("← Re-enter", use_container_width=True): go_back("attendance_punch_in")
            else:
                total = si.get("total",8.5); half = total/2
                res   = evaluate_attendance(hours, si)
                ca,cb = st.columns(2)
                with ca:
                    st.markdown(f"- **Shift:** {st.session_state.shift}")
                    st.markdown(f"- **Scheduled:** {si.get('in','?')} → {si.get('out','?')}")
                    st.markdown(f"- **Punch In:** {st.session_state.punch_in}")
                    st.markdown(f"- **Punch Out:** {st.session_state.punch_out}")
                with cb:
                    st.markdown(f"- **Hours Worked:** {hours:.2f} hrs")
                    st.markdown(f"- **Full Day:** ≥ {total:.2f} hrs")
                    st.markdown(f"- **Half Day:** ≥ {half:.2f} hrs")
                    st.markdown(f"- **Type:** {'Part-Time' if si.get('part_time') else '7-Day' if si.get('seven_day') else 'Regular'}")
                if   res["color"]=="success": st.success(res["message"])
                elif res["color"]=="warning": st.warning(res["message"])
                else:                         st.error(res["message"])
                if is_late_punch_in(si.get("in","08:00"), st.session_state.punch_in):
                    st.warning(f"⚠️ Late punch-in: {st.session_state.punch_in} vs {si.get('in','?')} (buffer {PUNCH_IN_BUFFER_MIN} min)")
            st.divider()
            cb2,cn2 = st.columns(2)
            with cb2:
                if st.button("← Back", key="btn_res_back", use_container_width=True): go_back("attendance_punch_out")
            with cn2:
                if st.button("🔄 New Session", key="btn_restart_att", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

    # ══════════ LEAVE ═════════════════════════════════════════════════════════
    elif st.session_state.selected_issue == "Leave":
        st.success(f"✓ ERP: **{st.session_state.employee_erp}** · Issue: **Leave**")
        st.divider()

        if st.session_state.chat_state == "leave_type":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("**Step 3** — What is your leave concern?")
            concern = st.selectbox("Select:", ["-- Select --","Leaves were not credited","Leaves lapsed","Missed to apply leave"], key="leave_concern_select")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_leave_back", use_container_width=True): go_back("select_issue")
            with cn:
                if st.button("➡️ Continue", key="btn_leave_continue", use_container_width=True):
                    if concern == "-- Select --": st.error("❌ Please select a leave issue")
                    else:
                        st.session_state.leave_concern = concern
                        st.session_state.chat_state = ("leave_missed" if concern=="Missed to apply leave"
                                                       else "leave_lapsed" if concern=="Leaves lapsed"
                                                       else "leave_not_credited")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "leave_not_credited":
            st.info("📋 **Leaves Were Not Credited**")
            st.markdown("""
**Leave Cycle:** 26th May to 25th May (next year)

**CL Credit Schedule:**
- 6 days credited in **June** | 5 days in **December**
- Maximum **3 CL** allowed per month

**Why leave may not have been credited:**
- Joined after credit date — pro-rata basis applies
- Leave balance exhausted — day marked as LOP
- ERP/system delay — check Eduvate after 2–3 working days

**Contact:** payroll2.branch@orchids.edu.in
            """)
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_nc_back", use_container_width=True): go_back("leave_type")
            with cn:
                if st.button("🔄 New Session", key="btn_restart_nc", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "leave_missed":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("📅 **Missed to Apply Leave** — Select the date:")
            ld = st.date_input("Leave date:", value=datetime.now().date(), key="leave_date_widget")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_missed_back", use_container_width=True): go_back("leave_type")
            with cn:
                if st.button("✅ Check Eligibility", key="btn_check_arrears", use_container_width=True):
                    st.session_state.leave_date = ld; st.session_state.chat_state = "leave_missed_result"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "leave_missed_result":
            ld = st.session_state.leave_date
            st.subheader("📋 Eligibility Result")
            if is_within_two_months(ld):
                st.success("✅ **Eligible for Arrears Application**")
                st.markdown(f"Date **{ld.strftime('%d-%b-%Y')}** is within the 2-month window.\n\n"
                            "Log in to **Eduvate** → Leave → Apply for Arrears.\n\n**Contact:** payroll2.branch@orchids.edu.in")
            else:
                st.error("❌ **Not Eligible — Beyond 2-Month Window**")
                st.markdown(f"Date **{ld.strftime('%d-%b-%Y')}** is outside the policy window.\n\n"
                            "Email HR explaining your situation for case-by-case review.\n\n**Contact:** payroll2.branch@orchids.edu.in")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_mr_back", use_container_width=True): go_back("leave_missed")
            with cn:
                if st.button("🔄 New Session", key="btn_restart_missed", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "leave_lapsed":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("📋 **Leaves Lapsed** — Which leave type?")
            lapsed = st.selectbox("Select:", ["-- Select --","Casual Leave (CL)","Compensatory Off (CO)","Weekly Off (WO)"], key="lapsed_type_select")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_lapsed_back", use_container_width=True): go_back("leave_type")
            with cn:
                if st.button("➡️ Continue", key="btn_lapsed_continue", use_container_width=True):
                    if lapsed == "-- Select --": st.error("❌ Please select a leave type")
                    else:
                        st.session_state.lapsed_type = lapsed; st.session_state.chat_state = "leave_lapsed_result"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "leave_lapsed_result":
            lapsed = st.session_state.lapsed_type
            st.subheader(f"📋 Leave Lapsed — {lapsed}")
            if lapsed == "Casual Leave (CL)":
                st.warning("⚠️ CL does **not carry forward**. Unused balance lapses at end of cycle (25th May).")
                st.markdown("Contact HR with your leave statement. **Contact:** payroll2.branch@orchids.edu.in")
            elif lapsed == "Compensatory Off (CO)":
                st.info("🗓️ CO must be availed within **90 days** of grant date. Lapses automatically after 90 days.")
                st.markdown("Contact HR with the grant date if lapsed before 90 days. **Contact:** payroll2.branch@orchids.edu.in")
            elif lapsed == "Weekly Off (WO)":
                st.info("📅 WO lapses after **1 week (5 working days)**. Cannot be carried beyond same week.")
                st.markdown("Contact HR with attendance statement if incorrectly lapsed. **Contact:** payroll2.branch@orchids.edu.in")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_lr_back", use_container_width=True): go_back("leave_lapsed")
            with cn:
                if st.button("🔄 New Session", key="btn_restart_lapsed", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

    # ══════════ SALARY ════════════════════════════════════════════════════════
    elif st.session_state.selected_issue == "Salary":
        st.success(f"✓ ERP: **{st.session_state.employee_erp}** · Issue: **Salary**")
        st.divider()

        if st.session_state.chat_state == "salary_type":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("**Step 3** — What is your salary concern?")
            concern = st.radio("Select:", ["Salary not received","Salary discrepancy","Salary components question"], key="salary_concern_radio")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_sal_back", use_container_width=True): go_back("select_issue")
            with cn:
                if st.button("➡️ Continue", key="btn_salary_continue", use_container_width=True):
                    st.session_state.salary_concern = concern
                    st.session_state.chat_state = ("salary_not_received" if concern=="Salary not received"
                                                   else "salary_discrepancy_days" if concern=="Salary discrepancy"
                                                   else "salary_components")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "salary_not_received":
            st.warning("💳 **Salary Not Received**")
            st.markdown("1. Check your bank account for recent credit.\n2. Wait 2–3 working days after processing date.\n3. Contact HR if still missing after 3 days.\n\n**Email:** payroll2.branch@orchids.edu.in")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_nr_back", use_container_width=True): go_back("salary_type")
            with cn:
                if st.button("🔄 New Session", key="btn_restart_nr", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "salary_discrepancy_days":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info("**Step 4** — Working Days in Payslip")
            wd = st.number_input("Working days shown in payslip:", min_value=0, max_value=31, step=1, key="working_days_input")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_wd_back", use_container_width=True): go_back("salary_type")
            with cn:
                if st.button("➡️ Next", key="btn_days_next", use_container_width=True):
                    st.session_state.working_days = int(wd); st.session_state.chat_state = "salary_discrepancy_lop"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "salary_discrepancy_lop":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info(f"**Step 5** — LOP Days  |  Working days: **{st.session_state.working_days}**")
            lop = st.number_input("LOP days in payslip:", min_value=0, max_value=31, step=1, key="lop_days_input")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_lop_back", use_container_width=True): go_back("salary_discrepancy_days")
            with cn:
                if st.button("➡️ Next", key="btn_lop_next", use_container_width=True):
                    st.session_state.lop_days = int(lop); st.session_state.chat_state = "salary_discrepancy_component"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "salary_discrepancy_component":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info(f"**Step 6** — Discrepancy Component  |  WD: {st.session_state.working_days} | LOP: {st.session_state.lop_days}")
            comp = st.text_input("Salary component (e.g. Basic, HRA, PF…):", placeholder="e.g., HRA", key="salary_component_input")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_comp_back", use_container_width=True): go_back("salary_discrepancy_lop")
            with cn:
                if st.button("➡️ Next", key="btn_component_next", use_container_width=True):
                    if comp.strip(): st.session_state.salary_component = comp.strip(); st.session_state.chat_state = "salary_discrepancy_description"; st.rerun()
                    else: st.error("❌ Please enter the component")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "salary_discrepancy_description":
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.info(f"**Step 7** — Describe Issue  |  Component: **{st.session_state.salary_component}**")
            desc = st.text_area("Describe the discrepancy:", placeholder="e.g., My HRA should be ₹8,000 but ₹6,000 was credited.", height=120, key="salary_description_input")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_desc_back", use_container_width=True): go_back("salary_discrepancy_component")
            with cn:
                if st.button("✅ Generate Mail Draft", key="btn_generate_mail", use_container_width=True):
                    if desc.strip(): st.session_state.salary_description = desc.strip(); st.session_state.chat_state = "salary_mail_draft"; st.rerun()
                    else: st.error("❌ Please describe your issue")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.chat_state == "salary_mail_draft":
            st.subheader("📧 Mail Draft — Ready to Send")
            erp  = st.session_state.get("employee_erp","[ERP]")
            wd   = st.session_state.get("working_days","N/A")
            lop  = st.session_state.get("lop_days","N/A")
            comp = st.session_state.get("salary_component","[Component]")
            desc = st.session_state.get("salary_description","[Description]")
            mo   = datetime.now().strftime("%B %Y")
            draft = (f"Subject: Salary Discrepancy — {comp} — {mo} — ERP: {erp}\n\n"
                     f"To,\nThe HR / Payroll Team,\n\nDear HR Team,\n\n"
                     f"I am writing regarding a discrepancy in my salary for {mo}.\n\n"
                     f"Employee Details:\n  • ERP Code       : {erp}\n  • Month          : {mo}\n"
                     f"  • Working Days   : {wd} days\n  • LOP Days       : {lop} days\n"
                     f"  • Component      : {comp}\n\nIssue:\n{desc}\n\n"
                     f"Kindly review and clarify or rectify at the earliest.\n\n"
                     f"Thank you,\n[Your Full Name]\nERP: {erp}\n[Department / Branch]\n[Contact Number]")
            st.code(draft, language="")
            st.caption(f"📋 Copy, fill in your details, and send to **{HR_EMAIL}**")
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_mail_back", use_container_width=True): go_back("salary_discrepancy_description")
            with cn:
                if st.button("🔄 New Session", key="btn_restart_mail", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "salary_components":
            st.info("📊 **Salary Components Reference Guide**")
            st.markdown("""
**Earnings:** Basic · HRA · DA · Other Allowances · Arrears

**Deductions:** PF (12% of Basic) · Income Tax · ESI (gross ≤ ₹21,000) · Insurance · Loan Recovery · LOP

Refer to your offer letter or contact **payroll2.branch@orchids.edu.in**
            """)
            cb,cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_comp_ref_back", use_container_width=True): go_back("salary_type")
            with cn:
                if st.button("🔄 New Session", key="btn_restart_comp", use_container_width=True):
                    reset_to_issue_select(); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — HANDBOOK BROWSER
# ══════════════════════════════════════════════════════════════════════════════
def handbook_browser_page():
    st.markdown("""
    <div class="page-header">
        <h1>📖 HR Handbook Browser</h1>
        <p>Browse and view all handbook sections in one place</p>
    </div>""", unsafe_allow_html=True)

    sections = load_handbook_sections(HANDBOOK)
    if not sections:
        st.warning("⚠️ Handbook file not found or has no sections. Please upload `handbook_text.txt`.")
        return

    col1,col2 = st.columns([1,2])
    with col1:
        st.subheader("📚 Sections")
        selected = st.selectbox("Choose a section:", sections, key="handbook_select", label_visibility="collapsed")
    with col2:
        st.subheader("📄 Content")
        if st.button("View Section", key="view_handbook", use_container_width=True):
            detail = get_section_detail(HANDBOOK, selected)
            if detail:
                clean   = detail.replace("\\r\\n","\n").replace("\\n","\n")
                bullets = summarize_section_text(clean)
                st.markdown("**Summary:**")
                for b in bullets: st.markdown(f"• {b}")
                if not bullets: st.markdown("_No summary available._")
                with st.expander("View Full Section"): st.markdown(clean)
            else:
                st.warning("No content found for this section.")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    if "page" not in st.session_state:
        st.session_state.page = "HR Helpdesk"

    with st.sidebar:
        st.markdown('<div class="sidebar-logo"> Mitra</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">HR Assistant Platform · Orchids</div>', unsafe_allow_html=True)

        st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)

        if st.button("HR Helpdesk", use_container_width=True):
            st.session_state.page = "HR Helpdesk"
    
        if st.button("HR Assistant", use_container_width=True):
            st.session_state.page = "HR Assistant"
    
        if st.button("Handbook Browser", use_container_width=True):
            st.session_state.page = "Handbook Browser"
        
        st.markdown("---")
    
        st.markdown('<div class="nav-section">Quick Contact</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="contact-card">
            <p><strong>Payroll & Leave Issues</strong></p>
            <p>📧 payroll2.branch@orchids.edu.in</p>
            <br>
            <p><strong>Eduvate ERP Portal</strong></p>
            <p>🌐 Attendance · Leave · Payslips</p>
        </div>""", unsafe_allow_html=True)
    
        st.markdown("---")
        st.markdown(
            '<p style="font-size:11px;color:#475569;text-align:center;">Mitra v2.0 · Built for Orchids HR</p>',
            unsafe_allow_html=True
        )
    
    return st.session_state.page


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    inject_css()
    page = render_sidebar()

    if   page == "HR Helpdesk":      hr_helpdesk_page()
    elif page == "HR Assistant":     hr_chatbot_page()
    elif page == "Handbook Browser": handbook_browser_page()

if __name__ == "__main__":
    main()
