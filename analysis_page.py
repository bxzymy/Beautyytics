import streamlit as st
import os

from chart import generate_streamlit_chart
from load_data import load_data
from prompt.prompt_model import BeautyAnalyticsPrompts
from prompt.prompt_model_en import BeautyAnalyticsPromptsEn
from sql import process_user_query, process_user_query_orchestrator
from dotenv import load_dotenv

from utils import show_history_panel

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")

CSS = """
/* 主应用容器样式 - 设置背景图 */
[data-testid="stAppViewContainer"] {
    background: url('/app/static/bg3.png') no-repeat center center fixed; /* 背景图不重复、居中、固定 */
    background-size: cover; /* 背景图覆盖整个容器 */
}

/* 隐藏Streamlit默认的菜单、页脚和页眉 */
#MainMenu, footer, header { 
    visibility: hidden; /* 隐藏元素但保留空间 */
}

/* 主内容区域样式 */
.main .block-container {
    background-color: rgba(0, 0, 0, 0.1) !important; /* 半透明黑色背景 */
    border-radius: 20px; /* 圆角边框 */
    padding: 2.5rem 2rem; /* 内边距 */
    margin: 2rem auto; /* 外边距居中 */
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.3); /* 阴影效果 */
}

/* 标题文字样式 */
.analysis-title {
    font-size: 6rem; !important; /* 字体大小 */
    font-weight: bold; /* 加粗 */
    background: linear-gradient(90deg, #FF8C00, #FFA500, #FFD700); /* 渐变色背景 */
    -webkit-background-clip: text; /* 背景裁剪为文字形状 */
    -webkit-text-fill-color: transparent; /* 文字透明显示背景 */
    text-align: center; /* 居中 */
    animation: rainbow 8s linear infinite; /* 彩虹动画效果 */
    margin-bottom: 1rem; /* 下边距 */
    font-family: 'Segoe UI', sans-serif; /* 字体 */
    filter: drop-shadow(0 0 6px rgba(255,255,255,0.2)); /* 文字阴影 */
}

/* 历史对话条目样式 */
.history-item {
    padding: 0.8rem; /* 内边距 */
    margin: 0.5rem 0; /* 外边距 */
    border-radius: 8px; /* 圆角 */
    background-color: rgba(255, 255, 255, 0.05); /* 半透明白色背景 */
    cursor: pointer; /* 鼠标指针变为手形 */
    transition: all 0.2s ease; /* 过渡动画 */
}

/* 历史对话条目悬停效果 */
.history-item:hover {
    background-color: rgba(74, 222, 128, 0.15); /* 悬停时背景色变化 */
}

/* 历史查询问题样式 */
.history-query {
    font-weight: bold; /* 加粗 */
    color: #4ADE80; /* 绿色文字 */
    margin-bottom: 0.3rem; /* 下边距 */
}

/* 历史回复样式 */
.history-response {
    color: #E5EAF5; /* 浅灰色文字 */
    font-size: 0.9rem; /* 较小字体 */
    white-space: nowrap; /* 不换行 */
    overflow: hidden; /* 隐藏溢出 */
    text-overflow: ellipsis; /* 溢出显示省略号 */
}

/* 聊天消息气泡样式 */
.stChatMessage {
    background-color: rgba(255, 255, 255, 0.07); /* 半透明白色背景 */
    border-left: 4px solid #4ade80; /* 左侧绿色边框 */
    padding: 1rem; /* 内边距 */
    border-radius: 10px; /* 圆角 */
    margin-bottom: 1.5rem; /* 下边距 */
}

/* 侧边栏主容器样式 */
[data-testid="stSidebar"] > div {
    background-color: rgba(27, 38, 59, 0.95); /* 深蓝色半透明背景 */
    border-left: 4px solid #4ade80; /* 左侧绿色边框 */
    padding: 1.5rem 1rem; /* 内边距 */
    border-radius: 0; /* 无圆角 */
}

/* 侧边栏内容区域样式 */
.sidebar .sidebar-content {
    background: transparent !important; /* 透明背景 */
}

/* 侧边栏内所有标题和文字样式 */
.sidebar h1, .sidebar h2, .sidebar h3, 
.sidebar h4, .sidebar h5, .sidebar h6, 
.sidebar p, .sidebar label {
    color: #333333 !important; /* 浅色文字 */
}


/* 按钮基础样式 */
div.stButton > button {
    background: linear-gradient(to right, #4ade80, #0ea5e9); /* 绿色到蓝色渐变 */
    color: #0F172A; /* 深色文字 */
    font-weight: 600; /* 字体粗细 */
    padding: 0.6rem 1.5rem; /* 内边距 */
    font-size: 1rem; /* 字体大小 */
    border: none; /* 无边框 */
    border-radius: 8px; /* 圆角 */
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.2); /* 阴影 */
    transition: all 0.3s ease; /* 过渡动画 */
}

/* 按钮悬停效果 */
div.stButton > button:hover {
    transform: scale(1.03); /* 轻微放大 */
    box-shadow: 0 0 18px rgba(255, 255, 255, 0.4); /* 阴影增强 */
}

/* 分割线样式 */
.divider {
    height: 1px; /* 高度 */
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.3), transparent); /* 渐变透明线 */
    margin: 2rem auto; /* 外边距 */
    width: 80%; /* 宽度 */
    border: none; /* 无边框 */
}

/* 警告提示框样式 */
div.stAlert {
    background-color: rgba(255, 255, 255, 0.08); /* 半透明白色背景 */
    border-left: 4px solid #4ade80; /* 左侧绿色边框 */
    border-radius: 8px; /* 圆角 */
    padding: 1rem; /* 内边距 */
    color: #F0F4FA; /* 浅色文字 */
}

/* 全局文字颜色设置 */
h1, h2, h3, h4, h5, h6, p, div, span {
    color: #E5EAF5 !important; /* 浅灰色文字 */
}

/* 彩虹渐变动画定义 */
@keyframes rainbow {
    0% { background-position: 0% 50%; } /* 动画起始位置 */
    50% { background-position: 100% 50%; } /* 动画中间位置 */
    100% { background-position: 0% 50%; } /* 动画结束位置 */
}


/* 侧边栏选择框标签文字颜色（黑色） */
[data-testid="stSidebar"] .stSelectbox label {
    color: #000000 !important;
}

/* 当前选中值文字颜色（黑色） */
[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #000000 !important;
}

/* 下拉菜单选项容器样式 */
[data-testid="stSidebar"] [role="listbox"] {
    background-color: white !important;
    border: 1px solid #e0e0e0 !important;
}

/* 下拉菜单选项文字颜色（黑色） */
[data-testid="stSidebar"] [role="listbox"] li,
[data-testid="stSidebar"] [role="listbox"] li > div,
[data-testid="stSidebar"] [role="listbox"] li > div > div {
    color: #000000 !important;
}

/* 鼠标悬停选项样式 */
[data-testid="stSidebar"] [role="listbox"] li:hover {
    background-color: #f5f5f5 !important;
}

/* 选中项样式 */
[data-testid="stSidebar"] [role="listbox"] li[aria-selected="true"] {
    background-color: #e0e0e0 !important;
}
"""

