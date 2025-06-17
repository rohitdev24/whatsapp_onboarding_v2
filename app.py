import streamlit as st
import os
import zipfile
import io
from datetime import datetime
import base64
import shutil
import re
import requests
import msal

st.set_page_config(page_title="✨ Onboarding Portal", layout="wide")

def safe_name(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name.replace(' ', '_'))

EMAIL_ADDRESS = "contactus@sssdistributors.com"
ONEDRIVE_CLIENT_ID = st.secrets["ONEDRIVE_CLIENT_ID"]
ONEDRIVE_CLIENT_SECRET = st.secrets["ONEDRIVE_CLIENT_SECRET"]
ONEDRIVE_TENANT_ID = st.secrets["ONEDRIVE_TENANT_ID"]

def send_email_graph_api(to, subject, body, attachment_bytes=None, attachment_filename=None):
    authority = f"https://login.microsoftonline.com/{ONEDRIVE_TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        ONEDRIVE_CLIENT_ID,
        authority=authority,
        client_credential=ONEDRIVE_CLIENT_SECRET,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    token_result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" not in token_result:
        st.error("Failed to authenticate with Microsoft Graph for email sending.")
        return False

    access_token = token_result["access_token"]
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": to}}
            ],
            "from": {"emailAddress": {"address": EMAIL_ADDRESS}},
        },
        "saveToSentItems": "false"
    }

    if attachment_bytes and attachment_filename:
        b64content = base64.b64encode(attachment_bytes).decode()
        attachment = {
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": attachment_filename,
            "contentBytes": b64content
        }
        message["message"]["attachments"] = [attachment]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    sendmail_url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ADDRESS}/sendMail"
    resp = requests.post(sendmail_url, headers=headers, json=message)
    if resp.status_code != 202:
        st.error(f"Failed to send email: {resp.status_code} {resp.text}")
        return False
    return True

def create_onedrive_folder_if_not_exists(access_token, folder_path_list):
    parent_id = None
    for folder in folder_path_list:
        if parent_id:
            url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ADDRESS}/drive/items/{parent_id}/children"
        else:
            url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ADDRESS}/drive/root/children"
        resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
        if resp.status_code not in [200, 201]:
            st.error(f"Failed to list folders in OneDrive: {resp.status_code} {resp.text}")
            return None
        folders = resp.json().get("value", [])
        folder_item = next((f for f in folders if f['name'] == folder and f['folder']), None)
        if folder_item:
            parent_id = folder_item['id']
        else:
            create_url = url
            create_resp = requests.post(
                create_url,
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={"name": folder, "folder": {}, "@microsoft.graph.conflictBehavior": "rename"}
            )
            if create_resp.status_code not in [200, 201]:
                st.error(f"Failed to create folder {folder} in OneDrive: {create_resp.status_code} {create_resp.text}")
                return None
            parent_id = create_resp.json()['id']
    return parent_id

def upload_to_onedrive(file_bytes, folder_path_list, filename):
    authority = f"https://login.microsoftonline.com/{ONEDRIVE_TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        ONEDRIVE_CLIENT_ID,
        authority=authority,
        client_credential=ONEDRIVE_CLIENT_SECRET,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    token_result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" not in token_result:
        st.error("Failed to authenticate with Microsoft Graph for OneDrive upload.")
        return None
    access_token = token_result["access_token"]

    parent_id = create_onedrive_folder_if_not_exists(access_token, folder_path_list)
    if not parent_id:
        st.error("Could not create/find OneDrive folders.")
        return None

    upload_url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ADDRESS}/drive/items/{parent_id}:/"+filename+":/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    resp = requests.put(upload_url, headers=headers, data=file_bytes)
    if resp.status_code not in [200, 201]:
        st.error(f"Failed to upload file to OneDrive: {resp.status_code} {resp.text}")
        return None
    return resp.json().get("webUrl", None)

st.markdown("""
    <style>
        /* ... [Your CSS unchanged for brevity] ... */
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="glass-header" style="user-select:none;">
    <span class="glass-header-title">✨ Onboarding Portal</span>
    <span class="glass-header-contact">Contact: <b>Contactus@sssdistributors.com</b></span>
</div>
""", unsafe_allow_html=True)

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

