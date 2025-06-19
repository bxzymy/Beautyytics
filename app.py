# app.py

import os
import json
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

# 导入特定语言的函数，而不是通用函数
from prompt.prompt_en import get_prompts_en, get_ui_texts_en
from prompt.prompt_zh import get_prompts_zh, get_ui_texts_zh

from llm_response import get_llm_response_structured, get_final_analysis_and_chart_details

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
# --- 1. 初始化与文本加载 ---
# 初始化会话状态中的语言选项
if "lang" not in st.session_state:
    st.session_state.lang = "中文"

# 根据选择的语言，加载对应的UI文本和指令
if st.session_state.lang == "English":
    TEXTS = get_ui_texts_en()
    PROMPTS = get_prompts_en()
else:  # 默认为中文
    TEXTS = get_ui_texts_zh()
    PROMPTS = get_prompts_zh()

# 从加载的PROMPTS字典中定义系统指令
DATABASE_SCHEMA_DESCRIPTION = PROMPTS["db_schema"]
MULTI_TURN_SYSTEM_PROMPT_EXTENSION = PROMPTS["multi_turn_system"]
FULL_SYSTEM_PROMPT = f"{DATABASE_SCHEMA_DESCRIPTION}\n\n{MULTI_TURN_SYSTEM_PROMPT_EXTENSION}"
DATA_ANALYSIS_PROMPT_TEMPLATE = PROMPTS["data_analysis"]
DATA_CAVEATS_INSTRUCTIONS = PROMPTS["data_caveats"]


# --- 2. 核心功能函数 ---

