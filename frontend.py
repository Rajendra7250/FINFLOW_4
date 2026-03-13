import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
from backend import *

USERS = {
    "admin": {
        "password": "admin123",
        "name": "Admin User",
        "role": "Admin",
        "color": "#5B8DEF"
    },
    "accountant": {
        "password": "acc123",
        "name": "Ramesh Kumar",
        "role": "Accountant",
        "color": "#7B9E87"
    },
    "viewer": {
        "password": "view123",
        "name": "Priya Sharma",
        "role": "Viewer",
        "color": "#C4A882"
    },
}

ROLE_ACCESS = {
    "Admin":      ["Dashboard","Upload & Extract","Manual Entry","Purchase Register",
                   "Sales Register","Reconciliation","GSTR-1 Report","GSTR-3B Report",
                   "GSTR-2A / 2B","User Guide"],
    "Accountant": ["Dashboard","Upload & Extract","Manual Entry","Purchase Register",
                   "Sales Register","Reconciliation","GSTR-1 Report","GSTR-3B Report",
                   "GSTR-2A / 2B","User Guide"],
    "Viewer":     ["Dashboard","Purchase Register","Sales Register",
                   "Reconciliation","GSTR-1 Report","GSTR-3B Report","User Guide"],
}

# ── GLOBAL STYLE ──
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg:       #12141A;
    --surface:  #1A1D25;
    --surface2: #20242E;
    --border:   #2A2F3D;
    --text:     #D4D8E2;
    --muted:    #606880;
    --blue:     #5B8DEF;
    --green:    #4EA882;
    --amber:    #C4913A;
    --red:      #C4564A;
    --purple:   #8B7EC8;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
}
.stApp { background: var(--bg); }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 2.5rem 2rem 4rem; max-width: 1300px; }

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="collapsedControl"] { display: none !important; }

/* Buttons — flat, no glow */
.stButton > button {
    background: var(--blue) !important;
    color: #fff !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.4rem !important;
    box-shadow: none !important;
    transition: background 0.15s !important;
}
.stButton > button:hover {
    background: #4a7dd8 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
}
label, .stSelectbox label, .stTextInput label {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 6px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 5px !important;
    border: none !important;
    padding: 0.45rem 1.1rem !important;
    font-size: 0.88rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: var(--text) !important;
}

/* Alerts */
.stSuccess { background: rgba(78,168,130,0.08) !important; border-left: 3px solid var(--green) !important; border-radius: 6px !important; }
.stError   { background: rgba(196,86,74,0.08)  !important; border-left: 3px solid var(--red)   !important; }
.stWarning { background: rgba(196,145,58,0.08) !important; border-left: 3px solid var(--amber) !important; }
.stInfo    { background: rgba(91,141,239,0.08) !important; border-left: 3px solid var(--blue)  !important; }

hr { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }

/* Progress bar */
.stProgress > div > div { background: var(--blue) !important; border-radius: 4px !important; }
.stProgress > div       { background: var(--surface2) !important; border-radius: 4px !important; }

/* Reusable component classes */
.page-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--text);
    margin-bottom: 0.2rem;
}
.page-sub {
    color: var(--muted);
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
}
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.2rem 0 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
}
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.35rem;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--text);
}
.kpi-sub { font-size: 0.75rem; color: var(--muted); margin-top: 0.15rem; }

