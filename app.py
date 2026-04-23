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
    page_title="LoyaltyIQ | Strategic Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STATE MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = "🏠 Executive Dashboard"

# --- PREMIUM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* App Background */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1e1b4b 0%, #0f172a 100%) !important;
        color: #f1f5f9;
        font-family: 'Outfit', 'Inter', sans-serif !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0rem !important; /* Hilangkan spasi gede di atas */
        gap: 0.1rem !important; /* Rapatkan gap antar elemen global sidebar */
    }

    /* Sidebar Navigation Menu Buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important;
        color: #94a3b8 !important;
        border: 1px solid transparent !important;
        padding: 0.4rem 1rem !important; /* Kurangi padding vertikal */
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        margin: 0px !important;
        width: 100% !important;
        border-radius: 10px !important;
        display: block !important;
        text-align: left !important;
    }

    /* Memaksa text di dalam button Streamlit agar benar-benar ke kiri */
    [data-testid="stSidebar"] .stButton > button div[data-testid="stMarkdownContainer"] p {
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] .stButton > button div {
        justify-content: flex-start !important;
        text-align: left !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(99, 102, 241, 0.08) !important;
        color: #fff !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
    }

    /* Target Active Button based on session state label (Logic via Python) */
    .sidebar-active-btn {
        background-color: rgba(99, 102, 241, 0.15) !important;
        color: #818cf8 !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }

    /* Container Height Synchronization & Layout */
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
        gap: 1.5rem !important;
    }

    /* Modern Glassmorphism Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(30, 41, 59, 0.3) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 1.25rem !important;
        height: 100% !important;
        padding: 1.5rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        display: flex;
        flex-direction: column;
    }

    /* Remove Black Input Artifacts */
    div[data-baseweb="input"], div[data-baseweb="number-input"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        height: 44px !important;
        color: #FFFFFF !important;
        transition: all 0.3s ease;
    }

    /* Recalculate Model Button - BRIGHT VIBRANT INDIGO */
    div[data-testid="stForm"] div.stButton > button, .main-btn button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        height: 50px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.2s ease !important;
        text-transform: none !important;
        width: 100% !important;
    }

    div[data-testid="stForm"] div.stButton > button:hover, .main-btn button:hover {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        transform: translateY(-2px) !important;
    }

    /* Custom Labels */
    .section-title {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
        letter-spacing: -0.02em;
    }

    /* Digital Input Styling */
    div[data-baseweb="input"], div[data-baseweb="number-input"] {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5) !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4), inset 0 2px 10px rgba(0,0,0,0.5) !important;
    }

    /* KPI Grid */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .kpi-card {
        background: rgba(30, 41, 59, 0.4);
        padding: 1.5rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.3s ease;
    }

    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2rem; font-weight: 900; color: #fff;'>Loyalty<span style='color: #6366f1;'>IQ</span></h1>
        <p style='color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;'>Intelligence Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom Button Navigation
    def nav_button(label):
        is_active = st.session_state.page == label
        # We use a container to apply different ID if needed, 
        # but Streamlit buttons are hard to style individually based on state without hacks.
        # Let's use standard button with a little trick.
        if st.button(label, key=f"btn_{label}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.page = label
            st.rerun()

    nav_button("🏠 Executive Dashboard")
    nav_button("🔮 Predictive Model")
    nav_button("📊 Customer Intelligence")
    nav_button("⚙️ System Configuration")
    
    st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.1'>", unsafe_allow_html=True)
    
    st.markdown("<h4 style='color: #fff; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.8rem; margin-top: 0.5rem;'>System Status</h4>", unsafe_allow_html=True)
    st.success("Core Engine: Online")
    st.info("Last Sync: Just now")
    
    st.markdown("<div style='position: fixed; bottom: 20px; left: 20px; color: #475569; font-size: 0.7rem;'>v4.2.0 | Strategic Intelligence Hub</div>", unsafe_allow_html=True)

# --- CORE LOGIC ---
@st.cache_data
def run_loyalty_model(m1, m2, m3):
    # Momentum Calculation (Hybrid Exponential Weighting)
    trend = (-2/3 * m1) + (1/3 * m2) + (4/3 * m3)
    wma = (0.2 * m1) + (0.3 * m2) + (0.5 * m3)
    raw_score = (0.4 * trend) + (0.6 * wma)
    
    # Scale Normalization
    base_scale = 1.0
    if max(m1, m2, m3) > 100:
        base_scale = 1000.0 if max(m1, m2, m3) > 1000 else 100.0
    
    thr_tinggi = 7 * base_scale
    thr_sedang = 4 * base_scale
    
    category = "Rendah"
    if raw_score >= thr_tinggi: category = "Tinggi"
    elif raw_score >= thr_sedang: category = "Sedang"
    
    insight = "Stabilitas performa terdeteksi"
    if trend > (1.5 * base_scale): insight = "🚀 Momentum Pertumbuhan Agresif"
    elif trend < (-0.5 * base_scale): insight = "⚠️ Risiko Penurunan Signifikan"
    elif raw_score > (8 * base_scale): insight = "💎 Elite Member Engagement"
    
    return {
        "score": round(raw_score, 2),
        "category": category,
        "insight": insight
    }

def process_bulk_data(df):
    # Handle both T1-T3 and M1-M3 mappings
    mapping = {"T1":"T1", "T2":"T2", "T3":"T3"}
    if "M1" in df.columns: mapping = {"T1":"M1", "T2":"M2", "T3":"M3"}
    
    if not all(k in df.columns for k in ["Nama", mapping["T1"], mapping["T2"], mapping["T3"]]):
        return None
        
    results = []
    for _, row in df.iterrows():
        res = run_loyalty_model(row[mapping["T1"]], row[mapping["T2"]], row[mapping["T3"]])
        results.append({
            "Nama": row["Nama"],
            "M1": row[mapping["T1"]], "M2": row[mapping["T2"]], "M3": row[mapping["T3"]],
            "Score": res["score"],
            "Category": res["category"],
            "Insight": res["insight"],
            "Timestamp": time.time()
        })
    return pd.DataFrame(results)

# --- DATA INITIALIZATION ---
if "master_data" not in st.session_state:
    mock_df = pd.DataFrame([
        {"Nama": "Adi Guna", "T1": 8000, "T2": 9000, "T3": 9500},
        {"Nama": "Siska Amalia", "T1": 4000, "T2": 5000, "T3": 3000},
        {"Nama": "Budi Hartono", "T1": 6000, "T2": 7000, "T3": 8500},
        {"Nama": "Lintang Sore", "T1": 9000, "T2": 8000, "T3": 9200},
        {"Nama": "Maya Putri", "T1": 2000, "T2": 2500, "T3": 2800},
        {"Nama": "Doni Aris", "T1": 7000, "T2": 7200, "T3": 7100}
    ])
    st.session_state.master_data = process_bulk_data(mock_df)

curr_data = st.session_state.master_data

# --- PAGE ROUTING ---
if st.session_state.page == "🏠 Executive Dashboard":
    st.markdown("""
    <div style='margin-bottom: 2.5rem;'>
        <div style='background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); color: #818cf8; padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; font-weight: 700; margin-bottom: 1rem; display: inline-block;'>
            EXECUTIVE OVERVIEW
        </div>
        <h1 style='font-size: 3.5rem; font-weight: 900; line-height: 1.1; color: #fff; margin-bottom: 0.5rem;'>Loyalty Intelligence <span style='color: #6366f1;'>Hub</span></h1>
        <p style='color: #94a3b8; font-size: 1.1rem; max-width: 600px;'>Pemantauan real-time performa loyalitas dan tren pertumbuhan poin pelanggan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Grid
    k1, k2, k3, k4, k5 = st.columns(5)
    
    def render_kpi(col, label, val, color="#f8fafc", trend=""):
        col.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.08); height: 100%;'>
            <div style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem;'>{label}</div>
            <div style='font-size: 2.2rem; font-weight: 900; color: {color};'>{val}</div>
            <div style='color: #10b981; font-size: 0.7rem; font-weight: 600; margin-top: 0.5rem;'>{trend}</div>
        </div>
        """, unsafe_allow_html=True)

    render_kpi(k1, "Total Customers", f"{len(curr_data)}", "#fff", "↑ 12% vs last month")
    render_kpi(k2, "Avg Point Index", f"{curr_data['Score'].mean():.1f}", "#6366f1", "↑ 2.4% yield")
    render_kpi(k3, "Total Points Velocity", f"{int(curr_data['M3'].sum()):,}", "#10b981", "↑ 45.2k current")
    render_kpi(k4, "Elite Ratio", f"{( (curr_data['Score']>=7).sum()/len(curr_data)*100 ):.0f}%", "#f59e0b", "Stable conversion")
    render_kpi(k5, "Retention Risk", f"{( (curr_data['Score']<4).sum()/len(curr_data)*100 ):.0f}%", "#f43f5e", "↓ 5% improved")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row 1
    c1, c2 = st.columns([1.5, 1])
    with c1:
        with st.container(border=True):
            st.markdown("### **Loyalty Points Progression (Top 10)**")
            top_10 = curr_data.sort_values("Score", ascending=True).tail(10)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=top_10["M1"], y=top_10["Nama"], name="Month 1", orientation='h', marker_color='rgba(99, 102, 241, 0.2)'))
            fig.add_trace(go.Bar(x=top_10["M3"], y=top_10["Nama"], name="Month 3 (Predicted)", orientation='h', marker_color='#6366f1'))
            fig.update_layout(
                barmode='overlay', 
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=450, 
                margin=dict(l=0, r=0, t=30, b=80),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("### **Category Distribution**")
            cv = curr_data["Category"].value_counts()
            fig = px.pie(values=cv.values, names=cv.index, hole=0.7, 
                         color_discrete_map={'Tinggi':'#10b981', 'Sedang':'#f59e0b', 'Rendah':'#f43f5e'})
            fig.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=450, 
                showlegend=True, 
                margin=dict(l=0, r=0, t=30, b=80),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

    # Charts Row 2
    st.markdown("<br>", unsafe_allow_html=True)
    c3, c4 = st.columns([1, 1])
    with c3:
        with st.container(border=True):
            st.markdown("### **Point Growth Trajectory**")
            # Sample trend data
            trend_df = pd.DataFrame({
                "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "Points": [45000, 48000, 52000, 50000, 55000, 59000]
            })
            fig = px.area(trend_df, x="Month", y="Points", line_shape="spline", color_discrete_sequence=['#10b981'])
            fig.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=400, 
                margin=dict(l=0, r=0, t=30, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        with st.container(border=True):
            st.markdown("### **Sentiment vs Prediction Analysis**")
            fig = px.scatter(curr_data, x="M1", y="Score", size="M3", color="Category", 
                             hover_name="Nama", template="plotly_dark",
                             color_discrete_map={'Tinggi':'#10b981', 'Sedang':'#f59e0b', 'Rendah':'#f43f5e'})
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=400, 
                margin=dict(l=0, r=0, t=30, b=80),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "🔮 Predictive Model":
    st.markdown("""
    <div style='margin-bottom: 2.5rem;'>
        <h1 style='font-size: 2.5rem; font-weight: 800; color: #fff;'>Predictive <span style='color: #6366f1;'>Engine</span></h1>
        <p style='color: #94a3b8;'>Simulasikan atau proses data historis untuk memprediksi perolehan poin loyalitas masa depan.</p>
    </div>
    """, unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🎯 Individual Prediction", "📂 Intelligent Bulk Upload"])
    
    with t1:
        cc1, cc2 = st.columns([1, 1.3], gap="large")
        with cc1:
            with st.container(border=True):
                st.markdown("<div class='section-title'>Parameter Input</div>", unsafe_allow_html=True)
                with st.form("ind_pred_form", border=False):
                    f_name = st.text_input("Customer Name", placeholder="e.g. John Doe")
                    m1v = st.number_input("Month 1 Points", value=5000.0)
                    m2v = st.number_input("Month 2 Points", value=5500.0)
                    m3v = st.number_input("Month 3 Points", value=6000.0)
                    submit = st.form_submit_button("Generate Prediction")
                    
                    if submit:
                        res = run_loyalty_model(m1v, m2v, m3v)
                        st.session_state.temp_res = {**res, "name": f_name, "m1": m1v, "m2": m2v, "m3": m3v}
                        st.rerun()

        with cc2:
            with st.container(border=True):
                st.markdown("<div class='section-title'>Outcome Intelligence</div>", unsafe_allow_html=True)
                res = st.session_state.get("temp_res", {"score":0, "category":"STANDBY", "insight":"Ready for analysis", "name":""})
                
                b_col = "#64748b"
                if res["category"] == "Tinggi": b_col = "#10b981"
                elif res["category"] == "Sedang": b_col = "#f59e0b"
                elif res["category"] == "Rendah": b_col = "#f43f5e"
                
                score_norm = min(max(int((res['score'] / 10000 * 100) if res['score'] > 100 else (res['score'] * 10)), 0), 100)
                
                st.markdown(f"""
                <div style='display: flex; flex-direction: column; align-items: center; padding: 2rem 0; height: 100%; justify-content: space-around;'>
                    <div style='position: relative; width: 240px; height: 240px; border-radius: 50%; background: conic-gradient({b_col} {score_norm}%, rgba(255,255,255,0.05) 0); display: flex; align-items: center; justify-content: center; box-shadow: 0 0 40px {b_col}20;'>
                        <div style='position: absolute; inset: 15px; background: #0f172a; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                            <span style='color: #64748b; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.2em;'>PREDICT</span>
                            <span style='font-size: 4.5rem; color: #fff; font-weight: 900;'>{res['score']:.1f}</span>
                        </div>
                    </div>
                    <div style='text-align: center; margin-top: 2rem;'>
                        <div style='background: {b_col}20; color: {b_col}; padding: 8px 30px; border-radius: 50px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em; display: inline-block; margin-bottom: 1rem;'>{res['category']}</div>
                        <p style='color: #94a3b8; font-style: italic; font-size: 1.1rem;'>"{res['insight']}"</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.get("temp_res"):
                    if st.button("📥 Archive to Master Database", use_container_width=True):
                        new_row = pd.DataFrame([{
                            "Nama": res["name"] if res["name"] else "Anonymous",
                            "M1": res["m1"], "M2": res["m2"], "M3": res["m3"],
                            "Score": res["score"], "Category": res["category"], "Insight": res["insight"],
                            "Timestamp": time.time()
                        }])
                        st.session_state.master_data = pd.concat([st.session_state.master_data, new_row], ignore_index=True)
                        del st.session_state.temp_res
                        st.toast("Success: Record permanented in vault", icon="🔒")
                        st.rerun()

    with t2:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Datasets Ingestion</div>", unsafe_allow_html=True)
            u_file = st.file_uploader("Drop CSV or XLSX files", type=["csv", "xlsx"])
            if u_file:
                up_df = pd.read_csv(u_file) if u_file.name.endswith('.csv') else pd.read_excel(u_file)
                p_df = process_bulk_data(up_df)
                if p_df is not None:
                    st.success(f"Successfully processed {len(p_df)} records.")
                    if st.button("Merge with Master Database"):
                        st.session_state.master_data = pd.concat([st.session_state.master_data, p_df], ignore_index=True).drop_duplicates(subset=["Nama"], keep="last")
                        st.toast("Intelligence Cloud Synced.")
                        st.rerun()
                else:
                    st.error("Invalid File Format. Ensure columns: Nama, T1, T2, T3 (or M1, M2, M3)")

elif st.session_state.page == "📊 Customer Intelligence":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1 style='font-size: 2.5rem; font-weight: 800; color: #fff;'>Customer <span style='color: #6366f1;'>Vault</span></h1>
        <p style='color: #94a3b8;'>Eksplorasi data pelanggan dan segmentasi performa secara mendalam.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### **Global Customer Explorer**")
        search = st.text_input("🔍 Search Database", placeholder="Cari nama pelanggan...")
        filtered = curr_data[curr_data["Nama"].str.contains(search, case=False)] if search else curr_data
        
        st.dataframe(filtered.sort_values("Score", ascending=False), 
                     use_container_width=True, 
                     hide_index=True,
                     column_config={
                         "Score": st.column_config.ProgressColumn("Loyalty Points Index", min_value=0, max_value=12000 if curr_data['Score'].max() > 100 else 10),
                         "Timestamp": st.column_config.DatetimeColumn("Analyzed At")
                     })

    st.markdown("<br>", unsafe_allow_html=True)
    cl1, cl2 = st.columns(2)
    with cl1:
        with st.container(border=True):
            st.markdown("### **Performance Correlation**")
            fig = px.density_heatmap(curr_data, x="M1", y="M3", text_auto=True, color_continuous_scale="Viridis")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig, use_container_width=True)
            
    with cl2:
        with st.container(border=True):
            st.markdown("### **Segment Velocity**")
            fig = px.box(curr_data, x="Category", y="Score", points="all", color="Category",
                         color_discrete_map={'Tinggi':'#10b981', 'Sedang':'#f59e0b', 'Rendah':'#f43f5e'})
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("### **Intelligence System Configuration**")
    with st.container(border=True):
        st.info("System is running in Optimal Performance Mode.")
        st.write("Target Confidence: 94.2%")
        st.write("Model Type: Hybrid Momentum Prediction v4")
        if st.button("Reset Intelligence Database", type="secondary"):
            del st.session_state.master_data
            st.rerun()

st.markdown("<br><hr style='opacity: 0.1'><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #475569; font-size: 0.8rem;'>Copyright © 2024 LoyaltyIQ Strategic Intelligence. All rights reserved.</div>", unsafe_allow_html=True)
