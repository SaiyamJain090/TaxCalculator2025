import streamlit as st

# ------------------------------------------------------------------------------
# INITIAL SETUP & SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
if "nav_section" not in st.session_state:
    st.session_state.nav_section = "Salary Details"

st.sidebar.title("Navigation")
# The radio here both displays and allows manual switching.
nav = st.sidebar.radio(
    "Select Section",
    options=["Salary Details", "Exemptions (Old Scheme)", "Results"],
    key="nav_section"
)

# ------------------------------------------------------------------------------
# CUSTOM CSS: Black background, white text, styled sections, and result card
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
    h1, h2, h3, h4, label, p, .css-1d391kg {
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

# ------------------------------------------------------------------------------
# SECTION 1: SALARY DETAILS
# ------------------------------------------------------------------------------
if nav == "Salary Details":
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
        
        submitted_salary = st.form_submit_button("Save Salary Details")
        if submitted_salary:
            st.session_state["annual_ctc"] = annual_ctc
            st.session_state["bonus"] = bonus
            st.session_state["total_income"] = total_income
            st.session_state["basic_salary"] = basic_salary
            st.session_state["hra_received"] = hra_received
            st.success("Salary details saved!")
            # Advance automatically to the next section:
            st.session_state.nav_section = "Exemptions (Old Scheme)"
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()  # Stop so that only one section shows at a time

# ------------------------------------------------------------------------------
# SECTION 2: EXEMPTIONS FOR OLD TAX SCHEME
# ------------------------------------------------------------------------------
if nav == "Exemptions (Old Scheme)":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.header("Section 2: Exemptions for Old Tax Scheme")
    st.markdown("*These inputs apply only for the Old Tax Scheme calculation.*")
    
    with st.form(key="exemptions_form"):
        monthly_rent = st.number_input("Monthly Rent Paid (₹)", min_value=0, value=0, step=500)
        city_type = st.selectbox("City Type", ("Metro", "Non-Metro"))
        sec80c = st.number_input("Section 80C Ded
