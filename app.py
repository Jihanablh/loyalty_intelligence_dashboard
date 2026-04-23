import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import io
import time

# --- CONFIG & THEME ---
st.set_page_config(
    page_title="LoyaltyIQ | Intelligence & Prediction",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PREMIUM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 20% 10%, #1e1b4b 0%, #0f172a 100%);
        color: #f8fafc;
    }

    /* Hero Header */
    .hero-title {
        background: linear-gradient(90deg, #6366f1 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    .badge-ai {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(99, 102, 241, 0.3);
        display: inline-block;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Premium KPI Cards */
    .kpi-container {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        padding: 1.5rem;
        border-radius: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        flex: 1;
        transition: all 0.3s ease;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .kpi-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(99, 102, 241, 0.4);
        background: rgba(30, 41, 59, 0.7);
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
    }

    /* Glassmorphism Section */
    .section-card {
        background: rgba(30, 41, 59, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    /* Prediction Result Card */
    .result-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        border-radius: 1.5rem;
        padding: 2.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 1rem;
    }

    /* Status Badges */
    .badge-status {
        padding: 6px 16px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .status-tinggi { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .status-sedang { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .status-rendah { background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid #f43f5e; }

    /* Custom Input Styling */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Center align numeric inputs */
    input[type="number"] {
        text-align: center !important;
    }

    /* Hide standard metrics */
    [data-testid="stMetricValue"] {
        font-size: 0 !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- CORE LOGIC & MATHEMATICS ---
@st.cache_data
def run_loyalty_model(m1, m2, m3):
    """
    Main Predictive Engine
    Trend: Differential momentum weight
    WMA: Weighted Moving Average (Recency Bias)
    Score: Composite Loyalty Score
    """
    # Trend = (-2/3 * M1) + (1/3 * M2) + (4/3 * M3)
    trend = (-2/3 * m1) + (1/3 * m2) + (4/3 * m3)
    # WMA = (0.2 * M1) + (0.3 * M2) + (0.5 * M3)
    wma = (0.2 * m1) + (0.3 * m2) + (0.5 * m3)
    # Final Score = 0.4 * Trend + 0.6 * WMA
    raw_score = (0.4 * trend) + (0.6 * wma)
    
    # User constraint: 0-10 scale for categorization
    # If the inputs are larger than 10, we treat this as a raw index or handle scaling.
    # We will provide a normalized version for the 0-10 classification if needed, 
    # but strictly use user ranges for categorization.
    
    category = "Rendah"
    if raw_score >= 7: category = "Tinggi"
    elif raw_score >= 4: category = "Sedang"
    
    insight = "Performanya stabil"
    if trend > 1.5: insight = "🔍 Tren Pertumbuhan Eksplosif"
    elif trend < -0.5: insight = "⚠️ Risiko Churn Terdeteksi"
    elif raw_score > 8: insight = "💎 Pelanggan VIP Berharga"
    
    return {
        "score": round(raw_score, 2),
        "trend": round(trend, 2),
        "wma": round(wma, 2),
        "category": category,
        "insight": insight
    }

def process_bulk_data(df):
    """Processes uploaded dataframe and appends model results."""
    if not all(k in df.columns for k in ["Nama", "T1", "T2", "T3"]):
        return None
    
    results = []
    for _, row in df.iterrows():
        res = run_loyalty_model(row["T1"], row["T2"], row["T3"])
        results.append({
            "Nama": row["Nama"],
            "M1": row["T1"],
            "M2": row["T2"],
            "M3": row["T3"],
            "Predicted Score": res["score"],
            "Category": res["category"],
            "Insight": res["insight"]
        })
    return pd.DataFrame(results)

# --- DATA INITIALIZATION ---
if "master_data" not in st.session_state:
    # Initial realistic mock data
    mock_df = pd.DataFrame([
        {"Nama": "Adi Guna", "T1": 8, "T2": 9, "T3": 9.5},
        {"Nama": "Siska Amalia", "T1": 4, "T2": 5, "T3": 3},
        {"Nama": "Budi Hartono", "T1": 6, "T2": 7, "T3": 8.5},
        {"Nama": "Lintang Sore", "T1": 9, "T2": 8, "T3": 9.2},
        {"Nama": "Citra Lestari", "T1": 2, "T2": 3, "T3": 4.5},
        {"Nama": "Fajar Sidik", "T1": 5, "T2": 4, "T3": 5.5},
        {"Nama": "Riza Rahayu", "T1": 7, "T2": 6, "T3": 8},
        {"Nama": "Tono Wijaya", "T1": 3, "T2": 2, "T3": 2.5}
    ])
    st.session_state.master_data = process_bulk_data(mock_df)

# --- DASHBOARD LAYOUT ---

# 🔹 1. Hero Header
st.markdown("<div class='badge-ai'>AI Powered Prediction System</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>💎 Loyalty Intelligence Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Advanced customer retention analysis using predictive transaction modeling.</div>", unsafe_allow_html=True)

# 🔹 2. KPI Cards Section
data = st.session_state.master_data
high_value_pct = (data["Predicted Score"] >= 7).sum() / len(data) * 100

kpi_cols = st.columns(5)
metrics = [
    ("Total Customers", f"{len(data)}", "#6366f1"),
    ("Average Score", f"{data['Predicted Score'].mean():.2f}", "#10b981"),
    ("Highest Score", f"{data['Predicted Score'].max():.1f}", "#818cf8"),
    ("Lowest Score", f"{data['Predicted Score'].min():.1f}", "#f43f5e"),
    ("% High Value", f"{high_value_pct:.0f}%", "#fbbf24")
]

for col, (label, val, color) in zip(kpi_cols, metrics):
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value' style='color: {color};'>{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# MODE TOGGLE
app_mode = st.radio("Pipeline Mode", ["Manual Simulation", "Bulk Intelligence Module"], horizontal=True)

# 🔹 3. Manual Input Section
if app_mode == "Manual Simulation":
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### ⚡ Predict Individual Loyalty")
    
    i_col1, i_col2, i_col3, i_col4 = st.columns([2, 1, 1, 1])
    with i_col1:
        s_name = st.text_input("Customer Name", "Prospect #242")
    with i_col2:
        s_m1 = st.number_input("Month 1 (M1)", 0.0, 100.0, 5.0)
    with i_col3:
        s_m2 = st.number_input("Month 2 (M2)", 0.0, 100.0, 6.0)
    with i_col4:
        s_m3 = st.number_input("Month 3 (M3)", 0.0, 100.0, 7.5)
    
    if st.button("Run Predictive Model"):
        with st.spinner("Processing intelligence..."):
            time.sleep(0.8)
            res = run_loyalty_model(s_m1, s_m2, s_m3)
            st.session_state.last_res = {**res, "name": s_name}
            st.toast("Intelligence processed successfully!", icon="✅")

    # 🔹 5. Result Section (Manual)
    if "last_res" in st.session_state:
        r = st.session_state.last_res
        cat_class = f"status-{r['category'].lower()}"
        
        st.markdown(f"""
        <div class='result-card'>
            <p style='color: #94a3b8; font-size: 1rem; margin-bottom: 0.5rem;'>Analysis for {r['name']}</p>
            <h1 style='font-size: 4.5rem; margin: 0; color: #f8fafc;'>{r['score']}</h1>
            <div style='margin: 1.5rem 0;'>
                <span class='badge-status {cat_class}'>Loyalty Category: {r['category']}</span>
            </div>
            <h3 style='color: #10b981;'>{r['insight']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Save to DB
        if st.button("Add to Master Records"):
            new_row = pd.DataFrame([{
                "Nama": r["name"], "M1": s_m1, "M2": s_m2, "M3": s_m3,
                "Predicted Score": r["score"], "Category": r["category"], "Insight": r["insight"]
            }])
            st.session_state.master_data = pd.concat([st.session_state.master_data, new_row], ignore_index=True)
            st.success("Record committed to history.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# 🔹 8. Bulk Upload Section
else:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### 📤 Bulk Intelligence Processor")
    up_file = st.file_uploader("Upload Intel (CSV/Excel)", type=["csv", "xlsx"])
    
    if up_file:
        try:
            if up_file.name.endswith(".csv"):
                df_up = pd.read_csv(up_file)
            else:
                df_up = pd.read_excel(up_file)
            
            st.markdown("#### Data Preview")
            st.dataframe(df_up.head(), use_container_width=True)
            
            if st.button("Generate Mass Predictions"):
                with st.spinner("Running high-concurrency model..."):
                    time.sleep(1.5)
                    processed = process_bulk_data(df_up)
                    if processed is not None:
                        st.session_state.master_data = pd.concat([st.session_state.master_data, processed], ignore_index=True).drop_duplicates(subset=["Nama"], keep="last")
                        st.success(f"Successfully processed {len(processed)} records.")
                        st.rerun()
                    else:
                        st.error("Invalid Schema. Need columns: Nama, T1, T2, T3")
        except Exception as e:
            st.error(f"Inference Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# 🔹 6. Visual Analytics Section
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("### 📊 Advanced Data Analytics")

v_col1, v_col2 = st.columns([2, 1])

with v_col1:
    st.markdown("#### Transaction Lifecycle & Outcome")
    # Plotting top 5 for line chart
    top_v = data.sort_values("Predicted Score", ascending=False).head(5)
    l_points = []
    for _, row in top_v.iterrows():
        l_points.append({"Nama": row["Nama"], "Stage": "M1", "Val": row["M1"]})
        l_points.append({"Nama": row["Nama"], "Stage": "M2", "Val": row["M2"]})
        l_points.append({"Nama": row["Nama"], "Stage": "M3", "Val": row["M3"]})
        l_points.append({"Nama": row["Nama"], "Stage": "Outcome", "Val": row["Predicted Score"]})
    l_df = pd.DataFrame(l_points)
    
    fig_line = px.line(l_df, x="Stage", y="Val", color="Nama", markers=True, line_shape="spline")
    fig_line.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_line, use_container_width=True)

with v_col2:
    st.markdown("#### Category Split")
    cat_dist = data["Category"].value_counts().reset_index()
    fig_pie = px.pie(cat_dist, values="count", names="Category", hole=0.5, 
                     color_discrete_map={"Tinggi": "#10b981", "Sedang": "#f59e0b", "Rendah": "#f43f5e"})
    fig_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

v_col3, v_col4 = st.columns(2)
with v_col3:
    st.markdown("#### Leadership Board (Top 10)")
    fig_lb = px.bar(data.nlargest(10, "Predicted Score"), x="Predicted Score", y="Nama", orientation="h", color="Predicted Score", color_continuous_scale="Viridis")
    fig_lb.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig_lb, use_container_width=True)

with v_col4:
    st.markdown("#### Score Density")
    fig_hist = px.histogram(data, x="Predicted Score", nbins=15, color_discrete_sequence=["#818cf8"])
    fig_hist.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# 🔹 7 & 9. Data Table & Interaction
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("### 🔍 Historical Intelligence Ledger")

q_col1, q_col2, q_col3 = st.columns([2, 1, 1])
with q_col1:
    search_q = st.text_input("Find Record", placeholder="Type a name...")
with q_col2:
    cat_sel = st.multiselect("Category", ["Tinggi", "Sedang", "Rendah"], default=["Tinggi", "Sedang", "Rendah"])
with q_col3:
    score_lim = st.slider("Min Score", 0.0, 10.0, 0.0)

filtered_df = data[
    (data["Nama"].str.contains(search_q, case=False)) &
    (data["Category"].isin(cat_sel)) &
    (data["Predicted Score"] >= score_lim)
]

# Highlight logic without manual HTML or matplotlib
def style_table(df):
    def highlight_score(val):
        color = 'transparent'
        if val >= 7: color = 'rgba(16, 185, 129, 0.2)' # Green
        elif val >= 4: color = 'rgba(245, 158, 11, 0.2)' # Orange
        else: color = 'rgba(244, 63, 94, 0.2)' # Red
        return f'background-color: {color}'

    return df.style.map(highlight_score, subset=["Predicted Score"]) \
                   .highlight_max(subset=["Predicted Score"], color="rgba(99, 102, 241, 0.4)")

st.dataframe(style_table(filtered_df), use_container_width=True, height=400)

# 🔹 10. Download Output
csv_out = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Export Intelligence Ledger (CSV)",
    csv_out,
    "loyalty_intelligence_export.csv",
    "text/csv",
    key='download-csv'
)
st.markdown("</div>", unsafe_allow_html=True)

# 🔹 4. Model Explanation Section
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("### 📘 How The Model Works")
with st.expander("Explore the Mathematical Intelligence Hierarchy"):
    st.write("""
    Dashboard ini menggunakan kombinasi **Diferensial Momentum** dan **Analisis Recency bias** untuk memprediksi nilai loyalitas pelanggan.
    
    1. **Trend Analysis (`Trend`)**: Mengukur apakah intensitas transaksi pelanggan meningkat atau menurun. T3 (bulan terakhir) diberi beban paling berat, sementara T1 (bulan awal) diberi beban negatif untuk menonjolkan akselerasi.
       - Formula: `Trend = (-2/3 * M1) + (1/3 * M2) + (4/3 * M3)`
       
    2. **Weighted Moving Average (`WMA`)**: Menghitung rata-rata volume transaksi dengan prioritas pada aktivitas terbaru untuk mencerminkan status terkini pelanggan.
       - Formula: `WMA = (0.2 * M1) + (0.3 * M2) + (0.5 * M3)`
       
    3. **Final Loyalty Score**: Gabungan harmonis antara Tren (40%) dan Volume stabil (60%).
       - Formula: `Final = 0.4 * Trend + 0.6 * WMA`
    
    **Klasifikasi Klasik:**
    - 🔴 **Rendah (0–4)**: Pelanggan berisiko churn atau pasif.
    - 🟡 **Sedang (4–7)**: Pelanggan stabil dengan potensi pertumbuhan.
    - 🟢 **Tinggi (7–10)**: Pelanggan loyal dengan nilai kontribusi tinggi.
    """)
st.markdown("</div>", unsafe_allow_html=True)

# FOOTER
st.markdown("<p style='text-align: center; opacity: 0.5; font-size: 0.8rem;'>LoyaltyIQ Alpha v2.4 | Enterprise Predictive Interface | © 2026</p>", unsafe_allow_html=True)
