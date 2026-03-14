import streamlit as st
import pandas as pd
import os, re, json
from datetime import datetime, date
from io import BytesIO
from pathlib import Path

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FinFlow · GST Register",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');
:root {
    --bg:#0A0C10; --surface:#111318; --surface2:#181C24; --border:#1E2330;
    --accent:#00E5A0; --accent2:#7B61FF; --text:#E8ECF4; --muted:#5A6075;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); }
.stApp { background: var(--bg); }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem; max-width: 960px !important; margin: 0 auto; }
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }
[data-testid="collapsedControl"] { display: none !important; }
.stButton > button {
    background: linear-gradient(135deg, #00E5A0, #00C88A) !important;
    color: #0A0C10 !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; border: none !important; border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important; transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(0,229,160,0.3) !important; }
.stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > textarea {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
}
.stSelectbox > div > div { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
label, .stSelectbox label, .stTextInput label { color: var(--muted) !important; font-size: 0.78rem !important; font-family: 'DM Mono', monospace !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 10px !important; padding: 4px !important; gap: 4px !important; border: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; border-radius: 7px !important; border: none !important; }
.stTabs [aria-selected="true"] { background: var(--surface2) !important; color: var(--accent) !important; border: 1px solid var(--border) !important; }
[data-testid="stMetric"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; color: var(--text) !important; }
hr { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }
.reject-box {
    background: rgba(204,0,0,0.08); border: 2px solid #CC0000;
    border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILE-BASED PERSISTENT STORAGE
# ─────────────────────────────────────────────
DATA_DIR = Path("finflow_data")
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.json"

def _load_users() -> dict:
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text())
        except Exception:
            pass
    # Default admin
    default = {
        "admin": {
            "password": "Admin@123",
            "name": "Admin User",
            "color": "#00E5A0",
        }
    }
    _save_users(default)
    return default

def _save_users(db: dict):
    USERS_FILE.write_text(json.dumps(db, indent=2))

def _user_dir(username: str) -> Path:
    d = DATA_DIR / username
    d.mkdir(exist_ok=True)
    return d

def _user_file(username: str, key: str) -> Path:
    return _user_dir(username) / f"{key}.json"

def _load_user_key(username: str, key: str, default=None):
    f = _user_file(username, key)
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            pass
    return default

def _save_user_key(username: str, key: str, value):
    _user_file(username, key).write_text(json.dumps(value, indent=2))

# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
def validate_password(pwd: str):
    rules = [
        ("min_len", len(pwd) >= 6,                           "At least 6 characters"),
        ("max_len", len(pwd) <= 12,                          "At most 12 characters"),
        ("upper",   bool(re.search(r'[A-Z]', pwd)),          "At least 1 uppercase letter"),
        ("special", bool(re.search(r'[^A-Za-z0-9]', pwd)),  "At least 1 special character"),
    ]
    return all(ok for _, ok, _ in rules), rules

# ─────────────────────────────────────────────
# DEFAULTS
# ─────────────────────────────────────────────
EMPTY_SETTINGS = {
    "my_gstin": "29AAAAA1111B1Z1",
    "my_name":  "Sai Coffee Traders",
    "my_city":  "Dharwad",
    "my_state": "Karnataka",
    "counter":  1,
}
COLS = ["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total","Status"]

# ─────────────────────────────────────────────
# USER DB HELPERS
# ─────────────────────────────────────────────
def get_user_db():
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = _load_users()
    return st.session_state["user_db"]

def save_user_db():
    db = st.session_state.get("user_db", {})
    # Only save credentials — not data (data is per-file)
    creds = {u: {k: v for k, v in info.items() if k != "data"}
             for u, info in db.items()}
    _save_users(creds)

# ─────────────────────────────────────────────
# PER-USER DATA HELPERS  (file-backed)
# ─────────────────────────────────────────────
def _uname() -> str:
    return st.session_state.get("username", "")

def get_setting(key, default=""):
    if not _uname(): return default
    settings = _load_user_key(_uname(), "settings", EMPTY_SETTINGS.copy())
    return settings.get(key, EMPTY_SETTINGS.get(key, default))

def save_setting_val(key, value):
    settings = _load_user_key(_uname(), "settings", EMPTY_SETTINGS.copy())
    settings[key] = value
    _save_user_key(_uname(), "settings", settings)

def get_register(key) -> pd.DataFrame:
    rows = _load_user_key(_uname(), key, [])
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=COLS)

def set_register(key, df: pd.DataFrame):
    _save_user_key(_uname(), key, df.to_dict("records"))

def get_counter() -> int:
    return int(get_setting("counter", 1))

def inc_counter():
    save_setting_val("counter", get_counter() + 1)

def get_gstr2a() -> pd.DataFrame:
    GCOLS = ["GSTIN","Vendor","InvoiceNo","Date","Taxable","CGST","SGST","IGST","Total","Source"]
    rows = _load_user_key(_uname(), "gstr2a_data", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=GCOLS)

def set_gstr2a(df: pd.DataFrame):
    _save_user_key(_uname(), "gstr2a_data", df.to_dict("records"))

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for k, v in {"logged_in": False, "username": "", "user_name": "",
             "user_color": "#00E5A0", "page": "Dashboard",
             "extracted": None, "lang": "English",
             "upload_rejected": False, "reject_reason": ""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_inr(val):
    try: return f"Rs.{float(val):,.2f}"
    except: return "Rs.0.00"

def make_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%y%m%d')}-{get_counter():04d}"

def add_to_register(data, doc_type):
    is_sales = "Sales" in doc_type
    prefix = "SAL" if is_sales else "PUR"
    row = {
        "ID": make_id(prefix), "Date": data.get("date",""),
        "Vendor": data.get("vendor",""), "GSTIN": data.get("gstin",""),
        "Category": "Goods",
        "Subtotal": data.get("subtotal",0), "CGST": data.get("cgst",0),
        "SGST": data.get("sgst",0), "IGST": data.get("igst",0),
        "Total": data.get("total",0), "Status": "Verified"
    }
    reg_key = "sales_register" if is_sales else "purchase_register"
    df = get_register(reg_key)
    updated = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    set_register(reg_key, updated)
    inc_counter()
    return row["ID"], reg_key

def get_tax_summary():
    p = get_register("purchase_register")
    s = get_register("sales_register")
    def ts(df):
        if df.empty: return 0., 0., 0., 0.
        return (df["CGST"].astype(float).sum(), df["SGST"].astype(float).sum(),
                df["IGST"].astype(float).sum(), df["Total"].astype(float).sum())
    pc,ps,pi,pt = ts(p); sc,ss,si,st_ = ts(s)
    return {"p_cgst":pc,"p_sgst":ps,"p_igst":pi,"p_total":pt,
            "s_cgst":sc,"s_sgst":ss,"s_igst":si,"s_total":st_,
            "net_cgst":round(sc-pc,2),"net_sgst":round(ss-ps,2),
            "net_igst":round(si-pi,2),"net_tax":round((sc+ss+si)-(pc+ps+pi),2),
            "p_count":len(p),"s_count":len(s)}

# ─────────────────────────────────────────────
# INVOICE VALIDATION — error file detection
# ─────────────────────────────────────────────
VALID_GSTIN_RE = re.compile(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9][Z][A-Z0-9]$')

def validate_invoice_before_upload(extracted: dict) -> tuple[bool, str]:
    """
    Returns (is_valid, rejection_reason).
    Rejects if:
      1. No GSTIN on seller side AND tax is charged  — illegal collection
      2. Seller GSTIN is present but format is invalid (fake/wrong)
      3. Invoice watermark text contains ERROR keywords
    """
    gstin      = str(extracted.get("gstin", "")).strip()
    cgst       = float(extracted.get("cgst", 0) or 0)
    sgst       = float(extracted.get("sgst", 0) or 0)
    igst       = float(extracted.get("igst", 0) or 0)
    has_tax    = (cgst + sgst + igst) > 0
    raw_text   = extracted.get("_raw_text", "").lower()

    # Check for ERROR watermark keywords in the raw OCR text
    error_keywords = [
        "unregistered supplier", "no gstin", "composition scheme dealer",
        "cannot collect gst", "invalid / fake gstin", "fake gstin",
        "illegal", "error:", "itc cannot be claimed"
    ]
    for kw in error_keywords:
        if kw in raw_text:
            return False, (
                "🚨 REJECTED — This invoice contains error flags.\n\n"
                "An **unregistered person** or **Composition scheme dealer** "
                "cannot legally collect GST from buyers.\n\n"
                "**ITC (Input Tax Credit) CANNOT be claimed** on this invoice. "
                "Demand a corrected invoice from a GST-registered supplier."
            )

    # No GSTIN but GST charged
    if (not gstin or gstin == "") and has_tax:
        return False, (
            "🚨 REJECTED — Supplier has **NO GSTIN** but is charging GST.\n\n"
            "Under the CGST Act, **only GST-registered persons** can collect tax "
            "from buyers. An unregistered supplier collecting GST is **illegal**.\n\n"
            "**You cannot claim ITC** on this invoice. "
            "Demand a corrected invoice without GST, or switch to a registered supplier."
        )

    # GSTIN present but invalid format
    if gstin and not VALID_GSTIN_RE.match(gstin.upper()):
        return False, (
            f"🚨 REJECTED — The GSTIN **'{gstin}'** on this invoice is **invalid / fake**.\n\n"
            "A valid GSTIN is 15 characters: e.g. `29ABCDE1234F1Z5`\n\n"
            "**ITC cannot be claimed** on invoices with fake GSTINs. "
            "Verify the supplier's registration at **gstin.gov.in** before payment."
        )

    return True, ""

# ─────────────────────────────────────────────
# TEXT EXTRACTION — try direct PDF text first,
# fall back to OCR only for scanned/image PDFs
# ─────────────────────────────────────────────
def extract_text_from_file(uploaded_file) -> str:
    """
    For text-based PDFs: use pypdf (perfect quality, no OCR loss).
    For image PDFs / images: fall back to pytesseract OCR.
    """
    fb  = uploaded_file.read()
    ext = uploaded_file.name.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        # ── Try direct text extraction first ──────────────────
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(fb))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                return text          # ← perfect text, done
        except Exception:
            pass

        # ── Fall back: render PDF page → image → OCR ──────────
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=fb, filetype="pdf")
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(3, 3))
            from PIL import Image
            img = Image.open(BytesIO(pix.tobytes("png")))
        except Exception:
            try:
                from pdf2image import convert_from_bytes
                img = convert_from_bytes(fb, dpi=300)[0]
            except Exception as e:
                raise RuntimeError(f"Cannot render PDF: {e}")
        return _ocr_image(img)

    else:
        # Image file — straight OCR
        from PIL import Image
        img = Image.open(BytesIO(fb))
        return _ocr_image(img)

