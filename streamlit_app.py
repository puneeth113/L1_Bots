import streamlit as st
import re
from typing import List, Optional, Dict
from datetime import datetime, timedelta

st.set_page_config(page_title="HR Handbook & Chatbot", page_icon="📘", layout="wide")

HANDBOOK = "handbook_text.txt"

# ==================== SHIFT DEFINITIONS ====================
# Marketing shift is intentionally excluded.
# Structure: label -> {in, out, total_hours, part_time, seven_day}
SHIFTS: Dict[str, dict] = {
    # ── Regular full-time ─────────────────────────────────────────────────────
    "09:00 - 17:30  (8.50 hrs)":  {"in": "09:00", "out": "17:30", "total": 8.50,  "part_time": False, "seven_day": False},
    "09:00 - 16:30  (7.50 hrs)":  {"in": "09:00", "out": "16:30", "total": 7.50,  "part_time": False, "seven_day": False},
    "09:00 - 15:45  (6.75 hrs)":  {"in": "09:00", "out": "15:45", "total": 6.75,  "part_time": False, "seven_day": False},
    "08:00 - 17:00  (9.00 hrs)":  {"in": "08:00", "out": "17:00", "total": 9.00,  "part_time": False, "seven_day": False},
    "08:15 - 17:00  (8.75 hrs)":  {"in": "08:15", "out": "17:00", "total": 8.75,  "part_time": False, "seven_day": False},
    "08:15 - 16:45  (8.50 hrs)":  {"in": "08:15", "out": "16:45", "total": 8.50,  "part_time": False, "seven_day": False},
    "08:15 - 16:30  (8.25 hrs)":  {"in": "08:15", "out": "16:30", "total": 8.25,  "part_time": False, "seven_day": False},
    "08:15 - 16:15  (8.00 hrs)":  {"in": "08:15", "out": "16:15", "total": 8.00,  "part_time": False, "seven_day": False},
    "08:15 - 14:30  (6.25 hrs)":  {"in": "08:15", "out": "14:30", "total": 6.25,  "part_time": False, "seven_day": False},
    "08:15 - 14:15  (6.00 hrs)":  {"in": "08:15", "out": "14:15", "total": 6.00,  "part_time": False, "seven_day": False},
    "08:30 - 15:30  (7.00 hrs)":  {"in": "08:30", "out": "15:30", "total": 7.00,  "part_time": False, "seven_day": False},
    "07:30 - 16:00  (8.50 hrs)":  {"in": "07:30", "out": "16:00", "total": 8.50,  "part_time": False, "seven_day": False},
    "07:40 - 15:40  (8.00 hrs)":  {"in": "07:40", "out": "15:40", "total": 8.00,  "part_time": False, "seven_day": False},
    # ── 7-Day shifts ─────────────────────────────────────────────────────────
    "7D | 09:30 - 18:00  (8.50 hrs)": {"in": "09:30", "out": "18:00", "total": 8.50, "part_time": False, "seven_day": True},
    "7D | 09:00 - 17:30  (8.50 hrs)": {"in": "09:00", "out": "17:30", "total": 8.50, "part_time": False, "seven_day": True},
    # ── Part-time / Corp_7D_SP ────────────────────────────────────────────────
    "PT | 09:00 - 16:30  (7.50 hrs)": {"in": "09:00", "out": "16:30", "total": 7.50, "part_time": True, "seven_day": False},
    "PT | 08:15 - 15:00  (6.75 hrs)": {"in": "08:15", "out": "15:00", "total": 6.75, "part_time": True, "seven_day": False},
    "PT | 08:00 - 14:45  (6.75 hrs)": {"in": "08:00", "out": "14:45", "total": 6.75, "part_time": True, "seven_day": False},
}

PUNCH_IN_BUFFER_MIN = 15  # minutes grace period for late punch-in


def get_shift_info(label: str) -> dict:
    return SHIFTS.get(label, {})


def validate_time_format(time_str: str) -> bool:
    try:
        datetime.strptime(time_str.strip(), "%H:%M")
        return True
    except ValueError:
        return False