TEXT_CONTENT = {
    'zh': {
        "back_to_home": "返回主页",
        "analysis_options": "分析选项",
        "info_header": "💡 妆策灵析是什么？",
        "info_body": "结合 LLM 与销售数据的智能分析助手。",
        "supported_analysis_header": "📊 支持的分析类型",
        "supported_analysis_body": "销售额、趋势、地域、BA贡献、产品表现等。",
        "use_case_header": "🎯 应用场景推荐",
        "use_case_body": "门店复盘 / 产品推荐 / 销售差异排查",
        "select_framework": "选择分析框架:",
        "clear_history": "清除对话历史",
        "view_history": "查看历史对话",
        "api_key_warning": "API Key 未配置! LLM 功能可能受限。",
        "analysis_page_title": "妆策灵析",
        "welcome_message": "👋 欢迎回来！请在下方输入框用自然语言提问开始分析。",
        "try_asking_header": "💡 试试这样问我：",
        "chat_input_placeholder": "请输入您的问题...",
        "sales_analysis_title": "📦 销售额分析",
        "sales_analysis_caption": "比较不同产品的销售表现",
        "sales_analysis_button": "示例：产品对比",
        "trend_analysis_title": "📈 时间趋势分析",
        "trend_analysis_caption": "查看时间序列走势变化",
        "trend_analysis_button": "示例：时间趋势",
        "geo_analysis_title": "📍 地域分析",
        "geo_analysis_caption": "洞察各区域的销售情况",
        "geo_analysis_button": "示例：地区对比",
        "contribution_analysis_title": "💄 产品贡献率",
        "contribution_analysis_caption": "评估不同品类对整体销售的贡献",
        "contribution_analysis_button": "示例：类目贡献",
        "channel_analysis_title": "🏬 终端表现分析",
        "channel_analysis_caption": "比较不同终端（门店、电商）表现",
        "channel_analysis_button": "示例：终端排行",
        "repurchase_analysis_title": "🔁 复购行为分析",
        "repurchase_analysis_caption": "用户是否有重复购买行为",
        "repurchase_analysis_button": "示例：复购率",
        "based_on_framework": "基于框架",
        "ai_guidance": "AI 指导",
        "query_results_and_chart": "📋 查询结果与图表 (历史):",
        "historical_chart": "历史图表",
        "ai_data_insights": "🤖 AI 数据洞察 (历史):",
        "query_no_data": "查询成功执行，但没有返回数据 (历史)。",
        "historical_recommendations": "💡 历史分析建议:",
    },
    'en': {
        "back_to_home": "Back to Home",
        "analysis_options": "Analysis Options",
        "info_header": "💡 What is Beautyytics?",
        "info_body": "An intelligent analysis assistant combining LLM with sales data.",
        "supported_analysis_header": "📊 Supported Analysis Types",
        "supported_analysis_body": "Sales, trends, regions, BA contributions, product performance, etc.",
        "use_case_header": "🎯 Recommended Scenarios",
        "use_case_body": "Store reviews / Product recommendations / Sales discrepancy investigation",
        "select_framework": "Select Analysis Framework:",
        "clear_history": "Clear Chat History",
        "view_history": "View History",
        "api_key_warning": "API Key is not configured! LLM functions may be limited.",
        "analysis_page_title": "Beautyytics",
        "welcome_message": "👋 Welcome back! Please ask a question in natural language below to start the analysis.",
        "try_asking_header": "💡 Try asking me:",
        "chat_input_placeholder": "Please enter your question...",
        "sales_analysis_title": "📦 Sales Analysis",
        "sales_analysis_caption": "Compare sales performance of different products",
        "sales_analysis_button": "Example: Product Comparison",
        "trend_analysis_title": "📈 Trend Analysis",
        "trend_analysis_caption": "View changes in time series trends",
        "trend_analysis_button": "Example: Time Trend",
        "geo_analysis_title": "📍 Geographical Analysis",
        "geo_analysis_caption": "Gain insights into sales in various regions",
        "geo_analysis_button": "Example: Regional Comparison",
        "contribution_analysis_title": "💄 Product Contribution",
        "contribution_analysis_caption": "Assess the contribution of different categories to overall sales",
        "contribution_analysis_button": "Example: Category Contribution",
        "channel_analysis_title": "🏬 Channel Performance",
        "channel_analysis_caption": "Compare performance of different channels (stores, e-commerce)",
        "channel_analysis_button": "Example: Channel Ranking",
        "repurchase_analysis_title": "🔁 Repurchase Behavior",
        "repurchase_analysis_caption": "Analyze user repeat purchase behavior",
        "repurchase_analysis_button": "Example: Repurchase Rate",
        "based_on_framework": "Based on framework",
        "ai_guidance": "AI Guidance",
        "query_results_and_chart": "📋 Query Results & Chart (Historical):",
        "historical_chart": "Historical Chart",
        "ai_data_insights": "🤖 AI Data Insights (Historical):",
        "query_no_data": "Query executed successfully but returned no data (Historical).",
        "historical_recommendations": "💡 Historical Analysis Recommendations:",
    }
}


