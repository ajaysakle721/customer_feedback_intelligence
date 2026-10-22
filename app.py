import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Feedback Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- STYLING ----------
st.markdown(
    """
    <style>
    @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap)');

    :root {
        --primary: #7c3aed;
        --secondary: #06b6d4;
        --accent: #f97316;
        --text: #172033;
        --muted: #64748b;
        --glass: rgba(255, 255, 255, 0.78);
    }

    * {
        font-family: "Inter", sans-serif;
        box-sizing: border-box;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 10%, rgba(249, 115, 22, .22), transparent 30%),
            radial-gradient(circle at 92% 15%, rgba(6, 182, 212, .25), transparent 32%),
            radial-gradient(circle at 50% 95%, rgba(124, 58, 237, .22), transparent 36%),
            linear-gradient(135deg, #fff7ed 0%, #eff6ff 48%, #f5f3ff 100%);
        background-attachment: fixed;
        color: var(--text);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 22px;
        margin-bottom: 28px;
        border: 1px solid rgba(255,255,255,.8);
        border-radius: 22px;
        background: rgba(255,255,255,.65);
        backdrop-filter: blur(18px);
        box-shadow: 0 12px 35px rgba(63, 42, 120, .10);
    }

    .brand {
        font-size: 1.15rem;
        font-weight: 800;
        color: #5b21b6;
    }

    .status {
        padding: 8px 13px;
        border-radius: 999px;
        color: #047857;
        background: #d1fae5;
        font-size: .82rem;
        font-weight: 700;
    }

    .hero {
        text-align: center;
        padding: 40px 18px 24px;
    }

    .badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(124, 58, 237, .10);
        color: #6d28d9;
        font-size: .82rem;
        font-weight: 700;
        border: 1px solid rgba(124, 58, 237, .16);
    }

    .hero h1 {
        margin: 18px auto 12px;
        max-width: 850px;
        font-size: clamp(2.25rem, 6vw, 4.6rem);
        line-height: 1.05;
        letter-spacing: -3px;
        color: #172033;
    }

    .gradient-text {
        background: linear-gradient(90deg, #7c3aed, #0ea5e9, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        max-width: 700px;
        margin: auto;
        color: var(--muted);
        font-size: 1.03rem;
        line-height: 1.75;
    }

    .feature-card, div[data-testid="stForm"] {
        padding: 24px;
        border: 1px solid rgba(255,255,255,.9);
        border-radius: 24px;
        background: var(--glass);
        backdrop-filter: blur(18px);
        box-shadow: 0 18px 50px rgba(76, 59, 130, .11);
    }

    .feature-icon {
        display: grid;
        place-items: center;
        width: 48px;
        height: 48px;
        margin-bottom: 16px;
        border-radius: 15px;
        background: linear-gradient(135deg, #7c3aed, #06b6d4);
        color: white;
        font-size: 1.35rem;
    }

    .feature-card h3 {
        color: #1e293b;
        margin: 0 0 8px;
        font-size: 1.05rem;
    }

    .feature-card p {
        color: #64748b;
        margin: 0;
        line-height: 1.6;
        font-size: .9rem;
    }

    div[data-testid="stForm"] {
        margin-top: 26px;
    }

    div[data-testid="stForm"] h3 {
        color: #312e81;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 13px;
        border-color: #ddd6fe;
        background: rgba(255,255,255,.86);
    }

    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        min-height: 48px;
        border: 0;
        border-radius: 14px;
        color: white;
        font-weight: 750;
        background: linear-gradient(90deg, #7c3aed, #2563eb, #06b6d4);
        box-shadow: 0 10px 25px rgba(91, 33, 182, .25);
        transition: transform .2s ease, box-shadow .2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 15px 32px rgba(37, 99, 235, .30);
    }

    .result-box {
        margin-top: 22px;
        padding: 25px;
        border-radius: 22px;
        color: #e0f2fe;
        background: linear-gradient(135deg, #172554, #312e81 55%, #164e63);
        box-shadow: 0 18px 45px rgba(30, 41, 99, .25);
    }

    .result-box h3, .result-box h4 {
        margin-top: 0;
        color: white;
    }

    .result-box strong {
        color: #67e8f9;
    }

    .footer {
        padding-top: 30px;
        text-align: center;
        color: #64748b;
        font-size: .83rem;
    }

    /* Mobile responsive rules */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .navbar {
            padding: 12px 15px;
            border-radius: 17px;
        }

        .hero {
            padding: 28px 4px 18px;
        }

        .hero h1 {
            font-size: 2.35rem;
            letter-spacing: -1.5px;
        }

        .hero p {
            font-size: .93rem;
        }

        .feature-card,
        div[data-testid="stForm"] {
            padding: 18px;
            border-radius: 18px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- NAVBAR ----------
st.markdown(
    """
    <div class="navbar">
        <div class="brand">✨ FeedSense AI</div>
        <div class="status">● AI System Active</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- HERO ----------
st.markdown(
    """
    <section class="hero">
        <span class="badge">⚡ Powered by n8n + AI</span>
        <h1>Turn customer feedback into
            <span class="gradient-text">actionable insights.</span>
        </h1>
        <p>
            Customer feedback submit karein aur AI se sentiment,
            important issues aur recommended action instantly hasil karein.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

# ---------- FEATURE CARDS ----------
col1, col2, col3 = st.columns(3, gap="large")

features = [
    (
        col1,
        "🧠",
        "Smart Analysis",
        "AI feedback ka context aur customer sentiment understand karta hai.",
    ),
    (
        col2,
        "⚡",
        "Instant Results",
        "n8n automation se analysis aur business action turant milta hai.",
    ),
    (
        col3,
        "🎯",
        "Better Decisions",
        "Issues prioritize karke customer experience improve karein.",
    ),
]

for column, icon, title, description in features:
    with column:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------- FEEDBACK FORM ----------
with st.form("feedback_form", clear_on_submit=False):
    st.markdown("### Share Customer Feedback")
    st.caption("Fields fill karke feedback ko AI analysis ke liye submit karein.")

    left, right = st.columns(2, gap="large")

    with left:
        customer_name = st.text_input(
            "Customer name",
            placeholder="e.g. Rahul Sharma",
        )
        email = st.text_input(
            "Email address",
            placeholder="rahul@example.com",
        )

    with right:
        rating = st.select_slider(
            "Customer rating",
            options=[1, 2, 3, 4, 5],
            value=4,
        )
        category = st.selectbox(
            "Feedback category",
            ["Product", "Service", "Support", "Delivery", "Other"],
        )

    feedback = st.text_area(
        "Feedback message",
        placeholder="Customer ka detailed feedback yahan likhein...",
        height=150,
    )

    submitted = st.form_submit_button("✨ Analyse Feedback")

# ---------- FORM LOGIC ----------
if submitted:
    if not customer_name.strip() or not feedback.strip():
        st.warning("Customer name aur feedback message required hain.")
    else:
        payload = {
            "customer_name": customer_name.strip(),
            "email": email.strip(),
            "rating": rating,
            "category": category,
            "feedback": feedback.strip(),
        }

        webhook_url = os.getenv("N8N_WEBHOOK_URL", "").strip()

        if not webhook_url:
            st.error("`.env` file mein `N8N_WEBHOOK_URL` configure karein.")
        else:
            response = None
            try:
                with st.spinner("AI feedback analyse kar raha hai..."):
                    response = requests.post(
                        webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30,
                    )
                    response.raise_for_status()

                # n8n should return a JSON object containing sentiment,
                # key_issues, and suggested_action.
                try:
                    result = response.json()
                except ValueError:
                    result = None

                # Handle common n8n response shapes:
                # {"sentiment": "..."} OR [{"sentiment": "..."}]
                # OR {"data": {"sentiment": "..."}} OR {"body": {...}}
                if isinstance(result, list) and result:
                    result = result[0]

                if isinstance(result, dict):
                    for wrapper in ("data", "body", "output", "response"):
                        if isinstance(result.get(wrapper), dict):
                            result = result[wrapper]
                            break

                if not isinstance(result, dict):
                    st.error(
                        "n8n ne JSON response nahi bheja. "
                        "Respond to Webhook node mein JSON response configure karein."
                    )
                    st.code(response.text[:2000])
                else:
                    # Accept common field-name variations.
                    sentiment = result.get("sentiment", "Not available")
                    key_issues = result.get(
                        "key_issues",
                        result.get("issues", result.get("keyIssues", "Not available")),
                    )
                    suggested_action = result.get(
                        "suggested_action",
                        result.get("action", result.get("suggestedAction", "Not available")),
                    )

                    # Detect unresolved n8n template expressions such as {{$json.sentiment}}.
                    all_values = f"{sentiment} {key_issues} {suggested_action}"
                    if "{{" in all_values and "}}" in all_values:
                        st.error(
                            "n8n response mein expressions as plain text aa rahe hain. "
                            "Respond to Webhook node ko neeche diye gaye JSON format mein set karein."
                        )
                        st.code(
                            '{\n'
                            '  "sentiment": "Positive",\n'
                            '  "key_issues": "No major issue reported",\n'
                            '  "suggested_action": "Thank the customer for the feedback"\n'
                            '}',
                            language="json",
                        )
                    else:
                        # Make list/dict values readable in the UI.
                        if isinstance(key_issues, (list, dict)):
                            key_issues = ", ".join(map(str, key_issues)) if isinstance(key_issues, list) else str(key_issues)
                        if isinstance(suggested_action, (list, dict)):
                            suggested_action = ", ".join(map(str, suggested_action)) if isinstance(suggested_action, list) else str(suggested_action)

                        st.markdown(
                            f"""
                            <div class="result-box">
                                <h3>✨ AI Insight Summary</h3>
                                <p><strong>Sentiment:</strong> {sentiment}</p>
                                <p><strong>Key issues:</strong> {key_issues}</p>
                                <p><strong>Suggested action:</strong> {suggested_action}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            except requests.exceptions.Timeout:
                st.error("n8n response dene mein 30 seconds se zyada le raha hai. Workflow check karein.")
            except requests.exceptions.HTTPError as error:
                st.error(f"n8n ne HTTP error diya: {error}")
                if response is not None:
                    st.code(response.text[:2000])
            except requests.exceptions.RequestException as error:
                st.error(f"n8n webhook connect nahi hua: {error}")

st.markdown(
    '<div class="footer">FeedSense AI · Customer Feedback Intelligence</div>',
    unsafe_allow_html=True,
)
