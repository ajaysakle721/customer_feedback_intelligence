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

        # Local development: read N8N_WEBHOOK_URL from .env.
        # Streamlit Cloud: add N8N_WEBHOOK_URL under App settings > Secrets.
        webhook_url = os.getenv("N8N_WEBHOOK_URL", "").strip()
        if not webhook_url:
            try:
                webhook_url = str(st.secrets.get("N8N_WEBHOOK_URL", "")).strip()
            except Exception:
                webhook_url = ""

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