with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("---")

    if "members_count" not in st.session_state:
        st.session_state["members_count"] = 1
    if "family_head_name" not in st.session_state:
        st.session_state["family_head_name"] = ""
    if "family_head_age" not in st.session_state:
        st.session_state["family_head_age"] = 0

    with st.form("family_form", clear_on_submit=False):
        cols = st.columns([2,1,1])
        with cols[0]:
            head_name = st.text_input("Primary Applicant Name", placeholder="Full name", value=st.session_state["family_head_name"])
        with cols[1]:
            head_age = st.number_input("Primary Applicant Age", min_value=0, max_value=120, step=1, value=st.session_state["family_head_age"])
        with cols[2]:
            members_count = st.number_input(
                "How many members wish to invest?", min_value=1, max_value=10, step=1, value=st.session_state["members_count"]
            )
        family_submitted = st.form_submit_button("Confirm Family Info")
        if family_submitted:
            st.session_state["family_head_name"] = head_name
            st.session_state["family_head_age"] = head_age
            st.session_state["members_count"] = members_count

    if "members" not in st.session_state or family_submitted:
        st.session_state["members"] = [
            {"name": "", "age": 0, "avatar": None, "avatar_data": None, "is_complete": False, "is_locked": False}
            for _ in range(int(st.session_state["members_count"]))
        ]
        st.session_state["tab_names"] = []
        st.session_state["active_tab"] = 0
        if st.session_state["family_head_name"]:
            st.session_state["members"][0]["name"] = st.session_state["family_head_name"]
            st.session_state["members"][0]["age"] = st.session_state["family_head_age"]

    if st.session_state.get("members") and st.session_state.get("family_head_name"):
        if not st.session_state["members"][0]["name"]:
            st.session_state["members"][0]["name"] = st.session_state["family_head_name"]
        if not st.session_state["members"][0]["age"]:
            st.session_state["members"][0]["age"] = st.session_state["family_head_age"]

    members = st.session_state["members"]

    tab_names = [m["name"] if m["name"] else f"👤 Member {i+1}" for i, m in enumerate(members)]
    if "active_tab" not in st.session_state or len(tab_names) != len(st.session_state.get("tab_names", [])):
        st.session_state.active_tab = 0
        st.session_state.tab_names = tab_names
    else:
        st.session_state.tab_names = tab_names

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
        name = st.text_input("Full Name", value=members[idx].get("name", ""), key=f"name_{idx}", help="Enter legal name as per ID", disabled=members[idx].get("is_locked", False))
    with mcols[1]:
        age = st.number_input("Age", min_value=0, max_value=120, value=members[idx].get("age", 0), key=f"age_{idx}", disabled=members[idx].get("is_locked", False))
    with mcols[2]:
        passport_photo = st.file_uploader("Passport Size Photo (optional for minors)", type=["png", "jpg", "jpeg"], key=f"photo_{idx}", disabled=members[idx].get("is_locked", False))
        avatar_data = members[idx].get("avatar_data")
        if passport_photo:
            st.session_state[f"member_{idx}_passport_photo_bytes"] = passport_photo.getvalue()
            st.session_state[f"member_{idx}_passport_photo_filename"] = passport_photo.name
            avatar_data = base64.b64encode(passport_photo.getvalue()).decode()
        if avatar_data:
            st.markdown(
                f"<img src='data:image/png;base64,{avatar_data}' class='avatar' style='width:64px;height:64px;margin-top:0.5em;'>",
                unsafe_allow_html=True
            )
    if not members[idx].get("is_locked", False):
        members[idx]['name'], members[idx]['age'] = name, age
        members[idx]['avatar'], members[idx]['avatar_data'] = passport_photo, avatar_data

    docs = {}
    all_fields = True
    if name and age >= 0:
        if age < 18:
            docs['Birth Certificate'] = st.file_uploader("Birth Certificate", key=f"birthcert_{idx}", disabled=members[idx].get("is_locked", False))
            if docs['Birth Certificate']:
                st.session_state[f"member_{idx}_birthcert_bytes"] = docs['Birth Certificate'].getvalue()
                st.session_state[f"member_{idx}_birthcert_filename"] = docs['Birth Certificate'].name
            docs['Minor PAN Card (optional)'] = st.file_uploader("Minor PAN Card (optional)", type=["jpg", "jpeg", "png", "pdf"], key=f"minorpancard_{idx}", disabled=members[idx].get("is_locked", False))
            if docs['Minor PAN Card (optional)']:
                st.session_state[f"member_{idx}_minorpancard_bytes"] = docs['Minor PAN Card (optional)'].getvalue()
                st.session_state[f"member_{idx}_minorpancard_filename"] = docs['Minor PAN Card (optional)'].name
            guardian_list = []
            num_guardians = st.number_input(f"Number of guardians?", min_value=1, max_value=2, value=1, key=f"guardian_count_{idx}", disabled=members[idx].get("is_locked", False))
            for g in range(int(num_guardians)):
                with st.expander(f"Guardian {g+1} Details"):
                    guardian = {}
                    guardian['Guardian PAN'] = st.file_uploader("Guardian PAN Card", key=f"guardian_pan_{idx}_{g}", disabled=members[idx].get("is_locked", False))
                    if guardian['Guardian PAN']:
                        st.session_state[f"member_{idx}_guardian_{g}_pan_bytes"] = guardian['Guardian PAN'].getvalue()
                        st.session_state[f"member_{idx}_guardian_{g}_pan_filename"] = guardian['Guardian PAN'].name
                    guardian['Guardian Aadhaar'] = st.file_uploader("Guardian Aadhaar", key=f"guardian_aadhaar_{idx}_{g}", disabled=members[idx].get("is_locked", False))
                    if guardian['Guardian Aadhaar']:
                        st.session_state[f"member_{idx}_guardian_{g}_aadhaar_bytes"] = guardian['Guardian Aadhaar'].getvalue()
                        st.session_state[f"member_{idx}_guardian_{g}_aadhaar_filename"] = guardian['Guardian Aadhaar'].name
                    guardian['Guardian Bank Statement/Cheque'] = st.file_uploader("Guardian Bank Statement or Cancelled Cheque", key=f"guardian_bank_{idx}_{g}", disabled=members[idx].get("is_locked", False))
                    if guardian['Guardian Bank Statement/Cheque']:
                        st.session_state[f"member_{idx}_guardian_{g}_bank_bytes"] = guardian['Guardian Bank Statement/Cheque'].getvalue()
                        st.session_state[f"member_{idx}_guardian_{g}_bank_filename"] = guardian['Guardian Bank Statement/Cheque'].name
                    guardian_list.append(guardian)
            docs['Guardians'] = guardian_list
            all_fields = bool(docs['Birth Certificate']) and num_guardians >= 1
            for guard in guardian_list:
                all_fields = all_fields and bool(guard.get("Guardian PAN")) and bool(guard.get("Guardian Aadhaar"))
        else:
            docs['E-Aadhaar'] = st.file_uploader("E-Aadhaar (Masked PDF)", type=["pdf"], key=f"aadhaar_{idx}", disabled=members[idx].get("is_locked", False))
            if docs['E-Aadhaar']:
                st.session_state[f"member_{idx}_aadhaar_bytes"] = docs['E-Aadhaar'].getvalue()
                st.session_state[f"member_{idx}_aadhaar_filename"] = docs['E-Aadhaar'].name
            docs['PAN Card'] = st.file_uploader("PAN Card", type=["jpg", "jpeg", "png", "pdf"], key=f"pan_{idx}", disabled=members[idx].get("is_locked", False))
            if docs['PAN Card']:
                st.session_state[f"member_{idx}_pan_bytes"] = docs['PAN Card'].getvalue()
                st.session_state[f"member_{idx}_pan_filename"] = docs['PAN Card'].name
            docs['Cancelled Cheque/Bank Statement'] = st.file_uploader("Cancelled Cheque or Bank Statement", key=f"cheque_{idx}", disabled=members[idx].get("is_locked", False))
            if docs['Cancelled Cheque/Bank Statement']:
                st.session_state[f"member_{idx}_cheque_bytes"] = docs['Cancelled Cheque/Bank Statement'].getvalue()
                st.session_state[f"member_{idx}_cheque_filename"] = docs['Cancelled Cheque/Bank Statement'].name
            docs['Passport Size Photo'] = passport_photo
            docs['Email'] = st.text_input("Email", key=f"email_{idx}", value=members[idx].get("email", ""), disabled=members[idx].get("is_locked", False))
            docs['Phone'] = st.text_input("Phone Number", key=f"phone_{idx}", value=members[idx].get("phone", ""), disabled=members[idx].get("is_locked", False))
            docs['Mother Name'] = st.text_input("Mother's Name", key=f"mother_{idx}", value=members[idx].get("mother", ""), disabled=members[idx].get("is_locked", False))
            docs['Place of Birth'] = st.text_input("Place of Birth", key=f"birthplace_{idx}", value=members[idx].get("birthplace", ""), disabled=members[idx].get("is_locked", False))
            nominee_list = []
            num_nominees = st.number_input(f"Number of nominees?", min_value=1, max_value=3, value=1, key=f"nominee_count_{idx}", disabled=members[idx].get("is_locked", False))
            for n in range(int(num_nominees)):
                with st.expander(f"Nominee {n+1} Details"):
                    nominee = {}
                    nominee['Name'] = st.text_input("Nominee Name", key=f"nominee_name_{idx}_{n}", disabled=members[idx].get("is_locked", False))
                    nominee['Relation'] = st.text_input("Relation", key=f"nominee_relation_{idx}_{n}", disabled=members[idx].get("is_locked", False))
                    nominee['PAN Card'] = st.file_uploader("Nominee PAN Card", key=f"nominee_pan_{idx}_{n}", disabled=members[idx].get("is_locked", False))
                    if nominee['PAN Card']:
                        st.session_state[f"member_{idx}_nominee_{n}_pan_bytes"] = nominee['PAN Card'].getvalue()
                        st.session_state[f"member_{idx}_nominee_{n}_pan_filename"] = nominee['PAN Card'].name
                    nominee['Occupation'] = st.text_input("Occupation", key=f"nominee_occ_{idx}_{n}", disabled=members[idx].get("is_locked", False))
                    nominee['Income'] = st.text_input("Income", key=f"nominee_income_{idx}_{n}", disabled=members[idx].get("is_locked", False))
                    nominee_list.append(nominee)
            docs['Nominees'] = nominee_list
            required_fields = [
                docs.get('E-Aadhaar'), docs.get('PAN Card'), docs.get('Cancelled Cheque/Bank Statement'),
                docs.get('Email'), docs.get('Phone'), docs.get('Mother Name'), docs.get('Place of Birth'),
                passport_photo
            ]
            all_fields = all(required_fields)
            for nm in nominee_list:
                all_fields = all_fields and bool(nm.get("Name")) and bool(nm.get("Relation"))
    else:
        all_fields = False

    if not members[idx].get("is_locked", False):
        members[idx]['docs'] = docs
        members[idx]['is_complete'] = all_fields

    if not members[idx].get("is_locked", False):
        if st.button("Submit Member Data", key=f"submit_member_{idx}"):
            if all_fields:
                members[idx]['is_locked'] = True
                members[idx]['is_complete'] = True
                members[idx]['docs'] = docs
                if idx + 1 < len(members):
                    st.session_state.active_tab = idx + 1
                    st.experimental_rerun()
                else:
                    st.success("All members' data submitted. Now submit all documents for onboarding.")
            else:
                st.warning("Please fill all required fields and upload all required documents before submitting.")

    completed_forms = sum(1 for m in members if m.get("is_complete", False))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<span class='progress-label'>Form Completion</span>", unsafe_allow_html=True)
    percent = completed_forms / max(1, len(members))
    st.markdown(
        f"<div class='animated-progress'><div class='animated-progress-bar' style='width:{int(percent*100)}%'></div></div>",
        unsafe_allow_html=True
    )
    st.markdown(f"<span style='color:#b8e9ff;font-size:1.04em;'>{completed_forms} of {len(members)} complete</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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
    if completed_forms == len(members):
        if st.button("🚀 Submit & Upload All Documents"):
            with st.spinner("Collecting and zipping documents..."):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                family_head_folder = safe_name(st.session_state['family_head_name'])
                # In-memory zip
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for idx2, member in enumerate(members):
                        name = member['name']
                        member_folder = f"{family_head_folder}/{safe_name(name)}"
                        details_lines = [
                            f"Name: {name}",
                            f"Age: {member.get('age', '')}",
                        ]
                        docs = member.get('docs', {})
                        if member.get('age', 0) < 18:
                            details_lines.append("Type: Minor")
                            details_lines.append(f"Number of Guardians: {len(docs.get('Guardians', []))}")
                            for idx_g, guardian in enumerate(docs.get('Guardians', [])):
                                details_lines.append(f"  Guardian {idx_g+1}:")
                                for gkey, gfile in guardian.items():
                                    details_lines.append(f"    {gkey}: {'Uploaded' if gfile else 'Not uploaded'}")
                            details_lines.append(f"Birth Certificate: {'Uploaded' if docs.get('Birth Certificate') else 'Not uploaded'}")
                            details_lines.append(f"Minor PAN Card: {'Uploaded' if docs.get('Minor PAN Card (optional)') else 'Not uploaded'}")
                        else:
                            details_lines.append("Type: Adult")
                            details_lines.append(f"E-Aadhaar: {'Uploaded' if docs.get('E-Aadhaar') else 'Not uploaded'}")
                            details_lines.append(f"PAN Card: {'Uploaded' if docs.get('PAN Card') else 'Not uploaded'}")
                            details_lines.append(f"Cancelled Cheque/Bank Statement: {'Uploaded' if docs.get('Cancelled Cheque/Bank Statement') else 'Not uploaded'}")
                            details_lines.append(f"Passport Size Photo: {'Uploaded' if docs.get('Passport Size Photo') else 'Not uploaded'}")
                            details_lines.append(f"Email: {docs.get('Email', '')}")
                            details_lines.append(f"Phone: {docs.get('Phone', '')}")
                            details_lines.append(f"Mother Name: {docs.get('Mother Name', '')}")
                            details_lines.append(f"Place of Birth: {docs.get('Place of Birth', '')}")
                            nominee_list = docs.get('Nominees', [])
                            details_lines.append(f"Number of Nominees: {len(nominee_list)}")
                            for idx_n, nominee in enumerate(nominee_list):
                                details_lines.append(f"  Nominee {idx_n+1}:")
                                for nkey, nval in nominee.items():
                                    if hasattr(nval, 'name'):
                                        details_lines.append(f"    {nkey}: Uploaded")
                                    else:
                                        details_lines.append(f"    {nkey}: {nval}")
                        # Write details.txt into zip
                        zipf.writestr(f"{member_folder}/details.txt", '\n'.join(details_lines))
                        # Add files from session_state
                        # Minor files
                        if member.get('age', 0) < 18:
                            bc_bytes = st.session_state.get(f"member_{idx2}_birthcert_bytes")
                            bc_fn = st.session_state.get(f"member_{idx2}_birthcert_filename")
                            if bc_bytes and bc_fn:
                                zipf.writestr(f"{member_folder}/{bc_fn}", bc_bytes)
                            pan_bytes = st.session_state.get(f"member_{idx2}_minorpancard_bytes")
                            pan_fn = st.session_state.get(f"member_{idx2}_minorpancard_filename")
                            if pan_bytes and pan_fn:
                                zipf.writestr(f"{member_folder}/{pan_fn}", pan_bytes)
                            for idx_g, guardian in enumerate(docs.get('Guardians', [])):
                                gpan_bytes = st.session_state.get(f"member_{idx2}_guardian_{idx_g}_pan_bytes")
                                gpan_fn = st.session_state.get(f"member_{idx2}_guardian_{idx_g}_pan_filename")
                                if gpan_bytes and gpan_fn:
                                    zipf.writestr(f"{member_folder}/guardian_{idx_g+1}_{gpan_fn}", gpan_bytes)
                                gaadhaar_bytes = st.session_state.get(f"member_{idx2}_guardian_{idx_g}_aadhaar_bytes")
                                gaadhaar_fn = st.session_state.get(f"member_{idx2}_guardian_{idx_g}_aadhaar_filename")
                                if gaadhaar_bytes and gaadhaar_fn:
                                    zipf.writestr(f"{member_folder}/guardian_{idx_g+1}_{gaardhaar_fn}", gaadhaar_bytes)
                                gbank_bytes = st.session_state.get(f"member_{idx2}_guardian_{idx_g}_bank_bytes")
                                gbank_fn = st.session_state.get(f"member_{idx2}_guardian_{idx_g}_bank_filename")
                                if gbank_bytes and gbank_fn:
                                    zipf.writestr(f"{member_folder}/guardian_{idx_g+1}_{gbank_fn}", gbank_bytes)
                            photo_bytes = st.session_state.get(f"member_{idx2}_passport_photo_bytes")
                            photo_fn = st.session_state.get(f"member_{idx2}_passport_photo_filename")
                            if photo_bytes and photo_fn:
                                zipf.writestr(f"{member_folder}/{photo_fn}", photo_bytes)
                        # Adult files
                        else:
                            aadhaar_bytes = st.session_state.get(f"member_{idx2}_aadhaar_bytes")
                            aadhaar_fn = st.session_state.get(f"member_{idx2}_aadhaar_filename")
                            if aadhaar_bytes and aadhaar_fn:
                                zipf.writestr(f"{member_folder}/{aadhaar_fn}", aadhaar_bytes)
                            pan_bytes = st.session_state.get(f"member_{idx2}_pan_bytes")
                            pan_fn = st.session_state.get(f"member_{idx2}_pan_filename")
                            if pan_bytes and pan_fn:
                                zipf.writestr(f"{member_folder}/{pan_fn}", pan_bytes)
                            cheque_bytes = st.session_state.get(f"member_{idx2}_cheque_bytes")
                            cheque_fn = st.session_state.get(f"member_{idx2}_cheque_filename")
                            if cheque_bytes and cheque_fn:
                                zipf.writestr(f"{member_folder}/{cheque_fn}", cheque_bytes)
                            photo_bytes = st.session_state.get(f"member_{idx2}_passport_photo_bytes")
                            photo_fn = st.session_state.get(f"member_{idx2}_passport_photo_filename")
                            if photo_bytes and photo_fn:
                                zipf.writestr(f"{member_folder}/{photo_fn}", photo_bytes)
                            for idx_n, nominee in enumerate(docs.get('Nominees', [])):
                                npan_bytes = st.session_state.get(f"member_{idx2}_nominee_{idx_n}_pan_bytes")
                                npan_fn = st.session_state.get(f"member_{idx2}_nominee_{idx_n}_pan_filename")
                                if npan_bytes and npan_fn:
                                    zipf.writestr(f"{member_folder}/nominee_{idx_n+1}_{npan_fn}", npan_bytes)

                zip_name = f"{safe_name(st.session_state['family_head_name'])}_onboarding.zip"
                zip_buffer.seek(0)
                st.download_button("⬇️ Download All Documents (.zip)", zip_buffer, file_name=zip_name, mime='application/zip')

                st.info("Uploading to OneDrive...")
                zip_buffer.seek(0)
                onedrive_link = upload_to_onedrive(
                    zip_buffer.read(),
                    ["Client Data", safe_name(st.session_state['family_head_name'])],
                    zip_name
                )
                if onedrive_link:
                    st.success("Documents uploaded to OneDrive.")
                else:
                    st.error("Failed to upload to OneDrive.")

                applicant_email = None
                for m in members:
                    if m.get('age', 0) >= 18:
                        applicant_email = m.get('docs', {}).get('Email', None)
                        break
                subject = "✨ SSS Distributors Onboarding Submission Received"
                admin_body = (
                    f"New onboarding submission from {st.session_state['family_head_name']}.\n"
                    f"Submission time: {timestamp}\n"
                    f"Family members: {', '.join([m['name'] for m in members])}\n"
                    f"Download all documents from OneDrive: {onedrive_link}\n"
                )
                applicant_body = (
                    f"Dear {st.session_state['family_head_name']},\n\n"
                    "Your onboarding submission is received. We will review and get back to you shortly.\n\n"
                    "Best regards,\nSSS Distributors Onboarding Team"
                )
                emails_ok = send_email_graph_api(
                    EMAIL_ADDRESS, subject, admin_body, attachment_bytes=zip_buffer.getvalue(), attachment_filename=zip_name
                )
                if applicant_email:
                    emails_ok = emails_ok and send_email_graph_api(
                        applicant_email, subject, applicant_body, attachment_bytes=zip_buffer.getvalue(), attachment_filename=zip_name
                    )
                if emails_ok:
                    st.success("Confirmation emails sent!")
                else:
                    st.error("Failed to send emails (see above for details).")

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
