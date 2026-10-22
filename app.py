
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
    .main {
        padding-top: 2rem;
    }
    .result-box {
        background-color: #f0f7ff;
        border-left: 5px solid #2563eb;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        color: #172554;
    }
    .result-box h3 {
        color: #1d4ed8;
    }
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

# ---------- HEADER ----------
st.title("✨ FeedSense AI")
st.subheader("Customer Feedback Intelligence")
st.write(
    "Submit customer feedback to analyse sentiment, "
    "identify key issues, and generate suggested actions using AI."
)

st.divider()

# ---------- FEEDBACK FORM ----------
with st.form("feedback_form"):
    st.subheader("📝 Customer Feedback Form")

    customer_name = st.text_input(
        "Customer Name *",
        placeholder="Enter customer name",
    )

    email = st.text_input(
        "Email Address",
        placeholder="Enter email address (optional)",
    )

    rating = st.slider(
        "Rating *",
        min_value=1,
        max_value=5,
        value=3,
        help="1 = Very Poor, 5 = Excellent",
    )

    st.caption("1 ⭐ Very Poor  |  5 ⭐ Excellent")

    category = st.selectbox(
        "Feedback Category *",
        [
            "Product",
            "Service",
            "Delivery",
            "Pricing",
            "Support",
            "Other",
        ],
    )

    feedback = st.text_area(
        "Feedback Message *",
        placeholder="Write your customer feedback here...",
        height=150,
    )

    submitted = st.form_submit_button(
        "🚀 Analyse Feedback",
        use_container_width=True,
    )

# ---------- FORM LOGIC ----------
if submitted:
    if not customer_name.strip() or not feedback.strip():
        st.warning(
            "Customer name aur feedback message required hain."
        )

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

        # Get n8n webhook URL from .env or Streamlit secrets
        webhook_url = os.getenv("N8N_WEBHOOK_URL", "").strip()

        if not webhook_url:
            try:
                webhook_url = str(
                    st.secrets.get("N8N_WEBHOOK_URL", "")
                ).strip()
            except Exception:
                webhook_url = ""

        if not webhook_url:
            st.error(
                "N8N_WEBHOOK_URL configure nahi hai. "
                "Project folder ki .env file mein webhook URL add karein."
            )

        else:
            response = None

            try:
                with st.spinner(
                    "🤖 AI feedback analyse kar raha hai..."
                ):
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30,
                    )
                    response.raise_for_status()

                # Parse n8n response
                try:
                    result = response.json()
                except ValueError:
                    result = None

                # Handle list responses
                if isinstance(result, list) and result:
                    result = result[0]

                # Handle common wrapper formats
                if isinstance(result, dict):
                    for wrapper in (
                        "data",
                        "body",
                        "output",
                        "response",
                    ):
                        if isinstance(result.get(wrapper), dict):
                            result = result[wrapper]
                            break

                if not isinstance(result, dict):
                    st.error(
                        "n8n se valid JSON response nahi mila. "
                        "Apne n8n workflow ke Respond to Webhook "
                        "node ki configuration check karein."
                    )

                    if response is not None:
                        st.code(response.text[:2000])

                else:
                    sentiment = result.get(
                        "sentiment",
                        "Not available",
                    )

                    key_issues = result.get(
                        "key_issues",
                        result.get(
                            "issues",
                            result.get(
                                "keyIssues",
                                "Not available",
                            ),
                        ),
                    )

                    suggested_action = result.get(
                        "suggested_action",
                        result.get(
                            "action",
                            result.get(
                                "suggestedAction",
                                "Not available",
                            ),
                        ),
                    )

                    # Detect unresolved expressions
                    all_values = (
                        f"{sentiment} "
                        f"{key_issues} "
                        f"{suggested_action}"
                    )

                    if "{{" in all_values and "}}" in all_values:
                        st.error(
                            "n8n response mein expressions "
                            "plain text ke roop mein aa rahe hain. "
                            "Respond to Webhook node check karein."
                        )
                        st.code(
                            '{\n'
                            '  "sentiment": "Positive",\n'
                            '  "key_issues": "No major issue reported",\n'
                            '  "suggested_action": "Thank the customer"\n'
                            '}',
                            language="json",
                        )

                    else:
                        # Make list/dict values readable
                        if isinstance(key_issues, (list, dict)):
                            if isinstance(key_issues, list):
                                key_issues = ", ".join(
                                    map(str, key_issues)
                                )
                            else:
                                key_issues = str(key_issues)

                        if isinstance(
                            suggested_action,
                            (list, dict),
                        ):
                            if isinstance(suggested_action, list):
                                suggested_action = ", ".join(
                                    map(str, suggested_action)
                                )
                            else:
                                suggested_action = str(
                                    suggested_action
                                )

                        # Escape values before inserting into HTML
                        sentiment = html.escape(str(sentiment))
                        key_issues = html.escape(str(key_issues))
                        suggested_action = html.escape(
                            str(suggested_action)
                        )

                        st.markdown(
                            f"""
                            <div class="result-box">
                                <h3>✨ AI Insight Summary</h3>
                                <p><strong>Sentiment:</strong>
                                {sentiment}</p>
                                <p><strong>Key issues:</strong>
                                {key_issues}</p>
                                <p><strong>Suggested action:</strong>
                                {suggested_action}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            except requests.exceptions.Timeout:
                st.error(
                    "n8n response dene mein 30 seconds se "
                    "zyada le raha hai. Workflow check karein."
                )

            except requests.exceptions.HTTPError as error:
                st.error(f"n8n ne HTTP error diya: {error}")

                if response is not None:
                    st.code(response.text[:2000])

            except requests.exceptions.RequestException as error:
                st.error(
                    f"n8n webhook connect nahi hua: {error}"
                )

# ---------- FOOTER ----------
st.divider()

st.markdown(
    '<div class="footer">'
    'FeedSense AI · Customer Feedback Intelligence'
    '</div>',
    unsafe_allow_html=True,
)
