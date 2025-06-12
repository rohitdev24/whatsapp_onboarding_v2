import streamlit as st
import os
import zipfile
from datetime import datetime
import time

st.set_page_config(page_title="Onboarding App", layout="centered")

# Apply custom styling with animations
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .stApp {
            background-color: #121212;
            color: #e0e0e0;
        }
        .css-1d391kg, .css-1cpxqw2, .css-ffhzg2 {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
            transition: all 0.3s ease;
        }
        .css-1v3fvcr:hover, .css-1n76uvr:hover {
            background-color: #2c2c2c !important;
            transition: all 0.3s ease;
        }
        .css-1v3fvcr, .css-1n76uvr {
            background-color: #1e1e1e !important;
        }
    </style>
""", unsafe_allow_html=True)

# App logo and title
st.image("https://raw.githubusercontent.com/rohitdev24/whatsapp_onboarding_v2/main/logo.png", width=250)
with st.spinner("Loading form components..."):
    time.sleep(1)
    st.title("Client Onboarding Form")
    st.markdown("Contact us at **Contactus@sssdistributors.com**")

# Function to collect documents for an individual
def upload_docs(name, is_minor):
    with st.expander(f"Click to upload documents for {name}", expanded=True):
        st.subheader(f"Documents for {name}")
        docs = {}
        if not is_minor:
            docs['E-Aadhaar'] = st.file_uploader("E-Aadhaar (Masked PDF)", type=["pdf"], key=f"aadhaar_{name}")
            docs['PAN Card'] = st.file_uploader("PAN Card", type=["jpg", "jpeg", "png", "pdf"], key=f"pan_{name}")
            docs['Cancelled Cheque/Bank Statement'] = st.file_uploader("Cancelled Cheque or Bank Statement", key=f"cheque_{name}")
            docs['Photo'] = st.file_uploader("Photo", type=["jpg", "jpeg", "png"], key=f"photo_{name}")
            docs['Email'] = st.text_input("Email", key=f"email_{name}")
            docs['Phone'] = st.text_input("Phone Number", key=f"phone_{name}")
            docs['Mother Name'] = st.text_input("Mother's Name", key=f"mother_{name}")
            docs['Place of Birth'] = st.text_input("Place of Birth", key=f"birthplace_{name}")

            nominee_list = []
            num_nominees = st.slider(f"How many nominees for {name}?", min_value=1, max_value=3, value=1, key=f"nominee_count_{name}")
            for n in range(int(num_nominees)):
                with st.expander(f"Nominee {n+1} Details"):
                    nominee = {}
                    nominee['Name'] = st.text_input("Nominee Name", key=f"nominee_name_{name}_{n}")
                    nominee['Relation'] = st.text_input("Relation", key=f"nominee_relation_{name}_{n}")
                    nominee['PAN Card'] = st.file_uploader("Nominee PAN Card", key=f"nominee_pan_{name}_{n}")
                    nominee['Occupation'] = st.text_input("Occupation", key=f"nominee_occ_{name}_{n}")
                    nominee['Income'] = st.text_input("Income", key=f"nominee_income_{name}_{n}")
                    nominee_list.append(nominee)
            docs['Nominees'] = nominee_list

        else:
            docs['Birth Certificate'] = st.file_uploader("Birth Certificate", key=f"birthcert_{name}")
            guardian_list = []
            num_guardians = st.slider(f"How many guardians for {name}?", min_value=1, max_value=2, value=1, key=f"guardian_count_{name}")
            for g in range(int(num_guardians)):
                with st.expander(f"Guardian {g+1} Details"):
                    guardian = {}
                    guardian['Guardian PAN'] = st.file_uploader("Guardian PAN Card", key=f"guardian_pan_{name}_{g}")
                    guardian['Guardian Aadhaar'] = st.file_uploader("Guardian Aadhaar", key=f"guardian_aadhaar_{name}_{g}")
                    guardian['Guardian Bank Statement/Cheque'] = st.file_uploader("Guardian Bank Statement or Cancelled Cheque", key=f"guardian_bank_{name}_{g}")
                    guardian_list.append(guardian)
            docs['Guardians'] = guardian_list

        return docs

# Main form logic
with st.form("onboarding_form"):
    head_name = st.text_input("Family Head Name")
    head_age = st.number_input("Family Head Age", min_value=0, max_value=120)
    members_count = st.slider("How many family members want to invest?", min_value=0, max_value=10)
    members = []
    for i in range(int(members_count)):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Member {i+1} Name", key=f"name_{i}")
        with col2:
            age = st.number_input(f"Member {i+1} Age", min_value=0, max_value=120, key=f"age_{i}")
        members.append({"name": name, "age": age})
    submitted = st.form_submit_button("Submit")

if submitted:
    with st.spinner("Collecting and zipping documents..."):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = f"temp_{timestamp}"
        os.makedirs(base_dir, exist_ok=True)
        all_docs = {}
        for member in members:
            name = member['name']
            age = member['age']
            folder = os.path.join(base_dir, name.replace(" ", "_"))
            os.makedirs(folder, exist_ok=True)
            docs = upload_docs(name, is_minor=(age < 18))
            all_docs[name] = docs

            for key, file in docs.items():
                if isinstance(file, list):
                    for idx, subdict in enumerate(file):
                        for subkey, subfile in subdict.items():
                            if hasattr(subfile, 'read'):
                                ext = subfile.name.split('.')[-1]
                                with open(os.path.join(folder, f"{key}_{idx+1}_{subkey}.{ext}"), "wb") as f:
                                    f.write(subfile.read())
                elif isinstance(file, dict):
                    for nkey, nfile in file.items():
                        if hasattr(nfile, 'read'):
                            ext = nfile.name.split('.')[-1]
                            with open(os.path.join(folder, f"{nkey}.{ext}"), "wb") as f:
                                f.write(nfile.read())
                elif hasattr(file, 'read'):
                    ext = file.name.split('.')[-1]
                    with open(os.path.join(folder, f"{key}.{ext}"), "wb") as f:
                        f.write(file.read())

        zip_path = f"{head_name.replace(' ', '_')}_onboarding.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(base_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), base_dir))

    st.success(f"Documents collected and zipped into {zip_path}")

    st.markdown("### Next Steps")
    st.markdown("- You'll receive an AOF (Account Opening Form) shortly for confirmation.")
    st.markdown("- Post confirmation, approve the following emails from BSE StarMF:")
    st.markdown("1. **E-log**: After verifying AOF details")
    st.markdown("2. **Nominee Authentication")
    st.markdown("3. **E-Mandate**: Authorizes BSE to debit your account directly for future SIPs or lump sum investments.")
    st.info("The E-mandate sets a max transaction limit, ensuring secure investments through your account only.")