def _ocr_image(img) -> str:
    import shutil
    try:
        import pytesseract
    except ImportError:
        raise ImportError("Install pytesseract: pip install pytesseract")
    if shutil.which("tesseract") is None:
        for p in [r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                  r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p; break
    return pytesseract.image_to_string(img, lang="eng")

def run_ocr(uploaded_file):
    raw = extract_text_from_file(uploaded_file)
    if not raw.strip():
        st.error("Could not extract text from the file.")
        return {}
    result = parse_invoice_text(raw)
    result["_raw_text"] = raw
    return result

def get_my_identity():
    gstin   = get_setting("my_gstin", "29AAAAA1111B1Z1").strip().upper()
    name    = get_setting("my_name",  "Sai Coffee Traders").strip()
    aliases = [name.lower(), name.lower().replace(" ",""), gstin.lower()]
    for w in name.lower().split():
        if len(w) > 3: aliases.append(w)
    return gstin, name, aliases

def parse_invoice_text(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full  = " ".join(lines)

    # ── Numeric amount extractor ───────────────────────────────
    def fa(pats):
        for p in pats:
            m = re.search(p, full, re.IGNORECASE)
            if m:
                try: return float(m.group(1).replace(",","").replace(" ",""))
                except: pass
        return 0.

    # ── GSTIN extraction ───────────────────────────────────────
    GSTIN_RE = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b')
    all_g = list(dict.fromkeys(GSTIN_RE.findall(full.upper())))

    my_g, my_n, MY_A = get_my_identity()

    # ── Find section boundaries using SOLD BY / BILLED TO ─────
    sold_by_idx   = next((i for i,l in enumerate(lines)
                          if re.match(r'sold\s*by', l, re.IGNORECASE)), None)
    billed_to_idx = next((i for i,l in enumerate(lines)
                          if re.match(r'billed?\s*to', l, re.IGNORECASE)), None)

    # ── Vendor name: grab line immediately after the relevant label ──
    def name_after(idx):
        """Return the first non-empty line after idx that looks like a name."""
        if idx is None:
            return None
        for ln in lines[idx+1 : idx+5]:
            lc = ln.strip()
            # Skip lines that are addresses, GSTINs, or "NO GSTIN" markers
            if not lc or len(lc) < 3:
                continue
            if GSTIN_RE.search(lc.upper()):
                continue
            if re.search(r'no\s*gstin|unregistered|gstin\s*:', lc, re.IGNORECASE):
                continue
            if re.search(r'^\d[\d\s\-,]+$', lc):   # pure numbers / pin
                continue
            if any(c.isalpha() for c in lc):
                return lc
        return None

    # For a PURCHASE invoice: vendor = SOLD BY party (not us)
    # For a SALES invoice:    vendor = BILLED TO party (the buyer)
    # We detect invoice type first using GSTIN position and keywords

    # Detect invoice type ─────────────────────────────────────
    def has_me(block_lines):
        b = " ".join(block_lines).lower()
        return my_g.lower() in b or any(a in b for a in MY_A)

    if sold_by_idx is not None and billed_to_idx is not None:
        seller_block = lines[sold_by_idx:billed_to_idx]
        buyer_block  = lines[billed_to_idx:]
    elif billed_to_idx is not None:
        seller_block = lines[:billed_to_idx]
        buyer_block  = lines[billed_to_idx:]
    else:
        mid = len(lines)//2
        seller_block = lines[:mid]; buyer_block = lines[mid:]

    iam_seller = has_me(seller_block)
    iam_buyer  = has_me(buyer_block)

    if   iam_seller and not iam_buyer:                           dt = "Sales Invoice"
    elif iam_buyer  and not iam_seller:                          dt = "Purchase Invoice"
    elif re.search(r'purchase\s*invoice', full, re.IGNORECASE): dt = "Purchase Invoice"
    elif re.search(r'sales\s*invoice',    full, re.IGNORECASE): dt = "Sales Invoice"
    elif re.search(r'tax\s*invoice',      full, re.IGNORECASE): dt = "Sales Invoice"
    elif re.search(r'credit\s*note',      full, re.IGNORECASE): dt = "Credit Note"
    elif re.search(r'debit\s*note',       full, re.IGNORECASE): dt = "Debit Note"
    else: dt = "Purchase Invoice"

    # Vendor = the OTHER party (not us)
    if dt == "Sales Invoice":
        # We are the seller → vendor is the BUYER (Billed To)
        vendor = name_after(billed_to_idx)
    else:
        # We are the buyer → vendor is the SELLER (Sold By)
        vendor = name_after(sold_by_idx)

    # Fallback if label-based lookup failed
    if not vendor:
        # Walk all lines, pick first that isn't us, isn't a label, isn't a GSTIN
        label_re = re.compile(
            r'^(sold\s*by|billed?\s*to|ship\s*to|invoice|date|gstin|phone|email|#|description|qty|rate|cgst|sgst|igst|total|subtotal|taxable|thank|computer|signature|finflow)',
            re.IGNORECASE)
        for ln in lines:
            lc = ln.strip()
            if len(lc) < 3: continue
            if GSTIN_RE.search(lc.upper()): continue
            if re.search(r'no\s*gstin|unregistered', lc, re.IGNORECASE): continue
            if label_re.search(lc): continue
            if any(a in lc.lower() for a in MY_A): continue
            if my_g in lc.upper(): continue
            if re.search(r'^\d[\d\s\-,]+$', lc): continue
            if any(c.isalpha() for c in lc):
                vendor = lc; break
        if not vendor:
            vendor = "Unknown"

    # ── GSTIN of the other party ───────────────────────────────
    gstin = ""
    for g in all_g:
        if g != my_g:
            gstin = g; break
    if not gstin and all_g:
        gstin = all_g[0]

    # ── Date ──────────────────────────────────────────────────
    dm = re.search(r'(?:invoice\s*date|date)[:\s]+(\d{1,2}[-/]\w{3,9}[-/]\d{2,4})', full, re.IGNORECASE)
    if not dm: dm = re.search(r'date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', full, re.IGNORECASE)
    if not dm: dm = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', full)
    if not dm: dm = re.search(r'(\d{1,2}[-/]\w{3}[-/]\d{4})', full)
    ds = dm.group(1).replace("/","-") if dm else date.today().strftime("%d-%m-%Y")

    # ── Amounts ────────────────────────────────────────────────
    total = fa([
        r'GRAND\s*TOTAL\s*[:\s]*Rs\.?\s*([0-9,]+\.?\d*)',
        r'(?:total\s*amount\s*payable|grand\s*total|total\s*amount)[:\sRs.\u20b9]*([0-9,]+\.?\d*)',
        r'total\s*payable[:\sRs.\u20b9]*([0-9,]+\.?\d*)',
        r'(?:amount\s*due|net\s*payable)[:\sRs.\u20b9]*([0-9,]+\.?\d*)',
    ])
    if total == 0.:
        nums = [float(x) for x in re.findall(r'\b\d{1,7}\.\d{2}\b', full)]
        total = max(nums, default=0.)

    sub = fa([
        r'Taxable\s*Amount\s*[:\s]*Rs\.?\s*([0-9,]+\.?\d*)',
        r'(?:taxable\s*value|subtotal|taxable\s*amount)[:\sRs.\u20b9]*([0-9,]+\.?\d*)',
        r'SUBTOTAL\s+([0-9,]+\.?\d*)',
    ])

    hc   = bool(re.search(r'\bCGST\b', full, re.IGNORECASE))
    hs   = bool(re.search(r'\bSGST\b', full, re.IGNORECASE))
    hi   = bool(re.search(r'\bIGST\b', full, re.IGNORECASE))

    cgst = fa([r'CGST\b[^0-9]*([0-9,]{2,}\.?\d*)',
               r'CGST\s*@[^0-9]*([0-9,]{2,}\.?\d*)'  ]) if hc else 0.
    sgst = fa([r'SGST\b[^0-9]*([0-9,]{2,}\.?\d*)',
               r'SGST\s*@[^0-9]*([0-9,]{2,}\.?\d*)'  ]) if hs else 0.
    igst = fa([r'IGST\b[^0-9]*([0-9,]{2,}\.?\d*)',
               r'IGST\s*@[^0-9]*([0-9,]{2,}\.?\d*)'  ]) if hi else 0.

    # Reconcile sub/tax/total
    tax = cgst + sgst + igst
    if sub == 0. and total > 0 and tax > 0:
        sub = round(total - tax, 2)
    elif sub == 0. and total > 0:
        sub = total
    if tax > 0:
        if not hi and (hc or hs) and cgst == 0. and sgst == 0.:
            cgst = sgst = round(tax / 2, 2)
        elif hi and not hc and not hs and igst == 0.:
            igst = tax

    found = sum([vendor != "Unknown", bool(gstin), total > 0,
                 sub > 0, tax > 0, iam_seller or iam_buyer])
    return {
        "vendor": vendor, "date": ds, "gstin": gstin, "doc_type": dt,
        "subtotal": sub, "cgst": cgst, "sgst": sgst, "igst": igst, "total": total,
        "confidence": min(50 + found * 8, 97),
        "detected_by": "Label Match" if (sold_by_idx is not None or billed_to_idx is not None) else "Keyword",
            "has_cgst":hc,"has_sgst":hs,"has_igst":hi}

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def show_login():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.4rem;
            background:linear-gradient(135deg,#00E5A0,#7B61FF);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">FinFlow</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#5A6075;
            letter-spacing:0.15em;margin-top:0.3rem;">GST REGISTER · SIGN IN</div>
    </div>""", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        tab_in, tab_reg = st.tabs(["Sign In", "Create Account"])

        with tab_in:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                sub = st.form_submit_button("Sign In →", use_container_width=True)
                if sub:
                    db = get_user_db(); u = username.strip().lower()
                    if u in db and db[u]["password"] == password:
                        st.session_state.logged_in  = True
                        st.session_state.username   = u
                        st.session_state.user_name  = db[u]["name"]
                        st.session_state.user_color = db[u].get("color","#00E5A0")
                        st.session_state.page       = "Dashboard"
                        st.success(f"Welcome back, {db[u]['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            

        with tab_reg:
            with st.form("reg_form"):
                nu  = st.text_input("Choose Username", placeholder="e.g. john_trader")
                fn  = st.text_input("Full Name",       placeholder="e.g. John Doe")
                np1 = st.text_input("New Password",    type="password")
                np2 = st.text_input("Confirm Password",type="password")
                rs  = st.form_submit_button("Create Account →", use_container_width=True)
                if rs:
                    db = get_user_db(); un = nu.strip().lower()
                    ok, _ = validate_password(np1)
                    if not un or not fn.strip():
                        st.error("Username and full name are required.")
                    elif un in db:
                        st.error("Username already exists.")
                    elif not ok:
                        st.error("Password does not meet requirements.")
                    elif np1 != np2:
                        st.error("Passwords do not match.")
                    else:
                        db[un] = {"password": np1, "name": fn.strip(), "color": "#00E5A0"}
                        save_user_db()
                        # init settings file for new user
                        _save_user_key(un, "settings", EMPTY_SETTINGS.copy())
                        st.success(f"Account created! Sign in as **{un}**")
            st.markdown("""
            <div style="margin-top:0.8rem;background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);
                border-radius:10px;padding:0.8rem 1rem;font-family:'DM Mono',monospace;font-size:0.75rem;">
                <div style="color:#7B61FF;font-weight:600;margin-bottom:0.4rem;">PASSWORD RULES</div>
                <div style="color:#5A6075;">✓ 6-12 characters total</div>
                <div style="color:#5A6075;">✓ At least 1 UPPERCASE letter</div>
                <div style="color:#5A6075;">✓ At least 1 special character (!@#$%^&*...)</div>
            </div>""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    show_login(); st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    color = st.session_state.user_color
    st.markdown(f"""
    <div style="padding:0.9rem 1rem;background:var(--surface2);border:1px solid var(--border);
        border-radius:10px;margin-bottom:1rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;">
            <div style="width:34px;height:34px;border-radius:50%;
                background:linear-gradient(135deg,{color},{color}88);
                display:flex;align-items:center;justify-content:center;
                font-weight:800;font-size:0.95rem;color:#0A0C10;">
                {st.session_state.user_name[0].upper()}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.88rem;color:#E8ECF4;">
                    {st.session_state.user_name}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:{color};
                    text-transform:uppercase;letter-spacing:0.1em;">Admin</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        for k in ["logged_in","username","user_name","user_color","extracted","upload_rejected","reject_reason"]:
            st.session_state[k] = False if k == "logged_in" else ""
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="padding:0.5rem 0 1.2rem;">
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
            background:linear-gradient(135deg,#00E5A0,#7B61FF);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">FinFlow</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#5A6075;
            letter-spacing:0.15em;text-transform:uppercase;">GST Sales & Purchase Register</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    PAGES = [("📊","Dashboard"),("📤","Upload & Extract"),("✏️","Manual Entry"),
             ("📋","Purchase Register"),("💰","Sales Register"),("🔄","Reconciliation"),
             ("📄","GSTR-1 Report"),("📑","GSTR-3B Report"),("🔍","GSTR-2A / 2B"),
             ("📖","User Guide"),("⚙️","Settings")]

    for icon, internal in PAGES:
        if st.button(f"{icon}  {internal}", key=f"nav_{internal}", use_container_width=True):
            st.session_state.page = internal
            st.session_state.upload_rejected = False
            st.session_state.reject_reason   = ""
            st.rerun()

    st.markdown("---")
    tx = get_tax_summary()
    net_color = "#FF6B6B" if tx["net_tax"] > 0 else "#00E5A0"
    st.markdown(f"""
    <div style="padding:0.75rem;background:var(--surface2);border-radius:10px;
        border:1px solid var(--border);font-size:0.82rem;">
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#5A6075;
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;">Quick Stats</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="color:#5A6075;">📥 Purchases</span>
            <span style="color:#FFB547;font-family:'DM Mono',monospace;font-weight:600;">{tx['p_count']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="color:#5A6075;">📤 Sales</span>
            <span style="color:#00E5A0;font-family:'DM Mono',monospace;font-weight:600;">{tx['s_count']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#5A6075;">Net Tax Due</span>
            <span style="color:{net_color};font-family:'DM Mono',monospace;font-weight:700;">Rs.{tx['net_tax']:,.0f}</span>
        </div>
    </div>
    <div style="margin-top:0.6rem;padding:0.5rem 0.75rem;background:rgba(0,229,160,0.05);
        border-radius:8px;border:1px solid rgba(0,229,160,0.15);">
        <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#5A6075;">
        💾 Data saved to disk — persists across page reloads</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────
page = st.session_state.page

# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("## 📊 Dashboard")
    st.caption("GST Sales & Purchase Register overview")
    tx = get_tax_summary()
    profit    = tx["s_total"] - tx["p_total"]
    net_label = "Tax Payable" if tx["net_tax"] > 0 else "Tax Refund"
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📥 Total Purchases", f"Rs.{tx['p_total']:,.0f}", f"{tx['p_count']} invoices")
    c2.metric("📤 Total Sales",     f"Rs.{tx['s_total']:,.0f}", f"{tx['s_count']} invoices")
    c3.metric("💹 Gross Margin",    f"Rs.{profit:,.0f}", "Sales minus Purchases")
    c4.metric(f"🧾 {net_label}",    f"Rs.{abs(tx['net_tax']):,.0f}", "Output − Input tax")
    st.markdown("---")
    l,r = st.columns(2)
    with l:
        st.markdown("**🧾 GST Tax Breakdown**")
        st.dataframe(pd.DataFrame({
            "Tax":           ["CGST","SGST","IGST","TOTAL"],
            "Purchase(In)":  [fmt_inr(tx["p_cgst"]),fmt_inr(tx["p_sgst"]),fmt_inr(tx["p_igst"]),fmt_inr(tx["p_cgst"]+tx["p_sgst"]+tx["p_igst"])],
            "Sales(Out)":    [fmt_inr(tx["s_cgst"]),fmt_inr(tx["s_sgst"]),fmt_inr(tx["s_igst"]),fmt_inr(tx["s_cgst"]+tx["s_sgst"]+tx["s_igst"])],
            "Net Due":       [fmt_inr(tx["net_cgst"]),fmt_inr(tx["net_sgst"]),fmt_inr(tx["net_igst"]),fmt_inr(tx["net_tax"])],
        }), use_container_width=True, hide_index=True)
        if tx["net_tax"] > 0: st.warning(f"⚠️ Rs.{tx['net_tax']:,.2f} payable to government")
        else:                  st.success(f"✅ Input credit exceeds output — carry forward Rs.{abs(tx['net_tax']):,.2f}")
    with r:
        st.markdown("**📊 Sales vs Purchases**")
        st.bar_chart(pd.DataFrame({"Amount":[tx["p_total"],tx["s_total"]]},
                                   index=["Purchases","Sales"]), color="#00E5A0")
    p = get_register("purchase_register"); s = get_register("sales_register")
    if not p.empty or not s.empty:
        st.markdown("---"); st.markdown("**🕒 Recent Activity**")
        comb = pd.concat([
            p.assign(Type="📥 Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Type="📤 Sales")    if not s.empty else pd.DataFrame()
        ]).sort_values("Date", ascending=False).head(8)
        disp = comb[["ID","Date","Vendor","Type","Total","Status"]].copy()
        disp["Total"] = disp["Total"].apply(lambda x: f"Rs.{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# UPLOAD & EXTRACT  — with error-invoice rejection
# ══════════════════════════════════════════════
elif page == "Upload & Extract":
    st.markdown("## 📤 Upload & Extract")
    st.caption("Upload your invoice — the system validates GSTIN compliance before accepting.")

    # Explain the error-rejection feature
    st.info(
        "🛡️ **Smart Validation Active** — Invoices from unregistered suppliers "
        "(no GSTIN), Composition scheme dealers, or those with invalid/fake GSTINs "
        "will be **automatically rejected**. Only compliant invoices are accepted into the register."
    )

    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        uf = st.file_uploader("Drop invoice here", type=["pdf","png","jpg","jpeg"])

        if uf:
            st.success(f"✓ {uf.name} ({uf.size//1024} KB)")
            ext = uf.name.lower().rsplit(".", 1)[-1]
            if ext in ("png","jpg","jpeg"):
                st.image(uf, width=380); uf.seek(0)
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔍 Extract & Validate", use_container_width=True):
                # Reset previous state
                st.session_state.upload_rejected = False
                st.session_state.reject_reason   = ""
                st.session_state.extracted       = None

                with st.spinner("Reading & validating invoice..."):
                    try:
                        uf.seek(0)
                        ext_d = run_ocr(uf)
                        if ext_d:
                            is_valid, reason = validate_invoice_before_upload(ext_d)
                            if not is_valid:
                                st.session_state.upload_rejected = True
                                st.session_state.reject_reason   = reason
                            else:
                                st.session_state.extracted = ext_d
                                st.success("✓ Validation passed — extraction complete!")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

        # ── REJECTION PANEL ──────────────────────────────────
        if st.session_state.get("upload_rejected"):
            st.markdown("---")
            reason = st.session_state.reject_reason
            st.markdown(f"""
            <div class="reject-box">
                <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;
                    color:#FF4444;margin-bottom:0.6rem;">
                    ❌ INVOICE REJECTED — UPLOAD NOT ALLOWED
                </div>
                <div style="font-size:0.9rem;color:#E8ECF4;line-height:1.7;">
                    {reason.replace(chr(10),'<br/>').replace('**','<b>').replace('**','</b>')}
                </div>
            </div>""", unsafe_allow_html=True)

            st.error("**This invoice has NOT been added to your register.**")
            st.markdown("""
            **What to do next:**
            - Ask your supplier for a corrected invoice showing their valid GSTIN
            - Verify supplier registration at [gstin.gov.in](https://www.gstin.gov.in)
            - If supplier is unregistered, ask them to register under GST
            - For Composition dealers — request an invoice **without GST** (you pay full price, no ITC)
            """)

        # ── EXTRACTED DATA DISPLAY ───────────────────────────
        if st.session_state.extracted and not st.session_state.get("upload_rejected"):
            ed = st.session_state.extracted
            conf  = ed.get("confidence", 80)
            dtype = ed.get("doc_type", "Purchase Invoice")
            hc    = ed.get("has_cgst", True)
            hs_   = ed.get("has_sgst", True)
            hi    = ed.get("has_igst", False)

            st.markdown("---"); st.markdown("**🔎 Extracted Fields**")
            bc   = "#00E5A0" if "Sales" in dtype else "#FFB547"
            dest = "Sales Register" if "Sales" in dtype else "Purchase Register"
            st.markdown(f"""<div style="display:inline-block;padding:0.3rem 0.9rem;border-radius:100px;
                background:rgba(0,229,160,0.1);border:1px solid {bc};color:{bc};
                font-family:'DM Mono',monospace;font-size:0.78rem;font-weight:600;margin-bottom:0.75rem;">
                {'📤' if 'Sales' in dtype else '📥'} {dtype} → {dest}</div>""",
                unsafe_allow_html=True)

            bc2 = "#00E5A0" if conf >= 80 else "#FFB547" if conf >= 60 else "#FF6B6B"
            st.markdown(f"""<div style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#5A6075;margin-bottom:0.3rem;">
                    <span>OCR Confidence</span><span style="color:{bc2};font-weight:600;">{conf}%</span></div>
                <div style="height:5px;background:#1E2330;border-radius:100px;">
                    <div style="height:100%;width:{conf}%;background:{bc2};border-radius:100px;"></div></div></div>""",
                unsafe_allow_html=True)

            fields = [
                ("Vendor / Party",  ed.get("vendor","")),
                ("Invoice Type",    dtype),
                ("Date",            ed.get("date","")),
                ("GSTIN",           ed.get("gstin","") or "⚠️ No GSTIN"),
                ("Subtotal",        fmt_inr(ed.get("subtotal",0))),
            ]
            if hc:  fields.append(("CGST",  fmt_inr(ed.get("cgst",0))))
            if hs_: fields.append(("SGST",  fmt_inr(ed.get("sgst",0))))
            if hi:  fields.append(("IGST",  fmt_inr(ed.get("igst",0))))
            fields.append(("Total Amount", fmt_inr(ed.get("total",0))))
            st.table(pd.DataFrame(fields, columns=["Field","Value"]))

    with c2:
        st.markdown("**✏️ Review & Confirm**")
        if st.session_state.extracted and not st.session_state.get("upload_rejected"):
            ed = st.session_state.extracted
            hc = ed.get("has_cgst",True); hs_ = ed.get("has_sgst",True); hi = ed.get("has_igst",False)
            with st.form("confirm_form"):
                vendor   = st.text_input("Vendor / Party Name", value=ed.get("vendor",""))
                EN_TYPES = ["Purchase Invoice","Sales Invoice","Credit Note","Debit Note","Expense Receipt"]
                doc_type = st.selectbox("Invoice Type", EN_TYPES)
                txn_date = st.text_input("Date", value=ed.get("date",""))
                gstin    = st.text_input("GSTIN", value=ed.get("gstin",""))
                sub      = st.number_input("Subtotal (Rs.)", value=float(ed.get("subtotal",0)),  min_value=0., step=0.01)
                cgst = sgst = igst = 0.
                if hc and not hi:  cgst = st.number_input("CGST (Rs.)", value=float(ed.get("cgst",0)),  min_value=0., step=0.01)
                if hs_ and not hi: sgst = st.number_input("SGST (Rs.)", value=float(ed.get("sgst",0)),  min_value=0., step=0.01)
                if hi:             igst = st.number_input("IGST (Rs.)", value=float(ed.get("igst",0)),  min_value=0., step=0.01)
                if not hc and not hs_ and not hi:
                    cgst = st.number_input("CGST (Rs.)", value=0., min_value=0., step=0.01)
                    sgst = st.number_input("SGST (Rs.)", value=0., min_value=0., step=0.01)
                    igst = st.number_input("IGST (Rs.)", value=0., min_value=0., step=0.01)
                total_c = sub + cgst + sgst + igst
                st.metric("Calculated Total", fmt_inr(total_c))
                if st.form_submit_button("✅ Confirm & Add to Register", use_container_width=True):
                    data = {"vendor":vendor,"date":txn_date,"gstin":gstin,
                            "subtotal":sub,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total_c}
                    txn_id, reg = add_to_register(data, doc_type)
                    st.session_state.extracted = None
                    rn = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"✓ {txn_id} added to **{rn}**!")
        elif st.session_state.get("upload_rejected"):
            st.markdown("""
            <div style="padding:1.2rem;background:rgba(204,0,0,0.08);border:1px solid #CC0000;
                border-radius:10px;text-align:center;">
                <div style="font-size:2rem;">🚫</div>
                <div style="color:#FF4444;font-family:'Syne',sans-serif;font-weight:700;margin-top:0.4rem;">
                    Upload Rejected</div>
                <div style="color:#5A6075;font-size:0.82rem;margin-top:0.4rem;">
                    This invoice cannot be added to the register.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Upload a document and click Extract to see data here.")

# ══════════════════════════════════════════════
# MANUAL ENTRY
# ══════════════════════════════════════════════
elif page == "Manual Entry":
    st.markdown("## ✏️ Manual Entry")
    c1, c2 = st.columns(2)
    with c1:
        EN_TYPES = ["Purchase Invoice","Sales Invoice","Expense Receipt","Credit Note","Debit Note"]
        with st.form("manual_form"):
            doc_type = st.selectbox("Invoice Type", EN_TYPES)
            vendor   = st.text_input("Vendor / Party Name")
            txn_date = st.date_input("Date", value=date.today())
            gstin    = st.text_input("GSTIN (optional)")
            cc1, cc2 = st.columns(2)
            with cc1:
                sub = st.number_input("Subtotal (Rs.)", min_value=0., value=1000., step=1.)
                cp  = st.number_input("CGST %", min_value=0., max_value=28., value=0., step=0.5)
            with cc2:
                sp = st.number_input("SGST %", min_value=0., max_value=28., value=0., step=0.5)
                ip = st.number_input("IGST %", min_value=0., max_value=28., value=0., step=0.5)
            cgst  = round(sub * cp / 100, 2)
            sgst  = round(sub * sp / 100, 2)
            igst  = round(sub * ip / 100, 2)
            total = sub + cgst + sgst + igst
            st.metric("Calculated Total", fmt_inr(total))
            if st.form_submit_button("➕ Add Entry", use_container_width=True):
                if not vendor:
                    st.error("Vendor name is required.")
                else:
                    data = {"vendor":vendor,"date":txn_date.strftime("%d-%m-%Y"),
                            "gstin":gstin,"subtotal":sub,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total}
                    txn_id, reg = add_to_register(data, doc_type)
                    rn = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"✓ {txn_id} added to **{rn}**!")
    with c2:
        st.markdown("**📌 Recent Entries**")
        p = get_register("purchase_register"); s = get_register("sales_register")
        if not p.empty or not s.empty:
            comb = pd.concat([
                p.assign(Type="📥 Purchase") if not p.empty else pd.DataFrame(),
                s.assign(Type="📤 Sales")    if not s.empty else pd.DataFrame()
            ]).tail(8)[["ID","Vendor","Type","Total"]].copy()
            comb["Total"] = comb["Total"].apply(lambda x: f"Rs.{float(x):,.2f}")
            st.dataframe(comb, use_container_width=True, hide_index=True)
        else:
            st.info("No entries yet.")

# ══════════════════════════════════════════════
# PURCHASE REGISTER
# ══════════════════════════════════════════════
elif page == "Purchase Register":
    st.markdown("## 📋 Purchase Register")
    st.caption("All invoices where you are the buyer — Input Tax Credit (ITC) eligible.")
    df = get_register("purchase_register")
    if df.empty:
        st.info("No purchase entries yet. Upload purchase invoices or add manually.")
    else:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total Purchases",   f"Rs.{df['Total'].astype(float).sum():,.2f}")
        m2.metric("Input CGST (ITC)",  f"Rs.{df['CGST'].astype(float).sum():,.2f}")
        m3.metric("Input SGST (ITC)",  f"Rs.{df['SGST'].astype(float).sum():,.2f}")
        m4.metric("Total Entries",     len(df))
        st.markdown("---")
        search = st.text_input("🔍 Search vendor")
        if search: df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for c in ["Subtotal","CGST","SGST","IGST","Total"]:
            disp[c] = disp[c].apply(lambda x: f"Rs.{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button("⬇️ Export CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"purchase_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")

# ══════════════════════════════════════════════
# SALES REGISTER
# ══════════════════════════════════════════════
elif page == "Sales Register":
    st.markdown("## 💰 Sales Register")
    st.caption("All invoices where you are the seller — Output Tax collected from customers.")
    df = get_register("sales_register")
    if df.empty:
        st.info("No sales entries yet. Upload sales invoices or add manually.")
    else:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total Sales",    f"Rs.{df['Total'].astype(float).sum():,.2f}")
        m2.metric("Output CGST",    f"Rs.{df['CGST'].astype(float).sum():,.2f}")
        m3.metric("Output SGST",    f"Rs.{df['SGST'].astype(float).sum():,.2f}")
        m4.metric("Total Entries",  len(df))
        st.markdown("---")
        search = st.text_input("🔍 Search buyer")
        if search: df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for c in ["Subtotal","CGST","SGST","IGST","Total"]:
            disp[c] = disp[c].apply(lambda x: f"Rs.{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button("⬇️ Export CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"sales_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")

# ══════════════════════════════════════════════
# RECONCILIATION
# ══════════════════════════════════════════════
elif page == "Reconciliation":
    st.markdown("## 🔄 GST Reconciliation")
    tx = get_tax_summary()
    p  = get_register("purchase_register")
    s  = get_register("sales_register")
    if p.empty and s.empty:
        st.info("Add purchase and sales entries to run reconciliation.")
    else:
        st.markdown("**📊 Full Tax Statement**")
        st.dataframe(pd.DataFrame({
            "Tax Head":             ["CGST","SGST","IGST","TOTAL"],
            "Input Tax (Purchase)": [fmt_inr(tx["p_cgst"]),fmt_inr(tx["p_sgst"]),fmt_inr(tx["p_igst"]),fmt_inr(tx["p_cgst"]+tx["p_sgst"]+tx["p_igst"])],
            "Output Tax (Sales)":   [fmt_inr(tx["s_cgst"]),fmt_inr(tx["s_sgst"]),fmt_inr(tx["s_igst"]),fmt_inr(tx["s_cgst"]+tx["s_sgst"]+tx["s_igst"])],
            "Net Payable":          [fmt_inr(tx["net_cgst"]),fmt_inr(tx["net_sgst"]),fmt_inr(tx["net_igst"]),fmt_inr(tx["net_tax"])],
        }), use_container_width=True, hide_index=True)
        if tx["net_tax"] > 0:
            st.error(f"⚠️ Net GST Payable to Government: Rs.{tx['net_tax']:,.2f} — Pay by 20th of next month.")
        else:
            st.success(f"✅ Input Tax Credit exceeds Output Tax by Rs.{abs(tx['net_tax']):,.2f} — Carry forward.")
        st.markdown("---"); st.markdown("**✅ GSTIN Validation**")
        all_df = pd.concat([
            p.assign(Register="Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Register="Sales")    if not s.empty else pd.DataFrame()
        ])
        g = all_df[["ID","Vendor","GSTIN","Register"]].copy()
        def chk(x):
            if not x or str(x).strip()=="" or str(x)=="nan": return "❌ No GSTIN"
            elif VALID_GSTIN_RE.match(str(x).upper()): return "✅ Valid"
            else: return "⚠️ Invalid Format"
        g["Valid"] = g["GSTIN"].apply(chk)
        st.dataframe(g, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# GSTR-1
# ══════════════════════════════════════════════
elif page == "GSTR-1 Report":
    st.markdown("## 📄 GSTR-1 — Outward Supplies")
    st.caption("Statement of outward supplies — file by 11th of following month.")
    sdf = get_register("sales_register")
    if sdf.empty:
        st.warning("No sales data. Add sales invoices to generate GSTR-1.")
    else:
        df = sdf.copy()
        for c in ["CGST","SGST","IGST","Subtotal","Total"]: df[c] = df[c].astype(float)
        b2b = df[df["GSTIN"].str.strip().str.len() > 5] if "GSTIN" in df.columns else pd.DataFrame()
        b2c = df[~df.index.isin(b2b.index)]
        k1,k2,k3,k4,k5 = st.columns(5)
        k1.metric("Taxable Turnover", fmt_inr(df["Subtotal"].sum()))
        k2.metric("CGST", fmt_inr(df["CGST"].sum()))
        k3.metric("SGST", fmt_inr(df["SGST"].sum()))
        k4.metric("IGST", fmt_inr(df["IGST"].sum()))
        k5.metric("Grand Total", fmt_inr(df["Total"].sum()))
        st.markdown("---")
        tb1,tb2,tb3 = st.tabs(["📦 B2B Invoices","🛒 B2C Invoices","📋 Full Table"])
        with tb1:
            if b2b.empty: st.info("No B2B invoices.")
            else:
                d = b2b[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: d[c] = d[c].apply(fmt_inr)
                st.dataframe(d, use_container_width=True, hide_index=True)
        with tb2:
            if b2c.empty: st.info("No B2C invoices.")
            else:
                d = b2c[["ID","Date","Vendor","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: d[c] = d[c].apply(fmt_inr)
                st.dataframe(d, use_container_width=True, hide_index=True)
        with tb3:
            d = sdf[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total","Status"]].copy()
            for c in ["Subtotal","CGST","SGST","IGST","Total"]: d[c] = d[c].apply(fmt_inr)
            st.dataframe(d, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download GSTR-1 CSV", data=sdf.to_csv(index=False).encode(),
            file_name=f"GSTR1_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv",
            use_container_width=True)

# ══════════════════════════════════════════════
# GSTR-3B
# ══════════════════════════════════════════════
elif page == "GSTR-3B Report":
    st.markdown("## 📑 GSTR-3B — Monthly Summary Return")
    st.caption("Self-declaration of net tax payable — file by 20th of following month.")
    st.warning("⚠️ Output tax − ITC = Net tax payable. 18% p.a. interest on late payment.")
    sdf = get_register("sales_register"); pdf = get_register("purchase_register")
    if sdf.empty and pdf.empty:
        st.info("Add sales and purchase entries to generate GSTR-3B.")
    else:
        def sm(df):
            if df.empty: return 0.,0.,0.,0.
            return (df["Subtotal"].astype(float).sum(), df["CGST"].astype(float).sum(),
                    df["SGST"].astype(float).sum(), df["IGST"].astype(float).sum())
        ss,sc,sg,si = sm(sdf); ps,pc,pg,pi = sm(pdf)
        d = {"out_taxable":ss,"out_cgst":sc,"out_sgst":sg,"out_igst":si,
             "itc_taxable":ps,"itc_cgst":pc,"itc_sgst":pg,"itc_igst":pi,
             "net_cgst":round(sc-pc,2),"net_sgst":round(sg-pg,2),
             "net_igst":round(si-pi,2),"net_total":round((sc+sg+si)-(pc+pg+pi),2)}
        tb1,tb2,tb3 = st.tabs(["📋 3.1 Output Tax","📥 4. ITC Available","💰 Net Tax Payable"])
        with tb1:
            st.dataframe(pd.DataFrame([
                {"Section":"3.1(a)","Nature":"Outward taxable supplies",
                 "Taxable":fmt_inr(d["out_taxable"]),"CGST":fmt_inr(d["out_cgst"]),
                 "SGST":fmt_inr(d["out_sgst"]),"IGST":fmt_inr(d["out_igst"])},
                {"Section":"3.1(b)","Nature":"Zero rated supplies",
                 "Taxable":"Rs.0.00","CGST":"Rs.0.00","SGST":"Rs.0.00","IGST":"Rs.0.00"},
            ]), use_container_width=True, hide_index=True)
        with tb2:
            st.dataframe(pd.DataFrame([
                {"Section":"4(A)(5)","Nature":"All other ITC (domestic)",
                 "Taxable":fmt_inr(d["itc_taxable"]),"CGST":fmt_inr(d["itc_cgst"]),
                 "SGST":fmt_inr(d["itc_sgst"]),"IGST":fmt_inr(d["itc_igst"])},
            ]), use_container_width=True, hide_index=True)
        with tb3:
            st.dataframe(pd.DataFrame([
                {"":"","Nature":"Output Tax Liability",
                 "CGST":fmt_inr(d["out_cgst"]),"SGST":fmt_inr(d["out_sgst"]),
                 "IGST":fmt_inr(d["out_igst"]),"Total":fmt_inr(d["out_cgst"]+d["out_sgst"]+d["out_igst"])},
                {"":"","Nature":"Less: ITC Available",
                 "CGST":f"(-) {fmt_inr(d['itc_cgst'])}","SGST":f"(-) {fmt_inr(d['itc_sgst'])}",
                 "IGST":f"(-) {fmt_inr(d['itc_igst'])}","Total":f"(-) {fmt_inr(d['itc_cgst']+d['itc_sgst']+d['itc_igst'])}"},
                {"":"","Nature":"NET TAX PAYABLE",
                 "CGST":fmt_inr(d["net_cgst"]),"SGST":fmt_inr(d["net_sgst"]),
                 "IGST":fmt_inr(d["net_igst"]),"Total":fmt_inr(d["net_total"])},
            ]), use_container_width=True, hide_index=True)
            if d["net_total"] > 0:
                st.error(f"You owe Rs.{d['net_total']:,.2f} in GST. Pay via GSTN portal by 20th.")
            else:
                st.success(f"Excess ITC of Rs.{abs(d['net_total']):,.2f} — carry forward to next period.")

# ══════════════════════════════════════════════
# USER GUIDE
# ══════════════════════════════════════════════
elif page == "User Guide":
    st.markdown("## 📖 User Guide")
    st.markdown("---")
    st.markdown("**📋 How FinFlow Works**")
    st.markdown("**Invoice → OCR Reads → Validate GSTIN → Auto Sort → Dashboard → File GST**")
    st.markdown("---")
    steps = [
        ("1️⃣ Upload Invoice", "Go to 📤 Upload & Extract → Select PDF or image → Click 🔍 Extract & Validate."),
        ("2️⃣ Validation", "System checks GSTIN compliance. Error invoices (no GSTIN, Composition, fake GSTIN) are automatically rejected."),
        ("3️⃣ Review & Confirm", "Check vendor name, amounts, CGST/SGST/IGST → Fix errors → Click ✅ Confirm & Add."),
        ("4️⃣ Check Registers", "📋 Purchase Register = bills you paid | 💰 Sales Register = bills you raised."),
        ("5️⃣ View Dashboard", "📊 Dashboard shows total purchases, sales, and net GST payable automatically."),
        ("6️⃣ GST Reports", "📄 GSTR-1 for sales | 📑 GSTR-3B for net tax payable → Download CSV → File on GST portal."),
        ("7️⃣ Persistent Data", "💾 All data is saved to disk in the finflow_data/ folder — survives page reloads and browser restarts."),
    ]
    for title, desc in steps:
        st.markdown(f"**{title}**  \n{desc}"); st.markdown("---")
    cy, cn = st.columns(2)
    with cy:
        st.success("**✅ ITC Can Be Claimed**\n\n✔ Supplier has valid GSTIN\n\n✔ They filed GSTR-1\n\n✔ Invoice shows GST amount\n\n✔ Appears in your GSTR-2A")
    with cn:
        st.error("**❌ ITC Cannot Be Claimed**\n\n✘ Supplier has NO GSTIN\n\n✘ Composition Scheme dealer\n\n✘ Tax charged without GSTIN (ILLEGAL)\n\n✘ Supplier hasn't filed GSTR-1")
    st.warning("⚠️ A supplier without a GSTIN cannot legally collect GST. Demand a corrected invoice.")
    st.markdown("---")
    st.markdown("**❓ FAQ**")
    for q, a in [
        ("Why was my invoice rejected?", "The invoice either has no GSTIN but charges GST (illegal), is from a Composition scheme dealer, or has an invalid GSTIN format."),
        ("Where is my data saved?", "All data is saved to a finflow_data/ folder on the server disk. It persists across page reloads, browser restarts, and logouts."),
        ("What is ITC?", "Input Tax Credit — GST you paid on purchases deducted from GST collected on sales. You only pay the difference to the government."),
        ("How often to file GST?", "GSTR-1 by 11th | GSTR-3B by 20th of the following month. Late = Rs.50/day + 18% annual interest."),
    ]:
        with st.expander(f"❓ {q}"): st.write(a)

# ══════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════
elif page == "Settings":
    st.markdown("## ⚙️ Settings")
    st.caption("Your business details — used to auto-detect Sales vs Purchase invoices.")
    tb_b, tb_p = st.tabs(["🏢 Business Identity", "🔑 Change Password"])

    with tb_b:
        st.markdown("**Current Business Identity**")
        st.table(pd.DataFrame([
            ("Business Name", get_setting("my_name","Sai Coffee Traders")),
            ("GSTIN",         get_setting("my_gstin","29AAAAA1111B1Z1")),
            ("City",          get_setting("my_city","Dharwad")),
            ("State",         get_setting("my_state","Karnataka")),
        ], columns=["Field","Value"]))
        st.markdown("---"); st.markdown("**✏️ Update Details**")
        with st.form("settings_form"):
            cc1, cc2 = st.columns(2)
            with cc1:
                nn = st.text_input("Business Name", value=get_setting("my_name","Sai Coffee Traders"))
                nc = st.text_input("City",          value=get_setting("my_city","Dharwad"))
            with cc2:
                ng = st.text_input("My GSTIN", value=get_setting("my_gstin","29AAAAA1111B1Z1"), max_chars=15).strip().upper()
                ns = st.text_input("State",    value=get_setting("my_state","Karnataka"))
            if ng:
                if VALID_GSTIN_RE.match(ng): st.success("✅ Valid GSTIN format")
                else: st.warning("⚠️ Format looks off — should be 15 chars like 29ABCDE1234F1Z5")
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                if not nn.strip(): st.error("Business name cannot be empty.")
                elif not ng.strip(): st.error("GSTIN cannot be empty.")
                else:
                    save_setting_val("my_gstin", ng); save_setting_val("my_name", nn.strip())
                    save_setting_val("my_city",  nc.strip()); save_setting_val("my_state", ns.strip())
                    st.success(f"✅ Saved! Using **{nn}** ({ng}) for invoice detection.")
                    st.rerun()

    with tb_p:
        st.markdown("**🔑 Change Your Password**")
        with st.form("change_pwd_form"):
            op  = st.text_input("Current Password",  type="password")
            np1 = st.text_input("New Password",      type="password", help="6-12 chars, 1 uppercase, 1 special")
            np2 = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("🔒 Update Password", use_container_width=True):
                db = get_user_db(); u = st.session_state.username
                if db[u]["password"] != op:
                    st.error("Current password is incorrect.")
                elif np1 != np2:
                    st.error("Passwords do not match.")
                else:
                    ok, rules = validate_password(np1)
                    if not ok:
                        failed = [msg for _, passed, msg in rules if not passed]
                        st.error("; ".join(failed))
                    else:
                        db[u]["password"] = np1
                        save_user_db()
                        st.success("✅ Password updated successfully!")
        st.markdown("""
        <div style="margin-top:0.8rem;background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);
            border-radius:10px;padding:0.8rem 1rem;font-family:'DM Mono',monospace;font-size:0.75rem;">
            <div style="color:#7B61FF;font-weight:600;margin-bottom:0.4rem;">PASSWORD RULES</div>
            <div style="color:#5A6075;">✓ 6-12 characters total</div>
            <div style="color:#5A6075;">✓ At least 1 UPPERCASE letter (A-Z)</div>
            <div style="color:#5A6075;">✓ At least 1 special character (!@#$%^&*...)</div>
        </div>""", unsafe_allow_html=True)

elif page == "GSTR-2A / 2B":
    st.markdown("## 🔍 GSTR-2A / 2B — Inward Supplies ITC")
    st.caption("Auto-populated from your suppliers' GSTR-1 filings.")
    pdf = get_register("purchase_register"); g2a = get_gstr2a()
    tb1,tb2,tb3,tb4 = st.tabs(["📡 GSTR-2A","🔒 GSTR-2B","🔍 Reconciliation","➕ Add 2A Entry"])
    with tb4:
        with st.form("add_2a_form"):
            cc1, cc2 = st.columns(2)
            with cc1:
                sg = st.text_input("Supplier GSTIN"); sv = st.text_input("Supplier Name")
                si = st.text_input("Invoice Number"); sd = st.date_input("Invoice Date", value=date.today())
            with cc2:
                stx = st.number_input("Taxable Value (Rs.)", min_value=0., value=1000., step=1.)
                sc_ = st.number_input("CGST (Rs.)", min_value=0., value=0., step=0.01)
                ss_ = st.number_input("SGST (Rs.)", min_value=0., value=0., step=0.01)
                si_ = st.number_input("IGST (Rs.)", min_value=0., value=0., step=0.01)
            st_ = stx + sc_ + ss_ + si_
            if st.form_submit_button("➕ Add to GSTR-2A", use_container_width=True):
                nr = {"GSTIN":sg,"Vendor":sv,"InvoiceNo":si,"Date":sd.strftime("%d-%m-%Y"),
                      "Taxable":stx,"CGST":sc_,"SGST":ss_,"IGST":si_,"Total":st_,"Source":"GSTR-2A"}
                upd = pd.concat([g2a, pd.DataFrame([nr])], ignore_index=True)
                set_gstr2a(upd); st.success(f"Entry from {sv} added to GSTR-2A."); st.rerun()
    g2a_fresh = get_gstr2a()
    with tb1:
        if g2a_fresh.empty: st.info("No GSTR-2A entries.")
        else:
            itc = (g2a_fresh["CGST"].astype(float).sum()+g2a_fresh["SGST"].astype(float).sum()+g2a_fresh["IGST"].astype(float).sum())
            k1,k2,k3 = st.columns(3)
            k1.metric("Suppliers Filed", g2a_fresh["GSTIN"].nunique())
            k2.metric("Total Invoices",  len(g2a_fresh))
            k3.metric("ITC Available",   fmt_inr(itc))
            d = g2a_fresh.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: d[c] = d[c].apply(fmt_inr)
            st.dataframe(d, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download GSTR-2A CSV", data=g2a_fresh.to_csv(index=False).encode(),
                file_name=f"GSTR2A_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
    with tb2:
        if g2a_fresh.empty: st.info("Add 2A entries first.")
        else:
            it = (g2a_fresh["CGST"].astype(float).sum()+g2a_fresh["SGST"].astype(float).sum()+g2a_fresh["IGST"].astype(float).sum())
            st.info(f"🔒 GSTR-2B locked snapshot — Total claimable ITC: **{fmt_inr(it)}**")
            d = g2a_fresh.copy(); d["Source"] = "GSTR-2B (Locked)"
            for c in ["Taxable","CGST","SGST","IGST","Total"]: d[c] = d[c].apply(fmt_inr)
            st.dataframe(d, use_container_width=True, hide_index=True)
    with tb3:
        if pdf.empty: st.info("No purchase entries to reconcile.")
        elif g2a_fresh.empty: st.info("Add 2A entries and purchase invoices to reconcile.")
        else:
            rows = []
            for _, row in pdf.iterrows():
                gstin = str(row.get("GSTIN","")).strip()
                matched = g2a_fresh[g2a_fresh["GSTIN"] == gstin] if gstin else pd.DataFrame()
                if matched.empty: status = "⚠️ Not in GSTR-2A"
                else:
                    a_c = matched["CGST"].astype(float).sum()
                    status = "✅ Matched" if abs(float(row["CGST"]) - a_c) < 1. else "❌ Amount Mismatch"
                rows.append({"ID":row["ID"],"Vendor":str(row.get("Vendor","")),"GSTIN":gstin,
                             "Your CGST":fmt_inr(row["CGST"]),"Status":status,
                             "ITC Claimable":"Yes" if status == "✅ Matched" else "No"})
            recon_df = pd.DataFrame(rows)
            st.dataframe(recon_df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Reconciliation CSV",
                data=recon_df.to_csv(index=False).encode(),
                file_name=f"GSTR2A_Recon_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv",
                use_container_width=True)
