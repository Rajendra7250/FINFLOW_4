import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
from backend import *

st.set_page_config(
    page_title="FinFlow · GST Register",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');
:root {
    --bg:#0A0C10; --surface:#111318; --surface2:#181C24; --border:#1E2330;
    --accent:#00E5A0; --accent2:#7B61FF; --text:#E8ECF4; --muted:#5A6075;
    --success:#00E5A0; --warning:#FFB547; --danger:#FF6B6B;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);}
.stApp{background:var(--bg);}
#MainMenu,footer{visibility:hidden;}
.block-container{padding:3.5rem 2.5rem 4rem;max-width:1400px;}
[data-testid="stSidebar"]{
    background:var(--surface) !important;
    border-right:1px solid var(--border);
}
/* Always keep sidebar visible even if user tried to collapse it */
[data-testid="stSidebar"][aria-expanded="false"]{
    margin-left:0 !important;
    visibility:visible !important;
}
/* Hide the collapse/expand hamburger so users can't accidentally close it */
[data-testid="collapsedControl"]{
    display:none !important;
}
.finflow-logo{font-family:'Syne',sans-serif;font-weight:800;font-size:2.2rem;letter-spacing:-1px;
    background:linear-gradient(135deg,#00E5A0 0%,#7B61FF 100%);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;line-height:1;}
.finflow-tagline{font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--muted);
    letter-spacing:0.15em;text-transform:uppercase;margin-top:0.3rem;}
.section-header{font-family:'Syne',sans-serif;font-weight:700;font-size:1.2rem;color:var(--text);
    margin:1.5rem 0 1rem;display:flex;align-items:center;gap:0.6rem;}
.section-header::after{content:'';flex:1;height:1px;background:var(--border);}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;
    padding:1.2rem 1.5rem;position:relative;overflow:hidden;}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--accent),var(--accent2));}
.kpi-label{font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--muted);
    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;}
.kpi-value{font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:700;color:var(--text);}
.kpi-sub{font-size:0.75rem;color:var(--muted);margin-top:0.2rem;}
.tax-box{border-radius:12px;padding:1.5rem;margin:0.5rem 0;}
.tax-row{display:flex;justify-content:space-between;padding:0.5rem 0;
    border-bottom:1px solid rgba(255,255,255,0.06);font-size:0.88rem;}
.tax-row:last-child{border-bottom:none;}
.extracted-card{background:var(--surface2);border:1px solid var(--border);
    border-radius:12px;padding:1.5rem;margin-top:1rem;}
.extracted-field{display:flex;justify-content:space-between;align-items:center;
    padding:0.5rem 0;border-bottom:1px solid var(--border);font-size:0.88rem;}
.extracted-field:last-child{border-bottom:none;}
.field-key{color:var(--muted);font-family:'DM Mono',monospace;font-size:0.78rem;}
.field-val{color:var(--accent);font-weight:500;}
.stButton>button{background:linear-gradient(135deg,#00E5A0,#00C88A) !important;
    color:#0A0C10 !important;font-family:'Syne',sans-serif !important;font-weight:700 !important;
    border:none !important;border-radius:8px !important;padding:0.6rem 1.6rem !important;
    box-shadow:0 4px 15px rgba(0,229,160,0.2) !important;transition:all 0.2s !important;}
.stButton>button:hover{transform:translateY(-1px) !important;box-shadow:0 6px 20px rgba(0,229,160,0.35) !important;}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div,.stTextArea>div>textarea{
    background:var(--surface2) !important;border:1px solid var(--border) !important;
    border-radius:8px !important;color:var(--text) !important;}
label,.stSelectbox label,.stTextInput label{color:var(--muted) !important;font-size:0.78rem !important;
    font-family:'DM Mono',monospace !important;text-transform:uppercase !important;letter-spacing:0.1em !important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface) !important;border-radius:10px !important;
    padding:4px !important;gap:4px !important;border:1px solid var(--border) !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:var(--muted) !important;
    font-family:'Syne',sans-serif !important;font-weight:600 !important;border-radius:7px !important;
    border:none !important;padding:0.5rem 1.2rem !important;}
.stTabs [aria-selected="true"]{background:var(--surface2) !important;color:var(--accent) !important;
    border:1px solid var(--border) !important;}
[data-testid="stMetric"]{background:var(--surface) !important;border:1px solid var(--border) !important;
    border-radius:10px !important;padding:1rem !important;}
[data-testid="stMetricValue"]{font-family:'Syne',sans-serif !important;color:var(--text) !important;}
.stSuccess{background:rgba(0,229,160,0.08) !important;border-left:3px solid var(--success) !important;border-radius:8px !important;}
.stError{background:rgba(255,107,107,0.08) !important;border-left:3px solid var(--danger) !important;}
.stWarning{background:rgba(255,181,71,0.08) !important;border-left:3px solid var(--warning) !important;}
hr{border:none;border-top:1px solid var(--border);margin:1.5rem 0;}
.stProgress>div>div{background:linear-gradient(90deg,var(--accent),var(--accent2)) !important;border-radius:100px !important;}
.stProgress>div{background:var(--surface2) !important;border-radius:100px !important;}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──
COLS = ["ID","Date","Vendor","GSTIN","Category","Subtotal","CGST","SGST","IGST","Total","Status"]
CATEGORIES = ["none"]

