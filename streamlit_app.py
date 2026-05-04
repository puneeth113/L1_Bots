import streamlit as st
import re
import urllib.parse
from typing import List, Optional, Dict
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Mitra — HR Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

HR_EMAIL = "payroll2.branch@orchids.edu.in"
HANDBOOK = "handbook_text.txt"

# ══════════════════════════════════════════════════════════════════════════════
# POLICY CONSTANTS  (sourced directly from handbook)
# ══════════════════════════════════════════════════════════════════════════════
POLICY = {
    "leave_cycle_start":        "26th May",
    "leave_cycle_end":          "25th May (next year)",
    "cl_per_cycle":             11,
    "cl_june":                  6,
    "cl_december":              5,
    "cl_max_per_month":         3,
    "payroll_cycle":            "26th of current month to 25th of next month",
    "salary_release_by":        "10th of the following month",
    "punch_buffer_min":         15,
    "regularizations_per_month":2,
    "pf_threshold_basic":       15000,
    "probation_admin_marketing":12,   # months
    "probation_teaching":       6,    # months
    "salary_advance_after":     6,    # months of service
    "co_validity_days":         90,
    "wo_validity_days":         5,
    "arrears_window_days":      60,
}


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#0f172a 0%,#1e293b 100%) !important;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .sidebar-logo {
        font-size:22px; font-weight:700; color:#38bdf8 !important;
        letter-spacing:-0.5px; padding:8px 0 4px 0;
    }
    [data-testid="stSidebar"] .sidebar-tagline {
        font-size:11px; color:#64748b !important; margin-bottom:20px;
    }
    [data-testid="stSidebar"] .nav-section {
        font-size:10px; font-weight:700; text-transform:uppercase;
        letter-spacing:1.2px; color:#475569 !important; margin:16px 0 8px 0;
    }
    [data-testid="stSidebar"] .contact-card {
        background:#1e3a5f; border:1px solid #2563eb33;
        border-radius:10px; padding:12px 14px; margin-top:12px;
    }
    [data-testid="stSidebar"] .contact-card p { font-size:12px; margin:3px 0; color:#93c5fd !important; }
    [data-testid="stSidebar"] .contact-card strong { color:#bfdbfe !important; }

    /* Page header */
    .page-header {
        background: linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
        border-radius:14px; padding:22px 28px; margin-bottom:24px;
        border:1px solid #1e40af33;
    }
    .page-header h1 { color:#f0f9ff; margin:0; font-size:24px; font-weight:700; }
    .page-header p  { color:#94a3b8; margin:6px 0 0 0; font-size:13px; }

    /* Tool cards — clickable hyperlinks on helpdesk */
    .tool-card {
        background:#f8fafc; border:1.5px solid #e2e8f0;
        border-radius:14px; padding:22px 24px; text-align:center;
        transition:all 0.2s ease; cursor:pointer;
    }
    .tool-card:hover { border-color:#3b82f6; box-shadow:0 4px 16px rgba(59,130,246,0.15); transform:translateY(-2px); }
    .tool-card .tool-icon { font-size:36px; margin-bottom:10px; }
    .tool-card .tool-title { font-size:16px; font-weight:700; color:#0f172a; margin-bottom:6px; }
    .tool-card .tool-desc  { font-size:12px; color:#64748b; line-height:1.5; }

    /* Step card */
    .step-card {
        background:#f8fafc; border:1px solid #e2e8f0;
        border-radius:12px; padding:18px 20px; margin-bottom:14px;
    }

    /* WhatsApp bubbles */
    .msg-bot  { display:flex; align-items:flex-start; gap:10px; margin:10px 0; }
    .msg-bot .avatar {
        width:36px; height:36px; border-radius:50%;
        background:linear-gradient(135deg,#1d4ed8,#3b82f6);
        display:flex; align-items:center; justify-content:center;
        font-size:17px; flex-shrink:0; margin-top:2px;
        box-shadow:0 2px 8px rgba(59,130,246,0.3);
    }
    .msg-bot .bubble {
        background:#ffffff; border:1px solid #e2e8f0;
        border-radius:4px 16px 16px 16px;
        padding:12px 16px; max-width:82%;
        font-size:14px; line-height:1.7; color:#1e293b;
        box-shadow:0 1px 4px rgba(0,0,0,0.07);
    }
    .msg-user { display:flex; justify-content:flex-end; margin:10px 0; }
    .msg-user .bubble {
        background:linear-gradient(135deg,#1d4ed8,#2563eb);
        color:white; border-radius:16px 4px 16px 16px;
        padding:10px 16px; max-width:70%;
        font-size:14px; line-height:1.7;
        box-shadow:0 2px 8px rgba(37,99,235,0.25);
    }

    /* Draft box */
    .draft-box {
        background:#f0f7ff; border:1.5px dashed #2563eb;
        border-radius:12px; padding:16px 20px; margin:12px 0;
        font-size:13px; color:#1e293b; white-space:pre-wrap;
        font-family:'Plus Jakarta Sans',sans-serif; line-height:1.8;
    }
    .draft-label {
        font-size:10px; font-weight:700; color:#2563eb;
        text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;
    }

    /* Closed banner */
    .closed-banner {
        background:#f0fdf4; border:1px solid #bbf7d0;
        border-radius:12px; padding:16px 22px;
        text-align:center; color:#166534;
        font-weight:700; font-size:15px; margin-top:16px;
    }

    /* Policy badge */
    .policy-badge {
        background:#eff6ff; border:1px solid #bfdbfe;
        border-radius:8px; padding:8px 14px;
        font-size:12px; color:#1d4ed8; font-weight:500;
        display:inline-block; margin:6px 0;
    }

    /* Buttons */
    div[data-testid="stButton"] button {
        border-radius:10px !important; font-weight:500 !important;
        font-size:13px !important; transition:all 0.15s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        transform:translateY(-1px) !important;
        box-shadow:0 4px 12px rgba(0,0,0,0.12) !important;
    }

    /* Inputs */
    div[data-testid="stTextInput"] input {
        border-radius:10px !important; border:1.5px solid #cbd5e1 !important;
        padding:10px 14px !important; font-size:14px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color:#3b82f6 !important;
        box-shadow:0 0 0 3px rgba(59,130,246,0.15) !important;
    }
    hr { border-color:#e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ERP VALIDATOR  — 11 digits + _OIS
# ══════════════════════════════════════════════════════════════════════════════
def validate_erp(erp: str) -> tuple[bool, str]:
    erp = erp.strip()
    if not re.fullmatch(r"\d{11}_OIS", erp):
        return False, ("❌ Invalid ERP format. It must be **11 digits followed by _OIS**.\n"
                       "Example: `20262002367_OIS`")
    return True, ""


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


# ══════════════════════════════════════════════════════════════════════════════
# ATTENDANCE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def get_shift_info(label): return SHIFTS.get(label, {})

def validate_time_fmt(t):
    try: datetime.strptime(t.strip(),"%H:%M"); return True
    except: return False

def calc_hours(pi, po):
    try: return (datetime.strptime(po.strip(),"%H:%M") - datetime.strptime(pi.strip(),"%H:%M")).total_seconds()/3600
    except: return None

def is_late(sched, actual):
    try:
        diff = (datetime.strptime(actual,"%H:%M") - datetime.strptime(sched,"%H:%M")).total_seconds()/60
        return diff > POLICY["punch_buffer_min"]
    except: return False

def eval_attendance(hours, si):
    total = si.get("total",8.5); half = total/2; pt = si.get("part_time",False)
    lbl = "Part-time half-day" if pt else "Half-day"
    if   hours >= total: return {"color":"success","message":f"✅ Full working day ({hours:.2f}/{total:.2f} hrs) — Valid attendance."}
    elif hours >= half:  return {"color":"warning","message":f"⚠️ {lbl} ({hours:.2f} hrs worked, threshold {half:.2f} hrs). Apply regularization if a punch was missed."}
    else:                return {"color":"error",  "message":f"❌ Insufficient hours ({hours:.2f} hrs, minimum {half:.2f} hrs for half-day). Please contact HR."}

def is_within_arrears_window(d):
    today = datetime.now().date()
    return today - timedelta(days=POLICY["arrears_window_days"]) <= d <= today

def reset_att():
    for k in ["att_shift","att_pi","att_po"]: st.session_state.pop(k,None)
    st.session_state.att_state = "shift"

def go_back_att(s): st.session_state.att_state = s; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# FAQ DATA — policy-verified against handbook
# ══════════════════════════════════════════════════════════════════════════════
FAQ = {
    "💰 Salary & Payslip": {
        "Salary not credited": {
            "policy_note": f"Salaries are released on or before the 10th of the following month (Policy: Section 8).",
            "explanation": (
                "As per policy, salaries are released **on or before the 10th** of every month.\n\n"
                "**What you should do:**\n"
                "- Check your bank account — credit may take 2–3 working days after processing.\n"
                "- Verify your bank account details are updated correctly in HR records.\n"
                "- If it is past the 10th and not credited, raise it with payroll immediately.\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Salary Not Credited – {month} – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI am writing to bring to your attention that my salary "
                     "for the month of {month} has not been credited to my bank account as of today, {date}.\n\n"
                     "My details:\n- Name: {name}\n- ERP Code: {erp}\n- Bank Account No: {bank_account}\n\n"
                     "As per policy, salaries are released on or before the 10th. "
                     "Kindly look into this at the earliest and confirm the expected credit date.\n\nThank you,\n{name}"),
        },
        "Wrong salary amount credited": {
            "policy_note": "If an employee joins after 22nd, they are added to next month's payroll with arrears (Section 8).",
            "explanation": (
                "A salary discrepancy can occur due to:\n"
                "- Incorrect LOP calculation\n- Joining after the 22nd (moved to next cycle with arrears)\n"
                "- Wrong payroll grade or a missed revision\n\n"
                "**What to check first:**\n"
                "- Download your payslip and compare Gross vs Net Pay.\n"
                "- Check if LOP days were applied correctly.\n"
                "- If you joined after 22nd of the month, your first salary may include arrears adjustment.\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Salary Discrepancy – {month} – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI noticed a discrepancy in my salary credited for {month}.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Expected Amount: ₹___________\n- Amount Received: ₹___________\n\n"
                     "Kindly review and revert with a clarification or correction at the earliest.\n\nThank you,\n{name}"),
        },
        "Payslip not received": {
            "policy_note": "Payroll cycle: 26th current month to 25th next month. Salaries by 10th (Section 8).",
            "explanation": (
                "Payslips are usually shared via registered email or the HR portal after salary is processed.\n\n"
                "**Steps to try first:**\n"
                "- Check your registered email inbox including spam/junk folder.\n"
                "- Log in to the **Eduvate ERP portal** to access your payslip.\n"
                "- If still not received after the 10th, raise a request with payroll.\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Payslip Not Received – {month} – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI have not received my payslip for {month} as of {date}.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n- Registered Email: ___________\n\n"
                     "Request you to share the payslip or guide me on how to access it in Eduvate.\n\nThank you,\n{name}"),
        },
        "LOP (Loss of Pay) dispute": {
            "policy_note": "LOP is applied when leave balance is exhausted (Section 7). Payroll cycle is 26th–25th (Section 8).",
            "explanation": (
                "LOP is applied when your leave balance is zero and you take additional leaves or are absent.\n\n"
                "**What to verify:**\n"
                "- Check your leave balance in **Eduvate ERP** (attendance section).\n"
                "- Confirm if your leave application was submitted and approved.\n"
                "- Check if the Sandwich Policy was triggered — taking leave adjacent to a holiday causes those holiday days to also be counted as leave/LOP.\n"
                "- Check if Vacation Sandwich applies — taking leave the day before vacation starts or reopening day makes the entire vacation LOP.\n\n"
                "📌 *Policy Reference: Section 7 — Leave Policy | Section 8 — Salary*"
            ),
            "subject": "LOP Deduction Dispute – {month} – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI would like to raise a dispute regarding the LOP deduction "
                     "applied in my salary for {month}.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- LOP Days Deducted: ___________\n- Reason for Dispute: ___________\n\n"
                     "I will share the relevant attendance and leave records on request. "
                     "Kindly review and revert.\n\nThank you,\n{name}"),
        },
        "Salary advance request": {
            "policy_note": "Salary advance available after 6 months of service — up to 1 month gross, repayable in 3 installments (Section 8).",
            "explanation": (
                "As per policy, employees are eligible for a **Salary Advance** after completing **6 months of service**.\n\n"
                "**Advance Details:**\n"
                "- Maximum: Up to **1 month's gross salary**\n"
                "- Repayment: In **3 equal monthly installments** from salary\n"
                "- Eligibility: Must have completed 6 months of continuous service\n\n"
                "**Steps:**\n"
                "- Raise the request formally with HR via email.\n"
                "- Approval is subject to management discretion.\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Salary Advance Request – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI would like to formally request a Salary Advance as per company policy.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n- Date of Joining: ___________\n"
                     "- Months of Service Completed: ___________\n- Advance Amount Required: ₹___________\n\n"
                     "I understand this will be repaid in 3 equal monthly installments from my salary. "
                     "Kindly process this request at the earliest.\n\nThank you,\n{name}"),
        },
    },

    "📅 Leave & Attendance": {
        "Leave not credited": {
            "policy_note": "CL: 11 days/cycle. 6 credited in June, 5 in December. Max 3 CL per month. Pro-rata for new joiners (Section 7).",
            "explanation": (
                "As per the Leave Policy:\n\n"
                f"- **Leave Cycle:** {POLICY['leave_cycle_start']} to {POLICY['leave_cycle_end']}\n"
                f"- **Casual Leave (CL):** {POLICY['cl_per_cycle']} days per cycle\n"
                f"  — {POLICY['cl_june']} days credited in **June**, {POLICY['cl_december']} days in **December**\n"
                f"- **Maximum {POLICY['cl_max_per_month']} CL** allowed per month\n\n"
                "**Why leave may not have been credited:**\n"
                "- Joined after the credit date — credits are on a **pro-rata** basis\n"
                "- Leave balance exhausted — absent day may be marked as LOP\n"
                "- ERP/system delay — check **Eduvate** after 2–3 working days of the credit date\n\n"
                "📌 *Policy Reference: Section 7 — Leave Policy*"
            ),
            "subject": "Leave Not Credited – {erp}",
            "body": ("Dear HR Team,\n\nI would like to raise a concern that my Casual Leave balance has not been "
                     "credited as expected for the current leave cycle.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Expected Credit Month: ___________\n- Balance Currently Showing: ___ days\n\n"
                     "As per policy, CL is credited in June (6 days) and December (5 days). "
                     "Kindly verify and update my leave balance.\n\nThank you,\n{name}"),
        },
        "Leaves lapsed": {
            "policy_note": "CL does not carry forward. CO valid 90 days. WO valid 5 working days (Section 7).",
            "explanation": (
                "Leave lapse rules as per policy:\n\n"
                "- **Casual Leave (CL):** Does **not carry forward** — unused CL lapses at end of cycle (25th May)\n"
                f"- **Compensatory Off (CO):** Must be availed within **{POLICY['co_validity_days']} days** of grant date\n"
                f"- **Weekly Off (WO):** Must be availed within **{POLICY['wo_validity_days']} working days** (same week)\n\n"
                "Please select the specific leave type that lapsed for more details.\n\n"
                "📌 *Policy Reference: Section 7 — Leave Policy*"
            ),
            "subject": "Leave Lapsed Query – {erp}",
            "body": ("Dear HR Team,\n\nI noticed that my leave balance shows a lapse that I would like to query.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Leave Type That Lapsed: ___________\n- Grant Date (if CO/WO): ___________\n\n"
                     "Kindly review and revert with clarification.\n\nThank you,\n{name}"),
        },
        "Missed to apply leave": {
            "policy_note": "Arrears leave application allowed within 2 months via Eduvate (Section 7).",
            "explanation": (
                "If you forgot to apply for leave, you can apply for **Arrears Leave** via Eduvate ERP.\n\n"
                f"**Eligibility Window:** Within **{POLICY['arrears_window_days']} days (2 months)** of the leave date\n\n"
                "**Steps:**\n"
                "1. Log in to **Eduvate ERP** → Leave → Apply for Arrears\n"
                "2. Select the missed date and provide reason\n"
                "3. Submit for HR approval\n\n"
                "⚠️ Beyond 2 months, arrears application is not permitted by policy. "
                "You would need to email HR for a case-by-case review.\n\n"
                "📌 *Policy Reference: Section 7 — Leave Policy*"
            ),
            "subject": "Missed Leave Application – {erp}",
            "body": ("Dear HR Team,\n\nI missed applying for leave on the following date and would like to "
                     "request an arrears leave application.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Missed Leave Date: ___________\n- Reason: ___________\n\n"
                     "Kindly guide me on the next steps or approve the arrears application in Eduvate.\n\nThank you,\n{name}"),
        },
        "Sandwich policy / LOP on holiday": {
            "policy_note": "Sandwich and Vacation Sandwich policy applies per Section 7.",
            "explanation": (
                "The **Sandwich Policy** and **Vacation Sandwich Policy** are important to understand:\n\n"
                "**Sandwich Policy:**\n"
                "- If you take leave **both before and after** a public holiday or weekly off, "
                "those in-between holiday days are also counted as leaves.\n"
                "- Example: Holiday on Wednesday. You take leave Tuesday + Thursday → "
                "Wednesday holiday is also counted as leave.\n\n"
                "**Vacation Sandwich Policy:**\n"
                "- Taking leave on the **day before a vacation starts** OR on the **day of reopening** "
                "results in the **entire vacation period being treated as LOP**.\n"
                "- Example: Summer vacation starts Monday. Taking leave Friday before → "
                "entire summer vacation becomes LOP.\n\n"
                "📌 *Policy Reference: Section 7 — Leave Policy*"
            ),
            "subject": "Sandwich Policy LOP Dispute – {month} – {erp}",
            "body": ("Dear HR Team,\n\nI would like to raise a concern regarding LOP applied under the "
                     "Sandwich / Vacation Sandwich Policy for {month}.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Date(s) of Leave Taken: ___________\n- Holiday / Vacation Dates: ___________\n"
                     "- LOP Days Applied: ___________\n\n"
                     "Kindly review and revert.\n\nThank you,\n{name}"),
        },
        "Attendance regularization": {
            "policy_note": "Only 2 attendance regularizations allowed per month (Section 6).",
            "explanation": (
                "As per the Attendance Policy:\n\n"
                f"- Only **{POLICY['regularizations_per_month']} attendance regularizations** are allowed per month.\n"
                "- Regularization is for genuine cases where you forgot to punch or had a biometric issue.\n"
                "- You must check your attendance on **Eduvate** every 3–4 days to catch issues early.\n\n"
                "**Steps:**\n"
                "1. Log in to Eduvate → Attendance → Regularization Request\n"
                "2. Select the date and provide reason\n"
                "3. Submit for manager/HR approval\n\n"
                "⚠️ If you have already used both regularizations for the month, "
                "you will need to email HR directly with supporting proof.\n\n"
                "📌 *Policy Reference: Section 6 — Attendance Policy*"
            ),
            "subject": "Attendance Regularization Request – {erp}",
            "body": ("Dear HR / Attendance Team,\n\nI am requesting attendance regularization for the following date(s).\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Date(s) Requiring Regularization: ___________\n- Reason: ___________\n\n"
                     "I confirm this is within my 2 permitted regularizations for the month. "
                     "Kindly process the request.\n\nThank you,\n{name}"),
        },
    },

    "🏦 PF / ESI / Tax": {
        "PF not reflecting in EPFO": {
            "policy_note": "PF mandatory for employees with basic salary ≤ ₹15,000/month (Section 8).",
            "explanation": (
                "PF contributions typically take **45–60 days** to reflect on the EPFO portal after deduction.\n\n"
                "**Policy note:** PF is mandatory for employees with a Basic Salary of ₹15,000 or below per month.\n\n"
                "**What to check:**\n"
                "- Log in to **epfindia.gov.in** with your UAN number.\n"
                "- Ensure your UAN is activated and linked to Aadhaar.\n"
                "- Verify Aadhaar shows your full Date of Birth (mandatory as per Section 3 policy).\n"
                "- If contributions from older months are missing, raise with HR.\n\n"
                "📌 *Policy Reference: Section 8 — Salary | Section 3 — Recruitment (Aadhaar requirement)*"
            ),
            "subject": "PF Contribution Not Reflecting in EPFO – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nMy PF contributions are not reflecting on the EPFO portal.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- UAN Number: ___________\n- Missing Months: ___________\n\n"
                     "Kindly verify if contributions have been deposited and help resolve this.\n\nThank you,\n{name}"),
        },
        "Wrong TDS deducted": {
            "policy_note": "TDS based on projected annual income and declared investments (Section 8).",
            "explanation": (
                "TDS is calculated based on your **projected annual income** and **investment declarations**.\n\n"
                "**Common reasons for higher TDS:**\n"
                "- Investment declarations (LIC, PF, rent receipts) not submitted to HR\n"
                "- HRA exemption not claimed — rent receipts not provided\n"
                "- Previous employer TDS not considered\n\n"
                "**Immediate action:**\n"
                "- Submit your investment proof / Form 12B to HR\n"
                "- Submit rent receipts if you pay rent (for HRA exemption)\n"
                "- TDS will be adjusted in the upcoming months\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Incorrect TDS Deduction – {month} – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI believe the TDS deducted in my salary for {month} is incorrect.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- TDS Deducted: ₹___________\n- Expected TDS: ₹___________\n- Reason: ___________\n\n"
                     "I have attached / will share my investment declarations. "
                     "Kindly review and adjust TDS for upcoming months.\n\nThank you,\n{name}"),
        },
        "PF withdrawal help": {
            "policy_note": "PF withdrawal process via EPFO portal. KYC approval required from employer (Section 8).",
            "explanation": (
                "You can withdraw PF after **2 months of unemployment**, or partially during employment "
                "for specific reasons (medical, marriage, home loan).\n\n"
                "**Steps:**\n"
                "1. Activate UAN on **epfindia.gov.in**\n"
                "2. Link Aadhaar, PAN, and bank account (Aadhaar must show full Date of Birth)\n"
                "3. Ensure HR has approved your **KYC** on the EPFO employer portal\n"
                "4. Submit **Form 19** (full withdrawal) or **Form 31** (partial) online\n\n"
                "⚠️ HR must approve your KYC before withdrawal is possible.\n\n"
                "📌 *Policy Reference: Section 8 — Salary | Section 3 — Aadhaar requirement*"
            ),
            "subject": "PF Withdrawal Assistance Request – {erp}",
            "body": ("Dear HR Team,\n\nI would like to initiate a PF withdrawal and need assistance.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- UAN Number: ___________\n- Withdrawal Type: [ ] Full  [ ] Partial\n"
                     "- Reason (if partial): ___________\n\n"
                     "Kindly guide me through the process or approve my KYC on the EPFO portal.\n\nThank you,\n{name}"),
        },
        "Form 16 not received": {
            "policy_note": "Form 16 issued after financial year end (April–June). Required for ITR filing.",
            "explanation": (
                "Form 16 is issued by your employer after the **financial year ends (April–June)**.\n\n"
                "**What Form 16 contains:**\n"
                "- **Part A:** TDS deposited by company on your behalf\n"
                "- **Part B:** Full salary breakup for the year\n\n"
                "**Important:** Form 16 is mandatory for filing your **Income Tax Return (ITR)**.\n\n"
                "If not received by June-end, raise a request with HR immediately.\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Form 16 Not Received – FY {year} – {erp}",
            "body": ("Dear HR / Payroll Team,\n\nI have not received my Form 16 for Financial Year {year}.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- PAN: ___________\n- Registered Email: ___________\n\n"
                     "Kindly share Form 16 at the earliest as it is required for ITR filing.\n\nThank you,\n{name}"),
        },
    },

    "📋 Policy & General": {
        "Probation period query": {
            "policy_note": "Admin/Marketing: 12 months probation. Teaching/Deputy Leaders: 6 months. Extension possible up to 3 years (Section 5).",
            "explanation": (
                "As per the Probation Policy:\n\n"
                f"- **Admin & Marketing Staff:** {POLICY['probation_admin_marketing']} months probation\n"
                f"- **Teaching Staff & Deputy Leaders:** {POLICY['probation_teaching']} months probation\n"
                "- Organization reserves the right to **extend up to 3 years** based on performance\n"
                "- Employees are considered **confirmed** unless a written extension of probation is issued\n"
                "- **Leave rules are the same** for confirmed and non-confirmed staff\n\n"
                "📌 *Policy Reference: Section 5 — Probation and Confirmation*"
            ),
            "subject": "Probation Period Query – {erp}",
            "body": ("Dear HR Team,\n\nI have a query regarding my probation period and confirmation status.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n- Date of Joining: ___________\n"
                     "- Staff Category: ___________\n\n"
                     "Kindly clarify my current probation status and expected confirmation date.\n\nThank you,\n{name}"),
        },
        "Staff children fee concession": {
            "policy_note": "Fee concession available after completing probation (Section 8).",
            "explanation": (
                "As per policy, employees are eligible for **Staff Children Fee Concession** after "
                "completing their probation period.\n\n"
                "**Eligibility:**\n"
                "- Must have successfully completed the probation period\n"
                "- Concession applies for employee's own children\n\n"
                "**Action:** Contact HR with your child's admission details and confirmation letter "
                "to initiate the concession process.\n\n"
                "📌 *Policy Reference: Section 8 — Salary and Payroll*"
            ),
            "subject": "Staff Children Fee Concession Request – {erp}",
            "body": ("Dear HR Team,\n\nI would like to apply for the Staff Children Fee Concession "
                     "as per company policy.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Date of Joining: ___________\n- Probation Completion Date: ___________\n"
                     "- Child's Name: ___________\n- Child's Class / Campus: ___________\n\n"
                     "Kindly process this request at the earliest.\n\nThank you,\n{name}"),
        },
        "Reimbursement claim": {
            "policy_note": "All reimbursements need pre-approval. Claims without original bills not considered (Section 10).",
            "explanation": (
                "As per the Reimbursement Policy:\n\n"
                "- All travel and reimbursement requests must be **pre-approved** by your reporting manager and HOD\n"
                "- For air travel, you must choose the **lowest available airfare**\n"
                "- Food/daily expense reimbursements follow the **Entitlement Matrix** based on your cadre\n"
                "- Claims **without scanned copies of original bills** will NOT be considered\n"
                "- Local conveyance claims must use the specific **Local Conveyance Claim Form**\n\n"
                "📌 *Policy Reference: Section 10 — Reimbursement Policy*"
            ),
            "subject": "Reimbursement Claim – {erp}",
            "body": ("Dear HR Team,\n\nI would like to submit a reimbursement claim for the following expenses.\n\n"
                     "My Details:\n- Name: {name}\n- ERP Code: {erp}\n"
                     "- Expense Type: ___________\n- Amount: ₹___________\n"
                     "- Date of Expense: ___________\n- Pre-approved by: ___________\n\n"
                     "I have attached scanned copies of all original bills. "
                     "Kindly process the claim.\n\nThank you,\n{name}"),
        },
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPDESK SESSION HELPERS
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

def _usr(text):
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
         "I'll help you understand your issue based on Orchids HR Policy "
         "and draft a ready-to-send email to HR.\n\n"
         "What is your **full name?**")
    st.session_state.hd_stage    = "collect_info"
    st.session_state.hd_info_step = 0

def _handle_collect_info(val):
    step = st.session_state.hd_info_step
    info = st.session_state.hd_user_info
    if step == 0:
        info["name"] = val; _usr(val)
        _bot("Got it! Please enter your **ERP Code**.\n\n"
             "_(Format: 11 digits followed by `_OIS` — e.g. `20262002367_OIS`)_")
        st.session_state.hd_info_step = 1
    elif step == 1:
        ok, err = validate_erp(val)
        if not ok:
            _usr(val)
            _bot(f"{err}\n\nPlease re-enter your ERP Code:")
            return
        info["erp"] = val; _usr(val)
        _show_categories()

def _handle_category(cat):
    _usr(cat)
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
        _usr(issue); _show_categories(); return
    _usr(issue)
    cat  = st.session_state.hd_category
    data = FAQ[cat][issue]
    st.session_state.hd_issue = issue
    st.session_state.hd_stage = "resolution"
    _bot(f"**ℹ️ {issue}**\n\n{data['explanation']}")
    info  = st.session_state.hd_user_info
    today = datetime.now().strftime("%d %B %Y")
    month = datetime.now().strftime("%B %Y")
    fy    = f"{datetime.now().year-1}–{str(datetime.now().year)[2:]}"
    subj  = data["subject"].format(erp=info.get("erp","[ERP]"),month=month,year=fy)
    body  = data["body"].format(
        name=info.get("name","[Name]"), erp=info.get("erp","[ERP]"),
        bank_account="[Bank Account No]", month=month, date=today, year=fy
    )
    st.session_state["hd_draft_subject"] = subj
    st.session_state["hd_draft_body"]    = body
    _bot(f"📧 **Your draft email is ready below.**\n\nFill in the blanks `___________` and send to **{HR_EMAIL}**",
         buttons=["✅ Issue resolved","❓ Need more clarity","🔄 I have another issue","❌ Close chat"])

def _handle_custom_input(text):
    _usr(f'"{text}"')
    info  = st.session_state.hd_user_info
    today = datetime.now().strftime("%d %B %Y")
    subj  = f"HR Helpdesk Query – {info.get('erp','[ERP]')}"
    body  = (f"Dear HR / Payroll Team,\n\nI am writing to bring the following issue to your attention:\n\n"
             f"\"{text}\"\n\nMy Details:\n- Name: {info.get('name','[Name]')}\n"
             f"- ERP Code: {info.get('erp','[ERP]')}\n- Date: {today}\n\n"
             f"Kindly look into this and revert at the earliest.\n\nThank you,\n{info.get('name','[Name]')}")
    st.session_state["hd_draft_subject"] = subj
    st.session_state["hd_draft_body"]    = body
    st.session_state.hd_stage            = "resolution"
    _bot(f"📧 **Your draft email is ready below.**\n\nSend it to **{HR_EMAIL}**",
         buttons=["✅ Issue resolved","❓ Need more clarity","🔄 I have another issue","❌ Close chat"])

def _handle_resolution(choice):
    _usr(choice)
    if choice == "✅ Issue resolved":
        st.session_state.hd_stage = "closed"
        _bot("🎉 Great! Glad your issue is resolved.\n\n"
             "Do you have any other issue or need clarification on something?\n\n"
             "Your conversation is now **closed**. Come back anytime! 👋")
    elif choice == "❓ Need more clarity":
        cat = st.session_state.hd_category; issue = st.session_state.hd_issue
        if cat and issue:
            pnote = FAQ[cat][issue].get("policy_note","")
            _bot(f"Sure! Here's more detail on **{issue}**:\n\n"
                 f"{FAQ[cat][issue]['explanation']}\n\n"
                 f"📌 **Policy Note:** {pnote}\n\n"
                 "If this still doesn't resolve your issue, send the drafted email to HR — "
                 "they'll provide the most accurate answer for your specific case.",
                 buttons=["✅ Issue resolved","🔄 I have another issue","❌ Close chat"])
        else:
            _bot("For custom issues, the best next step is to send the drafted email and await HR's response.",
                 buttons=["✅ Issue resolved","🔄 I have another issue","❌ Close chat"])
    elif choice == "🔄 I have another issue":
        st.session_state.hd_stage    = "category"
        st.session_state.hd_category = None; st.session_state.hd_issue = None
        st.session_state.pop("hd_draft_subject",None); st.session_state.pop("hd_draft_body",None)
        _show_categories()
    elif choice == "❌ Close chat":
        st.session_state.hd_stage = "closed"
        _bot("Thank you for using Mitra HR Helpdesk. 😊\n\n"
             "Conversation **closed**. Come back anytime you need help! 👋")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — ATTENDANCE VERIFIER  (linked from Helpdesk)
# ══════════════════════════════════════════════════════════════════════════════
def attendance_verifier_page():
    st.markdown("""
    <div class="page-header">
        <h1>🕐 Attendance Verifier</h1>
        <p>Check if your punch-in / punch-out qualifies as full day, half day, or insufficient hours</p>
    </div>""", unsafe_allow_html=True)

    col_back, _ = st.columns([1,5])
    with col_back:
        if st.button("← Back to Helpdesk", key="att_back_btn"):
            st.session_state.current_page = "helpdesk"; st.rerun()

    # ERP gate
    if "att_erp_verified" not in st.session_state:
        st.session_state.att_erp_verified = False
    if "att_state" not in st.session_state:
        st.session_state.att_state = "erp"

    if not st.session_state.att_erp_verified:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info("**Step 1** — Enter your ERP Code to continue")
        erp = st.text_input("ERP Code:", placeholder="e.g. 20262002367_OIS", key="att_erp_input")
        if st.button("✅ Verify", key="att_erp_verify", use_container_width=True):
            ok, err = validate_erp(erp)
            if ok:
                st.session_state.att_erp       = erp.strip()
                st.session_state.att_erp_verified = True
                st.session_state.att_state     = "shift"
                st.rerun()
            else: st.error(err)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.success(f"✓ ERP: **{st.session_state.att_erp}**")
    st.divider()

    # Policy reminder
    st.markdown(f'<div class="policy-badge">📋 Attendance Policy: {POLICY["punch_buffer_min"]}-min buffer from shift start · '
                f'{POLICY["regularizations_per_month"]} regularizations/month · Check Eduvate every 3–4 days</div>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    state = st.session_state.att_state

    # Shift selection
    if state == "shift":
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info("**Step 2** — Select Your Shift")
        stype = st.radio("Shift category:", ["Regular","7-Day","Part-Time"], key="att_stype", horizontal=True)
        if stype == "Regular":  opts = [k for k,v in SHIFTS.items() if not v["part_time"] and not v["seven_day"]]
        elif stype == "7-Day":  opts = [k for k,v in SHIFTS.items() if v["seven_day"]]
        else:                   opts = [k for k,v in SHIFTS.items() if v["part_time"]]
        sel = st.selectbox("Select shift:", opts, key="att_shift_sel")
        si  = get_shift_info(sel)
        if si:
            lbl = "📋 Part-Time" if si["part_time"] else "🗓️ 7-Day" if si["seven_day"] else "👔 Regular"
            st.info(f"{lbl}  |  🕐 **{si['in']} → {si['out']}**  |  "
                    f"Total: **{si['total']:.2f} hrs**  |  Half-day threshold: **{si['total']/2:.2f} hrs**")
        if st.button("➡️ Next", key="att_shift_next", use_container_width=True):
            st.session_state.att_shift = sel; st.session_state.att_state = "punch_in"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "punch_in":
        si = get_shift_info(st.session_state.att_shift)
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info(f"**Step 3** — Punch-In Time  |  Scheduled: **{si.get('in','?')}**")
        pi = st.text_input("Actual punch-in (HH:MM):", placeholder=si.get("in","08:15"), key="att_pi_input")
        st.caption(f"Grace period: up to **{POLICY['punch_buffer_min']} min** after scheduled time.")
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="att_pi_back", use_container_width=True): go_back_att("shift")
        with cn:
            if st.button("➡️ Next", key="att_pi_next", use_container_width=True):
                if not pi.strip(): st.error("❌ Enter punch-in time")
                elif not validate_time_fmt(pi): st.error("❌ Use HH:MM format (e.g. 08:15)")
                else:
                    if is_late(si.get("in","08:00"), pi.strip()):
                        st.warning(f"⚠️ Punch-in {pi.strip()} is more than {POLICY['punch_buffer_min']} min after "
                                   f"scheduled {si.get('in','?')}. This may be flagged as half-day by the system.")
                    st.session_state.att_pi = pi.strip(); st.session_state.att_state = "punch_out"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "punch_out":
        si = get_shift_info(st.session_state.att_shift)
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info(f"**Step 4** — Punch-Out Time  |  Scheduled: **{si.get('out','?')}**")
        po = st.text_input("Actual punch-out (HH:MM):", placeholder=si.get("out","17:00"), key="att_po_input")
        st.caption(f"Full day ≥ **{si.get('total',8.5):.2f} hrs**  |  Half-day ≥ **{si.get('total',8.5)/2:.2f} hrs**")
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="att_po_back", use_container_width=True): go_back_att("punch_in")
        with cn:
            if st.button("✅ Analyse Attendance", key="att_analyse", use_container_width=True):
                if not po.strip(): st.error("❌ Enter punch-out time")
                elif not validate_time_fmt(po): st.error("❌ Use HH:MM format (e.g. 17:00)")
                else:
                    st.session_state.att_po = po.strip(); st.session_state.att_state = "result"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "result":
        si    = get_shift_info(st.session_state.att_shift)
        hours = calc_hours(st.session_state.att_pi, st.session_state.att_po)
        st.subheader("📊 Attendance Analysis Result")
        if hours is None:
            st.error("❌ Could not parse times. Please re-enter.")
            if st.button("← Re-enter", use_container_width=True): go_back_att("punch_in")
        elif hours < 0:
            st.error("❌ Punch-out is earlier than punch-in. Please correct.")
            if st.button("← Re-enter", use_container_width=True): go_back_att("punch_in")
        else:
            total = si.get("total",8.5); half = total/2
            res   = eval_attendance(hours, si)
            ca,cb = st.columns(2)
            with ca:
                st.markdown(f"- **Shift:** {st.session_state.att_shift}")
                st.markdown(f"- **Scheduled:** {si.get('in','?')} → {si.get('out','?')}")
                st.markdown(f"- **Punch In:** {st.session_state.att_pi}")
                st.markdown(f"- **Punch Out:** {st.session_state.att_po}")
            with cb:
                st.markdown(f"- **Hours Worked:** {hours:.2f} hrs")
                st.markdown(f"- **Full Day:** ≥ {total:.2f} hrs")
                st.markdown(f"- **Half Day:** ≥ {half:.2f} hrs")
                st.markdown(f"- **Type:** {'Part-Time' if si.get('part_time') else '7-Day' if si.get('seven_day') else 'Regular'}")
            if   res["color"]=="success": st.success(res["message"])
            elif res["color"]=="warning": st.warning(res["message"])
            else:                         st.error(res["message"])
            if is_late(si.get("in","08:00"), st.session_state.att_pi):
                st.warning(f"⚠️ Late punch-in: **{st.session_state.att_pi}** vs scheduled **{si.get('in','?')}** "
                           f"(grace: {POLICY['punch_buffer_min']} min). System may auto-mark as half-day.")
        st.divider()
        cb2,cn2 = st.columns(2)
        with cb2:
            if st.button("← Re-analyse", key="att_re", use_container_width=True): go_back_att("punch_in")
        with cn2:
            if st.button("🔄 New Check", key="att_new", use_container_width=True):
                reset_att(); st.session_state.att_erp_verified = False; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — MAIL DRAFTER  (linked from Helpdesk)
# ══════════════════════════════════════════════════════════════════════════════
def mail_drafter_page():
    st.markdown("""
    <div class="page-header">
        <h1>📧 Salary Discrepancy Mail Drafter</h1>
        <p>Step-by-step guided mail drafting for salary issues — ready to send to HR</p>
    </div>""", unsafe_allow_html=True)

    col_back, _ = st.columns([1,5])
    with col_back:
        if st.button("← Back to Helpdesk", key="mail_back_btn"):
            st.session_state.current_page = "helpdesk"; st.rerun()

    if "md_state" not in st.session_state: st.session_state.md_state = "erp"
    if "md_erp_verified" not in st.session_state: st.session_state.md_erp_verified = False

    # ERP gate
    if not st.session_state.md_erp_verified:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info("**Step 1** — Verify your ERP Code")
        erp = st.text_input("ERP Code:", placeholder="e.g. 20262002367_OIS", key="md_erp_input")
        if st.button("✅ Verify", key="md_erp_verify", use_container_width=True):
            ok, err = validate_erp(erp)
            if ok:
                st.session_state.md_erp = erp.strip(); st.session_state.md_erp_verified = True
                st.session_state.md_state = "name"; st.rerun()
            else: st.error(err)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.success(f"✓ ERP: **{st.session_state.md_erp}**")
    st.divider()

    state = st.session_state.md_state

    if state == "name":
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info("**Step 2** — Your Full Name")
        nm = st.text_input("Full Name:", placeholder="e.g. Puneeth Kumar", key="md_name_input")
        if st.button("➡️ Next", key="md_name_next", use_container_width=True):
            if nm.strip(): st.session_state.md_name = nm.strip(); st.session_state.md_state = "days"; st.rerun()
            else: st.error("❌ Please enter your name")
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "days":
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info(f"**Step 3** — Working Days in Payslip  |  Name: **{st.session_state.md_name}**")
        st.number_input("Working days shown in payslip:", min_value=0, max_value=31, step=1, key="md_wd")
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="md_days_back", use_container_width=True): st.session_state.md_state = "name"; st.rerun()
        with cn:
            if st.button("➡️ Next", key="md_days_next", use_container_width=True):
                st.session_state.md_state = "lop"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "lop":
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info(f"**Step 4** — LOP Days  |  Working days: **{st.session_state.md_wd}**")
        st.number_input("LOP (Loss of Pay) days:", min_value=0, max_value=31, step=1, key="md_lop")
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="md_lop_back", use_container_width=True): st.session_state.md_state = "days"; st.rerun()
        with cn:
            if st.button("➡️ Next", key="md_lop_next", use_container_width=True):
                st.session_state.md_state = "component"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "component":
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info(f"**Step 5** — Component  |  WD: {st.session_state.md_wd} | LOP: {st.session_state.md_lop}")
        comp = st.text_input("Which salary component has the discrepancy?", placeholder="e.g. HRA, Basic, PF…", key="md_comp_input")
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="md_comp_back", use_container_width=True): st.session_state.md_state = "lop"; st.rerun()
        with cn:
            if st.button("➡️ Next", key="md_comp_next", use_container_width=True):
                if comp.strip(): st.session_state.md_comp = comp.strip(); st.session_state.md_state = "desc"; st.rerun()
                else: st.error("❌ Please enter the component")
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "desc":
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.info(f"**Step 6** — Describe Issue  |  Component: **{st.session_state.md_comp}**")
        desc = st.text_area("Describe the discrepancy:", placeholder="e.g. My HRA should be ₹8,000 as per offer letter but ₹6,000 was credited.", height=110, key="md_desc_input")
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="md_desc_back", use_container_width=True): st.session_state.md_state = "component"; st.rerun()
        with cn:
            if st.button("✅ Generate Draft", key="md_generate", use_container_width=True):
                if desc.strip(): st.session_state.md_desc = desc.strip(); st.session_state.md_state = "draft"; st.rerun()
                else: st.error("❌ Please describe your issue")
        st.markdown('</div>', unsafe_allow_html=True)

    elif state == "draft":
        st.subheader("📧 Your Mail Draft — Ready to Send")
        erp  = st.session_state.md_erp
        nm   = st.session_state.md_name
        wd   = st.session_state.md_wd
        lop  = st.session_state.md_lop
        comp = st.session_state.md_comp
        desc = st.session_state.md_desc
        mo   = datetime.now().strftime("%B %Y")
        draft = (f"Subject: Salary Discrepancy — {comp} — {mo} — ERP: {erp}\n\n"
                 f"To,\nThe HR / Payroll Team,\nOrchids The International School\n\n"
                 f"Dear HR Team,\n\n"
                 f"I am writing regarding a discrepancy I have noticed in my salary for the month of {mo}.\n\n"
                 f"Employee Details:\n"
                 f"  • ERP Code        : {erp}\n"
                 f"  • Name            : {nm}\n"
                 f"  • Month           : {mo}\n"
                 f"  • Working Days    : {wd} days\n"
                 f"  • LOP Days        : {lop} days\n"
                 f"  • Component       : {comp}\n\n"
                 f"Issue Description:\n{desc}\n\n"
                 f"I request you to kindly review my payslip and salary records for the above month "
                 f"and clarify or rectify the discrepancy at the earliest.\n\n"
                 f"Thank you for your time.\n\n"
                 f"Warm regards,\n{nm}\nERP Code: {erp}\n[Department / Branch]\n[Contact Number]")
        st.code(draft, language="")
        st.caption(f"📋 Copy, fill in remaining details, and send to **{HR_EMAIL}**")
        mailto = (f"mailto:{HR_EMAIL}?subject={urllib.parse.quote(f'Salary Discrepancy – {comp} – {mo} – ERP: {erp}')}"
                  f"&body={urllib.parse.quote(draft)}")
        st.markdown(f'<a href="{mailto}" target="_blank"><button style="background:#1d4ed8;color:white;border:none;'
                    'padding:10px 24px;border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;margin:8px 0;'
                    'box-shadow:0 2px 8px rgba(29,78,216,0.3);">📨 Open in Mail App</button></a>',
                    unsafe_allow_html=True)
        st.divider()
        cb,cn = st.columns(2)
        with cb:
            if st.button("← Back", key="md_draft_back", use_container_width=True): st.session_state.md_state = "desc"; st.rerun()
        with cn:
            if st.button("🔄 New Draft", key="md_new", use_container_width=True):
                for k in [k for k in st.session_state if k.startswith("md_")]: del st.session_state[k]
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — HR HELPDESK (main chatbot + tool links)
# ══════════════════════════════════════════════════════════════════════════════
def hr_helpdesk_page():
    _hd_init()

    st.markdown("""
    <div class="page-header">
        <h1>💬 HR Helpdesk — Mitra</h1>
        <p>Select your issue · Get policy-based explanation · Draft & send email to HR</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("🔄 New Chat", use_container_width=True, key="hd_new_chat"):
            _hd_reset(); st.rerun()

    if not st.session_state.hd_messages:
        _hd_start()

    # Render chat
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
                st.markdown(f'<a href="{mailto}" target="_blank"><button style="background:#1d4ed8;color:white;'
                    'border:none;padding:9px 22px;border-radius:20px;cursor:pointer;font-size:13px;font-weight:600;'
                    'margin:6px 0;box-shadow:0 2px 8px rgba(29,78,216,0.3);">📨 Open in Mail App</button></a>',
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
        cols = st.columns(min(len(btns),3))
        for i,btn in enumerate(btns):
            with cols[i % min(len(btns),3)]:
                if st.button(btn, key=f"hd_{stage}_{i}_{btn[:20]}", use_container_width=True):
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
            val = st.text_area("Describe your issue:", placeholder="Type your issue here…", height=100)
            if st.form_submit_button("Send ➤") and val.strip():
                _handle_custom_input(val.strip()); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — HANDBOOK BROWSER
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

def handbook_browser_page():
    st.markdown("""
    <div class="page-header">
        <h1>📖 HR Handbook Browser</h1>
        <p>Browse all Orchids HR policy sections — Sections 1–10</p>
    </div>""", unsafe_allow_html=True)

    col_back, _ = st.columns([1,5])
    with col_back:
        if st.button("← Back to Helpdesk", key="hb_back"):
            st.session_state.current_page = "helpdesk"; st.rerun()

    sections = load_handbook_sections(HANDBOOK)
    if not sections:
        st.warning("⚠️ `handbook_text.txt` not found or has no sections.")
        st.info("Place your `handbook_text.txt` file in the same directory as `app.py`.")
        return

    col1,col2 = st.columns([1,2])
    with col1:
        st.subheader("📚 Sections")
        selected = st.selectbox("Choose:", sections, key="hb_select", label_visibility="collapsed")
    with col2:
        st.subheader("📄 Content")
        if st.button("View Section", key="hb_view", use_container_width=True):
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
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🤖 Mitra</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">HR Assistant · Orchids The International School</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)

        pages = {
            "💬 HR Helpdesk":         "helpdesk",
            "🕐 Attendance Verifier": "attendance",
            "📧 Salary Mail Drafter": "maildrafter",
            "📖 Handbook Browser":    "handbook",
        }
        if "current_page" not in st.session_state:
            st.session_state.current_page = "helpdesk"

        for label, key in pages.items():
            active = st.session_state.current_page == key
            style  = "background:#1e3a5f;border-radius:8px;padding:6px 10px;margin:2px 0;" if active else "padding:6px 10px;margin:2px 0;"
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key; st.rerun()

        st.markdown("---")
        st.markdown('<div class="nav-section">Quick Contact</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="contact-card">
            <p><strong>Payroll & Leave Issues</strong></p>
            <p>📧 payroll2.branch@orchids.edu.in</p>
            <br>
            <p><strong>Eduvate ERP Portal</strong></p>
            <p>🌐 Attendance · Leaves · Payslips</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<p style="font-size:11px;color:#475569;text-align:center;">Mitra v2.1 · Policy-verified responses</p>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    inject_css()
    render_sidebar()
    if "current_page" not in st.session_state:
        st.session_state.current_page = "helpdesk"

    page = st.session_state.current_page
    if   page == "helpdesk":    hr_helpdesk_page()
    elif page == "attendance":  attendance_verifier_page()
    elif page == "maildrafter": mail_drafter_page()
    elif page == "handbook":    handbook_browser_page()

if __name__ == "__main__":
    main()