PROMPT_MODEL_OPTIONS_ZH = {
    "通用分析 (默认)": None,
    "描述性分析 (销售全景)": BeautyAnalyticsPrompts.descriptive_analysis(),
    "诊断性分析 (问题根因)": BeautyAnalyticsPrompts.diagnostic_analysis(),
    "预测性分析 (未来业绩)": BeautyAnalyticsPrompts.predictive_analysis(),
    "SWOT分析 (竞争力评估)": BeautyAnalyticsPrompts.swot_analysis(),
    "漏斗分析 (转化路径)": BeautyAnalyticsPrompts.funnel_analysis(),
    "逻辑树分析 (复杂问题拆解)": BeautyAnalyticsPrompts.logic_tree(),
}

PROMPT_MODEL_OPTIONS_EN = {
    "General Analysis (Default)": None,
    "Descriptive Analysis (Sales Overview)": BeautyAnalyticsPromptsEn.descriptive_analysis(),
    "Diagnostic Analysis (Root Cause)": BeautyAnalyticsPromptsEn.diagnostic_analysis(),
    "Predictive Analysis (Future Performance)": BeautyAnalyticsPromptsEn.predictive_analysis(),
    "SWOT Analysis (Competitive Assessment)": BeautyAnalyticsPromptsEn.swot_analysis(),
    "Funnel Analysis (Conversion Path)": BeautyAnalyticsPromptsEn.funnel_analysis(),
    "Logic Tree Analysis (Problem Decomposition)": BeautyAnalyticsPromptsEn.logic_tree(),
}


