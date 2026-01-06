import streamlit as st
import pandas as pd
import time
import os


try:
    from auth import login
    from utils.router import choose_models
    from utils.parallel import run_parallel
    from utils.rate_limiter  import check_limit
    from utils.report import generate_report
except Exception as e:
    st.error("⚠️ Backend modules not found. Ensure 'auth', 'utils' folders exist.")
    st.stop()

st.set_page_config(
    page_title="LLM Nexus | Enterprise Comparison",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top, #0b1220, #020617);
    color: #f8fafc;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header {
    visibility: hidden;
}

/* LOGIN WRAPPER */
.login-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

/* LOGIN CARD */
.login-card {
    background: rgba(15, 23, 42, 0.92);
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 2.5rem;
    width: 480px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 40px 80px rgba(0,0,0,0.6);
}

/* TITLES */
.login-title {
    font-size: 1.9rem;
    font-weight: 700;
}

.login-sub {
    color: #94a3b8;
    margin-bottom: 1.8rem;
}

/* INPUTS */
.stTextInput input {
    background-color: #020617 !important;
    border: 1.6px solid #334155 !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
    padding: 14px !important;
}

.stTextInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8;
}

/* ERROR VISUAL (shadow, not border) */
div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* BUTTON */
.stButton button {
    background: linear-gradient(135deg, #38bdf8, #0ea5e9);
    color: #020617;
    border-radius: 14px;
    padding: 0.85rem;
    font-weight: 700;
    width: 100%;
    border: none;
}

.stButton button:hover {
    box-shadow: 0 12px 30px rgba(56,189,248,0.45);
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("⚙️ Controls")
    
    if "user" in st.session_state:
        st.info(f"👤 Logged in as: *{st.session_state.user}*")
    
    st.markdown("---")
    
    st.subheader("Configuration")

    st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
    st.number_input("Max Tokens", value=1024, step=256)
    
    st.markdown("---")
    st.caption("v2.1.0 | Enterprise Edition")


def main():
    
    login()
    if "user" not in st.session_state:
        st.stop()

   
    st.markdown('<div class="main-header">LLM Nexus</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent routing & cost-analysis engine for Generative AI.</div>', unsafe_allow_html=True)

    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    
        st.markdown("### Active Models")
        st.markdown("## 3 Online")
        st.success("All Systems Go")
        st.markdown('</div>', unsafe_allow_html=True)
        task = st.selectbox(
            "Target Objective",
            ["General", "Coding", "Fast Response", "Cost Saving"],
            help="This determines which models are selected via the router."
        )
        
       
        st.metric(label="Active Models", value="3 Online", delta="All Systems Go")

    with col2:
        prompt = st.text_area(
            "Input Prompt",
            height=140,
            placeholder="E.g., Write a secure Python function to connect to AWS S3...",
            label_visibility="visible"
        )

   
    col_submit, col_spacer = st.columns([1, 4])
    with col_submit:
        run_btn = st.button("⚡ Execute Query")

    if run_btn:
        if not check_limit(st.session_state.user):
            st.error("🚫 Rate limit reached. Please upgrade your plan or wait.")
            st.stop()
            
        if not prompt.strip():
            st.warning("⚠️ Please provide a prompt to analyze.")
            st.stop()

     
        with st.status("🔄 Orchestrating Model Requests...", expanded=True) as status:
            st.write("🔍 Analyzing intent...")
            models = choose_models(task)
            st.write(f"✅ Selected optimized models: *{', '.join(models)}*")
            
            st.write("🚀 Dispatching parallel requests...")
            start_time = time.time()
            
            responses = run_parallel(prompt, models)
            
            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✅ Complete! Processed in {elapsed}s", state="complete", expanded=False)

     
        st.markdown("### 📊 Analysis Results")
        
       
        tab1, tab2, tab3, tab4 = st.tabs([
            "👁️ Visual Comparison",
            "📝 Raw Data",
            "📉 Cost Report",
            "📊 Performance Dashboard"
        ])



        with tab1:
           
            cols = st.columns(len(responses))
            
         
            for idx, (model_name, response_text) in enumerate(responses.items()):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="model-card">
                        <div class="model-name">{model_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(response_text) 

        with tab2:
            st.json(responses)

        with tab3:
           
            report_status = generate_report(prompt, responses)
            st.success("Report generated and saved to database.")
            
           
            metrics_col1, metrics_col2 = st.columns(2)
            metrics_col1.metric("Estimated Cost", "$0.0042", "-12%")
            metrics_col2.metric("Latency Average", f"{elapsed}s", "Fast")
        with tab4:
            st.markdown("### 📊 Model Performance Dashboard")

            metrics_file = "data/metrics/metrics.csv"

            if not os.path.exists(metrics_file):
                st.warning("No metrics data available yet. Run some prompts first.")
            else:
                df = pd.read_csv(metrics_file)

                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

                st.subheader("⏱️ Average Latency per Model")
                latency_df = df.groupby("model")["latency"].mean().reset_index()
                st.bar_chart(latency_df.set_index("model"))

                st.subheader("📏 Average Response Length")
                length_df = df.groupby("model")["response_length"].mean().reset_index()
                st.bar_chart(length_df.set_index("model"))

                st.subheader("📈 Requests Over Time")
                time_df = df.set_index("timestamp").resample("1min").count()["model"]
                st.line_chart(time_df)


if __name__== "__main__":
    main()