def calculate_working_hours(punch_in: str, punch_out: str) -> Optional[float]:
    """Returns float hours worked, None on parse error. Negative = wrong order."""
    try:
        t_in  = datetime.strptime(punch_in.strip(),  "%H:%M")
        t_out = datetime.strptime(punch_out.strip(), "%H:%M")
        return (t_out - t_in).total_seconds() / 3600
    except Exception:
        return None


def is_late_punch_in(scheduled_in: str, actual_in: str) -> bool:
    try:
        diff = (datetime.strptime(actual_in, "%H:%M") -
                datetime.strptime(scheduled_in, "%H:%M")).total_seconds() / 60
        return diff > PUNCH_IN_BUFFER_MIN
    except Exception:
        return False


def get_punch_in_delay_minutes(scheduled_in: str, actual_in: str) -> float:
    """Returns the delay in minutes (0 if on time or within buffer)."""
    try:
        diff = (datetime.strptime(actual_in, "%H:%M") -
                datetime.strptime(scheduled_in, "%H:%M")).total_seconds() / 60
        return max(0, diff)
    except Exception:
        return 0


def evaluate_attendance(actual_hours: float, shift_info: dict, is_late: bool = False) -> dict:
    """Per-shift attendance evaluation — full / half / short.
    If late punch-in beyond buffer, mark as half-day regardless of hours."""
    total       = shift_info.get("total", 8.5)
    half_thresh = total / 2
    is_pt       = shift_info.get("part_time", False)
    pt_label    = "Part-time half-day" if is_pt else "Half-day"

    # If punch-in is delayed beyond buffer, mark as half-day
    if is_late:
        return {"status": "HALF",  "color": "warning",
                "message": (f"⚠️ {pt_label} — Late punch-in detected ({actual_hours:.2f} hrs worked). "
                            "Attendance marked as half-day due to delayed arrival.")}

    if actual_hours >= total:
        return {"status": "FULL",  "color": "success",
                "message": f"✅ Full working day ({actual_hours:.2f} / {total:.2f} hrs) — Valid attendance!"}
    elif actual_hours >= half_thresh:
        return {"status": "HALF",  "color": "warning",
                "message": (f"⚠️ {pt_label} ({actual_hours:.2f} hrs worked, "
                            f"threshold {half_thresh:.2f} hrs). "
                            "Apply regularization if a punch was missed.")}
    else:
        return {"status": "SHORT", "color": "error",
                "message": (f"❌ Insufficient hours ({actual_hours:.2f} hrs worked, "
                            f"minimum {half_thresh:.2f} hrs for half-day). "
                            "Please contact HR.")}


# ==================== HANDBOOK HELPERS ====================

def load_handbook_sections(path: str) -> List[str]:
    sections: List[str] = []
    section_pattern = re.compile(r"^Section\s*\d+\s*(.+)$", re.IGNORECASE)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if section_pattern.match(line.strip()):
                sections.append(line.strip())
    return sections