def render_analysis_job():
    """
    渲染 "智能报告" 模式下的分析任务状态和最终报告。
    """
    job = st.session_state.get("current_analysis_job")
    if not job:
        return

    status = job.get("job_status")
    message = job.get("status_message")
    texts = TEXT_CONTENT.get(st.session_state.get('lang', 'zh'), TEXT_CONTENT['zh'])

    # 在处理过程中显示状态更新
    if status not in ["DONE", "FAILED"]:
        default_processing_text = "正在处理中..." if st.session_state.get('lang', 'zh') == 'zh' else "Processing..."
        st.info(f"⚙️ {message or default_processing_text}")

    # 如果分析失败，显示错误信息
    if status == "FAILED":
        st.error(f"分析失败: {message}")

    # 如果分析完成，则渲染结构化的最终报告
    if status == "DONE":
        report = job.get("stages", {}).get("stage4_report")
        if not report:
            st.error("分析已完成，但未能生成最终报告。")
            return

        st.markdown(f"## {report.get('title', '分析报告')}")
        st.markdown("---")
        st.success(f"**核心摘要:** {report.get('summary', '未提供摘要。')}")

        # 准备图表所需的数据
        evidence_dfs = {
            key: item["dataframe"]
            for key, item in job["stages"].get("stage3_evidence", {}).items()
            if item.get("dataframe") is not None
        }
        if "stage1_baseline" in job["stages"]:
            evidence_dfs["baseline"] = job["stages"]["stage1_baseline"]["data"]

        # 遍历报告中的章节并显示
        for chapter in report.get("chapters", []):
            with st.expander(chapter.get("title", "未命名章节"), expanded=True):
                st.markdown(chapter.get("content", "此章节无内容。"))

                chart_params = chapter.get("chart_params")
                if chart_params and chart_params.get("data_key"):
                    st.markdown("---")
                    data_key = chart_params.get("data_key")
                    chart_df = evidence_dfs.get(data_key)

                    if chart_df is not None:
                        final_chart_params = chart_params.copy()
                        if "title" not in final_chart_params:
                            final_chart_params["title"] = chapter.get("title")

                        generate_streamlit_chart(
                            chart_type=chapter.get("chart_type", "table"),
                            df=chart_df,
                            chart_params=final_chart_params,
                            lang=st.session_state.lang
                        )
                    else:
                        st.warning(f"未能找到用于生成图表的数据源 '{data_key}'。")

        st.markdown("### 策略建议")
        recommendations = report.get("recommendations", [])
        if recommendations:
            for rec in recommendations:
                st.markdown(f"- {rec}")
        else:
            st.markdown("未生成明确的策略建议。")


def init_session_state():
    """初始化会话状态"""
    if 'page' not in st.session_state:
        st.session_state.page = 'analysis'
    if 'lang' not in st.session_state:
        st.session_state.lang = 'zh'
    if "llm_conversation_history" not in st.session_state:
        st.session_state.llm_conversation_history = []
    if "ui_messages" not in st.session_state:
        st.session_state.ui_messages = []
    if "selected_suggestion_query" not in st.session_state:
        st.session_state.selected_suggestion_query = None
    if "selected_analysis_prompt_key" not in st.session_state:
        st.session_state.selected_analysis_prompt_key = "通用分析 (默认)"
    if "active_analysis_framework_prompt" not in st.session_state:
        st.session_state.active_analysis_framework_prompt = PROMPT_MODEL_OPTIONS_ZH[
            st.session_state.selected_analysis_prompt_key]
    if "selected_analysis_prompt_display_name" not in st.session_state:
        st.session_state.selected_analysis_prompt_display_name = st.session_state.selected_analysis_prompt_key
    if "show_history" not in st.session_state:
        st.session_state.show_history = False


