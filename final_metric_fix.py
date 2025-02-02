import streamlit as st

# =============================================================================
# INITIAL SETUP: Define Tax Slabs, Deductions, and Helper Function
# =============================================================================

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
    tax = 0
    for lower, upper, rate in slabs:
        if income > lower:
            taxable = min(income, upper) - lower
            tax += taxable * (rate / 100)
        else:
            break
    return tax

# =============================================================================
# SETUP SESSION STATE
# =============================================================================
if 'step' not in st.session_state:
    st.session_state.step = 1

# =============================================================================
# CUSTOM CSS for Basic Styling
# =============================================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .header, h2, h3, h4 {
        color: #000000 !important;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================================================================
# STEP 1: Select Current Tax Scheme
# =============================================================================
def render_step1():
    st.markdown('<p class="header">Income Tax Comparison Calculator</p>', unsafe_allow_html=True)
    st.write("**Step 1:** Please select the tax scheme you are currently using.")
    with st.form("step1_form"):
        scheme = st.radio("Which tax scheme are you currently using?", ("Old Tax Scheme", "New Tax Scheme"))
        submitted = st.form_submit_button("Next")
        if submitted:
            st.session_state.current_scheme = scheme
            st.session_state.step = 2
            st.experimental_rerun()

# =============================================================================
# STEP 2: Enter Annual Income Details
# =============================================================================
def render_step2():
    st.markdown('<p class="header">Income Details</p>', unsafe_allow_html=True)
    st.write("**Step 2:** Enter your Annual CTC and Bonus.")
    with st.form("step2_form"):
        ctc = st.number_input("Annual CTC (₹)", min_value=100000, value=600000, step=50000)
        bonus = st.number_input("Bonus (₹)", min_value=0, value=0, step=5000)
        submitted = st.form_submit_button("Next")
        if submitted:
            st.session_state.ctc = ctc
            st.session_state.bonus = bonus
            st.session_state.total_income = ctc + bonus
            st.session_state.step = 3
            st.experimental_rerun()

# =============================================================================
# STEP 3: Enter Basic Salary and (if applicable) HRA Details
# =============================================================================
def render_step3():
    st.markdown('<p class="header">Salary & HRA Details</p>', unsafe_allow_html=True)
    st.write("**Step 3:** Enter your Basic Salary details. (If you are on the Old Tax Scheme, please also provide your HRA details.)")
    with st.form("step3_form"):
        # Basic Salary
        basic_mode = st.radio("Provide Basic Salary as:", ["Percentage", "Amount"], index=0)
        if basic_mode == "Percentage":
            basic_pct = st.number_input("Basic Salary (%)", min_value=10, max_value=50, value=30, step=1)
            basic_salary = (basic_pct / 100) * st.session_state.total_income
        else:
            basic_salary = st.number_input("Basic Salary (₹)", min_value=10000, value=int(0.3 * st.session_state.total_income), step=1000)
        st.session_state.basic_salary = basic_salary

        # HRA details: Only applicable if current scheme is Old
        if st.session_state.current_scheme == "Old Tax Scheme":
            st.write("### HRA Details (Old Tax Scheme)")
            hra_mode = st.radio("Provide HRA Received as:", ["Percentage of Basic", "Fixed Amount"], key="hra_mode")
            if hra_mode == "Percentage of Basic":
                hra_pct = st.number_input("HRA (% of Basic Salary)", min_value=0, max_value=100, value=50, step=1, key="hra_pct")
                hra_received = (hra_pct / 100) * basic_salary
            else:
                # Ask if the fixed amount is monthly or annual
                fixed_period = st.radio("Is the HRA amount provided Monthly or Annual?", ["Monthly", "Annual"], key="fixed_period")
                fixed_amount = st.number_input("HRA Received (₹)", min_value=0, value=int(0.5 * basic_salary), step=1000, key="fixed_amount")
                if fixed_period == "Monthly":
                    hra_received = fixed_amount * 12
                else:
                    hra_received = fixed_amount
            st.session_state.hra_received = hra_received

            # Ask for monthly rent and city type (for computing HRA exemption)
            monthly_rent = st.number_input("Monthly Rent Paid (₹)", min_value=0, value=0, step=500, key="monthly_rent")
            st.session_state.monthly_rent = monthly_rent
            city_type = st.selectbox("City Type", ["Metro", "Non-Metro"], key="city_type")
            st.session_state.city_type = city_type

        submitted = st.form_submit_button("Next")
        if submitted:
            # For New scheme, set defaults for HRA-related fields.
            if st.session_state.current_scheme == "New Tax Scheme":
                st.session_state.hra_received = 0
                st.session_state.monthly_rent = 0
                st.session_state.city_type = ""
            # Next step: if Old scheme, proceed to deductions; else, skip to summary.
            if st.session_state.current_scheme == "Old Tax Scheme":
                st.session_state.step = 4
            else:
                st.session_state.step = 5
            st.experimental_rerun()

