import streamlit as st
import pandas as pd
import re
from datetime import datetime, date
from backend import parse, add_entry
from backend import run_ocr

st.set_page_config(page_title="FinFlow", page_icon="💳")
COLS = ["ID","Date","Vendor","GSTIN","Category","Subtotal","CGST","SGST","IGST","Total"]
CATS = ["Raw Materials","Office Supplies","IT & Software","Travel","Utilities","Rent","Marketing","Miscellaneous"]

def init():
    defaults = {"preg": pd.DataFrame(columns=COLS), "sreg": pd.DataFrame(columns=COLS), "n": 1, "ext": None}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
            #loop acts like tempoarary storage to ensure our page doesnt resets
init()

def summary():
    p, s = st.session_state.preg, st.session_state.sreg
    def sums(df):
        if df.empty: return 0., 0., 0., 0.
        return df.CGST.astype(float).sum(), df.SGST.astype(float).sum(), df.IGST.astype(float).sum(), df.Total.astype(float).sum()
    pc, ps, pi, pt = sums(p)
    sc, ss, si, st2 = sums(s)
    return dict(pt=pt, st=st2, pc=pc, ps=ps, pi=pi, sc=sc, ss=ss, si=si,
                nc=round(sc-pc,2), ns=round(ss-ps,2), ni=round(si-pi,2),
                net=round((sc+ss+si)-(pc+ps+pi),2), pn=len(p), sn=len(s))


# ── Sidebar ──
with st.sidebar:
    st.title("💳 FinFlow")
    st.caption("GST Purchase & Sales Register")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "Guide",
            "Upload & Extract",
            "Dashboard",
            "Manual Entry",
            "Purchase Register",
            "Sales Register",
            "Reconciliation"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    t = summary()
    st.metric("Purchases", t["pn"])
    st.metric("Sales", t["sn"])
    st.metric("Net Tax", f"₹{t['net']:,.0f}")

if page == "Guide":

    st.title("📘 FinFlow User Guide")

    st.header("1️⃣ Upload & Extract")
    st.write("""
    Upload invoice or receipt images.  
    FinFlow will automatically extract:
    - Vendor Name
    - GSTIN
    - Tax Amounts
    - Total Value
    """)

    st.header("2️⃣ Manual Entry")
    st.write("""
    If OCR fails or you want to add records manually,
    use the manual entry form to input invoice details.
    """)

    st.header("3️⃣ Dashboard")
    st.write("""
    View overall financial summary including:
    - Total Purchases
    - Total Sales
    - Net GST payable
    """)

    st.header("4️⃣ Purchase Register")
    st.write("""
    Displays all purchase transactions with GST details.
    Useful for GST input credit tracking.
    """)

    st.header("5️⃣ Sales Register")
    st.write("""
    Displays all sales invoices and GST collected.
    """)

    st.header("6️⃣ Reconciliation")
    st.write("""
    Helps match purchase and sales GST data
    to identify mismatches or missing entries.
    """)

    st.success("Tip: Upload invoices regularly to keep your GST records updated.")

