import streamlit as st
import os
import zipfile
from datetime import datetime
import base64

st.set_page_config(page_title="✨ Onboarding Portal", layout="wide")

# -- Custom CSS for full theme (no top margin, glassmorphism, gradients, animation) --
st.markdown("""
    <style>
        html, body, .stApp {
            background: linear-gradient(135deg, #100c2a 0%, #3a2b7c 100%) !important;
            color: #f0f0fa;
            padding-top: 0px !important;
            margin-top: 0px !important;
        }
        .glass-card {
            background: rgba(34, 34, 51, 0.69);
            border-radius: 20px;
            box-shadow: 0 8px 40px #8775e040, 0 1.5px 12px #00000033;
            backdrop-filter: blur(12px);
            padding: 2.2rem 2rem 1.5rem 2rem;
            margin-bottom: 2rem;
            border: 1.5px solid #5233e440;
        }
        .glass-sidebar {
            background: rgba(47, 47, 72, 0.88);
            border-radius: 18px;
            box-shadow: 0 2px 24px #5233e420;
            backdrop-filter: blur(8px);
            padding: 1.2rem 1rem 1.5rem 1rem;
            margin-bottom: 2rem;
            border: 1px solid #3311aa33;
        }
        .member-list-item {
            display: flex; align-items: center;
            margin-bottom: 0.9rem;
        }
        .avatar {
            border-radius: 50%;
            width: 34px; height: 34px;
            margin-right: 0.7rem;
            border: 2.5px solid #8877ee;
            object-fit: cover;
            background: #26244d;
        }
        .checkmark {
            color: #7bffb0;
            font-size: 1.1em;
            margin-left: 0.5em;
            vertical-align: middle;
        }
        .incomplete-dot {
            width:14px; height:14px; border-radius:50%;
            background: #e19ebe;
            display:inline-block; margin-left: 0.6em; margin-right:0.1em;
            border: 2px solid #eeaacc44;
            vertical-align: middle;
        }
        .sidebar-title {
            font-weight: bold;
            margin: 0.6rem 0 0.9rem 0;
            color: #c6b9fa;
            font-size: 1.18rem;
            letter-spacing: 0.03em;
        }
        .stButton > button {
            background: linear-gradient(90deg, #8f7dff 10%, #39f8c8 90%) !important;
            color: #16113a !important;
            border-radius: 9px;
            font-weight: 700;
            font-size: 1.07em;
            box-shadow: 0 2px 14px #39f8c833;
            border: none;
            padding: 0.65em 1.5em;
            margin-top: 0.6em;
            transition: filter 0.15s;
        }
        .stButton > button:hover {
            filter: brightness(1.13);
        }
        .sticky-footer {
            position:fixed;
            bottom:0; left:0; width:100vw;
            z-index:999;
            background: linear-gradient(90deg, #2d265c 60%, #2eebfa22 100%);
            box-shadow: 0 0 22px #5233e433;
            padding: 1.1rem 1.5rem 1.1rem 1.5rem;
        }
        .footer-center {
            max-width:700px; margin:auto; text-align:center;
        }
        .animated-progress {
            height: 16px;
            border-radius: 20px;
            background: #211b40;
            overflow: hidden;
            margin-bottom: 0.3em;
        }
        .animated-progress-bar {
            height: 100%;
            border-radius: 20px;
            background: linear-gradient(90deg, #39f8c8 0%, #8f7dff 100%);
            transition: width 0.7s cubic-bezier(.74,-0.01,.4,1.09);
        }
        .progress-label {
            font-size: 1.06em;
            color: #b8ffef;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 1.07em;
            color: #b9bcff;
            padding: 0.6em 1.2em 0.6em 1.2em;
            background: #1b1834;
            margin-right: 0.1em;
            border-radius: 16px 16px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #3e307c 30%, #39f8c8 100%) !important;
            color: #130b2a !important;
            font-weight: 700;
        }
        /* Remove possible empty widget at top */
        .block-container > div:first-child:empty {
            display: none !important;
        }
        .tooltip-wrap {
            display: inline-block;
            position: relative;
        }
        .tooltip-icon {
            color: #6be0ff;
            cursor: pointer;
            font-size: 1.08em;
            margin-left: 0.28em;
            vertical-align: middle;
        }
        .tooltip-box {
            visibility: hidden;
            width: 380px;
            background: #25204aee;
            color: #b8e9ff;
            text-align: left;
            border-radius: 8px;
            padding: 0.85em 1em;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            margin-left: -190px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.97em;
            box-shadow: 0 2px 16px #2eebfa55;
        }
        .tooltip-wrap:hover .tooltip-box,
        .tooltip-wrap:active .tooltip-box {
            visibility: visible;
            opacity: 1;
        }
        @media (max-width: 600px) {
            .tooltip-box { width: 90vw; left: 5vw; margin-left: 0; }
        }
    </style>
""", unsafe_allow_html=True)

