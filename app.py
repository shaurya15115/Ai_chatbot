import streamlit as st
import requests
import json
import time
import logging

# Set page config FIRST
st.set_page_config(
    page_title="📈 AI Investment Advisor",
    page_icon="💹",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS with market theme
# Update the CSS section with this code
st.markdown("""
<style>
    :root {
        --primary-color: #2ecc71;
        --secondary-color: #3498db;
        --text-dark: #2c3e50;
        --text-light: #ecf0f1;
        --success: #27ae60;
        --warning: #f1c40f;
        --error: #e74c3c;
    }

    .stApp {
        background-image: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), url('https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3');
        background-size: cover;
        color: var(--text-dark) !important;
    }

    .main-container {
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(8px);
        border: 1px solid var(--primary-color);
    }

    .stChatMessage {
        background: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid #dfe6e9 !important;
    }

    [data-testid="stChatMessage"][aria-label="assistant"] {
        border-left: 4px solid var(--primary-color);
        background: linear-gradient(135deg, #f8fff9 0%, #f4f9ff 100%) !important;
    }

    .market-card {
        background: rgba(255, 255, 255, 0.98) !important;
        border: 2px solid var(--primary-color);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .market-card h4 {
        color: var(--primary-color) !important;
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 0.5rem;
    }

    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: var(--text-light) !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3);
    }

    /* Text hierarchy */
    h1, h2, h3 {
        color: var(--text-dark) !important;
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 0.5rem;
    }

    p, li {
        color: var(--text-dark) !important;
        line-height: 1.6;
    }

    /* Special highlights */
    .recommendation {
        color: var(--success) !important;
        font-weight: 600;
    }

    .risk-alert {
        color: var(--warning) !important;
        border-left: 3px solid var(--warning);
        padding-left: 1rem;
    }

    .market-update {
        background: rgba(52, 152, 219, 0.1) !important;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Welcome to your AI Investment Advisor! 💼 How can I help grow your portfolio today?"
    }]

# Configure sidebar
with st.sidebar:
    st.title("⚙️ Advisor Settings")
    with st.container():
        api_key = st.text_input("OpenRouter API Key", type="password", help="Required for market analysis")
        st.markdown("[Get API Key](https://openrouter.ai/keys)")
        
        with st.expander("📈 Quick Start"):
            st.markdown("""
            1. Obtain API key
            2. Select analysis model
            3. Ask about:
               - Portfolio optimization
               - Market trends
               - Risk assessment
            """)
        
        model_name = st.selectbox(
            "🤖 Analysis Engine",
            ("google/palm-2-chat-bison"),
            index=0
        )
        
        with st.expander("⚙️ Analysis Parameters"):
            risk_profile = st.select_slider(
                "📉 Risk Tolerance",
                options=["Conservative", "Moderate", "Aggressive"]
            )
            time_horizon = st.selectbox(
                "⏳ Investment Horizon",
                ["Short-term (<1yr)", "Medium-term (1-5yrs)", "Long-term (>5yrs)"]
            )
            max_retries = st.number_input("🔄 Max Analysis Retries", 1, 5, 2)
        
        if st.button("🧹 New Session"):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Session cleared! Let's analyze new opportunities!"
            }]

# Main interface
with st.container():
    st.title("💹 AI Portfolio Strategist")
    st.caption("Data-driven investment recommendations powered by market intelligence")

    # Market feature cards
    cols = st.columns(4)
    features = [
        ("📊 Portfolio Analysis", "Optimize asset allocation"),
        ("🌍 Global Markets", "International opportunities"),
        ("⚖️ Risk Management", "Tailored risk assessment"),
        ("📈 Trend Prediction", "AI-powered forecasts    ")
    ]
    for col, (emoji, text) in zip(cols, features):
        col.markdown(
            f"""<div class='market-card'>
                <h4 style='color: #27ae60;'>{emoji}</h4>
                <p style='color: #2c3e50;'>{text}</p>
            </div>""", 
            unsafe_allow_html=True
        )

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask investment questions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required for market analysis")
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 10px;'>
                <h4 style='color: #27ae60;'>Get Started:</h4>
                <ol style='color: #2c3e50;'>
                    <li>Visit <a href="https://openrouter.ai/keys" style='color: #27ae60;'>OpenRouter</a></li>
                    <li>Create professional account</li>
                    <li>Enter credentials in sidebar</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0
        
        with st.spinner("📊 Analyzing market data..."):
            time.sleep(0.5)
        
        while attempts < max_retries:
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://investment-advisor.streamlit.app",
                        "X-Title": "AI Portfolio Strategist"
                    },
                    json={
                        "model": model_name,
                        "messages": [{
                            "role": "system",
                            "content": f"""You are a certified financial advisor with Wall Street experience. STRICT RULES:
1. Format recommendations:
   - Asset Class: [Equities/Fixed Income/etc]
   - Risk Level: {risk_profile}
   - Time Horizon: {time_horizon}
   - Expected Return: X-Y%
   - Key Factors: [Market conditions]
2. Use financial emojis: 💹📉📊💼
3. Include technical analysis elements
4. Current date: {time.strftime("%Y-%m-%d")}
5. Highlight sector opportunities
6. Never provide generic advice
7. Maintain SEC compliance standards"""
                        }] + st.session_state.messages[-4:],
                        "temperature": 0.4,
                        "response_format": {"type": "text"}
                    },
                    timeout=20
                )

                response.raise_for_status()
                data = response.json()
                raw_response = data['choices'][0]['message']['content']
                
                # Format response
                processed_response = raw_response.replace("**", "").replace("```", "")
                
                # Stream response
                lines = processed_response.split('\n')
                for line in lines:
                    words = line.split()
                    for word in words:
                        full_response += word + " "
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.03)
                    full_response += "\n"
                    response_placeholder.markdown(full_response + "▌")
                
                # Final formatting
                full_response = full_response.replace("BUY", "<span style='color: #27ae60'>BUY</span>") \
                                           .replace("SELL", "<span style='color: #e74c3c'>SELL</span>") \
                                           .replace("HOLD", "<span style='color: #f1c40f'>HOLD</span>")
                
                response_placeholder.markdown(full_response, unsafe_allow_html=True)
                break
                
            except json.JSONDecodeError as e:
                logging.error(f"Analysis Error: {str(e)}")
                attempts += 1
                if attempts == max_retries:
                    response_placeholder.error("⚠️ Market data processing failed")
                    response_placeholder.markdown("""
                    <div style='background: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 10px;'>
                        <h4 style='color: #27ae60;'>Troubleshooting:</h4>
                        <ul style='color: #2c3e50;'>
                            <li>Rephrase your query</li>
                            <li>Check market data inputs</li>
                            <li>Verify financial parameters</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                response_placeholder.error(f"🌐 Market Data Connection Error: {str(e)}")
                full_response = "Market data feed unavailable - retry later"
                break
                
            except Exception as e:
                logging.error(f"Analysis Error: {str(e)}")
                response_placeholder.error(f"❌ Portfolio Analysis Failed: {str(e)}")
                full_response = "Financial analysis error - please retry"
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})