@st.cache_data
def load_data():
    """加载CSV数据并进行初步清洗"""
    CSV_COLUMN_NAMES = [
        "order_no", "order_time", "order_date", "brand_code", "program_code",
        "order_type", "sales", "item_qty", "item_price", "channel",
        "subchannel", "sub_subchannel", "material_code", "material_name_cn",
        "material_type", "merged_c_code", "tier_code", "first_order_date",
        "is_mtd_active_member_flag", "ytd_active_arr", "r12_active_arr",
        "manager_counter_code", "ba_code", "province_name", "line_city_name",
        "line_city_level", "store_no", "terminal_name", "terminal_code",
        "terminal_region", "default_flag"
    ]
    try:
        df = pd.read_csv(
            "random_order_data.csv", sep=";", encoding='gbk',
            header=None, names=CSV_COLUMN_NAMES
        )
        df.columns = [col.lower() for col in df.columns]

        # 类型转换与清洗
        if 'order_time' in df.columns:
            df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

        numeric_cols = ['sales', 'item_qty', 'item_price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

        print(f"数据加载完成。列名: {df.columns.tolist()}")
        return df
    except FileNotFoundError:
        st.error(TEXTS["error_loading_data"])
        return None
    except Exception as e:
        st.error(TEXTS["error_loading_data_unknown"].format(e=e))
        return None


def execute_sql(sql_query: str, current_df_data: pd.DataFrame):
    """使用DuckDB执行SQL查询"""
    if not sql_query or not sql_query.strip():
        return None, TEXTS["error_no_sql"]
    if current_df_data is None:
        return None, TEXTS["error_no_data_for_sql"]
    try:
        con = duckdb.connect(database=':memory:', read_only=False)
        con.register('df_data', current_df_data)
        result_df = con.execute(sql_query).fetchdf()
        con.close()
        return result_df, None
    except Exception as e:
        error_message = TEXTS["error_sql_execution"].format(e=e, sql_query=sql_query)
        return None, error_message


def generate_streamlit_chart(chart_type: str, df: pd.DataFrame, chart_params: dict, chart_key: str = None):
    """根据图表类型和参数生成Streamlit图表"""
    if df is None or df.empty:
        return
    title = chart_params.get('title', 'Untitled Chart')
    explanation = chart_params.get('explanation', '')
    st.markdown(f"##### {title}")
    try:
        fig = None
        if chart_type == "line":
            x_col, y_col = chart_params.get("x_axis"), chart_params.get("y_axis")
            if x_col and y_col and x_col in df.columns and any(
                    c in df.columns for c in (y_col if isinstance(y_col, list) else [y_col])):
                fig = px.line(df, x=x_col,
                              y=[c for c in (y_col if isinstance(y_col, list) else [y_col]) if c in df.columns],
                              title=title)
            else:
                st.warning(TEXTS["chart_warning_missing_cols"].format(chart_type="Line", x_col=x_col, y_col=y_col));
                st.dataframe(df)
        elif chart_type == "bar":
            x_col, y_col = chart_params.get("x_axis"), chart_params.get("y_axis")
            if x_col and y_col and x_col in df.columns and any(
                    c in df.columns for c in (y_col if isinstance(y_col, list) else [y_col])):
                fig = px.bar(df, x=x_col,
                             y=[c for c in (y_col if isinstance(y_col, list) else [y_col]) if c in df.columns],
                             title=title)
            else:
                st.warning(TEXTS["chart_warning_missing_cols"].format(chart_type="Bar", x_col=x_col, y_col=y_col));
                st.dataframe(df)
        elif chart_type == "pie":
            cat_col, val_col = chart_params.get("category_column"), chart_params.get("value_column")
            if cat_col and val_col and cat_col in df.columns and val_col in df.columns:
                fig = px.pie(df, names=cat_col, values=val_col, title=title)
            else:
                st.warning(TEXTS["chart_warning_missing_cols_pie"].format(cat_col=cat_col, val_col=val_col));
                st.dataframe(df)
        elif chart_type == "scatter":
            x_col, y_col = chart_params.get("x_axis"), chart_params.get("y_axis")
            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                fig = px.scatter(df, x=x_col, y=y_col, title=title)
            else:
                st.warning(TEXTS["chart_warning_missing_cols_scatter"].format(x_col=x_col, y_col=y_col));
                st.dataframe(df)
        elif chart_type == "table":
            st.dataframe(df)
        else:
            st.info(TEXTS["chart_info_unknown_type"].format(chart_type=chart_type));
            st.dataframe(df)

        if fig:
            st.plotly_chart(fig, use_container_width=True, key=chart_key)

        if explanation and (fig or chart_type == "table"):
            st.caption(f"{TEXTS.get('chart_explanation_label', 'Chart Explanation')}: {explanation}")
    except Exception as e:
        st.error(TEXTS["chart_error_generating"].format(title=title, chart_type=chart_type, e=e));
        st.dataframe(df)


def process_user_query(user_query: str, current_df_data: pd.DataFrame, active_analysis_framework_prompt: str = None):
    """处理用户输入，执行两轮LLM调用并展示结果"""
    st.session_state.llm_conversation_history.append({"role": "user", "content": user_query})
    selected_prompt_display_name = st.session_state.get("selected_analysis_prompt_display_name",
                                                        TEXTS["framework_general"])

    ui_user_content = user_query
    if active_analysis_framework_prompt and selected_prompt_display_name != TEXTS["framework_general"]:
        framework_caption = TEXTS['based_on_framework_caption'].format(framework_name=selected_prompt_display_name)
        ui_user_content = f"({framework_caption})\n{user_query}"

    st.session_state.ui_messages.append({"role": "user", "content": ui_user_content})

    with st.chat_message("user"):
        st.markdown(ui_user_content)

    with st.chat_message("assistant"):
        assistant_ui_msg = {"role": "assistant", "query_result_df": None}
        spinner_text_call1 = TEXTS["spinner_thinking"]
        if active_analysis_framework_prompt:
            spinner_text_call1 = TEXTS["spinner_thinking_framework"].format(framework_name=selected_prompt_display_name)

        with st.spinner(spinner_text_call1):
            llm_response_call1_data = get_llm_response_structured(
                st.session_state.llm_conversation_history,
                FULL_SYSTEM_PROMPT,
                PROMPTS,
                active_analysis_framework_prompt=active_analysis_framework_prompt
            )

        if not llm_response_call1_data:
            st.error(TEXTS["llm_error_sql_generation"])
            assistant_ui_msg["error_message"] = TEXTS["llm_error_sql_generation"]
            st.session_state.ui_messages.append(assistant_ui_msg)
            return

        # 更新UI消息字典和LLM历史
        assistant_ui_msg.update(llm_response_call1_data)
        st.session_state.llm_conversation_history.append(
            {"role": "assistant", "content": json.dumps(llm_response_call1_data, ensure_ascii=False)})

        if assistant_ui_msg.get("explanation"):
            st.info(TEXTS["ai_guidance"].format(explanation=assistant_ui_msg['explanation']))

        generated_sql = assistant_ui_msg.get("sql_query")
        if generated_sql and generated_sql.strip():
            query_result_df, error_msg_sql = execute_sql(generated_sql, current_df_data)
            assistant_ui_msg["query_result_df"] = query_result_df
            assistant_ui_msg["error_message"] = error_msg_sql

            if error_msg_sql:
                st.error(error_msg_sql)
            elif query_result_df is not None and not query_result_df.empty:
                st.markdown("---")
                st.markdown(TEXTS["ai_data_insights_header"])
                spinner_text_call2 = TEXTS["spinner_analyzing_framework"].format(
                    framework_name=selected_prompt_display_name) if active_analysis_framework_prompt else TEXTS[
                    "spinner_analyzing"]

                with st.spinner(spinner_text_call2):
                    llm_response_call2_data = get_final_analysis_and_chart_details(
                        data_df=query_result_df,
                        user_query_for_analysis=user_query,
                        system_prompt_for_call2=PROMPTS["llm_response_system_prompt_call2"],
                        prompt_fragments=PROMPTS,
                        active_analysis_framework_prompt=active_analysis_framework_prompt,
                        base_data_analysis_prompt_template=DATA_ANALYSIS_PROMPT_TEMPLATE,
                        data_caveats_instructions=DATA_CAVEATS_INSTRUCTIONS
                    )

                if llm_response_call2_data:
                    assistant_ui_msg.update(llm_response_call2_data)  # 将第二轮结果更新到UI消息中
                    st.markdown(TEXTS["query_results_chart_header"])
                    generate_streamlit_chart(
                        assistant_ui_msg.get("chart_type", "table"), query_result_df, assistant_ui_msg,
                        chart_key=f"current_chart_{len(st.session_state.ui_messages)}"
                    )
                    if assistant_ui_msg.get("analysis_text"):
                        st.info(assistant_ui_msg["analysis_text"])
                else:
                    st.warning(TEXTS["warning_analysis_failed_fallback"])
                    st.markdown(TEXTS["query_results_chart_header_prelim"])
                    generate_streamlit_chart(
                        assistant_ui_msg.get("chart_type", "table"), query_result_df, assistant_ui_msg,
                        chart_key=f"prelim_chart_{len(st.session_state.ui_messages)}"
                    )
            elif query_result_df is not None:
                st.info(TEXTS["info_query_success_no_data"])

        if assistant_ui_msg.get("recommended_analyses"):
            st.markdown(TEXTS["recommendations_header"])
            for i, rec in enumerate(assistant_ui_msg["recommended_analyses"]):
                if rec.get('example_query'):
                    if st.button(TEXTS["try_query_button"].format(query=rec['example_query']),
                                 key=f"rec_btn_{i}_{len(st.session_state.ui_messages)}"):
                        st.session_state.selected_suggestion_query = rec['example_query']
                        st.rerun()

        st.session_state.ui_messages.append(assistant_ui_msg)


# --- 3. Streamlit 应用主体与界面渲染 ---

# 动态生成分析框架选项
PROMPT_MODEL_OPTIONS = {
    TEXTS["framework_general"]: None,
    TEXTS["framework_descriptive"]: PROMPTS["descriptive_analysis"],
    TEXTS["framework_diagnostic"]: PROMPTS["diagnostic_analysis"],
    TEXTS["framework_predictive"]: PROMPTS["predictive_analysis"],
    TEXTS["framework_swot"]: PROMPTS["swot_analysis"],
    TEXTS["framework_funnel"]: PROMPTS["funnel_analysis"],
    TEXTS["framework_logic_tree"]: PROMPTS["logic_tree"],
}

# 检查API Key
api_key_present = bool(os.getenv("DASHSCOPE_API_KEY") or (hasattr(st, 'secrets') and "DASHSCOPE_API_KEY" in st.secrets))
if not api_key_present:
    st.warning(TEXTS["api_key_warning"])

# 页面背景CSS
page_bg_gradient_css = """
<style>
/* ... (CSS 内容不变) ... */
</style>
"""

df_data = load_data()

if df_data is not None:
    st.markdown(page_bg_gradient_css, unsafe_allow_html=True)

    # 初始化会话状态
    if "llm_conversation_history" not in st.session_state:
        st.session_state.llm_conversation_history = []
    if "ui_messages" not in st.session_state:
        st.session_state.ui_messages = []
    if "selected_suggestion_query" not in st.session_state:
        st.session_state.selected_suggestion_query = None
    if "selected_analysis_prompt_key" not in st.session_state:
        st.session_state.selected_analysis_prompt_key = TEXTS["framework_general"]
    if "active_analysis_framework_prompt" not in st.session_state:
        st.session_state.active_analysis_framework_prompt = PROMPT_MODEL_OPTIONS.get(
            st.session_state.selected_analysis_prompt_key)
    if "selected_analysis_prompt_display_name" not in st.session_state:
        st.session_state.selected_analysis_prompt_display_name = st.session_state.selected_analysis_prompt_key

    # --- 侧边栏 ---
    with st.sidebar:
        st.header(TEXTS["sidebar_header"])

        lang_options = ["中文", "English"]
        current_lang_index = lang_options.index(st.session_state.lang)
        selected_lang = st.radio(
            TEXTS["language_selector_label"], options=lang_options, index=current_lang_index,
            horizontal=True, key="lang_selector"
        )
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            if selected_lang == "English":
                st.session_state.selected_analysis_prompt_key = get_ui_texts_en()["framework_general"]
            else:
                st.session_state.selected_analysis_prompt_key = get_ui_texts_zh()["framework_general"]
            st.rerun()

        st.markdown("---")

        prompt_keys = list(PROMPT_MODEL_OPTIONS.keys())
        current_prompt_index = prompt_keys.index(
            st.session_state.selected_analysis_prompt_key) if st.session_state.selected_analysis_prompt_key in prompt_keys else 0
        selected_key = st.selectbox(
            label=TEXTS["sidebar_framework_select_box"], options=prompt_keys,
            index=current_prompt_index, key="analysis_prompt_selector"
        )
        if selected_key != st.session_state.selected_analysis_prompt_key:
            st.session_state.selected_analysis_prompt_key = selected_key
            st.session_state.active_analysis_framework_prompt = PROMPT_MODEL_OPTIONS[selected_key]
            st.session_state.selected_analysis_prompt_display_name = selected_key

        if st.button(TEXTS["clear_history_button"]):
            st.session_state.llm_conversation_history, st.session_state.ui_messages = [], []
            st.session_state.selected_suggestion_query = None
            st.rerun()
        st.markdown("---")

    # --- 主页面 ---
    if not st.session_state.ui_messages:
        # 欢迎界面
        st.markdown(f"""<div style="text-align: center; margin-bottom: 30px;">
                        <h1>{TEXTS["main_title"]}</h1>
                        <p style="font-size: 18px; color: #666;"><em>{TEXTS["main_subtitle"]}</em></p>
                        </div>""", unsafe_allow_html=True)
        st.success(TEXTS["welcome_message"])
        st.markdown(TEXTS["welcome_instruction"])
        st.divider()
        with st.container(border=True):
            st.subheader(TEXTS["try_asking_header"])
            col1, col2, col3 = st.columns(3)
            with col1: st.info(TEXTS["example_sales"])
            with col2: st.info(TEXTS["example_trend"])
            with col3: st.info(TEXTS["example_geo"])
    else:
        # 历史消息展示
        st.title(TEXTS["history_title"])
        for i, msg_info in enumerate(st.session_state.ui_messages):
            with st.chat_message(msg_info["role"]):
                if msg_info["role"] == "user":
                    st.markdown(msg_info["content"])
                elif msg_info["role"] == "assistant":
                    if msg_info.get("analysis_framework_used") and msg_info["analysis_framework_used"] != TEXTS[
                        "framework_general"]:
                        st.caption(TEXTS["based_on_framework_caption"].format(
                            framework_name=msg_info["analysis_framework_used"]))

                    if msg_info.get("query_result_df") is not None and not msg_info["query_result_df"].empty:
                        st.markdown(TEXTS["query_results_chart_header_history"])
                        generate_streamlit_chart(
                            msg_info.get("chart_type", "table"), msg_info["query_result_df"], msg_info,
                            chart_key=f"history_chart_{i}"
                        )
                        if msg_info.get("analysis_text"):
                            st.markdown("---")
                            st.markdown(TEXTS["ai_insights_history_header"])
                            st.info(msg_info["analysis_text"])

                    if msg_info.get("error_message"):
                        st.error(msg_info["error_message"])

    # 用户输入处理
    input_for_processing = st.session_state.selected_suggestion_query or st.chat_input(TEXTS["chat_input_placeholder"])
    if input_for_processing:
        if st.session_state.selected_suggestion_query:
            st.session_state.selected_suggestion_query = None  # 清除建议查询
        process_user_query(input_for_processing, df_data, st.session_state.active_analysis_framework_prompt)
        st.rerun()

else:
    st.error(TEXTS["data_load_fail_app_stop"])