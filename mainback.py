import streamlit as st
import pandas as pd
import re
from datetime import datetime, date
def parse(text):
    #acts as smart invoice and converts raw ocr into strructed invoice
    ls = [l.strip() for l in text.splitlines() if l.strip()]
    full = " ".join(ls)
    def amt(pats):
        for p in pats:
            m = re.search(p, full, re.I)
            if m:
                try: return float(m.group(1).replace(",", ""))
                except: pass
        return 0.0
    doc_type = "Sales Invoice" if re.search(r'sales\s*invoice', full, re.I) else "Purchase Invoice"
    skip = [r'\d{2}[A-Za-z]{5}\d{4}', r'phone|email|gstin|billing', r'@', r'^\d+$', r'invoice|bill to']
    def co(ll):
        for l in ll:
            lc = re.sub(r'[|/*]', '', l).strip()
            if len(lc) < 4: continue
            if not any(re.search(p, lc, re.I) for p in skip) and any(c.isalpha() for c in lc):
                return lc
        return ""
    bi = next((i for i, l in enumerate(ls) if re.search(r'bill\s*to', l, re.I)), len(ls))
    vendor = co(ls[bi+1:bi+6]) if "Sales" in doc_type else co(ls[:bi])
    dm = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', full)
    ds = dm.group(1).replace("/", "-") if dm else date.today().strftime("%d-%m-%Y")
    gm = re.findall(r'\b\d{2}[A-Za-z]{5}\d{4}[A-Za-z][A-Za-z0-9][Zz][A-Za-z0-9]\b', full)
    gstin = gm[0].upper() if gm else ""
    tot = amt([r'(?:grand\s*total|total\s*amount)[:\sRs.]*([0-9,]+\.?\d*)'])
    if not tot:
        tot = max([float(x) for x in re.findall(r'\b\d{1,7}\.\d{2}\b', full)], default=0.0)
    sub = amt([r'(?:taxable\s*value|subtotal)[:\sRs.]*([0-9,]+\.?\d*)'])
    cg = amt([r'CGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)'])
    sg = amt([r'SGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)'])
    ig = amt([r'IGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR)?\s*([0-9,]{3,}\.?\d*)'])
    if not sub and tot:
        sub = round(tot - (cg+sg+ig), 2) if cg+sg+ig else round(tot/1.18, 2)
    if not cg and not sg and sub:
        tax = round(tot - sub, 2); cg = sg = round(tax/2, 2)
    return {"vendor": vendor, "date": ds, "gstin": gstin, "doc_type": doc_type,
            "subtotal": sub, "cgst": cg, "sgst": sg, "igst": ig, "total": tot, "category": "Miscellaneous"}


def add_entry(data, doc_type):
    is_sales = "Sales" in doc_type
    tid = f"{'SAL' if is_sales else 'PUR'}-{datetime.now().strftime('%y%m%d')}-{st.session_state.n:04d}"
    row = {"ID": tid, "Date": data["date"], "Vendor": data["vendor"], "GSTIN": data["gstin"],
           "Category": data["category"], "Subtotal": data["subtotal"], "CGST": data["cgst"],
           "SGST": data["sgst"], "IGST": data["igst"], "Total": data["total"]}
    key = "sreg" if is_sales else "preg"
    st.session_state[key] = pd.concat([st.session_state[key], pd.DataFrame([row])], ignore_index=True)
    st.session_state.n += 1
    return tid, key

def run_ocr(f):
    import pytesseract, shutil, os
    from PIL import Image
    from io import BytesIO
    if shutil.which("tesseract") is None:
        for p in [r"C:\Program Files\Tesseract-OCR\tesseract.exe"]:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
    b = f.read()
    ext = f.name.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        import fitz
        pg = fitz.open(stream=b, filetype="pdf")[0]
        img = Image.open(BytesIO(pg.get_pixmap(matrix=fitz.Matrix(3,3)).tobytes("png")))
    else:
        img = Image.open(BytesIO(b))
    return parse(pytesseract.image_to_string(img, lang="eng"))


