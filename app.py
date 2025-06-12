import streamlit as st
import os
import zipfile
from datetime import datetime

st.set_page_config(page_title="Onboarding App", layout="centered")

# Styling
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #3C3C3C;
        border-radius: 8px;
    }
    .stButton > button {
        background-color: #3C3C3C;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 10px;
        font-weight: bold;
    }
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# App UI
st.image("https://via.placeholder.com/250x80.png?text=SSS+Distributors+Logo", use_column_width=False)
st.title("SSS Distributors Pvt Ltd")
st.subheader("WhatsApp Client Onboarding")
st.markdown("---")

st.markdown("**How many family members want to invest (excluding the family head)?**")
members_count = st.number_input("Enter number of members", min_value=0, step=1)

family_head_name = st.text_input("Name of Family Head")
family_head_age = st.number_input("Age of Family Head", min_value=0, max_value=120, step=1)

member_details = []

for i in range(int(members_count)):
    with st.expander(f"Enter details for Family Member {i+1}"):
        name = st.text_input(f"Name of Member {i+1}", key=f"name_{i}")
        age = st.number_input(f"Age of {name}", min_value=0, max_value=120, step=1, key=f"age_{i}")
        member_details.append({"name": name, "age": age})

if st.button("Next"):
    st.markdown("---")
    st.markdown("### Document Upload")

    def upload_docs(label):
        st.markdown(f"**{label}**")
        aadhaar = st.file_uploader("E-Aadhaar (Masked PDF)", type="pdf", key=f"aadhaar_{label}")
        pan = st.file_uploader("PAN Card", type=["png", "jpg", "jpeg", "pdf"], key=f"pan_{label}")
        bank = st.file_uploader("Cancelled Cheque/Bank Statement", type=["png", "jpg", "jpeg", "pdf"], key=f"bank_{label}")
        photo = st.file_uploader("Photo", type=["png", "jpg", "jpeg"], key=f"photo_{label}")
        email = st.text_input("Email", key=f"email_{label}")
        phone = st.text_input("Phone Number", key=f"phone_{label}")
        mother = st.text_input("Mother's Name", key=f"mother_{label}")
        nominee = st.text_area("Nominee Details (Name, Relation, PAN, Occupation, Income)", key=f"nominee_{label}")
        pob = st.text_input("Place of Birth", key=f"pob_{label}")

    def upload_minor_docs(label):
        st.markdown(f"**{label} (Minor)**")
        bc = st.file_uploader("Birth Certificate", type="pdf", key=f"bc_{label}")
        g_name = st.text_input("Guardian Name", key=f"gname_{label}")
        g_pan = st.file_uploader("Guardian PAN Card", type="pdf", key=f"gpan_{label}")
        g_aadhaar = st.file_uploader("Guardian Aadhaar", type="pdf", key=f"gaadhaar_{label}")
        g_bank = st.file_uploader("Guardian Bank Statement/Cancelled Cheque", type="pdf", key=f"gbank_{label}")

    st.subheader(f"Documents for {family_head_name} (Family Head)")
    if family_head_age >= 18:
        upload_docs(family_head_name)
    else:
        upload_minor_docs(family_head_name)

    for i, member in enumerate(member_details):
        st.subheader(f"Documents for {member['name']}")
        if member['age'] >= 18:
            upload_docs(member['name'])
        else:
            upload_minor_docs(member['name'])

    st.markdown("---")
    st.markdown("### Important Notes")
    st.markdown("""
    **E-Mandate Explanation:**  
    You will receive an email for e-mandate approval. This is an agreement between you and BSE Star MF that ensures money can only go from your account to BSE and can only be invested in your name. The amount shown is just the maximum transaction limit — this mandate will be used for all your SIPs and lump sum investments if internet banking isn't available.
    """)

    st.markdown("---")
    st.markdown("Contact us at: [Contactus@sssdistributors.com](mailto:Contactus@sssdistributors.com)")
