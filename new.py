import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date

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
CATEGORIES = ["Office Supplies","Travel & Transport","Food & Entertainment","Utilities",
               "Rent","Professional Services","IT & Software","Marketing","Raw Materials","Miscellaneous"]

# ── SESSION STATE ──
def init_state():
    defaults = {
        "page": "Dashboard",
        "purchase_register": pd.DataFrame(columns=COLS),
        "sales_register":    pd.DataFrame(columns=COLS),
        "counter": 1,
        "extracted": None,
        "inv_type_detected": "Purchase Invoice",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── OCR (Tesseract) ──
def run_ocr(uploaded_file) -> dict:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError("Run: pip install pytesseract pillow")

    import shutil
    if shutil.which("tesseract") is None:
        for path in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

    file_bytes = uploaded_file.read()
    ext = uploaded_file.name.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        try:
            import fitz
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            page = pdf_doc[0]
            mat = fitz.Matrix(3, 3)
            pix = page.get_pixmap(matrix=mat)
            from io import BytesIO
            img = Image.open(BytesIO(pix.tobytes("png")))
        except ImportError:
            try:
                from pdf2image import convert_from_bytes
                pages = convert_from_bytes(file_bytes, dpi=300)
                img = pages[0]
            except Exception:
                raise ImportError("PDF support requires pymupdf. Run: pip install pymupdf")
    else:
        from io import BytesIO
        img = Image.open(BytesIO(file_bytes))

    raw_text = pytesseract.image_to_string(img, lang="eng")

    if not raw_text.strip():
        st.error("OCR found no text. Try a clearer image.")
        return {}

    return parse_invoice_text(raw_text)


def parse_invoice_text(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = " ".join(lines)

    def find_amount(patterns):
        for p in patterns:
            m = re.search(p, full, re.IGNORECASE)
            if m:
                try: return float(m.group(1).replace(",","").replace(" ",""))
                except: pass
        return 0.0

    # ── Detect invoice type ──
    if re.search(r'sales\s*invoice|sale\s*invoice', full, re.IGNORECASE):
        doc_type = "Sales Invoice"
    elif re.search(r'credit\s*note', full, re.IGNORECASE):
        doc_type = "Credit Note"
    elif re.search(r'debit\s*note', full, re.IGNORECASE):
        doc_type = "Debit Note"
    elif re.search(r'purchase\s*invoice', full, re.IGNORECASE):
        doc_type = "Purchase Invoice"
    else:
        doc_type = "Purchase Invoice"

    # ── Vendor detection ──
    skip_pats = [
        r'\d{2}[A-Za-z]{5}\d{4}', r'phone|email|gstin|gst no|billing|authorised',
        r'@', r'^[\d\s\-\+]+$', r'^\d+$',
        r'tax invoice|purchase invoice|sales invoice|invoice no|bill to|due date',
    ]

    def find_company(line_list):
        for line in line_list:
            lc = re.sub(r'[|/*]', '', line).strip()
            if len(lc) < 4: continue
            skip = any(re.search(p, lc, re.IGNORECASE) for p in skip_pats)
            if not skip and any(c.isalpha() for c in lc):
                return lc
        return "Unknown"

    bill_idx = next((i for i,l in enumerate(lines) if re.search(r'bill\s*to', l, re.IGNORECASE)), len(lines))
    seller   = find_company(lines[:bill_idx])
    buyer    = find_company(lines[bill_idx+1:bill_idx+6])
    vendor   = buyer if doc_type == "Sales Invoice" else seller

    # ── Date ──
    dm = re.search(r'(?:invoice\s*date|date)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', full, re.IGNORECASE)
    if not dm: dm = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', full)
    date_str = dm.group(1).replace("/","-") if dm else date.today().strftime("%d-%m-%Y")

    # ── GSTIN ──
    gstin_match = re.findall(r'\b\d{2}[A-Za-z]{5}\d{4}[A-Za-z][A-Za-z0-9][Zz][A-Za-z0-9]\b', full)
    gstin = gstin_match[0].upper() if gstin_match else ""

    # ── Amounts ──
    total = find_amount([
        r'(?:total\s*amount\s*payable|grand\s*total|total\s*amount)[:\sRs.]*([0-9,]+\.?\d*)',
        r'total\s*payable[:\sRs.]*([0-9,]+\.?\d*)',
    ])
    if total == 0.0:
        all_nums = [float(x) for x in re.findall(r'\b\d{1,7}\.\d{2}\b', full)]
        total = max(all_nums) if all_nums else 0.0

    subtotal = find_amount([r'(?:taxable\s*value|subtotal)[:\sRs.]*([0-9,]+\.?\d*)'])
    cgst     = find_amount([
        r'CGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)',
        r'CGST\s*@?\s*[\d.]*\s*%?\s*[:\sRs.]*([0-9,]{2,}\.?\d*)',
    ])
    sgst     = find_amount([
        r'SGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)',
        r'SGST\s*@?\s*[\d.]*\s*%?\s*[:\sRs.]*([0-9,]{2,}\.?\d*)',
    ])
    igst     = find_amount([
        r'IGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)',
        r'IGST\s*@?\s*[\d.]*\s*%?\s*[:\sRs.]*([0-9,]{2,}\.?\d*)',
    ])

    if subtotal == 0.0 and total > 0:
        tax = cgst + sgst + igst
        subtotal = round(total - tax, 2) if tax > 0 else round(total / 1.18, 2)
    if cgst == 0.0 and sgst == 0.0 and igst == 0.0 and total > 0 and subtotal > 0:
        tax = round(total - subtotal, 2)
        cgst = sgst = round(tax / 2, 2)

    # ── Category ──
    category = "Miscellaneous"
    tl = full.lower()
    kw_map = {
        "Office Supplies":       ["stationery","paper","pen","office"],
        "Travel & Transport":    ["travel","transport","cab","fuel","flight"],
        "Utilities":             ["electricity","water","internet"],
        "Rent":                  ["rent","lease"],
        "Professional Services": ["consulting","legal","audit"],
        "IT & Software":         ["software","laptop","computer","server"],
        "Marketing":             ["marketing","advertisement","printing"],
        "Raw Materials":         ["seeds","fertilizer","agriculture","grain","rice","wheat","fabric","cotton"],
    }
    for cat, kws in kw_map.items():
        if any(k in tl for k in kws):
            category = cat
            break

    found = sum([bool(vendor and vendor!="Unknown"), bool(gstin), total>0, subtotal>0, cgst>0 or sgst>0])
    confidence = min(55 + found * 9, 95)

    return {
        "vendor": vendor, "date": date_str, "gstin": gstin, "doc_type": doc_type,
        "subtotal": subtotal, "cgst": cgst, "sgst": sgst, "igst": igst,
        "total": total, "category": category, "confidence": confidence,
    }


# ── HELPERS ──
def make_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%y%m%d')}-{st.session_state.counter:04d}"

def add_to_register(data: dict, doc_type: str):
    is_sales = "Sales" in doc_type
    prefix   = "SAL" if is_sales else "PUR"
    txn_id   = make_id(prefix)
    row = {
        "ID": txn_id, "Date": data.get("date",""),
        "Vendor": data.get("vendor",""), "GSTIN": data.get("gstin",""),
        "Category": data.get("category",""),
        "Subtotal": data.get("subtotal",0), "CGST": data.get("cgst",0),
        "SGST": data.get("sgst",0),         "IGST": data.get("igst",0),
        "Total": data.get("total",0),       "Status": "Verified",
    }
    reg_key = "sales_register" if is_sales else "purchase_register"
    st.session_state[reg_key] = pd.concat(
        [st.session_state[reg_key], pd.DataFrame([row])], ignore_index=True
    )
    st.session_state.counter += 1
    return txn_id, reg_key

def get_tax_summary():
    p = st.session_state.purchase_register
    s = st.session_state.sales_register

    def tax_sum(df):
        if df.empty: return 0.0, 0.0, 0.0, 0.0
        return (df["CGST"].astype(float).sum(),
                df["SGST"].astype(float).sum(),
                df["IGST"].astype(float).sum(),
                df["Total"].astype(float).sum())

    p_cgst, p_sgst, p_igst, p_total = tax_sum(p)
    s_cgst, s_sgst, s_igst, s_total = tax_sum(s)

    return {
        "p_cgst": p_cgst, "p_sgst": p_sgst, "p_igst": p_igst, "p_total": p_total,
        "s_cgst": s_cgst, "s_sgst": s_sgst, "s_igst": s_igst, "s_total": s_total,
        "net_cgst": round(s_cgst - p_cgst, 2),
        "net_sgst": round(s_sgst - p_sgst, 2),
        "net_igst": round(s_igst - p_igst, 2),
        "net_tax":  round((s_cgst+s_sgst+s_igst) - (p_cgst+p_sgst+p_igst), 2),
        "p_count":  len(p),
        "s_count":  len(s),
    }


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem;">
        <div class="finflow-logo">FinFlow</div>
        <div class="finflow-tagline">GST Sales & Purchase Register</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    pages = [
        ("📊","Dashboard"),
        ("📤","Upload & Extract"),
        ("✏️","Manual Entry"),
        ("📋","Purchase Register"),
        ("💰","Sales Register"),
        ("🔄","Reconciliation"),
    ]
    for icon, name in pages:
        if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
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
                    color:{'#FF6B6B' if tx['net_tax']>0 else '#00E5A0'};">
                    ₹{tx['net_tax']:,.2f}
                </span>
            </div>
            <div style="font-size:0.72rem;color:var(--muted);margin-top:0.4rem;">
                {'⚠️ Tax payable to government' if tx['net_tax']>0 else '✅ Input credit exceeds output tax'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-header">📊 Sales vs Purchases</div>', unsafe_allow_html=True)
        chart_data = pd.DataFrame({
            "Amount": [tx['p_total'], tx['s_total']],
        }, index=["Purchases", "Sales"])
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
                </div>
                """, unsafe_allow_html=True)

                st.progress(conf / 100)
                st.markdown(f"""
                <div class="extracted-card">
                    <div class="extracted-field"><span class="field-key">Vendor / Party</span><span class="field-val">{ext_data.get('vendor','')}</span></div>
                    <div class="extracted-field"><span class="field-key">Invoice Type</span><span class="field-val" style="color:{badge_color};">{ext_data.get('doc_type','')}</span></div>
                    <div class="extracted-field"><span class="field-key">Date</span><span class="field-val">{ext_data.get('date','')}</span></div>
                    <div class="extracted-field"><span class="field-key">GSTIN</span><span class="field-val" style="font-family:DM Mono,monospace;">{ext_data.get('gstin','—')}</span></div>
                    <div class="extracted-field"><span class="field-key">Category</span><span class="field-val">{ext_data.get('category','')}</span></div>
                    <div class="extracted-field"><span class="field-key">Subtotal</span><span class="field-val">₹{ext_data.get('subtotal',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">CGST</span><span class="field-val">₹{ext_data.get('cgst',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">SGST</span><span class="field-val">₹{ext_data.get('sgst',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">IGST</span><span class="field-val">₹{ext_data.get('igst',0):,.2f}</span></div>
                    <div class="extracted-field"><span class="field-key">Total Amount</span><span class="field-val" style="font-size:1.1rem;font-weight:700;">₹{ext_data.get('total',0):,.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)

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
                    cgst     = st.number_input("CGST (₹)",     value=float(ext_data.get("cgst",0)),     min_value=0.0, step=0.01)
                with c2:
                    sgst     = st.number_input("SGST (₹)",     value=float(ext_data.get("sgst",0)),     min_value=0.0, step=0.01)
                    igst     = st.number_input("IGST (₹)",     value=float(ext_data.get("igst",0)),     min_value=0.0, step=0.01)

                total_calc = subtotal + cgst + sgst + igst
                st.markdown(f"""
                <div style="background:rgba(0,229,160,0.08);border:1px solid rgba(0,229,160,0.2);
                    border-radius:8px;padding:0.75rem 1rem;margin:0.5rem 0;
                    display:flex;justify-content:space-between;">
                    <span style="font-family:DM Mono,monospace;color:var(--muted);font-size:0.85rem;">Calculated Total</span>
                    <span style="font-family:Syne,sans-serif;font-weight:700;color:var(--accent);font-size:1.1rem;">₹{total_calc:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)

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
            </div>
            """, unsafe_allow_html=True)


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
            </div>
            """, unsafe_allow_html=True)

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
        st.markdown("""
        <div style="background:var(--surface);border:1px dashed var(--border);border-radius:16px;padding:4rem;text-align:center;">
            <div style="font-size:3rem;">📋</div>
            <div style="color:var(--muted);margin-top:0.75rem;">No purchase entries yet. Upload purchase invoices or add manually.</div>
        </div>""", unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Total Purchases",  f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric("Input CGST (ITC)",  f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric("Input SGST (ITC)",  f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric("Entries",           len(df))

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
        st.markdown("""
        <div style="background:var(--surface);border:1px dashed var(--border);border-radius:16px;padding:4rem;text-align:center;">
            <div style="font-size:3rem;">💰</div>
            <div style="color:var(--muted);margin-top:0.75rem;">No sales entries yet. Upload sales invoices or add manually.</div>
        </div>""", unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Total Sales",       f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric("Output CGST",        f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric("Output SGST",        f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric("Entries",            len(df))

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
        g["Valid"] = g["GSTIN"].apply(lambda x: "✅ Valid" if re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]$', str(x)) else "⚠️ Check")
        st.dataframe(g, use_container_width=True, hide_index=True)