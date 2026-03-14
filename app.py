import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
from io import BytesIO

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
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
}
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
.stSelectbox > div > div { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text) !important; }
label, .stSelectbox label, .stTextInput label { color: var(--muted) !important; font-size: 0.78rem !important; font-family: 'DM Mono', monospace !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 10px !important; padding: 4px !important; gap: 4px !important; border: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important; border-radius: 7px !important; border: none !important; }
.stTabs [aria-selected="true"] { background: var(--surface2) !important; color: var(--accent) !important; border: 1px solid var(--border) !important; }
[data-testid="stMetric"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; color: var(--text) !important; }
hr { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }
.pwd-rule { font-size: 0.75rem; font-family: 'DM Mono', monospace; padding: 2px 0; }
.pwd-ok { color: #00E5A0; } .pwd-fail { color: #FF6B6B; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FULL TRANSLATION DICTIONARY
# ─────────────────────────────────────────────
T = {
    "English": {
        # Login
        "app_subtitle": "GST REGISTER · SIGN IN",
        "sign_in": "Sign In",
        "create_account": "Create Account",
        "username": "Username",
        "password": "Password",
        "enter_username": "Enter username",
        "enter_password": "Enter password",
        "sign_in_btn": "Sign In →",
        "demo_creds": "DEMO CREDENTIALS",
        "demo_line": "admin / Admin@123 · Admin",
        "invalid_creds": "Invalid username or password.",
        "welcome_back": "Welcome back",
        "choose_username": "Choose Username",
        "full_name": "Full Name",
        "eg_username": "e.g. john_trader",
        "eg_name": "e.g. John Doe",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "create_account_btn": "Create Account →",
        "username_required": "Username and full name are required.",
        "username_exists": "Username already exists.",
        "pwd_req_fail": "Password does not meet requirements (see rules below).",
        "pwd_no_match": "Passwords do not match.",
        "account_created": "Account created! Sign in as",
        "pwd_rules_title": "PASSWORD RULES",
        "pwd_rule_1": "✓ 6–12 characters total",
        "pwd_rule_2": "✓ At least 1 UPPERCASE letter (A–Z)",
        "pwd_rule_3": "✓ At least 1 special character (!@#$%^&*...)",
        "pwd_r1": "At least 6 characters",
        "pwd_r2": "At most 12 characters",
        "pwd_r3": "At least 1 uppercase letter",
        "pwd_r4": "At least 1 special character",
        # Sidebar
        "logout": "🚪 Logout",
        "app_tagline": "GST Sales & Purchase Register",
        "language": "🌐 Language",
        "quick_stats": "Quick Stats",
        "purchases_lbl": "📥 Purchases",
        "sales_lbl": "📤 Sales",
        "net_tax_due": "Net Tax Due",
        # Nav
        "nav_dashboard": "Dashboard",
        "nav_upload": "Upload & Extract",
        "nav_manual": "Manual Entry",
        "nav_purchase": "Purchase Register",
        "nav_sales": "Sales Register",
        "nav_recon": "Reconciliation",
        "nav_gstr1": "GSTR-1 Report",
        "nav_gstr3b": "GSTR-3B Report",
        "nav_gstr2": "GSTR-2A / 2B",
        "nav_guide": "User Guide",
        "nav_settings": "Settings",
        # Dashboard
        "dashboard_title": "## 📊 Dashboard",
        "dashboard_caption": "GST Sales & Purchase Register overview",
        "total_purchases": "📥 Total Purchases",
        "total_sales": "📤 Total Sales",
        "gross_margin": "💹 Gross Margin",
        "sales_minus_purchases": "Sales minus Purchases",
        "tax_payable": "Tax Payable",
        "tax_refund": "Tax Refund",
        "output_minus_input": "Output tax − Input tax",
        "gst_breakdown": "**🧾 GST Tax Breakdown**",
        "tax_col": "Tax",
        "purchase_input": "Purchase (Input)",
        "sales_output": "Sales (Output)",
        "net_due": "Net Due",
        "payable_warning": "payable to government",
        "carry_forward": "Input credit exceeds output — carry forward",
        "sales_vs_purchases": "**📊 Sales vs Purchases**",
        "chart_info": "**Output Tax** (on Sales) − **Input Tax Credit** (on Purchases) = **Net GST Payable**",
        "recent_activity": "**🕒 Recent Activity**",
        "type_col": "Type",
        "purchase_type": "Purchase",
        "sales_type": "Sales",
        "gstr_status": "**📋 GSTR Filing Status**",
        "no_data": "⚪ No Data",
        "ready_to_file": "🟢 Ready to File",
        # Upload
        "upload_title": "## 📤 Upload & Extract",
        "upload_caption": "Upload your invoice — OCR reads and auto-detects whether it is a Purchase or Sales invoice.",
        "drop_invoice": "Drop invoice here",
        "extract_btn": "🔍 Extract Data",
        "reading_invoice": "Reading invoice...",
        "extraction_complete": "✓ Extraction complete!",
        "extraction_failed": "Extraction failed:",
        "extracted_fields": "**🔎 Extracted Fields**",
        "detection": "Detection:",
        "ocr_confidence": "OCR Confidence",
        "illegal_tax": "🚨 ILLEGAL TAX ALERT — No GSTIN but GST charged. Cannot claim ITC. Demand corrected invoice.",
        "no_gstin_warn": "⚠️ No GSTIN — Unregistered or Composition Scheme. No ITC can be claimed.",
        "vendor_party": "Vendor / Party",
        "invoice_type": "Invoice Type",
        "date_col": "Date",
        "gstin_col": "GSTIN",
        "no_gstin": "⚠️ No GSTIN",
        "category_col": "Category",
        "subtotal_col": "Subtotal",
        "cgst_col": "CGST",
        "sgst_col": "SGST",
        "igst_col": "IGST",
        "total_amount": "Total Amount",
        "field_col": "Field",
        "value_col": "Value",
        "review_confirm": "**✏️ Review & Confirm**",
        "vendor_name": "Vendor / Party Name",
        "txn_date": "Date",
        "calculated_total": "Calculated Total",
        "confirm_btn": "✅ Confirm & Add to Register",
        "added_to": "added to",
        "upload_first": "Upload a document and click Extract to see data here.",
        "purchase_invoice": "Purchase Invoice",
        "sales_invoice": "Sales Invoice",
        "credit_note": "Credit Note",
        "debit_note": "Debit Note",
        "expense_receipt": "Expense Receipt",
        "to_sales_reg": "Sales Register",
        "to_purchase_reg": "Purchase Register",
        # Manual
        "manual_title": "## ✏️ Manual Entry",
        "add_entry_btn": "➕ Add Entry",
        "vendor_required": "Vendor name is required.",
        "recent_entries": "**📌 Recent Entries**",
        "no_entries": "No entries yet.",
        "cgst_pct": "CGST %",
        "sgst_pct": "SGST %",
        "igst_pct": "IGST %",
        "subtotal_inr": "Subtotal (₹)",
        # Purchase Register
        "purchase_reg_title": "## 📋 Purchase Register",
        "purchase_reg_caption": "All invoices where you are the buyer — Input Tax Credit (ITC) eligible.",
        "no_purchase": "No purchase entries yet. Upload purchase invoices or add manually.",
        "total_purchases_m": "Total Purchases",
        "input_cgst": "Input CGST (ITC)",
        "input_sgst": "Input SGST (ITC)",
        "total_entries": "Total Entries",
        "search_vendor": "🔍 Search vendor",
        "export_csv": "⬇️ Export CSV",
        # Sales Register
        "sales_reg_title": "## 💰 Sales Register",
        "sales_reg_caption": "All invoices where you are the seller — Output Tax collected from customers.",
        "no_sales": "No sales entries yet. Upload sales invoices or add manually.",
        "total_sales_m": "Total Sales",
        "output_cgst": "Output CGST",
        "output_sgst": "Output SGST",
        "search_buyer": "🔍 Search buyer",
        # Reconciliation
        "recon_title": "## 🔄 GST Reconciliation",
        "no_recon_data": "Add purchase and sales entries to run reconciliation.",
        "full_tax_stmt": "**📊 Full Tax Statement**",
        "tax_head": "Tax Head",
        "input_tax_purchase": "Input Tax (Purchase)",
        "output_tax_sales": "Output Tax (Sales)",
        "net_payable": "Net Payable",
        "net_gst_payable": "Net GST Payable to Government",
        "pay_by_20th": "Pay by 20th of next month.",
        "itc_exceeds": "Input Tax Credit exceeds Output Tax by",
        "carry_fwd": "Carry forward.",
        "gstin_validation": "**✅ GSTIN Validation**",
        "no_gstin_col": "❌ No GSTIN",
        "valid_gstin": "✅ Valid",
        "invalid_gstin": "⚠️ Invalid Format",
        "register_col": "Register",
        "valid_col": "Valid",
        # GSTR-1
        "gstr1_title": "## 📄 GSTR-1 — Outward Supplies",
        "gstr1_caption": "Statement of outward supplies — file by 11th of following month.",
        "gstr1_info": "ℹ️ B2B invoices auto-appear in buyer's GSTR-2A.",
        "no_sales_gstr1": "No sales data. Add sales invoices to generate GSTR-1.",
        "taxable_turnover": "Taxable Turnover",
        "grand_total": "Grand Total",
        "b2b_tab": "📦 B2B Invoices",
        "b2c_tab": "🛒 B2C Invoices",
        "hsn_tab": "📊 HSN Summary",
        "full_table_tab": "📋 Full Table",
        "b2b_caption": "B2B invoices (with GSTIN) — auto-appear in buyer's GSTR-2A.",
        "b2c_caption": "B2C invoices (no GSTIN) — buyer cannot claim ITC.",
        "no_b2b": "No B2B invoices.",
        "no_b2c": "No B2C invoices.",
        "hsn_caption": "Category-wise summary (proxy for HSN/SAC grouping).",
        "invoices_col": "Invoices",
        "taxable_col": "Taxable",
        "download_gstr1": "⬇️ Download GSTR-1 CSV",
        # GSTR-3B
        "gstr3b_title": "## 📑 GSTR-3B — Monthly Summary Return",
        "gstr3b_caption": "Self-declaration of net tax payable — file by 20th of following month.",
        "gstr3b_warn": "⚠️ Output tax − ITC = Net tax payable. 18% p.a. interest on late payment.",
        "no_data_gstr3b": "Add sales and purchase entries to generate GSTR-3B.",
        "output_tax_tab": "📋 3.1 Output Tax",
        "itc_tab": "📥 4. ITC Available",
        "net_tax_tab": "💰 Net Tax Payable",
        "output_tax_heading": "**Table 3.1 — Details of Outward Supplies & Tax Liability**",
        "itc_heading": "**Table 4 — Eligible Input Tax Credit (ITC)**",
        "net_tax_heading": "**Table 6.1 — Net Tax Payable**",
        "section_col": "Section",
        "nature_col": "Nature",
        "outward_taxable": "Outward taxable supplies",
        "zero_rated": "Zero rated supplies",
        "nil_rated": "Nil rated / exempt",
        "itc_imports_goods": "ITC on imports of goods",
        "itc_imports_svc": "ITC on imports of services",
        "itc_domestic": "All other ITC (domestic)",
        "output_liability": "Output Tax Liability",
        "less_itc": "Less: ITC Available",
        "net_tax_payable": "NET TAX PAYABLE",
        "owe_gst": "You owe ₹{} in GST. Pay via GSTN portal by 20th.",
        "excess_itc": "Excess ITC of ₹{} — carry forward to next period.",
        "download_gstr3b": "⬇️ Download GSTR-3B CSV",
        # GSTR-2A/2B
        "gstr2_title": "## 🔍 GSTR-2A / 2B — Inward Supplies ITC",
        "gstr2_caption": "Auto-populated from your suppliers' GSTR-1 filings.",
        "gstr2a_dynamic": "**📡 GSTR-2A — Dynamic:** Auto-updates as suppliers file. Changes when they amend.",
        "gstr2b_static": "**🔒 GSTR-2B — Static:** Locked snapshot for a return period. Use this to claim ITC in 3B.",
        "gstr2a_tab": "📡 GSTR-2A Data",
        "gstr2b_tab": "🔒 GSTR-2B (Static)",
        "recon_tab": "🔍 Reconciliation",
        "add_2a_tab": "➕ Add 2A Entry",
        "add_2a_caption": "Simulate supplier-filed entries (in production this pulls from GSTN API).",
        "supplier_gstin": "Supplier GSTIN",
        "supplier_name": "Supplier Name",
        "invoice_no": "Invoice Number",
        "invoice_date": "Invoice Date",
        "taxable_value": "Taxable Value (₹)",
        "add_2a_btn": "➕ Add to GSTR-2A",
        "added_to_2a": "Entry from {} added to GSTR-2A.",
        "no_2a_data": "No GSTR-2A entries. Go to 'Add 2A Entry' tab to simulate supplier data.",
        "suppliers_filed": "Suppliers Filed",
        "total_invoices": "Total Invoices",
        "itc_available": "ITC Available",
        "download_2a": "⬇️ Download GSTR-2A CSV",
        "no_2b_data": "Add 2A entries first — GSTR-2B is generated from GSTR-2A data.",
        "gstr2b_locked": "🔒 GSTR-2B locked snapshot — Total claimable ITC:",
        "download_2b": "⬇️ Download GSTR-2B CSV",
        "recon_caption": "Match your Purchase Register vs GSTR-2A to identify claimable ITC.",
        "no_purchase_recon": "No purchase entries to reconcile.",
        "no_2a_recon": "Add 2A entries and purchase invoices to reconcile.",
        "matched": "✅ Matched",
        "mismatch": "❌ Amount Mismatch",
        "not_in_2a": "⚠️ Not in GSTR-2A",
        "itc_claimable_col": "ITC Claimable",
        "action_guide": """**Action Guide:**
- ✅ **Matched** — Claim ITC in GSTR-3B Table 4
- ❌ **Amount Mismatch** — Contact supplier to amend GSTR-1, or reverse ITC
- ⚠️ **Not in GSTR-2A** — Supplier hasn't filed. Follow up before claiming ITC""",
        "download_recon": "⬇️ Download Reconciliation CSV",
        # User Guide
        "guide_title": "## 📖 User Guide",
        "guide_caption": "Complete step-by-step guide to using FinFlow.",
        "how_works": "**📋 How FinFlow Works**",
        "how_works_flow": "**Invoice → OCR Reads → Auto Sort (Purchase / Sales) → Dashboard → File GST**",
        "step_by_step": "**🪜 Step-by-Step Instructions**",
        "steps": [
            ("1️⃣ Upload Invoice", "Go to 📤 Upload & Extract → Select PDF or image → Click 🔍 Extract Data."),
            ("2️⃣ Review & Confirm", "Check vendor name, amounts, CGST/SGST/IGST → Fix errors → Click ✅ Confirm & Add to Register."),
            ("3️⃣ Check Registers", "📋 Purchase Register = bills you paid  |  💰 Sales Register = bills you raised."),
            ("4️⃣ View Dashboard", "📊 Dashboard shows total purchases, sales, and net GST payable automatically."),
            ("5️⃣ GST Reports", "📄 GSTR-1 for sales  |  📑 GSTR-3B for net tax payable → Download CSV → File on GST portal."),
            ("6️⃣ Reconciliation", "🔄 Check all GSTINs are valid and identify unregistered dealers."),
        ],
        "itc_rules": "**💡 ITC Rules — When Can You Claim?**",
        "itc_yes": "**✅ ITC Can Be Claimed**\n\n✔ Supplier has valid GSTIN\n\n✔ They have filed their GSTR-1\n\n✔ Invoice shows GST amount\n\n✔ It appears in your GSTR-2A",
        "itc_no": "**❌ ITC Cannot Be Claimed**\n\n✘ Supplier has NO GSTIN\n\n✘ Supplier on Composition Scheme\n\n✘ Tax charged without GSTIN (ILLEGAL)\n\n✘ Supplier hasn't filed GSTR-1",
        "itc_warn": "⚠️ A supplier without a GSTIN cannot legally collect GST. You cannot claim ITC on such purchases — demand a corrected invoice.",
        "faq_title": "**❓ Frequently Asked Questions**",
        "faqs": [
            ("What is ITC?", "Input Tax Credit means the GST you paid on purchases can be deducted from GST collected on sales. You only pay the difference to the government."),
            ("My supplier has no GSTIN — can I claim ITC?", "No. Unregistered suppliers cannot legally charge GST. Demand a corrected invoice without GST."),
            ("What is Composition Scheme?", "Small businesses below ₹1.5 crore turnover can opt for a flat low rate but CANNOT collect GST from buyers."),
            ("What if OCR reads the wrong amount?", "Correct any field in the Review & Confirm section before adding the entry."),
            ("How often should I file GST?", "GSTR-1 by 11th | GSTR-3B by 20th of the following month. Late = ₹50/day + 18% annual interest."),
            ("Are my entries saved when I log out and log back in?", "Yes! FinFlow stores all your entries linked to your login ID within the same browser session."),
        ],
        # Settings
        "settings_title": "## ⚙️ Settings",
        "settings_caption": "Your business details — used to auto-detect Sales vs Purchase invoices.",
        "biz_tab": "🏢 Business Identity",
        "pwd_tab": "🔑 Change Password",
        "current_biz": "**Current Business Identity**",
        "biz_name": "Business Name",
        "city_lbl": "City",
        "state_lbl": "State",
        "my_gstin": "My GSTIN",
        "update_details": "**✏️ Update Details**",
        "save_settings": "💾 Save Settings",
        "biz_empty": "Business name cannot be empty.",
        "gstin_empty": "GSTIN cannot be empty.",
        "saved_ok": "✅ Saved! Using **{}** ({}) for invoice detection.",
        "valid_gstin": "✅ Valid GSTIN format",
        "gstin_warn": "⚠️ Format looks off — should be 15 chars like 29ABCDE1234F1Z5",
        "change_pwd": "**🔑 Change Your Password**",
        "current_pwd": "Current Password",
        "new_pwd_lbl": "New Password",
        "new_pwd_help": "6–12 chars, 1 uppercase, 1 special character",
        "confirm_new_pwd": "Confirm New Password",
        "update_pwd_btn": "🔒 Update Password",
        "wrong_current_pwd": "Current password is incorrect.",
        "pwd_updated": "✅ Password updated successfully!",
        "invoice_detection": "**ℹ️ How Invoice Detection Works**",
        "detect_table": """| Priority | Method | Logic |
|----------|--------|-------|
| 1️⃣ | **GSTIN Position** | Your GSTIN in seller block → Sales Invoice |
| 1️⃣ | **GSTIN Position** | Your GSTIN in BILL TO block → Purchase Invoice |
| 2️⃣ | **Name Match** | Your business name in seller / buyer section |
| 3️⃣ | **Keywords** | Text says "Sales Invoice" / "Purchase Invoice" |
| 4️⃣ | **Position** | Your GSTIN in top half → Sales, else Purchase |""",
        # Categories
        "categories": ["Raw Materials", "Office Supplies", "Travel & Transport", "Utilities", "Rent", "Professional Services", "IT & Software", "Marketing", "Miscellaneous"],
        "role_lbl": "Admin",
        "invoices_count": "invoices",
        "needscorrection": "Needs correction",
        "follow_up": "Follow up",
        "itc_claimable": "ITC claimable",
        "total_col": "Total",
        "status_col": "Status",
        "id_col": "ID",
    },

    "ಕನ್ನಡ": {
        # Login
        "app_subtitle": "ಜಿಎಸ್‌ಟಿ ನೋಂದಣಿ · ಪ್ರವೇಶ",
        "sign_in": "ಒಳಗೆ ಹೋಗಿ",
        "create_account": "ಖಾತೆ ತೆರೆಯಿರಿ",
        "username": "ಬಳಕೆದಾರ ಹೆಸರು",
        "password": "ಗುಪ್ತಪದ",
        "enter_username": "ಬಳಕೆದಾರ ಹೆಸರು ನಮೂದಿಸಿ",
        "enter_password": "ಗುಪ್ತಪದ ನಮೂದಿಸಿ",
        "sign_in_btn": "ಒಳಗೆ ಹೋಗಿ →",
        "demo_creds": "ಡೆಮೋ ರುಜುವಾತುಗಳು",
        "demo_line": "admin / Admin@123 · ನಿರ್ವಾಹಕ",
        "invalid_creds": "ತಪ್ಪಾದ ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಗುಪ್ತಪದ.",
        "welcome_back": "ಮತ್ತೆ ಸ್ವಾಗತ",
        "choose_username": "ಬಳಕೆದಾರ ಹೆಸರು ಆರಿಸಿ",
        "full_name": "ಪೂರ್ಣ ಹೆಸರು",
        "eg_username": "ಉದಾ: john_trader",
        "eg_name": "ಉದಾ: ರಾಜೇಶ್ ಕುಮಾರ್",
        "new_password": "ಹೊಸ ಗುಪ್ತಪದ",
        "confirm_password": "ಗುಪ್ತಪದ ದೃಢಪಡಿಸಿ",
        "create_account_btn": "ಖಾತೆ ತೆರೆಯಿರಿ →",
        "username_required": "ಬಳಕೆದಾರ ಹೆಸರು ಮತ್ತು ಪೂರ್ಣ ಹೆಸರು ಅಗತ್ಯ.",
        "username_exists": "ಈ ಬಳಕೆದಾರ ಹೆಸರು ಈಗಾಗಲೇ ಇದೆ.",
        "pwd_req_fail": "ಗುಪ್ತಪದ ನಿಯಮಗಳನ್ನು ಪೂರೈಸಿಲ್ಲ (ಕೆಳಗೆ ನೋಡಿ).",
        "pwd_no_match": "ಗುಪ್ತಪದಗಳು ಹೊಂದುತ್ತಿಲ್ಲ.",
        "account_created": "ಖಾತೆ ತೆರೆಯಲಾಗಿದೆ! ಇಂತಹ ಹೆಸರಿನಿಂದ ಒಳಗೆ ಹೋಗಿ:",
        "pwd_rules_title": "ಗುಪ್ತಪದ ನಿಯಮಗಳು",
        "pwd_rule_1": "✓ ಒಟ್ಟು 6–12 ಅಕ್ಷರಗಳು",
        "pwd_rule_2": "✓ ಕನಿಷ್ಠ 1 ದೊಡ್ಡ ಅಕ್ಷರ (A–Z)",
        "pwd_rule_3": "✓ ಕನಿಷ್ಠ 1 ವಿಶೇಷ ಚಿಹ್ನೆ (!@#$%^&*...)",
        "pwd_r1": "ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು",
        "pwd_r2": "ಗರಿಷ್ಠ 12 ಅಕ್ಷರಗಳು",
        "pwd_r3": "ಕನಿಷ್ಠ 1 ದೊಡ್ಡ ಅಕ್ಷರ",
        "pwd_r4": "ಕನಿಷ್ಠ 1 ವಿಶೇಷ ಚಿಹ್ನೆ",
        # Sidebar
        "logout": "🚪 ಹೊರಗೆ ಹೋಗಿ",
        "app_tagline": "ಜಿಎಸ್‌ಟಿ ಮಾರಾಟ & ಖರೀದಿ ನೋಂದಣಿ",
        "language": "🌐 ಭಾಷೆ",
        "quick_stats": "ತ್ವರಿತ ಅಂಕಿಅಂಶ",
        "purchases_lbl": "📥 ಖರೀದಿಗಳು",
        "sales_lbl": "📤 ಮಾರಾಟಗಳು",
        "net_tax_due": "ನಿವ್ವಳ ತೆರಿಗೆ ಬಾಕಿ",
        # Nav
        "nav_dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "nav_upload": "ಅಪ್‌ಲೋಡ್ & ಓದು",
        "nav_manual": "ಕೈಯಾರೆ ನಮೂದು",
        "nav_purchase": "ಖರೀದಿ ನೋಂದಣಿ",
        "nav_sales": "ಮಾರಾಟ ನೋಂದಣಿ",
        "nav_recon": "ತೆರಿಗೆ ಲೆಕ್ಕ",
        "nav_gstr1": "ಜಿಎಸ್‌ಟಿಆರ್-1 ವರದಿ",
        "nav_gstr3b": "ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ ವರದಿ",
        "nav_gstr2": "ಜಿಎಸ್‌ಟಿಆರ್-2ಎ / 2ಬಿ",
        "nav_guide": "ಬಳಕೆದಾರ ಮಾರ್ಗದರ್ಶಿ",
        "nav_settings": "ಸೆಟ್ಟಿಂಗ್ಸ್",
        # Dashboard
        "dashboard_title": "## 📊 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "dashboard_caption": "ಜಿಎಸ್‌ಟಿ ಮಾರಾಟ & ಖರೀದಿ ನೋಂದಣಿ ಅವಲೋಕನ",
        "total_purchases": "📥 ಒಟ್ಟು ಖರೀದಿ",
        "total_sales": "📤 ಒಟ್ಟು ಮಾರಾಟ",
        "gross_margin": "💹 ಒಟ್ಟು ಲಾಭ",
        "sales_minus_purchases": "ಮಾರಾಟ ಮೈನಸ್ ಖರೀದಿ",
        "tax_payable": "ತೆರಿಗೆ ಪಾವತಿಸಬೇಕು",
        "tax_refund": "ತೆರಿಗೆ ಮರುಪಾವತಿ",
        "output_minus_input": "ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ − ಇನ್‌ಪುಟ್ ತೆರಿಗೆ",
        "gst_breakdown": "**🧾 ಜಿಎಸ್‌ಟಿ ತೆರಿಗೆ ವಿವರ**",
        "tax_col": "ತೆರಿಗೆ",
        "purchase_input": "ಖರೀದಿ (ಇನ್‌ಪುಟ್)",
        "sales_output": "ಮಾರಾಟ (ಔಟ್‌ಪುಟ್)",
        "net_due": "ನಿವ್ವಳ ಬಾಕಿ",
        "payable_warning": "ಸರ್ಕಾರಕ್ಕೆ ಪಾವತಿಸಬೇಕು",
        "carry_forward": "ಇನ್‌ಪುಟ್ ಕ್ರೆಡಿಟ್ ಹೆಚ್ಚಾಗಿದೆ — ಮುಂದಿನ ತಿಂಗಳಿಗೆ ಒಯ್ಯಿ",
        "sales_vs_purchases": "**📊 ಮಾರಾಟ ಮತ್ತು ಖರೀದಿ**",
        "chart_info": "**ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ** (ಮಾರಾಟದಲ್ಲಿ) − **ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್** (ಖರೀದಿಯಲ್ಲಿ) = **ನಿವ್ವಳ ಜಿಎಸ್‌ಟಿ ಪಾವತಿ**",
        "recent_activity": "**🕒 ಇತ್ತೀಚಿನ ವ್ಯವಹಾರ**",
        "type_col": "ವಿಧ",
        "purchase_type": "ಖರೀದಿ",
        "sales_type": "ಮಾರಾಟ",
        "gstr_status": "**📋 ಜಿಎಸ್‌ಟಿಆರ್ ಸಲ್ಲಿಕೆ ಸ್ಥಿತಿ**",
        "no_data": "⚪ ಮಾಹಿತಿ ಇಲ್ಲ",
        "ready_to_file": "🟢 ಸಲ್ಲಿಸಲು ಸಿದ್ಧ",
        # Upload
        "upload_title": "## 📤 ಅಪ್‌ಲೋಡ್ & ಓದು",
        "upload_caption": "ನಿಮ್ಮ ಬಿಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ — ಅದು ಖರೀದಿ ಅಥವಾ ಮಾರಾಟ ಬಿಲ್ ಎಂದು ತಾನಾಗಿ ಗುರುತಿಸುತ್ತದೆ.",
        "drop_invoice": "ಬಿಲ್ ಇಲ್ಲಿ ಹಾಕಿ",
        "extract_btn": "🔍 ಮಾಹಿತಿ ತೆಗೆಯಿರಿ",
        "reading_invoice": "ಬಿಲ್ ಓದಲಾಗುತ್ತಿದೆ...",
        "extraction_complete": "✓ ಮಾಹಿತಿ ತೆಗೆಯಲಾಗಿದೆ!",
        "extraction_failed": "ತೆಗೆಯಲು ವಿಫಲ:",
        "extracted_fields": "**🔎 ತೆಗೆದ ಮಾಹಿತಿ**",
        "detection": "ಪತ್ತೆ ವಿಧಾನ:",
        "ocr_confidence": "ಓಸಿಆರ್ ವಿಶ್ವಾಸಾರ್ಹತೆ",
        "illegal_tax": "🚨 ಕಾನೂನು ಬಾಹಿರ ತೆರಿಗೆ — ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲದೆ ತೆರಿಗೆ ವಿಧಿಸಲಾಗಿದೆ. ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಲಾಗದು. ಸರಿಪಡಿಸಿದ ಬಿಲ್ ಕೇಳಿ.",
        "no_gstin_warn": "⚠️ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲ — ನೋಂದಣಿ ಇಲ್ಲದ ಅಥವಾ ಕಂಪೊಸಿಷನ್ ಯೋಜನೆ. ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಲಾಗದು.",
        "vendor_party": "ಮಾರಾಟಗಾರ / ಪಾರ್ಟಿ",
        "invoice_type": "ಬಿಲ್ ವಿಧ",
        "date_col": "ದಿನಾಂಕ",
        "gstin_col": "ಜಿಎಸ್‌ಟಿಐಎನ್",
        "no_gstin": "⚠️ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲ",
        "category_col": "ವರ್ಗ",
        "subtotal_col": "ಒಳಮೊತ್ತ",
        "cgst_col": "ಸಿಜಿಎಸ್‌ಟಿ",
        "sgst_col": "ಎಸ್‌ಜಿಎಸ್‌ಟಿ",
        "igst_col": "ಐಜಿಎಸ್‌ಟಿ",
        "total_amount": "ಒಟ್ಟು ಮೊತ್ತ",
        "field_col": "ಅಂಶ",
        "value_col": "ಮೌಲ್ಯ",
        "review_confirm": "**✏️ ಪರಿಶೀಲಿಸಿ & ದೃಢಪಡಿಸಿ**",
        "vendor_name": "ಮಾರಾಟಗಾರ / ಪಾರ್ಟಿ ಹೆಸರು",
        "txn_date": "ದಿನಾಂಕ",
        "calculated_total": "ಲೆಕ್ಕ ಮಾಡಿದ ಒಟ್ಟು",
        "confirm_btn": "✅ ದೃಢಪಡಿಸಿ & ನೋಂದಣಿಗೆ ಸೇರಿಸಿ",
        "added_to": "ಸೇರಿಸಲಾಗಿದೆ",
        "upload_first": "ದಾಖಲೆ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಮಾಹಿತಿ ತೆಗೆಯಿರಿ.",
        "purchase_invoice": "ಖರೀದಿ ಬಿಲ್",
        "sales_invoice": "ಮಾರಾಟ ಬಿಲ್",
        "credit_note": "ಕ್ರೆಡಿಟ್ ನೋಟ್",
        "debit_note": "ಡೆಬಿಟ್ ನೋಟ್",
        "expense_receipt": "ಖರ್ಚು ರಶೀದಿ",
        "to_sales_reg": "ಮಾರಾಟ ನೋಂದಣಿ",
        "to_purchase_reg": "ಖರೀದಿ ನೋಂದಣಿ",
        # Manual
        "manual_title": "## ✏️ ಕೈಯಾರೆ ನಮೂದು",
        "add_entry_btn": "➕ ನಮೂದು ಸೇರಿಸಿ",
        "vendor_required": "ಮಾರಾಟಗಾರ ಹೆಸರು ಅಗತ್ಯ.",
        "recent_entries": "**📌 ಇತ್ತೀಚಿನ ನಮೂದುಗಳು**",
        "no_entries": "ಇನ್ನೂ ನಮೂದುಗಳಿಲ್ಲ.",
        "cgst_pct": "ಸಿಜಿಎಸ್‌ಟಿ %",
        "sgst_pct": "ಎಸ್‌ಜಿಎಸ್‌ಟಿ %",
        "igst_pct": "ಐಜಿಎಸ್‌ಟಿ %",
        "subtotal_inr": "ಒಳಮೊತ್ತ (₹)",
        # Purchase Register
        "purchase_reg_title": "## 📋 ಖರೀದಿ ನೋಂದಣಿ",
        "purchase_reg_caption": "ನೀವು ಖರೀದಿದಾರರಾಗಿರುವ ಎಲ್ಲ ಬಿಲ್‌ಗಳು — ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್ ಅರ್ಹ.",
        "no_purchase": "ಇನ್ನೂ ಖರೀದಿ ನಮೂದುಗಳಿಲ್ಲ. ಖರೀದಿ ಬಿಲ್‌ಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕೈಯಾರೆ ಸೇರಿಸಿ.",
        "total_purchases_m": "ಒಟ್ಟು ಖರೀದಿ",
        "input_cgst": "ಇನ್‌ಪುಟ್ ಸಿಜಿಎಸ್‌ಟಿ (ಐಟಿಸಿ)",
        "input_sgst": "ಇನ್‌ಪುಟ್ ಎಸ್‌ಜಿಎಸ್‌ಟಿ (ಐಟಿಸಿ)",
        "total_entries": "ಒಟ್ಟು ನಮೂದುಗಳು",
        "search_vendor": "🔍 ಮಾರಾಟಗಾರ ಹುಡುಕಿ",
        "export_csv": "⬇️ ಸಿಎಸ್‌ವಿ ರಫ್ತು",
        # Sales Register
        "sales_reg_title": "## 💰 ಮಾರಾಟ ನೋಂದಣಿ",
        "sales_reg_caption": "ನೀವು ಮಾರಾಟಗಾರರಾಗಿರುವ ಎಲ್ಲ ಬಿಲ್‌ಗಳು — ಗ್ರಾಹಕರಿಂದ ಸಂಗ್ರಹಿಸಿದ ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ.",
        "no_sales": "ಇನ್ನೂ ಮಾರಾಟ ನಮೂದುಗಳಿಲ್ಲ. ಮಾರಾಟ ಬಿಲ್‌ಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕೈಯಾರೆ ಸೇರಿಸಿ.",
        "total_sales_m": "ಒಟ್ಟು ಮಾರಾಟ",
        "output_cgst": "ಔಟ್‌ಪುಟ್ ಸಿಜಿಎಸ್‌ಟಿ",
        "output_sgst": "ಔಟ್‌ಪುಟ್ ಎಸ್‌ಜಿಎಸ್‌ಟಿ",
        "search_buyer": "🔍 ಖರೀದಿದಾರ ಹುಡುಕಿ",
        # Reconciliation
        "recon_title": "## 🔄 ಜಿಎಸ್‌ಟಿ ಹೊಂದಾಣಿಕೆ",
        "no_recon_data": "ಹೊಂದಾಣಿಕೆ ಮಾಡಲು ಖರೀದಿ ಮತ್ತು ಮಾರಾಟ ನಮೂದುಗಳನ್ನು ಸೇರಿಸಿ.",
        "full_tax_stmt": "**📊 ಸಂಪೂರ್ಣ ತೆರಿಗೆ ಹೇಳಿಕೆ**",
        "tax_head": "ತೆರಿಗೆ ಮುಖ್ಯಾಂಶ",
        "input_tax_purchase": "ಇನ್‌ಪುಟ್ ತೆರಿಗೆ (ಖರೀದಿ)",
        "output_tax_sales": "ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ (ಮಾರಾಟ)",
        "net_payable": "ನಿವ್ವಳ ಪಾವತಿ",
        "net_gst_payable": "ಸರ್ಕಾರಕ್ಕೆ ನಿವ್ವಳ ಜಿಎಸ್‌ಟಿ ಪಾವತಿ",
        "pay_by_20th": "ಮುಂದಿನ ತಿಂಗಳ 20ನೇ ತಾರೀಖಿನ ಒಳಗೆ ಪಾವತಿಸಿ.",
        "itc_exceeds": "ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್ ಔಟ್‌ಪುಟ್ ತೆರಿಗೆಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ",
        "carry_fwd": "ಮುಂದಿನ ತಿಂಗಳಿಗೆ ಒಯ್ಯಿ.",
        "gstin_validation": "**✅ ಜಿಎಸ್‌ಟಿಐಎನ್ ಪರಿಶೀಲನೆ**",
        "no_gstin_col": "❌ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲ",
        "valid_gstin": "✅ ಮಾನ್ಯ",
        "invalid_gstin": "⚠️ ಅಮಾನ್ಯ ಮಾದರಿ",
        "register_col": "ನೋಂದಣಿ",
        "valid_col": "ಮಾನ್ಯತೆ",
        # GSTR-1
        "gstr1_title": "## 📄 ಜಿಎಸ್‌ಟಿಆರ್-1 — ಹೊರ ಪೂರೈಕೆ",
        "gstr1_caption": "ಹೊರ ಪೂರೈಕೆಯ ಹೇಳಿಕೆ — ಮುಂದಿನ ತಿಂಗಳ 11ರ ಒಳಗೆ ಸಲ್ಲಿಸಿ.",
        "gstr1_info": "ℹ️ ಬಿ2ಬಿ ಬಿಲ್‌ಗಳು ಖರೀದಿದಾರನ ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ನಲ್ಲಿ ತಾನಾಗಿ ಕಾಣಿಸುತ್ತವೆ.",
        "no_sales_gstr1": "ಮಾರಾಟ ಮಾಹಿತಿಯಿಲ್ಲ. ಜಿಎಸ್‌ಟಿಆರ್-1 ರಚಿಸಲು ಮಾರಾಟ ಬಿಲ್‌ಗಳನ್ನು ಸೇರಿಸಿ.",
        "taxable_turnover": "ತೆರಿಗೆ ವಿಧಿಸಬಹುದಾದ ವಹಿವಾಟು",
        "grand_total": "ಒಟ್ಟು ಮೊತ್ತ",
        "b2b_tab": "📦 ಬಿ2ಬಿ ಬಿಲ್‌ಗಳು",
        "b2c_tab": "🛒 ಬಿ2ಸಿ ಬಿಲ್‌ಗಳು",
        "hsn_tab": "📊 ಎಚ್‌ಎಸ್‌ಎನ್ ಸಾರಾಂಶ",
        "full_table_tab": "📋 ಸಂಪೂರ್ಣ ಪಟ್ಟಿ",
        "b2b_caption": "ಬಿ2ಬಿ ಬಿಲ್‌ಗಳು (ಜಿಎಸ್‌ಟಿಐಎನ್ ಸಹಿತ) — ಖರೀದಿದಾರನ ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ನಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ.",
        "b2c_caption": "ಬಿ2ಸಿ ಬಿಲ್‌ಗಳು (ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲ) — ಖರೀದಿದಾರ ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಲಾಗದು.",
        "no_b2b": "ಬಿ2ಬಿ ಬಿಲ್‌ಗಳಿಲ್ಲ.",
        "no_b2c": "ಬಿ2ಸಿ ಬಿಲ್‌ಗಳಿಲ್ಲ.",
        "hsn_caption": "ವರ್ಗವಾರು ಸಾರಾಂಶ (ಎಚ್‌ಎಸ್‌ಎನ್/ಎಸ್‌ಎಸಿ ಗುಂಪಿನ ಪ್ರಾಕ್ಸಿ).",
        "invoices_col": "ಬಿಲ್‌ಗಳು",
        "taxable_col": "ತೆರಿಗೆಯೋಗ್ಯ",
        "download_gstr1": "⬇️ ಜಿಎಸ್‌ಟಿಆರ್-1 ಸಿಎಸ್‌ವಿ ಡೌನ್‌ಲೋಡ್",
        # GSTR-3B
        "gstr3b_title": "## 📑 ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ — ಮಾಸಿಕ ಸಾರಾಂಶ ರಿಟರ್ನ್",
        "gstr3b_caption": "ನಿವ್ವಳ ತೆರಿಗೆ ಪಾವತಿಯ ಸ್ವ-ಘೋಷಣೆ — ಮುಂದಿನ ತಿಂಗಳ 20ರ ಒಳಗೆ ಸಲ್ಲಿಸಿ.",
        "gstr3b_warn": "⚠️ ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ − ಐಟಿಸಿ = ನಿವ್ವಳ ತೆರಿಗೆ ಪಾವತಿ. ತಡವಾದ ಪಾವತಿಗೆ ವರ್ಷಕ್ಕೆ 18% ಬಡ್ಡಿ.",
        "no_data_gstr3b": "ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ ರಚಿಸಲು ಮಾರಾಟ ಮತ್ತು ಖರೀದಿ ನಮೂದುಗಳನ್ನು ಸೇರಿಸಿ.",
        "output_tax_tab": "📋 3.1 ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ",
        "itc_tab": "📥 4. ಐಟಿಸಿ ಲಭ್ಯ",
        "net_tax_tab": "💰 ನಿವ್ವಳ ತೆರಿಗೆ ಪಾವತಿ",
        "output_tax_heading": "**ಕೋಷ್ಟಕ 3.1 — ಹೊರ ಪೂರೈಕೆ ಮತ್ತು ತೆರಿಗೆ ಹೊಣೆ ವಿವರ**",
        "itc_heading": "**ಕೋಷ್ಟಕ 4 — ಅರ್ಹ ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್ (ಐಟಿಸಿ)**",
        "net_tax_heading": "**ಕೋಷ್ಟಕ 6.1 — ನಿವ್ವಳ ತೆರಿಗೆ ಪಾವತಿ**",
        "section_col": "ವಿಭಾಗ",
        "nature_col": "ಸ್ವಭಾವ",
        "outward_taxable": "ಹೊರ ತೆರಿಗೆಯೋಗ್ಯ ಪೂರೈಕೆ",
        "zero_rated": "ಶೂನ್ಯ ದರದ ಪೂರೈಕೆ",
        "nil_rated": "ಶೂನ್ಯ / ವಿನಾಯಿತಿ ದರ",
        "itc_imports_goods": "ಆಮದು ಸರಕಿನ ಐಟಿಸಿ",
        "itc_imports_svc": "ಆಮದು ಸೇವೆಯ ಐಟಿಸಿ",
        "itc_domestic": "ಇತರ ಎಲ್ಲ ಐಟಿಸಿ (ದೇಶೀಯ)",
        "output_liability": "ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ ಹೊಣೆ",
        "less_itc": "ಕಡಿಮೆ: ಲಭ್ಯ ಐಟಿಸಿ",
        "net_tax_payable": "ನಿವ್ವಳ ತೆರಿಗೆ ಪಾವತಿ",
        "owe_gst": "ನೀವು ₹{} ಜಿಎಸ್‌ಟಿ ಕೊಡಬೇಕು. ಜಿಎಸ್‌ಟಿಎನ್ ಪೋರ್ಟಲ್ ಮೂಲಕ 20ರ ಒಳಗೆ ಪಾವತಿಸಿ.",
        "excess_itc": "₹{} ಹೆಚ್ಚಿನ ಐಟಿಸಿ — ಮುಂದಿನ ಅವಧಿಗೆ ಒಯ್ಯಿ.",
        "download_gstr3b": "⬇️ ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ ಸಿಎಸ್‌ವಿ ಡೌನ್‌ಲೋಡ್",
        # GSTR-2A/2B
        "gstr2_title": "## 🔍 ಜಿಎಸ್‌ಟಿಆರ್-2ಎ / 2ಬಿ — ಒಳ ಪೂರೈಕೆ ಐಟಿಸಿ",
        "gstr2_caption": "ನಿಮ್ಮ ಪೂರೈಕೆದಾರರ ಜಿಎಸ್‌ಟಿಆರ್-1 ಸಲ್ಲಿಕೆಯಿಂದ ತಾನಾಗಿ ತುಂಬಿಸಲಾಗಿದೆ.",
        "gstr2a_dynamic": "**📡 ಜಿಎಸ್‌ಟಿಆರ್-2ಎ — ಕ್ರಿಯಾಶೀಲ:** ಪೂರೈಕೆದಾರರು ಸಲ್ಲಿಸಿದಾಗ ತಾನಾಗಿ ನವೀಕರಣಗೊಳ್ಳುತ್ತದೆ.",
        "gstr2b_static": "**🔒 ಜಿಎಸ್‌ಟಿಆರ್-2ಬಿ — ಸ್ಥಿರ:** ಒಂದು ಅವಧಿಗೆ ಲಾಕ್ ಮಾಡಿದ ಮಾಹಿತಿ. 3ಬಿ ನಲ್ಲಿ ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಲು ಬಳಸಿ.",
        "gstr2a_tab": "📡 ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ಮಾಹಿತಿ",
        "gstr2b_tab": "🔒 ಜಿಎಸ್‌ಟಿಆರ್-2ಬಿ (ಸ್ಥಿರ)",
        "recon_tab": "🔍 ಹೊಂದಾಣಿಕೆ",
        "add_2a_tab": "➕ 2ಎ ನಮೂದು ಸೇರಿಸಿ",
        "add_2a_caption": "ಪೂರೈಕೆದಾರ ಸಲ್ಲಿಸಿದ ನಮೂದುಗಳನ್ನು ಅನುಕರಿಸಿ (ಉತ್ಪಾದನೆಯಲ್ಲಿ ಜಿಎಸ್‌ಟಿಎನ್ ಎಪಿಐ ಮೂಲಕ ಬರುತ್ತದೆ).",
        "supplier_gstin": "ಪೂರೈಕೆದಾರ ಜಿಎಸ್‌ಟಿಐಎನ್",
        "supplier_name": "ಪೂರೈಕೆದಾರ ಹೆಸರು",
        "invoice_no": "ಬಿಲ್ ಸಂಖ್ಯೆ",
        "invoice_date": "ಬಿಲ್ ದಿನಾಂಕ",
        "taxable_value": "ತೆರಿಗೆಯೋಗ್ಯ ಮೌಲ್ಯ (₹)",
        "add_2a_btn": "➕ ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ಗೆ ಸೇರಿಸಿ",
        "added_to_2a": "{} ದಿಂದ ನಮೂದು ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ಗೆ ಸೇರಿಸಲಾಗಿದೆ.",
        "no_2a_data": "ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ನಮೂದುಗಳಿಲ್ಲ. '2ಎ ನಮೂದು ಸೇರಿಸಿ' ಟ್ಯಾಬ್‌ಗೆ ಹೋಗಿ.",
        "suppliers_filed": "ಸಲ್ಲಿಸಿದ ಪೂರೈಕೆದಾರರು",
        "total_invoices": "ಒಟ್ಟು ಬಿಲ್‌ಗಳು",
        "itc_available": "ಲಭ್ಯ ಐಟಿಸಿ",
        "download_2a": "⬇️ ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ಸಿಎಸ್‌ವಿ ಡೌನ್‌ಲೋಡ್",
        "no_2b_data": "ಮೊದಲು 2ಎ ನಮೂದುಗಳನ್ನು ಸೇರಿಸಿ — ಜಿಎಸ್‌ಟಿಆರ್-2ಬಿ ಅದರಿಂದ ರಚಿಸಲಾಗುತ್ತದೆ.",
        "gstr2b_locked": "🔒 ಜಿಎಸ್‌ಟಿಆರ್-2ಬಿ ಲಾಕ್ ಆಗಿದೆ — ಒಟ್ಟು ಕ್ಲೈಮ್ ಮಾಡಬಹುದಾದ ಐಟಿಸಿ:",
        "download_2b": "⬇️ ಜಿಎಸ್‌ಟಿಆರ್-2ಬಿ ಸಿಎಸ್‌ವಿ ಡೌನ್‌ಲೋಡ್",
        "recon_caption": "ಐಟಿಸಿ ಗುರುತಿಸಲು ನಿಮ್ಮ ಖರೀದಿ ನೋಂದಣಿ ಮತ್ತು ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ಹೊಂದಿಸಿ.",
        "no_purchase_recon": "ಹೊಂದಿಸಲು ಖರೀದಿ ನಮೂದುಗಳಿಲ್ಲ.",
        "no_2a_recon": "ಹೊಂದಿಸಲು 2ಎ ನಮೂದುಗಳು ಮತ್ತು ಖರೀದಿ ಬಿಲ್‌ಗಳು ಬೇಕು.",
        "matched": "✅ ಹೊಂದಿಕೆಯಾಗಿದೆ",
        "mismatch": "❌ ಮೊತ್ತ ಹೊಂದುತ್ತಿಲ್ಲ",
        "not_in_2a": "⚠️ ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ನಲ್ಲಿ ಇಲ್ಲ",
        "itc_claimable_col": "ಐಟಿಸಿ ಕ್ಲೈಮ್ ಸಾಧ್ಯ",
        "action_guide": """**ಕ್ರಿಯಾ ಮಾರ್ಗದರ್ಶಿ:**
- ✅ **ಹೊಂದಿಕೆ** — ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ ಕೋಷ್ಟಕ 4 ನಲ್ಲಿ ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಿ
- ❌ **ಮೊತ್ತ ಹೊಂದುತ್ತಿಲ್ಲ** — ಪೂರೈಕೆದಾರರನ್ನು ಜಿಎಸ್‌ಟಿಆರ್-1 ತಿದ್ದಲು ಹೇಳಿ
- ⚠️ **2ಎ ನಲ್ಲಿ ಇಲ್ಲ** — ಪೂರೈಕೆದಾರ ಸಲ್ಲಿಸಿಲ್ಲ. ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡುವ ಮೊದಲು ಅನುಸರಿಸಿ""",
        "download_recon": "⬇️ ಹೊಂದಾಣಿಕೆ ಸಿಎಸ್‌ವಿ ಡೌನ್‌ಲೋಡ್",
        # User Guide
        "guide_title": "## 📖 ಬಳಕೆದಾರ ಮಾರ್ಗದರ್ಶಿ",
        "guide_caption": "ಫಿನ್‌ಫ್ಲೋ ಬಳಸುವ ಸಂಪೂರ್ಣ ಹಂತ ಹಂತದ ಮಾರ್ಗದರ್ಶಿ.",
        "how_works": "**📋 ಫಿನ್‌ಫ್ಲೋ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ**",
        "how_works_flow": "**ಬಿಲ್ → ಓಸಿಆರ್ ಓದುತ್ತದೆ → ತಾನಾಗಿ ವಿಂಗಡಿಸುತ್ತದೆ (ಖರೀದಿ / ಮಾರಾಟ) → ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ → ಜಿಎಸ್‌ಟಿ ಸಲ್ಲಿಸಿ**",
        "step_by_step": "**🪜 ಹಂತ ಹಂತವಾಗಿ ಬಳಸಿ**",
        "steps": [
            ("1️⃣ ಬಿಲ್ ಅಪ್‌ಲೋಡ್", "📤 ಅಪ್‌ಲೋಡ್ & ಓದು ಗೆ ಹೋಗಿ → ಪಿಡಿಎಫ್ / ಫೋಟೋ ಆಯ್ಕೆ → 🔍 ಮಾಹಿತಿ ತೆಗೆಯಿರಿ ಕ್ಲಿಕ್ ಮಾಡಿ."),
            ("2️⃣ ಪರಿಶೀಲಿಸಿ & ದೃಢಪಡಿಸಿ", "ಹೆಸರು, ಮೊತ್ತ, ಸಿಜಿಎಸ್‌ಟಿ/ಎಸ್‌ಜಿಎಸ್‌ಟಿ/ಐಜಿಎಸ್‌ಟಿ ನೋಡಿ → ತಪ್ಪಿದ್ದರೆ ಸರಿಪಡಿಸಿ → ✅ ದೃಢಪಡಿಸಿ & ನೋಂದಣಿಗೆ ಸೇರಿಸಿ ಕ್ಲಿಕ್ ಮಾಡಿ."),
            ("3️⃣ ನೋಂದಣಿ ನೋಡಿ", "📋 ಖರೀದಿ ನೋಂದಣಿ = ನೀವು ಕೊಂಡ ಬಿಲ್‌ಗಳು  |  💰 ಮಾರಾಟ ನೋಂದಣಿ = ನೀವು ಮಾರಿದ ಬಿಲ್‌ಗಳು."),
            ("4️⃣ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ನೋಡಿ", "📊 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ನಲ್ಲಿ ಒಟ್ಟು ಖರೀದಿ, ಮಾರಾಟ ಮತ್ತು ನಿವ್ವಳ ಜಿಎಸ್‌ಟಿ ಪಾವತಿ ತಾನಾಗಿ ಕಾಣಿಸುತ್ತದೆ."),
            ("5️⃣ ಜಿಎಸ್‌ಟಿ ವರದಿ", "📄 ಜಿಎಸ್‌ಟಿಆರ್-1 (ಮಾರಾಟಕ್ಕೆ)  |  📑 ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ (ನಿವ್ವಳ ತೆರಿಗೆಗೆ) → ಸಿಎಸ್‌ವಿ ಡೌನ್‌ಲೋಡ್ → ಜಿಎಸ್‌ಟಿ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಸಲ್ಲಿಸಿ."),
            ("6️⃣ ಹೊಂದಾಣಿಕೆ", "🔄 ಎಲ್ಲ ಜಿಎಸ್‌ಟಿಐಎನ್ ಗಳು ಮಾನ್ಯವಾಗಿವೆಯೇ ಪರಿಶೀಲಿಸಿ → ನೋಂದಣಿ ಇಲ್ಲದ ವ್ಯಾಪಾರಿಗಳನ್ನು ಗುರುತಿಸಿ."),
        ],
        "itc_rules": "**💡 ಐಟಿಸಿ ನಿಯಮಗಳು — ಯಾವಾಗ ಕ್ಲೈಮ್ ಮಾಡಬಹುದು?**",
        "itc_yes": "**✅ ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಬಹುದು**\n\n✔ ಪೂರೈಕೆದಾರರಿಗೆ ಮಾನ್ಯ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇದೆ\n\n✔ ಅವರು ಜಿಎಸ್‌ಟಿಆರ್-1 ಸಲ್ಲಿಸಿದ್ದಾರೆ\n\n✔ ಬಿಲ್‌ನಲ್ಲಿ ಜಿಎಸ್‌ಟಿ ಮೊತ್ತ ಇದೆ\n\n✔ ನಿಮ್ಮ ಜಿಎಸ್‌ಟಿಆರ್-2ಎ ನಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ",
        "itc_no": "**❌ ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಲಾಗದು**\n\n✘ ಪೂರೈಕೆದಾರರಿಗೆ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲ\n\n✘ ಪೂರೈಕೆದಾರರು ಕಂಪೊಸಿಷನ್ ಯೋಜನೆಯಲ್ಲಿದ್ದಾರೆ\n\n✘ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲದೆ ತೆರಿಗೆ ವಿಧಿಸಿದ್ದಾರೆ (ಕಾನೂನು ಬಾಹಿರ)\n\n✘ ಪೂರೈಕೆದಾರರು ಜಿಎಸ್‌ಟಿಆರ್-1 ಸಲ್ಲಿಸಿಲ್ಲ",
        "itc_warn": "⚠️ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲದ ಪೂರೈಕೆದಾರರು ಕಾನೂನುಬದ್ಧವಾಗಿ ಜಿಎಸ್‌ಟಿ ವಿಧಿಸಲಾಗದು. ಅಂತಹ ಖರೀದಿಗಳಲ್ಲಿ ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಲಾಗದು — ಸರಿಪಡಿಸಿದ ಬಿಲ್ ಕೇಳಿ.",
        "faq_title": "**❓ ಸಾಮಾನ್ಯ ಪ್ರಶ್ನೆಗಳು**",
        "faqs": [
            ("ಐಟಿಸಿ ಎಂದರೇನು?", "ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್ ಎಂದರೆ ನೀವು ಖರೀದಿಯಲ್ಲಿ ಪಾವತಿಸಿದ ಜಿಎಸ್‌ಟಿ ಅನ್ನು ಮಾರಾಟದಲ್ಲಿ ಸಂಗ್ರಹಿಸಿದ ಜಿಎಸ್‌ಟಿ ನಿಂದ ಕಳೆಯಬಹುದು. ವ್ಯತ್ಯಾಸ ಮಾತ್ರ ಸರ್ಕಾರಕ್ಕೆ ಪಾವತಿಸಬೇಕು."),
            ("ನನ್ನ ಪೂರೈಕೆದಾರರಿಗೆ ಜಿಎಸ್‌ಟಿಐಎನ್ ಇಲ್ಲ — ಐಟಿಸಿ ಕ್ಲೈಮ್ ಮಾಡಬಹುದೇ?", "ಇಲ್ಲ. ನೋಂದಣಿ ಇಲ್ಲದ ಪೂರೈಕೆದಾರರು ಕಾನೂನುಬದ್ಧವಾಗಿ ಜಿಎಸ್‌ಟಿ ವಿಧಿಸಲಾಗದು. ಜಿಎಸ್‌ಟಿ ಇಲ್ಲದ ಸರಿಪಡಿಸಿದ ಬಿಲ್ ಕೇಳಿ."),
            ("ಕಂಪೊಸಿಷನ್ ಯೋಜನೆ ಎಂದರೇನು?", "₹1.5 ಕೋಟಿಗಿಂತ ಕಡಿಮೆ ವಹಿವಾಟು ಇರುವ ಸಣ್ಣ ವ್ಯವಹಾರಗಳು ಕಡಿಮೆ ದರದಲ್ಲಿ ತೆರಿಗೆ ಪಾವತಿಸಬಹುದು ಆದರೆ ಖರೀದಿದಾರರಿಂದ ಜಿಎಸ್‌ಟಿ ಸಂಗ್ರಹಿಸಲಾಗದು."),
            ("ಓಸಿಆರ್ ತಪ್ಪಾದ ಮೊತ್ತ ಓದಿದರೆ?", "ನಮೂದು ಮಾಡುವ ಮೊದಲು 'ಪರಿಶೀಲಿಸಿ & ದೃಢಪಡಿಸಿ' ವಿಭಾಗದಲ್ಲಿ ಯಾವುದೇ ಅಂಶವನ್ನು ಸರಿಪಡಿಸಿ."),
            ("ಎಷ್ಟು ಬಾರಿ ಜಿಎಸ್‌ಟಿ ಸಲ್ಲಿಸಬೇಕು?", "ಜಿಎಸ್‌ಟಿಆರ್-1 ಪ್ರತಿ ತಿಂಗಳ 11 ರ ಒಳಗೆ | ಜಿಎಸ್‌ಟಿಆರ್-3ಬಿ 20 ರ ಒಳಗೆ. ತಡವಾದರೆ ₹50/ದಿನ + ವರ್ಷಕ್ಕೆ 18% ಬಡ್ಡಿ."),
            ("ಹೊರಗೆ ಹೋಗಿ ಮತ್ತೆ ಒಳಗೆ ಬಂದರೆ ನಮೂದುಗಳು ಉಳಿಯುತ್ತವೆಯೇ?", "ಹೌದು! ಫಿನ್‌ಫ್ಲೋ ಎಲ್ಲ ನಮೂದುಗಳನ್ನು ನಿಮ್ಮ ಲಾಗಿನ್ ಐಡಿ ಗೆ ಜೋಡಿಸಿ ಉಳಿಸುತ್ತದೆ — ಅದೇ ಬ್ರೌಸರ್ ಸೆಷನ್‌ನಲ್ಲಿ ಮತ್ತೆ ಒಳಗೆ ಬಂದಾಗ ಕಾಣಿಸುತ್ತದೆ."),
        ],
        # Settings
        "settings_title": "## ⚙️ ಸೆಟ್ಟಿಂಗ್ಸ್",
        "settings_caption": "ನಿಮ್ಮ ವ್ಯವಹಾರದ ಮಾಹಿತಿ — ಮಾರಾಟ ಮತ್ತು ಖರೀದಿ ಬಿಲ್ ಪತ್ತೆಗೆ ಬಳಸಲಾಗುತ್ತದೆ.",
        "biz_tab": "🏢 ವ್ಯವಹಾರ ಗುರುತು",
        "pwd_tab": "🔑 ಗುಪ್ತಪದ ಬದಲಿಸಿ",
        "current_biz": "**ಪ್ರಸ್ತುತ ವ್ಯವಹಾರ ಗುರುತು**",
        "biz_name": "ವ್ಯವಹಾರದ ಹೆಸರು",
        "city_lbl": "ನಗರ",
        "state_lbl": "ರಾಜ್ಯ",
        "my_gstin": "ನನ್ನ ಜಿಎಸ್‌ಟಿಐಎನ್",
        "update_details": "**✏️ ವಿವರ ನವೀಕರಿಸಿ**",
        "save_settings": "💾 ಸೆಟ್ಟಿಂಗ್ಸ್ ಉಳಿಸಿ",
        "biz_empty": "ವ್ಯವಹಾರದ ಹೆಸರು ಖಾಲಿ ಇರಬಾರದು.",
        "gstin_empty": "ಜಿಎಸ್‌ಟಿಐಎನ್ ಖಾಲಿ ಇರಬಾರದು.",
        "saved_ok": "✅ ಉಳಿಸಲಾಗಿದೆ! ಬಿಲ್ ಪತ್ತೆಗೆ **{}** ({}) ಬಳಸಲಾಗುತ್ತಿದೆ.",
        "valid_gstin": "✅ ಮಾನ್ಯ ಜಿಎಸ್‌ಟಿಐಎನ್ ಮಾದರಿ",
        "gstin_warn": "⚠️ ಮಾದರಿ ಸರಿ ಇಲ್ಲ — 29ABCDE1234F1Z5 ರೀತಿ 15 ಅಕ್ಷರಗಳು ಇರಬೇಕು",
        "change_pwd": "**🔑 ನಿಮ್ಮ ಗುಪ್ತಪದ ಬದಲಿಸಿ**",
        "current_pwd": "ಪ್ರಸ್ತುತ ಗುಪ್ತಪದ",
        "new_pwd_lbl": "ಹೊಸ ಗುಪ್ತಪದ",
        "new_pwd_help": "6–12 ಅಕ್ಷರಗಳು, 1 ದೊಡ್ಡ ಅಕ್ಷರ, 1 ವಿಶೇಷ ಚಿಹ್ನೆ",
        "confirm_new_pwd": "ಹೊಸ ಗುಪ್ತಪದ ದೃಢಪಡಿಸಿ",
        "update_pwd_btn": "🔒 ಗುಪ್ತಪದ ನವೀಕರಿಸಿ",
        "wrong_current_pwd": "ಪ್ರಸ್ತುತ ಗುಪ್ತಪದ ತಪ್ಪಾಗಿದೆ.",
        "pwd_updated": "✅ ಗುಪ್ತಪದ ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ!",
        "invoice_detection": "**ℹ️ ಬಿಲ್ ಪತ್ತೆ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ**",
        "detect_table": """| ಆದ್ಯತೆ | ವಿಧಾನ | ತರ್ಕ |
|--------|--------|------|
| 1️⃣ | **ಜಿಎಸ್‌ಟಿಐಎನ್ ಸ್ಥಾನ** | ಮಾರಾಟಗಾರ ಬ್ಲಾಕ್‌ನಲ್ಲಿ ನಿಮ್ಮ ಜಿಎಸ್‌ಟಿಐಎನ್ → ಮಾರಾಟ ಬಿಲ್ |
| 1️⃣ | **ಜಿಎಸ್‌ಟಿಐಎನ್ ಸ್ಥಾನ** | ಬಿಲ್ ಟು ಬ್ಲಾಕ್‌ನಲ್ಲಿ ನಿಮ್ಮ ಜಿಎಸ್‌ಟಿಐಎನ್ → ಖರೀದಿ ಬಿಲ್ |
| 2️⃣ | **ಹೆಸರು ಹೊಂದಾಣಿಕೆ** | ಮಾರಾಟಗಾರ / ಖರೀದಿದಾರ ವಿಭಾಗದಲ್ಲಿ ನಿಮ್ಮ ವ್ಯವಹಾರ ಹೆಸರು |
| 3️⃣ | **ಕೀಲಿಪದ** | "ಮಾರಾಟ ಬಿಲ್" / "ಖರೀದಿ ಬಿಲ್" ಪಠ್ಯ ಇದೆ |
| 4️⃣ | **ಸ್ಥಾನ** | ಮೇಲ್ಭಾಗದಲ್ಲಿ ನಿಮ್ಮ ಜಿಎಸ್‌ಟಿಐಎನ್ → ಮಾರಾಟ, ಇಲ್ಲವಾದರೆ ಖರೀದಿ |""",
        # Categories in Kannada
        "categories": ["ಕಚ್ಚಾ ವಸ್ತುಗಳು", "ಕಚೇರಿ ಸಾಮಗ್ರಿ", "ಪ್ರಯಾಣ & ಸಾರಿಗೆ", "ಉಪಯೋಗಗಳು", "ಬಾಡಿಗೆ", "ವೃತ್ತಿಪರ ಸೇವೆ", "ಐಟಿ & ತಂತ್ರಾಂಶ", "ಮಾರ್ಕೆಟಿಂಗ್", "ಇತರ"],
        "role_lbl": "ನಿರ್ವಾಹಕ",
        "invoices_count": "ಬಿಲ್‌ಗಳು",
        "needscorrection": "ತಿದ್ದುಪಡಿ ಬೇಕು",
        "follow_up": "ಅನುಸರಿಸಿ",
        "itc_claimable": "ಐಟಿಸಿ ಕ್ಲೈಮ್ ಸಾಧ್ಯ",
        "total_col": "ಒಟ್ಟು",
        "status_col": "ಸ್ಥಿತಿ",
        "id_col": "ಐಡಿ",
    }
}

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
COLS = ["ID", "Date", "Vendor", "GSTIN",
        "Subtotal", "CGST", "SGST", "IGST", "Total", "Status"]

# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────
def validate_password(pwd: str):
    rules = [
        ("min_len", len(pwd) >= 6,                          "pwd_r1"),
        ("max_len", len(pwd) <= 12,                         "pwd_r2"),
        ("upper",   bool(re.search(r'[A-Z]', pwd)),         "pwd_r3"),
        ("special", bool(re.search(r'[^A-Za-z0-9]', pwd)), "pwd_r4"),
    ]
    all_ok = all(ok for _, ok, _ in rules)
    return all_ok, rules

# ─────────────────────────────────────────────
# USER DB — single role: Admin
# ─────────────────────────────────────────────
EMPTY_DATA = lambda: {
    "purchase_register": [], "sales_register": [], "gstr2a_data": [],
    "counter": 1,
    "my_gstin": "29AAAAA1111B1Z1", "my_name": "Sai Coffee Traders",
    "my_city": "Dharwad", "my_state": "Karnataka",
}

def get_user_db():
    if "user_db" not in st.session_state:
        st.session_state["user_db"] = {
            "admin": {"password": "Admin@123", "name": "Admin User", "color": "#00E5A0", "data": EMPTY_DATA()},
        }
    return st.session_state["user_db"]

def get_user_data():
    return get_user_db()[st.session_state.username]["data"]

def save_setting_val(key, value):
    get_user_data()[key] = value

def get_setting(key, default=""):
    if not st.session_state.get("logged_in"):
        return default
    return get_user_data().get(key, default)

def get_register(key):
    rows = get_user_data().get(key, [])
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=COLS)

