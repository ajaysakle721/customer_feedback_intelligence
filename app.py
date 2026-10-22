import os
import html
import requests
import streamlit as st
from dotenv import load_dotenv

# ---------- CONFIGURATION ----------
load_dotenv()

st.set_page_config(
    page_title="FeedSense AI - Customer Feedback Intelligence",
    page_icon="✨",
    layout="centered",
)

# ---------- CUSTOM CSS ----------
st.markdown(
    """
    <style>
    .main { padding-top: 2rem; }
    .result-box {
        background-color: #f0f7ff;
        border-left: 5px solid #2563eb;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        color: #172554;
    }
    .result-box h3 { color: #1d4ed8; }
    .footer {
        text-align: center;
        color: #888888;
        padding: 25px 0 10px 0;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def get_webhook_url():
    """Read webhook URL from environment or Streamlit Cloud secrets."""
    url = os.getenv("N8N_WEBHOOK_URL", "").strip()
    if not url:
        try:
            url = str(st.secrets.get("N8N_WEBHOOK_URL", "")).strip()
        except Exception:
            url = ""
    return url

def unwrap_response(data):
    """Unwrap common n8n response shapes without assuming one exact schema."""
    for _ in range(3):
        if isinstance(data, list):
            if not data:
                return None
            data = data[0]
        elif isinstance(data, dict):
            for key in ("data", "body", "output", "response"):
                value = data.get(key)
                if isinstance(value, (dict, list)):
                    data = value
                    break
            else:
                return data
        else:
            return None
    return data if isinstance(data, dict) else None

def readable(value, default="Not available"):
    if value is None or value == "":
        return default
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else default
    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in value.items()) if value else default
    return str(value)

# ---------- HEADER ----------
st.title("✨ FeedSense AI")
st.subheader("Customer Feedback Intelligence")
st.write(
    "Submit customer feedback to analyse sentiment, identify key issues, "
    "and generate suggested actions using AI."
)
st.divider()

# ---------- FEEDBACK FORM ----------
with st.form("feedback_form"):
    st.subheader("📝 Customer Feedback Form")
    customer_name = st.text_input("Customer Name *", placeholder="Enter customer name")
    email = st.text_input("Email Address", placeholder="Enter email address (optional)")
    rating = st.slider("Rating *", min_value=1, max_value=5, value=3,
                       help="1 = Very Poor, 5 = Excellent")
    st.caption("1 ⭐ Very Poor  |  5 ⭐ Excellent")
    category = st.selectbox(
        "Feedback Category *",
        ["Product", "Service", "Delivery", "Pricing", "Support", "Other"],
    )
    feedback = st.text_area(
        "Feedback Message *",
        placeholder="Write your customer feedback here...",
        height=150,
    )
    submitted = st.form_submit_button("🚀 Analyse Feedback", use_container_width=True)

# ---------- FORM LOGIC ----------
if submitted:
    if not customer_name.strip() or not feedback.strip():
        st.warning("Customer name aur feedback message required hain.")
    elif email.strip() and (
        "@" not in email.strip()
        or "." not in email.strip().split("@")[-1]
    ):
        st.warning("Please ek valid email address enter karein.")
    else:
        payload = {
            "customer_name": customer_name.strip(),
            "email": email.strip(),
            "rating": rating,
            "category": category,
            "feedback": feedback.strip(),
        }
        webhook_url = get_webhook_url()

        if not webhook_url:
            st.error(
                "N8N_WEBHOOK_URL configure nahi hai. "
                "Streamlit Cloud → App → Settings → Secrets mein "
                "N8N_WEBHOOK_URL set karein, ya local .env file mein add karein."
            )
        elif not webhook_url.startswith(("https://", "http://")):
            st.error("N8N_WEBHOOK_URL valid HTTP/HTTPS URL nahi lag raha. URL setting check karein.")
        else:
            response = None
            try:
                with st.spinner("🤖 AI feedback analyse kar raha hai..."):
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        timeout=60,
                    )

                if not response.ok:
                    st.error(
                        f"n8n ne HTTP {response.status_code} error diya. "
                        "Iska matlab workflow ya uske kisi node mein failure ho sakta hai."
                    )
                    st.write("n8n response details:")
                    st.code(response.text[:4000] or "(Empty response)", language="json")
                    st.info(
                        "n8n → Executions mein latest failed execution kholo aur "
                        "red node ka Error details check karo. App se request pahunch rahi "
                        "hai, lekin HTTP error ko app.py akela fix nahi kar sakta."
                    )
                else:
                    try:
                        raw_result = response.json()
                    except ValueError:
                        raw_result = None

                    result = unwrap_response(raw_result)

                    if not isinstance(result, dict):
                        st.warning(
                            "Webhook ne success status diya, lekin response JSON object nahi hai. "
                            "n8n ke Respond to Webhook node ka response format check karein."
                        )
                        st.code(response.text[:4000] or "(Empty response)")
                    else:
                        # Supports both the original UI schema and the current AI classifier schema.
                        sentiment = result.get(
                            "sentiment",
                            result.get("category", result.get("label", "Not available")),
                        )
                        key_issues = result.get(
                            "key_issues",
                            result.get(
                                "issues",
                                result.get(
                                    "keyIssues",
                                    result.get("reason", result.get("product", "Not available")),
                                ),
                            ),
                        )
                        suggested_action = result.get(
                            "suggested_action",
                            result.get(
                                "action",
                                result.get(
                                    "suggestedAction",
                                    result.get("severity", "Not available"),
                                ),
                            ),
                        )

                        st.markdown(
                            f"""
                            <div class="result-box">
                                <h3>✨ AI Insight Summary</h3>
                                <p><strong>Sentiment / Category:</strong>
                                {html.escape(readable(sentiment))}</p>
                                <p><strong>Key issues / Reason:</strong>
                                {html.escape(readable(key_issues))}</p>
                                <p><strong>Suggested action / Severity:</strong>
                                {html.escape(readable(suggested_action))}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Show other fields when the workflow returns them.
                        extra_fields = {
                            "Product": result.get("product"),
                            "Severity": result.get("severity"),
                            "Confidence": result.get("confidence"),
                        }
                        extras = {k: v for k, v in extra_fields.items() if v is not None}
                        if extras:
                            st.subheader("Additional AI details")
                            for label, value in extras.items():
                                st.write(f"**{label}:** {readable(value)}")

            except requests.exceptions.Timeout:
                st.error(
                    "n8n ne 60 seconds ke andar response nahi diya. "
                    "n8n Executions mein workflow status check karein."
                )
            except requests.exceptions.RequestException as error:
                st.error(f"n8n webhook connect nahi hua: {error}")

# ---------- FOOTER ----------
st.divider()
st.markdown(
    '<div class="footer">FeedSense AI · Customer Feedback Intelligence</div>',
    unsafe_allow_html=True,
)
