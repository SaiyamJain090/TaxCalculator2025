
import streamlit as st
import pandas as pd

# Fully fixed CSS with proper contrast, heading visibility, and button fixes
st.markdown(
    '''
    <style>
    /* Background color */
    .stApp {
        background-color: #f5f5f5;
    }
    /* Headings (Black) */
    .header, h2, h3, h4 {
        color: #000000 !important;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* Section Styling */
    .section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    /* Ensure all labels and text are visible */
    div[data-testid="stMarkdownContainer"] p, label {
        color: #003366 !important;  /* Dark Blue */
        font-weight: bold !important;
    }
    /* Fix radio button text color */
    div[data-testid="stRadio"] label {
        color: #003366 !important;
        font-weight: bold !important;
    }
    /* Fix button styling */
    .stButton > button {
        background-color: #0056b3 !important;
        color: white !important;
        font-size: 1em !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        border: 2px solid #003366 !important;
    }
    /* Ensure results and metric text are dark and bold */
    .metric, .stMetricValue {
        font-size: 1.5em !important;
        font-weight: bold !important;
        color: #003366 !important;
    }
    /* Remove unwanted white bar (if it is an input field) */
    div[data-testid="stTextInput"] input {
        display: none !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# Tax Slabs and Deductions
OLD_TAX_SLABS = [(0, 250000, 0), (250000, 500000, 5), (500000, 1000000, 20), (1000000, float('inf'), 30)]
STANDARD_DEDUCTION_OLD = 50000

NEW_TAX_SLABS = [(0, 400000, 0), (400000, 800000, 5), (800000, 1200000, 10),
                 (1200000, 1600000, 15), (1600000, 2000000, 20), (2000000, 2400000, 25), (2400000, float('inf'), 30)]
STANDARD_DEDUCTION_NEW = 75000

# Tax Calculation Function
def calculate_tax(income, slabs):
    tax = 0
    for lower, upper, rate in slabs:
        if income > lower:
            taxable = min(income, upper) - lower
            tax += taxable * (rate / 100)
        else:
            break
    return tax

# App Header
st.markdown('<p class="header">Income Tax Comparison Calculator</p>', unsafe_allow_html=True)
st.write("This tool helps you compare tax liabilities under the **Old vs. New Tax Regime**.")

# Scheme Selection
current_scheme = st.radio("Which tax scheme are you currently using?", ("Old Tax Scheme", "New Tax Scheme"))

st.markdown('<div class="section">', unsafe_allow_html=True)

# Input Form
with st.form("tax_form"):
    st.subheader("Income Details")
    col1, col2 = st.columns(2)
    with col1:
        ctc = st.number_input("Annual CTC (₹)", min_value=100000, value=600000, step=50000)
    with col2:
        bonus = st.number_input("Bonus (₹)", min_value=0, value=0, step=5000)
    total_income = ctc + bonus

    st.write("### Basic Salary Details")
    basic_mode = st.radio("Provide Basic Salary as:", ["Percentage", "Amount"], index=0)
    if basic_mode == "Percentage":
        basic_pct = st.number_input("Basic Salary (%)", min_value=10, max_value=50, value=30, step=1)
        basic_salary = (basic_pct / 100) * total_income
    else:
        basic_salary = st.number_input("Basic Salary (₹)", min_value=10000, value=int(0.3 * total_income), step=1000)

    st.write("### HRA Details")
    hra_mode = st.radio("Provide HRA as:", ["Percentage of Basic", "Fixed Amount"], index=0)
    if hra_mode == "Percentage of Basic":
        hra_pct = st.number_input("HRA (% of Basic Salary)", min_value=0, max_value=100, value=50, step=1)
        hra_received = (hra_pct / 100) * basic_salary
    else:
        hra_received = st.number_input("HRA Received (₹)", min_value=0, value=int(0.5 * basic_salary), step=1000)

    rent_paid = st.number_input("Rent Paid (₹)", min_value=0, value=0, step=1000)
    city_type = st.selectbox("City Type", ["Metro", "Non-Metro"])

    st.write("### Other Deductions (Only applicable for Old Tax Scheme)")
    sec80c = st.number_input("Section 80C Deduction (₹, max 1.5L)", min_value=0, max_value=150000, value=150000, step=10000)
    sec80d = st.number_input("Section 80D (Insurance) Deduction (₹)", min_value=0, max_value=100000, value=50000, step=5000)
    home_loan = st.number_input("Home Loan Interest Deduction (₹, max 2L)", min_value=0, max_value=200000, value=0, step=5000)
    other_ded = st.number_input("Other Deductions (₹)", min_value=0, value=0, step=5000)

    submitted = st.form_submit_button("Calculate Tax")

st.markdown('</div>', unsafe_allow_html=True)

if submitted:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("Calculation Results")
    
    # HRA Exemption Calculation
    excess_rent = max(rent_paid - (0.1 * basic_salary), 0)
    city_limit = 0.5 * basic_salary if city_type == "Metro" else 0.4 * basic_salary
    hra_exemption = min(hra_received, excess_rent, city_limit)

    # Old Regime Tax Calculation
    total_deductions_old = STANDARD_DEDUCTION_OLD + sec80c + sec80d + home_loan + other_ded + hra_exemption
    taxable_income_old = max(total_income - total_deductions_old, 0)
    tax_old = calculate_tax(taxable_income_old, OLD_TAX_SLABS)

    # New Regime Tax Calculation
    taxable_income_new = max(total_income - STANDARD_DEDUCTION_NEW, 0)
    tax_new = calculate_tax(taxable_income_new, NEW_TAX_SLABS)

    # Display Side-by-Side Results
    col_old, col_new = st.columns(2)
    with col_old:
        st.markdown("### Old Tax Scheme")
        st.metric("Taxable Income", "₹{:,.0f}".format(taxable_income_old))
        st.metric("Tax Liability", "₹{:,.0f}".format(tax_old))
    with col_new:
        st.markdown("### New Tax Scheme")
        st.metric("Taxable Income", "₹{:,.0f}".format(taxable_income_new))
        st.metric("Tax Liability", "₹{:,.0f}".format(tax_new))

    # Recommendation
    st.markdown("---")
    if tax_old < tax_new:
        st.success("✅ Based on the details provided, the **Old Tax Scheme** is better for you!")
    elif tax_old > tax_new:
        st.success("✅ Based on the details provided, the **New Tax Scheme** is better for you!")
    else:
        st.info("⚖️ Both schemes result in the same tax liability.")
