import streamlit as st

# ------------------------------------------------------------------------------
# SET PAGE CONFIGURATION (optional)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Income Tax Calculator", layout="wide")

# ------------------------------------------------------------------------------
# DEFINE NAVIGATION OPTIONS & INITIALIZE CURRENT SECTION
# ------------------------------------------------------------------------------
nav_options = ["Salary Details", "Exemptions (Old Scheme)", "Results"]

# Read the current section from the URL query parameters using the new API.
params = st.query_params
if "section" in params and params["section"]:
    current_section = params["section"][0]
else:
    current_section = "Salary Details"

# Ensure the current section is valid.
if current_section not in nav_options:
    current_section = "Salary Details"
st.session_state.current_section = current_section

default_index = nav_options.index(st.session_state.current_section)

# Sidebar: Manual Navigation
nav = st.sidebar.radio(
    "Select Section",
    options=nav_options,
    index=default_index,
    key="nav_radio"
)
if nav != st.session_state.current_section:
    st.session_state.current_section = nav
    st.set_query_params(section=nav)

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
       
