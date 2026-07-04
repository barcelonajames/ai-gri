"""
disease.py
AI-powered crop disease detection using Claude vision.
"""

import streamlit as st
import anthropic
import base64
import json

from db import get_fields, save_scan, get_scans

CROP_OPTIONS = [
    "Rice/Palay", "Corn", "Coconut", "Sugarcane",
    "Saging", "Other",
]


def get_client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def show_disease(farmer):
    st.title("Crop Disease Detection")
    st.caption("Upload a photo of your crop leaf or plant — AI will diagnose it.")

    # Step 1: crop + field selector
    c1, c2 = st.columns(2)
    with c1:
        selected_crop = st.selectbox("Select crop type", CROP_OPTIONS)
    with c2:
        fields = get_fields(farmer["id"])
        field_options = ["No specific field"] + [f[2] for f in fields]
        selected_field_label = st.selectbox("Link to field (optional)", field_options)

    selected_field_id = None
    if selected_field_label != "No specific field":
        selected_field_id = next(
            (f[0] for f in fields if f[2] == selected_field_label), None
        )

    # Step 2: image upload
    uploaded_file = st.file_uploader(
        "Upload crop photo", type=["jpg", "jpeg", "png"],
        help="Take a clear close-up of the affected leaf or plant part",
    )

    analyze_btn = False
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="Uploaded photo", use_container_width=True)
        with col2:
            st.info("Photo uploaded. Click Analyze Crop to detect diseases.")
            analyze_btn = st.button(
                "Analyze Crop", type="primary", use_container_width=True
            )

    # Step 3: API call
    if analyze_btn and uploaded_file:
        with st.spinner("Analyzing your crop with AI..."):
            try:
                file_bytes = uploaded_file.getvalue()
                img_b64 = base64.standard_b64encode(file_bytes).decode("utf-8")
                media_type = uploaded_file.type or "image/jpeg"

                system_prompt = f"""You are an expert plant pathologist for
Philippine agriculture. Diagnose {selected_crop} crops and respond
ONLY in this exact JSON format (no markdown, no extra text):
{{
  "disease_name": "Name or 'Healthy'",
  "severity": "Healthy | Mild | Moderate | Severe",
  "confidence": "High | Medium | Low",
  "symptoms_observed": "What you see",
  "cause": "Fungal / Bacterial / Viral / Pest / Nutrient deficiency",
  "treatment": "Step-by-step treatment in Taglish",
  "prevention": "Prevention tips in Taglish",
  "urgency": "Can wait | Act within a week | Act immediately"
}}"""

                client = get_client()
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": img_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": f"Diagnose this {selected_crop} photo.",
                            },
                        ],
                    }],
                )

                raw = response.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                result = json.loads(raw.strip())
            except Exception as e:
                st.error(f"Something went wrong while analyzing the image: {e}")
                result = None

        if result:
            render_result(result)
            save_scan(
                user_id=farmer["id"],
                field_id=selected_field_id,
                crop_type=selected_crop,
                image_name=uploaded_file.name,
                diagnosis=json.dumps(result, ensure_ascii=False),
                severity=result.get("severity", "Unknown"),
            )
            st.caption("Scan saved to your history.")

    # Scan history
    st.divider()
    st.subheader("Your Scan History")
    scans = get_scans(farmer["id"], limit=10)
    if not scans:
        st.info("No scans yet.")
    else:
        for scan in scans:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 3])
                with c1:
                    st.write(f"**{scan[3]}**")
                with c2:
                    sev = scan[6]
                    if sev == "Healthy":
                        st.success(sev)
                    elif sev == "Mild":
                        st.info(sev)
                    elif sev == "Moderate":
                        st.warning(sev)
                    else:
                        st.error(sev)
                with c3:
                    st.caption(str(scan[7])[:10])
                with c4:
                    try:
                        d = json.loads(scan[5])
                        st.caption(d.get("disease_name", "—"))
                    except Exception:
                        st.caption(str(scan[5])[:60])


def render_result(result):
    severity = result.get("severity", "Unknown")
    disease = result.get("disease_name", "Unknown")

    if severity == "Healthy":
        st.success(f"Healthy — {disease}")
    elif severity == "Mild":
        st.info(f"Mild: {disease}")
    elif severity == "Moderate":
        st.warning(f"Moderate: {disease}")
    else:
        st.error(f"Severe: {disease} — act now!")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Symptoms**")
            st.write(result.get("symptoms_observed", "—"))
            st.markdown("**Cause**")
            st.write(result.get("cause", "—"))
            st.markdown("**Confidence**")
            st.write(result.get("confidence", "—"))
    with col2:
        with st.container(border=True):
            st.markdown("**Treatment**")
            st.write(result.get("treatment", "—"))
            st.markdown("**Prevention**")
            st.write(result.get("prevention", "—"))
            st.markdown("**Urgency**")
            urg = result.get("urgency", "—")
            if "immediately" in urg.lower():
                st.error(urg)
            elif "week" in urg.lower():
                st.warning(urg)
            else:
                st.info(urg)

