import streamlit as st
import os
import sys
from pathlib import Path
import warnings
import json
import time
from datetime import datetime
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent))

from src.generation.rag_pipeline import UniversalRAGPipeline

# Page config
st.set_page_config(
    page_title="GitLab Onboarding Intelligence",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
if 'avg_response_time' not in st.session_state:
    st.session_state.avg_response_time = 0
if 'response_times' not in st.session_state:
    st.session_state.response_times = []
if 'system_stats' not in st.session_state:
    st.session_state.system_stats = None
if 'scroll_to' not in st.session_state:
    st.session_state.scroll_to = None

# Complete Enhanced CSS with Animated Background and Smooth Scrolling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html {
        scroll-behavior: smooth;
    }
    
    /* Animated Background - Layer 1: Base Gradient */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1424 100%);
        position: relative;
        overflow-x: hidden;
    }
    
    /* Layer 2: Animated Radial Gradients */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(240, 147, 251, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(79, 172, 254, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 60% 90%, rgba(67, 233, 123, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 90% 30%, rgba(255, 216, 155, 0.1) 0%, transparent 50%);
        animation: backgroundMove 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes backgroundMove {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(5%, -5%) scale(1.05); }
        50% { transform: translate(-5%, 5%) scale(0.95); }
        75% { transform: translate(5%, 5%) scale(1.02); }
    }
    
    /* Layer 3: Animated Grid */
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(79, 172, 254, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(79, 172, 254, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: moveGrid 20s linear infinite;
        pointer-events: none;
        z-index: 1;
    }
    
    @keyframes moveGrid {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    /* Layer 4: Floating Orbs */
    .floating-orbs {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 2;
        overflow: hidden;
    }
    
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.4;
        animation: floatOrb 15s ease-in-out infinite;
    }
    
    .orb-1 {
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(79, 172, 254, 0.6), transparent);
        top: -200px;
        left: -150px;
        animation-delay: 0s;
    }
    
    .orb-2 {
        width: 700px;
        height: 700px;
        background: radial-gradient(circle, rgba(240, 147, 251, 0.5), transparent);
        bottom: -250px;
        right: -200px;
        animation-delay: 2s;
    }
    
    .orb-3 {
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(67, 233, 123, 0.4), transparent);
        top: 40%;
        right: -150px;
        animation-delay: 4s;
    }
    
    .orb-4 {
        width: 550px;
        height: 550px;
        background: radial-gradient(circle, rgba(255, 216, 155, 0.4), transparent);
        top: 10%;
        left: 50%;
        animation-delay: 1s;
    }
    
    .orb-5 {
        width: 650px;
        height: 650px;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.3), transparent);
        bottom: 10%;
        left: -200px;
        animation-delay: 3s;
    }
    
    @keyframes floatOrb {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(40px, -60px) scale(1.1); }
        50% { transform: translate(-40px, 80px) scale(0.9); }
        75% { transform: translate(60px, 40px) scale(1.05); }
    }
    
    /* Content Layer */
    .content-layer {
        position: relative;
        z-index: 10;
    }
    
    /* Hide Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Header */
    .app-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background: rgba(10, 14, 39, 0.85);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 3rem;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .logo-section {
        display: flex;
        flex-direction: column;
        cursor: pointer;
    }
    
    .logo-text {
        font-size: 1.5rem;
        font-weight: 800;
        color: #60a5fa;
        line-height: 1.2;
    }
    
    .logo-subtitle {
        font-size: 0.65rem;
        color: #a78bfa;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    .nav-menu {
        display: flex;
        gap: 2.5rem;
        align-items: center;
    }
    
    .nav-link {
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.95rem;
        transition: color 0.3s;
        cursor: pointer;
        text-decoration: none;
    }
    
    .nav-link:hover {
        color: #60a5fa;
    }
    
    /* Content Spacing */
    .content-wrapper {
        padding-top: 90px;
    }
    
    /* Section Anchors */
    .section-anchor {
        display: block;
        position: relative;
        top: -90px;
        visibility: hidden;
    }
    
    /* Hero */
    .hero-section {
        text-align: center;
        padding: 5rem 2rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .hero-badge {
        display: inline-block;
        padding: 0.6rem 1.5rem;
        background: rgba(102, 126, 234, 0.15);
        border: 1.5px solid rgba(102, 126, 234, 0.4);
        border-radius: 50px;
        color: #667eea;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .hero-title {
        font-size: clamp(2.5rem, 8vw, 5rem);
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 25%, #f472b6 50%, #34d399 75%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -2px;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        max-width: 700px;
        margin: 0 auto 3rem;
        line-height: 1.8;
        font-weight: 300;
    }
    
    /* Section Titles */
    .section-title {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    
    .section-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Steps */
    .steps-container {
        max-width: 900px;
        margin: 4rem auto;
        padding: 0 2rem;
    }
    
    .step-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.4s;
        backdrop-filter: blur(10px);
    }
    
    .step-box:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(15px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
    }
    
    .step-box.step-1 { border-left: 4px solid #60a5fa; }
    .step-box.step-2 { border-left: 4px solid #a78bfa; }
    .step-box.step-3 { border-left: 4px solid #34d399; }
    
    .step-number {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .step-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .step-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Stats */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        max-width: 1200px;
        margin: 3rem auto;
        padding: 0 2rem;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.4s;
        backdrop-filter: blur(10px);
    }
    
    .stat-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.4);
        transform: translateY(-10px);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .stat-label {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .stat-desc {
        font-size: 0.85rem;
        color: #94a3b8;
        line-height: 1.5;
    }
    
    /* Features */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        max-width: 1200px;
        margin: 3rem auto 5rem;
        padding: 0 2rem;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.4s;
        backdrop-filter: blur(10px);
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-10px);
        border-color: rgba(102, 126, 234, 0.4);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.25);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.6;
    }
    
    /* Footer */
    .app-footer {
        background: rgba(10, 14, 39, 0.95);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 3rem 3rem 2rem;
        margin-top: 6rem;
        position: relative;
        z-index: 10;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .footer-section h4 {
        color: #f1f5f9;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    
    .footer-link {
        display: block;
        color: #94a3b8;
        text-decoration: none;
        margin-bottom: 0.7rem;
        font-size: 0.9rem;
        transition: color 0.3s;
        cursor: pointer;
    }
    
    .footer-link:hover {
        color: #60a5fa;
    }
    
    .footer-bottom {
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #64748b;
        font-size: 0.85rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 1rem 3rem;
        font-size: 1.1rem;
        font-weight: 700;
        transition: all 0.3s;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.6);
    }
    
    /* App Styles */
    .answer-box {
        background: rgba(102, 126, 234, 0.08);
        border-left: 4px solid #667eea;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Loading Animation */
    .loading-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1424 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loader {
        position: relative;
        width: 200px;
        height: 200px;
    }
    
    .loader-ring {
        position: absolute;
        width: 100%;
        height: 100%;
        border: 4px solid transparent;
        border-radius: 50%;
        animation: rotate 2s linear infinite;
    }
    
    .loader-ring:nth-child(1) {
        border-top-color: #60a5fa;
        animation-delay: 0s;
    }
    
    .loader-ring:nth-child(2) {
        border-right-color: #a78bfa;
        animation-delay: 0.2s;
        width: 85%;
        height: 85%;
        top: 7.5%;
        left: 7.5%;
    }
    
    .loader-ring:nth-child(3) {
        border-bottom-color: #34d399;
        animation-delay: 0.4s;
        width: 70%;
        height: 70%;
        top: 15%;
        left: 15%;
    }
    
    .loader-ring:nth-child(4) {
        border-left-color: #fbbf24;
        animation-delay: 0.6s;
        width: 55%;
        height: 55%;
        top: 22.5%;
        left: 22.5%;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 3rem;
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399, #fbbf24);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .loading-subtext {
        margin-top: 1rem;
        font-size: 1rem;
        color: #94a3b8;
        animation: fadeInOut 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes fadeInOut {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .loading-dots {
        display: inline-flex;
        gap: 0.5rem;
        margin-left: 0.5rem;
    }
    
    .loading-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        animation: bounce 1.4s ease-in-out infinite;
    }
    
    .loading-dot:nth-child(1) { animation-delay: 0s; }
    .loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .loading-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .features-grid {
            grid-template-columns: 1fr;
        }
        .footer-content {
            grid-template-columns: repeat(2, 1fr);
        }
        .nav-menu {
            display: none;
        }
        .loader {
            width: 150px;
            height: 150px;
        }
    }
    </style>
    
    <script>
    function scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    </script>
""", unsafe_allow_html=True)

def get_system_stats():
    """Get system statistics"""
    stats = {
        'num_documents': 0,
        'embedding_dim': 0,
        'model_name': 'Unknown',
        'vector_store': 'ChromaDB + GCS'
    }
    
    embedding_info_path = Path("models/embeddings/model_info.json")
    if embedding_info_path.exists():
        with open(embedding_info_path, 'r') as f:
            info = json.load(f)
            stats['num_documents'] = info.get('num_embeddings', 0)
            stats['embedding_dim'] = info.get('embedding_dim', 0)
            stats['model_name'] = info.get('model_name', 'Unknown')
    
    return stats

@st.cache_resource
def initialize_pipeline():
    """Initialize RAG pipeline"""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path is None:
        default_creds = Path("mlops-476419-2c1937dab204.json")
        if default_creds.exists():
            creds_path = str(default_creds)
    
    return UniversalRAGPipeline(
        provider="groq",
        use_gcs=True,
        bucket_name="mlops-data-oa",
        project_id="mlops-476419",
        credentials_path=creds_path
    )

def create_response_time_chart(times):
    """Create response time chart"""
    if not times:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=times,
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.update_layout(
        title="Response Time Trend",
        xaxis_title="Query",
        yaxis_title="Time (s)",
        template="plotly_dark",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def show_landing_page():
    """Display complete landing page"""
    
    # Header with working navigation
    st.markdown("""
        <div class="app-header">
            <div class="logo-section" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">
                <div class="logo-text">GitLab</div>
                <div class="logo-subtitle">ONBOARDING INTELLIGENCE</div>
            </div>
            <div class="nav-menu">
                <a href="#how-it-works" class="nav-link">How It Works</a>
                <a href="#features" class="nav-link">Features</a>
                <a href="#get-started" class="nav-link">Get Started</a>
            </div>
        </div>
        
        <div class="floating-orbs">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <div class="orb orb-4"></div>
            <div class="orb orb-5"></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="content-wrapper content-layer">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <div class="hero-badge">Team 13 • Northeastern University MLOps</div>
            <h1 class="hero-title">Transform Your GitLab Team Experience</h1>
            <p class="hero-subtitle">
                Streamline employee orientation with AI-powered guidance, seamless automation, 
                and personalized support for every GitLab team member worldwide.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Launch Button - Centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Launch Intelligence System", key="launch_btn"):
            # Show loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loader">
                        <div class="loader-ring"></div>
                        <div class="loader-ring"></div>
                        <div class="loader-ring"></div>
                        <div class="loader-ring"></div>
                    </div>
                    <div class="loading-text">
                        Initializing AI System
                        <div class="loading-dots">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                    </div>
                    <div class="loading-subtext">Loading RAG pipeline from Google Cloud Storage</div>
                </div>
            """, unsafe_allow_html=True)
            
            time.sleep(2)  # Simulate loading time
            loading_placeholder.empty()
            
            st.session_state.show_landing = False
            st.rerun()
    
    # How It Works Section
    st.markdown('<span id="how-it-works" class="section-anchor"></span>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top: 6rem;"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">How It Works</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Simple, powerful, and intelligent automation at every step</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="steps-container">
            <div class="step-box step-1">
                <span class="step-number">01</span>
                <div class="step-title">Smart Integration</div>
                <div class="step-desc">Seamlessly connect with your existing HR systems and documentation</div>
            </div>
            <div class="step-box step-2">
                <span class="step-number">02</span>
                <div class="step-title">AI Processing</div>
                <div class="step-desc">Advanced language models analyze and understand your company information</div>
            </div>
            <div class="step-box step-3">
                <span class="step-number">03</span>
                <div class="step-title">Intelligent Delivery</div>
                <div class="step-desc">Personalized guidance and answers tailored to each new employee</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tech Stack Section
    st.markdown('<div style="margin-top: 6rem;"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Tech Stack</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Powered by cutting-edge technologies</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-value">🤖</span>
                <div class="stat-label">Groq API</div>
                <div class="stat-desc">Ultra-fast LLM inference with Llama models</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">🎨</span>
                <div class="stat-label">Streamlit</div>
                <div class="stat-desc">Interactive web interface for seamless UX</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">🗄️</span>
                <div class="stat-label">ChromaDB</div>
                <div class="stat-desc">High-performance vector database</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">☁️</span>
                <div class="stat-label">Google Cloud</div>
                <div class="stat-desc">Scalable storage with GCS buckets</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">🔬</span>
                <div class="stat-label">Sentence Transformers</div>
                <div class="stat-desc">State-of-the-art embedding models</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">📊</span>
                <div class="stat-label">MLflow</div>
                <div class="stat-desc">Experiment tracking and model registry</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">🔄</span>
                <div class="stat-label">Apache Airflow</div>
                <div class="stat-desc">Pipeline orchestration and automation</div>
            </div>
            <div class="stat-card">
                <span class="stat-value">🐙</span>
                <div class="stat-label">GitHub Actions</div>
                <div class="stat-desc">CI/CD pipelines and automated testing</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown('<span id="features" class="section-anchor"></span>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top: 6rem;"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Features</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Everything you need for intelligent onboarding</p>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="features-grid">
            <div class="feature-card">
                <span class="feature-icon">🎯</span>
                <div class="feature-title">Smart Automation</div>
                <div class="feature-desc">Automate repetitive onboarding tasks with intelligent workflows</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🧠</span>
                <div class="feature-title">AI Intelligence</div>
                <div class="feature-desc">Leverage advanced AI for personalized employee guidance</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">⚡</span>
                <div class="feature-title">Lightning Fast</div>
                <div class="feature-desc">Get instant answers with blazing-fast performance</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔒</span>
                <div class="feature-title">Enterprise Security</div>
                <div class="feature-desc">Bank-level security protecting sensitive employee data</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🌍</span>
                <div class="feature-title">Global Scale</div>
                <div class="feature-desc">Support for multiple languages and worldwide deployment</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔄</span>
                <div class="feature-title">Seamless Integration</div>
                <div class="feature-desc">Connect with your existing HR systems effortlessly</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown('<span id="get-started" class="section-anchor"></span>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top: 6rem; text-align: center; padding: 3rem 2rem;">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Ready to Transform Your Team Onboarding?</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">GitLab Intelligent Onboarding - Powering teams globally</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Launch Intelligence System Now", key="launch_cta"):
            # Show loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
                <div class="loading-container">
                    <div class="loader">
                        <div class="loader-ring"></div>
                        <div class="loader-ring"></div>
                        <div class="loader-ring"></div>
                        <div class="loader-ring"></div>
                    </div>
                    <div class="loading-text">
                        Initializing AI System
                        <div class="loading-dots">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                    </div>
                    <div class="loading-subtext">Loading RAG pipeline from Google Cloud Storage</div>
                </div>
            """, unsafe_allow_html=True)
            
            time.sleep(2)  # Simulate loading time
            loading_placeholder.empty()
            
            st.session_state.show_landing = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div class="app-footer">
            <div class="footer-content" style="display: flex; justify-content: center;">
                <div class="footer-section">
                    <h4>Team 13 - Northeastern University</h4>
                    <div class="footer-link">Saran Jagadeesan Uma</div>
                    <div class="footer-link">Akshaj Nevgi</div>
                    <div class="footer-link">Lakshmi Vandhanie Ganesh</div>
                    <div class="footer-link">Mithun Dineshkumar</div>
                    <div class="footer-link">Zankhana Pratik Mehta</div>
                </div>
            </div>
            <div class="footer-bottom">
                © 2025 GitLab Intelligent Onboarding • Team 13 - Northeastern University MLOps Course • Built with advanced AI and cutting-edge design
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_app():
    """Display chatbot app with history - CENTERED VERSION"""
    
    # Add the same animated background for consistency
    st.markdown("""
        <div class="floating-orbs">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <div class="orb orb-4"></div>
            <div class="orb orb-5"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Home button
    if st.button("🏠 Home"):
        st.session_state.show_landing = True
        st.rerun()
    
    # Sidebar with history
    with st.sidebar:
        st.image("https://about.gitlab.com/images/press/logo/png/gitlab-logo-gray-rgb.png", width=200)
        
        st.markdown("## 🚀 GitLab Assistant")
        st.markdown("---")
        
        # API Status
        if os.getenv("GROQ_API_KEY"):
            st.success("✅ Groq API Connected")
        else:
            st.warning("⚠️ No API Key")
        
        st.markdown("---")
        
        # Stats
        if st.session_state.system_stats is None:
            st.session_state.system_stats = get_system_stats()
        
        stats = st.session_state.system_stats
        
        st.markdown("### 📊 Session Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.total_queries}</div>
                <div class="metric-label">Queries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_time = st.session_state.avg_response_time
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_time:.1f}s</div>
                <div class="metric-label">Avg Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Response time chart
        if st.session_state.response_times:
            chart = create_response_time_chart(st.session_state.response_times[-10:])
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        
        st.markdown("---")
        
        # Chat History in Sidebar
        if st.session_state.chat_history:
            st.markdown("### 📜 Recent History")
            for i, item in enumerate(st.session_state.chat_history[:5], 1):
                with st.expander(f"{i}. {item['query'][:40]}...", expanded=False):
                    st.caption(f"⏱️ {item.get('response_time', 0):.2f}s")
                    st.caption(f"📚 {item['num_sources']} sources")
        
        st.markdown("---")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.total_queries = 0
            st.session_state.response_times = []
            st.session_state.avg_response_time = 0
            st.rerun()
    
    # --- CENTERED LAYOUT LOGIC STARTS HERE ---
    # We use columns [1, 2, 1] to create a centered channel
    spacer_left, main_content, spacer_right = st.columns([1, 2, 1])
    
    with main_content:
        # Main Content
        st.markdown("<h1 style='text-align: center;'>🦊 GitLab Onboarding Assistant</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #94a3b8; font-weight: 300;'>Ask me anything about GitLab!</h3>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Initialize pipeline
        if st.session_state.rag_pipeline is None:
            with st.spinner("Initializing AI from GCS..."):
                st.session_state.rag_pipeline = initialize_pipeline()
            st.success("✅ Ready!")
        
        # Query input - Now strictly centered
        query_input = st.text_input(
            "Your Question:",
            placeholder="e.g., What is GitLab's sustainability approach?",
            key="query_input",
            label_visibility="collapsed" # Hides label for cleaner look
        )
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Ask button - Centered within the main content column
        # Using inner columns to make the button not full width of the center column
        b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
        with b_col2:
            search_button = st.button("🔍 Ask Now!", use_container_width=True, type="primary")
        
        # Process query
        if search_button and query_input:
            st.session_state.total_queries += 1
            
            with st.spinner("Processing..."):
                start_time = time.time()
                result = st.session_state.rag_pipeline.generate_answer(query_input, k=3)
                response_time = time.time() - start_time
                
                # Update stats
                st.session_state.response_times.append(response_time)
                st.session_state.avg_response_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
                
                # Save to history
                result['response_time'] = response_time
                st.session_state.chat_history.insert(0, result)
            
            st.markdown("---")
            
            # Display answer
            st.markdown("### 💡 Answer")
            st.markdown(f'<div class="answer-box">{result["answer"]}</div>', unsafe_allow_html=True)
            st.markdown(f"⏱️ **Response Time:** {response_time:.2f}s")
            
            # Sources (WITHOUT Type column)
            st.markdown("### 📚 Retrieved Sources")
            
            for i, doc in enumerate(result['sources'], 1):
                title = doc['metadata'].get('title', 'Unknown')
                score = doc.get('rerank_score', doc.get('similarity', 0))
                text = doc['document']
                
                score_emoji = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🟠"
                
                with st.expander(f"{score_emoji} Source {i}: {title} | Relevance: {score:.1%}", expanded=(i==1)):
                    # Only 2 columns: Relevance and Rank (NO Type)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Relevance Score", f"{score:.4f}")
                    with col2:
                        st.metric("Retrieval", "Top-K")
                    
                    st.markdown(f"""
                    <div style="background-color: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; margin-top: 10px;">
                        {text[:500]}{'...' if len(text) > 500 else ''}
                    </div>
                    """, unsafe_allow_html=True)
        
        elif search_button:
            st.warning("⚠️ Please enter a question!")
        
        # Show full conversation history below
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 📜 Full Conversation History")
            
            for i, item in enumerate(st.session_state.chat_history, 1):
                with st.expander(f"#{i} • {item['query']}", expanded=False):
                    st.markdown(f"**💬 Answer:** {item['answer']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Sources", item['num_sources'])
                    with col2:
                        st.metric("Provider", item.get('provider', 'Groq'))
                    with col3:
                        st.metric("Time", f"{item.get('response_time', 0):.2f}s")

# Main logic
if st.session_state.show_landing:
    show_landing_page()
else:
    show_app()