# ── Dashboard ──
if page == "Dashboard":
    st.title("Dashboard")
    t = summary()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Purchases", f"₹{t['pt']:,.0f}", f"{t['pn']} invoices")
    c2.metric("Total Sales", f"₹{t['st']:,.0f}", f"{t['sn']} invoices")
    c3.metric("Gross Margin", f"₹{t['st']-t['pt']:,.0f}")
    c4.metric("Net Tax Due", f"₹{abs(t['net']):,.0f}")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tax Distribution")
        tax_data = pd.DataFrame({
            "Tax Type": ["CGST","SGST","IGST"],
            "Purchases": [t["pc"], t["ps"], t["pi"]],
            "Sales": [t["sc"], t["ss"], t["si"]]
        })
        tax_data.set_index("Tax Type", inplace=True)
        st.bar_chart(tax_data, use_container_width=True)
   
    with col2:
        st.subheader("Sales vs Purchases")
        st.bar_chart(pd.DataFrame({"Amount": [t["pt"], t["st"]]}, index=["Purchases", "Sales"]))
    p, s = st.session_state.preg, st.session_state.sreg
    if not p.empty or not s.empty:
        st.subheader("Recent Transactions")
        df = pd.concat([p.assign(Type="Purchase") if not p.empty else pd.DataFrame(),
                        s.assign(Type="Sales") if not s.empty else pd.DataFrame()]).tail(5)
        df = df[["ID","Date","Vendor","Type","Total"]].copy()
        df["Total"] = df["Total"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(df, hide_index=True, use_container_width=True)

# ── Upload & Extract ──
elif page == "Upload & Extract":
    st.title("Upload & Extract")
    col1, col2 = st.columns(2)
    with col1:
        f = st.file_uploader("Upload invoice", type=["pdf","png","jpg","jpeg"])
        if f:
            if f.name.lower().rsplit(".",1)[-1] in ("png","jpg","jpeg"):
                st.image(f, width=300); f.seek(0)
            if st.button("Extract Data"):
                with st.spinner("Reading..."):
                    try:
                        f.seek(0)
                        e = run_ocr(f)
                        st.session_state.ext = e
                        st.success("Done!")
                    except Exception as ex:
                        st.error(str(ex))
        if st.session_state.ext:
            e = st.session_state.ext
            st.subheader("Extracted Data")
            st.dataframe(pd.DataFrame({
                "Field": ["Vendor","Type","Date","GSTIN","Subtotal","CGST","SGST","IGST","Total"],
                "Value": [e.get("vendor",""), e.get("doc_type",""), e.get("date",""), e.get("gstin",""),
                          f"₹{e.get('subtotal',0):,.2f}", f"₹{e.get('cgst',0):,.2f}",
                          f"₹{e.get('sgst',0):,.2f}", f"₹{e.get('igst',0):,.2f}", f"₹{e.get('total',0):,.2f}"]
            }), hide_index=True, use_container_width=True)
    with col2:
        if st.session_state.ext:
            e = st.session_state.ext
            st.subheader("Confirm & Save")
            with st.form("confirm"):
                vendor  = st.text_input("Vendor", value=e.get("vendor",""))
                dt      = st.selectbox("Type", ["Purchase Invoice","Sales Invoice","Expense Receipt","Credit Note","Debit Note"],
                                       index=1 if "Sales" in e.get("doc_type","") else 0)
                txd     = st.text_input("Date", value=e.get("date",""))
                gstin   = st.text_input("GSTIN", value=e.get("gstin",""))
                cat     = st.selectbox("Category", CATS)
                sub     = st.number_input("Subtotal ₹", value=float(e.get("subtotal",0)), min_value=0.0)
                cg      = st.number_input("CGST ₹",    value=float(e.get("cgst",0)),    min_value=0.0)
                sg      = st.number_input("SGST ₹",    value=float(e.get("sgst",0)),    min_value=0.0)
                ig      = st.number_input("IGST ₹",    value=float(e.get("igst",0)),    min_value=0.0)
                st.write(f"**Total: ₹{sub+cg+sg+ig:,.2f}**")
                if st.form_submit_button("Save to Register"):
                    tid, key = add_entry({"vendor":vendor,"date":txd,"gstin":gstin,"category":cat,
                                          "subtotal":sub,"cgst":cg,"sgst":sg,"igst":ig,"total":sub+cg+sg+ig}, dt)
                    st.session_state.ext = None
                    st.success(f"Saved as {tid}!")

# ── Manual Entry ──
elif page == "Manual Entry":
    st.title("Manual Entry")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("manual"):
            dt      = st.selectbox("Invoice Type", ["Purchase Invoice","Sales Invoice","Expense Receipt","Credit Note","Debit Note"])
            vendor  = st.text_input("Vendor / Party")
            txd     = st.date_input("Date", value=date.today())
            gstin   = st.text_input("GSTIN (optional)")
            cat     = st.selectbox("Category", CATS)
            sub     = st.number_input("Subtotal ₹", min_value=0.0, value=0.0)
            c1, c2  = st.columns(3)[0], st.columns(3)[1]
            cgst_p  = st.number_input("CGST %", min_value=0.0, max_value=28.0, value=0)
            sgst_p  = st.number_input("SGST %", min_value=0.0, max_value=28.0, value=0.0)
            igst_p  = st.number_input("IGST %", min_value=0.0, max_value=28.0, value=0.0)
            cg = round(sub*cgst_p/100, 2)
            sg = round(sub*sgst_p/100, 2)
            ig = round(sub*igst_p/100, 2)
            tot = sub + cg + sg + ig
            st.write(f"CGST ₹{cg:,.2f} | SGST ₹{sg:,.2f} | IGST ₹{ig:,.2f} | **Total ₹{tot:,.2f}**")
            if st.form_submit_button("Add Entry"):
                if not vendor:
                    st.error("Vendor is required.")
                else:
                    tid, key = add_entry({"vendor":vendor,"date":txd.strftime("%d-%m-%Y"),"gstin":gstin,
                                          "category":cat,"subtotal":sub,"cgst":cg,"sgst":sg,"igst":ig,"total":tot}, dt)
                    st.success(f"Added: {tid}")
    with col2:
        st.subheader("Recent Entries")
        p, s = st.session_state.preg, st.session_state.sreg
        if not p.empty or not s.empty:
            df = pd.concat([p.assign(Type="Purchase") if not p.empty else pd.DataFrame(),
                            s.assign(Type="Sales") if not s.empty else pd.DataFrame()]).tail(8)[["ID","Vendor","Type","Total"]].copy()
            df["Total"] = df["Total"].apply(lambda x: f"₹{float(x):,.2f}")
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("No entries yet.")

# ── Purchase Register ──
elif page == "Purchase Register":
    st.title("Purchase Register")
    st.caption("Invoices where you are the buyer — Input Tax Credit (ITC) eligible")
    df = st.session_state.preg.copy()
    if df.empty:
        st.info("No purchase entries yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", f"₹{df.Total.astype(float).sum():,.2f}")
        c2.metric("CGST (ITC)", f"₹{df.CGST.astype(float).sum():,.2f}")
        c3.metric("SGST (ITC)", f"₹{df.SGST.astype(float).sum():,.2f}")
        c4.metric("Count", len(df))
        search = st.text_input("Search vendor")
        if search:
            df = df[df.Vendor.str.contains(search, case=False, na=False)]
        d = df.copy()
        for col in ["Subtotal","CGST","SGST","IGST","Total"]:
            d[col] = d[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(d, hide_index=True, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode(),
                           f"purchases_{date.today()}.csv", "text/csv")

# ── Sales Register ──
elif page == "Sales Register":
    st.title("Sales Register")
    st.caption("Invoices where you are the seller — Output Tax collected")
    df = st.session_state.sreg.copy()
    if df.empty:
        st.info("No sales entries yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", f"₹{df.Total.astype(float).sum():,.2f}")
        c2.metric("CGST", f"₹{df.CGST.astype(float).sum():,.2f}")
        c3.metric("SGST", f"₹{df.SGST.astype(float).sum():,.2f}")
        c4.metric("Count", len(df))
        search = st.text_input("Search buyer")
        if search:
            df = df[df.Vendor.str.contains(search, case=False, na=False)]
        d = df.copy()
        for col in ["Subtotal","CGST","SGST","IGST","Total"]:
            d[col] = d[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(d, hide_index=True, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode(),
                           f"sales_{date.today()}.csv", "text/csv")

# ── Reconciliation ──
elif page == "Reconciliation":
    st.title("GST Reconciliation")
    t = summary()
    p, s = st.session_state.preg, st.session_state.sreg
    if p.empty and s.empty:
        st.info("Add entries to run reconciliation.")
    else:
        st.subheader("Tax Statement")
        st.dataframe(pd.DataFrame({
            "Tax Head": ["CGST","SGST","IGST","TOTAL"],
            "Input Tax (Purchase)": [f"₹{t['pc']:,.2f}",f"₹{t['ps']:,.2f}",f"₹{t['pi']:,.2f}",f"₹{t['pc']+t['ps']+t['pi']:,.2f}"],
            "Output Tax (Sales)":   [f"₹{t['sc']:,.2f}",f"₹{t['ss']:,.2f}",f"₹{t['si']:,.2f}",f"₹{t['sc']+t['ss']+t['si']:,.2f}"],
            "Net Payable":          [f"₹{t['nc']:,.2f}",f"₹{t['ns']:,.2f}",f"₹{t['ni']:,.2f}",f"₹{t['net']:,.2f}"],
        }), hide_index=True, use_container_width=True)
        if t["net"] > 0:
            st.warning(f"GST Payable to Government: ₹{t['net']:,.2f}")
        else:
            st.success(f"Input Tax Credit exceeds Output Tax by ₹{abs(t['net']):,.2f}")
        st.subheader("GSTIN Validation")
        all_df = pd.concat([p.assign(Register="Purchase") if not p.empty else pd.DataFrame(),
                            s.assign(Register="Sales") if not s.empty else pd.DataFrame()])
        g = all_df[["ID","Vendor","GSTIN","Register"]].copy()
        g["Valid"] = g.GSTIN.apply(lambda x: "✅ Valid" if re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]$', str(x)) else "⚠️ Check")
        st.dataframe(g, hide_index=True, use_container_width=True)
        
