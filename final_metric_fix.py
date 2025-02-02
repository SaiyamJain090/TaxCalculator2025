import streamlit as st

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Income Tax Comparison Calculator", layout="wide")

# ------------------------------------------------------------------------------
# HEADING & INSTRUCTIONS
# ------------------------------------------------------------------------------
st.title("Income Tax Comparison Calculator – (Old Scheme vs New Scheme 2025)")
st.markdown("""
**Instructions:**
- This tool helps you compare your tax liabilities under the Old and New tax schemes for the FY26
- Follow the steps on each page to enter your salary details and the relevant deductions/exemptions.
- **Note:** None of the data is saved or stored permanently. All inputs are used only for the duration of your session.
- /Prepared by - Saiyam Jain (Please reach out for any feedback)/
""")

# ------------------------------------------------------------------------------
# DEFINE NAVIGATION OPTIONS & INITIALIZE CURRENT SECTION
# ------------------------------------------------------------------------------
nav_options = ["Salary Details", "Exemptions (Old Scheme)", "Results"]

if "current_section" not in st.session_state:
    st.session_state.current_section = "Salary Details"

default_index = nav_options.index(st.session_state.current_section)

# Sidebar: Manual Navigation (updates session state)
nav = st.sidebar.radio(
    "Select Section",
    options=nav_options,
    index=default_index,
    key="nav_radio"
)
if nav != st.session_state.current_section:
    st.session_state.current_section = nav