# -- Sidebar --
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

# -- Main Card Layout --
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-weight:900; letter-spacing:.02em; background:linear-gradient(90deg,#b8e9ff 10%,#d6bfff 90%);"
                "-webkit-background-clip:text; color:transparent;display:inline;'>✨ Onboarding Portal</h1>", unsafe_allow_html=True)
    st.markdown("<div style='color:#aeefff;font-size:1.12rem;margin-top:0.6em;'>Contact: <b>Contactus@sssdistributors.com</b></div>", unsafe_allow_html=True)
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

    # -- Init session state for members --
    if 'members' not in st.session_state or family_submitted:
        st.session_state['members'] = [
            {"name": "", "age": 0, "avatar": None, "avatar_data": None, "is_complete": False}
            for _ in range(int(members_count))
        ]

    # -- Member Tabs --
    members = st.session_state['members']
    if members:
        st.markdown("### <span style='color:#b8e9ff'>Family Members</span>", unsafe_allow_html=True)
        tab_names = [m["name"] if m["name"] else f"👤 Member {i+1}" for i,m in enumerate(members)]
        member_tabs = st.tabs(tab_names)
        completed_forms = 0

        for idx, (tab, member) in enumerate(zip(member_tabs, members)):
            with tab:
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.subheader(f"Member {idx+1} Details")
                mcols = st.columns([2,1,1])
                with mcols[0]:
                    name = st.text_input("Full Name", value=member.get("name", ""), key=f"name_{idx}", help="Enter legal name as per ID")
                with mcols[1]:
                    age = st.number_input("Age", min_value=0, max_value=120, value=member.get("age", 0), key=f"age_{idx}")
                with mcols[2]:
                    passport_photo = st.file_uploader("Passport Size Photo (optional for minors)", type=["png", "jpg", "jpeg"], key=f"photo_{idx}")
                    avatar_data = None
                    if passport_photo:
                        avatar_data = base64.b64encode(passport_photo.getvalue()).decode()
                        st.markdown(
                            f"<img src='data:image/png;base64,{avatar_data}' class='avatar' style='width:64px;height:64px;margin-top:0.5em;'>",
                            unsafe_allow_html=True
                        )
                member['name'], member['age'] = name, age
                member['avatar'], member['avatar_data'] = passport_photo, avatar_data

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
                    else:
                        docs['E-Aadhaar'] = st.file_uploader("E-Aadhaar (Masked PDF)", type=["pdf"], key=f"aadhaar_{idx}")
                        docs['PAN Card'] = st.file_uploader("PAN Card", type=["jpg", "jpeg", "png", "pdf"], key=f"pan_{idx}")
                        docs['Cancelled Cheque/Bank Statement'] = st.file_uploader("Cancelled Cheque or Bank Statement", key=f"cheque_{idx}")
                        docs['Passport Size Photo'] = passport_photo
                        docs['Email'] = st.text_input("Email", key=f"email_{idx}", value=member.get("email", ""))
                        docs['Phone'] = st.text_input("Phone Number", key=f"phone_{idx}", value=member.get("phone", ""))
                        docs['Mother Name'] = st.text_input("Mother's Name", key=f"mother_{idx}", value=member.get("mother", ""))
                        docs['Place of Birth'] = st.text_input("Place of Birth", key=f"birthplace_{idx}", value=member.get("birthplace", ""))
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

                member['docs'] = docs
                member['is_complete'] = all_fields
                if all_fields:
                    completed_forms += 1
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
                for idx, member in enumerate(members):
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
                            for idx2, subdict in enumerate(file):
                                for subkey, subfile in subdict.items():
                                    if hasattr(subfile, 'read'):
                                        ext = subfile.name.split('.')[-1]
                                        fname = f"{key}_{idx2+1}_{subkey.replace(' ', '_')}.{ext}"
                                        with open(os.path.join(folder, fname), "wb") as f:
                                            f.write(subfile.read())
                        elif hasattr(file, 'read') and key not in ['Passport Size Photo', 'Minor PAN Card (optional)']:
                            ext = file.name.split('.')[-1]
                            fname = f"{key.replace(' ', '_')}.{ext}"
                            with open(os.path.join(folder, fname), "wb") as f:
                                f.write(file.read())
                        elif key == 'Minor PAN Card (optional)' and hasattr(file, 'read'):
                            ext = file.name.split('.')[-1]
                            fname = f"minor_pan_card.{ext}"
                            with open(os.path.join(folder, fname), "wb") as f:
                                f.write(file.read())
                zip_path = f"{head_name.replace(' ', '_')}_onboarding.zip"
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for root, _, files in os.walk(base_dir):
                        for file in files:
                            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), base_dir))
                st.success(f"Documents collected and zipped into {zip_path}")
                with open(zip_path, 'rb') as f:
                    st.download_button("⬇️ Download All Documents (.zip)", f, file_name=zip_path, mime='application/zip')
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