# ── SESSION STATE ──
def init_state():
    defaults = {
        "page": "Dashboard",
        "purchase_register": pd.DataFrame(columns=COLS),
        "sales_register":    pd.DataFrame(columns=COLS),
        "counter": 1,
        "extracted": None,
        "inv_type_detected": "Purchase Invoice",
        "gstr2a_data": pd.DataFrame(columns=["GSTIN","Vendor","InvoiceNo","Date","Taxable","CGST","SGST","IGST","Total","Source"]),
        "lang": "English",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem;">
        <div class="finflow-logo">FinFlow</div>
        <div class="finflow-tagline">GST Sales & Purchase Register</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Language toggle
    lang = st.selectbox("🌐 Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"],
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
        ("📊","Dashboard"),
        ("📤","Upload & Extract"),
        ("✏️","Manual Entry"),
        ("📋","Purchase Register"),
        ("💰","Sales Register"),
        ("🔄","Reconciliation"),
        ("📄","GSTR-1 Report"),
        ("📑","GSTR-3B Report"),
        ("🔍","GSTR-2A / 2B"),
        ("📖","User Guide"),
    ]
    for icon, name in pages:
        label = KN.get(name, name) if lang == "ಕನ್ನಡ" else name
        if st.button(f"{icon}  {label}", key=f"nav_{name}", use_container_width=True):
            st.session_state.page = name
            st.rerun()

    st.markdown("---")
    tx = get_tax_summary()
    st.markdown(f"""
    <div style="padding:0.75rem;background:var(--surface2);border-radius:10px;border:1px solid var(--border);">
        <div style="font-family:DM Mono,monospace;font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;">Quick Stats</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="color:var(--muted);font-size:0.8rem;">📥 Purchases</span>
            <span style="color:#FFB547;font-family:DM Mono,monospace;font-weight:600;">{tx['p_count']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="color:var(--muted);font-size:0.8rem;">📤 Sales</span>
            <span style="color:#00E5A0;font-family:DM Mono,monospace;font-weight:600;">{tx['s_count']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:var(--muted);font-size:0.8rem;">Net Tax Due</span>
            <span style="color:{'#FF6B6B' if tx['net_tax']>0 else '#00E5A0'};font-family:DM Mono,monospace;font-weight:700;">₹{tx['net_tax']:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── PAGES ──
page = st.session_state.page


# ════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown('<div class="finflow-logo" style="font-size:2rem;margin-bottom:0.2rem;">FinFlow</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);font-size:0.88rem;margin-bottom:1.5rem;">GST Sales & Purchase Register</p>', unsafe_allow_html=True)

    tx = get_tax_summary()

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">📥 Total Purchases</div>
            <div class="kpi-value">₹{tx['p_total']:,.0f}</div>
            <div class="kpi-sub">{tx['p_count']} invoices</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">📤 Total Sales</div>
            <div class="kpi-value">₹{tx['s_total']:,.0f}</div>
            <div class="kpi-sub">{tx['s_count']} invoices</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        profit = tx['s_total'] - tx['p_total']
        color  = "#00E5A0" if profit >= 0 else "#FF6B6B"
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">💹 Gross Margin</div>
            <div class="kpi-value" style="color:{color};">₹{profit:,.0f}</div>
            <div class="kpi-sub">Sales minus Purchases</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        net_color = "#FF6B6B" if tx['net_tax'] > 0 else "#00E5A0"
        net_label = "Tax Payable" if tx['net_tax'] > 0 else "Tax Refund"
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">🧾 {net_label}</div>
            <div class="kpi-value" style="color:{net_color};">₹{abs(tx['net_tax']):,.0f}</div>
            <div class="kpi-sub">Output tax − Input tax</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-header">🧾 GST Tax Breakdown</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="tax-box" style="background:var(--surface);border:1px solid var(--border);">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0.5rem;
                font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--muted);
                text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;">
                <span></span><span>PURCHASE<br>(Input)</span><span>SALES<br>(Output)</span><span>NET DUE</span>
            </div>
            <div class="tax-row">
                <span style="color:var(--muted);font-family:'DM Mono',monospace;font-size:0.82rem;">CGST</span>
                <span style="color:#FFB547;">₹{tx['p_cgst']:,.2f}</span>
                <span style="color:#00E5A0;">₹{tx['s_cgst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_cgst']>0 else '#00E5A0'};font-weight:700;">₹{tx['net_cgst']:,.2f}</span>
            </div>
            <div class="tax-row">
                <span style="color:var(--muted);font-family:'DM Mono',monospace;font-size:0.82rem;">SGST</span>
                <span style="color:#FFB547;">₹{tx['p_sgst']:,.2f}</span>
                <span style="color:#00E5A0;">₹{tx['s_sgst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_sgst']>0 else '#00E5A0'};font-weight:700;">₹{tx['net_sgst']:,.2f}</span>
            </div>
            <div class="tax-row">
                <span style="color:var(--muted);font-family:'DM Mono',monospace;font-size:0.82rem;">IGST</span>
                <span style="color:#FFB547;">₹{tx['p_igst']:,.2f}</span>
                <span style="color:#00E5A0;">₹{tx['s_igst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_igst']>0 else '#00E5A0'};font-weight:700;">₹{tx['net_igst']:,.2f}</span>
            </div>
            <div style="border-top:1px solid var(--border);margin-top:0.75rem;padding-top:0.75rem;
                display:flex;justify-content:space-between;align-items:center;">
                <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;">TOTAL TAX NET</span>
                <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.3rem;
                    color:{'#FF6B6B' if tx['net_tax']>0 else '#00E5A0'};">₹{tx['net_tax']:,.2f}</span>
            </div>
            <div style="font-size:0.72rem;color:var(--muted);margin-top:0.4rem;">
                {'⚠️ Tax payable to government' if tx['net_tax']>0 else '✅ Input credit exceeds output tax'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-header">📊 Sales vs Purchases</div>', unsafe_allow_html=True)
        chart_data = pd.DataFrame({"Amount": [tx['p_total'], tx['s_total']]}, index=["Purchases", "Sales"])
        st.bar_chart(chart_data, color="#00E5A0")
        st.markdown(f"""
        <div style="background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.2);
            border-radius:10px;padding:0.9rem 1.1rem;margin-top:0.75rem;">
            <div style="font-size:0.8rem;color:var(--muted);margin-bottom:0.3rem;">How net tax is calculated</div>
            <div style="font-size:0.85rem;color:var(--text);">
                <b>Output Tax</b> (on Sales) − <b>Input Tax Credit</b> (on Purchases) = <b>Net GST Payable</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    p = st.session_state.purchase_register
    s = st.session_state.sales_register
    if not p.empty or not s.empty:
        st.markdown('<div class="section-header">🕒 Recent Activity</div>', unsafe_allow_html=True)
        combined = pd.concat([
            p.assign(Type="Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Type="Sales")    if not s.empty else pd.DataFrame(),
        ]).sort_values("Date", ascending=False).head(8)
        disp = combined[["ID","Date","Vendor","Type","Total","Status"]].copy()
        disp["Total"] = disp["Total"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

    # GSTR Filing Status
    st.markdown('<div class="section-header">📋 GSTR Filing Status</div>', unsafe_allow_html=True)
    g1,g2,g3,g4 = st.columns(4)
    has_data = not st.session_state.sales_register.empty or not st.session_state.purchase_register.empty
    for col, label, form, desc in [
        (g1,"GSTR-1","Outward Supplies","Sales register → File monthly"),
        (g2,"GSTR-3B","Summary Return","Net tax payable summary"),
        (g3,"GSTR-2A","Auto-Populated","From supplier filings"),
        (g4,"GSTR-2B","Static ITC","Locked ITC statement"),
    ]:
        sc = "#FFB547" if has_data else "#5A6075"
        st_txt = "Ready to File" if has_data else "No Data"
        col.markdown(f"""<div class="kpi-card" style="border-color:{sc}33;">
            <div class="kpi-label">{label}</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;margin:0.3rem 0;">{form}</div>
            <div style="font-size:0.75rem;color:{sc};margin-top:0.3rem;">{st_txt}</div>
            <div style="font-size:0.72rem;color:var(--muted);margin-top:0.2rem;">{desc}</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# UPLOAD & EXTRACT
# ════════════════════════════════════════════════
elif page == "Upload & Extract":
    st.markdown('<div class="section-header" style="font-size:1.5rem;font-family:Syne,sans-serif;">📤 Upload & Extract</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);">Upload your invoice — OCR reads and auto-detects whether it is a Purchase or Sales invoice.</p>', unsafe_allow_html=True)

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
            if st.button("🔍 Extract Data", use_container_width=True):
                with st.spinner("Reading invoice..."):
                    try:
                        uploaded_file.seek(0)
                        extracted = run_ocr(uploaded_file)
                        if extracted:
                            st.session_state.extracted = extracted
                            st.session_state.inv_type_detected = extracted.get("doc_type","Purchase Invoice")
                            st.success("✓ Extraction complete!")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

            if st.session_state.extracted:
                ext_data = st.session_state.extracted
                conf = ext_data.get("confidence", 80)
                st.markdown('<div class="section-header">🔎 Extracted Fields</div>', unsafe_allow_html=True)
                dtype = ext_data.get("doc_type","Purchase Invoice")
                badge_color = "#00E5A0" if "Sales" in dtype else "#FFB547"
                st.markdown(f"""
                <div style="display:inline-block;padding:0.3rem 0.9rem;border-radius:100px;
                    background:rgba(0,229,160,0.1);border:1px solid {badge_color};
                    color:{badge_color};font-family:DM Mono,monospace;font-size:0.78rem;
                    font-weight:600;margin-bottom:1rem;">
                    {'📤 SALES INVOICE → Goes to Sales Register' if 'Sales' in dtype else '📥 PURCHASE INVOICE → Goes to Purchase Register'}
                </div>""", unsafe_allow_html=True)
                st.progress(conf / 100)
                if not ext_data.get("gstin"):
                    has_tax = (ext_data.get("cgst",0) > 0 or ext_data.get("sgst",0) > 0 or ext_data.get("igst",0) > 0)
                    if has_tax:
                        st.error("🚨 ILLEGAL TAX ALERT — This party has NO GSTIN but has charged GST on this invoice. An unregistered dealer CANNOT collect GST by law. You CANNOT claim ITC on this. Demand a corrected invoice without any GST charges.")
                    else:
                        st.warning("⚠️ No GSTIN found — This party is Unregistered or on Composition Scheme. No Input Tax Credit (ITC) can be claimed on this purchase.")
                st.markdown(f"""
                <div class="extracted-card">
                    <div class="extracted-field"><span class="field-key">Vendor / Party</span><span class="field-val">{ext_data.get('vendor','')}</span></div>
                    <div class="extracted-field"><span class="field-key">Invoice Type</span><span class="field-val" style="color:{badge_color};">{ext_data.get('doc_type','')}</span></div>
                    <div class="extracted-field"><span class="field-key">Date</span><span class="field-val">{ext_data.get('date','')}</span></div>
                    <div class="extracted-field"><span class="field-key">GSTIN</span><span class="field-val" style="font-family:DM Mono,monospace;">{"⚠️ No GSTIN — Unregistered Dealer" if not ext_data.get('gstin') else ext_data.get('gstin')}</span></div>
                    <div class="extracted-field"><span class="field-key">Category</span><span class="field-val">{ext_data.get('category','')}</span></div>
                    <div class="extracted-field"><span class="field-key">Subtotal</span><span class="field-val">₹{ext_data.get('subtotal',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">CGST</span><span class="field-val">₹{ext_data.get('cgst',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">SGST</span><span class="field-val">₹{ext_data.get('sgst',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">IGST</span><span class="field-val">₹{ext_data.get('igst',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">Total Amount</span><span class="field-val" style="font-size:1.1rem;font-weight:700;">₹{ext_data.get('total',0):,.2f}</span></div>
                </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">✏️ Review & Confirm</div>', unsafe_allow_html=True)
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
                    cgst     = st.number_input("CGST (₹)", value=float(ext_data.get("cgst",0)), min_value=0.0, step=0.01)
                with c2:
                    sgst     = st.number_input("SGST (₹)", value=float(ext_data.get("sgst",0)), min_value=0.0, step=0.01)
                    igst     = st.number_input("IGST (₹)", value=float(ext_data.get("igst",0)), min_value=0.0, step=0.01)
                total_calc = subtotal + cgst + sgst + igst
                st.markdown(f"""
                <div style="background:rgba(0,229,160,0.08);border:1px solid rgba(0,229,160,0.2);
                    border-radius:8px;padding:0.75rem 1rem;margin:0.5rem 0;display:flex;justify-content:space-between;">
                    <span style="font-family:DM Mono,monospace;color:var(--muted);font-size:0.85rem;">Calculated Total</span>
                    <span style="font-family:Syne,sans-serif;font-weight:700;color:var(--accent);font-size:1.1rem;">₹{total_calc:,.2f}</span>
                </div>""", unsafe_allow_html=True)
                submitted = st.form_submit_button("✅ Confirm & Add to Register", use_container_width=True)
                if submitted:
                    data = {"vendor":vendor,"date":txn_date,"gstin":gstin,"category":category,
                            "subtotal":subtotal,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total_calc}
                    txn_id, reg = add_to_register(data, doc_type)
                    st.session_state.extracted = None
                    reg_name = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"✓ {txn_id} added to **{reg_name}**!")
        else:
            st.markdown("""
            <div style="background:var(--surface);border:1px dashed var(--border);border-radius:12px;
                padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-size:2.5rem;margin-bottom:0.75rem;">🔍</div>
                <div style="color:var(--muted);">Upload a document and click Extract</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# MANUAL ENTRY
# ════════════════════════════════════════════════
elif page == "Manual Entry":
    st.markdown('<div class="section-header" style="font-size:1.5rem;font-family:Syne,sans-serif;">✏️ Manual Entry</div>', unsafe_allow_html=True)

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
            <div style="background:var(--surface2);border-radius:10px;padding:1rem;margin:0.5rem 0;border:1px solid var(--border);">
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;font-size:0.85rem;margin-bottom:0.5rem;">
                    <span style="color:var(--muted);">CGST</span><span style="color:var(--text);text-align:right;">₹{cgst:,.2f}</span>
                    <span style="color:var(--muted);">SGST</span><span style="color:var(--text);text-align:right;">₹{sgst:,.2f}</span>
                    <span style="color:var(--muted);">IGST</span><span style="color:var(--text);text-align:right;">₹{igst:,.2f}</span>
                </div>
                <div style="border-top:1px solid var(--border);padding-top:0.5rem;display:flex;justify-content:space-between;">
                    <span style="font-weight:700;">Total</span>
                    <span style="color:var(--accent);font-weight:700;font-size:1.1rem;">₹{total:,.2f}</span>
                </div>
            </div>""", unsafe_allow_html=True)
            submit = st.form_submit_button("➕ Add Entry", use_container_width=True)
            if submit:
                if not vendor:
                    st.error("Vendor name is required.")
                else:
                    data = {"vendor":vendor,"date":txn_date.strftime("%d-%m-%Y"),"gstin":gstin,
                            "category":category,"subtotal":subtotal,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total}
                    txn_id, reg = add_to_register(data, doc_type)
                    reg_name = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"✓ {txn_id} added to **{reg_name}**!")

    with col2:
        st.markdown('<div class="section-header">📌 Recent Entries</div>', unsafe_allow_html=True)
        p = st.session_state.purchase_register
        s = st.session_state.sales_register
        if not p.empty or not s.empty:
            combined = pd.concat([
                p.assign(Type="📥 Purchase") if not p.empty else pd.DataFrame(),
                s.assign(Type="📤 Sales")    if not s.empty else pd.DataFrame(),
            ]).tail(8)[["ID","Vendor","Type","Total"]].copy()
            combined["Total"] = combined["Total"].apply(lambda x: f"₹{float(x):,.2f}")
            st.dataframe(combined, use_container_width=True, hide_index=True)
        else:
            st.info("No entries yet.")


# ════════════════════════════════════════════════
# PURCHASE REGISTER
# ════════════════════════════════════════════════
elif page == "Purchase Register":
    st.markdown('<div class="section-header" style="font-size:1.5rem;font-family:Syne,sans-serif;">📋 Purchase Register</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);">All invoices where you are the buyer — Input Tax Credit (ITC) eligible.</p>', unsafe_allow_html=True)

    df = st.session_state.purchase_register.copy()
    if df.empty:
        st.markdown("""<div style="background:var(--surface);border:1px dashed var(--border);border-radius:16px;padding:4rem;text-align:center;">
            <div style="font-size:3rem;">📋</div>
            <div style="color:var(--muted);margin-top:0.75rem;">No purchase entries yet. Upload purchase invoices or add manually.</div>
        </div>""", unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Total Purchases", f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric("Input CGST (ITC)", f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric("Input SGST (ITC)", f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric("Entries", len(df))
        st.markdown("---")
        search = st.text_input("🔍 Search vendor")
        if search: df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for col in ["Subtotal","CGST","SGST","IGST","Total"]:
            disp[col] = disp[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button("⬇️ Export Purchase Register CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"purchase_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ════════════════════════════════════════════════
# SALES REGISTER
# ════════════════════════════════════════════════
elif page == "Sales Register":
    st.markdown('<div class="section-header" style="font-size:1.5rem;font-family:Syne,sans-serif;">💰 Sales Register</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);">All invoices where you are the seller — Output Tax collected from customers.</p>', unsafe_allow_html=True)

    df = st.session_state.sales_register.copy()
    if df.empty:
        st.markdown("""<div style="background:var(--surface);border:1px dashed var(--border);border-radius:16px;padding:4rem;text-align:center;">
            <div style="font-size:3rem;">💰</div>
            <div style="color:var(--muted);margin-top:0.75rem;">No sales entries yet. Upload sales invoices or add manually.</div>
        </div>""", unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Total Sales", f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric("Output CGST", f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric("Output SGST", f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric("Entries", len(df))
        st.markdown("---")
        search = st.text_input("🔍 Search buyer")
        if search: df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for col in ["Subtotal","CGST","SGST","IGST","Total"]:
            disp[col] = disp[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button("⬇️ Export Sales Register CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"sales_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ════════════════════════════════════════════════
# RECONCILIATION
# ════════════════════════════════════════════════
elif page == "Reconciliation":
    st.markdown('<div class="section-header" style="font-size:1.5rem;font-family:Syne,sans-serif;">🔄 GST Reconciliation</div>', unsafe_allow_html=True)

    tx = get_tax_summary()
    p  = st.session_state.purchase_register
    s  = st.session_state.sales_register

    if p.empty and s.empty:
        st.info("Add purchase and sales entries to run reconciliation.")
    else:
        st.markdown('<div class="section-header">📊 Full Tax Statement</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;">
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;
                font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--muted);
                text-transform:uppercase;letter-spacing:0.08em;margin-bottom:1rem;">
                <span>Tax Head</span><span>Input Tax (Purchase)</span><span>Output Tax (Sales)</span><span>Net Payable</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;align-items:center;padding:0.75rem 0;border-top:1px solid var(--border);">
                <span style="font-weight:600;">CGST</span>
                <span style="color:#FFB547;">₹{tx['p_cgst']:,.2f}</span>
                <span style="color:#00E5A0;">₹{tx['s_cgst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_cgst']>0 else '#00E5A0'};font-weight:700;font-size:1rem;">₹{tx['net_cgst']:,.2f}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;align-items:center;padding:0.75rem 0;border-top:1px solid var(--border);">
                <span style="font-weight:600;">SGST</span>
                <span style="color:#FFB547;">₹{tx['p_sgst']:,.2f}</span>
                <span style="color:#00E5A0;">₹{tx['s_sgst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_sgst']>0 else '#00E5A0'};font-weight:700;font-size:1rem;">₹{tx['net_sgst']:,.2f}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;align-items:center;padding:0.75rem 0;border-top:1px solid var(--border);">
                <span style="font-weight:600;">IGST</span>
                <span style="color:#FFB547;">₹{tx['p_igst']:,.2f}</span>
                <span style="color:#00E5A0;">₹{tx['s_igst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_igst']>0 else '#00E5A0'};font-weight:700;font-size:1rem;">₹{tx['net_igst']:,.2f}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:1rem;align-items:center;
                padding:1rem 0 0.5rem;border-top:2px solid var(--border);margin-top:0.25rem;">
                <span style="font-family:'Syne',sans-serif;font-weight:800;font-size:1rem;">TOTAL</span>
                <span style="color:#FFB547;font-weight:700;">₹{tx['p_cgst']+tx['p_sgst']+tx['p_igst']:,.2f}</span>
                <span style="color:#00E5A0;font-weight:700;">₹{tx['s_cgst']+tx['s_sgst']+tx['s_igst']:,.2f}</span>
                <span style="color:{'#FF6B6B' if tx['net_tax']>0 else '#00E5A0'};font-weight:800;font-size:1.2rem;">₹{tx['net_tax']:,.2f}</span>
            </div>
        </div>
        <div style="background:{'rgba(255,107,107,0.08)' if tx['net_tax']>0 else 'rgba(0,229,160,0.08)'};
            border:1px solid {'rgba(255,107,107,0.3)' if tx['net_tax']>0 else 'rgba(0,229,160,0.3)'};
            border-radius:10px;padding:1rem 1.25rem;">
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;
                color:{'#FF6B6B' if tx['net_tax']>0 else '#00E5A0'};">
                {'⚠️ Net GST Payable to Government: ₹' + f"{tx['net_tax']:,.2f}" if tx['net_tax']>0
                 else '✅ Input Tax Credit exceeds Output Tax by ₹' + f"{abs(tx['net_tax']):,.2f}"}
            </div>
            <div style="font-size:0.8rem;color:var(--muted);margin-top:0.3rem;">
                {'You owe this amount as GST to the government after adjusting input tax credit.' if tx['net_tax']>0
                 else 'You can carry forward this excess input tax credit to next period.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">✅ GSTIN Validation</div>', unsafe_allow_html=True)
        all_df = pd.concat([
            p.assign(Register="Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Register="Sales")    if not s.empty else pd.DataFrame(),
        ])
        g = all_df[["ID","Vendor","GSTIN","Register"]].copy()
        def check_gstin(x):
            if not x or str(x).strip() == "" or str(x) == "nan":
                return "❌ No GSTIN — Unregistered Dealer"
            elif re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]$', str(x)):
                return "✅ Valid"
            else:
                return "⚠️ Invalid Format"
        g["Valid"] = g["GSTIN"].apply(check_gstin)
        st.dataframe(g, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════
# GSTR-1 REPORT
# ════════════════════════════════════════════════
elif page == "GSTR-1 Report":
    st.markdown('<div class="finflow-logo" style="font-size:1.6rem;margin-bottom:0.2rem;">GSTR-1</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:var(--muted);font-size:0.88rem;margin-bottom:0.25rem;">
        <b style="color:var(--accent);">Statement of Outward Supplies</b> — Filed by 11th of following month
    </p>
    <div style="background:rgba(123,97,255,0.08);border:1px solid rgba(123,97,255,0.25);border-radius:8px;
        padding:0.6rem 1rem;margin-bottom:1.5rem;font-size:0.82rem;color:#a89cff;">
        ℹ️ GSTR-1 reports all outward (sales) supplies. B2B invoices auto-appear in buyer's GSTR-2A.
    </div>
    """, unsafe_allow_html=True)

    s_df = st.session_state.sales_register

    if s_df.empty:
        st.markdown("""<div style="background:var(--surface);border:1px dashed var(--border);border-radius:16px;
            padding:4rem;text-align:center;">
            <div style="font-size:3rem;">📄</div>
            <div style="color:var(--muted);margin-top:0.75rem;">No sales data. Add sales invoices to generate GSTR-1.</div>
        </div>""", unsafe_allow_html=True)
    else:
        summary, b2b_df, b2c_df = build_gstr1(s_df)

        k1,k2,k3,k4,k5 = st.columns(5)
        for col, label, val, sub in [
            (k1, "Taxable Turnover",    f"₹{summary['total_taxable']:,.2f}", ""),
            (k2, "Total CGST (Output)", f"₹{summary['total_cgst']:,.2f}", ""),
            (k3, "Total SGST (Output)", f"₹{summary['total_sgst']:,.2f}", ""),
            (k4, "Total IGST (Output)", f"₹{summary['total_igst']:,.2f}", ""),
            (k5, "Grand Total",         f"₹{summary['grand_total']:,.2f}", f"{len(s_df)} invoices"),
        ]:
            col.markdown(f"""<div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="font-size:1.2rem;">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["📦 B2B Invoices", "🛒 B2C Invoices", "📊 HSN Summary", "📋 Full Table"])

        with tab1:
            st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:0.75rem;">B2B invoices (with GSTIN) — auto-appear in buyer\'s GSTR-2A.</div>', unsafe_allow_html=True)
            if b2b_df.empty:
                st.info("No B2B invoices (no entries with GSTIN).")
            else:
                disp = b2b_df[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
                st.dataframe(disp, use_container_width=True, hide_index=True)
                total_tax = b2b_df["CGST"].astype(float).sum() + b2b_df["SGST"].astype(float).sum() + b2b_df["IGST"].astype(float).sum()
                st.markdown(f'<div style="background:rgba(0,229,160,0.06);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:var(--muted);">{len(b2b_df)} B2B invoice(s) · Taxable: {fmt_inr(b2b_df["Subtotal"].astype(float).sum())} · Tax: {fmt_inr(total_tax)}</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:0.75rem;">B2C invoices (no GSTIN) — buyer cannot claim ITC.</div>', unsafe_allow_html=True)
            if b2c_df.empty:
                st.info("No B2C invoices.")
            else:
                disp = b2c_df[["ID","Date","Vendor","Category","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
                st.dataframe(disp, use_container_width=True, hide_index=True)

        with tab3:
            st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:0.75rem;">Category-wise summary (proxy for HSN/SAC grouping).</div>', unsafe_allow_html=True)
            hsn = s_df.groupby("Category").agg(
                Invoices=("ID","count"),
                Taxable=("Subtotal", lambda x: x.astype(float).sum()),
                CGST=("CGST", lambda x: x.astype(float).sum()),
                SGST=("SGST", lambda x: x.astype(float).sum()),
                IGST=("IGST", lambda x: x.astype(float).sum()),
                Total=("Total", lambda x: x.astype(float).sum()),
            ).reset_index()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: hsn[c] = hsn[c].apply(fmt_inr)
            st.dataframe(hsn, use_container_width=True, hide_index=True)

        with tab4:
            disp = s_df.copy()
            for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("⬇️ Download GSTR-1 CSV",
            data=s_df.to_csv(index=False).encode(),
            file_name=f"GSTR1_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# GSTR-3B REPORT
# ════════════════════════════════════════════════
elif page == "GSTR-3B Report":
    st.markdown('<div class="finflow-logo" style="font-size:1.6rem;margin-bottom:0.2rem;">GSTR-3B</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:var(--muted);font-size:0.88rem;margin-bottom:0.25rem;">
        <b style="color:var(--accent);">Monthly Summary Return</b> — Filed by 20th of following month
    </p>
    <div style="background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.2);border-radius:8px;
        padding:0.6rem 1rem;margin-bottom:1.5rem;font-size:0.82rem;color:#ff9a9a;">
        ⚠️ GSTR-3B is a self-declaration. Output tax − ITC = Net tax payable. Interest applies on late payment.
    </div>
    """, unsafe_allow_html=True)

    s_df = st.session_state.sales_register
    p_df = st.session_state.purchase_register

    if s_df.empty and p_df.empty:
        st.info("Add sales and purchase entries to generate GSTR-3B.")
    else:
        data = build_gstr3b(s_df, p_df)
        tab1, tab2, tab3 = st.tabs(["📋 3.1 Output Tax", "📥 4. ITC Available", "💰 Net Tax Payable"])

        with tab1:
            st.markdown('<div style="font-size:0.9rem;font-family:Syne,sans-serif;font-weight:700;color:var(--text);margin-bottom:0.75rem;">Table 3.1 — Details of Outward Supplies & Tax Liability</div>', unsafe_allow_html=True)
            rows = [
                ("3.1(a)", "Outward taxable supplies (other than zero rated)", data["out_taxable"], data["out_cgst"], data["out_sgst"], data["out_igst"]),
                ("3.1(b)", "Outward taxable supplies (zero rated)", 0, 0, 0, 0),
                ("3.1(c)", "Other outward supplies (nil rated, exempt)", 0, 0, 0, 0),
            ]
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;">
                <div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;
                    background:var(--surface2);padding:0.75rem 1rem;font-family:'DM Mono',monospace;
                    font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;">
                    <span>Section</span><span>Nature</span><span>Taxable Value</span><span>CGST</span><span>SGST</span><span>IGST</span>
                </div>
                {"".join([f'<div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;padding:0.75rem 1rem;border-top:1px solid var(--border);font-size:0.85rem;"><span style="font-family:DM Mono,monospace;color:var(--muted);font-size:0.75rem;">{r[0]}</span><span>{r[1]}</span><span style="color:var(--accent);">{fmt_inr(r[2])}</span><span>{fmt_inr(r[3])}</span><span>{fmt_inr(r[4])}</span><span>{fmt_inr(r[5])}</span></div>' for r in rows])}
                <div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;
                    padding:0.75rem 1rem;border-top:2px solid var(--border);background:var(--surface2);font-weight:700;">
                    <span></span><span>TOTAL OUTPUT TAX</span>
                    <span style="color:var(--accent);">{fmt_inr(data['out_taxable'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_cgst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_sgst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_igst'])}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="font-size:0.9rem;font-family:Syne,sans-serif;font-weight:700;color:var(--text);margin-bottom:0.75rem;">Table 4 — Eligible Input Tax Credit (ITC)</div>', unsafe_allow_html=True)
            itc_rows = [
                ("4(A)(1)", "ITC on Imports of goods", 0, 0, 0, 0),
                ("4(A)(2)", "ITC on Imports of services", 0, 0, 0, 0),
                ("4(A)(5)", "All other ITC (domestic purchases)", data["itc_taxable"], data["itc_cgst"], data["itc_sgst"], data["itc_igst"]),
            ]
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;">
                <div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;
                    background:var(--surface2);padding:0.75rem 1rem;font-family:'DM Mono',monospace;
                    font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;">
                    <span>Section</span><span>Nature</span><span>Taxable Value</span><span>CGST</span><span>SGST</span><span>IGST</span>
                </div>
                {"".join([f'<div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;padding:0.75rem 1rem;border-top:1px solid var(--border);font-size:0.85rem;"><span style="font-family:DM Mono,monospace;color:var(--muted);font-size:0.75rem;">{r[0]}</span><span>{r[1]}</span><span style="color:#FFB547;">{fmt_inr(r[2])}</span><span>{fmt_inr(r[3])}</span><span>{fmt_inr(r[4])}</span><span>{fmt_inr(r[5])}</span></div>' for r in itc_rows])}
                <div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr 1fr;
                    padding:0.75rem 1rem;border-top:2px solid var(--border);background:var(--surface2);font-weight:700;">
                    <span></span><span>TOTAL ITC AVAILABLE</span>
                    <span style="color:#FFB547;">{fmt_inr(data['itc_taxable'])}</span>
                    <span style="color:#00E5A0;">{fmt_inr(data['itc_cgst'])}</span>
                    <span style="color:#00E5A0;">{fmt_inr(data['itc_sgst'])}</span>
                    <span style="color:#00E5A0;">{fmt_inr(data['itc_igst'])}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        with tab3:
            st.markdown('<div style="font-size:0.9rem;font-family:Syne,sans-serif;font-weight:700;color:var(--text);margin-bottom:0.75rem;">Table 6.1 — Payment of Tax (Net Liability)</div>', unsafe_allow_html=True)
            nc = "#FF6B6B" if data["net_cgst"] > 0 else "#00E5A0"
            ns = "#FF6B6B" if data["net_sgst"] > 0 else "#00E5A0"
            ni = "#FF6B6B" if data["net_igst"] > 0 else "#00E5A0"
            nt = "#FF6B6B" if data["net_total"] > 0 else "#00E5A0"
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:1.5rem;">
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;
                    background:var(--surface2);padding:0.75rem 1rem;font-family:'DM Mono',monospace;
                    font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;">
                    <span>Description</span><span>CGST</span><span>SGST</span><span>IGST</span><span>Total</span>
                </div>
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;padding:0.75rem 1rem;border-top:1px solid var(--border);">
                    <span>Output Tax Liability</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_cgst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_sgst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_igst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_cgst']+data['out_sgst']+data['out_igst'])}</span>
                </div>
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;padding:0.75rem 1rem;border-top:1px solid var(--border);">
                    <span>Less: ITC Available</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_cgst'])}</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_sgst'])}</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_igst'])}</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_cgst']+data['itc_sgst']+data['itc_igst'])}</span>
                </div>
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;
                    padding:1rem;border-top:2px solid var(--border);background:var(--surface2);font-weight:700;font-size:1rem;">
                    <span style="font-family:'Syne',sans-serif;font-weight:800;">NET TAX PAYABLE</span>
                    <span style="color:{nc};font-size:1.1rem;">{fmt_inr(data['net_cgst'])}</span>
                    <span style="color:{ns};font-size:1.1rem;">{fmt_inr(data['net_sgst'])}</span>
                    <span style="color:{ni};font-size:1.1rem;">{fmt_inr(data['net_igst'])}</span>
                    <span style="color:{nt};font-size:1.2rem;font-weight:800;">{fmt_inr(data['net_total'])}</span>
                </div>
            </div>
            <div style="background:{'rgba(255,107,107,0.08)' if data['net_total']>0 else 'rgba(0,229,160,0.08)'};
                border:1px solid {'rgba(255,107,107,0.3)' if data['net_total']>0 else 'rgba(0,229,160,0.3)'};
                border-radius:10px;padding:1.25rem 1.5rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:{nt};margin-bottom:0.4rem;">
                    {'⚠️ You owe ₹' + f"{data['net_total']:,.2f}" + ' in GST' if data['net_total']>0
                     else '✅ Excess ITC of ₹' + f"{abs(data['net_total']):,.2f}" + ' — carry forward'}
                </div>
                <div style="font-size:0.82rem;color:var(--muted);">
                    Pay via GSTN portal under Electronic Cash Ledger by 20th of following month.
                    Delay attracts 18% p.a. interest + ₹50/day late fee.
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        gstr3b_export = pd.DataFrame([
            {"Section":"3.1(a)","Description":"Outward Taxable Supplies","Taxable":data['out_taxable'],"CGST":data['out_cgst'],"SGST":data['out_sgst'],"IGST":data['out_igst']},
            {"Section":"4(A)(5)","Description":"ITC on Domestic Purchases","Taxable":data['itc_taxable'],"CGST":data['itc_cgst'],"SGST":data['itc_sgst'],"IGST":data['itc_igst']},
            {"Section":"6.1","Description":"Net Tax Payable","Taxable":data['out_taxable']-data['itc_taxable'],"CGST":data['net_cgst'],"SGST":data['net_sgst'],"IGST":data['net_igst']},
        ])
        st.download_button("⬇️ Download GSTR-3B Summary CSV",
            data=gstr3b_export.to_csv(index=False).encode(),
            file_name=f"GSTR3B_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# GSTR-2A / GSTR-2B
# ════════════════════════════════════════════════
elif page == "GSTR-2A / 2B":
    st.markdown('<div class="finflow-logo" style="font-size:1.6rem;margin-bottom:0.2rem;">GSTR-2A / 2B</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:var(--muted);font-size:0.88rem;margin-bottom:0.25rem;">
        <b style="color:var(--accent);">Inward Supplies ITC Statement</b> — Auto-populated from your suppliers' GSTR-1 filings
    </p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
        <div style="background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.2);border-radius:10px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:var(--accent);margin-bottom:0.4rem;">📡 GSTR-2A — Dynamic</div>
            <div style="font-size:0.82rem;color:var(--muted);">Auto-populated in real-time as suppliers file GSTR-1. Changes when suppliers amend or file late.</div>
        </div>
        <div style="background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);border-radius:10px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#a89cff;margin-bottom:0.4rem;">🔒 GSTR-2B — Static / Locked</div>
            <div style="font-size:0.82rem;color:var(--muted);">Locked snapshot of ITC available for a specific return period. Use this to claim ITC in GSTR-3B.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    p_df = st.session_state.purchase_register
    tab1, tab2, tab3, tab4 = st.tabs(["📡 GSTR-2A Data", "🔒 GSTR-2B (Static)", "🔍 Reconciliation", "➕ Add 2A Entry"])

    with tab4:
        st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:1rem;">Simulate supplier-filed entries (in production this pulls from GSTN API).</div>', unsafe_allow_html=True)
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
                s_igst    = st.number_input("IGST (₹)", min_value=0.0, value=0.0, step=0.01)
            s_total = s_taxable + s_cgst + s_sgst + s_igst
            st.markdown(f"**Total: {fmt_inr(s_total)}**")
            add_2a = st.form_submit_button("➕ Add to GSTR-2A", use_container_width=True)
            if add_2a:
                new_row = {"GSTIN":s_gstin,"Vendor":s_vendor,"InvoiceNo":s_inv_no,
                           "Date":s_date.strftime("%d-%m-%Y"),"Taxable":s_taxable,
                           "CGST":s_cgst,"SGST":s_sgst,"IGST":s_igst,"Total":s_total,
                           "Source":"GSTR-2A (Supplier Filed)"}
                st.session_state.gstr2a_data = pd.concat(
                    [st.session_state.gstr2a_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✓ Entry from {s_vendor} added to GSTR-2A.")
                st.rerun()

    gstr2a_df, gstr2b_df, recon_df = build_gstr2a_2b(p_df, st.session_state.gstr2a_data)

    with tab1:
        if st.session_state.gstr2a_data.empty:
            st.markdown("""<div style="background:var(--surface);border:1px dashed var(--border);border-radius:12px;
                padding:3rem;text-align:center;">
                <div style="font-size:2.5rem;">📡</div>
                <div style="color:var(--muted);margin-top:0.75rem;">No GSTR-2A entries. Go to "Add 2A Entry" tab to simulate supplier data.</div>
            </div>""", unsafe_allow_html=True)
        else:
            total_itc = (st.session_state.gstr2a_data["CGST"].astype(float).sum()
                        + st.session_state.gstr2a_data["SGST"].astype(float).sum()
                        + st.session_state.gstr2a_data["IGST"].astype(float).sum())
            k1,k2,k3 = st.columns(3)
            k1.markdown(f"""<div class="kpi-card"><div class="kpi-label">Suppliers Filed</div>
                <div class="kpi-value">{st.session_state.gstr2a_data['GSTIN'].nunique()}</div></div>""", unsafe_allow_html=True)
            k2.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Invoices (2A)</div>
                <div class="kpi-value">{len(st.session_state.gstr2a_data)}</div></div>""", unsafe_allow_html=True)
            k3.markdown(f"""<div class="kpi-card"><div class="kpi-label">ITC Available (2A)</div>
                <div class="kpi-value" style="font-size:1.3rem;">{fmt_inr(total_itc)}</div></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            disp = st.session_state.gstr2a_data.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download GSTR-2A CSV",
                data=st.session_state.gstr2a_data.to_csv(index=False).encode(),
                file_name=f"GSTR2A_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv")

    with tab2:
        if gstr2b_df.empty:
            st.markdown("""<div style="background:var(--surface);border:1px dashed var(--border);border-radius:12px;
                padding:3rem;text-align:center;">
                <div style="font-size:2.5rem;">🔒</div>
                <div style="color:var(--muted);margin-top:0.75rem;">GSTR-2B generated after 2A data is available. Add entries in "Add 2A Entry" first.</div>
            </div>""", unsafe_allow_html=True)
        else:
            itc_total = (gstr2b_df["CGST"].astype(float).sum() + gstr2b_df["SGST"].astype(float).sum()
                        + gstr2b_df["IGST"].astype(float).sum())
            st.markdown(f"""
            <div style="background:rgba(123,97,255,0.08);border:1px solid rgba(123,97,255,0.25);border-radius:10px;
                padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:#a89cff;">
                🔒 GSTR-2B snapshot — Locked ITC you can claim in GSTR-3B. Total claimable: <b>{fmt_inr(itc_total)}</b>
            </div>""", unsafe_allow_html=True)
            disp = gstr2b_df.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download GSTR-2B CSV",
                data=gstr2b_df.to_csv(index=False).encode(),
                file_name=f"GSTR2B_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv")

    with tab3:
        st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:1rem;">Match your Purchase Register vs GSTR-2A to identify claimable ITC.</div>', unsafe_allow_html=True)
        if p_df.empty:
            st.info("No purchase entries to reconcile.")
        elif recon_df.empty:
            st.info("Add 2A entries and purchase invoices to reconcile.")
        else:
            matched   = len(recon_df[recon_df["Status"] == "✅ Matched"])
            mismatch  = len(recon_df[recon_df["Status"] == "❌ Amount Mismatch"])
            not_in_2a = len(recon_df[recon_df["Status"] == "⚠️ Not in GSTR-2A"])
            k1,k2,k3,k4 = st.columns(4)
            k1.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Invoices</div><div class="kpi-value">{len(recon_df)}</div></div>""", unsafe_allow_html=True)
            k2.markdown(f"""<div class="kpi-card" style="border-color:#00E5A033;"><div class="kpi-label" style="color:#00E5A0;">✅ Matched</div><div class="kpi-value" style="color:#00E5A0;">{matched}</div><div class="kpi-sub">ITC claimable</div></div>""", unsafe_allow_html=True)
            k3.markdown(f"""<div class="kpi-card" style="border-color:#FF6B6B33;"><div class="kpi-label" style="color:#FF6B6B;">❌ Mismatch</div><div class="kpi-value" style="color:#FF6B6B;">{mismatch}</div><div class="kpi-sub">Needs correction</div></div>""", unsafe_allow_html=True)
            k4.markdown(f"""<div class="kpi-card" style="border-color:#FFB54733;"><div class="kpi-label" style="color:#FFB547;">⚠️ Not in 2A</div><div class="kpi-value" style="color:#FFB547;">{not_in_2a}</div><div class="kpi-sub">Supplier not filed</div></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            disp = recon_df.copy()
            for c in ["Your CGST","Your IGST","2A CGST","2A IGST"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.markdown("""
            <div style="background:var(--surface2);border-radius:10px;padding:1rem 1.25rem;margin-top:1rem;font-size:0.82rem;">
                <div style="color:var(--text);font-weight:600;margin-bottom:0.5rem;">📌 Action Guide</div>
                <div style="color:var(--muted);line-height:1.8;">
                    <b style="color:#00E5A0;">✅ Matched</b> — Claim ITC in GSTR-3B Table 4.<br>
                    <b style="color:#FF6B6B;">❌ Amount Mismatch</b> — Contact supplier to amend GSTR-1, or reverse ITC.<br>
                    <b style="color:#FFB547;">⚠️ Not in GSTR-2A</b> — Supplier hasn't filed. Follow up before claiming ITC.
                </div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇️ Download Reconciliation Report CSV",
                data=recon_df.to_csv(index=False).encode(),
                file_name=f"GSTR2A_Recon_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)

# ════════════════════════════════════════════════
# USER GUIDE
# ════════════════════════════════════════════════
elif page == "User Guide":
    lang = st.session_state.get("lang", "English")
    is_kn = lang == "ಕನ್ನಡ"

    if is_kn:
        st.markdown('<div class="finflow-logo" style="font-size:1.8rem;margin-bottom:0.2rem;">FinFlow ಮಾರ್ಗದರ್ಶಿ</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:var(--muted);font-size:0.95rem;margin-bottom:1.5rem;">ಈ ಅಪ್ಲಿಕೇಶನ್ ಅನ್ನು ಹೇಗೆ ಬಳಸಬೇಕು ಎಂಬ ಸಂಪೂರ್ಣ ಮಾಹಿತಿ</p>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="finflow-logo" style="font-size:1.8rem;margin-bottom:0.2rem;">📖 User Guide</div>', unsafe_allow_html=True)
        st.markdown('<p style="color:var(--muted);font-size:0.95rem;margin-bottom:1.5rem;">Complete guide on how to use FinFlow — step by step</p>', unsafe_allow_html=True)

    # ── Visual Flow Diagram ──
    st.markdown(f'<div class="section-header">{"📋 ಅಪ್ಲಿಕೇಶನ್ ಕಾರ್ಯ ವಿಧಾನ" if is_kn else "📋 How FinFlow Works"}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;padding:1.25rem;
        background:var(--surface);border:1px solid var(--border);border-radius:14px;">
        <div style="text-align:center;padding:0.75rem 1rem;background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.3);border-radius:10px;min-width:110px;">
            <div style="font-size:1.8rem;">🧾</div>
            <div style="font-size:0.75rem;color:#00E5A0;font-weight:600;margin-top:0.3rem;">Invoice</div>
            <div style="font-size:0.68rem;color:var(--muted);">Upload PDF/Image</div>
        </div>
        <div style="font-size:1.5rem;color:var(--muted);">→</div>
        <div style="text-align:center;padding:0.75rem 1rem;background:rgba(123,97,255,0.1);border:1px solid rgba(123,97,255,0.3);border-radius:10px;min-width:110px;">
            <div style="font-size:1.8rem;">🤖</div>
            <div style="font-size:0.75rem;color:#a89cff;font-weight:600;margin-top:0.3rem;">OCR Reads</div>
            <div style="font-size:0.68rem;color:var(--muted);">AI extracts data</div>
        </div>
        <div style="font-size:1.5rem;color:var(--muted);">→</div>
        <div style="text-align:center;padding:0.75rem 1rem;background:rgba(255,181,71,0.1);border:1px solid rgba(255,181,71,0.3);border-radius:10px;min-width:110px;">
            <div style="font-size:1.8rem;">🔀</div>
            <div style="font-size:0.75rem;color:#FFB547;font-weight:600;margin-top:0.3rem;">Auto Sort</div>
            <div style="font-size:0.68rem;color:var(--muted);">Purchase or Sales</div>
        </div>
        <div style="font-size:1.5rem;color:var(--muted);">→</div>
        <div style="text-align:center;padding:0.75rem 1rem;background:rgba(0,229,160,0.1);border:1px solid rgba(0,229,160,0.3);border-radius:10px;min-width:110px;">
            <div style="font-size:1.8rem;">📊</div>
            <div style="font-size:0.75rem;color:#00E5A0;font-weight:600;margin-top:0.3rem;">Dashboard</div>
            <div style="font-size:0.68rem;color:var(--muted);">Live GST total</div>
        </div>
        <div style="font-size:1.5rem;color:var(--muted);">→</div>
        <div style="text-align:center;padding:0.75rem 1rem;background:rgba(255,107,107,0.1);border:1px solid rgba(255,107,107,0.3);border-radius:10px;min-width:110px;">
            <div style="font-size:1.8rem;">🏛️</div>
            <div style="font-size:0.75rem;color:#FF6B6B;font-weight:600;margin-top:0.3rem;">File GST</div>
            <div style="font-size:0.68rem;color:var(--muted);">GSTR-1 / 3B ready</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Step by Step ──
    st.markdown(f'<div class="section-header">{"🪜 ಹಂತ ಹಂತವಾಗಿ ಬಳಸಿ" if is_kn else "🪜 Step-by-Step Instructions"}</div>', unsafe_allow_html=True)

    steps_en = [
        ("1️⃣", "Upload Invoice", "Go to 📤 Upload & Extract → Click 'Browse files' → Select your bill (PDF or photo) → Click 🔍 Extract Data", "#00E5A0"),
        ("2️⃣", "Review & Confirm", "Check if the vendor name, amount, CGST/SGST are correct → Fix any errors → Click ✅ Confirm & Add to Register", "#a89cff"),
        ("3️⃣", "Check Registers", "Go to 📋 Purchase Register (bills you paid) or 💰 Sales Register (bills you raised) → See all entries", "#FFB547"),
        ("4️⃣", "See Dashboard", "Go to 📊 Dashboard → See total purchases, sales, and NET GST you owe to government automatically", "#00E5A0"),
        ("5️⃣", "GST Reports", "Go to 📄 GSTR-1 for sales report or 📑 GSTR-3B for net tax payable → Download CSV → File on GST portal", "#FF6B6B"),
        ("6️⃣", "Reconciliation", "Go to 🔄 Reconciliation → Check if all GSTINs are valid → Identify unregistered dealers", "#FFB547"),
    ]
    steps_kn = [
        ("1️⃣", "ಬಿಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ", "📤 Upload & Extract ಗೆ ಹೋಗಿ → 'Browse files' ಕ್ಲಿಕ್ ಮಾಡಿ → ನಿಮ್ಮ ಬಿಲ್ (PDF ಅಥವಾ ಫೋಟೋ) ಆಯ್ಕೆ ಮಾಡಿ → 🔍 Extract Data ಕ್ಲಿಕ್ ಮಾಡಿ", "#00E5A0"),
        ("2️⃣", "ಪರಿಶೀಲಿಸಿ ಮತ್ತು ದೃಢಪಡಿಸಿ", "ಹೆಸರು, ಮೊತ್ತ, CGST/SGST ಸರಿಯಾಗಿದೆಯೇ ಎಂದು ನೋಡಿ → ತಪ್ಪಿದ್ದರೆ ಸರಿಪಡಿಸಿ → ✅ Confirm ಕ್ಲಿಕ್ ಮಾಡಿ", "#a89cff"),
        ("3️⃣", "ನೋಂದಣಿ ನೋಡಿ", "📋 Purchase Register (ನೀವು ಕೊಂಡ ಬಿಲ್‌ಗಳು) ಅಥವಾ 💰 Sales Register (ನೀವು ಮಾರಿದ ಬಿಲ್‌ಗಳು) ತೆರೆಯಿರಿ", "#FFB547"),
        ("4️⃣", "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ನೋಡಿ", "📊 Dashboard ಗೆ ಹೋಗಿ → ಒಟ್ಟು ಖರೀದಿ, ಮಾರಾಟ, ಮತ್ತು ಸರ್ಕಾರಕ್ಕೆ ಕೊಡಬೇಕಾದ GST ತಿಳಿಯುತ್ತದೆ", "#00E5A0"),
        ("5️⃣", "GST ವರದಿ", "📄 GSTR-1 (ಮಾರಾಟ ವರದಿ) ಅಥವಾ 📑 GSTR-3B (ನಿವ್ವಳ ತೆರಿಗೆ) → CSV ಡೌನ್‌ಲೋಡ್ → GST ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಸಲ್ಲಿಸಿ", "#FF6B6B"),
        ("6️⃣", "ಹೊಂದಾಣಿಕೆ", "🔄 Reconciliation ಗೆ ಹೋಗಿ → GSTIN ಸರಿಯಾಗಿದೆಯೇ ಪರಿಶೀಲಿಸಿ → ನೋಂದಾಯಿತವಲ್ಲದ ವ್ಯಾಪಾರಿಗಳನ್ನು ಗುರುತಿಸಿ", "#FFB547"),
    ]

    steps = steps_kn if is_kn else steps_en
    for num, title, desc, color in steps:
        st.markdown(f"""
        <div style="display:flex;gap:1rem;margin-bottom:1rem;padding:1.1rem 1.25rem;
            background:var(--surface);border:1px solid var(--border);border-radius:12px;
            border-left:4px solid {color};">
            <div style="font-size:1.6rem;flex-shrink:0;">{num}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.95rem;color:{color};margin-bottom:0.3rem;">{title}</div>
                <div style="font-size:0.85rem;color:var(--muted);line-height:1.6;">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── ITC Rules Visual ──
    st.markdown(f'<div class="section-header">{"💡 ITC (Input Tax Credit) ನಿಯಮಗಳು" if is_kn else "💡 ITC Rules — When Can You Claim?"}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
        <div style="background:rgba(0,229,160,0.08);border:1px solid rgba(0,229,160,0.3);border-radius:12px;padding:1.25rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">✅</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#00E5A0;margin-bottom:0.75rem;">
                {"ITC ಕ್ಲೇಮ್ ಮಾಡಬಹುದು" if is_kn else "ITC Can Be Claimed"}
            </div>
            <div style="font-size:0.85rem;color:var(--muted);line-height:2;">
                {"✔ ವ್ಯಾಪಾರಿಯ GSTIN ಇದೆ<br>✔ ಅವರು GSTR-1 ಸಲ್ಲಿಸಿದ್ದಾರೆ<br>✔ ಬಿಲ್‌ನಲ್ಲಿ GST ಮೊತ್ತ ಇದೆ<br>✔ ನಿಮ್ಮ GSTR-2A ನಲ್ಲಿ ಕಾಣಿಸಿಕೊಳ್ಳುತ್ತದೆ" 
                if is_kn else 
                "✔ Supplier has a valid GSTIN<br>✔ They have filed their GSTR-1<br>✔ Invoice shows GST amount<br>✔ It appears in your GSTR-2A"}
            </div>
        </div>
        <div style="background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.3);border-radius:12px;padding:1.25rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">❌</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#FF6B6B;margin-bottom:0.75rem;">
                {"ITC ಕ್ಲೇಮ್ ಮಾಡಲಾಗಲ್ಲ" if is_kn else "ITC Cannot Be Claimed"}
            </div>
            <div style="font-size:0.85rem;color:var(--muted);line-height:2;">
                {"✘ ವ್ಯಾಪಾರಿಗೆ GSTIN ಇಲ್ಲ (ಅನೋಂದಿತ)<br>✘ Composition Scheme ನಲ್ಲಿದ್ದಾರೆ<br>✘ GSTIN ಇಲ್ಲದೇ ತೆರಿಗೆ ಸಂಗ್ರಹಿಸಿದ್ದಾರೆ — ಇದು ಕಾನೂನು ಬಾಹಿರ!<br>✘ GSTR-1 ಸಲ್ಲಿಸಿಲ್ಲ" 
                if is_kn else 
                "✘ Supplier has NO GSTIN (Unregistered)<br>✘ Supplier is on Composition Scheme<br>✘ Tax charged without GSTIN — ILLEGAL!<br>✘ Supplier hasn't filed GSTR-1"}
            </div>
        </div>
    </div>
    <div style="background:rgba(255,181,71,0.08);border:1px solid rgba(255,181,71,0.4);border-radius:10px;padding:1rem 1.25rem;">
        <div style="font-weight:700;color:#FFB547;margin-bottom:0.3rem;">
            {"⚠️ ಮುಖ್ಯ ಎಚ್ಚರಿಕೆ" if is_kn else "⚠️ Important Warning"}
        </div>
        <div style="font-size:0.85rem;color:var(--muted);">
            {"ಯಾವ ವ್ಯಾಪಾರಿಗೆ GSTIN ಇಲ್ಲವೋ ಅವರು GST ಸಂಗ್ರಹಿಸುವ ಹಕ್ಕು ಹೊಂದಿಲ್ಲ. ನೀವು ಅಂತಹ ವ್ಯಾಪಾರಿಗೆ GST ಕೊಟ್ಟರೆ, ನೀವು ಅದನ್ನು ಮರಳಿ ಕ್ಲೇಮ್ ಮಾಡಲಾಗಲ್ಲ ಮತ್ತು ಆ ವ್ಯಾಪಾರಿ ಕಾನೂನು ಉಲ್ಲಂಘನೆ ಮಾಡುತ್ತಿದ್ದಾರೆ."
            if is_kn else
            "A supplier without a GSTIN has NO legal right to collect GST. If they charge you GST without a GSTIN, that tax is illegally collected — you cannot claim ITC on it, and you should report it or demand a corrected invoice without GST."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Icon Legend ──
    st.markdown(f'<div class="section-header">{"🎨 ಬಣ್ಣ ಮತ್ತು ಚಿಹ್ನೆ ಅರ್ಥ" if is_kn else "🎨 Colour & Icon Legend"}</div>', unsafe_allow_html=True)
    legends = [
        ("#00E5A0", "✅", "Green / ಹಸಿರು", "Good — Sales, ITC Matched, Valid GSTIN / ಮಾರಾಟ, ಸರಿಯಾದ GSTIN"),
        ("#FFB547", "⚠️", "Yellow / ಹಳದಿ", "Warning — Check needed, Purchase input tax / ಎಚ್ಚರಿಕೆ, ಖರೀದಿ ತೆರಿಗೆ"),
        ("#FF6B6B", "❌", "Red / ಕೆಂಪು", "Danger — Tax payable, No GSTIN, Mismatch / ತೆರಿಗೆ ಕೊಡಬೇಕು, GSTIN ಇಲ್ಲ"),
        ("#a89cff", "🔒", "Purple / ನೇರಳೆ", "GSTR-2B — Locked ITC snapshot / ಲಾಕ್ ಆದ ITC ಮಾಹಿತಿ"),
    ]
    cols = st.columns(4)
    for col, (color, icon, label, desc) in zip(cols, legends):
        col.markdown(f"""
        <div style="background:var(--surface);border:1px solid {color}44;border-radius:10px;padding:1rem;text-align:center;">
            <div style="font-size:1.6rem;">{icon}</div>
            <div style="color:{color};font-weight:700;font-size:0.82rem;margin:0.3rem 0;">{label}</div>
            <div style="color:var(--muted);font-size:0.72rem;line-height:1.5;">{desc}</div>
        </div>""", unsafe_allow_html=True)

    # ── FAQ ──
    st.markdown(f'<div class="section-header">{"❓ ಸಾಮಾನ್ಯ ಪ್ರಶ್ನೆಗಳು" if is_kn else "❓ Frequently Asked Questions"}</div>', unsafe_allow_html=True)
    faqs_en = [
        ("What is ITC?", "Input Tax Credit (ITC) means the GST you paid on purchases can be deducted from the GST you collected on sales. You only pay the difference to the government."),
        ("My supplier doesn't have a GSTIN — can I still claim ITC?", "No. If your supplier has no GSTIN, they are unregistered and cannot legally charge GST. You cannot claim ITC on that purchase. Ask them to remove GST from the bill."),
        ("What is Composition Scheme?", "Small businesses with turnover below ₹1.5 crore can choose Composition Scheme. They pay a flat low tax rate but CANNOT collect GST from buyers and CANNOT give ITC."),
        ("What if OCR reads the wrong amount?", "You can manually correct any field in the Review & Confirm section before adding the entry. Always double-check extracted data."),
        ("How often should I file GST?", "GSTR-1 by 11th of next month (sales). GSTR-3B by 20th of next month (net tax payment). Late filing attracts ₹50/day penalty + 18% annual interest."),
    ]
    faqs_kn = [
        ("ITC ಎಂದರೇನು?", "Input Tax Credit (ITC) ಎಂದರೆ ನೀವು ಖರೀದಿಗೆ ಕೊಟ್ಟ GST ಅನ್ನು ನೀವು ಮಾರಾಟದಲ್ಲಿ ಸಂಗ್ರಹಿಸಿದ GST ನಿಂದ ಕಳೆಯಬಹುದು. ಉಳಿದ ಮೊತ್ತ ಮಾತ್ರ ಸರ್ಕಾರಕ್ಕೆ ಕೊಡಿ."),
        ("ನನ್ನ ವ್ಯಾಪಾರಿಗೆ GSTIN ಇಲ್ಲ — ITC ಕ್ಲೇಮ್ ಮಾಡಬಹುದೇ?", "ಇಲ್ಲ. GSTIN ಇಲ್ಲದ ವ್ಯಾಪಾರಿ GST ಸಂಗ್ರಹಿಸುವ ಹಕ್ಕು ಹೊಂದಿಲ್ಲ. ಅಂಥ ಖರೀದಿಗೆ ITC ಸಿಗಲ್ಲ. ಅವರಿಗೆ GST ಇಲ್ಲದ ಬಿಲ್ ಕೊಡಲು ಕೇಳಿ."),
        ("Composition Scheme ಎಂದರೇನು?", "₹1.5 ಕೋಟಿಗಿಂತ ಕಡಿಮೆ ವಹಿವಾಟು ಇರುವ ಸಣ್ಣ ವ್ಯಾಪಾರಿಗಳು Composition Scheme ಆಯ್ಕೆ ಮಾಡಬಹುದು. ಅವರು ಕಡಿಮೆ ದರದಲ್ಲಿ ತೆರಿಗೆ ಕೊಡುತ್ತಾರೆ ಆದರೆ GST ಸಂಗ್ರಹಿಸಲು ಅನುಮತಿ ಇಲ್ಲ."),
        ("OCR ತಪ್ಪಾಗಿ ಓದಿದರೆ?", "Review & Confirm ವಿಭಾಗದಲ್ಲಿ ನೀವು ಯಾವ ಮಾಹಿತಿಯನ್ನೂ ಸರಿಪಡಿಸಬಹುದು. ಯಾವಾಗಲೂ ದಾಖಲಿಸುವ ಮೊದಲು ಪರಿಶೀಲಿಸಿ."),
        ("GST ಎಷ್ಟು ಬಾರಿ ಸಲ್ಲಿಸಬೇಕು?", "GSTR-1 — ಮುಂದಿನ ತಿಂಗಳ 11ನೇ ತಾರೀಕಿಗೆ (ಮಾರಾಟ). GSTR-3B — 20ನೇ ತಾರೀಕಿಗೆ (ನಿವ್ವಳ ತೆರಿಗೆ). ತಡವಾದರೆ ₹50/ದಿನ ದಂಡ + 18% ಬಡ್ಡಿ."),
    ]
    faqs = faqs_kn if is_kn else faqs_en
    for q, a in faqs:
        with st.expander(f"❓ {q}"):
            st.markdown(f'<div style="color:var(--muted);font-size:0.88rem;line-height:1.7;padding:0.25rem 0;">{a}</div>', unsafe_allow_html=True)