# ------------------------------------------------------------------------------
# CUSTOM CSS FOR STYLING
# ------------------------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #000000;
}
body {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Helvetica', sans-serif;
}
h1, h2, h3, h4, label, p {
    color: #ffffff !important;
}
.section {
    background-color: #1a1a1a;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    box-shadow: 0px 4px 8px rgba(255, 255, 255, 0.1);
}
.stButton>button {
    background-color: #0056b3;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 16px;
}
.result-card {
    background: linear-gradient(135deg, #0056b3, #003366);
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4);
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

# =============================================================================
# PAGE FUNCTIONS
# =============================================================================

def show_salary_details():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.header("Section 1: Salary Details")
    st.subheader("Enter your salary details below:")
    with st.form(key="salary_form"):
        annual_ctc = st.number_input("Total Annual CTC (₹)", min_value=0, value=600000, step=10000)
        bonus = st.number_input("Total Bonus (₹)", min_value=0, value=0, step=1000)
        total_income = annual_ctc + bonus
        st.write(f"**Total Income:** ₹{total_income:,.0f}")
        
        basic_mode = st.radio("How would you like to enter Basic Salary?",
                              ("Enter Amount", "Percentage of Total Annual CTC"))
        if basic_mode == "Enter Amount":
            basic_salary = st.number_input("Basic Salary (₹)", min_value=0, value=int(0.3 * total_income), step=1000)
        else:
            basic_pct = st.number_input("Basic Salary (%)", min_value=0, max_value=100, value=30, step=1)
            basic_salary = total_income * basic_pct / 100
        st.write(f"**Basic Salary:** ₹{basic_salary:,.0f}")
        
        hra_mode = st.radio("How would you like to enter HRA Received?",
                            ("Enter Amount (Annual)", "Percentage of Basic Salary"))
        if hra_mode == "Enter Amount (Annual)":
            hra_received = st.number_input("HRA Received (₹, Annual)", min_value=0, value=int(0.5 * basic_salary), step=1000)
        else:
            hra_pct = st.number_input("HRA (%) of Basic Salary", min_value=0, max_value=100, value=50, step=1)
            hra_received = basic_salary * hra_pct / 100
        st.write(f"**HRA Received (Annual):** ₹{hra_received:,.0f}")
        
        save_salary = st.form_submit_button("Save Salary Details")
    
    if save_salary:
        st.session_state["annual_ctc"] = annual_ctc
        st.session_state["bonus"] = bonus
        st.session_state["total_income"] = total_income
        st.session_state["basic_salary"] = basic_salary
        st.session_state["hra_received"] = hra_received
        st.session_state.salary_saved = True
        st.success("Salary details saved!")
    
    if st.session_state.get("salary_saved", False):
        st.button("Next", on_click=lambda: st.session_state.update({"current_section": "Exemptions (Old Scheme)"}))
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_exemptions():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.header("Section 2: Exemptions for Old Tax Scheme")
    st.markdown("*These inputs apply only for the Old Tax Scheme calculation.*")
    with st.form(key="exemptions_form"):
        monthly_rent = st.number_input("Monthly Rent Paid (₹)", min_value=0, value=0, step=500)
        city_type = st.selectbox("City Type", ("Metro", "Non-Metro"))
        sec80c = st.number_input("Section 80C Deduction (₹)", min_value=0, value=150000, step=1000)
        home_loan = st.number_input("Home Loan Interest Deduction (₹)", min_value=0, value=0, step=1000)
        nps = st.number_input("NPS Deduction (₹)", min_value=0, value=0, step=1000)
        vol_pf = st.number_input("Voluntary PF Deduction (₹)", min_value=0, value=0, step=1000)
        other_deductions = st.number_input("Other Deductions (₹)", min_value=0, value=0, step=1000)
        save_exemptions = st.form_submit_button("Save Exemptions")
    
    if save_exemptions:
        st.session_state["monthly_rent"] = monthly_rent
        st.session_state["city_type"] = city_type
        st.session_state["sec80c"] = sec80c
        st.session_state["home_loan"] = home_loan
        st.session_state["nps"] = nps
        st.session_state["vol_pf"] = vol_pf
        st.session_state["other_deductions"] = other_deductions
        st.session_state.exemptions_saved = True
        st.success("Exemptions saved!")
    
    if st.session_state.get("exemptions_saved", False):
        st.button("Next", on_click=lambda: st.session_state.update({"current_section": "Results"}))
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_results():
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.header("Section 3: Tax Calculation and Scheme Comparison")
    
    if "total_income" not in st.session_state or "basic_salary" not in st.session_state:
        st.warning("Please fill in the Salary Details first!")
        return
    
    total_income = st.session_state["total_income"]
    basic_salary = st.session_state["basic_salary"]
    hra_received = st.session_state["hra_received"]
    
    monthly_rent = st.session_state.get("monthly_rent", 0)
    city_type = st.session_state.get("city_type", "Metro")
    annual_rent = monthly_rent * 12
    excess_rent = max(annual_rent - (0.1 * basic_salary), 0)
    city_limit = 0.5 * basic_salary if city_type == "Metro" else 0.4 * basic_salary
    hra_exemption = min(hra_received, excess_rent, city_limit)
    
    sec80c = st.session_state.get("sec80c", 0)
    home_loan = st.session_state.get("home_loan", 0)
    nps = st.session_state.get("nps", 0)
    vol_pf = st.session_state.get("vol_pf", 0)
    other_deductions = st.session_state.get("other_deductions", 0)
    other_total = sec80c + home_loan + nps + vol_pf + other_deductions
    
    total_deductions_old = STANDARD_DEDUCTION_OLD + hra_exemption + other_total
    taxable_income_old = max(total_income - total_deductions_old, 0)
    old_tax = calculate_tax(taxable_income_old, OLD_TAX_SLABS)
    
    if total_income < 1275000:
        new_tax = 0
        taxable_income_new = total_income
    else:
        taxable_income_new = max(total_income - STANDARD_DEDUCTION_NEW, 0)
        new_tax = calculate_tax(taxable_income_new, NEW_TAX_SLABS)
    
    st.subheader("Your Tax Calculation Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Old Tax Scheme")
        st.write(f"**Taxable Income:** ₹{taxable_income_old:,.0f}")
        st.write(f"**Tax Liability:** ₹{old_tax:,.0f}")
    with col2:
        st.markdown("#### New Tax Scheme")
        st.write(f"**Taxable Income:** ₹{taxable_income_new:,.0f}")
        st.write(f"**Tax Liability:** ₹{new_tax:,.0f}")
    
    if old_tax < new_tax:
        better = "Old Tax Scheme"
    elif new_tax < old_tax:
        better = "New Tax Scheme"
    else:
        better = "Both schemes yield the same tax liability"
    
    st.markdown(f"""
    <div class="result-card">
      <h2>Better Scheme: {better}</h2>
      <p>Based on your inputs, the <strong>{better}</strong> offers a lower tax liability.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# MAIN EXECUTION: DISPLAY THE CURRENT SECTION
# =============================================================================
if st.session_state.current_section == "Salary Details":
    show_salary_details()
elif st.session_state.current_section == "Exemptions (Old Scheme)":
    show_exemptions()
elif st.session_state.current_section == "Results":
    show_results()
