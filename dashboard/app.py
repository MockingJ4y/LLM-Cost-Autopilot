import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="LLM Autopilot", layout="wide")

# Connect to your Render API
API_URL = "https://llm-cost-autopilot-xzlf.onrender.com/v1/completions"
LOGS_URL = "https://llm-cost-autopilot-xzlf.onrender.com/v1/logs"

# --- Sidebar ---
st.sidebar.title("✉️ Send Custom Request")
st.sidebar.write("Test your routing logic live!")
user_prompt = st.sidebar.text_area("Enter your prompt:")

if st.sidebar.button("Send to Autopilot"):
    if user_prompt:
        with st.sidebar.status("Routing request...", expanded=True) as status:
            try:
                res = requests.post(API_URL, json={"prompt": user_prompt})
                res.raise_for_status()
                data = res.json()
                
                if "error" in data["data"]:
                    status.update(label=f"Routed to {data['routed_model']} - FAILED", state="error")
                    st.sidebar.error(f"**Provider Error:**\n\n{data['data']['error']}")
                elif data["data"].get("text"):
                    status.update(label=f"Success! Routed to {data['routed_model']}", state="complete")
                    st.sidebar.success(f"**Response:**\n\n{data['data']['text']}")
                else:
                    status.update(label=f"Routed to {data['routed_model']} - Unexpected Format", state="warning")
                    st.sidebar.warning("**API returned an unexpected format. Raw data:**")
                    st.sidebar.json(data)
                
                st.sidebar.caption(f"Reasoning: {data.get('reasoning', 'N/A')}")
            except Exception as e:
                status.update(label="API Request Failed", state="error")
                st.sidebar.error(f"Ensure the FastAPI server is running. Error: {e}")
    else:
        st.sidebar.warning("Prompt cannot be empty.")

# --- Main Page Analytics ---
st.title("🚀 LLM Cost Autopilot Analytics")

# Fetch data from the Render API instead of the local database!
try:
    logs_res = requests.get(LOGS_URL)
    logs_res.raise_for_status()
    logs = logs_res.json().get("logs", [])
except Exception as e:
    logs = []
    st.error(f"Waiting for API to wake up... (If this persists, send a prompt first!)")

if not logs:
    st.warning("No routing data available yet. Use the sidebar to send a request!")
else:
    df = pd.DataFrame(logs)
    
    total_requests = len(df)
    actual_cost = df["cost"].sum()
    baseline_cost = total_requests * 0.0150 # Baseline GPT-4o cost assumption
    money_saved = baseline_cost - actual_cost
    savings_percent = (money_saved / baseline_cost * 100) if baseline_cost > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", total_requests)
    col2.metric("Actual Cost", f"${actual_cost:.4f}")
    col3.metric("Baseline (GPT-4o) Cost", f"${baseline_cost:.4f}")
    col4.metric("Money Saved", f"${money_saved:.4f}", f"↑ {savings_percent:.1f}%")

    st.markdown("---")
    st.subheader("🤖 Metrics by AI Model")
    
    model_stats = df.groupby("routed_model").agg(
        Requests=("id", "count"),
        Total_Cost_USD=("cost", "sum"),
        Avg_Latency_ms=("latency_ms", "mean"),
        Avg_Quality_Score=("quality_score", "mean")
    ).reset_index()
    
    model_stats["Total_Cost_USD"] = model_stats["Total_Cost_USD"].apply(lambda x: f"${x:.6f}")
    model_stats["Avg_Latency_ms"] = model_stats["Avg_Latency_ms"].apply(lambda x: f"{x:.0f} ms")
    model_stats["Avg_Quality_Score"] = model_stats["Avg_Quality_Score"].apply(lambda x: f"{x:.1f} / 5")
    
    st.dataframe(model_stats, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Traffic Distribution")
        st.bar_chart(df["routed_model"].value_counts())
    with col_chart2:
        st.subheader("Quality Scores (1-5)")
        st.bar_chart(df["quality_score"].value_counts())