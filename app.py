import streamlit as st
import os

# --- Company Logo Fix ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        # Fallback: use a URL or show message
        st.image("https://yourdomain.com/path/to/logo.png", width=150)
        # Or: st.warning("Logo not found. Please check your file path or URL!")

# ... your onboarding app code here ...

# --- Download Button Fix ---
zip_path = "onboarding_20250616_123456.zip"  # Replace with your actual zip filename

if os.path.exists(zip_path):
    with open(zip_path, "rb") as f:
        st.download_button(
            label="⬇️ Download All Documents (.zip)",
            data=f,
            file_name=os.path.basename(zip_path),
            mime="application/zip"
        )
else:
    st.warning("Download not available. ZIP file missing or not created.")