def show_analysis_page():
    init_session_state()

    if st.session_state.page == 'home':
        return

    st.set_page_config(layout="wide", page_title="妆策灵析 | Beautyytics")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    df_data = load_data()

    # 左侧边栏
    with st.sidebar:

        lang_options = ['zh', 'en']
        lang_labels = ['中文', 'English']
        selected_lang_index = lang_options.index(st.session_state.get('lang', 'zh'))

        selected_lang = st.radio(
            "语言 / Language",
            options=lang_options,
            format_func=lambda lang: lang_labels[lang_options.index(lang)],
            index=selected_lang_index,
            horizontal=True,
            key='lang_radio'
        )

        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.session_state.llm_conversation_history = []
            st.session_state.ui_messages = []
            st.session_state.selected_suggestion_query = None

            if st.session_state.lang == 'zh':
                st.session_state.selected_analysis_prompt_key = "通用分析 (默认)"
            else:
                st.session_state.selected_analysis_prompt_key = "General Analysis (Default)"
            st.rerun()

        # 根据语言选择加载对应的文本和分析框架
        texts = TEXT_CONTENT[st.session_state.lang]
        if st.session_state.lang == 'zh':
            PROMPT_MODEL_OPTIONS = PROMPT_MODEL_OPTIONS_ZH
        else:
            PROMPT_MODEL_OPTIONS = PROMPT_MODEL_OPTIONS_EN

        # 使用加载的文本
        st.button(texts["back_to_home"], on_click=go_to_home_page)
        st.header(texts["analysis_options"])
        st.markdown("---")

        st.markdown(f"""
        ### {texts['info_header']}
        {texts['info_body']}

        ### {texts['supported_analysis_header']}
        {texts['supported_analysis_body']}

        ### {texts['use_case_header']}
        {texts['use_case_body']}
        """)
        st.markdown("---")

        prompt_keys = list(PROMPT_MODEL_OPTIONS.keys())
        current_prompt_index = prompt_keys.index(
            st.session_state.selected_analysis_prompt_key) if st.session_state.selected_analysis_prompt_key in prompt_keys else 0

        selected_key = st.selectbox(
            texts["select_framework"],
            options=prompt_keys,
            index=current_prompt_index,
            key="analysis_prompt_selector"
        )

        if selected_key != st.session_state.selected_analysis_prompt_key:
            st.session_state.selected_analysis_prompt_key = selected_key
            st.session_state.active_analysis_framework_prompt = PROMPT_MODEL_OPTIONS[selected_key]
            st.session_state.selected_analysis_prompt_display_name = selected_key

        if st.button(texts["clear_history"], key="sidebar_clear_history_button"):
            st.session_state.llm_conversation_history = []
            st.session_state.ui_messages = []
            if "current_analysis_job" in st.session_state:
                del st.session_state["current_analysis_job"]
            st.rerun()

        st.session_state.show_history = st.checkbox(texts["view_history"], value=st.session_state.show_history)

        if st.session_state.show_history:
            show_history_panel()

        st.markdown("---")
        if not api_key:
            st.warning(texts["api_key_warning"])

        st.markdown("---") # 添加分割线
        st.session_state.smart_report_mode = st.toggle(
            '✨ 开启智能报告模式',
            key='smart_report_toggle',
            help='开启后，AI将进行多步骤的深度分析，并生成一份全面的结构化报告。关闭则为标准的单轮问答模式。'
        )
        st.markdown("---")


    if df_data is None:
        st.error("数据未能成功加载，应用无法继续。请检查 CSV 文件和加载逻辑。")
        st.button(texts["back_to_home"], on_click=go_to_home_page)
        return

    # 主内容区
    if st.session_state.get('smart_report_mode', False):
        if "current_analysis_job" in st.session_state:
            render_analysis_job()
        else:
            # 智能报告模式的欢迎界面
            st.markdown(
                f"<div style='text-align: center; margin-bottom: 30px;'><h1 class='analysis-title'>{texts['analysis_page_title']} (智能报告)</h1></div>",
                unsafe_allow_html=True)
            st.success("您已进入智能报告模式。请输入一个分析主题，AI将为您进行深度探索。")
    else:
        if not st.session_state.ui_messages:
            st.markdown(
                f"<div style='text-align: center; margin-bottom: 30px;'><h1 class='analysis-title'>{texts['analysis_page_title']}</h1></div>",
                unsafe_allow_html=True)
            st.success(texts['welcome_message'])
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"### {texts['try_asking_header']}")
                st.markdown('<div class="card-grid">', unsafe_allow_html=True)

                row1_col1, row1_col2, row1_col3 = st.columns(3)
                row2_col1, row2_col2, row2_col3 = st.columns(3)

                # 使用texts字典动态生成所有建议卡片
                with row1_col1:
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    st.markdown(f"#### {texts['sales_analysis_title']}")
                    st.caption(texts['sales_analysis_caption'])
                    if st.button(texts['sales_analysis_button'], key="suggestion_1"):
                        st.session_state.selected_suggestion_query = "不同产品销售额对比" if st.session_state.lang == 'zh' else "Sales comparison across different products"
                    st.markdown('</div>', unsafe_allow_html=True)

                with row1_col2:
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    st.markdown(f"#### {texts['trend_analysis_title']}")
                    st.caption(texts['trend_analysis_caption'])
                    if st.button(texts['trend_analysis_button'], key="suggestion_2"):
                        st.session_state.selected_suggestion_query = "2024年10月的销售趋势图" if st.session_state.lang == 'zh' else "Sales trend for October 2024"
                    st.markdown('</div>', unsafe_allow_html=True)

                with row1_col3:
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    st.markdown(f"#### {texts['geo_analysis_title']}")
                    st.caption(texts['geo_analysis_caption'])
                    if st.button(texts['geo_analysis_button'], key="suggestion_3"):
                        st.session_state.selected_suggestion_query = "2024年江浙沪的订单数对比" if st.session_state.lang == 'zh' else "Order count comparison for Shanghai, Jiangsu, and Zhejiang in 2024"
                    st.markdown('</div>', unsafe_allow_html=True)

                with row2_col1:
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    st.markdown(f"#### {texts['contribution_analysis_title']}")
                    st.caption(texts['contribution_analysis_caption'])
                    if st.button(texts['contribution_analysis_button'], key="suggestion_4"):
                        st.session_state.selected_suggestion_query = "2024年各产品类型销售占比" if st.session_state.lang == 'zh' else "Sales proportion by product category in 2024"
                    st.markdown('</div>', unsafe_allow_html=True)

                with row2_col2:
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    st.markdown(f"#### {texts['channel_analysis_title']}")
                    st.caption(texts['channel_analysis_caption'])
                    if st.button(texts['channel_analysis_button'], key="suggestion_5"):
                        st.session_state.selected_suggestion_query = "不同渠道或终端的销售额对比" if st.session_state.lang == 'zh' else "Sales comparison by different channels or terminals"
                    st.markdown('</div>', unsafe_allow_html=True)

                with row2_col3:
                    st.markdown('<div class="card-box">', unsafe_allow_html=True)
                    st.markdown(f"#### {texts['repurchase_analysis_title']}")
                    st.caption(texts['repurchase_analysis_caption'])
                    if st.button(texts['repurchase_analysis_button'], key="suggestion_6"):
                        st.session_state.selected_suggestion_query = "用户重复购买排行前三的产品对比" if st.session_state.lang == 'zh' else "Comparison of top 3 products with repeat purchases"
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

    # 历史消息显示
    if "ui_messages" in st.session_state:
        for i, msg_info in enumerate(st.session_state.ui_messages):
            with st.chat_message(msg_info["role"]):
                if "content" in msg_info and msg_info["role"] == "user":
                    st.markdown(msg_info["content"])
                elif msg_info["role"] == "assistant":
                    framework_used = msg_info.get("analysis_framework_used")
                    if framework_used and framework_used not in ["通用分析 (默认)", "General Analysis (Default)"]:
                        st.caption(f"({texts['based_on_framework']}: {framework_used})")

                    llm_general_explanation_from_call1 = msg_info.get("llm_general_explanation")
                    final_chart_explanation_from_call2 = msg_info.get("final_chart_explanation")

                    if llm_general_explanation_from_call1 and (
                            llm_general_explanation_from_call1 != final_chart_explanation_from_call2 or not final_chart_explanation_from_call2):
                        st.info(f"{texts['ai_guidance']}: {llm_general_explanation_from_call1}")

                    if msg_info.get("query_result_df") is not None:
                        if not msg_info["query_result_df"].empty:
                            st.markdown(f"**{texts['query_results_and_chart']}**")
                            history_chart_title = msg_info.get("chart_params", {}).get("title",
                                                                                       texts['historical_chart'])
                            generate_streamlit_chart(
                                msg_info.get("chart_type", "table"),
                                msg_info["query_result_df"],
                                msg_info.get("chart_params", {}),
                                chart_key=f"history_chart_{i}_{history_chart_title.replace(' ', '_')}",
                                lang=st.session_state.lang
                            )

                            if msg_info.get("data_analysis_text"):
                                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                                st.markdown(f"##### {texts['ai_data_insights']}")
                                st.info(msg_info["data_analysis_text"])
                        elif msg_info.get("sql_query"):
                            st.info(texts['query_no_data'])
                    elif "content" in msg_info and not msg_info.get("sql_query") and not msg_info.get(
                            "recommended_analyses"):
                        st.markdown(msg_info["content"])

                    if msg_info.get("recommended_analyses"):
                        st.markdown(f"💡 **{texts['historical_recommendations']}**")

                    if msg_info.get("error_message") and not (
                            "content" in msg_info and msg_info["content"] == msg_info["error_message"]):
                        st.error(msg_info["error_message"])

                elif "content" in msg_info and not msg_info.get("sql_query") and not msg_info.get(
                        "recommended_analyses"):
                    # 增加一个检查，确保 content 不为 None
                    if msg_info.get("content") is not None:
                        st.markdown(msg_info["content"])

    input_for_processing = None
    if st.session_state.get("selected_suggestion_query"):
        input_for_processing = st.session_state.selected_suggestion_query
        st.session_state.selected_suggestion_query = None

    user_typed_input = st.chat_input(texts['chat_input_placeholder'])
    if user_typed_input:
        input_for_processing = user_typed_input

    # 2. 如果有新输入，则启动一个新任务
    if input_for_processing:
        if st.session_state.get('smart_report_mode', False):
            # 清理旧任务，准备开始新任务
            if "current_analysis_job" in st.session_state:
                del st.session_state["current_analysis_job"]
            # 调用一次编排器来“初始化”新任务
            process_user_query_orchestrator(input_for_processing, df_data, lang=st.session_state.lang)
        else:
            # 标准模式的逻辑不变
            process_user_query(input_for_processing, df_data, st.session_state.active_analysis_framework_prompt,
                               lang=st.session_state.lang)

    # 3. 【新增】如果当前有正在进行的智能报告任务，则持续调用编排器以推进状态
    job = st.session_state.get("current_analysis_job")
    if job and job.get("job_status") not in ["DONE", "FAILED", None]:
        # 只要任务没结束，就调用编排器让它继续跑
        process_user_query_orchestrator(job["original_query"], df_data, lang=st.session_state.lang)

