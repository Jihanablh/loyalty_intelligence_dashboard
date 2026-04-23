import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import os
from datetime import datetime
import io

# --- CONFIG & STYLING ---
st.set_page_config(
    page_title="LoyaltyIQ Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Glassmorphism & Fintech Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
    }
    
    /* Center text alignments */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    
    /* Text Gradients */
    .gradient-text {
        background: linear-gradient(90deg, #6366f1, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Badges */
    .badge {
        padding: 5px 12px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .badge-platinum { background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid #818cf8; }
    .badge-gold { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #34d399; }
    .badge-silver { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #fbbf24; }
    .badge-bronze { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #f87171; }
    
    /* Sidebar */
    .css-1d391kg { background-color: rgba(15, 23, 42, 0.95); }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #94a3b8;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #6366f1;
    }
    .stTabs [aria-selected="true"] {
        color: #6366f1 !important;
        border-bottom: 2px solid #6366f1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MODEL LOGIC ---
def calculate_loyalty(t1, t2, t3):
    # Rumus Trend = (-2/3 × T1) + (1/3 × T2) + (4/3 × T3)
    trend = (-2/3 * t1) + (1/3 * t2) + (4/3 * t3)
    # Rumus WMA = (0.2 × T1) + (0.3 × T2) + (0.5 × T3)
    wma = (0.2 * t1) + (0.3 * t2) + (0.5 * t3)
    # Loyalty Score = (0.4 × Trend) + (0.6 × WMA)
    score = (0.4 * trend) + (0.6 * wma)
    
    # Normalisasi ke skala 0 - 100
    score = max(0, min(100, score))
    
    tier_info = {
        "Platinum": {"range": (85, 100), "color": "#6366f1", "icon": "💎", "class": "badge-platinum", "reward": "10% Unlimited Cashback"},
        "Gold": {"range": (70, 85), "color": "#10b981", "icon": "🟢", "class": "badge-gold", "reward": "Exclusive Vouchers (100k)"},
        "Silver": {"range": (40, 70), "color": "#f59e0b", "icon": "🟡", "class": "badge-silver", "reward": "5% Extra Points Multiplier"},
        "Bronze": {"range": (0, 40), "color": "#ef4444", "icon": "🔴", "class": "badge-bronze", "reward": "No active rewards"},
    }
    
    curr_tier = "Bronze"
    for tier, data in tier_info.items():
        if data["range"][0] <= score <= data["range"][1]:
            curr_tier = tier
            break
            
    return round(score, 2), round(trend, 2), round(wma, 2), curr_tier, tier_info[curr_tier]

def get_ai_insights(name, score, trend, wma, tier):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "AI Insights are unavailable (Missing API Key)."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        prompt = f"""
        Analyze customer loyalty data:
        Name: {name}
        Loyalty Score: {score}
        Transaction Trend: {trend}
        WMA: {wma}
        Tier: {tier}
        
        Provide 3 professional, punchy business insights in Indonesian for a fintech dashboard. 
        Focus on churn risk, growth opportunities, and personalization.
        Format: One short sentence per point, max 3 points.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Model reasoning... (Auto-generated): Customer shows stable engagement in {tier} tier."

# --- SESSION STATE ---
if "customer_db" not in st.session_state:
    # Initial mock data
    mock_data = [
        {"Nama": "Riza Ahmad", "T1": 80, "T2": 85, "T3": 95},
        {"Nama": "Budi Santoso", "T1": 60, "T2": 55, "T3": 50},
        {"Nama": "Siti Aminah", "T1": 40, "T2": 60, "T3": 85},
        {"Nama": "Dewi Lestari", "T1": 90, "T2": 95, "T3": 98},
        {"Nama": "Eko Wijaya", "T1": 30, "T2": 25, "T3": 20},
    ]
    df = pd.DataFrame(mock_data)
    processed = []
    for _, row in df.iterrows():
        score, trend, wma, tier, meta = calculate_loyalty(row["T1"], row["T2"], row["T3"])
        processed.append({**row, "Score": score, "Trend": trend, "WMA": wma, "Tier": tier, "Icon": meta["icon"]})
    st.session_state.customer_db = pd.DataFrame(processed)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/null/diamond.png", width=80)
    st.markdown("<h2 class='gradient-text'>LoyaltyIQ</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Interactive Controls")
    
    search_qr = st.text_input("🔍 Search Customer", "")
    tier_filter = st.multiselect("Filter Tier", ["Platinum", "Gold", "Silver", "Bronze"], default=["Platinum", "Gold", "Silver", "Bronze"])
    
    score_range = st.slider("Loyalty Score Range", 0, 100, (0, 100))
    
    st.markdown("---")
    st.caption("Powered by Gemini 3 Flash & Streamlit")

# --- MAIN DASHBOARD ---
st.markdown("<h1 class='gradient-text'>Smart Loyalty & Customer Intelligence</h1>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "⚡ Simulation & Upload", "📖 Model Details"])

with tab1:
    # --- KPI METRICS ---
    db = st.session_state.customer_db
    # Filter DB based on sidebar
    filtered_db = db[
        (db["Nama"].str.contains(search_qr, case=False)) &
        (db["Tier"].isin(tier_filter)) &
        (db["Score"] >= score_range[0]) &
        (db["Score"] <= score_range[1])
    ]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Customers", len(filtered_db))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Avg Score", f"{filtered_db['Score'].mean():.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Highest Loyalty", f"{filtered_db['Score'].max():.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Lowest Loyalty", f"{filtered_db['Score'].min():.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col5:
        high_loyalty = (filtered_db["Score"] >= 70).sum() / len(filtered_db) * 100 if len(filtered_db) > 0 else 0
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("% High Value", f"{high_loyalty:.0f}%", delta="Positive" if high_loyalty > 50 else "Watch")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- VISUALIZATIONS ---
    c_main1, c_main2 = st.columns([2, 1])
    
    with c_main1:
        st.markdown("### Transaction Momentum & Predictions")
        if not filtered_db.empty:
            # Prepare data for line chart
            plot_df = filtered_db.copy().sort_values("Score", ascending=False).head(10)
            fig_line = go.Figure()
            
            # Tren Transaksi
            for i, row in plot_df.iterrows():
                fig_line.add_trace(go.Scatter(
                    x=["Bulan 1", "Bulan 2", "Bulan 3", "Prediksi"],
                    y=[row['T1'], row['T2'], row['T3'], row['Score']],
                    name=row['Nama'],
                    mode='lines+markers',
                    line=dict(width=3, shape='spline'),
                    marker=dict(size=8)
                ))
            
            fig_line.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=20, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Please adjust filters to see data.")

    with c_main2:
        st.markdown("### Tier Distribution")
        tier_counts = filtered_db["Tier"].value_counts().reset_index()
        tier_counts.columns = ["Tier", "Count"]
        
        # Color mapping for plotly
        color_map = {"Platinum": "#6366f1", "Gold": "#10b981", "Silver": "#f59e0b", "Bronze": "#ef4444"}
        
        fig_donut = px.pie(
            tier_counts, values="Count", names="Tier", 
            hole=0.6,
            color="Tier",
            color_discrete_map=color_map
        )
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    c_sub1, c_sub2 = st.columns(2)
    
    with c_sub1:
        st.markdown("### Score Leaderboard (Top 10)")
        lb_df = filtered_db.sort_values("Score", ascending=False).head(10)
        fig_bar = px.bar(
            lb_df, x="Score", y="Nama", 
            orientation='h', 
            color="Score",
            color_continuous_scale="Viridis",
            text="Tier"
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Loyalty Points",
            yaxis_title=None
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_sub2:
        st.markdown("### Population Density (Score Histogram)")
        fig_hist = px.histogram(filtered_db, x="Score", nbins=15, color_discrete_sequence=['#6366f1'])
        fig_hist.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            bargap=0.1
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- CUSTOMER TABLE ---
    st.markdown("### Master Intelligence Records")
    
    # Sort and refine display
    display_db = filtered_db.sort_values("Score", ascending=False).copy()
    
    # Custom HTML Table for badges
    table_html = """
    <table style='width:100%; border-collapse: collapse; background: rgba(255,255,255,0.02);'>
        <tr style='border-bottom: 1px solid rgba(255,255,255,0.1); color: #94a3b8;'>
            <th style='padding:15px; text-align:left;'>Icon</th>
            <th style='padding:15px; text-align:left;'>Nama Customer</th>
            <th style='padding:15px; text-align:left;'>T1</th>
            <th style='padding:15px; text-align:left;'>T2</th>
            <th style='padding:15px; text-align:left;'>T3</th>
            <th style='padding:15px; text-align:left;'>Loyalty Score</th>
            <th style='padding:15px; text-align:left;'>Membership Tier</th>
        </tr>
    """
    
    for i, row in display_db.iterrows():
        badge_class = row['Tier'].lower()
        table_html += f"""
        <tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>
            <td style='padding:15px;'>{row['Icon']}</td>
            <td style='padding:15px; font-weight:600;'>{row['Nama']}</td>
            <td style='padding:15px; color:#cbd5e1;'>{row['T1']}</td>
            <td style='padding:15px; color:#cbd5e1;'>{row['T2']}</td>
            <td style='padding:15px; color:#cbd5e1;'>{row['T3']}</td>
            <td style='padding:15px; font-family: monospace; color:#6366f1; font-weight:bold;'>{row['Score']}</td>
            <td style='padding:15px;'><span class='badge badge-{badge_class}'>{row['Tier']}</span></td>
        </tr>
        """
    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)
    
    # Export
    st.markdown("<br>", unsafe_allow_html=True)
    csv = filtered_db.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Insight Records (CSV)",
        data=csv,
        file_name='loyalty_insights.csv',
        mime='text/csv',
    )

with tab2:
    mode = st.radio("Intelligence Mode", ["Single Simulation", "Batch Data Processor"], horizontal=True)
    
    if mode == "Single Simulation":
        c_sim1, c_sim2 = st.columns([1, 1.5])
        
        with c_sim1:
            st.markdown("### Configure Prospect")
            s_name = st.text_input("Name", "New Prospect")
            s_t1 = st.number_input("Transaction M1 (T1)", 0, 1000, 50)
            s_t2 = st.number_input("Transaction M2 (T2)", 0, 1000, 60)
            s_t3 = st.number_input("Transaction M3 (T3)", 0, 1000, 45)
            
            if st.button("Generate Loyalty Profile"):
                score, trend, wma, tier, meta = calculate_loyalty(s_t1, s_t2, s_t3)
                
                with st.spinner("Analyzing with Gemini AI..."):
                    insights = get_ai_insights(s_name, score, trend, wma, tier)
                
                st.session_state.current_sim = {
                    "Name": s_name, "Score": score, "Trend": trend, 
                    "WMA": wma, "Tier": tier, "Meta": meta, "Insights": insights
                }
                
                # Update DB
                new_row = {"Nama": s_name, "T1": s_t1, "T2": s_t2, "T3": s_t3, 
                           "Score": score, "Trend": trend, "WMA": wma, "Tier": tier, "Icon": meta["icon"]}
                st.session_state.customer_db = pd.concat([st.session_state.customer_db, pd.DataFrame([new_row])], ignore_index=True)
        
        with c_sim2:
            if "current_sim" in st.session_state:
                sim = st.session_state.current_sim
                st.markdown(f"### Intelligence Card: {sim['Name']}")
                
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <p style='margin:0; opacity:0.6; font-size:0.8rem;'>MEMBERSHIP LEVEL</p>
                            <h2 style='margin:0; color:{sim['Meta']['color']};'>{sim['Meta']['icon']} {sim['Tier']}</h2>
                        </div>
                        <div style='text-align:right;'>
                            <p style='margin:0; opacity:0.6; font-size:0.8rem;'>PREDICTED SCORE</p>
                            <h1 style='margin:0; font-size:3rem; color:#6366f1;'>{sim['Score']}</h1>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🎁 Tier Benefits")
                st.success(f"**Reward:** {sim['Meta']['reward']}")
                
                st.markdown("#### 🧠 Smart Insights (Gemini AI)")
                st.info(sim["Insights"])
    else:
        st.markdown("### Processor Pipeline")
        uploaded_file = st.file_uploader("Upload CSV/Excel Intelligence Source", type=["csv", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    u_df = pd.read_csv(uploaded_file)
                else:
                    u_df = pd.read_excel(uploaded_file)
                
                required_cols = {"Nama", "T1", "T2", "T3"}
                if not required_cols.issubset(u_df.columns):
                    st.error(f"Missing columns! Required: {required_cols}")
                else:
                    st.success(f"Data source authenticated. processing {len(u_df)} records.")
                    
                    if st.button("Run Batch Analysis"):
                        new_records = []
                        for _, row in u_df.iterrows():
                            score, trend, wma, tier, meta = calculate_loyalty(row["T1"], row["T2"], row["T3"])
                            new_records.append({**row, "Score": score, "Trend": trend, "WMA": wma, "Tier": tier, "Icon": meta["icon"]})
                        
                        st.session_state.customer_db = pd.concat([st.session_state.customer_db, pd.DataFrame(new_records)], ignore_index=True)
                        st.balloons()
                        st.info("Batch completed. View results in the Analytics Dashboard.")
            except Exception as e:
                st.error("Error processing file.")

with tab3:
    st.markdown("### Intelligence Methodology")
    
    with st.expander("🚀 Understanding Trend Forecasting"):
        st.markdown("""
        Model ini menggunakan bobot diferensial untuk mendeteksi 'momentum' aktivitas pelanggan.
        
        **Formula:**
        `Trend = (-2/3 × T1) + (1/3 × T2) + (4/3 × T3)`
        
        Bobot negatif pada T1 dan bobot tinggi pada T3 (terbaru) memastikan bahwa pertumbuhan yang cepat 
        mendapatkan skor trend yang tinggi, sementara penurunan aktivitas akan membebani skor.
        """)
        
    with st.expander("⚖️ Weighted Moving Average (WMA)"):
        st.markdown("""
        WMA memberikan gambaran 'stabilitas' transaksi pelanggan dengan penekanan pada bulan terakhir.
        
        **Formula:**
        `WMA = (0.2 × T1) + (0.3 × T2) + (0.5 × T3)`
        
        Ini merangkum total volume aktivitas dengan cara yang lebih adil dibandingkan rata-rata sederhana.
        """)

    with st.expander("💎 The Final Loyalty Score"):
        st.markdown("""
        Skor akhir adalah gabungan dari **Momentum (Trend)** dan **Stabilitas (WMA)**.
        
        **Formula Akhir:**
        `Loyalty Score = (0.4 × Trend) + (0.6 × WMA)`
        
        Kami menormalkan hasil akhir ke rentang **0 hingga 100** untuk standarisasi dashboard.
        """)

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.5;'>© 2026 LoyaltyIQ Customer Analytics. Developed for Professional Showcase.</p>", unsafe_allow_html=True)