def set_register(key, df):
    get_user_data()[key] = df.to_dict("records")

def get_counter():
    return get_user_data().get("counter", 1)

def inc_counter():
    get_user_data()["counter"] = get_user_data().get("counter", 1) + 1

def get_gstr2a():
    GCOLS = ["GSTIN","Vendor","InvoiceNo","Date","Taxable","CGST","SGST","IGST","Total","Source"]
    rows = get_user_data().get("gstr2a_data", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=GCOLS)

def set_gstr2a(df):
    get_user_data()["gstr2a_data"] = df.to_dict("records")

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for k, v in {"logged_in": False, "username": "", "user_name": "", "user_color": "#00E5A0",
             "page": "Dashboard", "extracted": None, "lang": "English"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def t(key):
    lang = st.session_state.get("lang", "English")
    return T.get(lang, T["English"]).get(key, T["English"].get(key, key))

def fmt_inr(val):
    try: return f"₹{float(val):,.2f}"
    except: return "₹0.00"

def make_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%y%m%d')}-{get_counter():04d}"

def add_to_register(data, doc_type):
    is_sales = "Sales" in doc_type or t("sales_invoice") in doc_type
    prefix = "SAL" if is_sales else "PUR"
    row = {"ID": make_id(prefix), "Date": data.get("date",""), "Vendor": data.get("vendor",""),
           "GSTIN": data.get("gstin",""), "Category": "Goods",
           "Subtotal": data.get("subtotal",0), "CGST": data.get("cgst",0),
           "SGST": data.get("sgst",0), "IGST": data.get("igst",0),
           "Total": data.get("total",0), "Status": "Verified"}
    reg_key = "sales_register" if is_sales else "purchase_register"
    updated = pd.concat([get_register(reg_key), pd.DataFrame([row])], ignore_index=True)
    set_register(reg_key, updated)
    inc_counter()
    return row["ID"], reg_key

def get_tax_summary():
    p = get_register("purchase_register")
    s = get_register("sales_register")
    def ts(df):
        if df.empty: return 0.,0.,0.,0.
        return (df["CGST"].astype(float).sum(), df["SGST"].astype(float).sum(),
                df["IGST"].astype(float).sum(), df["Total"].astype(float).sum())
    pc,ps,pi,pt = ts(p); sc,ss,si,st_ = ts(s)
    return {"p_cgst":pc,"p_sgst":ps,"p_igst":pi,"p_total":pt,
            "s_cgst":sc,"s_sgst":ss,"s_igst":si,"s_total":st_,
            "net_cgst":round(sc-pc,2),"net_sgst":round(ss-ps,2),
            "net_igst":round(si-pi,2),"net_tax":round((sc+ss+si)-(pc+ps+pi),2),
            "p_count":len(p),"s_count":len(s)}

def build_gstr1(sdf):
    if sdf.empty: return {},pd.DataFrame(),pd.DataFrame()
    df=sdf.copy()
    for c in ["CGST","SGST","IGST","Subtotal","Total"]: df[c]=df[c].astype(float)
    b2b=df[df["GSTIN"].str.strip().str.len()>5].copy() if "GSTIN" in df.columns else pd.DataFrame()
    b2c=df[~df.index.isin(b2b.index)].copy()
    s={"b2b_count":len(b2b),"b2c_count":len(b2c),
       "total_taxable":df["Subtotal"].sum(),"total_cgst":df["CGST"].sum(),
       "total_sgst":df["SGST"].sum(),"total_igst":df["IGST"].sum(),
       "grand_total":df["Total"].sum()}
    s["total_tax"]=s["total_cgst"]+s["total_sgst"]+s["total_igst"]
    return s,b2b,b2c

def build_gstr3b(sdf,pdf):
    def sm(df):
        if df.empty: return 0.,0.,0.,0.
        return (df["Subtotal"].astype(float).sum(),df["CGST"].astype(float).sum(),
                df["SGST"].astype(float).sum(),df["IGST"].astype(float).sum())
    ss,sc,sg,si=sm(sdf); ps,pc,pg,pi=sm(pdf)
    return {"out_taxable":ss,"out_cgst":sc,"out_sgst":sg,"out_igst":si,
            "itc_taxable":ps,"itc_cgst":pc,"itc_sgst":pg,"itc_igst":pi,
            "net_cgst":round(sc-pc,2),"net_sgst":round(sg-pg,2),
            "net_igst":round(si-pi,2),"net_total":round((sc+sg+si)-(pc+pg+pi),2)}

def build_gstr2a_2b(pdf,g2a):
    if pdf.empty: return pd.DataFrame(),pd.DataFrame(),pd.DataFrame()
    pr=pdf.copy()
    for c in ["CGST","SGST","IGST","Total","Subtotal"]: pr[c]=pr[c].astype(float)
    g2b=g2a.copy()
    if not g2b.empty: g2b["Source"]="GSTR-2B (Locked)"
    rows=[]
    for _,row in pr.iterrows():
        gstin=str(row.get("GSTIN","")).strip()
        matched=g2a[g2a["GSTIN"]==gstin] if not g2a.empty and gstin else pd.DataFrame()
        if matched.empty: status=t("not_in_2a")
        else:
            a_c=matched["CGST"].astype(float).sum(); a_i=matched["IGST"].astype(float).sum()
            status=(t("matched") if abs(float(row["CGST"])-a_c)<1. or abs(float(row["IGST"])-a_i)<1. else t("mismatch"))
        rows.append({"ID":row["ID"],"Vendor":str(row.get("Vendor","")),"GSTIN":gstin,
                     "Your CGST":row["CGST"],"Your IGST":row["IGST"],
                     "2A CGST":matched["CGST"].astype(float).sum() if not matched.empty else 0.,
                     "2A IGST":matched["IGST"].astype(float).sum() if not matched.empty else 0.,
                     "Status":status,"ITC Claimable":"Yes" if status==t("matched") else "No"})
    return g2a,g2b,pd.DataFrame(rows)

# ─────────────────────────────────────────────
# OCR + PARSE
# ─────────────────────────────────────────────
def run_ocr(uploaded_file):
    try: import pytesseract; from PIL import Image
    except: raise ImportError("pip install pytesseract pillow")
    import shutil
    if shutil.which("tesseract") is None:
        for p in [r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                  r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]:
            if os.path.exists(p): pytesseract.pytesseract.tesseract_cmd=p; break
    fb=uploaded_file.read(); ext=uploaded_file.name.lower().rsplit(".",1)[-1]
    if ext=="pdf":
        try:
            import fitz; doc=fitz.open(stream=fb,filetype="pdf")
            pix=doc[0].get_pixmap(matrix=fitz.Matrix(3,3))
            from PIL import Image; img=Image.open(BytesIO(pix.tobytes("png")))
        except:
            from pdf2image import convert_from_bytes; img=convert_from_bytes(fb,dpi=300)[0]
    else:
        from PIL import Image; img=Image.open(BytesIO(fb))
    raw=pytesseract.image_to_string(img,lang="eng")
    if not raw.strip(): st.error("OCR found no text."); return {}
    return parse_invoice_text(raw)

def get_my_identity():
    gstin=get_setting("my_gstin","29AAAAA1111B1Z1").strip().upper()
    name=get_setting("my_name","Sai Coffee Traders").strip()
    aliases=[name.lower(),name.lower().replace(" ",""),gstin.lower()]
    for w in name.lower().split():
        if len(w)>3: aliases.append(w)
    return gstin,name,aliases

def parse_invoice_text(text):
    lines=[l.strip() for l in text.splitlines() if l.strip()]
    full=" ".join(lines); fl=full.lower()

    def fa(pats):
        for p in pats:
            m=re.search(p,full,re.IGNORECASE)
            if m:
                try: return float(m.group(1).replace(",","").replace(" ",""))
                except: pass
        return 0.

    # ── GSTIN extraction: robust multi-pass ──────────────────────────
    # OCR often introduces spaces/noise inside GSTINs, so we:
    # 1) collapse all whitespace around alphanumeric runs on each line
    # 2) search collapsed text with a relaxed pattern then validate
    GSTIN_STRICT = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9][Z][A-Z0-9]\b')
    GSTIN_LOOSE  = re.compile(r'\b(\d{2})\s*([A-Za-z]{5})\s*(\d{4})\s*([A-Za-z])\s*([A-Za-z0-9])\s*([Zz])\s*([A-Za-z0-9])\b')

    def extract_gstins_from_text(txt):
        found = []
        # pass 1: strict on original
        found += GSTIN_STRICT.findall(txt.upper())
        # pass 2: loose (OCR spaces) — reassemble and validate
        for m in GSTIN_LOOSE.finditer(txt):
            candidate = "".join(m.groups()).upper()
            if GSTIN_STRICT.match(candidate) and candidate not in found:
                found.append(candidate)
        # pass 3: strip known label prefixes then retry
        cleaned = re.sub(r'(?i)(gstin|gst\s*no\.?|gstin\s*no\.?)\s*[:\-]?\s*', '', txt)
        found += [g for g in GSTIN_STRICT.findall(cleaned.upper()) if g not in found]
        return list(dict.fromkeys(found))  # deduplicate preserving order

    all_g = extract_gstins_from_text(full)

    bi=next((i for i,l in enumerate(lines) if re.search(r'bill\s*to',l,re.IGNORECASE)),None)
    my_g,my_n,MY_A=get_my_identity()

    def has_me(ll): b=" ".join(ll).lower(); return my_g.lower() in b or any(a in b for a in MY_A)
    if bi is not None: sl=lines[:bi]; bl=lines[bi+1:bi+10]
    else: mid=len(lines)//2; sl=lines[:mid]; bl=lines[mid:]
    iam_s=has_me(sl); iam_b=has_me(bl)

    if iam_s and not iam_b: dt="Sales Invoice"
    elif iam_b and not iam_s: dt="Purchase Invoice"
    elif re.search(r'sales\s*invoice',full,re.IGNORECASE): dt="Sales Invoice"
    elif re.search(r'purchase\s*invoice',full,re.IGNORECASE): dt="Purchase Invoice"
    elif re.search(r'credit\s*note',full,re.IGNORECASE): dt="Credit Note"
    elif re.search(r'debit\s*note',full,re.IGNORECASE): dt="Debit Note"
    else: top=" ".join(lines[:len(lines)//2]).upper(); dt="Sales Invoice" if my_g in top else "Purchase Invoice"

    mc=get_setting("my_city","").lower(); ms=get_setting("my_state","").lower()
    sp=[r'\d{2}[A-Za-z]{5}\d{4}',r'phone|email|gstin|gst\s*no|billing|authorised|mobile|fax',
        r'@',r'^[\d\s\-\+]+$',r'^\d+$',
        r'tax invoice|purchase invoice|sales invoice|invoice no|bill to|ship to|due date',
        r'^(to|from|dear|the|a|an)$']
    if mc: sp.append(re.escape(mc))
    if ms: sp.append(re.escape(ms))
    for a in MY_A:
        if len(a)>3: sp.append(re.escape(a))

    def fc(ll):
        for ln in ll:
            lc=re.sub(r'[|/*]','',ln).strip()
            if len(lc)<4 or my_g in lc.upper(): continue
            if any(a in lc.lower() for a in MY_A): continue
            if any(re.search(p,lc,re.IGNORECASE) for p in sp): continue
            if any(c.isalpha() for c in lc): return lc
        return "Unknown"

    other=fc(bl if dt=="Sales Invoice" else sl)
    vendor=other if other!="Unknown" else fc(lines)

    # Pick the first GSTIN that isn't ours
    gstin=""
    for g in all_g:
        if g != my_g:
            gstin=g; break
    # If still empty and there are GSTINs, take first one regardless
    if not gstin and all_g:
        gstin=all_g[0]

    dm=re.search(r'(?:invoice\s*date|date)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',full,re.IGNORECASE)
    if not dm: dm=re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})',full)
    ds=dm.group(1).replace("/","-") if dm else date.today().strftime("%d-%m-%Y")

    total=fa([r'(?:total\s*amount\s*payable|grand\s*total|total\s*amount)[:\sRs.\u20b9]*([0-9,]+\.?\d*)',
              r'total\s*payable[:\sRs.\u20b9]*([0-9,]+\.?\d*)',
              r'(?:amount\s*due|net\s*payable)[:\sRs.\u20b9]*([0-9,]+\.?\d*)'])
    if total==0.: total=max([float(x) for x in re.findall(r'\b\d{1,7}\.\d{2}\b',full)],default=0.)

    sub=fa([r'(?:taxable\s*value|subtotal|taxable\s*amount)[:\sRs.\u20b9]*([0-9,]+\.?\d*)'])

    hc=bool(re.search(r'\bCGST\b',full,re.IGNORECASE))
    hs=bool(re.search(r'\bSGST\b',full,re.IGNORECASE))
    hi=bool(re.search(r'\bIGST\b',full,re.IGNORECASE))

    cgst=fa([r'CGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9,]{2,}\.?\d*)',
             r'CGST\s*[:\-]?\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9,]{2,}\.?\d*)']) if hc else 0.
    sgst=fa([r'SGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9,]{2,}\.?\d*)',
             r'SGST\s*[:\-]?\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9,]{2,}\.?\d*)']) if hs else 0.
    igst=fa([r'IGST\s*@\s*\d+\.?\d*\s*%\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9,]{2,}\.?\d*)',
             r'IGST\s*[:\-]?\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9,]{2,}\.?\d*)']) if hi else 0.

    tax=cgst+sgst+igst
    sub=round(total-tax,2) if tax>0 else round(total,2)
    if cgst==0. and sgst==0. and igst==0. and total>0 and sub>0: tax=round(total-sub,2)
    if tax>0:
        if not hi and (hc or hs): cgst=sgst=round(tax/2,2)
        elif hi and not hc and not hs: igst=tax

    found=sum([bool(vendor and vendor!="Unknown"),bool(gstin),total>0,sub>0,cgst>0 or sgst>0 or igst>0,iam_s or iam_b])
    return {"vendor":vendor,"date":ds,"gstin":gstin,"doc_type":dt,
            "subtotal":sub,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total,
            "confidence":min(50+found*8,97),
            "detected_by":"GSTIN Match" if (iam_s or iam_b) else "Keyword",
            "has_cgst":hc,"has_sgst":hs,"has_igst":hi}

