import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import math
from zoneinfo import ZoneInfo

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Live Yogasana Scores",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# SESSION STATE DEFAULTS
# ==================================================
defaults = {
    "sheet_index": 0,
    "block_index": 0,
    "rows_per_block": 10,
    "seconds_per_block": 10,
    "auto_scroll": True,
    "manual_override": False,
    "freeze": False,
    "last_sheet_index": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================================================
# AUTO REFRESH
# ==================================================
st_autorefresh(
    interval=st.session_state.seconds_per_block * 1000,
    key="cycle"
)

# ==================================================
# GOOGLE SHEETS
# ==================================================
SHEET_ID = "18N4NcpXgFdk0tMLxSNSbZAUgnTQBZWWBLdCy_DPL_Nc"

SHEETS = [
    ("Team Traditional: Rig Veda-Stage 1",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=41081876"),
    ("Team Traditional: Yajur Veda-Stage 2",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1360132147"),
    ("Team Traditional: Sama Veda-Stage 3",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=404450838"),
    ("Team Traditional: Atharva Veda-Stage 4",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=96540094"),
    ("Individual Traditional: Eklavya-Stage 5",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"),
    ("Artistic: Arjuna-Stage 6",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1727603478"),
    ("Rhythmic: Nakula-Stage 7",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=594759708"),
]

total_sheets = len(SHEETS)

# ==================================================
# MANUAL MODE
# ==================================================
if st.session_state.manual_override:
    selected = st.selectbox(
        "Select Event (Manual Mode)",
        [s[0] for s in SHEETS],
        index=st.session_state.sheet_index
    )
    new_index = [s[0] for s in SHEETS].index(selected)
    if new_index != st.session_state.sheet_index:
        st.session_state.sheet_index = new_index
        st.session_state.block_index = 0

# ==================================================
# RESET ON SHEET CHANGE
# ==================================================
if st.session_state.last_sheet_index != st.session_state.sheet_index:
    st.session_state.block_index = 0
    st.session_state.last_sheet_index = st.session_state.sheet_index

sheet_name, sheet_url = SHEETS[st.session_state.sheet_index]

# ==================================================
# LOAD DATA (CLEANED)
# ==================================================
df = pd.read_csv(sheet_url, skiprows=9)
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(how="all").reset_index(drop=True)

# Remove line breaks inside cells/headers
df = df.replace(r'[\r\n]+', ' ', regex=True)

# ==================================================
# 🔥 SORT BY TOTAL (DESCENDING – FINAL)
# ==================================================
if "Total" in df.columns:
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    df = df.sort_values(
        by="Total",
        ascending=False,      # 🔥 DESCENDING
        na_position="last"    # blanks always at bottom
    ).reset_index(drop=True)

# ==================================================
# AUTO SCROLL LOGIC
# ==================================================
total_rows = len(df)
total_blocks = max(1, math.ceil(total_rows / st.session_state.rows_per_block))

start = st.session_state.block_index * st.session_state.rows_per_block
end = start + st.session_state.rows_per_block
block_df = df.iloc[start:end]

if st.session_state.auto_scroll and not st.session_state.freeze:
    st.session_state.block_index += 1
    if st.session_state.block_index >= total_blocks:
        st.session_state.block_index = 0
        if not st.session_state.manual_override:
            st.session_state.sheet_index = (st.session_state.sheet_index + 1) % total_sheets

# ==================================================
# STYLES
# ==================================================
st.markdown(
    """
    <style>
    body { background:#f8fafc; }

    .info-bar {
        display:grid;
        grid-template-columns: 1fr 2fr 1fr;
        align-items:center;
        padding:16px 20px;
        margin-bottom:14px;
        border-radius:14px;
        background: linear-gradient(90deg, #1A3A8A, #2563EB, #4F8EDC);
        color:white;
        font-size:26px;
        font-weight:700;
    }

    .info-center {
        text-align:center;
        font-size:30px;
        font-weight:900;
    }

    table {
        width:100%;
        border-collapse:collapse;
    }

    th {
        font-size:28px;
        font-weight:800;
        background:#e9effa;
        padding:18px;
        border:1px solid #cbd5e1;
        text-align:center;
        white-space:nowrap;
    }

    td {
        font-size:26px;
        font-weight:600;
        padding:16px;
        border:1px solid #e2e8f0;
        text-align:center;
        white-space:nowrap;
    }

    th:nth-child(2),
    td:nth-child(2) {
        text-align:left !important;
        padding-left:20px !important;
        white-space:normal;
    }

    tr:nth-child(even) {
        background:#f1f5f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# BANNER
# ==================================================
st.image(
    "assets/banner.png",
    use_container_width=True
)

# ==================================================
# INFO BAR
# ==================================================
st.markdown(
    f"""
    <div class="info-bar">
        <div>{start+1}–{min(end, total_rows)} of {total_rows}</div>
        <div class="info-center">{sheet_name}</div>
        <div style="text-align:right">
            🕒 {datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%d-%m-%Y %H:%M:%S')}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# TABLE
# ==================================================
st.markdown(
    block_df.to_html(index=False),
    unsafe_allow_html=True
)

# ==================================================
# CONTROL PANEL
# ==================================================
st.markdown("## 🎛️ Control Panel")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.session_state.auto_scroll = st.toggle("Auto Scroll", st.session_state.auto_scroll)
with c2:
    st.session_state.manual_override = st.toggle("Manual Mode", st.session_state.manual_override)
with c3:
    st.session_state.rows_per_block = st.slider("Rows per view", 5, 20, st.session_state.rows_per_block)
with c4:
    st.session_state.seconds_per_block = st.slider("Seconds per view", 5, 30, st.session_state.seconds_per_block)
with c5:
    st.session_state.freeze = st.toggle("🛑 FREEZE", st.session_state.freeze)

# ==================================================
# FOOTER
# ==================================================
st.markdown(
    "<hr><p style='text-align:center; color:gray;'>© S-VYASA Deemed-to-be University | Association of Indian Universities</p>",
    unsafe_allow_html=True
)