def get_section_detail(path: str, section_header: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(rf"(?ims)^{re.escape(section_header)}\s*(.*?)(?=^Section\s*\d+\s|\Z)")
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def summarize_section_text(section_text: str, max_lines: int = 7) -> List[str]:
    if not section_text:
        return []
    cleaned   = re.sub(r"\s+", " ", section_text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    summary: List[str] = []
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 15 or s.lower().startswith("section "):
            continue
        if s.isupper() and len(s) < 50:
            continue
        if s not in summary:
            summary.append(s)
            if len(summary) >= max_lines:
                break
    return summary


# ==================== MISC HELPERS ====================

def is_within_two_months(date_to_check) -> bool:
    today = datetime.now().date()
    return today - timedelta(days=60) <= date_to_check <= today


def reset_to_issue_select():
    for k in ["shift", "punch_in", "punch_out", "leave_concern", "leave_date",
              "lapsed_type", "salary_concern", "working_days", "lop_days",
              "salary_component", "salary_description"]:
        st.session_state.pop(k, None)
    st.session_state.selected_issue = None
    st.session_state.chat_state     = "select_issue"


def go_back(state: str):
    st.session_state.chat_state = state
    st.rerun()


# ==================== PAGE 1: HANDBOOK BROWSER ====================

def handbook_browser_page():
    st.title("📖 Handbook Browser")
    st.markdown("Browse and view all handbook sections here.")
    st.divider()

    sections = load_handbook_sections(HANDBOOK)
    if not sections:
        st.error("No sections found. Please check your handbook file.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📚 Sections")
        selected = st.selectbox("Choose a section:", sections,
                                key="handbook_select", label_visibility="collapsed")
    with col2:
        st.subheader("📄 Content")
        if st.button("View Section", key="view_handbook", use_container_width=True):
            detail = get_section_detail(HANDBOOK, selected)
            if detail:
                clean = detail.replace("\\r\\n", "\n").replace("\\n", "\n")
                st.markdown("**Summary:**")
                bullets = summarize_section_text(clean)
                for b in bullets:
                    st.markdown(f"• {b}")
                if not bullets:
                    st.markdown("_No summary available._")
                with st.expander("View Full Section"):
                    st.markdown(clean)
            else:
                st.warning("No content found for this section.")


# ==================== PAGE 2: HR CHATBOT ====================

def hr_chatbot_page():
    st.title("🤖 HR Assistant Chatbot")
    st.markdown("Resolve your HR concerns step by step.")
    st.divider()

    if "chat_state"     not in st.session_state: st.session_state.chat_state     = "get_erp"
    if "employee_erp"   not in st.session_state: st.session_state.employee_erp   = ""
    if "selected_issue" not in st.session_state: st.session_state.selected_issue = None

    # ── STEP 1: ERP ──────────────────────────────────────────────────────────
    if st.session_state.chat_state == "get_erp":
        st.info("**Step 1:** Verify Your Identity")
        erp = st.text_input("Enter your ERP/Employee Code:",
                            placeholder="e.g., 20262002367_OIS", key="erp_input")
        if st.button("➡️ Next", key="btn_erp_next", use_container_width=True):
            if erp.strip():
                st.session_state.employee_erp = erp.strip()
                st.session_state.chat_state   = "select_issue"
                st.rerun()
            else:
                st.error("❌ Please enter your ERP/Employee Code")

    # ── STEP 2: ISSUE SELECT ──────────────────────────────────────────────────
    elif st.session_state.chat_state == "select_issue":
        st.success(f"✓ ERP ID: **{st.session_state.employee_erp}**")
        st.divider()
        st.info("**Step 2:** Select Your Issue Type")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🕐 Attendance", key="btn_attendance", use_container_width=True):
                st.session_state.selected_issue = "Attendance"
                st.session_state.chat_state     = "attendance_shift"
                st.rerun()
        with c2:
            if st.button("🏖️ Leave", key="btn_leave", use_container_width=True):
                st.session_state.selected_issue = "Leave"
                st.session_state.chat_state     = "leave_type"
                st.rerun()
        with c3:
            if st.button("💰 Salary", key="btn_salary", use_container_width=True):
                st.session_state.selected_issue = "Salary"
                st.session_state.chat_state     = "salary_type"
                st.rerun()

    # ==================== ATTENDANCE FLOW ====================
    elif st.session_state.selected_issue == "Attendance":
        st.success(f"✓ ERP: **{st.session_state.employee_erp}** | Issue: **Attendance**")
        st.divider()

        # ── Shift Selection ──────────────────────────────────────────────────
        if st.session_state.chat_state == "attendance_shift":
            st.info("**Step 3:** Select Your Shift")

            shift_type = st.radio(
                "Shift category:",
                ["Regular", "7-Day", "Part-Time (Corp_7D_SP)"],
                key="shift_type_radio", horizontal=True
            )
            if shift_type == "Regular":
                options = [k for k, v in SHIFTS.items() if not v["part_time"] and not v["seven_day"]]
            elif shift_type == "7-Day":
                options = [k for k, v in SHIFTS.items() if v["seven_day"]]
            else:
                options = [k for k, v in SHIFTS.items() if v["part_time"]]

            selected_shift = st.selectbox("Select your shift:", options, key="shift_select")

            # Info card for selected shift
            si = get_shift_info(selected_shift)
            if si:
                half = si["total"] / 2
                type_label = ("📋 Part-Time" if si["part_time"]
                              else "🗓️ 7-Day" if si["seven_day"] else "👔 Regular")
                st.info(
                    f"{type_label}  |  🕐 **{si['in']} → {si['out']}**  |  "
                    f"Total: **{si['total']:.2f} hrs**  |  "
                    f"Half-day threshold: **{half:.2f} hrs**"
                )

            if st.button("➡️ Next", key="btn_shift", use_container_width=True):
                st.session_state.shift      = selected_shift
                st.session_state.chat_state = "attendance_punch_in"
                st.rerun()

        # ── Punch In ─────────────────────────────────────────────────────────
        elif st.session_state.chat_state == "attendance_punch_in":
            si = get_shift_info(st.session_state.shift)
            st.info(f"**Step 4:** Punch-In Time  |  Shift: **{si.get('in','?')} → {si.get('out','?')}**")
            st.markdown(f"**Selected Shift:** {st.session_state.shift}")

            pi = st.text_input("Enter actual punch-in time (HH:MM):",
                               placeholder=si.get("in", "08:15"), key="punch_in_input")
            st.caption(f"📌 Scheduled: **{si.get('in','?')}** — up to **{PUNCH_IN_BUFFER_MIN} min** late allowed.")

            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_pi_back", use_container_width=True):
                    go_back("attendance_shift")
            with cn:
                if st.button("➡️ Next", key="btn_punch_in", use_container_width=True):
                    if not pi.strip():
                        st.error("❌ Please enter punch-in time")
                    elif not validate_time_format(pi):
                        st.error("❌ Invalid format — use HH:MM (e.g. 08:15)")
                    else:
                        if is_late_punch_in(si.get("in", "08:00"), pi.strip()):
                            st.warning(
                                f"⚠️ Punch-in **{pi.strip()}** is more than {PUNCH_IN_BUFFER_MIN} min "
                                f"after scheduled time **{si.get('in','?')}**. This will be marked as half-day."
                            )
                        st.session_state.punch_in   = pi.strip()
                        st.session_state.chat_state = "attendance_punch_out"
                        st.rerun()

        # ── Punch Out ────────────────────────────────────────────────────────
        elif st.session_state.chat_state == "attendance_punch_out":
            si = get_shift_info(st.session_state.shift)
            st.info(f"**Step 5:** Punch-Out Time  |  Scheduled: **{si.get('out','?')}**")
            st.markdown(f"**Shift:** {st.session_state.shift}  |  **Punch In:** {st.session_state.punch_in}")

            half = si.get("total", 8.5) / 2
            po = st.text_input("Enter actual punch-out time (HH:MM):",
                               placeholder=si.get("out", "17:00"), key="punch_out_input")
            st.caption(f"📌 Full day ≥ **{si.get('total',8.5):.2f} hrs**  |  Half-day ≥ **{half:.2f} hrs**")

            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_po_back", use_container_width=True):
                    go_back("attendance_punch_in")
            with cn:
                if st.button("✅ Analyze Attendance", key="btn_validate", use_container_width=True):
                    if not po.strip():
                        st.error("❌ Please enter punch-out time")
                    elif not validate_time_format(po):
                        st.error("❌ Invalid format — use HH:MM (e.g. 16:30)")
                    else:
                        st.session_state.punch_out  = po.strip()
                        st.session_state.chat_state = "attendance_result"
                        st.rerun()

        # ── Result ──────────────────────────────────────────────────────────
        elif st.session_state.chat_state == "attendance_result":
            si    = get_shift_info(st.session_state.shift)
            hours = calculate_working_hours(st.session_state.punch_in, st.session_state.punch_out)
            is_late = is_late_punch_in(si.get("in", "08:00"), st.session_state.punch_in)
            st.divider()
            st.subheader("✓ Attendance Analysis")

            if hours is None:
                st.error("❌ Could not parse punch times. Please re-enter.")
                if st.button("← Re-enter", key="btn_reenter", use_container_width=True):
                    go_back("attendance_punch_in")
            elif hours < 0:
                st.error(
                    f"❌ Punch-out **{st.session_state.punch_out}** is earlier than "
                    f"punch-in **{st.session_state.punch_in}**. Please correct the times."
                )
                if st.button("← Re-enter", key="btn_reenter_neg", use_container_width=True):
                    go_back("attendance_punch_in")
            else:
                total = si.get("total", 8.5)
                half  = total / 2
                res   = evaluate_attendance(hours, si, is_late=is_late)

                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"- **Shift:** {st.session_state.shift}")
                    st.markdown(f"- **Scheduled:** {si.get('in','?')} → {si.get('out','?')}")
                    st.markdown(f"- **Punch In:** {st.session_state.punch_in}")
                    st.markdown(f"- **Punch Out:** {st.session_state.punch_out}")
                with cb:
                    st.markdown(f"- **Hours Worked:** {hours:.2f} hrs")
                    st.markdown(f"- **Full Day:** ≥ {total:.2f} hrs")
                    st.markdown(f"- **Half Day:** ≥ {half:.2f} hrs")
                    type_lbl = ("Part-Time" if si.get("part_time") else
                                "7-Day"     if si.get("seven_day") else "Regular")
                    st.markdown(f"- **Shift Type:** {type_lbl}")

                if   res["color"] == "success": st.success(res["message"])
                elif res["color"] == "warning": st.warning(res["message"])
                else:                           st.error(res["message"])

                if is_late:
                    delay_mins = get_punch_in_delay_minutes(si.get("in", "08:00"), st.session_state.punch_in)
                    st.warning(
                        f"⏰ **Delayed Punch-In:** {st.session_state.punch_in} vs scheduled "
                        f"{si.get('in','?')} (Delay: {delay_mins:.0f} min, Buffer: {PUNCH_IN_BUFFER_MIN} min). "
                        f"**Attendance marked as HALF-DAY.**"
                    )

            st.divider()
            cb2, cn2 = st.columns(2)
            with cb2:
                if st.button("← Back", key="btn_res_back", use_container_width=True):
                    go_back("attendance_punch_out")
            with cn2:
                if st.button("🔄 Start New Session", key="btn_restart_att", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

    # ==================== LEAVE FLOW ====================
    elif st.session_state.selected_issue == "Leave":
        st.success(f"✓ ERP: **{st.session_state.employee_erp}** | Issue: **Leave**")
        st.divider()

        if st.session_state.chat_state == "leave_type":
            st.info("**Step 3:** What is your leave concern?")
            concern = st.selectbox(
                "Select your leave issue:",
                ["-- Select --", "Leaves were not credited", "Leaves lapsed", "Missed to apply leave"],
                key="leave_concern_select"
            )
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_leave_back", use_container_width=True):
                    go_back("select_issue")
            with cn:
                if st.button("➡️ Continue", key="btn_leave_continue", use_container_width=True):
                    if concern == "-- Select --":
                        st.error("❌ Please select a leave issue type")
                    else:
                        st.session_state.leave_concern = concern
                        st.session_state.chat_state = (
                            "leave_missed"       if concern == "Missed to apply leave" else
                            "leave_lapsed"       if concern == "Leaves lapsed" else
                            "leave_not_credited"
                        )
                        st.rerun()

        elif st.session_state.chat_state == "leave_not_credited":
            st.info("📋 **Leaves Were Not Credited**")
            st.markdown("""
**Leave Cycle:** 26th May to 25th May (next year)

**CL Credit Schedule:**
- 6 days credited in **June**  |  5 days in **December**
- Maximum **3 CL** allowed per month

**Why leave may not have been credited:**
- Joined after credit date — credits are on **pro-rata** basis
- Leave balance exhausted — day marked as **LOP**
- ERP/system delay — check Eduvate after 2–3 working days of the credit date

**Action:** Email HR with your leave statement if balance shows zero after the expected credit date.

**Contact:** payroll2.branch@orchids.edu.in
            """)
            st.divider()
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_nc_back", use_container_width=True):
                    go_back("leave_type")
            with cn:
                if st.button("🔄 Start New Session", key="btn_restart_nc", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "leave_missed":
            st.info("📅 **Missed to Apply Leave**")
            st.markdown("Select the date on which you missed applying for leave:")
            leave_date = st.date_input("Leave date:", value=datetime.now().date(), key="leave_date_widget")
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_missed_back", use_container_width=True):
                    go_back("leave_type")
            with cn:
                if st.button("✅ Check Eligibility", key="btn_check_arrears", use_container_width=True):
                    st.session_state.leave_date = leave_date
                    st.session_state.chat_state = "leave_missed_result"
                    st.rerun()

        elif st.session_state.chat_state == "leave_missed_result":
            st.divider()
            st.subheader("📋 Eligibility Result")
            ld = st.session_state.leave_date
            if is_within_two_months(ld):
                st.success("✅ **Eligible for Arrears Application**")
                st.markdown(f"""
Your leave date **{ld.strftime('%d-%b-%Y')}** is within the 2-month window.

**Action Required:**
1. Log in to **Eduvate** ERP → **Leave → Apply for Arrears**
2. Select date: **{ld.strftime('%d-%b-%Y')}**
3. Provide reason for late application and submit for HR approval.

**Contact:** payroll2.branch@orchids.edu.in
                """)
            else:
                st.error("❌ **Not Eligible for Arrears**")
                st.markdown(f"""
Your leave date **{ld.strftime('%d-%b-%Y')}** is beyond the 2-month policy window.

Email HR explaining your situation — they may consider it on a case-by-case basis.

**Contact:** payroll2.branch@orchids.edu.in
                """)
            st.divider()
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_mr_back", use_container_width=True):
                    go_back("leave_missed")
            with cn:
                if st.button("🔄 Start New Session", key="btn_restart_missed", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "leave_lapsed":
            st.info("📋 **Leaves Lapsed — Which Leave Type?**")
            lapsed = st.selectbox(
                "Select the leave type that lapsed:",
                ["-- Select --", "Casual Leave (CL)", "Compensatory Off (CO)", "Weekly Off (WO)"],
                key="lapsed_type_select"
            )
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_lapsed_back", use_container_width=True):
                    go_back("leave_type")
            with cn:
                if st.button("➡️ Continue", key="btn_lapsed_continue", use_container_width=True):
                    if lapsed == "-- Select --":
                        st.error("❌ Please select a leave type")
                    else:
                        st.session_state.lapsed_type = lapsed
                        st.session_state.chat_state  = "leave_lapsed_result"
                        st.rerun()

        elif st.session_state.chat_state == "leave_lapsed_result":
            lapsed = st.session_state.lapsed_type
            st.divider()
            st.subheader(f"📋 Leave Lapsed — {lapsed}")

            if lapsed == "Casual Leave (CL)":
                st.warning("⚠️ **Casual Leave (CL) Lapsed**")
                st.markdown("""
CL does **not carry forward**. Any unused balance **lapses** at end of cycle (25th May each year).

**Possible reasons in your leave statement:**
- **Reversal Arrears** — already encashed, check your salary slip
- **Policy Limit** — exceeded the 3-CL-per-month cap

Contact HR with your leave statement if unclear. **Contact:** payroll2.branch@orchids.edu.in
                """)
            elif lapsed == "Compensatory Off (CO)":
                st.info("🗓️ **Compensatory Off (CO) — 90-Day Validity**")
                st.markdown("""
CO must be availed **within 90 days** of the grant date. It lapses automatically after 90 days.

Check the grant date in Eduvate. If lapsed before 90 days, contact HR with the grant date and leave statement.

**Contact:** payroll2.branch@orchids.edu.in
                """)
            elif lapsed == "Weekly Off (WO)":
                st.info("📅 **Weekly Off (WO) — 5-Day (1 Week) Validity**")
                st.markdown("""
WO lapses after **1 week (5 working days)**. It cannot be carried beyond the same working week.

If you believe it was incorrectly lapsed, contact HR with your attendance and leave statement.

**Contact:** payroll2.branch@orchids.edu.in
                """)

            st.divider()
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_lr_back", use_container_width=True):
                    go_back("leave_lapsed")
            with cn:
                if st.button("🔄 Start New Session", key="btn_restart_lapsed", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

    # ==================== SALARY FLOW ====================
    elif st.session_state.selected_issue == "Salary":
        st.success(f"✓ ERP: **{st.session_state.employee_erp}** | Issue: **Salary**")
        st.divider()

        if st.session_state.chat_state == "salary_type":
            st.info("**Step 3:** What is your salary concern?")
            concern = st.radio(
                "Select your concern:",
                ["Salary not received", "Salary discrepancy", "Salary components question"],
                key="salary_concern_radio"
            )
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_sal_back", use_container_width=True):
                    go_back("select_issue")
            with cn:
                if st.button("➡️ Continue", key="btn_salary_continue", use_container_width=True):
                    st.session_state.salary_concern = concern
                    st.session_state.chat_state = (
                        "salary_not_received"     if concern == "Salary not received" else
                        "salary_discrepancy_days" if concern == "Salary discrepancy" else
                        "salary_components"
                    )
                    st.rerun()

        elif st.session_state.chat_state == "salary_not_received":
            st.warning("💳 **Salary Not Received**")
            st.markdown("""
1. Check if salary was processed in your bank account
2. Wait **2–3 working days** for bank credit if recently processed
3. Contact HR if still not received after 3 days

**Contact HR with:** ERP Code, expected salary date, last date received.

**Email:** payroll2.branch@orchids.edu.in
            """)
            st.divider()
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_nr_back", use_container_width=True):
                    go_back("salary_type")
            with cn:
                if st.button("🔄 Start New Session", key="btn_restart_nr", use_container_width=True):
                    reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "salary_discrepancy_days":
            st.info("**Step 4:** Working Days in Your Payslip")
            wd = st.number_input("Working days shown in payslip this month?",
                                 min_value=0, max_value=31, step=1, key="working_days_input")
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_wd_back", use_container_width=True):
                    go_back("salary_type")
            with cn:
                if st.button("➡️ Next", key="btn_days_next", use_container_width=True):
                    st.session_state.working_days = int(wd)
                    st.session_state.chat_state   = "salary_discrepancy_lop"
                    st.rerun()

        elif st.session_state.chat_state == "salary_discrepancy_lop":
            st.info("**Step 5:** Loss of Pay (LOP) Days")
            st.markdown(f"Working days: **{st.session_state.working_days}**")
            lop = st.number_input("LOP (Loss of Pay) days in payslip?",
                                  min_value=0, max_value=31, step=1, key="lop_days_input")
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_lop_back", use_container_width=True):
                    go_back("salary_discrepancy_days")
            with cn:
                if st.button("➡️ Next", key="btn_lop_next", use_container_width=True):
                    st.session_state.lop_days   = int(lop)
                    st.session_state.chat_state = "salary_discrepancy_component"
                    st.rerun()

        elif st.session_state.chat_state == "salary_discrepancy_component":
            st.info("**Step 6:** Which Component Has the Discrepancy?")
            st.markdown(f"Working days: **{st.session_state.working_days}** | LOP: **{st.session_state.lop_days}**")
            comp = st.text_input("Type the salary component (e.g., Basic, HRA, DA, PF, Bonus…):",
                                 placeholder="e.g., HRA", key="salary_component_input")
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_comp_back", use_container_width=True):
                    go_back("salary_discrepancy_lop")
            with cn:
                if st.button("➡️ Next", key="btn_component_next", use_container_width=True):
                    if comp.strip():
                        st.session_state.salary_component = comp.strip()
                        st.session_state.chat_state       = "salary_discrepancy_description"
                        st.rerun()
                    else:
                        st.error("❌ Please enter the salary component")

        elif st.session_state.chat_state == "salary_discrepancy_description":
            st.info("**Step 7:** Describe Your Issue")
            st.markdown(
                f"Working days: **{st.session_state.working_days}** | "
                f"LOP: **{st.session_state.lop_days}** | "
                f"Component: **{st.session_state.salary_component}**"
            )
            desc = st.text_area(
                "Describe the discrepancy (expected vs actual, what seems wrong):",
                placeholder="e.g., My HRA should be ₹8,000 per offer letter but ₹6,000 was credited.",
                height=130, key="salary_description_input"
            )
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_desc_back", use_container_width=True):
                    go_back("salary_discrepancy_component")
            with cn:
                if st.button("✅ Generate Mail Draft", key="btn_generate_mail", use_container_width=True):
                    if desc.strip():
                        st.session_state.salary_description = desc.strip()
                        st.session_state.chat_state         = "salary_mail_draft"
                        st.rerun()
                    else:
                        st.error("❌ Please describe your issue before proceeding")

        elif st.session_state.chat_state == "salary_mail_draft":
            st.divider()
            st.subheader("📧 Mail Draft — Ready to Send to HR")
            erp       = st.session_state.get("employee_erp",       "[ERP Code]")
            wd        = st.session_state.get("working_days",        "N/A")
            lop       = st.session_state.get("lop_days",            "N/A")
            component = st.session_state.get("salary_component",   "[Component]")
            desc      = st.session_state.get("salary_description", "[Description]")
            month_yr  = datetime.now().strftime("%B %Y")

            if wd == "N/A" or component == "[Component]":
                st.warning("⚠️ Session data is incomplete. Please restart the salary discrepancy flow.")
                if st.button("↩️ Restart Salary Flow", key="btn_guard_restart", use_container_width=True):
                    st.session_state.chat_state = "salary_type"; st.rerun()
            else:
                draft = f"""Subject: Salary Discrepancy — {component} — {month_yr} — ERP: {erp}

To,
The HR / Payroll Team,

Dear HR Team,

I am writing to bring to your attention a discrepancy I have noticed in my salary for the month of {month_yr}.

Employee Details:
  • ERP / Employee Code           : {erp}
  • Month of Concern              : {month_yr}
  • Working Days (as per payslip) : {wd} days
  • LOP Days (as per payslip)     : {lop} days
  • Component with Discrepancy    : {component}

Issue Description:
{desc}

I request you to kindly review my payslip and salary records for the above-mentioned month
and clarify or rectify the discrepancy at the earliest.

Please let me know if any additional information is required from my side.

Thank you for your time and assistance.

Warm regards,
[Your Full Name]
ERP Code: {erp}
[Your Department / Branch]
[Your Contact Number]"""

                st.code(draft, language="")
                st.caption("📋 Copy the draft, fill in your details, and send to **payroll2.branch@orchids.edu.in**")
                st.divider()
                cb, cn = st.columns(2)
                with cb:
                    if st.button("← Back", key="btn_mail_back", use_container_width=True):
                        go_back("salary_discrepancy_description")
                with cn:
                    if st.button("🔄 Start New Session", key="btn_restart_mail", use_container_width=True):
                        reset_to_issue_select(); st.rerun()

        elif st.session_state.chat_state == "salary_components":
            st.info("📊 **Salary Components — Reference Guide**")
            st.markdown("""
**Earnings:**
- **Basic** — Base salary as per employment contract
- **HRA** — House Rent Allowance (typically % of Basic)
- **DA** — Dearness Allowance
- **Other Allowances** — Special / personal allowances
- **Arrears** — Pending adjustments from prior months

**Deductions:**
- **PF** — Provident Fund (12% of Basic, mandatory)
- **IT** — Income Tax (as per slab)
- **ESI** — Employee State Insurance (gross ≤ ₹21,000/month)
- **Insurance** — Group / personal insurance premium
- **Loan / Advance Recovery** — Active loan deductions
- **LOP** — Loss of Pay for absent days beyond leave balance

Refer to your offer letter / contract or contact HR at payroll2.branch@orchids.edu.in
            """)
            st.divider()
            cb, cn = st.columns(2)
            with cb:
                if st.button("← Back", key="btn_comp_ref_back", use_container_width=True):
                    go_back("salary_type")
            with cn:
                if st.button("🔄 Start New Session", key="btn_restart_comp", use_container_width=True):
                    reset_to_issue_select(); st.rerun()


# ==================== MAIN ====================

def main():
    st.sidebar.title("📍 Navigation")
    page = st.sidebar.radio(
        "Select Page:", ["🤖 HR Chatbot", "📖 Handbook Browser"],
        key="page_nav", label_visibility="collapsed"
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📞 Quick Contact")
    st.sidebar.markdown("**Payroll & Leave Issues:**")
    st.sidebar.markdown("📧 payroll2.branch@orchids.edu.in")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Eduvate ERP System:**")
    st.sidebar.markdown("🌐 Your portal for attendance, logs, salary slips, and leave")

    if page == "🤖 HR Chatbot":
        hr_chatbot_page()
    else:
        handbook_browser_page()


if __name__ == "__main__":
    main()