# ─────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────
def show_login():
    lang = st.session_state.get("lang", "English")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.4rem;
            background:linear-gradient(135deg,#00E5A0,#7B61FF);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">FinFlow</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#5A6075;
            letter-spacing:0.15em;margin-top:0.3rem;">{T[lang]['app_subtitle']}</div>
    </div>""", unsafe_allow_html=True)

    # Language selector at login
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        lang_choice = st.selectbox("", ["English", "ಕನ್ನಡ"],
                               index=0 if lang == "English" else 1, key="login_lang")
        if lang_choice != lang:
            st.session_state.lang = lang_choice
            st.rerun()

    
        tab_in, tab_reg = st.tabs([T[lang]["sign_in"], T[lang]["create_account"]])

        with tab_in:
            with st.form("login_form"):
                username = st.text_input(T[lang]["username"], placeholder=T[lang]["enter_username"])
                password = st.text_input(T[lang]["password"], type="password", placeholder=T[lang]["enter_password"])
                sub = st.form_submit_button(T[lang]["sign_in_btn"], use_container_width=True)
                if sub:
                    db = get_user_db(); u = username.strip().lower()
                    if u in db and db[u]["password"] == password:
                        st.session_state.logged_in = True
                        st.session_state.username  = u
                        st.session_state.user_name = db[u]["name"]
                        st.session_state.user_color= db[u]["color"]
                        st.session_state.page      = "Dashboard"
                        st.success(f"{T[lang]['welcome_back']}, {db[u]['name']}!")
                        st.rerun()
                    else:
                        st.error(T[lang]["invalid_creds"])
            

        with tab_reg:
            with st.form("reg_form"):
                nu = st.text_input(T[lang]["choose_username"], placeholder=T[lang]["eg_username"])
                fn = st.text_input(T[lang]["full_name"], placeholder=T[lang]["eg_name"])
                np1 = st.text_input(T[lang]["new_password"], type="password")
                np2 = st.text_input(T[lang]["confirm_password"], type="password")
                rs = st.form_submit_button(T[lang]["create_account_btn"], use_container_width=True)
                if rs:
                    db = get_user_db(); un = nu.strip().lower()
                    ok, _ = validate_password(np1)
                    if not un or not fn.strip(): st.error(T[lang]["username_required"])
                    elif un in db: st.error(T[lang]["username_exists"])
                    elif not ok: st.error(T[lang]["pwd_req_fail"])
                    elif np1 != np2: st.error(T[lang]["pwd_no_match"])
                    else:
                        db[un] = {"password": np1, "name": fn.strip(), "color": "#00E5A0", "data": EMPTY_DATA()}
                        st.success(f"{T[lang]['account_created']} **{un}**")
            st.markdown(f"""
            <div style="margin-top:0.8rem;background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);
                border-radius:10px;padding:0.8rem 1rem;font-family:'DM Mono',monospace;font-size:0.75rem;">
                <div style="color:#7B61FF;font-weight:600;margin-bottom:0.4rem;">{T[lang]['pwd_rules_title']}</div>
                <div style="color:#5A6075;">{T[lang]['pwd_rule_1']}</div>
                <div style="color:#5A6075;">{T[lang]['pwd_rule_2']}</div>
                <div style="color:#5A6075;">{T[lang]['pwd_rule_3']}</div>
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
            <div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,{color},{color}88);
                display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.95rem;color:#0A0C10;">
                {st.session_state.user_name[0].upper()}</div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.88rem;color:#E8ECF4;">
                    {st.session_state.user_name}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:{color};
                    text-transform:uppercase;letter-spacing:0.1em;">{t("role_lbl")}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    if st.button(t("logout"), key="logout_btn", use_container_width=True):
        for k in ["logged_in","username","user_name","user_color","extracted"]:
            st.session_state[k] = False if k=="logged_in" else ""
        st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style="padding:0.5rem 0 1.2rem;">
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.9rem;
            background:linear-gradient(135deg,#00E5A0,#7B61FF);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">FinFlow</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#5A6075;
            letter-spacing:0.15em;text-transform:uppercase;">{t("app_tagline")}</div>
    </div>""", unsafe_allow_html=True)

    lang_sel = st.selectbox(t("language"), ["English", "ಕನ್ನಡ"],
                            index=0 if st.session_state.lang=="English" else 1, key="lang_select")
    if lang_sel != st.session_state.lang:
        st.session_state.lang = lang_sel; st.rerun()

    st.markdown("---")

    PAGES = [("📊","nav_dashboard","Dashboard"),("📤","nav_upload","Upload & Extract"),
             ("✏️","nav_manual","Manual Entry"),("📋","nav_purchase","Purchase Register"),
             ("💰","nav_sales","Sales Register"),("🔄","nav_recon","Reconciliation"),
             ("📄","nav_gstr1","GSTR-1 Report"),("📑","nav_gstr3b","GSTR-3B Report"),
             ("🔍","nav_gstr2","GSTR-2A / 2B"),("📖","nav_guide","User Guide"),
             ("⚙️","nav_settings","Settings")]

    for icon, key, internal in PAGES:
        label = t(key)
        if st.button(f"{icon}  {label}", key=f"nav_{internal}", use_container_width=True):
            st.session_state.page = internal; st.rerun()

    st.markdown("---")
    tx = get_tax_summary()
    net_color = "#FF6B6B" if tx["net_tax"]>0 else "#00E5A0"
    st.markdown(f"""
    <div style="padding:0.75rem;background:var(--surface2);border-radius:10px;border:1px solid var(--border);font-size:0.82rem;">
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#5A6075;
            text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;">{t("quick_stats")}</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="color:#5A6075;">{t("purchases_lbl")}</span>
            <span style="color:#FFB547;font-family:'DM Mono',monospace;font-weight:600;">{tx['p_count']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="color:#5A6075;">{t("sales_lbl")}</span>
            <span style="color:#00E5A0;font-family:'DM Mono',monospace;font-weight:600;">{tx['s_count']}</span>
        </div>
        <div style="display:flex;justify-content:space-between;">
            <span style="color:#5A6075;">{t("net_tax_due")}</span>
            <span style="color:{net_color};font-family:'DM Mono',monospace;font-weight:700;">₹{tx['net_tax']:,.0f}</span>
        </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────
page = st.session_state.page

# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════
if page == "Dashboard":
    st.markdown(t("dashboard_title")); st.caption(t("dashboard_caption"))
    tx = get_tax_summary()
    profit = tx["s_total"] - tx["p_total"]
    net_label = t("tax_payable") if tx["net_tax"]>0 else t("tax_refund")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric(t("total_purchases"), f"₹{tx['p_total']:,.0f}", f"{tx['p_count']} {t('invoices_count')}")
    with c2: st.metric(t("total_sales"),     f"₹{tx['s_total']:,.0f}", f"{tx['s_count']} {t('invoices_count')}")
    with c3: st.metric(t("gross_margin"),    f"₹{profit:,.0f}", t("sales_minus_purchases"))
    with c4: st.metric(f"🧾 {net_label}",    f"₹{abs(tx['net_tax']):,.0f}", t("output_minus_input"))
    st.markdown("---")
    l,r = st.columns(2)
    with l:
        st.markdown(t("gst_breakdown"))
        st.dataframe(pd.DataFrame({
            t("tax_col"): ["CGST","SGST","IGST","TOTAL"],
            t("purchase_input"): [fmt_inr(tx["p_cgst"]),fmt_inr(tx["p_sgst"]),fmt_inr(tx["p_igst"]),fmt_inr(tx["p_cgst"]+tx["p_sgst"]+tx["p_igst"])],
            t("sales_output"):   [fmt_inr(tx["s_cgst"]),fmt_inr(tx["s_sgst"]),fmt_inr(tx["s_igst"]),fmt_inr(tx["s_cgst"]+tx["s_sgst"]+tx["s_igst"])],
            t("net_due"):        [fmt_inr(tx["net_cgst"]),fmt_inr(tx["net_sgst"]),fmt_inr(tx["net_igst"]),fmt_inr(tx["net_tax"])],
        }), use_container_width=True, hide_index=True)
        if tx["net_tax"]>0: st.warning(f"⚠️ ₹{tx['net_tax']:,.2f} {t('payable_warning')}")
        else: st.success(f"✅ {t('carry_forward')} ₹{abs(tx['net_tax']):,.2f}")
    with r:
        st.markdown(t("sales_vs_purchases"))
        st.bar_chart(pd.DataFrame({"Amount":[tx["p_total"],tx["s_total"]]},index=[t("purchase_type"),t("sales_type")]),color="#00E5A0")
        st.info(t("chart_info"))
    p=get_register("purchase_register"); s=get_register("sales_register")
    if not p.empty or not s.empty:
        st.markdown("---"); st.markdown(t("recent_activity"))
        comb=pd.concat([p.assign(**{t("type_col"):t("purchase_type")}) if not p.empty else pd.DataFrame(),
                        s.assign(**{t("type_col"):t("sales_type")}) if not s.empty else pd.DataFrame()
                        ]).sort_values("Date",ascending=False).head(8)
        disp=comb[["ID","Date","Vendor",t("type_col"),"Total","Status"]].copy()
        disp["Total"]=disp["Total"].apply(lambda x:f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)
    st.markdown("---"); st.markdown(t("gstr_status"))
    has_data = not s.empty or not p.empty
    g1,g2,g3,g4=st.columns(4)
    status = t("ready_to_file") if has_data else t("no_data")
    for col,code,desc,due in [(g1,"GSTR-1","Outward","11th"),(g2,"GSTR-3B","Summary","20th"),
                               (g3,"GSTR-2A","Auto","Auto"),(g4,"GSTR-2B","Locked","14th")]:
        col.metric(f"{code}",status,due)

# ══════════════════════════════════════════════
# UPLOAD & EXTRACT
# ══════════════════════════════════════════════
elif page == "Upload & Extract":
    st.markdown(t("upload_title")); st.caption(t("upload_caption"))
    c1,c2=st.columns([1.1,0.9])
    with c1:
        uf=st.file_uploader(t("drop_invoice"),type=["pdf","png","jpg","jpeg"])
        if uf:
            st.success(f"✓ {uf.name} ({uf.size//1024} KB)")
            ext=uf.name.lower().rsplit(".",1)[-1]
            if ext in ("png","jpg","jpeg"): st.image(uf,width=380); uf.seek(0)
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button(t("extract_btn"),use_container_width=True):
                with st.spinner(t("reading_invoice")):
                    try:
                        uf.seek(0); ext_d=run_ocr(uf)
                        if ext_d: st.session_state.extracted=ext_d; st.success(t("extraction_complete"))
                    except Exception as e: st.error(f"{t('extraction_failed')} {e}")
        if st.session_state.extracted:
            ed=st.session_state.extracted; conf=ed.get("confidence",80); dtype=ed.get("doc_type","Purchase Invoice")
            hc=ed.get("has_cgst",True); hs_=ed.get("has_sgst",True); hi=ed.get("has_igst",False)
            st.markdown("---"); st.markdown(t("extracted_fields"))
            bc="#00E5A0" if "Sales" in dtype else "#FFB547"
            dest=t("to_sales_reg") if "Sales" in dtype else t("to_purchase_reg")
            disp_dt=t("sales_invoice") if "Sales" in dtype else t("purchase_invoice")
            st.markdown(f"""<div style="display:inline-block;padding:0.3rem 0.9rem;border-radius:100px;
                background:rgba(0,229,160,0.1);border:1px solid {bc};color:{bc};
                font-family:'DM Mono',monospace;font-size:0.78rem;font-weight:600;margin-bottom:0.75rem;">
                {'📤' if 'Sales' in dtype else '📥'} {disp_dt} → {dest}</div>
                <div style="font-size:0.75rem;color:#5A6075;margin-bottom:0.75rem;">{t("detection")} {ed.get("detected_by","")}</div>""",
                unsafe_allow_html=True)
            bc2="#00E5A0" if conf>=80 else "#FFB547" if conf>=60 else "#FF6B6B"
            st.markdown(f"""<div style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#5A6075;margin-bottom:0.3rem;">
                    <span>{t("ocr_confidence")}</span><span style="color:{bc2};font-weight:600;">{conf}%</span></div>
                <div style="height:5px;background:#1E2330;border-radius:100px;">
                    <div style="height:100%;width:{conf}%;background:{bc2};border-radius:100px;"></div></div></div>""",
                unsafe_allow_html=True)
            if not ed.get("gstin"):
                has_tax=(ed.get("cgst",0)>0 or ed.get("sgst",0)>0 or ed.get("igst",0)>0)
                if has_tax: st.error(t("illegal_tax"))
                else: st.error(t("no_gstin_warn"))
            fields=[(t("vendor_party"),ed.get("vendor","")),
                    (t("invoice_type"),disp_dt),(t("date_col"),ed.get("date","")),
                    (t("gstin_col"),ed.get("gstin","") or t("no_gstin")),
                    (t("subtotal_col"),fmt_inr(ed.get("subtotal",0)))]
            if hc: fields.append((t("cgst_col"),fmt_inr(ed.get("cgst",0))))
            if hs_: fields.append((t("sgst_col"),fmt_inr(ed.get("sgst",0))))
            if hi: fields.append((t("igst_col"),fmt_inr(ed.get("igst",0))))
            fields.append((t("total_amount"),fmt_inr(ed.get("total",0))))
            st.table(pd.DataFrame(fields,columns=[t("field_col"),t("value_col")]))
    with c2:
        st.markdown(t("review_confirm"))
        if st.session_state.extracted:
            ed=st.session_state.extracted
            hc=ed.get("has_cgst",True); hs_=ed.get("has_sgst",True); hi=ed.get("has_igst",False)
            with st.form("confirm_form"):
                vendor=st.text_input(t("vendor_name"),value=ed.get("vendor",""))
                EN_TYPES=["Purchase Invoice","Sales Invoice","Credit Note","Debit Note","Expense Receipt"]
                KN_TYPES=[t("purchase_invoice"),t("sales_invoice"),t("credit_note"),t("debit_note"),t("expense_receipt")]
                doc_type=st.selectbox(t("invoice_type"),KN_TYPES)
                txn_date=st.text_input(t("txn_date"),value=ed.get("date",""))
                gstin=st.text_input(t("gstin_col"),value=ed.get("gstin",""))
                sub=st.number_input(t("subtotal_inr"),value=float(ed.get("subtotal",0)),min_value=0.,step=0.01)
                cgst=sgst=igst=0.
                if hc and not hi: cgst=st.number_input(t("cgst_col")+" (₹)",value=float(ed.get("cgst",0)),min_value=0.,step=0.01)
                if hs_ and not hi: sgst=st.number_input(t("sgst_col")+" (₹)",value=float(ed.get("sgst",0)),min_value=0.,step=0.01)
                if hi: igst=st.number_input(t("igst_col")+" (₹)",value=float(ed.get("igst",0)),min_value=0.,step=0.01)
                if not hc and not hs_ and not hi:
                    cgst=st.number_input(t("cgst_col")+" (₹)",value=0.,min_value=0.,step=0.01)
                    sgst=st.number_input(t("sgst_col")+" (₹)",value=0.,min_value=0.,step=0.01)
                    igst=st.number_input(t("igst_col")+" (₹)",value=0.,min_value=0.,step=0.01)
                total_c=sub+cgst+sgst+igst
                st.metric(t("calculated_total"),fmt_inr(total_c))
                if st.form_submit_button(t("confirm_btn"),use_container_width=True):
                    # map displayed type back to English for routing
                    dt_en=EN_TYPES[KN_TYPES.index(doc_type)] if doc_type in KN_TYPES else doc_type
                    data={"vendor":vendor,"date":txn_date,"gstin":gstin,
                          "subtotal":sub,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total_c}
                    txn_id,reg=add_to_register(data,dt_en)
                    st.session_state.extracted=None
                    rn=t("to_sales_reg") if "sales" in reg else t("to_purchase_reg")
                    st.success(f"✓ {txn_id} {t('added_to')} **{rn}**!")
        else: st.info(t("upload_first"))

# ══════════════════════════════════════════════
# MANUAL ENTRY
# ══════════════════════════════════════════════
elif page == "Manual Entry":
    st.markdown(t("manual_title"))
    c1,c2=st.columns(2)
    with c1:
        EN_TYPES=["Purchase Invoice","Sales Invoice","Expense Receipt","Credit Note","Debit Note"]
        KN_TYPES=[t("purchase_invoice"),t("sales_invoice"),t("expense_receipt"),t("credit_note"),t("debit_note")]
        with st.form("manual_form"):
            doc_type=st.selectbox(t("invoice_type"),KN_TYPES)
            vendor=st.text_input(t("vendor_name"))
            txn_date=st.date_input(t("txn_date"),value=date.today())
            gstin=st.text_input(t("gstin_col")+" (optional)")
            cc1,cc2=st.columns(2)
            with cc1:
                sub=st.number_input(t("subtotal_inr"),min_value=0.,value=1000.,step=1.)
                cp=st.number_input(t("cgst_pct"),min_value=0.,max_value=28.,value=0.,step=0.5)
            with cc2:
                sp=st.number_input(t("sgst_pct"),min_value=0.,max_value=28.,value=0.,step=0.5)
                ip=st.number_input(t("igst_pct"),min_value=0.,max_value=28.,value=0.,step=0.5)
            cgst=round(sub*cp/100,2); sgst=round(sub*sp/100,2); igst=round(sub*ip/100,2)
            total=sub+cgst+sgst+igst
            parts=[]
            if cgst>0: parts.append(f"**{t('cgst_col')}:** {fmt_inr(cgst)}")
            if sgst>0: parts.append(f"**{t('sgst_col')}:** {fmt_inr(sgst)}")
            if igst>0: parts.append(f"**{t('igst_col')}:** {fmt_inr(igst)}")
            parts.append(f"**{t('total_col')}:** {fmt_inr(total)}")
            st.markdown("  |  ".join(parts))
            if st.form_submit_button(t("add_entry_btn"),use_container_width=True):
                if not vendor: st.error(t("vendor_required"))
                else:
                    dt_en=EN_TYPES[KN_TYPES.index(doc_type)] if doc_type in KN_TYPES else doc_type
                    data={"vendor":vendor,"date":txn_date.strftime("%d-%m-%Y"),"gstin":gstin,
                          "subtotal":sub,"cgst":cgst,"sgst":sgst,"igst":igst,"total":total}
                    txn_id,reg=add_to_register(data,dt_en)
                    rn=t("to_sales_reg") if "sales" in reg else t("to_purchase_reg")
                    st.success(f"✓ {txn_id} {t('added_to')} **{rn}**!")
    with c2:
        st.markdown(t("recent_entries"))
        p=get_register("purchase_register"); s=get_register("sales_register")
        if not p.empty or not s.empty:
            comb=pd.concat([p.assign(Type=f"📥 {t('purchase_type')}") if not p.empty else pd.DataFrame(),
                            s.assign(Type=f"📤 {t('sales_type')}") if not s.empty else pd.DataFrame()
                            ]).tail(8)[["ID","Vendor","Type","Total"]].copy()
            comb["Total"]=comb["Total"].apply(lambda x:f"₹{float(x):,.2f}")
            st.dataframe(comb,use_container_width=True,hide_index=True)
        else: st.info(t("no_entries"))

# ══════════════════════════════════════════════
# PURCHASE REGISTER
# ══════════════════════════════════════════════
elif page == "Purchase Register":
    st.markdown(t("purchase_reg_title")); st.caption(t("purchase_reg_caption"))
    df=get_register("purchase_register")
    if df.empty: st.info(t("no_purchase"))
    else:
        m1,m2,m3,m4=st.columns(4)
        with m1: st.metric(t("total_purchases_m"),f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric(t("input_cgst"),f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric(t("input_sgst"),f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric(t("total_entries"),len(df))
        st.markdown("---")
        search=st.text_input(t("search_vendor"))
        if search: df=df[df["Vendor"].str.contains(search,case=False,na=False)]
        disp=df.copy()
        for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c]=disp[c].apply(lambda x:f"₹{float(x):,.2f}")
        st.dataframe(disp,use_container_width=True,hide_index=True,height=400)
        st.download_button(t("export_csv"),data=df.to_csv(index=False).encode(),
            file_name=f"purchase_register_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")

# ══════════════════════════════════════════════
# SALES REGISTER
# ══════════════════════════════════════════════
elif page == "Sales Register":
    st.markdown(t("sales_reg_title")); st.caption(t("sales_reg_caption"))
    df=get_register("sales_register")
    if df.empty: st.info(t("no_sales"))
    else:
        m1,m2,m3,m4=st.columns(4)
        with m1: st.metric(t("total_sales_m"),f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric(t("output_cgst"),f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric(t("output_sgst"),f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric(t("total_entries"),len(df))
        st.markdown("---")
        search=st.text_input(t("search_buyer"))
        if search: df=df[df["Vendor"].str.contains(search,case=False,na=False)]
        disp=df.copy()
        for c in ["Subtotal","CGST","SGST","IGST","Total"]: disp[c]=disp[c].apply(lambda x:f"₹{float(x):,.2f}")
        st.dataframe(disp,use_container_width=True,hide_index=True,height=400)
        st.download_button(t("export_csv"),data=df.to_csv(index=False).encode(),
            file_name=f"sales_register_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")

# ══════════════════════════════════════════════
# RECONCILIATION
# ══════════════════════════════════════════════
elif page == "Reconciliation":
    st.markdown(t("recon_title"))
    tx=get_tax_summary(); p=get_register("purchase_register"); s=get_register("sales_register")
    if p.empty and s.empty: st.info(t("no_recon_data"))
    else:
        st.markdown(t("full_tax_stmt"))
        st.dataframe(pd.DataFrame({
            t("tax_head"):          ["CGST","SGST","IGST","TOTAL"],
            t("input_tax_purchase"):[fmt_inr(tx["p_cgst"]),fmt_inr(tx["p_sgst"]),fmt_inr(tx["p_igst"]),fmt_inr(tx["p_cgst"]+tx["p_sgst"]+tx["p_igst"])],
            t("output_tax_sales"):  [fmt_inr(tx["s_cgst"]),fmt_inr(tx["s_sgst"]),fmt_inr(tx["s_igst"]),fmt_inr(tx["s_cgst"]+tx["s_sgst"]+tx["s_igst"])],
            t("net_payable"):       [fmt_inr(tx["net_cgst"]),fmt_inr(tx["net_sgst"]),fmt_inr(tx["net_igst"]),fmt_inr(tx["net_tax"])],
        }),use_container_width=True,hide_index=True)
        if tx["net_tax"]>0: st.error(f"⚠️ {t('net_gst_payable')}: ₹{tx['net_tax']:,.2f}  —  {t('pay_by_20th')}")
        else: st.success(f"✅ {t('itc_exceeds')} ₹{abs(tx['net_tax']):,.2f}  —  {t('carry_fwd')}")
        st.markdown("---"); st.markdown(t("gstin_validation"))
        all_df=pd.concat([p.assign(**{t("register_col"):t("purchase_type")}) if not p.empty else pd.DataFrame(),
                          s.assign(**{t("register_col"):t("sales_type")}) if not s.empty else pd.DataFrame()])
        g=all_df[["ID","Vendor","GSTIN",t("register_col")]].copy()
        def chk(x):
            if not x or str(x).strip()=="" or str(x)=="nan": return t("no_gstin_col")
            elif re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]$',str(x)): return t("valid_gstin")
            else: return t("invalid_gstin")
        g[t("valid_col")]=g["GSTIN"].apply(chk)
        st.dataframe(g,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════
# GSTR-1
# ══════════════════════════════════════════════
elif page == "GSTR-1 Report":
    st.markdown(t("gstr1_title")); st.caption(t("gstr1_caption")); st.info(t("gstr1_info"))
    sdf=get_register("sales_register")
    if sdf.empty: st.warning(t("no_sales_gstr1"))
    else:
        sm,b2b,b2c=build_gstr1(sdf)
        k1,k2,k3,k4,k5=st.columns(5)
        k1.metric(t("taxable_turnover"),fmt_inr(sm["total_taxable"]))
        k2.metric("CGST",fmt_inr(sm["total_cgst"])); k3.metric("SGST",fmt_inr(sm["total_sgst"]))
        k4.metric("IGST",fmt_inr(sm["total_igst"])); k5.metric(t("grand_total"),fmt_inr(sm["grand_total"]))
        st.markdown("---")
        tb1,tb2,tb3=st.tabs([t("b2b_tab"),t("b2c_tab"),t("full_table_tab")])
        with tb1:
            st.caption(t("b2b_caption"))
            if b2b.empty: st.info(t("no_b2b"))
            else:
                d=b2b[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: d[c]=d[c].apply(fmt_inr)
                st.dataframe(d,use_container_width=True,hide_index=True)
        with tb2:
            st.caption(t("b2c_caption"))
            if b2c.empty: st.info(t("no_b2c"))
            else:
                d=b2c[["ID","Date","Vendor","Subtotal","CGST","SGST","IGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","IGST","Total"]: d[c]=d[c].apply(fmt_inr)
                st.dataframe(d,use_container_width=True,hide_index=True)
        with tb3:
            d=sdf[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","IGST","Total","Status"]].copy()
            for c in ["Subtotal","CGST","SGST","IGST","Total"]: d[c]=d[c].apply(fmt_inr)
            st.dataframe(d,use_container_width=True,hide_index=True)
        st.download_button(t("download_gstr1"),data=sdf.to_csv(index=False).encode(),
            file_name=f"GSTR1_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv",use_container_width=True)

# ══════════════════════════════════════════════
# GSTR-3B
# ══════════════════════════════════════════════
elif page == "GSTR-3B Report":
    st.markdown(t("gstr3b_title")); st.caption(t("gstr3b_caption")); st.warning(t("gstr3b_warn"))
    sdf=get_register("sales_register"); pdf=get_register("purchase_register")
    if sdf.empty and pdf.empty: st.info(t("no_data_gstr3b"))
    else:
        d=build_gstr3b(sdf,pdf)
        tb1,tb2,tb3=st.tabs([t("output_tax_tab"),t("itc_tab"),t("net_tax_tab")])
        with tb1:
            st.markdown(t("output_tax_heading"))
            st.dataframe(pd.DataFrame([
                {t("section_col"):"3.1(a)",t("nature_col"):t("outward_taxable"),t("taxable_col"):fmt_inr(d["out_taxable"]),"CGST":fmt_inr(d["out_cgst"]),"SGST":fmt_inr(d["out_sgst"]),"IGST":fmt_inr(d["out_igst"])},
                {t("section_col"):"3.1(b)",t("nature_col"):t("zero_rated"),t("taxable_col"):"₹0.00","CGST":"₹0.00","SGST":"₹0.00","IGST":"₹0.00"},
                {t("section_col"):"3.1(c)",t("nature_col"):t("nil_rated"),t("taxable_col"):"₹0.00","CGST":"₹0.00","SGST":"₹0.00","IGST":"₹0.00"},
            ]),use_container_width=True,hide_index=True)
        with tb2:
            st.markdown(t("itc_heading"))
            st.dataframe(pd.DataFrame([
                {t("section_col"):"4(A)(1)",t("nature_col"):t("itc_imports_goods"),t("taxable_col"):"₹0.00","CGST":"₹0.00","SGST":"₹0.00","IGST":"₹0.00"},
                {t("section_col"):"4(A)(2)",t("nature_col"):t("itc_imports_svc"),t("taxable_col"):"₹0.00","CGST":"₹0.00","SGST":"₹0.00","IGST":"₹0.00"},
                {t("section_col"):"4(A)(5)",t("nature_col"):t("itc_domestic"),t("taxable_col"):fmt_inr(d["itc_taxable"]),"CGST":fmt_inr(d["itc_cgst"]),"SGST":fmt_inr(d["itc_sgst"]),"IGST":fmt_inr(d["itc_igst"])},
            ]),use_container_width=True,hide_index=True)
        with tb3:
            st.markdown(t("net_tax_heading"))
            st.dataframe(pd.DataFrame([
                {t("section_col"):"",t("nature_col"):t("output_liability"),"CGST":fmt_inr(d["out_cgst"]),"SGST":fmt_inr(d["out_sgst"]),"IGST":fmt_inr(d["out_igst"]),t("total_col"):fmt_inr(d["out_cgst"]+d["out_sgst"]+d["out_igst"])},
                {t("section_col"):"",t("nature_col"):t("less_itc"),"CGST":f"(−) {fmt_inr(d['itc_cgst'])}","SGST":f"(−) {fmt_inr(d['itc_sgst'])}","IGST":f"(−) {fmt_inr(d['itc_igst'])}",t("total_col"):f"(−) {fmt_inr(d['itc_cgst']+d['itc_sgst']+d['itc_igst'])}"},
                {t("section_col"):"",t("nature_col"):t("net_tax_payable"),"CGST":fmt_inr(d["net_cgst"]),"SGST":fmt_inr(d["net_sgst"]),"IGST":fmt_inr(d["net_igst"]),t("total_col"):fmt_inr(d["net_total"])},
            ]),use_container_width=True,hide_index=True)
            if d["net_total"]>0: st.error(t("owe_gst").format(f"{d['net_total']:,.2f}"))
            else: st.success(t("excess_itc").format(f"{abs(d['net_total']):,.2f}"))
        st.download_button(t("download_gstr3b"),
            data=pd.DataFrame([{"Section":"3.1(a)","Description":"Outward","Taxable":d["out_taxable"],"CGST":d["out_cgst"],"SGST":d["out_sgst"],"IGST":d["out_igst"]},
                               {"Section":"4(A)(5)","Description":"ITC","Taxable":d["itc_taxable"],"CGST":d["itc_cgst"],"SGST":d["itc_sgst"],"IGST":d["itc_igst"]},
                               {"Section":"6.1","Description":"Net","Taxable":d["out_taxable"]-d["itc_taxable"],"CGST":d["net_cgst"],"SGST":d["net_sgst"],"IGST":d["net_igst"]}
                               ]).to_csv(index=False).encode(),
            file_name=f"GSTR3B_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv",use_container_width=True)

# ══════════════════════════════════════════════
# GSTR-2A / 2B
# ══════════════════════════════════════════════
elif page == "GSTR-2A / 2B":
    st.markdown(t("gstr2_title")); st.caption(t("gstr2_caption"))
    ca,cb=st.columns(2); ca.success(t("gstr2a_dynamic")); cb.info(t("gstr2b_static"))
    pdf=get_register("purchase_register"); g2a=get_gstr2a()
    tb1,tb2,tb3,tb4=st.tabs([t("gstr2a_tab"),t("gstr2b_tab"),t("recon_tab"),t("add_2a_tab")])
    with tb4:
        st.caption(t("add_2a_caption"))
        with st.form("add_2a_form"):
            cc1,cc2=st.columns(2)
            with cc1:
                sg=st.text_input(t("supplier_gstin")); sv=st.text_input(t("supplier_name"))
                si=st.text_input(t("invoice_no")); sd=st.date_input(t("invoice_date"),value=date.today())
            with cc2:
                stx=st.number_input(t("taxable_value"),min_value=0.,value=1000.,step=1.)
                sc_=st.number_input(t("cgst_col")+" (₹)",min_value=0.,value=0.,step=0.01)
                ss_=st.number_input(t("sgst_col")+" (₹)",min_value=0.,value=0.,step=0.01)
                si_=st.number_input(t("igst_col")+" (₹)",min_value=0.,value=0.,step=0.01)
            st_=stx+sc_+ss_+si_
            st.markdown(f"**{t('total_col')}: {fmt_inr(st_)}**")
            if st.form_submit_button(t("add_2a_btn"),use_container_width=True):
                nr={"GSTIN":sg,"Vendor":sv,"InvoiceNo":si,"Date":sd.strftime("%d-%m-%Y"),
                    "Taxable":stx,"CGST":sc_,"SGST":ss_,"IGST":si_,"Total":st_,"Source":"GSTR-2A"}
                upd=pd.concat([g2a,pd.DataFrame([nr])],ignore_index=True)
                set_gstr2a(upd); st.success(t("added_to_2a").format(sv)); st.rerun()
    g2a_fresh=get_gstr2a(); g2a_out,g2b_df,recon_df=build_gstr2a_2b(pdf,g2a_fresh)
    with tb1:
        if g2a_fresh.empty: st.info(t("no_2a_data"))
        else:
            itc_tot=(g2a_fresh["CGST"].astype(float).sum()+g2a_fresh["SGST"].astype(float).sum()+g2a_fresh["IGST"].astype(float).sum())
            k1,k2,k3=st.columns(3)
            k1.metric(t("suppliers_filed"),g2a_fresh["GSTIN"].nunique())
            k2.metric(t("total_invoices"),len(g2a_fresh)); k3.metric(t("itc_available"),fmt_inr(itc_tot))
            d=g2a_fresh.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: d[c]=d[c].apply(fmt_inr)
            st.dataframe(d,use_container_width=True,hide_index=True)
            st.download_button(t("download_2a"),data=g2a_fresh.to_csv(index=False).encode(),
                file_name=f"GSTR2A_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")
    with tb2:
        if g2b_df.empty: st.info(t("no_2b_data"))
        else:
            it=(g2b_df["CGST"].astype(float).sum()+g2b_df["SGST"].astype(float).sum()+g2b_df["IGST"].astype(float).sum())
            st.info(f"{t('gstr2b_locked')} **{fmt_inr(it)}**")
            d=g2b_df.copy()
            for c in ["Taxable","CGST","SGST","IGST","Total"]: d[c]=d[c].apply(fmt_inr)
            st.dataframe(d,use_container_width=True,hide_index=True)
            st.download_button(t("download_2b"),data=g2b_df.to_csv(index=False).encode(),
                file_name=f"GSTR2B_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")
    with tb3:
        st.caption(t("recon_caption"))
        if pdf.empty: st.info(t("no_purchase_recon"))
        elif recon_df.empty: st.info(t("no_2a_recon"))
        else:
            ma=len(recon_df[recon_df["Status"]==t("matched")])
            mm=len(recon_df[recon_df["Status"]==t("mismatch")])
            ni=len(recon_df[recon_df["Status"]==t("not_in_2a")])
            k1,k2,k3,k4=st.columns(4)
            k1.metric(t("total_invoices"),len(recon_df))
            k2.metric(t("matched"),ma,delta=t("itc_claimable"))
            k3.metric(t("mismatch"),mm,delta=t("needscorrection") if mm else None)
            k4.metric(t("not_in_2a"),ni,delta=t("follow_up") if ni else None)
            d=recon_df.copy()
            for c in ["Your CGST","Your IGST","2A CGST","2A IGST"]: d[c]=d[c].apply(fmt_inr)
            st.dataframe(d,use_container_width=True,hide_index=True)
            st.markdown(t("action_guide"))
            st.download_button(t("download_recon"),data=recon_df.to_csv(index=False).encode(),
                file_name=f"GSTR2A_Recon_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv",use_container_width=True)

# ══════════════════════════════════════════════
# USER GUIDE
# ══════════════════════════════════════════════
elif page == "User Guide":
    st.markdown(t("guide_title")); st.caption(t("guide_caption"))
    st.markdown("---"); st.markdown(t("how_works")); st.markdown(t("how_works_flow"))
    st.markdown("---"); st.markdown(t("step_by_step"))
    for title,desc in t("steps"):
        st.markdown(f"**{title}**  \n{desc}"); st.markdown("---")
    st.markdown(t("itc_rules"))
    cy,cn=st.columns(2)
    with cy: st.success(t("itc_yes"))
    with cn: st.error(t("itc_no"))
    st.warning(t("itc_warn"))
    st.markdown("---"); st.markdown(t("faq_title"))
    for q,a in t("faqs"):
        with st.expander(f"❓ {q}"): st.write(a)

# ══════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════
elif page == "Settings":
    st.markdown(t("settings_title")); st.caption(t("settings_caption"))
    tb_b,tb_p=st.tabs([t("biz_tab"),t("pwd_tab")])
    with tb_b:
        st.markdown(t("current_biz"))
        st.table(pd.DataFrame([
            (t("biz_name"),get_setting("my_name","Sai Coffee Traders")),
            (t("my_gstin"),get_setting("my_gstin","29AAAAA1111B1Z1")),
            (t("city_lbl"),get_setting("my_city","Dharwad")),
            (t("state_lbl"),get_setting("my_state","Karnataka")),
        ],columns=[t("field_col"),t("value_col")]))
        st.markdown("---"); st.markdown(t("update_details"))
        with st.form("settings_form"):
            cc1,cc2=st.columns(2)
            with cc1:
                nn=st.text_input(t("biz_name"),value=get_setting("my_name","Sai Coffee Traders"))
                nc=st.text_input(t("city_lbl"),value=get_setting("my_city","Dharwad"))
            with cc2:
                ng=st.text_input(t("my_gstin"),value=get_setting("my_gstin","29AAAAA1111B1Z1"),max_chars=15).strip().upper()
                ns=st.text_input(t("state_lbl"),value=get_setting("my_state","Karnataka"))
            if ng:
                if re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9][Z][A-Z0-9]$',ng): st.success(t("valid_gstin"))
                else: st.warning(t("gstin_warn"))
            if st.form_submit_button(t("save_settings"),use_container_width=True):
                if not nn.strip(): st.error(t("biz_empty"))
                elif not ng.strip(): st.error(t("gstin_empty"))
                else:
                    save_setting_val("my_gstin",ng); save_setting_val("my_name",nn.strip())
                    save_setting_val("my_city",nc.strip()); save_setting_val("my_state",ns.strip())
                    st.success(t("saved_ok").format(nn,ng)); st.rerun()
    with tb_p:
        st.markdown(t("change_pwd"))
        with st.form("change_pwd_form"):
            op=st.text_input(t("current_pwd"),type="password")
            np1=st.text_input(t("new_pwd_lbl"),type="password",help=t("new_pwd_help"))
            np2=st.text_input(t("confirm_new_pwd"),type="password")
            if st.form_submit_button(t("update_pwd_btn"),use_container_width=True):
                db=get_user_db(); u=st.session_state.username
                if db[u]["password"]!=op: st.error(t("wrong_current_pwd"))
                elif np1!=np2: st.error(t("pwd_no_match"))
                else:
                    ok,rules=validate_password(np1)
                    if not ok:
                        failed=[t(rk) for _,passed,rk in rules if not passed]
                        st.error("; ".join(failed))
                    else:
                        db[u]["password"]=np1; st.success(t("pwd_updated"))
        st.markdown(f"""
        <div style="margin-top:0.8rem;background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);
            border-radius:10px;padding:0.8rem 1rem;font-family:'DM Mono',monospace;font-size:0.75rem;">
            <div style="color:#7B61FF;font-weight:600;margin-bottom:0.4rem;">{t('pwd_rules_title')}</div>
            <div style="color:#5A6075;">{t('pwd_rule_1')}</div>
            <div style="color:#5A6075;">{t('pwd_rule_2')}</div>
            <div style="color:#5A6075;">{t('pwd_rule_3')}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---"); st.markdown(t("invoice_detection")); st.markdown(t("detect_table"))
