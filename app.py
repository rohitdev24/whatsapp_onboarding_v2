
import streamlit as st
import os
import zipfile
from PIL import Image
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Onboarding App", page_icon="📄")
st.image("logo.png", width=200)
st.markdown("### Welcome to SSS Distributors Onboarding")
st.markdown("📧 Contact us at [Contactus@sssdistributors.com](mailto:Contactus@sssdistributors.com)")
st.write("---")

num_members = st.number_input("How many immediate family members want to invest?", min_value=1, step=1)
family_head = st.text_input("Name of Family Head")
family_zip = f"{family_head.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"

members = []

for i in range(num_members):
    st.subheader(f"Member {i+1} Details")
    name = st.text_input(f"Name of Member {i+1}", key=f"name_{i}")
    age = st.number_input(f"Age of {name or f'Member {i+1}'}", min_value=0, key=f"age_{i}")
    folder_name = name.replace(" ", "_") if name else f"Member_{i+1}"

    files = []
    if age >= 18:
        files.append(st.file_uploader("E-Aadhaar (Masked PDF)", key=f"aadhaar_{i}"))
        files.append(st.file_uploader("PAN Card", key=f"pan_{i}"))
        files.append(st.file_uploader("Cancelled Cheque / Bank Statement", key=f"cheque_{i}"))
        files.append(st.file_uploader("Photo", type=["jpg", "jpeg", "png"], key=f"photo_{i}"))
        st.text_input("Email", key=f"email_{i}")
        st.text_input("Phone No.", key=f"phone_{i}")
        st.text_input("Mother's Name", key=f"mother_{i}")
        st.text_input("Place of Birth", key=f"birthplace_{i}")
        st.text_input("Nominee Name", key=f"nominee_name_{i}")
        st.text_input("Nominee Relation", key=f"nominee_rel_{i}")
        st.text_input("Nominee PAN", key=f"nominee_pan_{i}")
        st.text_input("Nominee Occupation", key=f"nominee_occ_{i}")
    else:
        files.append(st.file_uploader("Birth Certificate", key=f"birth_{i}"))
        files.append(st.file_uploader("Guardian's PAN", key=f"g_pan_{i}"))
        files.append(st.file_uploader("Guardian's Aadhaar", key=f"g_adhar_{i}"))
        files.append(st.file_uploader("Guardian's Bank Statement / Cheque", key=f"g_cheque_{i}"))

    members.append((folder_name, files))

if st.button("Create ZIP"):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for folder, files in members:
            for file in files:
                if file is not None:
                    zipf.writestr(f"{folder}/{file.name}", file.read())
    st.success("ZIP file created!")
    st.download_button(label="Download ZIP", data=zip_buffer.getvalue(), file_name=family_zip, mime="application/zip")