def go_to_home_page():
    st.session_state.page = 'home'
    # st.session_state.should_rerun = True


if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = 'analysis'
    if 'lang' not in st.session_state:
        st.session_state.lang = 'zh'
    if "llm_conversation_history" not in st.session_state:
        st.session_state.llm_conversation_history = []
    if "ui_messages" not in st.session_state:
        st.session_state.ui_messages = []
    if "selected_suggestion_query" not in st.session_state:
        st.session_state.selected_suggestion_query = None
    if "selected_analysis_prompt_key" not in st.session_state:
        st.session_state.selected_analysis_prompt_key = "通用分析 (默认)" if st.session_state.lang == 'zh' else "General Analysis (Default)"

    PROMPT_OPTIONS = PROMPT_MODEL_OPTIONS_ZH if st.session_state.get('lang', 'zh') == 'zh' else PROMPT_MODEL_OPTIONS_EN

    if "active_analysis_framework_prompt" not in st.session_state:
        st.session_state.active_analysis_framework_prompt = PROMPT_OPTIONS.get(
            st.session_state.selected_analysis_prompt_key)

    if "selected_analysis_prompt_display_name" not in st.session_state:
        st.session_state.selected_analysis_prompt_display_name = st.session_state.selected_analysis_prompt_key
    if "show_history" not in st.session_state:
        st.session_state.show_history = False

    show_analysis_page()