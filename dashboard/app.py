import streamlit as st
import pandas as pd
import sqlite3
import requests

DB_PATH = "data/autopilot.db"
API_URL = API_URL = "https://llm-cost-autopilot-xzlf.onrender.com/v1/completions"

st.set_page_config(page_title="Autopilot Dashboard", layout="wide")
st.title("🚀 LLM Cost Autopilot Analytics")

# --- 1. USER DEFINED REQUESTS (Live Testing) ---
st.sidebar.header("✉️ Send Custom Request")
st.sidebar.markdown("Test your routing logic live!")
user_prompt = st.sidebar.text_area("Enter your prompt:", "What is the capital of France?", height=150)

if st.sidebar.button("Send to Autopilot"):
    if user_prompt.strip():
        with st.sidebar.status("Routing request...", expanded=True) as status:
            try:
                # Send the POST request to your FastAPI server
                res = requests.post(API_URL, json={"prompt": user_prompt})
                res.raise_for_status()
                data = res.json()
                
                # Check if the LLM backend returned an error
                if "error" in data["data"]:
                    status.update(label=f"Routed to {data['routed_model']} - FAILED", state="error")
                    st.sidebar.error(f"**Provider Error:**\n\n{data['data']['error']}\n\n*Check your .env file for the correct API key!*")
                elif data["data"].get("text"):
                    status.update(label=f"Success! Routed to {data['routed_model']}", state="complete")
                    st.sidebar.success(f"**Response:**\n\n{data['data']['text']}")
                else:
                    # FALLBACK: If text is missing but it's not officially an "error", dump the raw API response!
                    status.update(label=f"Routed to {data['routed_model']} - Unexpected Response", state="warning")
                    st.sidebar.warning("**API returned an unexpected format. Here is the raw data:**")
                    st.sidebar.json(data) # This will neatly format and display the raw payload
                
                st.sidebar.caption(f"Reasoning: {data.get('reasoning', 'N/A')}")
            except Exception as e:
                status.update(label="API Request Failed", state="error")
                st.sidebar.error(f"Ensure the FastAPI server is running on port 8000.\nError: {e}")
    else:
        st.sidebar.warning("Prompt cannot be empty.")

# --- 2. LOAD DATA ---
def load_data():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query("SELECT * FROM requests", conn)
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No routing data available yet. Use the sidebar to send a request!")
else:
    # --- 3. HIGH-LEVEL METRICS ---
    total_cost = df['cost'].sum()
    baseline_cost = len(df) * 0.015 # Assume avg GPT-4o request costs ~$0.015
    savings = baseline_cost - total_cost
    savings_pct = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", len(df))
    col2.metric("Actual Cost", f"${total_cost:.4f}")
    col3.metric("Baseline (GPT-4o) Cost", f"${baseline_cost:.4f}")
    col4.metric("Money Saved", f"${savings:.4f}", f"{savings_pct:.1f}%")

    st.divider()

    # --- 4. METRICS BY AI MODEL (New Feature) ---
    st.subheader("🤖 Metrics by AI Model")
    
    # Group the database logs by the routed_model column
    model_stats = df.groupby('routed_model').agg(
        Requests=('id', 'count'),
        Total_Cost_USD=('cost', 'sum'),
        Avg_Latency_ms=('latency_ms', 'mean'),
        Avg_Quality_Score=('quality_score', 'mean')
    ).reset_index()
    
    # Format the data cleanly for the UI
    model_stats['Total_Cost_USD'] = model_stats['Total_Cost_USD'].apply(lambda x: f"${x:.6f}")
    model_stats['Avg_Latency_ms'] = model_stats['Avg_Latency_ms'].apply(lambda x: f"{x:.0f} ms" if pd.notnull(x) else "N/A")
    model_stats['Avg_Quality_Score'] = model_stats['Avg_Quality_Score'].apply(lambda x: f"{x:.1f} / 5" if pd.notnull(x) else "Pending")
    
    # Render the table
    st.dataframe(model_stats, use_container_width=True, hide_index=True)

    st.divider()

    # --- 5. VISUALS ---
    colA, colB = st.columns(2)
    
    with colA:
        st.subheader("Traffic Distribution")
        model_counts = df['routed_model'].value_counts()
        st.bar_chart(model_counts)
        
    with colB:
        st.subheader("Quality Scores (1-5)")
        scores = df['quality_score'].dropna().value_counts().sort_index()
        st.bar_chart(scores)

    # --- 6. LOGS ---
    st.subheader("Recent Routing Logs")
    
    # Safely check which columns exist so old database files don't crash the app!
    expected_cols = ['timestamp', 'prompt', 'tier', 'routed_model', 'cost', 'latency_ms', 'quality_score']
    display_cols = [c for c in expected_cols if c in df.columns]
    
    # Show the newest items first
    display_df = df[display_cols].sort_values(by='timestamp', ascending=False).head(15)
    st.dataframe(display_df, use_container_width=True, hide_index=True)