.info-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-size: 0.85rem;
}
.tag {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    font-weight: 500;
}
.tag-green  { background: rgba(78,168,130,0.12); color: #4EA882; border: 1px solid rgba(78,168,130,0.3); }
.tag-amber  { background: rgba(196,145,58,0.12);  color: #C4913A; border: 1px solid rgba(196,145,58,0.3); }
.tag-red    { background: rgba(196,86,74,0.12);   color: #C4564A; border: 1px solid rgba(196,86,74,0.3); }
.tag-blue   { background: rgba(91,141,239,0.12);  color: #5B8DEF; border: 1px solid rgba(91,141,239,0.3); }
.tag-purple { background: rgba(139,126,200,0.12); color: #8B7EC8; border: 1px solid rgba(139,126,200,0.3); }
</style>
"""

def show_login():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .login-wrap {
        max-width: 400px; margin: 5rem auto 0;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 2.5rem 2rem;
    }
    .login-title {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600; font-size: 1.6rem;
        color: var(--text); text-align: center; margin-bottom: 0.2rem;
    }
    .login-sub {
        text-align: center; color: var(--muted);
        font-size: 0.78rem; margin-bottom: 2rem;
        font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.1em;
    }
    </style>
    """, unsafe_allow_html=True)

    
    st.markdown('<div class="login-title">FinFlow</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">GST REGISTER · SIGN IN</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        if submitted:
            username = username.strip().lower()
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in  = True
                st.session_state.username   = username
                st.session_state.user_name  = USERS[username]["name"]
                st.session_state.user_role  = USERS[username]["role"]
                st.session_state.user_color = USERS[username]["color"]
                st.session_state.page       = "Dashboard"
                st.success(f"Welcome, {USERS[username]['name']}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

   


st.set_page_config(
    page_title="FinFlow · GST Register",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(STYLE, unsafe_allow_html=True)

COLS       = ["ID","Date","Vendor","GSTIN","Category","Subtotal","CGST","SGST","IGST","Total","Status"]
CATEGORIES = ["Goods"]

def init_state():
    defaults = {
        "logged_in": False, "username": "", "user_name": "",
        "user_role": "", "user_color": "#5B8DEF",
        "page": "Dashboard",
        "purchase_register": pd.DataFrame(columns=COLS),
        "sales_register":    pd.DataFrame(columns=COLS),
        "counter": 1, "extracted": None,
        "inv_type_detected": "Purchase Invoice",
        "gstr2a_data": pd.DataFrame(columns=["GSTIN","Vendor","InvoiceNo",
                       "Date","Taxable","CGST","SGST","IGST","Total","Source"]),
        "lang": "English",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

if not st.session_state.logged_in:
    show_login()
    st.stop()

# ── SIDEBAR ──
with st.sidebar:
    role  = st.session_state.user_role
    color = st.session_state.user_color

    # User badge
    st.markdown(f"""
    <div style="padding:0.85rem 1rem; background:var(--surface2);
        border:1px solid var(--border); border-radius:8px; margin-bottom:1rem;">
        <div style="display:flex; align-items:center; gap:0.6rem;">
            <div style="width:32px; height:32px; border-radius:50%;
                background:{color}22; border:1px solid {color}66;
                display:flex; align-items:center; justify-content:center;
                font-weight:600; font-size:0.9rem; color:{color};">
                {st.session_state.user_name[0].upper()}
            </div>
            <div>
                <div style="font-weight:600; font-size:0.85rem; color:var(--text);">
                    {st.session_state.user_name}
                </div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.66rem;
                    color:{color}; text-transform:uppercase; letter-spacing:0.08em;">
                    {role}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Logout", key="logout_btn", use_container_width=True):
        for key in ["logged_in","username","user_name","user_role","user_color"]:
            st.session_state[key] = False if key == "logged_in" else ""
        st.rerun()

    st.markdown("---")

    st.markdown("""
    <div style="padding:0.75rem 0 1.25rem;">
        <div style="font-family:'IBM Plex Sans',sans-serif; font-weight:600;
            font-size:1.5rem; color:var(--text); letter-spacing:-0.5px;">FinFlow</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem;
            color:var(--muted); letter-spacing:0.12em; text-transform:uppercase; margin-top:0.2rem;">
            GST Sales & Purchase Register
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    lang = st.selectbox("Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"],
                        index=0 if st.session_state.lang == "English" else 1,
                        key="lang_select")
    st.session_state.lang = lang

    st.markdown("---")

    KN = {
        "Dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "Upload & Extract": "ಅಪ್‌ಲೋಡ್ & ಓದು",
        "Manual Entry": "ಕೈಯಾರೆ ನಮೂದು",
        "Purchase Register": "ಖರೀದಿ ನೋಂದಣಿ",
        "Sales Register": "ಮಾರಾಟ ನೋಂದಣಿ",
        "Reconciliation": "ತೆರಿಗೆ ಲೆಕ್ಕ",
        "GSTR-1 Report": "GSTR-1 ವರದಿ",
        "GSTR-3B Report": "GSTR-3B ವರದಿ",
        "GSTR-2A / 2B": "GSTR-2A / 2B",
        "User Guide": "ಬಳಕೆದಾರ ಮಾರ್ಗದರ್ಶಿ",
    }
    pages = [
        ("📊", "Dashboard"),
        ("📤", "Upload & Extract"),
        ("✏️", "Manual Entry"),
        ("📋", "Purchase Register"),
        ("💰", "Sales Register"),
        ("🔄", "Reconciliation"),
        ("📄", "GSTR-1 Report"),
        ("📑", "GSTR-3B Report"),
        ("🔍", "GSTR-2A / 2B"),
        ("📖", "User Guide"),
    ]

    allowed = ROLE_ACCESS.get(st.session_state.user_role, [])
    for icon, name in pages:
        if name not in allowed:
            continue
        label = KN.get(name, name) if lang == "ಕನ್ನಡ" else name
        if st.button(f"{icon}  {label}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()

    st.markdown("---")

    # Quick stats
    tx = get_tax_summary()
    net_color = "var(--red)" if tx['net_tax'] > 0 else "var(--green)"
    st.markdown(f"""
    <div style="padding:0.75rem 1rem; background:var(--surface2);
        border:1px solid var(--border); border-radius:8px;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
            color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.6rem;">
            Quick Stats
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
            <span style="color:var(--muted); font-size:0.8rem;">Purchases</span>
            <span style="color:var(--amber); font-family:'IBM Plex Mono',monospace; font-size:0.8rem;">{tx['p_count']}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
            <span style="color:var(--muted); font-size:0.8rem;">Sales</span>
            <span style="color:var(--green); font-family:'IBM Plex Mono',monospace; font-size:0.8rem;">{tx['s_count']}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding-top:0.4rem; border-top:1px solid var(--border);">
            <span style="color:var(--muted); font-size:0.8rem;">Net Tax Due</span>
            <span style="color:{net_color}; font-family:'IBM Plex Mono',monospace; font-size:0.8rem; font-weight:600;">
                ₹{tx['net_tax']:,.0f}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── PAGE ROUTING ──
page = st.session_state.page
allowed = ROLE_ACCESS.get(st.session_state.user_role, [])
if page not in allowed:
    st.session_state.page = "Dashboard"
page = st.session_state.page


# ════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">GST Sales & Purchase Register</div>', unsafe_allow_html=True)

    tx = get_tax_summary()
    c1, c2, c3, c4 = st.columns(4)

    profit    = tx['s_total'] - tx['p_total']
    p_color   = "var(--green)" if profit >= 0 else "var(--red)"
    net_color = "var(--red)"   if tx['net_tax'] > 0 else "var(--green)"
    net_label = "Tax Payable"  if tx['net_tax'] > 0 else "Tax Refund"

    for col, label, val, sub, color in [
        (c1, "Total Purchases", f"₹{tx['p_total']:,.0f}", f"{tx['p_count']} invoices", "var(--text)"),
        (c2, "Total Sales",     f"₹{tx['s_total']:,.0f}", f"{tx['s_count']} invoices", "var(--text)"),
        (c3, "Gross Margin",    f"₹{profit:,.0f}",        "Sales minus Purchases",     p_color),
        (c4, net_label,         f"₹{abs(tx['net_tax']):,.0f}", "Output tax − Input tax", net_color),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color};">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-label">GST Tax Breakdown</div>', unsafe_allow_html=True)
        rows = [
            ("CGST", tx['p_cgst'], tx['s_cgst'], tx['net_cgst']),
            ("SGST", tx['p_sgst'], tx['s_sgst'], tx['net_sgst']),
            ("IGST", tx['p_igst'], tx['s_igst'], tx['net_igst']),
        ]
        header = """
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
            padding:0.5rem 0.75rem; background:var(--surface2); border-radius:6px 6px 0 0;
            border:1px solid var(--border); border-bottom:none;
            font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
            color:var(--muted); text-transform:uppercase; letter-spacing:0.08em;">
            <span></span><span>Purchase</span><span>Sales</span><span>Net</span>
        </div>"""
        body = ""
        for head, pin, sout, net in rows:
            nc = "var(--red)" if net > 0 else "var(--green)"
            body += f"""
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
                padding:0.5rem 0.75rem; border:1px solid var(--border);
                border-top:none; font-size:0.84rem;">
                <span style="color:var(--muted); font-family:'IBM Plex Mono',monospace;">{head}</span>
                <span style="color:var(--amber);">₹{pin:,.2f}</span>
                <span style="color:var(--green);">₹{sout:,.2f}</span>
                <span style="color:{nc}; font-weight:600;">₹{net:,.2f}</span>
            </div>"""
        total_color = "var(--red)" if tx['net_tax'] > 0 else "var(--green)"
        footer = f"""
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
            padding:0.6rem 0.75rem; background:var(--surface2);
            border:1px solid var(--border); border-top:none; border-radius:0 0 6px 6px;
            font-size:0.88rem; font-weight:600;">
            <span>Total</span>
            <span style="color:var(--amber);">₹{tx['p_cgst']+tx['p_sgst']+tx['p_igst']:,.2f}</span>
            <span style="color:var(--green);">₹{tx['s_cgst']+tx['s_sgst']+tx['s_igst']:,.2f}</span>
            <span style="color:{total_color}; font-family:'IBM Plex Mono',monospace;">₹{tx['net_tax']:,.2f}</span>
        </div>"""
        st.markdown(header + body + footer, unsafe_allow_html=True)
        status_txt = "Tax payable to government" if tx['net_tax'] > 0 else "Input credit exceeds output tax"
        st.markdown(f'<div style="font-size:0.75rem; color:var(--muted); margin-top:0.5rem;">{status_txt}</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-label">Sales vs Purchases</div>', unsafe_allow_html=True)
        chart_data = pd.DataFrame({"Amount": [tx['p_total'], tx['s_total']]}, index=["Purchases", "Sales"])
        st.bar_chart(chart_data)
        st.markdown("""
        <div class="info-box" style="margin-top:0.75rem; font-size:0.82rem; color:var(--muted);">
            <b style="color:var(--text);">How net tax is calculated:</b><br>
            Output Tax (on Sales) − Input Tax Credit (on Purchases) = Net GST Payable
        </div>""", unsafe_allow_html=True)

    p = st.session_state.purchase_register
    s = st.session_state.sales_register
    if not p.empty or not s.empty:
        st.markdown('<div class="section-label">Recent Activity</div>', unsafe_allow_html=True)
        combined = pd.concat([
            p.assign(Type="Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Type="Sales")    if not s.empty else pd.DataFrame(),
        ]).sort_values("Date", ascending=False).head(8)
        disp = combined[["ID","Date","Vendor","Type","Total","Status"]].copy()
        disp["Total"] = disp["Total"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-label">GSTR Filing Status</div>', unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)
    has_data = not st.session_state.sales_register.empty or not st.session_state.purchase_register.empty
    for col, label, form, desc in [
        (g1, "GSTR-1",  "Outward Supplies",  "Sales register · File by 11th"),
        (g2, "GSTR-3B", "Summary Return",    "Net tax payable summary"),
        (g3, "GSTR-2A", "Auto-Populated",    "From supplier filings"),
        (g4, "GSTR-2B", "Static ITC",        "Locked ITC statement"),
    ]:
        status_color = "var(--amber)" if has_data else "var(--muted)"
        status_txt   = "Ready to File" if has_data else "No Data"
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div style="font-weight:600; font-size:0.9rem; margin:0.25rem 0;">{form}</div>
            <div style="font-size:0.74rem; color:{status_color}; margin-top:0.2rem;">{status_txt}</div>
            <div style="font-size:0.72rem; color:var(--muted); margin-top:0.15rem;">{desc}</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# UPLOAD & EXTRACT
# ════════════════════════════════════════════════
elif page == "Upload & Extract":
    st.markdown('<div class="page-title">📤 Upload & Extract</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Upload an invoice — OCR reads and auto-detects Purchase or Sales.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        uploaded_file = st.file_uploader("Drop invoice here", type=["pdf","png","jpg","jpeg"])
        if uploaded_file:
            st.success(f"✓ {uploaded_file.name} ({uploaded_file.size//1024} KB)")
            ext = uploaded_file.name.lower().rsplit(".",1)[-1]
            if ext in ("png","jpg","jpeg"):
                st.image(uploaded_file, width=420)
                uploaded_file.seek(0)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Extract Data", use_container_width=True):
                with st.spinner("Reading invoice..."):
                    try:
                        uploaded_file.seek(0)
                        extracted = run_ocr(uploaded_file)
                        if extracted:
                            st.session_state.extracted = extracted
                            st.session_state.inv_type_detected = extracted.get("doc_type","Purchase Invoice")
                            st.success("Extraction complete.")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

            if st.session_state.extracted:
                ext_data = st.session_state.extracted
                conf     = ext_data.get("confidence", 80)
                dtype    = ext_data.get("doc_type","Purchase Invoice")
                is_sales = "Sales" in dtype

                st.markdown('<div class="section-label">Extracted Fields</div>', unsafe_allow_html=True)

                tag_class = "tag-green" if is_sales else "tag-amber"
                tag_text  = "SALES INVOICE → Sales Register" if is_sales else "PURCHASE INVOICE → Purchase Register"
                st.markdown(f'<div style="margin-bottom:0.75rem;"><span class="tag {tag_class}">{tag_text}</span></div>', unsafe_allow_html=True)

                st.progress(conf / 100)

                if not ext_data.get("gstin"):
                    has_tax = (ext_data.get("cgst",0) > 0 or ext_data.get("sgst",0) > 0 or ext_data.get("igst",0) > 0)
                    if has_tax:
                        st.error("No GSTIN but GST charged — illegal. Cannot claim ITC. Request a corrected invoice.")
                    else:
                        st.warning("No GSTIN — Unregistered dealer. ITC cannot be claimed.")

                extracted_df = pd.DataFrame({
                    "Field": ["Vendor / Party", "Invoice Type", "Date", "GSTIN", "Category",
                              "Subtotal", "CGST", "SGST", "IGST", "Total"],
                    "Value": [
                        ext_data.get('vendor', ''),
                        ext_data.get('doc_type', ''),
                        ext_data.get('date', ''),
                        ext_data.get('gstin', '') or "No GSTIN — Unregistered",
                        ext_data.get('category', ''),
                        f"₹{ext_data.get('subtotal', 0):,.2f}",
                        f"₹{ext_data.get('cgst', 0):,.2f}",
                        f"₹{ext_data.get('sgst', 0):,.2f}",
                        f"₹{ext_data.get('igst', 0):,.2f}",
                        f"₹{ext_data.get('total', 0):,.2f}",
                    ]
                })
                st.dataframe(extracted_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown('<div class="section-label">Review & Confirm</div>', unsafe_allow_html=True)
        if st.session_state.extracted:
            ext_data = st.session_state.extracted
            with st.form("confirm_form"):
                vendor   = st.text_input("Vendor / Party Name", value=ext_data.get("vendor",""))
                doc_type = st.selectbox("Invoice Type",
                    ["Purchase Invoice","Sales Invoice","Credit Note","Debit Note","Expense Receipt"],
                    index=0 if "Purchase" in ext_data.get("doc_type","Purchase") else 1)
                txn_date = st.text_input("Date", value=ext_data.get("date",""))
                gstin    = st.text_input("GSTIN", value=ext_data.get("gstin",""))
                category = st.selectbox("Category", CATEGORIES,
                    index=CATEGORIES.index(ext_data["category"]) if ext_data.get("category") in CATEGORIES else 0)
                c1, c2 = st.columns(2)
                with c1:
                    subtotal = st.number_input("Subtotal (₹)", value=float(ext_data.get("subtotal",0)), min_value=0.0, step=0.01)
                    cgst     = st.number_input("CGST (₹)",     value=float(ext_data.get("cgst",0)),     min_value=0.0, step=0.01)
                with c2:
                    sgst  = st.number_input("SGST (₹)", value=float(ext_data.get("sgst",0)), min_value=0.0, step=0.01)
                    igst  = st.number_input("IGST (₹)", value=float(ext_data.get("igst",0)), min_value=0.0, step=0.01)
                total_calc = subtotal + cgst + sgst + igst
                st.markdown(f"""
                <div class="info-box" style="display:flex; justify-content:space-between; margin:0.5rem 0;">
                    <span style="color:var(--muted); font-size:0.85rem;">Calculated Total</span>
                    <span style="font-family:'IBM Plex Mono',monospace; font-weight:600; color:var(--blue);">₹{total_calc:,.2f}</span>
                </div>""", unsafe_allow_html=True)
                submitted = st.form_submit_button("Confirm & Add to Register", use_container_width=True)
                if submitted:
                    data = {"vendor":vendor,"date":txn_date,"gstin":gstin,"category":category,
                            "subtotal":subtotal,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total_calc}
                    txn_id, reg = add_to_register(data, doc_type)
                    st.session_state.extracted = None
                    reg_name = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"{txn_id} added to {reg_name}.")
        else:
            st.markdown("""
            <div class="info-box" style="text-align:center; padding:3rem 2rem; color:var(--muted);">
                Upload a document and click Extract
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# MANUAL ENTRY
# ════════════════════════════════════════════════
elif page == "Manual Entry":
    st.markdown('<div class="page-title">✏️ Manual Entry</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        with st.form("manual_form"):
            doc_type = st.selectbox("Invoice Type",
                ["Purchase Invoice","Sales Invoice","Expense Receipt","Credit Note","Debit Note"])
            vendor   = st.text_input("Vendor / Party Name")
            txn_date = st.date_input("Date", value=date.today())
            gstin    = st.text_input("GSTIN (optional)")
            category = st.selectbox("Category", CATEGORIES)
            c1, c2 = st.columns(2)
            with c1:
                subtotal = st.number_input("Subtotal (₹)", min_value=0.0, value=1000.0, step=1.0)
                cgst_pct = st.number_input("CGST %", min_value=0.0, max_value=28.0, value=9.0, step=0.5)
            with c2:
                sgst_pct = st.number_input("SGST %", min_value=0.0, max_value=28.0, value=9.0, step=0.5)
                igst_pct = st.number_input("IGST %", min_value=0.0, max_value=28.0, value=0.0, step=0.5)
            cgst  = round(subtotal * cgst_pct / 100, 2)
            sgst  = round(subtotal * sgst_pct / 100, 2)
            igst  = round(subtotal * igst_pct / 100, 2)
            total = subtotal + cgst + sgst + igst
            st.markdown(f"""
            <div class="info-box" style="margin:0.5rem 0;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.3rem; font-size:0.84rem; margin-bottom:0.5rem;">
                    <span style="color:var(--muted);">CGST</span><span style="text-align:right; font-family:'IBM Plex Mono',monospace;">₹{cgst:,.2f}</span>
                    <span style="color:var(--muted);">SGST</span><span style="text-align:right; font-family:'IBM Plex Mono',monospace;">₹{sgst:,.2f}</span>
                    <span style="color:var(--muted);">IGST</span><span style="text-align:right; font-family:'IBM Plex Mono',monospace;">₹{igst:,.2f}</span>
                </div>
                <div style="border-top:1px solid var(--border); padding-top:0.4rem;
                    display:flex; justify-content:space-between;">
                    <span style="font-weight:600;">Total</span>
                    <span style="color:var(--blue); font-family:'IBM Plex Mono',monospace; font-weight:600;">₹{total:,.2f}</span>
                </div>
            </div>""", unsafe_allow_html=True)
            submit = st.form_submit_button("Add Entry", use_container_width=True)
            if submit:
                if not vendor:
                    st.error("Vendor name is required.")
                else:
                    data = {"vendor":vendor,"date":txn_date.strftime("%d-%m-%Y"),"gstin":gstin,
                            "category":category,"subtotal":subtotal,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total}
                    txn_id, reg = add_to_register(data, doc_type)
                    reg_name = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"{txn_id} added to {reg_name}.")

    with col2:
        st.markdown('<div class="section-label">Recent Entries</div>', unsafe_allow_html=True)
        p = st.session_state.purchase_register
        s = st.session_state.sales_register
        if not p.empty or not s.empty:
            combined = pd.concat([
                p.assign(Type="Purchase") if not p.empty else pd.DataFrame(),
                s.assign(Type="Sales")    if not s.empty else pd.DataFrame(),
            ]).tail(8)[["ID","Vendor","Type","Total"]].copy()
            combined["Total"] = combined["Total"].apply(lambda x: f"₹{float(x):,.2f}")
            st.dataframe(combined, use_container_width=True, hide_index=True)
        else:
            st.info("No entries yet.")


# ════════════════════════════════════════════════
# PURCHASE REGISTER
# ════════════════════════════════════════════════
elif page == "Purchase Register":
    st.markdown('<div class="page-title">📋 Purchase Register</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">All invoices where you are the buyer — Input Tax Credit (ITC) eligible.</div>', unsafe_allow_html=True)

    df = st.session_state.purchase_register.copy()
    if df.empty:
        st.info("No purchase entries yet. Upload purchase invoices or add manually.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Purchases", f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric("Input CGST (ITC)", f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric("Input SGST (ITC)", f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric("Entries", len(df))
        st.markdown("---")
        search = st.text_input("Search vendor")
        if search:
            df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for col in ["Subtotal","CGST","SGST","IGST","Total"]:
            disp[col] = disp[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button("Export CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"purchase_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ════════════════════════════════════════════════
# SALES REGISTER
# ════════════════════════════════════════════════
elif page == "Sales Register":
    st.markdown('<div class="page-title">💰 Sales Register</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">All invoices where you are the seller — Output Tax collected from customers.</div>', unsafe_allow_html=True)

    df = st.session_state.sales_register.copy()
    if df.empty:
        st.info("No sales entries yet. Upload sales invoices or add manually.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Sales",    f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric("Output CGST",    f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric("Output SGST",    f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric("Entries", len(df))
        st.markdown("---")
        search = st.text_input("Search buyer")
        if search:
            df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for col in ["Subtotal","CGST","SGST","IGST","Total"]:
            disp[col] = disp[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button("Export CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"sales_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ════════════════════════════════════════════════
# RECONCILIATION
# ════════════════════════════════════════════════
elif page == "Reconciliation":
    st.markdown('<div class="page-title">🔄 GST Reconciliation</div>', unsafe_allow_html=True)

    tx = get_tax_summary()
    p  = st.session_state.purchase_register
    s  = st.session_state.sales_register

    if p.empty and s.empty:
        st.info("Add purchase and sales entries to run reconciliation.")
    else:
        st.markdown('<div class="section-label">Full Tax Statement</div>', unsafe_allow_html=True)

        rows = [
            ("CGST", tx['p_cgst'], tx['s_cgst'], tx['net_cgst']),
            ("SGST", tx['p_sgst'], tx['s_sgst'], tx['net_sgst']),
            ("IGST", tx['p_igst'], tx['s_igst'], tx['net_igst']),
        ]
        header = """
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
            padding:0.5rem 0.75rem; background:var(--surface2); border-radius:6px 6px 0 0;
            border:1px solid var(--border); border-bottom:none;
            font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
            color:var(--muted); text-transform:uppercase; letter-spacing:0.08em;">
            <span>Tax Head</span><span>Input (Purchase)</span><span>Output (Sales)</span><span>Net Payable</span>
        </div>"""
        body = ""
        for head, pin, sout, net in rows:
            nc = "var(--red)" if net > 0 else "var(--green)"
            body += f"""
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
                padding:0.5rem 0.75rem; border:1px solid var(--border); border-top:none; font-size:0.84rem;">
                <span style="color:var(--muted); font-family:'IBM Plex Mono',monospace;">{head}</span>
                <span style="color:var(--amber);">₹{pin:,.2f}</span>
                <span style="color:var(--green);">₹{sout:,.2f}</span>
                <span style="color:{nc}; font-weight:600;">₹{net:,.2f}</span>
            </div>"""
        tc = "var(--red)" if tx['net_tax'] > 0 else "var(--green)"
        footer = f"""
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
            padding:0.6rem 0.75rem; background:var(--surface2);
            border:1px solid var(--border); border-top:none; border-radius:0 0 6px 6px;
            font-size:0.88rem; font-weight:600; margin-bottom:1rem;">
            <span>Total</span>
            <span style="color:var(--amber);">₹{tx['p_cgst']+tx['p_sgst']+tx['p_igst']:,.2f}</span>
            <span style="color:var(--green);">₹{tx['s_cgst']+tx['s_sgst']+tx['s_igst']:,.2f}</span>
            <span style="color:{tc}; font-family:'IBM Plex Mono',monospace;">₹{tx['net_tax']:,.2f}</span>
        </div>"""
        st.markdown(header + body + footer, unsafe_allow_html=True)

        if tx['net_tax'] > 0:
            st.warning(f"Net GST Payable to Government: ₹{tx['net_tax']:,.2f}. You owe this amount after adjusting ITC.")
        else:
            st.success(f"Input Tax Credit exceeds Output Tax by ₹{abs(tx['net_tax']):,.2f}. Carry forward to next period.")

        st.markdown('<div class="section-label">GSTIN Validation</div>', unsafe_allow_html=True)
        all_df = pd.concat([
            p.assign(Register="Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Register="Sales")    if not s.empty else pd.DataFrame(),
        ])
        g = all_df[["ID","Vendor","GSTIN","Register"]].copy()
        def check_gstin(x):
            if not x or str(x).strip() == "" or str(x) == "nan":
                return "No GSTIN — Unregistered"
            elif re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]$', str(x)):
                return "Valid"
            else:
                return "Invalid Format"
        g["Status"] = g["GSTIN"].apply(check_gstin)
        st.dataframe(g, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════
# GSTR-1 REPORT
# ════════════════════════════════════════════════
elif page == "GSTR-1 Report":
    st.markdown('<div class="page-title">GSTR-1 — Statement of Outward Supplies</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Filed by 11th of the following month. B2B invoices auto-appear in buyer\'s GSTR-2A.</div>', unsafe_allow_html=True)

    s_df = st.session_state.sales_register

    if s_df.empty:
        st.info("No sales data. Add sales invoices to generate GSTR-1.")
    else:
        summary, b2b_df, b2c_df = build_gstr1(s_df)

        k1, k2, k3, k4, k5 = st.columns(5)
        for col, label, val, sub in [
            (k1, "Taxable Turnover",    f"₹{summary['total_taxable']:,.2f}", ""),
            (k2, "Total CGST",          f"₹{summary['total_cgst']:,.2f}",    ""),
            (k3, "Total SGST",          f"₹{summary['total_sgst']:,.2f}",    ""),
            (k4, "Total IGST",          f"₹{summary['total_igst']:,.2f}",    ""),
            (k5, "Grand Total",         f"₹{summary['grand_total']:,.2f}",   f"{len(s_df)} invoices"),
        ]:
            col.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="font-size:1.1rem;">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["B2B Invoices", "B2C Invoices", "HSN Summary", "Full Table"])

        with tab1:
            st.caption("B2B invoices (with GSTIN) — auto-appear in buyer's GSTR-2A.")
            if b2b_df.empty:
                st.info("No B2B invoices (no entries with GSTIN).")
            else:
                disp = b2b_df[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
                st.dataframe(disp, use_container_width=True, hide_index=True)

        with tab2:
            st.caption("B2C invoices (no GSTIN) — buyer cannot claim ITC.")
            if b2c_df.empty:
                st.info("No B2C invoices.")
            else:
                disp = b2c_df[["ID","Date","Vendor","Category","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
                st.dataframe(disp, use_container_width=True, hide_index=True)

        with tab3:
            st.caption("Category-wise summary (proxy for HSN/SAC grouping).")
            hsn = s_df.groupby("Category").agg(
                Invoices=("ID","count"),
                Taxable=("Subtotal",  lambda x: x.astype(float).sum()),
                CGST=   ("CGST",      lambda x: x.astype(float).sum()),
                SGST=   ("SGST",      lambda x: x.astype(float).sum()),
                IGST=   ("IGST",      lambda x: x.astype(float).sum()),
                Total=  ("Total",     lambda x: x.astype(float).sum()),
            ).reset_index()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: hsn[c] = hsn[c].apply(fmt_inr)
            st.dataframe(hsn, use_container_width=True, hide_index=True)

        with tab4:
            disp = s_df.copy()
            for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("Download GSTR-1 CSV",
            data=s_df.to_csv(index=False).encode(),
            file_name=f"GSTR1_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# GSTR-3B REPORT
# ════════════════════════════════════════════════
elif page == "GSTR-3B Report":
    st.markdown('<div class="page-title">GSTR-3B — Monthly Summary Return</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Filed by 20th of the following month. Output tax − ITC = Net tax payable.</div>', unsafe_allow_html=True)
    st.info("GSTR-3B is a self-declaration. Interest at 18% p.a. applies on late payment.")

    s_df = st.session_state.sales_register
    p_df = st.session_state.purchase_register

    if s_df.empty and p_df.empty:
        st.info("Add sales and purchase entries to generate GSTR-3B.")
    else:
        data = build_gstr3b(s_df, p_df)
        tab1, tab2, tab3 = st.tabs(["3.1 Output Tax", "4. ITC Available", "Net Tax Payable"])

        def tax_grid(title, rows, totals):
            header = f"""
            <div style="font-weight:600; font-size:0.9rem; margin-bottom:0.75rem; color:var(--text);">{title}</div>
            <div style="display:grid; grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;
                padding:0.5rem 0.75rem; background:var(--surface2); border-radius:6px 6px 0 0;
                border:1px solid var(--border); border-bottom:none;
                font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
                color:var(--muted); text-transform:uppercase; letter-spacing:0.08em;">
                <span>Sec</span><span>Nature</span><span>Taxable</span><span>CGST</span><span>SGST</span><span>IGST</span>
            </div>"""
            body = "".join([
                f'<div style="display:grid; grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;'
                f'padding:0.5rem 0.75rem; border:1px solid var(--border); border-top:none; font-size:0.82rem;">'
                f'<span style="font-family:\'IBM Plex Mono\',monospace; color:var(--muted); font-size:0.72rem;">{r[0]}</span>'
                f'<span>{r[1]}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(r[2])}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(r[3])}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(r[4])}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(r[5])}</span>'
                f'</div>'
                for r in rows
            ])
            footer = (
                f'<div style="display:grid; grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;'
                f'padding:0.6rem 0.75rem; background:var(--surface2); font-weight:600;'
                f'border:1px solid var(--border); border-top:none; border-radius:0 0 6px 6px; font-size:0.84rem;">'
                f'<span></span><span>{totals[0]}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(totals[1])}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(totals[2])}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(totals[3])}</span>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;">{fmt_inr(totals[4])}</span>'
                f'</div>'
            )
            return header + body + footer

        with tab1:
            rows = [
                ("3.1(a)", "Outward taxable supplies", data["out_taxable"], data["out_cgst"], data["out_sgst"], data["out_igst"]),
                ("3.1(b)", "Zero-rated supplies",      0, 0, 0, 0),
                ("3.1(c)", "Nil / exempt supplies",    0, 0, 0, 0),
            ]
            st.markdown(tax_grid(
                "Table 3.1 — Outward Supplies & Tax Liability", rows,
                ("Total Output Tax", data["out_taxable"], data["out_cgst"], data["out_sgst"], data["out_igst"])
            ), unsafe_allow_html=True)

        with tab2:
            itc_rows = [
                ("4(A)(1)", "ITC on Imports of goods",        0, 0, 0, 0),
                ("4(A)(2)", "ITC on Imports of services",     0, 0, 0, 0),
                ("4(A)(5)", "All other ITC (domestic purchases)", data["itc_taxable"], data["itc_cgst"], data["itc_sgst"], data["itc_igst"]),
            ]
            st.markdown(tax_grid(
                "Table 4 — Eligible Input Tax Credit (ITC)", itc_rows,
                ("Total ITC Available", data["itc_taxable"], data["itc_cgst"], data["itc_sgst"], data["itc_igst"])
            ), unsafe_allow_html=True)

        with tab3:
            nc = "var(--red)" if data["net_cgst"]  > 0 else "var(--green)"
            ns = "var(--red)" if data["net_sgst"]  > 0 else "var(--green)"
            ni = "var(--red)" if data["net_igst"]  > 0 else "var(--green)"
            nt = "var(--red)" if data["net_total"] > 0 else "var(--green)"
            st.markdown(f"""
            <div style="font-weight:600; font-size:0.9rem; margin-bottom:0.75rem; color:var(--text);">
                Table 6.1 — Payment of Tax (Net Liability)
            </div>
            <div style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr 1fr;
                padding:0.5rem 0.75rem; background:var(--surface2); border-radius:6px 6px 0 0;
                border:1px solid var(--border); border-bottom:none;
                font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
                color:var(--muted); text-transform:uppercase; letter-spacing:0.08em;">
                <span>Description</span><span>CGST</span><span>SGST</span><span>IGST</span><span>Total</span>
            </div>
            <div style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr 1fr;
                padding:0.5rem 0.75rem; border:1px solid var(--border); border-top:none; font-size:0.84rem;">
                <span>Output Tax Liability</span>
                <span style="color:var(--red); font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['out_cgst'])}</span>
                <span style="color:var(--red); font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['out_sgst'])}</span>
                <span style="color:var(--red); font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['out_igst'])}</span>
                <span style="color:var(--red); font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['out_cgst']+data['out_sgst']+data['out_igst'])}</span>
            </div>
            <div style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr 1fr;
                padding:0.5rem 0.75rem; border:1px solid var(--border); border-top:none; font-size:0.84rem;">
                <span>Less: ITC Available</span>
                <span style="color:var(--green); font-family:'IBM Plex Mono',monospace;">(−) {fmt_inr(data['itc_cgst'])}</span>
                <span style="color:var(--green); font-family:'IBM Plex Mono',monospace;">(−) {fmt_inr(data['itc_sgst'])}</span>
                <span style="color:var(--green); font-family:'IBM Plex Mono',monospace;">(−) {fmt_inr(data['itc_igst'])}</span>
                <span style="color:var(--green); font-family:'IBM Plex Mono',monospace;">(−) {fmt_inr(data['itc_cgst']+data['itc_sgst']+data['itc_igst'])}</span>
            </div>
            <div style="display:grid; grid-template-columns:2fr 1fr 1fr 1fr 1fr;
                padding:0.7rem 0.75rem; background:var(--surface2); font-weight:700;
                border:1px solid var(--border); border-top:none; border-radius:0 0 6px 6px; font-size:0.9rem;
                margin-bottom:1rem;">
                <span>NET TAX PAYABLE</span>
                <span style="color:{nc}; font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['net_cgst'])}</span>
                <span style="color:{ns}; font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['net_sgst'])}</span>
                <span style="color:{ni}; font-family:'IBM Plex Mono',monospace;">{fmt_inr(data['net_igst'])}</span>
                <span style="color:{nt}; font-family:'IBM Plex Mono',monospace; font-size:1rem;">{fmt_inr(data['net_total'])}</span>
            </div>
            """, unsafe_allow_html=True)

            if data['net_total'] > 0:
                st.warning(f"You owe ₹{data['net_total']:,.2f} in GST. Pay via GSTN portal by 20th of next month. Late payment: 18% p.a. + ₹50/day.")
            else:
                st.success(f"Excess ITC of ₹{abs(data['net_total']):,.2f} — carry forward to next period.")

        gstr3b_export = pd.DataFrame([
            {"Section":"3.1(a)", "Description":"Outward Taxable Supplies",   "Taxable":data['out_taxable'], "CGST":data['out_cgst'], "SGST":data['out_sgst'], "IGST":data['out_igst']},
            {"Section":"4(A)(5)","Description":"ITC on Domestic Purchases",  "Taxable":data['itc_taxable'], "CGST":data['itc_cgst'], "SGST":data['itc_sgst'], "IGST":data['itc_igst']},
            {"Section":"6.1",    "Description":"Net Tax Payable",            "Taxable":data['out_taxable']-data['itc_taxable'], "CGST":data['net_cgst'], "SGST":data['net_sgst'], "IGST":data['net_igst']},
        ])
        st.download_button("Download GSTR-3B CSV",
            data=gstr3b_export.to_csv(index=False).encode(),
            file_name=f"GSTR3B_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# GSTR-2A / GSTR-2B
# ════════════════════════════════════════════════
elif page == "GSTR-2A / 2B":
    st.markdown('<div class="page-title">GSTR-2A / 2B — Inward Supplies ITC Statement</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Auto-populated from your suppliers\' GSTR-1 filings.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.markdown("""
    <div class="info-box">
        <div style="font-weight:600; color:var(--blue); margin-bottom:0.3rem;">GSTR-2A — Dynamic</div>
        <div style="font-size:0.82rem; color:var(--muted);">Auto-populated in real-time as suppliers file GSTR-1. Changes when suppliers amend or file late.</div>
    </div>""", unsafe_allow_html=True)
    col2.markdown("""
    <div class="info-box">
        <div style="font-weight:600; color:var(--purple); margin-bottom:0.3rem;">GSTR-2B — Static / Locked</div>
        <div style="font-size:0.82rem; color:var(--muted);">Locked snapshot of ITC available for a specific return period. Use this to claim ITC in GSTR-3B.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    p_df = st.session_state.purchase_register
    tab1, tab2, tab3, tab4 = st.tabs(["GSTR-2A Data", "GSTR-2B (Static)", "Reconciliation", "Add 2A Entry"])

    with tab4:
        st.caption("Simulate supplier-filed entries (in production this pulls from GSTN API).")
        with st.form("add_2a_form"):
            c1, c2 = st.columns(2)
            with c1:
                s_gstin  = st.text_input("Supplier GSTIN")
                s_vendor = st.text_input("Supplier Name")
                s_inv_no = st.text_input("Invoice Number")
                s_date   = st.date_input("Invoice Date", value=date.today())
            with c2:
                s_taxable = st.number_input("Taxable Value (₹)", min_value=0.0, value=1000.0, step=1.0)
                s_cgst    = st.number_input("CGST (₹)", min_value=0.0, value=90.0, step=0.01)
                s_sgst    = st.number_input("SGST (₹)", min_value=0.0, value=90.0, step=0.01)
                s_igst    = st.number_input("IGST (₹)", min_value=0.0, value=0.0,  step=0.01)
            s_total = s_taxable + s_cgst + s_sgst + s_igst
            st.markdown(f"**Total: {fmt_inr(s_total)}**")
            if st.form_submit_button("Add to GSTR-2A", use_container_width=True):
                new_row = {"GSTIN":s_gstin,"Vendor":s_vendor,"InvoiceNo":s_inv_no,
                           "Date":s_date.strftime("%d-%m-%Y"),"Taxable":s_taxable,
                           "CGST":s_cgst,"SGST":s_sgst,"IGST":s_igst,"Total":s_total,
                           "Source":"GSTR-2A (Supplier Filed)"}
                st.session_state.gstr2a_data = pd.concat(
                    [st.session_state.gstr2a_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Entry from {s_vendor} added to GSTR-2A.")
                st.rerun()

    gstr2a_df, gstr2b_df, recon_df = build_gstr2a_2b(p_df, st.session_state.gstr2a_data)

    with tab1:
        if st.session_state.gstr2a_data.empty:
            st.info('No GSTR-2A entries. Go to "Add 2A Entry" tab to simulate supplier data.')
        else:
            total_itc = (st.session_state.gstr2a_data["CGST"].astype(float).sum()
                        + st.session_state.gstr2a_data["SGST"].astype(float).sum()
                        + st.session_state.gstr2a_data["IGST"].astype(float).sum())
            k1, k2, k3 = st.columns(3)
            k1.metric("Suppliers Filed",      st.session_state.gstr2a_data['GSTIN'].nunique())
            k2.metric("Total Invoices (2A)",  len(st.session_state.gstr2a_data))
            k3.metric("ITC Available (2A)",   fmt_inr(total_itc))
            disp = st.session_state.gstr2a_data.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.download_button("Download GSTR-2A CSV",
                data=st.session_state.gstr2a_data.to_csv(index=False).encode(),
                file_name=f"GSTR2A_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

    with tab2:
        if gstr2b_df.empty:
            st.info('GSTR-2B is generated after 2A data is available. Add entries in "Add 2A Entry" first.')
        else:
            itc_total = (gstr2b_df["CGST"].astype(float).sum() + gstr2b_df["SGST"].astype(float).sum()
                        + gstr2b_df["IGST"].astype(float).sum())
            st.info(f"GSTR-2B snapshot — Locked ITC claimable in GSTR-3B: {fmt_inr(itc_total)}")
            disp = gstr2b_df.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.download_button("Download GSTR-2B CSV",
                data=gstr2b_df.to_csv(index=False).encode(),
                file_name=f"GSTR2B_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

    with tab3:
        st.caption("Match your Purchase Register vs GSTR-2A to identify claimable ITC.")
        if p_df.empty:
            st.info("No purchase entries to reconcile.")
        elif recon_df.empty:
            st.info("Add 2A entries and purchase invoices to reconcile.")
        else:
            matched   = len(recon_df[recon_df["Status"] == "✅ Matched"])
            mismatch  = len(recon_df[recon_df["Status"] == "❌ Amount Mismatch"])
            not_in_2a = len(recon_df[recon_df["Status"] == "⚠️ Not in GSTR-2A"])
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Invoices", len(recon_df))
            k2.metric("Matched",        matched)
            k3.metric("Mismatch",       mismatch)
            k4.metric("Not in 2A",      not_in_2a)
            disp = recon_df.copy()
            for c in ["Your CGST","Your IGST","2A CGST","2A IGST"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.markdown("""
            <div class="info-box" style="margin-top:0.75rem; font-size:0.82rem; line-height:1.8; color:var(--muted);">
                <b style="color:var(--text);">Action Guide</b><br>
                <b style="color:var(--green);">Matched</b> — Claim ITC in GSTR-3B Table 4.<br>
                <b style="color:var(--red);">Amount Mismatch</b> — Contact supplier to amend GSTR-1, or reverse ITC.<br>
                <b style="color:var(--amber);">Not in GSTR-2A</b> — Supplier hasn't filed. Follow up before claiming ITC.
            </div>""", unsafe_allow_html=True)
            st.download_button("Download Reconciliation CSV",
                data=recon_df.to_csv(index=False).encode(),
                file_name=f"GSTR2A_Recon_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# USER GUIDE
# ════════════════════════════════════════════════
elif page == "User Guide":
    lang  = st.session_state.get("lang", "English")
    is_kn = lang == "ಕನ್ನಡ"

    st.markdown(f'<div class="page-title">{"FinFlow ಮಾರ್ಗದರ್ಶಿ" if is_kn else "📖 User Guide"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{"ಈ ಅಪ್ಲಿಕೇಶನ್ ಅನ್ನು ಹೇಗೆ ಬಳಸಬೇಕು ಎಂಬ ಸಂಪೂರ್ಣ ಮಾಹಿತಿ" if is_kn else "Complete guide on how to use FinFlow — step by step"}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-label">{"ಅಪ್ಲಿಕೇಶನ್ ಕಾರ್ಯ ವಿಧಾನ" if is_kn else "How FinFlow Works"}</div>', unsafe_allow_html=True)

    flow_items = [
        ("🧾", "Invoice",   "Upload PDF/Image"),
        ("🤖", "OCR Reads", "AI extracts data"),
        ("🔀", "Auto Sort", "Purchase or Sales"),
        ("📊", "Dashboard", "Live GST total"),
        ("🏛️", "File GST",  "GSTR-1 / 3B ready"),
    ]
    cols = st.columns(len(flow_items))
    for col, (icon, title, desc) in zip(cols, flow_items):
        col.markdown(f"""
        <div class="info-box" style="text-align:center; padding:1rem 0.75rem;">
            <div style="font-size:1.6rem; margin-bottom:0.4rem;">{icon}</div>
            <div style="font-weight:600; font-size:0.85rem; color:var(--text); margin-bottom:0.2rem;">{title}</div>
            <div style="font-size:0.74rem; color:var(--muted);">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="section-label">{"ಹಂತ ಹಂತವಾಗಿ ಬಳಸಿ" if is_kn else "Step-by-Step Instructions"}</div>', unsafe_allow_html=True)

    steps_en = [
        ("1", "Upload Invoice",      "Go to Upload & Extract → Select your bill (PDF or photo) → Click Extract Data"),
        ("2", "Review & Confirm",    "Check vendor name, amount, CGST/SGST → Fix errors → Click Confirm & Add to Register"),
        ("3", "Check Registers",     "Go to Purchase Register (bills you paid) or Sales Register (bills you raised)"),
        ("4", "See Dashboard",       "Dashboard shows total purchases, sales, and net GST owed to government"),
        ("5", "GST Reports",         "GSTR-1 for sales report · GSTR-3B for net tax → Download CSV → File on GST portal"),
        ("6", "Reconciliation",      "Check GSTIN validity · Identify unregistered dealers"),
    ]
    steps_kn = [
        ("1", "ಬಿಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",       "Upload & Extract ಗೆ ಹೋಗಿ → ನಿಮ್ಮ ಬಿಲ್ ಆಯ್ಕೆ ಮಾಡಿ → Extract Data ಕ್ಲಿಕ್ ಮಾಡಿ"),
        ("2", "ಪರಿಶೀಲಿಸಿ ದೃಢಪಡಿಸಿ",         "ಹೆಸರು, ಮೊತ್ತ, CGST/SGST ಸರಿಯಾಗಿದೆಯೇ ನೋಡಿ → Confirm ಕ್ಲಿಕ್ ಮಾಡಿ"),
        ("3", "ನೋಂದಣಿ ನೋಡಿ",               "Purchase Register ಅಥವಾ Sales Register ತೆರೆಯಿರಿ"),
        ("4", "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ನೋಡಿ",          "Dashboard ನಲ್ಲಿ ಒಟ್ಟು ಖರೀದಿ, ಮಾರಾಟ ಮತ್ತು ನಿವ್ವಳ GST ತಿಳಿಯುತ್ತದೆ"),
        ("5", "GST ವರದಿ",                  "GSTR-1 (ಮಾರಾಟ ವರದಿ) ಅಥವಾ GSTR-3B → CSV ಡೌನ್‌ಲೋಡ್ → GST ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಸಲ್ಲಿಸಿ"),
        ("6", "ಹೊಂದಾಣಿಕೆ",                "GSTIN ಸರಿಯಾಗಿದೆಯೇ ಪರಿಶೀಲಿಸಿ · ಅನೋಂದಿತ ವ್ಯಾಪಾರಿಗಳನ್ನು ಗುರುತಿಸಿ"),
    ]
    steps = steps_kn if is_kn else steps_en
    for num, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex; gap:1rem; margin-bottom:0.75rem; padding:0.9rem 1rem;
            background:var(--surface); border:1px solid var(--border); border-radius:8px;">
            <div style="min-width:28px; height:28px; border-radius:50%; background:var(--surface2);
                border:1px solid var(--border); display:flex; align-items:center; justify-content:center;
                font-family:'IBM Plex Mono',monospace; font-size:0.8rem; color:var(--muted); flex-shrink:0;">
                {num}
            </div>
            <div>
                <div style="font-weight:600; font-size:0.88rem; color:var(--text); margin-bottom:0.2rem;">{title}</div>
                <div style="font-size:0.82rem; color:var(--muted);">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="section-label">{"ITC ನಿಯಮಗಳು" if is_kn else "ITC Rules — When Can You Claim?"}</div>', unsafe_allow_html=True)
    itc_col1, itc_col2 = st.columns(2)
    itc_col1.markdown(f"""
    <div class="info-box">
        <div style="font-weight:600; color:var(--green); margin-bottom:0.5rem;">{"ITC ಕ್ಲೇಮ್ ಮಾಡಬಹುದು" if is_kn else "ITC Can Be Claimed"}</div>
        <div style="font-size:0.84rem; color:var(--muted); line-height:1.9;">
            {"✔ ವ್ಯಾಪಾರಿಯ GSTIN ಇದೆ<br>✔ ಅವರು GSTR-1 ಸಲ್ಲಿಸಿದ್ದಾರೆ<br>✔ ಬಿಲ್‌ನಲ್ಲಿ GST ಮೊತ್ತ ಇದೆ<br>✔ GSTR-2A ನಲ್ಲಿ ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತದೆ"
            if is_kn else
            "✔ Supplier has a valid GSTIN<br>✔ They have filed their GSTR-1<br>✔ Invoice shows GST amount<br>✔ Appears in your GSTR-2A"}
        </div>
    </div>""", unsafe_allow_html=True)
    itc_col2.markdown(f"""
    <div class="info-box">
        <div style="font-weight:600; color:var(--red); margin-bottom:0.5rem;">{"ITC ಕ್ಲೇಮ್ ಮಾಡಲಾಗಲ್ಲ" if is_kn else "ITC Cannot Be Claimed"}</div>
        <div style="font-size:0.84rem; color:var(--muted); line-height:1.9;">
            {"✘ ವ್ಯಾಪಾರಿಗೆ GSTIN ಇಲ್ಲ<br>✘ Composition Scheme ನಲ್ಲಿದ್ದಾರೆ<br>✘ GSTIN ಇಲ್ಲದೇ ತೆರಿಗೆ ಸಂಗ್ರಹಿಸಿದ್ದಾರೆ<br>✘ GSTR-1 ಸಲ್ಲಿಸಿಲ್ಲ"
            if is_kn else
            "✘ Supplier has NO GSTIN<br>✘ Supplier is on Composition Scheme<br>✘ Tax charged without GSTIN — ILLEGAL<br>✘ Supplier hasn't filed GSTR-1"}
        </div>
    </div>""", unsafe_allow_html=True)

    st.warning("A supplier without a GSTIN cannot legally collect GST. You cannot claim ITC on such purchases." if not is_kn else
               "GSTIN ಇಲ್ಲದ ವ್ಯಾಪಾರಿ GST ಸಂಗ್ರಹಿಸುವ ಹಕ್ಕು ಹೊಂದಿಲ್ಲ. ಅಂಥ ಖರೀದಿಗೆ ITC ಸಿಗಲ್ಲ.")

    st.markdown(f'<div class="section-label">{"ಸಾಮಾನ್ಯ ಪ್ರಶ್ನೆಗಳು" if is_kn else "Frequently Asked Questions"}</div>', unsafe_allow_html=True)

    faqs_en = [
        ("What is ITC?", "Input Tax Credit means the GST you paid on purchases can be deducted from the GST you collected on sales. You only pay the difference to the government."),
        ("My supplier has no GSTIN — can I claim ITC?", "No. Unregistered dealers cannot legally charge GST. You cannot claim ITC on that purchase. Ask them to remove GST from the bill."),
        ("What is Composition Scheme?", "Small businesses under ₹1.5 crore turnover can opt for Composition Scheme. They pay a flat low rate but cannot collect GST from buyers and cannot give ITC."),
        ("What if OCR reads the wrong amount?", "You can manually correct any field in the Review & Confirm section before saving. Always double-check extracted data."),
        ("How often should I file GST?", "GSTR-1 by 11th of next month. GSTR-3B by 20th of next month. Late filing: ₹50/day penalty + 18% annual interest."),
    ]
    faqs_kn = [
        ("ITC ಎಂದರೇನು?", "Input Tax Credit ಎಂದರೆ ನೀವು ಖರೀದಿಗೆ ಕೊಟ್ಟ GST ಅನ್ನು ಮಾರಾಟದ GST ನಿಂದ ಕಳೆಯಬಹುದು. ಉಳಿದ ಮೊತ್ತ ಮಾತ್ರ ಸರ್ಕಾರಕ್ಕೆ ಕೊಡಿ."),
        ("ವ್ಯಾಪಾರಿಗೆ GSTIN ಇಲ್ಲ — ITC ಸಿಗುತ್ತದೆಯೇ?", "ಇಲ್ಲ. GSTIN ಇಲ್ಲದ ವ್ಯಾಪಾರಿ GST ಸಂಗ್ರಹಿಸಲು ಅನುಮತಿ ಇಲ್ಲ. ITC ಸಿಗಲ್ಲ."),
        ("Composition Scheme ಎಂದರೇನು?", "₹1.5 ಕೋಟಿಗಿಂತ ಕಡಿಮೆ ವಹಿವಾಟಿನ ಸಣ್ಣ ವ್ಯಾಪಾರಿಗಳು ಈ ಯೋಜನೆ ಆಯ್ಕೆ ಮಾಡಬಹುದು. ಅವರು GST ಸಂಗ್ರಹಿಸಲು ಅಥವಾ ITC ಕೊಡಲು ಅನುಮತಿ ಇಲ್ಲ."),
        ("OCR ತಪ್ಪಾಗಿ ಓದಿದರೆ?", "Review & Confirm ವಿಭಾಗದಲ್ಲಿ ನೀವು ಯಾವ ಮಾಹಿತಿಯನ್ನೂ ಸರಿಪಡಿಸಬಹುದು."),
        ("GST ಎಷ್ಟು ಬಾರಿ ಸಲ್ಲಿಸಬೇಕು?", "GSTR-1 — 11ನೇ ತಾರೀಕು. GSTR-3B — 20ನೇ ತಾರೀಕು. ತಡವಾದರೆ ₹50/ದಿನ ದಂಡ + 18% ಬಡ್ಡಿ."),
    ]
    faqs = faqs_kn if is_kn else faqs_en
    for q, a in faqs:
        with st.expander(q):
            st.markdown(f'<div style="color:var(--muted); font-size:0.86rem; line-height:1.7;">{a}</div>', unsafe_allow_html=True)