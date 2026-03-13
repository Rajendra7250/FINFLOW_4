import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
from backend import *

USERS = {
    "admin": {
        "password": "Admin@123",
        "name": "Admin User",
        "role": "Admin",
        "color": "#00E5A0"
    },
    "accountant": {
        "password": "acc123",
        "name": "Ramesh Kumar",
        "role": "Accountant",
        "color": "#7B61FF"
    },
    "viewer": {
        "password": "view123",
        "name": "Priya Sharma",
        "role": "Viewer",
        "color": "#FFB547"
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

# ── TRANSLATIONS ──
TR = {
    # Sidebar
    "Quick Stats": "ತ್ವರಿತ ಅಂಕಿಅಂಶ",
    "Purchases": "ಖರೀದಿಗಳು",
    "Sales": "ಮಾರಾಟ",
    "Net Tax Due": "ನಿವ್ವಳ ತೆರಿಗೆ",
    "Logout": "ಲಾಗ್ ಔಟ್",

    # Dashboard
    "📊 Dashboard": "📊 ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
    "GST Sales & Purchase Register": "GST ಮಾರಾಟ ಮತ್ತು ಖರೀದಿ ನೋಂದಣಿ",
    "Field": "ವಿವರ",
    "Value": "ಮೌಲ್ಯ",
    "Vendor / Party": "ವ್ಯಾಪಾರಿ / ಪಾರ್ಟಿ",
    "Subtotal": "ಉಪ ಮೊತ್ತ",
    "Total": "ಒಟ್ಟು",
    "No GSTIN — Unregistered": "GSTIN ಇಲ್ಲ — ನೋಂದಾಯಿಸಲ್ಪಡದ",
    "Calculated Total": "ಲೆಕ್ಕ ಹಾಕಿದ ಒಟ್ಟು",
    "How net tax is calculated:": "ನಿವ್ವಳ ತೆರಿಗೆ ಹೇಗೆ ಲೆಕ್ಕ ಹಾಕಲಾಗುತ್ತದೆ:",
    "Output Tax (on Sales) − Input Tax Credit (on Purchases) = Net GST Payable": "ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ − ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್ = ನಿವ್ವಳ GST ಪಾವತಿ",

    "Total Purchases": "ಒಟ್ಟು ಖರೀದಿ",
    "Total Sales": "ಒಟ್ಟು ಮಾರಾಟ",
    "Gross Margin": "ಒಟ್ಟು ಲಾಭ",
    "Tax Payable": "ತೆರಿಗೆ ಪಾವತಿಸಬೇಕು",
    "Tax Refund": "ತೆರಿಗೆ ಮರುಪಾವತಿ",
    "invoices": "ಇನ್ವಾಯ್ಸ್‌ಗಳು",
    "Sales minus Purchases": "ಮಾರಾಟ ಮೈನಸ್ ಖರೀದಿ",
    "Output tax − Input tax": "ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ − ಇನ್‌ಪುಟ್ ತೆರಿಗೆ",
    "GST Tax Breakdown": "GST ತೆರಿಗೆ ವಿವರ",
    "Purchase": "ಖರೀದಿ",
    "Net": "ನಿವ್ವಳ",
    "Tax payable to government": "ಸರ್ಕಾರಕ್ಕೆ ತೆರಿಗೆ ಪಾವತಿಸಬೇಕು",
    "Input credit exceeds output tax": "ಇನ್‌ಪುಟ್ ಕ್ರೆಡಿಟ್ ಔಟ್‌ಪುಟ್ ತೆರಿಗೆಗಿಂತ ಹೆಚ್ಚಿದೆ",
    "Sales vs Purchases": "ಮಾರಾಟ vs ಖರೀದಿ",
    "Recent Activity": "ಇತ್ತೀಚಿನ ಚಟುವಟಿಕೆ",
    "GSTR Filing Status": "GSTR ಸಲ್ಲಿಕೆ ಸ್ಥಿತಿ",
    "Outward Supplies": "ಹೊರಮುಖ ಪೂರೈಕೆ",
    "Summary Return": "ಸಾರಾಂಶ ರಿಟರ್ನ್",
    "Auto-Populated": "ಸ್ವಯಂ-ತುಂಬಿದ",
    "Static ITC": "ಸ್ಥಿರ ITC",
    "Sales register · File by 11th": "ಮಾರಾಟ ನೋಂದಣಿ · 11ನೇ ತಾರೀಕಿಗೆ ಸಲ್ಲಿಸಿ",
    "Net tax payable summary": "ನಿವ್ವಳ ತೆರಿಗೆ ಸಾರಾಂಶ",
    "From supplier filings": "ಪೂರೈಕೆದಾರರ ಸಲ್ಲಿಕೆಯಿಂದ",
    "Locked ITC statement": "ಲಾಕ್ ಆದ ITC ಹೇಳಿಕೆ",
    "Ready to File": "ಸಲ್ಲಿಸಲು ಸಿದ್ಧ",
    "No Data": "ಡೇಟಾ ಇಲ್ಲ",

    # Upload & Extract
    "📤 Upload & Extract": "📤 ಅಪ್‌ಲೋಡ್ & ಓದು",
    "Upload an invoice — OCR reads and auto-detects Purchase or Sales.": "ಇನ್ವಾಯ್ಸ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ — OCR ಓದಿ ಖರೀದಿ ಅಥವಾ ಮಾರಾಟ ಗುರುತಿಸುತ್ತದೆ.",
    "Drop invoice here": "ಇಲ್ಲಿ ಇನ್ವಾಯ್ಸ್ ಹಾಕಿ",
    "Extract Data": "ಡೇಟಾ ತೆಗೆ",
    "Reading invoice...": "ಇನ್ವಾಯ್ಸ್ ಓದಲಾಗುತ್ತಿದೆ...",
    "Extraction complete.": "ಹೊರತೆಗೆಯುವಿಕೆ ಪೂರ್ಣವಾಯಿತು.",
    "Extracted Fields": "ತೆಗೆದ ವಿವರಗಳು",
    "SALES INVOICE → Sales Register": "ಮಾರಾಟ ಇನ್ವಾಯ್ಸ್ → ಮಾರಾಟ ನೋಂದಣಿ",
    "PURCHASE INVOICE → Purchase Register": "ಖರೀದಿ ಇನ್ವಾಯ್ಸ್ → ಖರೀದಿ ನೋಂದಣಿ",
    "Review & Confirm": "ಪರಿಶೀಲಿಸಿ & ದೃಢಪಡಿಸಿ",
    "Vendor / Party Name": "ವ್ಯಾಪಾರಿ / ಪಾರ್ಟಿ ಹೆಸರು",
    "Invoice Type": "ಇನ್ವಾಯ್ಸ್ ವಿಧ",
    "Date": "ದಿನಾಂಕ",
    "GSTIN": "GSTIN",
    "Calculated Total": "ಲೆಕ್ಕ ಹಾಕಿದ ಒಟ್ಟು",
    "Confirm & Add to Register": "ದೃಢಪಡಿಸಿ & ನೋಂದಣಿಗೆ ಸೇರಿಸಿ",
    "Upload a document and click Extract": "ದಾಖಲೆ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು Extract ಕ್ಲಿಕ್ ಮಾಡಿ",

    # Manual Entry
    "✏️ Manual Entry": "✏️ ಕೈಯಾರೆ ನಮೂದು",
    "Add Entry": "ನಮೂದು ಸೇರಿಸಿ",
    "GSTIN (optional)": "GSTIN (ಐಚ್ಛಿಕ)",
    "Recent Entries": "ಇತ್ತೀಚಿನ ನಮೂದುಗಳು",
    "No entries yet.": "ಇನ್ನೂ ನಮೂದುಗಳಿಲ್ಲ.",
    "Vendor name is required.": "ವ್ಯಾಪಾರಿ ಹೆಸರು ಅಗತ್ಯ.",

    # Purchase Register
    "📋 Purchase Register": "📋 ಖರೀದಿ ನೋಂದಣಿ",
    "All invoices where you are the buyer — Input Tax Credit (ITC) eligible.": "ನೀವು ಖರೀದಿದಾರರಾಗಿರುವ ಎಲ್ಲ ಇನ್ವಾಯ್ಸ್‌ಗಳು — ITC ಅರ್ಹ.",
    "Total Purchases": "ಒಟ್ಟು ಖರೀದಿ",
    "Input CGST (ITC)": "ಇನ್‌ಪುಟ್ CGST (ITC)",
    "Input SGST (ITC)": "ಇನ್‌ಪುಟ್ SGST (ITC)",
    "Entries": "ನಮೂದುಗಳು",
    "Search vendor": "ವ್ಯಾಪಾರಿ ಹುಡುಕಿ",
    "Export CSV": "CSV ರಫ್ತು",
    "No purchase entries yet. Upload purchase invoices or add manually.": "ಇನ್ನೂ ಖರೀದಿ ನಮೂದುಗಳಿಲ್ಲ. ಖರೀದಿ ಇನ್ವಾಯ್ಸ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕೈಯಾರೆ ಸೇರಿಸಿ.",

    # Sales Register
    "💰 Sales Register": "💰 ಮಾರಾಟ ನೋಂದಣಿ",
    "All invoices where you are the seller — Output Tax collected from customers.": "ನೀವು ಮಾರಾಟಗಾರರಾಗಿರುವ ಎಲ್ಲ ಇನ್ವಾಯ್ಸ್‌ಗಳು — ಗ್ರಾಹಕರಿಂದ ಸಂಗ್ರಹಿಸಿದ ತೆರಿಗೆ.",
    "Total Sales": "ಒಟ್ಟು ಮಾರಾಟ",
    "Output CGST": "ಔಟ್‌ಪುಟ್ CGST",
    "Output SGST": "ಔಟ್‌ಪುಟ್ SGST",
    "Search buyer": "ಖರೀದಿದಾರ ಹುಡುಕಿ",
    "No sales entries yet. Upload sales invoices or add manually.": "ಇನ್ನೂ ಮಾರಾಟ ನಮೂದುಗಳಿಲ್ಲ. ಮಾರಾಟ ಇನ್ವಾಯ್ಸ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕೈಯಾರೆ ಸೇರಿಸಿ.",

    # Reconciliation
    "🔄 GST Reconciliation": "🔄 GST ಹೊಂದಾಣಿಕೆ",
    "Full Tax Statement": "ಸಂಪೂರ್ಣ ತೆರಿಗೆ ಹೇಳಿಕೆ",
    "Tax Head": "ತೆರಿಗೆ ಮುಖ್ಯಸ್ಥ",
    "Input (Purchase)": "ಇನ್‌ಪುಟ್ (ಖರೀದಿ)",
    "Output (Sales)": "ಔಟ್‌ಪುಟ್ (ಮಾರಾಟ)",
    "Net Payable": "ನಿವ್ವಳ ಪಾವತಿಸಬೇಕು",
    "Total": "ಒಟ್ಟು",
    "GSTIN Validation": "GSTIN ಪರಿಶೀಲನೆ",
    "Add purchase and sales entries to run reconciliation.": "ಹೊಂದಾಣಿಕೆ ಮಾಡಲು ಖರೀದಿ ಮತ್ತು ಮಾರಾಟ ನಮೂದುಗಳನ್ನು ಸೇರಿಸಿ.",
    "Valid": "ಸರಿಯಾಗಿದೆ",
    "Invalid Format": "ತಪ್ಪಾದ ಸ್ವರೂಪ",
    "No GSTIN — Unregistered": "GSTIN ಇಲ್ಲ — ನೋಂದಾಯಿಸಲ್ಪಡದ",

    # GSTR-1
    "GSTR-1 — Statement of Outward Supplies": "GSTR-1 — ಹೊರಮುಖ ಪೂರೈಕೆ ಹೇಳಿಕೆ",
    "Filed by 11th of the following month. B2B invoices auto-appear in buyer's GSTR-2A.": "ಮುಂದಿನ ತಿಂಗಳ 11ನೇ ತಾರೀಕಿಗೆ ಸಲ್ಲಿಸಿ. B2B ಇನ್ವಾಯ್ಸ್‌ಗಳು ಖರೀದಿದಾರರ GSTR-2A ನಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ.",
    "Taxable Turnover": "ತೆರಿಗೆ ವಹಿವಾಟು",
    "Grand Total": "ಒಟ್ಟು ಮೊತ್ತ",
    "B2B Invoices": "B2B ಇನ್ವಾಯ್ಸ್‌ಗಳು",
    "B2C Invoices": "B2C ಇನ್ವಾಯ್ಸ್‌ಗಳು",
    "HSN Summary": "HSN ಸಾರಾಂಶ",
    "Full Table": "ಸಂಪೂರ್ಣ ಕೋಷ್ಟಕ",
    "No sales data. Add sales invoices to generate GSTR-1.": "ಮಾರಾಟ ಡೇಟಾ ಇಲ್ಲ. GSTR-1 ರಚಿಸಲು ಮಾರಾಟ ಇನ್ವಾಯ್ಸ್‌ಗಳನ್ನು ಸೇರಿಸಿ.",
    "Download GSTR-1 CSV": "GSTR-1 CSV ಡೌನ್‌ಲೋಡ್",

    # GSTR-3B
    "GSTR-3B — Monthly Summary Return": "GSTR-3B — ಮಾಸಿಕ ಸಾರಾಂಶ ರಿಟರ್ನ್",
    "Filed by 20th of the following month. Output tax − ITC = Net tax payable.": "ಮುಂದಿನ ತಿಂಗಳ 20ನೇ ತಾರೀಕಿಗೆ ಸಲ್ಲಿಸಿ. ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ − ITC = ನಿವ್ವಳ ತೆರಿಗೆ.",
    "GSTR-3B is a self-declaration. Interest at 18% p.a. applies on late payment.": "GSTR-3B ಸ್ವ-ಘೋಷಣೆ. ತಡ ಪಾವತಿಗೆ 18% ವಾರ್ಷಿಕ ಬಡ್ಡಿ ಅನ್ವಯಿಸುತ್ತದೆ.",
    "Add sales and purchase entries to generate GSTR-3B.": "GSTR-3B ರಚಿಸಲು ಮಾರಾಟ ಮತ್ತು ಖರೀದಿ ನಮೂದುಗಳನ್ನು ಸೇರಿಸಿ.",
    "3.1 Output Tax": "3.1 ಔಟ್‌ಪುಟ್ ತೆರಿಗೆ",
    "4. ITC Available": "4. ITC ಲಭ್ಯ",
    "Net Tax Payable": "ನಿವ್ವಳ ತೆರಿಗೆ ಪಾವತಿಸಬೇಕು",
    "Download GSTR-3B CSV": "GSTR-3B CSV ಡೌನ್‌ಲೋಡ್",

    # GSTR-2A/2B
    "GSTR-2A / 2B — Inward Supplies ITC Statement": "GSTR-2A / 2B — ಒಳಮುಖ ಪೂರೈಕೆ ITC ಹೇಳಿಕೆ",
    "Auto-populated from your suppliers' GSTR-1 filings.": "ನಿಮ್ಮ ಪೂರೈಕೆದಾರರ GSTR-1 ಸಲ್ಲಿಕೆಯಿಂದ ಸ್ವಯಂ-ತುಂಬಿದ.",
    "GSTR-2A Data": "GSTR-2A ಡೇಟಾ",
    "GSTR-2B (Static)": "GSTR-2B (ಸ್ಥಿರ)",
    "Reconciliation": "ಹೊಂದಾಣಿಕೆ",
    "Add 2A Entry": "2A ನಮೂದು ಸೇರಿಸಿ",
    "Supplier GSTIN": "ಪೂರೈಕೆದಾರ GSTIN",
    "Supplier Name": "ಪೂರೈಕೆದಾರ ಹೆಸರು",
    "Invoice Number": "ಇನ್ವಾಯ್ಸ್ ಸಂಖ್ಯೆ",
    "Invoice Date": "ಇನ್ವಾಯ್ಸ್ ದಿನಾಂಕ",
    "Add to GSTR-2A": "GSTR-2A ಗೆ ಸೇರಿಸಿ",
    "Suppliers Filed": "ಪೂರೈಕೆದಾರರು ಸಲ್ಲಿಸಿದ್ದಾರೆ",
    "Total Invoices (2A)": "ಒಟ್ಟು ಇನ್ವಾಯ್ಸ್‌ಗಳು (2A)",
    "ITC Available (2A)": "ITC ಲಭ್ಯ (2A)",
    "Download GSTR-2A CSV": "GSTR-2A CSV ಡೌನ್‌ಲೋಡ್",
    "Download GSTR-2B CSV": "GSTR-2B CSV ಡೌನ್‌ಲೋಡ್",
    "Download Reconciliation CSV": "ಹೊಂದಾಣಿಕೆ CSV ಡೌನ್‌ಲೋಡ್",
    "Total Invoices": "ಒಟ್ಟು ಇನ್ವಾಯ್ಸ್‌ಗಳು",
    "Matched": "ಹೊಂದಿದೆ",
    "Mismatch": "ಹೊಂದಿಲ್ಲ",
    "Not in 2A": "2A ನಲ್ಲಿ ಇಲ್ಲ",

    # Login
    "Username": "ಬಳಕೆದಾರ ಹೆಸರು",
    "Password": "ಪಾಸ್‌ವರ್ಡ್",
    "Enter username": "ಬಳಕೆದಾರ ಹೆಸರು ನಮೂದಿಸಿ",
    "Enter password": "ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ",
    "Sign In": "ಸೈನ್ ಇನ್",
    "Invalid username or password.": "ತಪ್ಪಾದ ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್.",

    # Upload & Extract form fields
    "Purchase Invoice": "ಖರೀದಿ ಇನ್ವಾಯ್ಸ್",
    "Sales Invoice": "ಮಾರಾಟ ಇನ್ವಾಯ್ಸ್",
    "Credit Note": "ಕ್ರೆಡಿಟ್ ನೋಟ್",
    "Debit Note": "ಡೆಬಿಟ್ ನೋಟ್",
    "Expense Receipt": "ವೆಚ್ಚದ ರಸೀದಿ",
    "Subtotal (₹)": "ಉಪ ಮೊತ್ತ (₹)",
    "CGST (₹)": "CGST (₹)",
    "SGST (₹)": "SGST (₹)",
    "CGST %": "CGST %",
    "SGST %": "SGST %",
    "Taxable Value (₹)": "ತೆರಿಗೆ ಮೌಲ್ಯ (₹)",
    "No GSTIN but GST charged — illegal. Cannot claim ITC. Request a corrected invoice.": "GSTIN ಇಲ್ಲದೆ GST ವಿಧಿಸಲಾಗಿದೆ — ಅಕ್ರಮ. ITC ಕ್ಲೇಮ್ ಮಾಡಲಾಗದು. ಸರಿಪಡಿಸಿದ ಇನ್ವಾಯ್ಸ್ ಕೇಳಿ.",
    "No GSTIN — Unregistered dealer. ITC cannot be claimed.": "GSTIN ಇಲ್ಲ — ನೋಂದಾಯಿಸಲ್ಪಡದ ವ್ಯಾಪಾರಿ. ITC ಕ್ಲೇಮ್ ಮಾಡಲಾಗದು.",

    # Metrics
    "Search vendor": "ವ್ಯಾಪಾರಿ ಹುಡುಕಿ",
    "Search buyer": "ಖರೀದಿದಾರ ಹುಡುಕಿ",

    # Reconciliation messages
    "Net GST Payable to Government: ": "ಸರ್ಕಾರಕ್ಕೆ ನಿವ್ವಳ GST ಪಾವತಿಸಬೇಕು: ",
    " You owe this amount after adjusting ITC.": " ITC ಸರಿಹೊಂದಿಸಿದ ನಂತರ ನೀವು ಈ ಮೊತ್ತ ಪಾವತಿಸಬೇಕು.",
    "Input Tax Credit exceeds Output Tax by ": "ಇನ್‌ಪುಟ್ ತೆರಿಗೆ ಕ್ರೆಡಿಟ್ ಔಟ್‌ಪುಟ್ ತೆರಿಗೆಗಿಂತ ಹೆಚ್ಚಿದೆ ",
    ". Carry forward to next period.": ". ಮುಂದಿನ ಅವಧಿಗೆ ಮುಂದೂಡಿ.",

    # GSTR-1 captions
    "B2B invoices (with GSTIN) — auto-appear in buyer's GSTR-2A.": "B2B ಇನ್ವಾಯ್ಸ್‌ಗಳು (GSTIN ಸಹಿತ) — ಖರೀದಿದಾರರ GSTR-2A ನಲ್ಲಿ ತಾನೇ ಕಾಣಿಸುತ್ತವೆ.",
    "No B2B invoices (no entries with GSTIN).": "B2B ಇನ್ವಾಯ್ಸ್‌ಗಳಿಲ್ಲ (GSTIN ಸಹಿತ ನಮೂದುಗಳಿಲ್ಲ).",
    "B2C invoices (no GSTIN) — buyer cannot claim ITC.": "B2C ಇನ್ವಾಯ್ಸ್‌ಗಳು (GSTIN ಇಲ್ಲ) — ಖರೀದಿದಾರರು ITC ಕ್ಲೇಮ್ ಮಾಡಲಾಗದು.",
    "No B2C invoices.": "B2C ಇನ್ವಾಯ್ಸ್‌ಗಳಿಲ್ಲ.",
    "Invoice summary (HSN/SAC grouping).": "ಇನ್ವಾಯ್ಸ್ ಸಾರಾಂಶ (HSN/SAC ಗುಂಪು).",

    # GSTR-3B messages
    "You owe ": "ನೀವು ₹",
    " in GST. Pay via GSTN portal by 20th of next month. Late payment: 18% p.a. + ₹50/day.": " GST ಪಾವತಿಸಬೇಕು. ಮುಂದಿನ ತಿಂಗಳ 20ನೇ ತಾರೀಕಿಗೆ GSTN ಪೋರ್ಟಲ್ ಮೂಲಕ ಪಾವತಿಸಿ. ತಡ ಪಾವತಿ: 18% + ₹50/ದಿನ.",
    "Excess ITC of ": "ಹೆಚ್ಚುವರಿ ITC ₹",
    " — carry forward to next period.": " — ಮುಂದಿನ ಅವಧಿಗೆ ಮುಂದೂಡಿ.",

    # GSTR-2A/2B
    "Simulate supplier-filed entries (in production this pulls from GSTN API).": "ಪೂರೈಕೆದಾರ-ಸಲ್ಲಿಸಿದ ನಮೂದುಗಳನ್ನು ಅನುಕರಿಸಿ (ಉತ್ಪಾದನೆಯಲ್ಲಿ GSTN API ನಿಂದ ತೆಗೆಯಲಾಗುತ್ತದೆ).",
    "No GSTR-2A entries. Go to Add 2A Entry tab to simulate supplier data.": "GSTR-2A ನಮೂದುಗಳಿಲ್ಲ. ಪೂರೈಕೆದಾರ ಡೇಟಾ ಅನುಕರಿಸಲು 2A ನಮೂದು ಸೇರಿಸಿ ಟ್ಯಾಬ್‌ಗೆ ಹೋಗಿ.",
    "GSTR-2B is generated after 2A data is available. Add entries in Add 2A Entry first.": "2A ಡೇಟಾ ಲಭ್ಯವಾದ ನಂತರ GSTR-2B ರಚಿಸಲಾಗುತ್ತದೆ. ಮೊದಲು 2A ನಮೂದು ಸೇರಿಸಿ ನಲ್ಲಿ ನಮೂದಿಸಿ.",
    "GSTR-2B snapshot — Locked ITC claimable in GSTR-3B: ": "GSTR-2B ಸ್ನ್ಯಾಪ್‌ಶಾಟ್ — GSTR-3B ನಲ್ಲಿ ಕ್ಲೇಮ್ ಮಾಡಬಹುದಾದ ಲಾಕ್ ITC: ",
    "Match your Purchase Register vs GSTR-2A to identify claimable ITC.": "ಕ್ಲೇಮ್ ಮಾಡಬಹುದಾದ ITC ಗುರುತಿಸಲು ನಿಮ್ಮ ಖರೀದಿ ನೋಂದಣಿ vs GSTR-2A ತಾಳೆ ಮಾಡಿ.",
    "No purchase entries to reconcile.": "ಹೊಂದಾಣಿಕೆ ಮಾಡಲು ಖರೀದಿ ನಮೂದುಗಳಿಲ್ಲ.",
    "Add 2A entries and purchase invoices to reconcile.": "ಹೊಂದಾಣಿಕೆ ಮಾಡಲು 2A ನಮೂದುಗಳು ಮತ್ತು ಖರೀದಿ ಇನ್ವಾಯ್ಸ್‌ಗಳನ್ನು ಸೇರಿಸಿ.",
    "Action Guide": "ಕ್ರಿಯಾ ಮಾರ್ಗದರ್ಶಿ",
    "Amount Mismatch": "ಮೊತ್ತ ಹೊಂದಿಲ್ಲ",
    "Supplier hasn't filed. Follow up before claiming ITC.": "ಪೂರೈಕೆದಾರರು ಸಲ್ಲಿಸಿಲ್ಲ. ITC ಕ್ಲೇಮ್ ಮಾಡುವ ಮೊದಲು ಅನುಸರಿಸಿ.",
    "Contact supplier to amend GSTR-1, or reverse ITC.": "GSTR-1 ತಿದ್ದುಪಡಿ ಮಾಡಲು ಪೂರೈಕೆದಾರರನ್ನು ಸಂಪರ್ಕಿಸಿ, ಅಥವಾ ITC ರಿವರ್ಸ್ ಮಾಡಿ.",
    "Claim ITC in GSTR-3B Table 4.": "GSTR-3B ಟೇಬಲ್ 4 ರಲ್ಲಿ ITC ಕ್ಲೇಮ್ ಮಾಡಿ.",
    "added to GSTR-2A.": "GSTR-2A ಗೆ ಸೇರಿಸಲಾಗಿದೆ.",
    "added to": "ಸೇರಿಸಲಾಗಿದೆ",
    "Sales Register": "ಮಾರಾಟ ನೋಂದಣಿ",
    "Purchase Register": "ಖರೀದಿ ನೋಂದಣಿ",
    "GSTR-1 — Dynamic": "GSTR-2A — ಕ್ರಿಯಾಶೀಲ",
    "GSTR-2A — Dynamic": "GSTR-2A — ಕ್ರಿಯಾಶೀಲ",
    "GSTR-2B — Static / Locked": "GSTR-2B — ಸ್ಥಿರ / ಲಾಕ್",
    "Auto-populated in real-time as suppliers file GSTR-1. Changes when suppliers amend or file late.": "ಪೂರೈಕೆದಾರರು GSTR-1 ಸಲ್ಲಿಸಿದಂತೆ ನೈಜ ಸಮಯದಲ್ಲಿ ಸ್ವಯಂ-ತುಂಬಿದ.",
    "Locked snapshot of ITC available for a specific return period. Use this to claim ITC in GSTR-3B.": "ನಿರ್ದಿಷ್ಟ ರಿಟರ್ನ್ ಅವಧಿಗೆ ಲಭ್ಯ ITC ಯ ಲಾಕ್ ಸ್ನ್ಯಾಪ್‌ಶಾಟ್. GSTR-3B ನಲ್ಲಿ ITC ಕ್ಲೇಮ್ ಮಾಡಲು ಇದನ್ನು ಬಳಸಿ.",
}

def T(key, lang=None):
    """Return Kannada translation if lang is Kannada, else return key as-is."""
    if lang is None:
        lang = st.session_state.get("lang", "English")
    if lang == "ಕನ್ನಡ":
        return TR.get(key, key)
    return key


# ── GLOBAL STYLE ──
STYLE = """
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
.stInfo{background:rgba(0,229,160,0.06) !important;border-left:3px solid var(--accent) !important;}
hr{border:none;border-top:1px solid var(--border);margin:1.5rem 0;}

.stProgress>div>div{background:linear-gradient(90deg,var(--accent),var(--accent2)) !important;border-radius:100px !important;}
.stProgress>div{background:var(--surface2) !important;border-radius:100px !important;}

/* Legacy class aliases so existing page code still works */
.page-title{font-family:'Syne',sans-serif;font-weight:800;font-size:1.5rem;color:var(--text);margin-bottom:0.2rem;}
.page-sub{color:var(--muted);font-size:0.88rem;margin-bottom:1.5rem;}
.section-label{font-family:'DM Mono',monospace;font-size:0.7rem;color:var(--muted);text-transform:uppercase;
letter-spacing:0.1em;margin:1.2rem 0 0.6rem;padding-bottom:0.4rem;border-bottom:1px solid var(--border);}
.info-box{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem 1.25rem;font-size:0.85rem;}
.tag{display:inline-block;padding:0.2rem 0.7rem;border-radius:100px;font-family:'DM Mono',monospace;font-size:0.74rem;font-weight:500;}
.tag-green{background:rgba(0,229,160,0.12);color:#00E5A0;border:1px solid rgba(0,229,160,0.3);}
.tag-amber{background:rgba(255,181,71,0.12);color:#FFB547;border:1px solid rgba(255,181,71,0.3);}
.tag-red{background:rgba(255,107,107,0.12);color:#FF6B6B;border:1px solid rgba(255,107,107,0.3);}
.tag-blue{background:rgba(123,97,255,0.12);color:#7B61FF;border:1px solid rgba(123,97,255,0.3);}
.tag-purple{background:rgba(123,97,255,0.12);color:#7B61FF;border:1px solid rgba(123,97,255,0.3);}

/* Hamburger button */
div[data-testid="stButton"].hamburger-wrap > button {
    position: fixed !important;top: 12px !important;left: 12px !important;
    z-index: 10000 !important;width: 40px !important;height: 36px !important;
    padding: 0 !important;font-size: 1rem !important;
    background: #111318 !important;border: 1px solid #1E2330 !important;
    border-radius: 8px !important;box-shadow: 0 4px 16px rgba(0,0,0,0.6) !important;
    line-height: 1 !important;color: #E8ECF4 !important;
    transition: background 0.15s, border-color 0.15s !important;
}
div[data-testid="stButton"].hamburger-wrap > button:hover {
    background: #181C24 !important;border-color: #00E5A0 !important;
}

</style>
"""

# ── HAMBURGER HELPER ──
def hamburger_btn():
    """Renders a fixed ☰/✕ button that toggles the sidebar overlay."""
    is_open = st.session_state.get("show_sidebar_overlay", False)
    icon = "✕" if is_open else "☰"
    st.markdown('<div class="hamburger-wrap" style="height:0;overflow:visible;">', unsafe_allow_html=True)
    if st.button(icon, key="hamburger"):
        st.session_state.show_sidebar_overlay = not is_open
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════
# LOGIN — animated card + password validation
# ════════════════════════════════════════════════
def show_login():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* ── Hide all Streamlit chrome on login ── */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"]        { display: none !important; }
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    .block-container {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── Grid background ── */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(0,229,160,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,229,160,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── Radial glow ── */
    [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed;
        top: 20%; left: 50%;
        transform: translateX(-50%);
        width: 600px; height: 400px;
        background: radial-gradient(ellipse at center,
            rgba(0,229,160,0.06) 0%,
            rgba(123,97,255,0.04) 50%,
            transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Card ── */
    .login-wrap {
        position: relative;
        z-index: 1;
        width: 340px;
        background: #111318;
        border: 1px solid #1E2330;
        border-radius: 20px;
        padding: 2.8rem 2.2rem 2.4rem;
        box-shadow:
            0 0 0 1px rgba(0,229,160,0.04),
            0 24px 60px rgba(0,0,0,0.6),
            0 8px 20px rgba(0,0,0,0.4),
            inset 0 1px 0 rgba(255,255,255,0.04);
        animation: cardIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    @keyframes cardIn {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* top accent line */
    .login-wrap::before {
        content: '';
        position: absolute;
        top: 0; left: 20%; right: 20%;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00E5A0, #7B61FF, transparent);
        border-radius: 100px;
    }

    .login-mark {
        width: 44px; height: 44px;
        background: linear-gradient(135deg, #00E5A0, #7B61FF);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 1.2rem;
        font-size: 1.3rem;
        box-shadow: 0 4px 20px rgba(0,229,160,0.25);
    }
    .login-title {
        font-family: 'Syne', sans-serif;
        font-weight: 800; font-size: 1.65rem;
        background: linear-gradient(135deg, #E8ECF4 30%, #00E5A0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center; margin-bottom: 0.2rem; letter-spacing: -0.5px;
    }
    .login-sub {
        text-align: center; color: #3A4055;
        font-size: 0.72rem; margin-bottom: 2rem;
        font-family: 'DM Mono', monospace;
        letter-spacing: 0.18em; text-transform: uppercase;
    }

    /* ── Inputs ── */
    .login-wrap .stTextInput > div > div > input {
        background: #0D0F14 !important;
        border: 1px solid #252A38 !important;
        border-radius: 10px !important;
        color: #E8ECF4 !important;
        font-size: 0.88rem !important;
        padding: 0.65rem 0.9rem !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .login-wrap .stTextInput > div > div > input:focus {
        border-color: #00E5A0 !important;
        box-shadow: 0 0 0 3px rgba(0,229,160,0.1) !important;
    }
    [data-testid="InputInstructions"] {
        display: none !important; visibility: hidden !important;
        opacity: 0 !important; height: 0 !important; overflow: hidden !important;
    }

    /* ── Sign In button ── */
    .login-wrap .stButton > button {
        background: linear-gradient(135deg, #00E5A0, #00BD85) !important;
        color: #060810 !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important; font-size: 0.92rem !important;
        border: none !important; border-radius: 10px !important;
        padding: 0.7rem 1.6rem !important; letter-spacing: 0.02em !important;
        box-shadow: 0 4px 20px rgba(0,229,160,0.2) !important;
        transition: all 0.2s !important; margin-top: 0.5rem !important;
    }
    .login-wrap .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(0,229,160,0.35) !important;
    }

    /* ── Password validation popup ── */
    #pw-popup {
        display: none; position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%) scale(0.92);
        z-index: 99999;
        background: #0E1118; border: 1px solid #1E2330; border-radius: 16px;
        padding: 1.8rem 2rem; width: 300px;
        box-shadow: 0 0 0 1px rgba(255,107,107,0.12), 0 24px 60px rgba(0,0,0,0.8);
        animation: popIn 0.25s cubic-bezier(0.22,1,0.36,1) forwards;
    }
    #pw-popup.show { display: block; }
    @keyframes popIn {
        from { opacity: 0; transform: translate(-50%, -50%) scale(0.88); }
        to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    }
    #pw-popup-overlay {
        display: none; position: fixed; inset: 0;
        background: rgba(0,0,0,0.55); z-index: 99998; backdrop-filter: blur(2px);
    }
    #pw-popup-overlay.show { display: block; }
    #pw-popup-icon { font-size: 2rem; text-align: center; margin-bottom: 0.75rem; }
    #pw-popup-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem;
        color: #FF6B6B; text-align: center; margin-bottom: 0.5rem; }
    #pw-popup-msg { font-family: 'DM Mono', monospace; font-size: 0.78rem; color: #8A90A8;
        text-align: center; line-height: 1.6; margin-bottom: 1.2rem; }
    #pw-popup-msg strong { color: #FFB547; font-weight: 500; }
    #pw-popup-close {
        display: block; width: 100%; padding: 0.6rem;
        background: rgba(255,107,107,0.1); border: 1px solid rgba(255,107,107,0.25);
        border-radius: 8px; color: #FF6B6B;
        font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.85rem;
        cursor: pointer; transition: background 0.15s;
    }
    #pw-popup-close:hover { background: rgba(255,107,107,0.18); }

    /* Eye-toggle button */
    .pw-eye-btn {
        position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
        background: none; border: none; cursor: pointer; padding: 4px 6px;
        z-index: 99; display: flex; align-items: center; justify-content: center;
        border-radius: 4px; transition: background 0.15s;
    }
    .pw-eye-btn:hover { background: rgba(255,255,255,0.05); }
    </style>

    <!-- Password Popup HTML -->
    <div id="pw-popup-overlay" onclick="closePwPopup()"></div>
    <div id="pw-popup">
        <div id="pw-popup-icon">🔐</div>
        <div id="pw-popup-title">Weak Password</div>
        <div id="pw-popup-msg"></div>
        <button id="pw-popup-close" onclick="closePwPopup()">Got it</button>
    </div>

    <script>
    function showPwPopup(message) {
        document.getElementById('pw-popup-msg').innerHTML = message;
        document.getElementById('pw-popup-overlay').classList.add('show');
        document.getElementById('pw-popup').classList.add('show');
    }
    function closePwPopup() {
        document.getElementById('pw-popup-overlay').classList.remove('show');
        document.getElementById('pw-popup').classList.remove('show');
    }
    document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closePwPopup(); });

    // ── Intercept form submit and validate password ──
    function attachPasswordValidator() {
        const submitBtns = document.querySelectorAll('[data-testid="stFormSubmitButton"] button');
        submitBtns.forEach(function(btn) {
            if (btn.dataset.pwValidatorAttached) return;
            btn.dataset.pwValidatorAttached = '1';
            btn.addEventListener('click', function(e) {
                const pwInput = document.querySelector(
                    '[data-testid="stTextInput"] input[type="password"], ' +
                    '[data-testid="stTextInput"] input[type="text"][data-eyeAttached]'
                );
                if (!pwInput) return;
                const pw = pwInput.value;
                let failMessage = null;
                if (pw.length < 8) {
                    failMessage = 'Password must be <strong>at least 8 characters</strong> long.';
                } else if (!/[A-Z]/.test(pw)) {
                    failMessage = 'Password must contain <strong>at least 1 uppercase letter</strong> (A-Z).';
                } else if (!/[a-z]/.test(pw)) {
                    failMessage = 'Password must contain <strong>at least 1 lowercase letter</strong> (a-z).';
                } else if (!/[0-9]/.test(pw)) {
                    failMessage = 'Password must contain <strong>at least 1 number</strong> (0-9).';
                } else if (!/[^A-Za-z0-9]/.test(pw)) {
                    failMessage = 'Password must contain <strong>at least 1 special character</strong> (e.g. @, #, $, !).';
                }
                if (failMessage) {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    showPwPopup(failMessage);
                }
            }, true);
        });
    }

    // ── Eye toggle ──
    const EYE_OPEN  = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5A6075" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    const EYE_SLASH = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5A6075" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;

    function attachEyeToggle() {
        const inputs = document.querySelectorAll('[data-testid="stTextInput"] input[type="password"]');
        inputs.forEach(function(input) {
            if (input.dataset.eyeAttached) return;
            input.dataset.eyeAttached = '1';
            const wrapper = input.parentElement;
            if (!wrapper) return;
            wrapper.style.position = 'relative';
            input.style.paddingRight = '2.5rem';
            const stBtn = wrapper.querySelector('button');
            if (stBtn) stBtn.style.display = 'none';
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'pw-eye-btn';
            btn.innerHTML = EYE_SLASH;
            btn.title = 'Show password';
            let isVisible = false;
            btn.addEventListener('click', function(e) {
                e.preventDefault(); e.stopPropagation();
                isVisible = !isVisible;
                input.type = isVisible ? 'text' : 'password';
                btn.innerHTML = isVisible ? EYE_OPEN : EYE_SLASH;
                btn.title = isVisible ? 'Hide password' : 'Show password';
            });
            wrapper.appendChild(btn);
        });
    }

    // MutationObserver to handle Streamlit async renders
    const domObserver = new MutationObserver(function() {
        attachEyeToggle();
        attachPasswordValidator();
    });
    domObserver.observe(document.body, { childList: true, subtree: true });
    setTimeout(attachEyeToggle, 300);
    setTimeout(attachEyeToggle, 800);
    setTimeout(attachPasswordValidator, 300);
    setTimeout(attachPasswordValidator, 800);
    </script>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown('<div class="login-mark">💳</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">FinFlow</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">GST Register · Sign In</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)
            if submitted:
                uname = username.strip().lower()
                # Server-side password validation (backup in case JS bypassed)
                pw_error = None
                import re as _re
                if len(password) < 8:
                    pw_error = "Password must be at least 8 characters long."
                elif not _re.search(r'[A-Z]', password):
                    pw_error = "Password must contain at least 1 uppercase letter (A-Z)."
                elif not _re.search(r'[a-z]', password):
                    pw_error = "Password must contain at least 1 lowercase letter (a-z)."
                elif not _re.search(r'[0-9]', password):
                    pw_error = "Password must contain at least 1 number (0-9)."
                elif not _re.search(r'[^A-Za-z0-9]', password):
                    pw_error = "Password must contain at least 1 special character (e.g. @, #, $, !)."

                if pw_error:
                    st.error(f"🔐 {pw_error}")
                elif uname in USERS and USERS[uname]["password"] == password:
                    st.session_state.logged_in  = True
                    st.session_state.username   = uname
                    st.session_state.user_name  = USERS[uname]["name"]
                    st.session_state.user_role  = USERS[uname]["role"]
                    st.session_state.user_color = USERS[uname]["color"]
                    st.session_state.page       = "Dashboard"
                    st.success(f"Welcome, {USERS[uname]['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        st.markdown('</div>', unsafe_allow_html=True)


st.set_page_config(
    page_title="FinFlow",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(STYLE, unsafe_allow_html=True)

COLS = ["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","Total","Status"]

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
                       "Date","Taxable","CGST","SGST","Total","Source"]),
        "lang": "English",
        "show_sidebar_overlay": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

if not st.session_state.logged_in:
    show_login()
    st.stop()

# ── SIDEBAR VISIBILITY ──
_page_is_dash = st.session_state.page == "Dashboard"
_overlay_open = st.session_state.get("show_sidebar_overlay", False)

if _page_is_dash:
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        display: block !important;
        position: relative !important;
        transform: none !important;
        height: 100vh;
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)
elif _overlay_open:
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        display: block !important;
        position: fixed !important;
        top: 0; left: 0;
        height: 100vh !important;
        width: 18rem !important;
        z-index: 9999 !important;
        transform: none !important;
        box-shadow: 8px 0 32px rgba(0,0,0,0.8) !important;
        overflow-y: auto;
    }
    [data-testid="stAppViewContainer"] > section:last-child {
        filter: brightness(0.4);
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    role  = st.session_state.user_role
    color = st.session_state.user_color

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

    if st.button(T("Logout"), key="logout_btn", use_container_width=True):
        for key in ["logged_in","username","user_name","user_role","user_color"]:
            st.session_state[key] = False if key == "logged_in" else ""
        st.session_state.show_sidebar_overlay = False
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
            st.session_state.show_sidebar_overlay = False
            st.rerun()

    st.markdown("---")

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
    st.markdown(f'<div class="page-title">{T("📊 Dashboard")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{T("GST Sales & Purchase Register")}</div>', unsafe_allow_html=True)

    tx = get_tax_summary()
    c1, c2, c3, c4 = st.columns(4)

    profit    = tx['s_total'] - tx['p_total']
    p_color   = "var(--green)" if profit >= 0 else "var(--red)"
    net_color = "var(--red)"   if tx['net_tax'] > 0 else "var(--green)"
    net_label = "Tax Payable"  if tx['net_tax'] > 0 else "Tax Refund"

    for col, label, val, sub, color in [
        (c1, T("Total Purchases"), f"₹{tx['p_total']:,.0f}", f"{tx['p_count']} {T('invoices')}", "var(--text)"),
        (c2, T("Total Sales"),     f"₹{tx['s_total']:,.0f}", f"{tx['s_count']} {T('invoices')}", "var(--text)"),
        (c3, T("Gross Margin"),    f"₹{profit:,.0f}",        T("Sales minus Purchases"),     p_color),
        (c4, net_label,         f"₹{abs(tx['net_tax']):,.0f}", T("Output tax − Input tax"), net_color),
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
        st.markdown(f'<div class="section-label">{T("GST Tax Breakdown")}</div>', unsafe_allow_html=True)
        rows = [
            ("CGST", tx['p_cgst'], tx['s_cgst'], tx['net_cgst']),
            ("SGST", tx['p_sgst'], tx['s_sgst'], tx['net_sgst']),
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
            <span style="color:var(--amber);">₹{tx['p_cgst']+tx['p_sgst']:,.2f}</span>
            <span style="color:var(--green);">₹{tx['s_cgst']+tx['s_sgst']:,.2f}</span>
            <span style="color:{total_color}; font-family:'IBM Plex Mono',monospace;">₹{tx['net_tax']:,.2f}</span>
        </div>"""
        st.markdown(header + body + footer, unsafe_allow_html=True)
        status_txt = T("Tax payable to government") if tx['net_tax'] > 0 else T("Input credit exceeds output tax")
        st.markdown(f'<div style="font-size:0.75rem; color:var(--muted); margin-top:0.5rem;">{status_txt}</div>', unsafe_allow_html=True)

    with right:
        st.markdown(f'<div class="section-label">{T("Sales vs Purchases")}</div>', unsafe_allow_html=True)
        chart_data = pd.DataFrame({"Amount": [tx['p_total'], tx['s_total']]}, index=["Purchases", "Sales"])
        st.bar_chart(chart_data)
        st.markdown(f"""
        <div class="info-box" style="margin-top:0.75rem; font-size:0.82rem; color:var(--muted);">
            <b style="color:var(--text);">{T("How net tax is calculated:")}</b><br>
            {T("Output Tax (on Sales) − Input Tax Credit (on Purchases) = Net GST Payable")}
        </div>""", unsafe_allow_html=True)

    p = st.session_state.purchase_register
    s = st.session_state.sales_register
    if not p.empty or not s.empty:
        st.markdown(f'<div class="section-label">{T("Recent Activity")}</div>', unsafe_allow_html=True)
        combined = pd.concat([
            p.assign(Type="Purchase") if not p.empty else pd.DataFrame(),
            s.assign(Type="Sales")    if not s.empty else pd.DataFrame(),
        ]).sort_values("Date", ascending=False).head(8)
        disp = combined[["ID","Date","Vendor","Type","Total","Status"]].copy()
        disp["Total"] = disp["Total"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

    st.markdown(f'<div class="section-label">{T("GSTR Filing Status")}</div>', unsafe_allow_html=True)
    g1, g2, g3, g4 = st.columns(4)
    has_data = not st.session_state.sales_register.empty or not st.session_state.purchase_register.empty
    for col, label, form, desc in [
        (g1, "GSTR-1",  T("Outward Supplies"),  T("Sales register · File by 11th")),
        (g2, "GSTR-3B", T("Summary Return"),    T("Net tax payable summary")),
        (g3, "GSTR-2A", T("Auto-Populated"),    T("From supplier filings")),
        (g4, "GSTR-2B", T("Static ITC"),        T("Locked ITC statement")),
    ]:
        status_color = "var(--amber)" if has_data else "var(--muted)"
        status_txt   = T("Ready to File") if has_data else T("No Data")
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
    hamburger_btn()
    st.markdown(f'<div class="page-title">{T("📤 Upload & Extract")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{T("Upload an invoice — OCR reads and auto-detects Purchase or Sales.")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        if st.session_state.get("lang") == "ಕನ್ನಡ":
            st.markdown("""
            <style>
            [data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child {
                font-size: 0 !important;
            }
            [data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child::after {
                content: "ಇಲ್ಲಿ ಫೈಲ್ ಎಳೆದು ಬಿಡಿ";
                font-size: 1rem !important;
                color: var(--text);
            }
            [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
                font-size: 0 !important;
            }
            [data-testid="stFileUploaderDropzoneInstructions"] > div > small::after {
                content: "ಗರಿಷ್ಠ 200MB • PDF, PNG, JPG, JPEG";
                font-size: 0.8rem !important;
                color: var(--muted);
            }
            [data-testid="stFileUploaderDropzone"] button {
                font-size: 0 !important;
            }
            [data-testid="stFileUploaderDropzone"] button::after {
                content: "ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ";
                font-size: 0.9rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(T("Drop invoice here"), type=["pdf","png","jpg","jpeg"])
        if uploaded_file:
            st.success(f"✓ {uploaded_file.name} ({uploaded_file.size//1024} KB)")
            ext = uploaded_file.name.lower().rsplit(".",1)[-1]
            if ext in ("png","jpg","jpeg"):
                st.image(uploaded_file, width=420)
                uploaded_file.seek(0)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(T("Extract Data"), use_container_width=True):
                with st.spinner(T("Reading invoice...")):
                    try:
                        uploaded_file.seek(0)
                        extracted = run_ocr(uploaded_file)
                        if extracted:
                            st.session_state.extracted = extracted
                            st.session_state.inv_type_detected = extracted.get("doc_type","Purchase Invoice")
                            st.success(T("Extraction complete."))
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

            if st.session_state.extracted:
                ext_data = st.session_state.extracted
                conf     = ext_data.get("confidence", 80)
                dtype    = ext_data.get("doc_type","Purchase Invoice")
                is_sales = "Sales" in dtype

                st.markdown(f'<div class="section-label">{T("Extracted Fields")}</div>', unsafe_allow_html=True)

                tag_class = "tag-green" if is_sales else "tag-amber"
                tag_text  = T("SALES INVOICE → Sales Register") if is_sales else T("PURCHASE INVOICE → Purchase Register")
                st.markdown(f'<div style="margin-bottom:0.75rem;"><span class="tag {tag_class}">{tag_text}</span></div>', unsafe_allow_html=True)

                st.progress(conf / 100)

                if not ext_data.get("gstin"):
                    has_tax = (ext_data.get("cgst",0) > 0 or ext_data.get("sgst",0) > 0)
                    if has_tax:
                        st.error(T("No GSTIN but GST charged — illegal. Cannot claim ITC. Request a corrected invoice."))
                    else:
                        st.warning(T("No GSTIN — Unregistered dealer. ITC cannot be claimed."))

                extracted_df = pd.DataFrame({
                    T("Field"): [
                        T("Vendor / Party"), T("Invoice Type"), T("Date"), T("GSTIN"),
                        T("Subtotal"), T("CGST (₹)"), T("SGST (₹)"), T("Total"),
                    ],
                    T("Value"): [
                        ext_data.get('vendor', ''),
                        ext_data.get('doc_type', ''),
                        ext_data.get('date', ''),
                        ext_data.get('gstin', '') or T("No GSTIN — Unregistered"),
                        f"₹{ext_data.get('subtotal', 0):,.2f}",
                        f"₹{ext_data.get('cgst', 0):,.2f}",
                        f"₹{ext_data.get('sgst', 0):,.2f}",
                        f"₹{ext_data.get('total', 0):,.2f}",
                    ]
                })
                st.dataframe(extracted_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown(f'<div class="section-label">{T("Review & Confirm")}</div>', unsafe_allow_html=True)
        if st.session_state.extracted:
            ext_data = st.session_state.extracted
            with st.form("confirm_form"):
                vendor   = st.text_input(T("Vendor / Party Name"), value=ext_data.get("vendor",""))
                doc_type = st.selectbox(T("Invoice Type"),
                    [T("Purchase Invoice"),T("Sales Invoice"),T("Credit Note"),T("Debit Note"),T("Expense Receipt")],
                    index=0 if "Purchase" in ext_data.get("doc_type","Purchase") else 1)
                txn_date = st.text_input(T("Date"), value=ext_data.get("date",""))
                gstin    = st.text_input(T("GSTIN"), value=ext_data.get("gstin",""))
                c1, c2 = st.columns(2)
                with c1:
                    subtotal = st.number_input(T("Subtotal (₹)"), value=float(ext_data.get("subtotal",0)), min_value=0.0, step=0.01)
                    cgst     = st.number_input(T("CGST (₹)"), value=float(ext_data.get("cgst",0)), min_value=0.0, step=0.01)
                with c2:
                    sgst  = st.number_input(T("SGST (₹)"), value=float(ext_data.get("sgst",0)), min_value=0.0, step=0.01)
                total_calc = subtotal + cgst + sgst
                st.markdown(f"""
                <div class="info-box" style="display:flex; justify-content:space-between; margin:0.5rem 0;">
                    <span style="color:var(--muted); font-size:0.85rem;">{T("Calculated Total")}</span>
                    <span style="font-family:'IBM Plex Mono',monospace; font-weight:600; color:var(--blue);">₹{total_calc:,.2f}</span>
                </div>""", unsafe_allow_html=True)
                submitted = st.form_submit_button(T("Confirm & Add to Register"), use_container_width=True)
                if submitted:
                    data = {"vendor":vendor,"date":txn_date,"gstin":gstin,
                            "subtotal":subtotal,"cgst":cgst,"sgst":sgst,"igst":0,"total":total_calc}
                    txn_id, reg = add_to_register(data, doc_type)
                    st.session_state.extracted = None
                    reg_name = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"{txn_id} added to {reg_name}.")
        else:
            st.markdown(f"""
            <div class="info-box" style="text-align:center; padding:3rem 2rem; color:var(--muted);">
                {T("Upload a document and click Extract")}
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# MANUAL ENTRY
# ════════════════════════════════════════════════
elif page == "Manual Entry":
    hamburger_btn()
    st.markdown(f'<div class="page-title">{T("✏️ Manual Entry")}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        with st.form("manual_form"):
            doc_type = st.selectbox(T("Invoice Type"),
                [T("Purchase Invoice"),T("Sales Invoice"),T("Expense Receipt"),T("Credit Note"),T("Debit Note")])
            vendor   = st.text_input(T("Vendor / Party Name"))
            txn_date = st.date_input(T("Date"), value=date.today())
            gstin    = st.text_input(T("GSTIN (optional)"))
            c1, c2 = st.columns(2)
            with c1:
                subtotal = st.number_input(T("Subtotal (₹)"), min_value=0.0, value=1000.0, step=1.0)
                cgst_pct = st.number_input(T("CGST %"), min_value=0.0, max_value=28.0, value=9.0, step=0.5)
            with c2:
                sgst_pct = st.number_input(T("SGST %"), min_value=0.0, max_value=28.0, value=9.0, step=0.5)
            cgst  = round(subtotal * cgst_pct / 100, 2)
            sgst  = round(subtotal * sgst_pct / 100, 2)
            total = subtotal + cgst + sgst
            st.markdown(f"""
            <div class="info-box" style="margin:0.5rem 0;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.3rem; font-size:0.84rem; margin-bottom:0.5rem;">
                    <span style="color:var(--muted);">{T('CGST %')[:4]}</span><span style="text-align:right; font-family:'IBM Plex Mono',monospace;">₹{cgst:,.2f}</span>
                    <span style="color:var(--muted);">{T('SGST %')[:4]}</span><span style="text-align:right; font-family:'IBM Plex Mono',monospace;">₹{sgst:,.2f}</span>
                </div>
                <div style="border-top:1px solid var(--border); padding-top:0.4rem;
                    display:flex; justify-content:space-between;">
                    <span style="font-weight:600;">{T('Total')}</span>
                    <span style="color:var(--blue); font-family:'IBM Plex Mono',monospace; font-weight:600;">₹{total:,.2f}</span>
                </div>
            </div>""", unsafe_allow_html=True)
            submit = st.form_submit_button(T("Add Entry"), use_container_width=True)
            if submit:
                if not vendor:
                    st.error(T("Vendor name is required."))
                else:
                    data = {"vendor":vendor,"date":txn_date.strftime("%d-%m-%Y"),"gstin":gstin,
                            "subtotal":subtotal,"cgst":cgst,"sgst":sgst,"igst":0,"total":total}
                    txn_id, reg = add_to_register(data, doc_type)
                    reg_name = "Sales Register" if "sales" in reg else "Purchase Register"
                    st.success(f"{txn_id} added to {reg_name}.")

    with col2:
        st.markdown(f'<div class="section-label">{T("Recent Entries")}</div>', unsafe_allow_html=True)
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
            st.info(T("No entries yet."))


# ════════════════════════════════════════════════
# PURCHASE REGISTER
# ════════════════════════════════════════════════
elif page == "Purchase Register":
    hamburger_btn()
    st.markdown(f'<div class="page-title">{T("📋 Purchase Register")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{T("All invoices where you are the buyer — Input Tax Credit (ITC) eligible.")}</div>', unsafe_allow_html=True)

    df = st.session_state.purchase_register.copy()
    if df.empty:
        st.info(T("No purchase entries yet. Upload purchase invoices or add manually."))
    else:
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric(T("Total Purchases"), f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric(T("Input CGST (ITC)"), f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric(T("Input SGST (ITC)"), f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric(T("Entries"), len(df))
        st.markdown("---")
        search = st.text_input(T("Search vendor"))
        if search:
            df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for col in ["Subtotal","CGST","SGST","Total"]:
            disp[col] = disp[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button(T("Export CSV"),
            data=df.to_csv(index=False).encode(),
            file_name=f"purchase_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ════════════════════════════════════════════════
# SALES REGISTER
# ════════════════════════════════════════════════
elif page == "Sales Register":
    hamburger_btn()
    st.markdown(f'<div class="page-title">{T("💰 Sales Register")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{T("All invoices where you are the seller — Output Tax collected from customers.")}</div>', unsafe_allow_html=True)

    df = st.session_state.sales_register.copy()
    if df.empty:
        st.info(T("No sales entries yet. Upload sales invoices or add manually."))
    else:
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric(T("Total Sales"), f"₹{df['Total'].astype(float).sum():,.2f}")
        with m2: st.metric(T("Output CGST"),  f"₹{df['CGST'].astype(float).sum():,.2f}")
        with m3: st.metric(T("Output SGST"),  f"₹{df['SGST'].astype(float).sum():,.2f}")
        with m4: st.metric(T("Entries"), len(df))
        st.markdown("---")
        search = st.text_input(T("Search buyer"))
        if search:
            df = df[df["Vendor"].str.contains(search, case=False, na=False)]
        disp = df.copy()
        for col in ["Subtotal","CGST","SGST","Total"]:
            disp[col] = disp[col].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True, height=400)
        st.download_button(T("Export CSV"),
            data=df.to_csv(index=False).encode(),
            file_name=f"sales_register_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")


# ════════════════════════════════════════════════
# RECONCILIATION
# ════════════════════════════════════════════════
elif page == "Reconciliation":
    hamburger_btn()
    st.markdown(f'<div class="page-title">{T("🔄 GST Reconciliation")}</div>', unsafe_allow_html=True)

    tx = get_tax_summary()
    p  = st.session_state.purchase_register
    s  = st.session_state.sales_register

    if p.empty and s.empty:
        st.info(T("Add purchase and sales entries to run reconciliation."))
    else:
        st.markdown(f'<div class="section-label">{T("Full Tax Statement")}</div>', unsafe_allow_html=True)

        rows = [
            ("CGST", tx['p_cgst'], tx['s_cgst'], tx['net_cgst']),
            ("SGST", tx['p_sgst'], tx['s_sgst'], tx['net_sgst']),
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
            <span style="color:var(--amber);">₹{tx['p_cgst']+tx['p_sgst']:,.2f}</span>
            <span style="color:var(--green);">₹{tx['s_cgst']+tx['s_sgst']:,.2f}</span>
            <span style="color:{tc}; font-family:'IBM Plex Mono',monospace;">₹{tx['net_tax']:,.2f}</span>
        </div>"""
        st.markdown(header + body + footer, unsafe_allow_html=True)

        if tx['net_tax'] > 0:
            st.warning(f"{T('Net GST Payable to Government: ')}₹{tx['net_tax']:,.2f}.{T(' You owe this amount after adjusting ITC.')}")
        else:
            st.success(f"{T('Input Tax Credit exceeds Output Tax by ')}₹{abs(tx['net_tax']):,.2f}{T('. Carry forward to next period.')}")

        st.markdown(f'<div class="section-label">{T("GSTIN Validation")}</div>', unsafe_allow_html=True)
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
    hamburger_btn()
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

        k1, k2, k3, k4 = st.columns(4)
        for col, label, val, sub in [
            (k1, "Taxable Turnover",    f"₹{summary['total_taxable']:,.2f}", ""),
            (k2, "Total CGST (Output)", f"₹{summary['total_cgst']:,.2f}",    ""),
            (k3, "Total SGST (Output)", f"₹{summary['total_sgst']:,.2f}",    ""),
            (k4, "Grand Total",         f"₹{summary['grand_total']:,.2f}",   f"{len(s_df)} invoices"),
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
                disp = b2b_df[["ID","Date","Vendor","GSTIN","Subtotal","CGST","SGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
                st.dataframe(disp, use_container_width=True, hide_index=True)
                total_tax = b2b_df["CGST"].astype(float).sum() + b2b_df["SGST"].astype(float).sum()
                st.markdown(f'<div style="background:rgba(0,229,160,0.06);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:var(--muted);">{len(b2b_df)} B2B invoice(s) · Taxable: {fmt_inr(b2b_df["Subtotal"].astype(float).sum())} · Tax: {fmt_inr(total_tax)}</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:0.75rem;">B2C invoices (no GSTIN) — buyer cannot claim ITC.</div>', unsafe_allow_html=True)
            if b2c_df.empty:
                st.info("No B2C invoices.")
            else:
                disp = b2c_df[["ID","Date","Vendor","Subtotal","CGST","SGST","Total"]].copy()
                for c in ["Subtotal","CGST","SGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
                st.dataframe(disp, use_container_width=True, hide_index=True)

        with tab3:
            st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:0.75rem;">Invoice summary (HSN/SAC grouping).</div>', unsafe_allow_html=True)
            hsn = pd.DataFrame({
                "Invoices": [len(s_df)],
                "Taxable":  [s_df["Subtotal"].astype(float).sum()],
                "CGST":     [s_df["CGST"].astype(float).sum()],
                "SGST":     [s_df["SGST"].astype(float).sum()],
                "Total":    [s_df["Total"].astype(float).sum()],
            })
            for c in ["Taxable","CGST","SGST","Total"]: hsn[c] = hsn[c].apply(fmt_inr)
            st.dataframe(hsn, use_container_width=True, hide_index=True)

        with tab4:
            disp = s_df.copy()
            for c in ["Subtotal","CGST","SGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
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
    hamburger_btn()
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

        def _grid_row(r, color="var(--text)"):
            return (f'<div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr;'
                    f'padding:0.75rem 1rem;border-top:1px solid var(--border);font-size:0.85rem;">'
                    f'<span style="font-family:DM Mono,monospace;color:var(--muted);font-size:0.75rem;">{r[0]}</span>'
                    f'<span>{r[1]}</span>'
                    f'<span style="color:{color};">{fmt_inr(r[2])}</span>'
                    f'<span>{fmt_inr(r[3])}</span><span>{fmt_inr(r[4])}</span><span>{fmt_inr(r[5])}</span></div>')

        def tax_table(title, rows, total_row, total_color="var(--accent)"):
            hdr = f"""<div style="font-size:0.9rem;font-family:Syne,sans-serif;font-weight:700;color:var(--text);margin-bottom:0.75rem;">{title}</div>
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;">
            <div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr;background:var(--surface2);
                padding:0.75rem 1rem;font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--muted);
                text-transform:uppercase;letter-spacing:0.08em;">
                <span>Section</span><span>Nature</span><span>Taxable</span><span>CGST</span><span>SGST</span>
            </div>"""
            body = "".join([_grid_row(r) for r in rows])
            foot = (f'<div style="display:grid;grid-template-columns:0.5fr 2.5fr 1fr 1fr 1fr;'
                    f'padding:0.75rem 1rem;border-top:2px solid var(--border);background:var(--surface2);font-weight:700;">'
                    f'<span></span><span>{total_row[0]}</span>'
                    f'<span style="color:{total_color};">{fmt_inr(total_row[1])}</span>'
                    f'<span style="color:{total_color};">{fmt_inr(total_row[2])}</span>'
                    f'<span style="color:{total_color};">{fmt_inr(total_row[3])}</span>'
                    f'</div></div>')
            return hdr + body + foot

        with tab1:
            rows = [
                ("3.1(a)", "Outward taxable supplies (other than zero rated)", data["out_taxable"], data["out_cgst"], data["out_sgst"], 0),
                ("3.1(b)", "Outward taxable supplies (zero rated)", 0, 0, 0),
                ("3.1(c)", "Other outward supplies (nil rated, exempt)", 0, 0, 0),
            ]
            st.markdown(tax_table("Table 3.1 — Details of Outward Supplies & Tax Liability", rows,
                ("TOTAL OUTPUT TAX", data["out_taxable"], data["out_cgst"], data["out_sgst"]), "#FF6B6B"), unsafe_allow_html=True)

        with tab2:
            itc_rows = [
                ("4(A)(1)", "ITC on Imports of goods",              0, 0, 0),
                ("4(A)(2)", "ITC on Imports of services",           0, 0, 0),
                ("4(A)(5)", "All other ITC (domestic purchases)",   data["itc_taxable"], data["itc_cgst"], data["itc_sgst"]),
            ]
            st.markdown(tax_table("Table 4 — Eligible Input Tax Credit (ITC)", itc_rows,
                ("TOTAL ITC AVAILABLE", data["itc_taxable"], data["itc_cgst"], data["itc_sgst"]), "#00E5A0"), unsafe_allow_html=True)

        with tab3:
            nc = "#FF6B6B" if data["net_cgst"]  > 0 else "#00E5A0"
            ns = "#FF6B6B" if data["net_sgst"]  > 0 else "#00E5A0"
            nt = "#FF6B6B" if data["net_total"] > 0 else "#00E5A0"
            st.markdown(f"""
            <div style="font-size:0.9rem;font-family:Syne,sans-serif;font-weight:700;color:var(--text);margin-bottom:0.75rem;">
                Table 6.1 — Payment of Tax (Net Liability)
            </div>
            <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:1.5rem;">
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;background:var(--surface2);
                    padding:0.75rem 1rem;font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--muted);
                    text-transform:uppercase;letter-spacing:0.08em;">
                    <span>Description</span><span>CGST</span><span>SGST</span><span>Total</span>
                </div>
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:0.75rem 1rem;border-top:1px solid var(--border);">
                    <span>Output Tax Liability</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_cgst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_sgst'])}</span>
                    <span style="color:#FF6B6B;">{fmt_inr(data['out_cgst']+data['out_sgst'])}</span>
                </div>
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:0.75rem 1rem;border-top:1px solid var(--border);">
                    <span>Less: ITC Available</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_cgst'])}</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_sgst'])}</span>
                    <span style="color:#00E5A0;">(−) {fmt_inr(data['itc_cgst']+data['itc_sgst'])}</span>
                </div>
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:1rem;
                    border-top:2px solid var(--border);background:var(--surface2);font-weight:700;font-size:1rem;">
                    <span style="font-family:'Syne',sans-serif;font-weight:800;">NET TAX PAYABLE</span>
                    <span style="color:{nc};font-size:1.1rem;">{fmt_inr(data['net_cgst'])}</span>
                    <span style="color:{ns};font-size:1.1rem;">{fmt_inr(data['net_sgst'])}</span>
                    <span style="color:{nt};font-size:1.2rem;font-weight:800;">{fmt_inr(data['net_total'])}</span>
                </div>
            </div>
            <div style="background:{'rgba(255,107,107,0.08)' if data['net_total']>0 else 'rgba(0,229,160,0.08)'};
                border:1px solid {'rgba(255,107,107,0.3)' if data['net_total']>0 else 'rgba(0,229,160,0.3)'};
                border-radius:10px;padding:1.25rem 1.5rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:{nt};margin-bottom:0.4rem;">
                    {'⚠️ You owe ₹' + f"{data['net_total']:,.2f}" + ' in GST'
                     if data['net_total']>0
                     else '✅ Excess ITC of ₹' + f"{abs(data['net_total']):,.2f}" + ' — carry forward'}
                </div>
                <div style="font-size:0.82rem;color:var(--muted);">
                    Pay via GSTN portal under Electronic Cash Ledger by 20th of following month.
                    Delay attracts 18% p.a. interest + ₹50/day late fee.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        gstr3b_export = pd.DataFrame([
            {"Section":"3.1(a)", "Description":"Outward Taxable Supplies",  "Taxable":data['out_taxable'], "CGST":data['out_cgst'], "SGST":data['out_sgst'], },
            {"Section":"4(A)(5)","Description":"ITC on Domestic Purchases", "Taxable":data['itc_taxable'], "CGST":data['itc_cgst'], "SGST":data['itc_sgst'], },
            {"Section":"6.1",    "Description":"Net Tax Payable",           "Taxable":data['out_taxable']-data['itc_taxable'], "CGST":data['net_cgst'], "SGST":data['net_sgst'], },
        ])
        st.download_button("⬇️ Download GSTR-3B Summary CSV",
            data=gstr3b_export.to_csv(index=False).encode(),
            file_name=f"GSTR3B_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# GSTR-2A / GSTR-2B
# ════════════════════════════════════════════════
elif page == "GSTR-2A / 2B":
    hamburger_btn()
    st.markdown('<div class="finflow-logo" style="font-size:1.6rem;margin-bottom:0.2rem;">GSTR-2A / 2B</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:var(--muted);font-size:0.88rem;margin-bottom:0.25rem;">
        <b style="color:var(--accent);">Inward Supplies ITC Statement</b> — Auto-populated from your suppliers' GSTR-1 filings
    </p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
        <div style="background:rgba(0,229,160,0.06);border:1px solid rgba(0,229,160,0.2);border-radius:10px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#00E5A0;margin-bottom:0.4rem;">📡 GSTR-2A — Dynamic</div>
            <div style="font-size:0.82rem;color:var(--muted);">Auto-populated in real-time as suppliers file GSTR-1. Changes when suppliers amend or file late.</div>
        </div>
        <div style="background:rgba(123,97,255,0.06);border:1px solid rgba(123,97,255,0.2);border-radius:10px;padding:1rem;">
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#a89cff;margin-bottom:0.4rem;">🔒 GSTR-2B — Static / Locked</div>
            <div style="font-size:0.82rem;color:var(--muted);">Locked snapshot of ITC available for a specific return period. Use this to claim ITC in GSTR-3B.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    p_df = st.session_state.purchase_register
    tab1, tab2, tab3, tab4 = st.tabs([T("GSTR-2A Data"), T("GSTR-2B (Static)"), T("Reconciliation"), T("Add 2A Entry")])

    with tab4:
        st.caption(T("Simulate supplier-filed entries (in production this pulls from GSTN API)."))
        with st.form("add_2a_form"):
            c1, c2 = st.columns(2)
            with c1:
                s_gstin  = st.text_input(T("Supplier GSTIN"))
                s_vendor = st.text_input(T("Supplier Name"))
                s_inv_no = st.text_input(T("Invoice Number"))
                s_date   = st.date_input(T("Invoice Date"), value=date.today())
            with c2:
                s_taxable = st.number_input(T("Taxable Value (₹)"), min_value=0.0, value=1000.0, step=1.0)
                s_cgst    = st.number_input(T("CGST (₹)"), min_value=0.0, value=90.0, step=0.01)
                s_sgst    = st.number_input(T("SGST (₹)"), min_value=0.0, value=90.0, step=0.01)
            s_total = s_taxable + s_cgst + s_sgst
            st.markdown(f"**Total: {fmt_inr(s_total)}**")
            if st.form_submit_button(T("Add to GSTR-2A"), use_container_width=True):
                new_row = {"GSTIN":s_gstin,"Vendor":s_vendor,"InvoiceNo":s_inv_no,
                           "Date":s_date.strftime("%d-%m-%Y"),"Taxable":s_taxable,
                           "CGST":s_cgst,"SGST":s_sgst,"IGST":0,"Total":s_total,
                           "Source":"GSTR-2A (Supplier Filed)"}
                st.session_state.gstr2a_data = pd.concat(
                    [st.session_state.gstr2a_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"{s_vendor} {T('added to GSTR-2A.')}")
                st.rerun()

    gstr2a_df, gstr2b_df, recon_df = build_gstr2a_2b(p_df, st.session_state.gstr2a_data)

    with tab1:
        if st.session_state.gstr2a_data.empty:
            st.info(T("No GSTR-2A entries. Go to Add 2A Entry tab to simulate supplier data."))
        else:
            total_itc = (st.session_state.gstr2a_data["CGST"].astype(float).sum()
                        + st.session_state.gstr2a_data["SGST"].astype(float).sum()
                )
            k1, k2, k3 = st.columns(3)
            k1.metric(T("Suppliers Filed"),     st.session_state.gstr2a_data['GSTIN'].nunique())
            k2.metric(T("Total Invoices (2A)"), len(st.session_state.gstr2a_data))
            k3.metric(T("ITC Available (2A)"),  fmt_inr(total_itc))
            disp = st.session_state.gstr2a_data.copy()
            for c in ["Taxable","CGST","SGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.download_button(T("Download GSTR-2A CSV"),
                data=st.session_state.gstr2a_data.to_csv(index=False).encode(),
                file_name=f"GSTR2A_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

    with tab2:
        if gstr2b_df.empty:
            st.info(T("GSTR-2B is generated after 2A data is available. Add entries in Add 2A Entry first."))
        else:
            itc_total = (gstr2b_df["CGST"].astype(float).sum() + gstr2b_df["SGST"].astype(float).sum()
)
            st.info(f"{T('GSTR-2B snapshot — Locked ITC claimable in GSTR-3B: ')}{fmt_inr(itc_total)}")
            disp = gstr2b_df.copy()
            for c in ["Taxable","CGST","SGST","Total"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.download_button(T("Download GSTR-2B CSV"),
                data=gstr2b_df.to_csv(index=False).encode(),
                file_name=f"GSTR2B_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

    with tab3:
        st.caption(T("Match your Purchase Register vs GSTR-2A to identify claimable ITC."))
        if p_df.empty:
            st.info(T("No purchase entries to reconcile."))
        elif recon_df.empty:
            st.info(T("Add 2A entries and purchase invoices to reconcile."))
        else:
            matched   = len(recon_df[recon_df["Status"] == "✅ Matched"])
            mismatch  = len(recon_df[recon_df["Status"] == "❌ Amount Mismatch"])
            not_in_2a = len(recon_df[recon_df["Status"] == "⚠️ Not in GSTR-2A"])
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(T("Total Invoices"), len(recon_df))
            k2.metric(T("Matched"),        matched)
            k3.metric(T("Mismatch"),       mismatch)
            k4.metric(T("Not in 2A"),      not_in_2a)
            disp = recon_df.copy()
            for c in ["Your CGST","2A CGST"]: disp[c] = disp[c].apply(fmt_inr)
            st.dataframe(disp, use_container_width=True, hide_index=True)
            st.markdown(f"""
            <div class="info-box" style="margin-top:0.75rem; font-size:0.82rem; line-height:1.8; color:var(--muted);">
                <b style="color:var(--text);">{T("Action Guide")}</b><br>
                <b style="color:var(--green);">✅ {T("Matched")}</b> — {T("Claim ITC in GSTR-3B Table 4.")}<br>
                <b style="color:var(--red);">❌ {T("Amount Mismatch")}</b> — {T("Contact supplier to amend GSTR-1, or reverse ITC.")}<br>
                <b style="color:var(--amber);">⚠️ {T("Not in 2A")}</b> — {T("Supplier hasn't filed. Follow up before claiming ITC.")}
            </div>""", unsafe_allow_html=True)
            st.download_button(T("Download Reconciliation CSV"),
                data=recon_df.to_csv(index=False).encode(),
                file_name=f"GSTR2A_Recon_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)


# ════════════════════════════════════════════════
# USER GUIDE
# ════════════════════════════════════════════════
elif page == "User Guide":
    hamburger_btn()
    lang  = st.session_state.get("lang", "English")
    is_kn = lang == "ಕನ್ನಡ"

    st.markdown(f'<div class="page-title">{"FinFlow ಮಾರ್ಗದರ್ಶಿ" if is_kn else "📖 User Guide"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{"ಈ ಅಪ್ಲಿಕೇಶನ್ ಅನ್ನು ಹೇಗೆ ಬಳಸಬೇಕು ಎಂಬ ಸಂಪೂರ್ಣ ಮಾಹಿತಿ" if is_kn else "Complete guide on how to use FinFlow — step by step"}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-label">{"ಅಪ್ಲಿಕೇಶನ್ ಕಾರ್ಯ ವಿಧಾನ" if is_kn else "How FinFlow Works"}</div>', unsafe_allow_html=True)

    flow_items_en = [
        ("🧾", "Invoice",   "Upload PDF/Image"),
        ("🤖", "OCR Reads", "AI extracts data"),
        ("🔀", "Auto Sort", "Purchase or Sales"),
        ("📊", "Dashboard", "Live GST total"),
        ("🏛️", "File GST",  "GSTR-1 / 3B ready"),
    ]
    flow_items_kn = [
        ("🧾", "ಇನ್ವಾಯ್ಸ್",       "PDF/ಫೋಟೋ ಅಪ್‌ಲೋಡ್"),
        ("🤖", "OCR ಓದುತ್ತದೆ",    "AI ಡೇಟಾ ತೆಗೆಯುತ್ತದೆ"),
        ("🔀", "ಸ್ವಯಂ ವಿಂಗಡಣೆ",  "ಖರೀದಿ ಅಥವಾ ಮಾರಾಟ"),
        ("📊", "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",   "ನೇರ GST ಒಟ್ಟು"),
        ("🏛️", "GST ಸಲ್ಲಿಸಿ",     "GSTR-1 / 3B ಸಿದ್ಧ"),
    ]
    flow_items = flow_items_kn if is_kn else flow_items_en
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
        ("1", "Upload Invoice",   "Go to Upload & Extract → Select your bill (PDF or photo) → Click Extract Data"),
        ("2", "Review & Confirm", "Check vendor name, amount, CGST/SGST → Fix errors → Click Confirm & Add to Register"),
        ("3", "Check Registers",  "Go to Purchase Register (bills you paid) or Sales Register (bills you raised)"),
        ("4", "See Dashboard",    "Dashboard shows total purchases, sales, and net GST owed to government"),
        ("5", "GST Reports",      "GSTR-1 for sales report · GSTR-3B for net tax → Download CSV → File on GST portal"),
        ("6", "Reconciliation",   "Check GSTIN validity · Identify unregistered dealers"),
    ]
    steps_kn = [
        ("1", "ಬಿಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",  "Upload & Extract ಗೆ ಹೋಗಿ → ನಿಮ್ಮ ಬಿಲ್ ಆಯ್ಕೆ ಮಾಡಿ → Extract Data ಕ್ಲಿಕ್ ಮಾಡಿ"),
        ("2", "ಪರಿಶೀಲಿಸಿ ದೃಢಪಡಿಸಿ",    "ಹೆಸರು, ಮೊತ್ತ, CGST/SGST ಸರಿಯಾಗಿದೆಯೇ ನೋಡಿ → Confirm ಕ್ಲಿಕ್ ಮಾಡಿ"),
        ("3", "ನೋಂದಣಿ ನೋಡಿ",          "Purchase Register ಅಥವಾ Sales Register ತೆರೆಯಿರಿ"),
        ("4", "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ನೋಡಿ",   "Dashboard ನಲ್ಲಿ ಒಟ್ಟು ಖರೀದಿ, ಮಾರಾಟ ಮತ್ತು ನಿವ್ವಳ GST ತಿಳಿಯುತ್ತದೆ"),
        ("5", "GST ವರದಿ",             "GSTR-1 (ಮಾರಾಟ ವರದಿ) ಅಥವಾ GSTR-3B → CSV ಡೌನ್‌ಲೋಡ್ → GST ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಸಲ್ಲಿಸಿ"),
        ("6", "ಹೊಂದಾಣಿಕೆ",           "GSTIN ಸರಿಯಾಗಿದೆಯೇ ಪರಿಶೀಲಿಸಿ · ಅನೋಂದಿತ ವ್ಯಾಪಾರಿಗಳನ್ನು ಗುರುತಿಸಿ"),
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
        with st.expander(f"❓ {q}"):
            st.markdown(f'<div style="color:var(--muted);font-size:0.88rem;line-height:1.7;padding:0.25rem 0;">{a}</div>', unsafe_allow_html=True)