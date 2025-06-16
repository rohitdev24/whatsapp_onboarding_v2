import streamlit as st
import os
import zipfile
from datetime import datetime
import base64
import shutil

st.set_page_config(page_title="✨ Onboarding Portal", layout="wide")

# ---- CSS for modern UI and horizontal radio tabs ----
st.markdown("""
    <style>
        /* ... [Your CSS unchanged for brevity] ... */
    </style>
""", unsafe_allow_html=True)

# --------- Clean Header (no logo, just title and contact) ----------
st.markdown("""
<div class="glass-header" style="user-select:none;">
    <span class="glass-header-title">✨ Onboarding Portal</span>
    <span class="glass-header-contact">Contact: <b>Contactus@sssdistributors.com</b></span>
</div>
""", unsafe_allow_html=True)

# --------- Sidebar progress ----------
with st.sidebar:
    st.markdown("<div class='glass-sidebar'>", unsafe_allow_html=True)
    st.image(
        "https://raw.githubusercontent.com/rohitdev24/whatsapp_onboarding_v2/main/logo.png",
        width=120
    )
    st.markdown("<div class='sidebar-title'>👨‍👩‍👧‍👦 Family Progress</div>", unsafe_allow_html=True)
    members = st.session_state.get('members', [])
    for idx, member in enumerate(members):
        name = member.get("name", f"Member {idx+1}")
        avatar_data = member.get("avatar_data")
        completed = member.get("is_complete", False)
        avatar_html = (
            f"<img src='data:image/png;base64,{avatar_data}' class='avatar'>" if avatar_data
            else f"<div class='avatar'></div>"
        )
        status = (f"<span class='checkmark'>&#10004;</span>" if completed 
            else "<span class='incomplete-dot'></span>")
        st.markdown(
            f"<div class='member-list-item'>{avatar_html}<span style='font-weight:500'>{name}</span> {status}</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# --------- Main Glass Card ----------
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("---")

    # -- Family Head Details --
    with st.form("family_form", clear_on_submit=False):
        cols = st.columns([2,1,1])
        with cols[0]:
            head_name = st.text_input("Primary Applicant Name", placeholder="Full name")
        with cols[1]:
            head_age = st.number_input("Primary Applicant Age", min_value=0, max_value=120, step=1)
        with cols[2]:
            members_count = st.number_input("How many members wish to invest?", min_value=1, max_value=10, step=1, value=1)
        family_submitted = st.form_submit_button("Confirm Family Info")

    # --------- Session state for members and active tab ----------
    if "members" not in st.session_state or family_submitted:
        st.session_state["members"] = [
            {"name": "", "age": 0, "avatar": None, "avatar_data": None, "is_complete": False}
            for _ in range(int(members_count))
        ]
    members = st.session_state["members"]

    tab_names = [m["name"] if m["name"] else f"👤 Member {i+1}" for i, m in enumerate(members)]
    if "active_tab" not in st.session_state or len(tab_names) != len(st.session_state.get("tab_names", [])):
        st.session_state.active_tab = 0
        st.session_state.tab_names = tab_names
    else:
        st.session_state.tab_names = tab_names

    # Radio as reliable tab navigation
    selected_tab = st.radio(
        "Select Member",
        options=range(len(tab_names)),
        format_func=lambda x: tab_names[x],
        index=st.session_state.active_tab,
        key="select_member_tab",
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.active_tab = selected_tab

    completed_forms = 0

    idx = selected_tab
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"Member {idx+1} Details")
    mcols = st.columns([2,1,1])
    with mcols[0]:
        name = st.text_input("Full Name", value=members[idx].get("name", ""), key=f"name_{idx}", help="Enter legal name as per ID")
    with mcols[1]:
        age = st.number_input("Age", min_value=0, max_value=120, value=members[idx].get("age", 0), key=f"age_{idx}")
    with mcols[2]:
        passport_photo = st.file_uploader("Passport Size Photo (optional for minors)", type=["png", "jpg", "jpeg"], key=f"photo_{idx}")
        avatar_data = None
        if passport_photo:
            avatar_data = base64.b64encode(passport_photo.getvalue()).decode()
            st.markdown(
                f"<img src='data:image/png;base64,{avatar_data}' class='avatar' style='width:64px;height:64px;margin-top:0.5em;'>",
                unsafe_allow_html=True
            )
    members[idx]['name'], members[idx]['age'] = name, age
    members[idx]['avatar'], members[idx]['avatar_data'] = passport_photo, avatar_data

    # -- Documents --
    docs = {}
    all_fields = True
    if name and age >= 0:
        if age < 18:
            docs['Birth Certificate'] = st.file_uploader("Birth Certificate", key=f"birthcert_{idx}")
            docs['Minor PAN Card (optional)'] = st.file_uploader("Minor PAN Card (optional)", type=["jpg", "jpeg", "png", "pdf"], key=f"minorpancard_{idx}")
            guardian_list = []
            num_guardians = st.number_input(f"Number of guardians?", min_value=1, max_value=2, value=1, key=f"guardian_count_{idx}")
            for g in range(int(num_guardians)):
                with st.expander(f"Guardian {g+1} Details"):
                    guardian = {}
                    guardian['Guardian PAN'] = st.file_uploader("Guardian PAN Card", key=f"guardian_pan_{idx}_{g}")
                    guardian['Guardian Aadhaar'] = st.file_uploader("Guardian Aadhaar", key=f"guardian_aadhaar_{idx}_{g}")
                    guardian['Guardian Bank Statement/Cheque'] = st.file_uploader("Guardian Bank Statement or Cancelled Cheque", key=f"guardian_bank_{idx}_{g}")
                    guardian_list.append(guardian)
            docs['Guardians'] = guardian_list
            all_fields &= bool(docs['Birth Certificate']) and num_guardians >= 1
            for guard in guardian_list:
                all_fields &= all(guard.get(x) for x in guard)
            # passport_photo and minor pan are both optional for minors
        else:
            docs['E-Aadhaar'] = st.file_uploader("E-Aadhaar (Masked PDF)", type=["pdf"], key=f"aadhaar_{idx}")
            docs['PAN Card'] = st.file_uploader("PAN Card", type=["jpg", "jpeg", "png", "pdf"], key=f"pan_{idx}")
            docs['Cancelled Cheque/Bank Statement'] = st.file_uploader("Cancelled Cheque or Bank Statement", key=f"cheque_{idx}")
            docs['Passport Size Photo'] = passport_photo
            docs['Email'] = st.text_input("Email", key=f"email_{idx}", value=members[idx].get("email", ""))
            docs['Phone'] = st.text_input("Phone Number", key=f"phone_{idx}", value=members[idx].get("phone", ""))
            docs['Mother Name'] = st.text_input("Mother's Name", key=f"mother_{idx}", value=members[idx].get("mother", ""))
            docs['Place of Birth'] = st.text_input("Place of Birth", key=f"birthplace_{idx}", value=members[idx].get("birthplace", ""))
            nominee_list = []
            num_nominees = st.number_input(f"Number of nominees?", min_value=1, max_value=3, value=1, key=f"nominee_count_{idx}")
            for n in range(int(num_nominees)):
                with st.expander(f"Nominee {n+1} Details"):
                    nominee = {}
                    nominee['Name'] = st.text_input("Nominee Name", key=f"nominee_name_{idx}_{n}")
                    nominee['Relation'] = st.text_input("Relation", key=f"nominee_relation_{idx}_{n}")
                    nominee['PAN Card'] = st.file_uploader("Nominee PAN Card", key=f"nominee_pan_{idx}_{n}")
                    nominee['Occupation'] = st.text_input("Occupation", key=f"nominee_occ_{idx}_{n}")
                    nominee['Income'] = st.text_input("Income", key=f"nominee_income_{idx}_{n}")
                    nominee_list.append(nominee)
            docs['Nominees'] = nominee_list
            all_fields &= all([
                docs['E-Aadhaar'], docs['PAN Card'], docs['Cancelled Cheque/Bank Statement'],
                docs['Email'], docs['Phone'], docs['Mother Name'], docs['Place of Birth'], passport_photo
            ])
            for nm in nominee_list:
                all_fields &= all(nm.get(x) for x in nm)
    else:
        all_fields = False

    members[idx]['docs'] = docs
    members[idx]['is_complete'] = all_fields

    # -- Progress calculation --
    completed_forms = sum(1 for m in members if m.get("is_complete"))

    st.markdown("</div>", unsafe_allow_html=True)

    # -- Animated Progress Bar & Label --
    st.markdown("---")
    st.markdown("<span class='progress-label'>Form Completion</span>", unsafe_allow_html=True)
    percent = completed_forms / max(1, len(members))
    st.markdown(
        f"<div class='animated-progress'><div class='animated-progress-bar' style='width:{int(percent*100)}%'></div></div>",
        unsafe_allow_html=True
    )
    st.markdown(f"<span style='color:#b8e9ff;font-size:1.04em;'>{completed_forms} of {len(members)} complete</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -- Sticky Footer Submission Bar --
if members:
    st.markdown(
        f"""
        <div class='sticky-footer'>
            <div class='footer-center'>
                {"<span style='color:#baffb8;font-size:1.1em;font-weight:700'>All members complete! Ready to submit.</span>"
                 if completed_forms == len(members) else '<span style="color:#e7aeee">Please complete all member details and uploads.</span>'}
                <br>
                """,
        unsafe_allow_html=True
    )
    # Only enable if all members complete
    if completed_forms == len(members):
        if st.button("🚀 Submit & Download All Documents"):
            with st.spinner("Collecting and zipping documents..."):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_dir = f"onboarding_{timestamp}"
                os.makedirs(base_dir, exist_ok=True)
                for idx2, member in enumerate(members):
                    name = member['name']
                    folder = os.path.join(base_dir, name.replace(" ", "_"))
                    os.makedirs(folder, exist_ok=True)
                    # Save passport photo if any
                    if member.get("avatar"):
                        ext = member['avatar'].name.split('.')[-1]
                        with open(os.path.join(folder, f"passport_photo.{ext}"), "wb") as f:
                            f.write(member['avatar'].getvalue())
                    docs = member.get('docs', {})
                    for key, file in docs.items():
                        if isinstance(file, list):  # Nominees or Guardians
                            for idx3, subdict in enumerate(file):
                                for subkey, subfile in subdict.items():
                                    if hasattr(subfile, 'getvalue'):
                                        ext = subfile.name.split('.')[-1]
                                        fname = f"{key}_{idx3+1}_{subkey.replace(' ', '_')}.{ext}"
                                        with open(os.path.join(folder, fname), "wb") as f:
                                            f.write(subfile.getvalue())
                        elif hasattr(file, 'getvalue') and key not in ['Passport Size Photo', 'Minor PAN Card (optional)']:
                            ext = file.name.split('.')[-1]
                            fname = f"{key.replace(' ', '_')}.{ext}"
                            with open(os.path.join(folder, fname), "wb") as f:
                                f.write(file.getvalue())
                        elif key == 'Minor PAN Card (optional)' and hasattr(file, 'getvalue'):
                            ext = file.name.split('.')[-1]
                            fname = f"minor_pan_card.{ext}"
                            with open(os.path.join(folder, fname), "wb") as f:
                                f.write(file.getvalue())
                zip_path = f"{head_name.replace(' ', '_')}_onboarding.zip"
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for root, _, files in os.walk(base_dir):
                        for file in files:
                            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), base_dir))
                st.success(f"Documents collected and zipped into {zip_path}")
                with open(zip_path, 'rb') as f:
                    st.download_button("⬇️ Download All Documents (.zip)", f, file_name=zip_path, mime='application/zip')
                # Optionally clean up temp files/folders after download button
                shutil.rmtree(base_dir, ignore_errors=True)
                #os.remove(zip_path)  # Uncomment if you want to remove zip after download (user may download again if commented)
            st.markdown("""
                ### Next Steps
                - You'll receive an AOF (Account Opening Form) shortly for confirmation.
                - Post confirmation, approve the following emails from BSE StarMF:
                    1. **E-log**: After verifying AOF details
                    2. **Nominee Authentication**
                    3. **E-Mandate** <span class="tooltip-wrap"><span class="tooltip-icon">ℹ️</span>
                        <span class="tooltip-box">
                            This mandate authorizes BSE Star MF to debit funds exclusively from your registered bank account for investment purposes.<br>
                            The maximum transaction limit specified ensures that only you can initiate investments in your name.<br>
                            This e-mandate will apply to all SIPs and lump sum transactions, and serves as a secure fallback should internet banking be temporarily unavailable.
                        </span>
                    </span>: Authorizes BSE to debit your account for future SIPs or lump sum investments.
                """, unsafe_allow_html=True)
            st.info("The e-mandate provides a secure, single point of authorization for all your mutual fund investments through BSE Star MF.")
    st.markdown("</div></div>", unsafe_allow_html=True)