# =============================================================================
# STEP 4: Enter Other Deductions (Only for Old Tax Scheme)
# =============================================================================
def render_step4():
    st.markdown('<p class="header">Other Deductions</p>', unsafe_allow_html=True)
    st.write("**Step 4:** Enter your other deductions. (This step is only applicable for the Old Tax Scheme.)")
    with st.form("step4_form"):
        sec80c = st.number_input("Section 80C Deduction (₹, max 1.5L)", min_value=0, max_value=150000, value=150000, step=10000)
        sec80d = st.number_input("Section 80D (Insurance) Deduction (₹)", min_value=0, max_value=100000, value=50000, step=5000)
        home_loan = st.number_input("Home Loan Interest Deduction (₹, max 2L)", min_value=0, max_value=200000, value=0, step=5000)
        other_ded = st.number_input("Other Deductions (₹)", min_value=0, value=0, step=5000)
        submitted = st.form_submit_button("Next")
        if submitted:
            st.session_state.sec80c = sec80c
            st.session_state.sec80d = sec80d
            st.session_state.home_loan = home_loan
            st.session_state.other_ded = other_ded
            st.session_state.step = 5
            st.experimental_rerun()

# =============================================================================
# STEP 5: Calculate and Show Final Result & Summary
# =============================================================================
def render_step5():
    st.markdown('<p class="header">Tax Calculation Summary</p>', unsafe_allow_html=True)
    
    # Retrieve stored values
    total_income = st.session_state.total_income
    basic_salary = st.session_state.basic_salary
    current_scheme = st.session_state.current_scheme

    # ---- New Tax Scheme Calculation ----
    taxable_income_new = max(total_income - STANDARD_DEDUCTION_NEW, 0)
    tax_new = calculate_tax(taxable_income_new, NEW_TAX_SLABS)

    # ---- Old Tax Scheme Calculation ----
    if current_scheme == "Old Tax Scheme":
        # HRA Exemption Calculation
        hra_received = st.session_state.hra_received
        monthly_rent = st.session_state.monthly_rent
        city_type = st.session_state.city_type
        annual_rent = monthly_rent * 12
        excess_rent = max(annual_rent - (0.1 * basic_salary), 0)
        city_limit = 0.5 * basic_salary if city_type == "Metro" else 0.4 * basic_salary
        hra_exemption = min(hra_received, excess_rent, city_limit)
    else:
        hra_exemption = 0

    if current_scheme == "Old Tax Scheme":
        sec80c = st.session_state.sec80c
        sec80d = st.session_state.sec80d
        home_loan = st.session_state.home_loan
        other_ded = st.session_state.other_ded
        total_deductions_old = STANDARD_DEDUCTION_OLD + sec80c + sec80d + home_loan + other_ded + hra_exemption
        taxable_income_old = max(total_income - total_deductions_old, 0)
        tax_old = calculate_tax(taxable_income_old, OLD_TAX_SLABS)
    else:
        taxable_income_old = 0
        tax_old = 0

    # Determine which scheme is current and which is the alternative
    if current_scheme == "Old Tax Scheme":
        current_taxable = taxable_income_old
        current_tax = tax_old
        alt_scheme = "New Tax Scheme"
        alt_taxable = taxable_income_new
        alt_tax = tax_new
    else:
        current_taxable = taxable_income_new
        current_tax = tax_new
        alt_scheme = "Old Tax Scheme"
        alt_taxable = taxable_income_old
        alt_tax = tax_old

    # ---- Display Summary ----
    st.write("### Summary of Your Details")
    st.write(f"**Total Income:** ₹{total_income:,.0f}")
    st.write(f"**Basic Salary:** ₹{basic_salary:,.0f}")
    if current_scheme == "Old Tax Scheme":
        st.write("**HRA Breakdown (Annual Figures):**")
        st.write(f"- HRA Received: ₹{st.session_state.hra_received:,.0f}")
        st.write(f"- Excess Rent (Annual Rent - 10% of Basic): ₹{excess_rent:,.0f}")
        st.write(f"- City Limit: ₹{city_limit:,.0f}")
        st.write(f"**HRA Exemption Claimed:** ₹{hra_exemption:,.0f}")
        st.write("**Other Deductions:**")
        st.write(f"- Section 80C: ₹{sec80c:,.0f}")
        st.write(f"- Section 80D: ₹{sec80d:,.0f}")
        st.write(f"- Home Loan Interest: ₹{home_loan:,.0f}")
        st.write(f"- Other Deductions: ₹{other_ded:,.0f}")

    st.write("### Tax Liability Comparison")
    col_current, col_alt = st.columns(2)
    with col_current:
        st.markdown(f"#### {current_scheme} (Your Current Scheme)")
        st.metric("Taxable Income", f"₹{current_taxable:,.0f}")
        st.metric("Tax Liability", f"₹{current_tax:,.0f}")
    with col_alt:
        st.markdown(f"#### {alt_scheme} (Alternative Scheme)")
        st.metric("Taxable Income", f"₹{alt_taxable:,.0f}")
        st.metric("Tax Liability", f"₹{alt_tax:,.0f}")

    if st.button("Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# =============================================================================
# MAIN FLOW: Render the appropriate step
# =============================================================================
if st.session_state.step == 1:
    render_step1()
elif st.session_state.step == 2:
    render_step2()
elif st.session_state.step == 3:
    render_step3()
elif st.session_state.step == 4:
    render_step4()
elif st.session_state.step == 5:
    render_step5()
