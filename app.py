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
    ("Team Traditional",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=41081876"),
    ("Individual Traditional",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"),
    ("Artistic",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1727603478"),
    ("Rhythmic",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=594759708"),
]

total_sheets = len(SHEETS)

# ==================================================
# MANUAL MODE – EVENT SELECTION
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
# LOAD DATA
# ==================================================
df = pd.read_csv(sheet_url, skiprows=9)
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(how="all").reset_index(drop=True)

total_rows = len(df)
total_blocks = max(1, math.ceil(total_rows / st.session_state.rows_per_block))

# ==================================================
# AUTO ROW SCROLL LOGIC
# ==================================================
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
    .top-title {
        text-align:center;
        font-size:15px;
        font-weight:600;
        margin-top:-8px;
        margin-bottom:10px;
    }

    .info-bar {
        display:grid;
        grid-template-columns: 1fr 2fr 1fr;
        align-items:center;
        padding:10px 14px;
        margin-bottom:8px;
        border-radius:12px;
        background: linear-gradient(90deg, #1A3A8A, #2563EB, #4F8EDC);
        color: white;
        font-size:20px;
        font-weight:600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .info-left { text-align:left; }
    .info-center { text-align:center; font-size:22px; font-weight:800; }
    .info-right { text-align:right; }

    .stDataFrame td {
        font-size:18px;
        padding:10px;
    }

    .stDataFrame th {
        font-size:19px;
        font-weight:700;
        padding:12px;
        background:#e9effa;
    }

    /* Disable CSV download */
    button[aria-label*="Download"],
    button[title*="Download"] {
        display:none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# HEADER
# ==================================================
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("assets/logo.png", width=220)

with col_title:
    st.markdown(
        """
        <div style="
            display:flex;
            align-items:center;
            height:100%;
            font-size:15px;
            font-weight:600;
        ">
            ALL INDIA INTER-UNIVERSITY YOGASANA CHAMPIONSHIPS
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    f"""
    <div class="info-bar">
        <div class="info-left">
            Chest ID {start+1}–{min(end, total_rows)} of {total_rows}
        </div>
        <div class="info-center">
            {sheet_name}
        </div>
        <div class="info-right">
            🕒 {datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%d-%m-%Y %H:%M:%S')}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==================================================
# TABLE
# ==================================================
st.dataframe(
    block_df,
    use_container_width=True,
    height=520,
    hide_index=True
)

# ==================================================
# CONTROL PANEL (FONT MODE REMOVED)
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
