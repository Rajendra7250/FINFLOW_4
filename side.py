# ── OCR (Tesseract) ──
import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
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

    dm = re.search(r'(?:invoice\s*date|date)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', full, re.IGNORECASE)
    if not dm: dm = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', full)
    date_str = dm.group(1).replace("/","-") if dm else date.today().strftime("%d-%m-%Y")

    gstin_match = re.findall(r'\b\d{2}[A-Za-z]{5}\d{4}[A-Za-z][A-Za-z0-9][Zz][A-Za-z0-9]\b', full)
    gstin = gstin_match[0].upper() if gstin_match else ""

    total = find_amount([
        r'(?:total\s*amount\s*payable|grand\s*total|total\s*amount)[:\sRs.]*([0-9,]+\.?\d*)',
        r'total\s*payable[:\sRs.]*([0-9,]+\.?\d*)',
    ])
    if total == 0.0:
        all_nums = [float(x) for x in re.findall(r'\b\d{1,7}\.\d{2}\b', full)]
        total = max(all_nums) if all_nums else 0.0

    subtotal = find_amount([r'(?:taxable\s*value|subtotal)[:\sRs.]*([0-9,]+\.?\d*)'])
    cgst = find_amount([r'CGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)', r'CGST\s*@?\s*[\d.]*\s*%?\s*[:\sRs.]*([0-9,]{2,}\.?\d*)'])
    sgst = find_amount([r'SGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)', r'SGST\s*@?\s*[\d.]*\s*%?\s*[:\sRs.]*([0-9,]{2,}\.?\d*)'])
    igst = find_amount([r'IGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)', r'IGST\s*@?\s*[\d.]*\s*%?\s*[:\sRs.]*([0-9,]{2,}\.?\d*)'])

    if subtotal == 0.0 and total > 0:
        tax = cgst + sgst + igst
        subtotal = round(total - tax, 2) if tax > 0 else round(total / 1.18, 2)
    if cgst == 0.0 and sgst == 0.0 and igst == 0.0 and total > 0 and subtotal > 0:
        tax = round(total - subtotal, 2)
        cgst = sgst = round(tax / 2, 2)

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

def fmt_inr(val):
    try: return f"₹{float(val):,.2f}"
    except: return "₹0.00"
def build_gstr1(sales_df):
    if sales_df.empty:
        return {}, pd.DataFrame(), pd.DataFrame()
    df = sales_df.copy()
    for c in ["CGST","SGST","IGST","Subtotal","Total"]:
        df[c] = df[c].astype(float)
    b2b = df[df["GSTIN"].str.strip().str.len() > 5].copy() if "GSTIN" in df.columns else pd.DataFrame()
    b2c = df[~df.index.isin(b2b.index)].copy()
    summary = {
        "b2b_count":     len(b2b),
        "b2c_count":     len(b2c),
        "total_taxable": df["Subtotal"].sum(),
        "total_cgst":    df["CGST"].sum(),
        "total_sgst":    df["SGST"].sum(),
        "total_igst":    df["IGST"].sum(),
        "total_tax":     df["CGST"].sum() + df["SGST"].sum() + df["IGST"].sum(),
        "grand_total":   df["Total"].sum(),
    }
    return summary, b2b, b2c


def build_gstr3b(sales_df, purchase_df):
    def sums(df):
        if df.empty: return 0.0, 0.0, 0.0, 0.0
        return (df["Subtotal"].astype(float).sum(),
                df["CGST"].astype(float).sum(),
                df["SGST"].astype(float).sum(),
                df["IGST"].astype(float).sum())
    s_sub, s_cgst, s_sgst, s_igst = sums(sales_df)
    p_sub, p_cgst, p_sgst, p_igst = sums(purchase_df)
    net_cgst  = round(s_cgst - p_cgst, 2)
    net_sgst  = round(s_sgst - p_sgst, 2)
    net_igst  = round(s_igst - p_igst, 2)
    net_total = round(net_cgst + net_sgst + net_igst, 2)
    return {
        "out_taxable": s_sub,  "out_cgst": s_cgst,  "out_sgst": s_sgst,  "out_igst": s_igst,
        "itc_taxable": p_sub,  "itc_cgst": p_cgst,  "itc_sgst": p_sgst,  "itc_igst": p_igst,
        "net_cgst": net_cgst,  "net_sgst": net_sgst, "net_igst": net_igst,"net_total": net_total,
    }


def build_gstr2a_2b(purchase_df, gstr2a_df):
    if purchase_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    pr = purchase_df.copy()
    for c in ["CGST","SGST","IGST","Total","Subtotal"]:
        pr[c] = pr[c].astype(float)
    gstr2b = gstr2a_df.copy()
    if not gstr2b.empty:
        gstr2b["Source"] = "GSTR-2B (Locked)"
    recon_rows = []
    for _, row in pr.iterrows():
        gstin  = str(row.get("GSTIN","")).strip()
        vendor = str(row.get("Vendor",""))
        matched = gstr2a_df[gstr2a_df["GSTIN"] == gstin] if not gstr2a_df.empty and gstin else pd.DataFrame()
        if matched.empty:
            status = "⚠️ Not in GSTR-2A"
        else:
            a_cgst = matched["CGST"].astype(float).sum()
            a_igst = matched["IGST"].astype(float).sum()
            if abs(float(row["CGST"]) - a_cgst) < 1.0 or abs(float(row["IGST"]) - a_igst) < 1.0:
                status = "✅ Matched"
            else:
                status = "❌ Amount Mismatch"
        recon_rows.append({
            "ID": row["ID"], "Vendor": vendor, "GSTIN": gstin,
            "Your CGST": row["CGST"], "Your IGST": row["IGST"],
            "2A CGST": matched["CGST"].astype(float).sum() if not matched.empty else 0.0,
            "2A IGST": matched["IGST"].astype(float).sum() if not matched.empty else 0.0,
            "Status": status,
            "ITC Claimable": "Yes" if status == "✅ Matched" else "No",
        })
    return gstr2a_df, gstr2b, pd.DataFrame(recon_rows)
