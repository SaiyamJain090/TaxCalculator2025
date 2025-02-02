import streamlit as st

# ------------------------------------------------------------------------------
# CUSTOM CSS for Good Readability and Visual Appeal
# ------------------------------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
      background-color: #f5f5f5;
    }
    h1, h2, h3, h4, label, p {
      color: #003366 !important;
      font-family: "Helvetica", sans-serif;
    }
    .section {
      background-color: #ffffff;
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
      box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# TAX SLABS & STANDARD DEDUCTIONS
# ------------------------------------------------------------------------------
OLD_TAX_SLABS = [
    (0, 250000, 0),
    (250000, 500000, 5),
    (500000, 1000000, 20),
    (1000000, float('inf'), 30)
]
STANDARD_DEDUCTION_OLD = 50000

NEW_TAX_SLABS = [
    (0, 400000, 0),
    (400000, 800000, 5),
    (800000, 1200000, 10),
    (1200000, 1600000, 15),
    (1600000, 2000000, 20),
    (2000000, 2400000, 25),
    (2400000, float('inf'), 30)
]
STANDARD_DEDUCTION_NEW = 75000

def calculate_tax(income, slabs):
    """Calculate tax liability based on income and tax slabs."""
    tax = 0
    for lower, upper, rate in slabs:
        if income > lower:
            taxable = min(income, upper) - lower
            tax += taxable * rate / 100
        else:
            break
    return tax

# ==============================================================================
# SECTION 1: SALARY DETAILS
# ==============================================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Section 1: Salary Details")
st.subheader("Enter your salary details below:")

with st.form(key="salary_details"):
    annual_ctc = st.number_input("Total Annual CTC (₹)", min_value=0, value=600000, step=10000)
    bonus = st.number_input("Total Bonus (₹)", min_value=0, value=0, step=1000)
    total_income = annual_ctc + bonus
    st.write(f"**Total Income:** ₹{total_income:,.0f}")
    
    basic_mode = st.radio("Enter Basic Salary as:", ("Amount", "Percentage of Total Annual CTC"))
    if basic_mode == "Amount":
        basic_salary = st.number_input("Basic Salary (₹)", min_value=0, value=int(0.3 * total_income), step=1000)
    else:
        basic_pct = st.number_input("Basic Salary (%)", min_value=0, max_value=100, value=30, step=1)
        basic_salary = total_income * basic_pct / 100
    st.write(f"**Basic Salary:** ₹{basic_salary:,.0f}")
    
    hra_mode = st.radio("Enter HRA Received as:", ("Amount (Annual)", "Percentage of Basic Salary"))
    if hra_mode == "Amount (Annual)":
        hra_received = st.number_input("HRA Received (₹, Annual)", min_value=0, value=int(0.5 * basic_salary), step=1000)
    else:
        hra_pct = st.number_input("HRA (%) of Basic Salary", min_value=0, max_value=100, value=50, step=1)
        hra_received = basic_salary * hra_pct / 100
    st.write(f"**HRA Received (Annual):** ₹{hra_received:,.0f}")
    
    submitted_salary = st.form_submit_button("Next")
st.markdown("</div>", unsafe_allow_html=True)

if not submitted_salary:
    st.stop()  # Wait for user input in Section 1

# ==============================================================================
# SECTION 2: EXEMPTIONS FOR OLD TAX SCHEME
# ==============================================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Section 2: Exemptions for Old Tax Scheme")
st.markdown("*These inputs apply only if you are opting for the Old Tax Scheme.*")

with st.form(key="old_exemptions"):
    monthly_rent = st.number_input("Monthly Rent Paid (₹)", min_value=0, value=0, step=500)
    city_type = st.selectbox("City Type", ("Metro", "Non-Metro"))
    sec80c = st.number_input("Section 80C Deduction (₹)", min_value=0, value=150000, step=1000)
    home_loan = st.number_input("Home Loan Interest Deduction (₹)", min_value=0, value=0, step=1000)
    nps = st.number_input("NPS Deduction (₹)", min_value=0, value=0, step=1000)
    vol_pf = st.number_input("Voluntary PF Deduction (₹)", min_value=0, value=0, step=1000)
    other_deductions = st.number_input("Other Deductions (₹)", min_value=0, value=0, step=1000)
    submitted_exemptions = st.form_submit_button("Calculate Tax")
st.markdown("</div>", unsafe_allow_html=True)

if not submitted_exemptions:
    st.stop()  # Wait for Section 2 inputs

# ==============================================================================
# SECTION 3: TAX CALCULATION & SCHEME COMPARISON
# ==============================================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Section 3: Tax Calculation and Scheme Comparison")

# --- OLD TAX SCHEME CALCULATION ---
# Calculate HRA exemption:
annual_rent = monthly_rent * 12
excess_rent = max(annual_rent - (0.1 * basic_salary), 0)
if city_type == "Metro":
    city_limit = 0.5 * basic_salary
else:
    city_limit = 0.4 * basic_salary
hra_exemption = min(hra_received, excess_rent, city_limit)
st.write(f"**HRA Exemption (Old Scheme):** ₹{hra_exemption:,.0f}")

other_total_deductions = sec80c + home_loan + nps + vol_pf + other_deductions
total_deductions_old = STANDARD_DEDUCTION_OLD + hra_exemption + other_total_deductions
taxable_income_old = max(total_income - total_deductions_old, 0)
old_tax = calculate_tax(taxable_income_old, OLD_TAX_SLABS)
st.write(f"**Taxable Income (Old Scheme):** ₹{taxable_income_old:,.0f}")
st.write(f"**Tax Liability (Old Scheme):** ₹{old_tax:,.0f}")

# --- NEW TAX SCHEME CALCULATION ---
# In the New Scheme, if total income is below ₹12.75 LPA then tax is 0.
if total_income < 1275000:
    new_tax = 0
    taxable_income_new = total_income  # Not used since tax is 0.
else:
    taxable_income_new = max(total_income - STANDARD_DEDUCTION_NEW, 0)
    new_tax = calculate_tax(taxable_income_new, NEW_TAX_SLABS)
st.write(f"**Taxable Income (New Scheme):** ₹{taxable_income_new:,.0f}")
st.write(f"**Tax Liability (New Scheme):** ₹{new_tax:,.0f}")

# --- SCHEME COMPARISON ---
if old_tax < new_tax:
    better_scheme = "Old Tax Scheme"
elif new_tax < old_tax:
    better_scheme = "New Tax Scheme"
else:
    better_scheme = "Both schemes yield the same tax liability"

st.subheader("Which Scheme is Better?")
st.write(f"Based on your inputs, the **{better_scheme}** is better for you.")
st.markdown("</div>", unsafe_allow_html=True)

