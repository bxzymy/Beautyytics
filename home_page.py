import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

TEXT_CONTENT = {
    "zh": {
        "title": "妆策灵析",
        "subtitle": "你的数据分析助手",
        "button_text": "立即尝试 ➤",
        "lang_toggle": "English",
        "section_title": "解决行业痛点",
        "features": {
            "title1": "🚫 非技术人员难以高效获取洞察",
            "body1": "虽有强烈的数据驱动意愿，但SQL门槛高，BI工具配置复杂，导致业务人员依赖技术团队，难以独立完成数据探索。",
            "title2": "📊 模板化报表缺乏灵活性与智能判断",
            "body2": "常规报表以'看数据'为主，缺乏'讲结果、提建议'的能力，难以针对具体场景（如促销效果、导购行为）给出智能洞察。"
        },
        "benefits_title": "✨ 智能分析引擎自动解读数据",
        "benefits": [
            "💬 自然语言生成分析报告 | 📈 智能预测业务趋势",
        ],
    },
    "en": {
        "title": "Beautyytics",
        "subtitle": "Your Data Analysis Assistant",
        "button_text": "Try Now ➤",
        "lang_toggle": "中文",
        "section_title": "Industry Pain Points",
        "features": {
            "title1": "🚫 Insights Are Hard to Get for Non-Technical Staff",
            "body1": "Despite a strong desire to be data-driven, the high barrier of SQL and complex BI tools prevent independent data exploration.",
            "title2": "📊 Templated Reports Lack Flexibility and Intelligence",
            "body2": "Standard reports focus on 'viewing data' but lack the ability to 'present results and suggest actions,' failing to provide smart insights for specific scenarios.",
        },
        "benefits_title": "✨ Smart Analysis Engine Automatically Interprets Data",
        "benefits": [
            "💬 Generates analysis reports in natural language | 📈 Intelligently predicts business trends",
        ],
    }
}

CSS = """
/* 基础和背景样式 */
[data-testid="stAppViewContainer"] {
    background: url('/app/static/bg3.png') no-repeat center center fixed;
    background-size: cover;
}
#MainMenu, footer, header { visibility: hidden; }

/* 主内容区块 */
.main .block-container {
    background-color: rgba(0, 0, 0, 0.7) !important;
    border-radius: 15px;
    padding: 2rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
} 

/* 首页特定样式 */
.logo-container { 
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 100;
}
.logo-img { 
    height: 50px;
    width: auto;
}
.main-title {
    font-size: 4.5rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #ff3366, #ff9933, #ffcc33, #33cc33, #3399ff, #3366ff, #9933ff, #ff33cc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    background-size: 400% 100%;
    animation: rainbow 6s linear infinite, pulse 2s ease infinite;
    margin-bottom: 0.5rem !important;
    letter-spacing: 1px;
    font-family: 'Arial Black', sans-serif;
    filter: drop-shadow(0 0 8px rgba(255,255,255,0.4));
}
.subtitle {
    text-align: center;
    color: #F0F4FA !important;
    font-size: 1.5rem !important;
    max-width: 720px;
    margin: 1rem auto 2rem auto !important;
    line-height: 1.4;
}
.feature-card {
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem auto;
    border-left: 4px solid #4ade80;
    transition: all 0.3s ease;
    text-align: center;
}
.feature-card:hover { 
    transform: translateY(-3px);
}
.feature-title { 
    color: white !important;
    font-size: 1.4rem !important;
    margin: 0 0 0.8rem 0 !important;
    font-weight: 700;
}
.feature-body { 
    color: #F0F4FA !important;
    font-size: 1.1rem !important;
    line-height: 3.0;
}
.benefits-container {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0 auto 2rem auto;
    text-align: center;
}
.benefits-title {
    color: white !important;
    font-size: 1.8rem !important;
    text-align: center;
    margin-bottom: 1.5rem !important;
    font-weight: 500;
}
.benefit-item {
    color: white !important;
    font-size: 1.2rem !important;
    margin: 0.8rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem 0;
}
.benefit-icon { 
    margin-right: 0.8rem;
    font-size: 1.5rem;
}
div.stButton > button[kind="primary"] {
    background: white;
    color: black;
    font-weight: 700;
    border: none;
    padding: 0.9rem 2.5rem;
    border-radius: 10px;
    font-size: 1.2rem;
    width: 250px;
    margin: 1.5rem auto;
    display: block;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.6);
    transition: all 0.3s ease-in-out;
}
div.stButton > button[kind="primary"]:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(255, 255, 255, 0.9);
}
.divider {
    border: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.4), transparent);
    margin: 2rem auto;
    width: 80%;
}
"""


def show_home_page():
    st.set_page_config(layout="wide", page_title="妆策灵析")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

    # st.markdown("""
    # <div class="logo-container">
    #     <img src="/app/static/logo.png" class="logo-img">
    # </div>
    # """, unsafe_allow_html=True)

    _, col_lang = st.columns([0.9, 0.1])
    with col_lang:
        st.button(TEXT_CONTENT[st.session_state.lang]["lang_toggle"],
                  on_click=toggle_language, type="secondary")

    with st.container():
        texts = TEXT_CONTENT[st.session_state.lang]
        st.markdown(f"<h1 class='main-title'>{texts['title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='subtitle'>{texts['subtitle']}</p>", unsafe_allow_html=True)

        _, btn_col, _ = st.columns([0.35, 0.3, 0.35])
        with btn_col:
            st.button(texts["button_text"], on_click=go_to_analysis_page,
                      use_container_width=True, type="primary")

        st.markdown(f"<div class='benefits-container'>", unsafe_allow_html=True)
        st.markdown(f"<h3 class='benefits-title'>{texts['benefits_title']}</h3>", unsafe_allow_html=True)
        for benefit in texts["benefits"]:
            st.markdown(
                f"<div class='benefit-item'><span class='benefit-icon'>{benefit.split(' ')[0]}</span>{' '.join(benefit.split(' ')[1:])}</div>",
                unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(f"<h2 class='benefits-title'>{texts['section_title']}</h2>", unsafe_allow_html=True)

        features = texts["features"]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"<div class='feature-card'><h3 class='feature-title'>{features['title1']}</h3><p class='feature-body'>{features['body1']}</p></div>",
                unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"<div class='feature-card'><h3 class='feature-title'>{features['title2']}</h3><p class='feature-body'>{features['body2']}</p></div>",
                unsafe_allow_html=True)


def toggle_language():
    st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"


def go_to_analysis_page():
    st.session_state.page = 'analysis'


if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'lang' not in st.session_state:
        st.session_state.lang = 'zh'

    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'analysis':
        # Import and show analysis page here
        # from analysis_page import show_analysis_page
        # show_analysis_page()
        pass

    # Rerun if page was changed
    if 'rerun' in st.session_state:
        del st.session_state.rerun
        st.rerun()