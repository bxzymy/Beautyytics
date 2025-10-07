import json

import duckdb
import pandas as pd
import streamlit as st

from chart import generate_streamlit_chart
from llm_response import get_llm_response_structured, get_final_analysis_and_chart_details, get_synthesized_report, get_analysis_plan
from prompt.prompt import FULL_SYSTEM_PROMPT, DATA_ANALYSIS_PROMPT_TEMPLATE, DATA_CAVEATS_INSTRUCTIONS
from prompt.prompt_en import FULL_SYSTEM_PROMPT_EN, DATA_ANALYSIS_PROMPT_TEMPLATE_EN, DATA_CAVEATS_INSTRUCTIONS_EN

# Language strings
LANGUAGE_STRINGS = {
    'zh': {
        'sql_empty': "SQL 查询为空或无效。",
        'data_not_loaded': "数据未能加载，无法执行SQL查询。",
        'sql_error': "SQL 查询执行错误: {error}\n尝试执行的 SQL: {query}",
        'ai_thinking': "AI 思考中...",
        'ai_thinking_framework': "AI 根据 ({framework}) 框架思考中...",
        'ai_failed': "抱歉，AI未能生成有效的SQL查询或分析建议。请稍后再试或调整您的问题。",
        'ai_guidance': "AI 指导: {text}",
        'data_insights': "##### 🤖 AI 数据洞察",
        'analyzing_data': "AI 正在分析数据...",
        'analyzing_data_framework': "AI 正基于 ({framework}) 框架分析数据...",
        'results_chart': "📋 **查询结果与图表:**",
        'no_analysis_text': "本次未能从AI获取数据分析文本。",
        'analysis_failed': "AI未能完成数据分析。将尝试使用初步的图表建议（如果可用）。",
        'preliminary_chart': "📋 **查询结果与图表 (基于初步建议):**",
        'no_data': "查询已成功执行，但没有返回任何数据。",
        'no_results': "查询未返回有效结果，也无明确错误信息。",
        'no_sql': "AI 未能生成 SQL 查询或提供明确指导。",
        'suggestions': "💡 或许您对以下分析方向感兴趣？",
        'no_action': "AI 返回了响应，但没有具体的操作或建议。"
    },
    'en': {
        'sql_empty': "SQL query is empty or invalid.",
        'data_not_loaded': "Data failed to load, cannot execute SQL query.",
        'sql_error': "SQL query execution error: {error}\nAttempted SQL: {query}",
        'ai_thinking': "AI is thinking...",
        'ai_thinking_framework': "AI is thinking using ({framework}) framework...",
        'ai_failed': "Sorry, the AI failed to generate a valid SQL query or analysis suggestion. Please try again later or adjust your question.",
        'ai_guidance': "AI Guidance: {text}",
        'data_insights': "##### 🤖 AI Data Insights",
        'analyzing_data': "AI is analyzing data...",
        'analyzing_data_framework': "AI is analyzing data using ({framework}) framework...",
        'results_chart': "📋 **Query Results & Chart:**",
        'no_analysis_text': "Could not get data analysis text from AI this time.",
        'analysis_failed': "AI failed to complete data analysis. Will try to use preliminary chart suggestion (if available).",
        'preliminary_chart': "📋 **Query Results & Chart (Preliminary):**",
        'no_data': "Query executed successfully but returned no data.",
        'no_results': "Query returned no valid results and no clear error message.",
        'no_sql': "AI failed to generate SQL query or provide clear guidance.",
        'suggestions': "💡 You might be interested in these analysis directions?",
        'no_action': "AI returned a response but no specific actions or suggestions."
    }
}


def get_text(key, lang='zh', **kwargs):
    """Helper function to get localized text with optional formatting"""
    return LANGUAGE_STRINGS[lang][key].format(**kwargs)


def execute_sql(sql_query: str, current_df_data: pd.DataFrame):
    if not sql_query or not sql_query.strip():
        return None, get_text('sql_empty')
    if current_df_data is None:
        return None, get_text('data_not_loaded')
    try:
        con = duckdb.connect(database=':memory:', read_only=False)
        con.register('df_data', current_df_data)
        result_df = con.execute(sql_query).fetchdf()
        con.close()
        return result_df, None
    except Exception as e:
        error_message = get_text('sql_error', error=e, query=sql_query)
        return None, error_message


def process_user_query(user_query: str, current_df_data: pd.DataFrame, active_analysis_framework_prompt: str = None,
                       lang='zh'):
    system_prompt = FULL_SYSTEM_PROMPT_EN if lang == 'en' else FULL_SYSTEM_PROMPT
    analysis_prompt_template = DATA_ANALYSIS_PROMPT_TEMPLATE_EN if lang == 'en' else DATA_ANALYSIS_PROMPT_TEMPLATE
    data_caveats = DATA_CAVEATS_INSTRUCTIONS_EN if lang == 'en' else DATA_CAVEATS_INSTRUCTIONS

    st.session_state.llm_conversation_history.append({"role": "user", "content": user_query})

    default_framework_name = "通用分析 (默认)" if lang == 'zh' else "General Analysis (Default)"
    selected_prompt_display_name = st.session_state.get("selected_analysis_prompt_display_name", default_framework_name)

    ui_user_content = user_query
    if active_analysis_framework_prompt and selected_prompt_display_name != default_framework_name:
        framework_prefix = "(Using framework: " if lang == 'en' else "（使用分析框架："
        framework_suffix = ")" if lang == 'en' else "）"
        ui_user_content = f"{framework_prefix}{selected_prompt_display_name}{framework_suffix}\n{user_query}"

    st.session_state.ui_messages.append({"role": "user", "content": ui_user_content})

    with st.chat_message("user"):
        st.markdown(ui_user_content)

    with st.chat_message("assistant"):
        assistant_ui_msg = {
            "role": "assistant",
            "analysis_framework_used": selected_prompt_display_name if active_analysis_framework_prompt else None,
            "sql_query": None,
            "chart_type": "table",
            "chart_params": {},
            "recommended_analyses": None,
            "llm_general_explanation": None,
            "query_result_df": None,
            "error_message": None,
            "data_analysis_text": None,
            "final_chart_explanation": None
        }

        # Determine spinner text based on language and framework
        spinner_text = get_text('ai_thinking', lang)
        if active_analysis_framework_prompt:
            spinner_text = get_text('ai_thinking_framework', lang, framework=selected_prompt_display_name)

        with st.spinner(spinner_text):
            llm_response_call1_data = get_llm_response_structured(
                st.session_state.llm_conversation_history,
                system_prompt,
                active_analysis_framework_prompt=active_analysis_framework_prompt,
                lang=lang
            )

        if not llm_response_call1_data:
            error_msg = get_text('ai_failed', lang)
            st.error(error_msg)
            assistant_ui_msg["error_message"] = error_msg
            st.session_state.llm_conversation_history.append({"role": "assistant", "content": f"Error: {error_msg}"})
            st.session_state.ui_messages.append(assistant_ui_msg)
            return

        generated_sql = llm_response_call1_data.get("sql_query")
        preliminary_chart_type = llm_response_call1_data.get("chart_type", "table")
        preliminary_chart_params = llm_response_call1_data
        assistant_ui_msg.update({
            "llm_general_explanation": llm_response_call1_data.get("explanation"),
            "recommended_analyses": llm_response_call1_data.get("recommended_analyses"),
            "sql_query": generated_sql,
            "chart_type": preliminary_chart_type,
            "chart_params": preliminary_chart_params
        })

        try:
            llm1_context_content = json.dumps(llm_response_call1_data)
        except TypeError:
            llm1_context_content = str(llm_response_call1_data)
        st.session_state.llm_conversation_history.append({"role": "assistant", "content": llm1_context_content})

        if assistant_ui_msg["llm_general_explanation"]:
            st.info(get_text('ai_guidance', lang, text=assistant_ui_msg["llm_general_explanation"]))

        query_result_df = None
        error_msg_sql = None

        if generated_sql and generated_sql.strip():
            print(f"Generated SQL (from LLM Call 1 - hidden from UI): {generated_sql}")
            query_result_df, error_msg_sql = execute_sql(generated_sql, current_df_data)
            assistant_ui_msg["query_result_df"] = query_result_df
            assistant_ui_msg["error_message"] = error_msg_sql

            if error_msg_sql:
                st.error(error_msg_sql)
            elif query_result_df is not None:
                if not query_result_df.empty:
                    st.markdown("---")
                    st.markdown(get_text('data_insights', lang))

                    analysis_spinner_text = get_text('analyzing_data', lang)
                    if active_analysis_framework_prompt:
                        analysis_spinner_text = get_text('analyzing_data_framework', lang,
                                                         framework=selected_prompt_display_name)

                    with st.spinner(analysis_spinner_text):
                        llm_response_call2_data = get_final_analysis_and_chart_details(
                            data_df=query_result_df,
                            user_query_for_analysis=user_query,
                            active_analysis_framework_prompt=active_analysis_framework_prompt,
                            base_data_analysis_prompt_template=analysis_prompt_template,
                            data_caveats_instructions=data_caveats,
                            lang=lang
                        )

                    if llm_response_call2_data:
                        assistant_ui_msg["data_analysis_text"] = llm_response_call2_data.get("analysis_text")
                        assistant_ui_msg["chart_type"] = llm_response_call2_data.get("chart_type",
                                                                                     preliminary_chart_type)
                        final_chart_params = {
                            "x_axis": llm_response_call2_data.get("x_axis"),
                            "y_axis": llm_response_call2_data.get("y_axis"),
                            "category_column": llm_response_call2_data.get("category_column"),
                            "value_column": llm_response_call2_data.get("value_column"),
                            "title": llm_response_call2_data.get("title", preliminary_chart_params.get("title",
                                                                                                       "分析结果图表" if lang == 'zh' else "Analysis Results Chart")),
                            "explanation": llm_response_call2_data.get("explanation")
                        }
                        assistant_ui_msg["chart_params"] = final_chart_params
                        assistant_ui_msg["final_chart_explanation"] = final_chart_params.get("explanation")

                        st.markdown(get_text('results_chart', lang))
                        current_chart_title = assistant_ui_msg["chart_params"].get("title")
                        generate_streamlit_chart(
                            assistant_ui_msg["chart_type"],
                            query_result_df,
                            assistant_ui_msg["chart_params"],
                            chart_key=f"current_chart_{len(st.session_state.ui_messages)}_{current_chart_title.replace(' ', '_')}"
                        )

                        if assistant_ui_msg["data_analysis_text"]:
                            st.info(assistant_ui_msg["data_analysis_text"])
                        else:
                            st.warning(get_text('no_analysis_text', lang))
                    else:
                        st.warning(get_text('analysis_failed', lang))
                        if not query_result_df.empty and preliminary_chart_type:
                            current_chart_title = preliminary_chart_params.get("title",
                                                                               "初步分析图表" if lang == 'zh' else "Preliminary Analysis Chart")
                            st.markdown(get_text('preliminary_chart', lang))
                            generate_streamlit_chart(
                                preliminary_chart_type,
                                query_result_df,
                                preliminary_chart_params,
                                chart_key=f"prelim_chart_{len(st.session_state.ui_messages)}_{current_chart_title.replace(' ', '_')}"
                            )
                else:
                    st.info(get_text('no_data', lang))
            else:
                st.warning(get_text('no_results', lang))

        elif assistant_ui_msg["recommended_analyses"]:
            pass
        elif not assistant_ui_msg["llm_general_explanation"]:
            st.markdown(get_text('no_sql', lang))

        if assistant_ui_msg["recommended_analyses"]:
            st.markdown(get_text('suggestions', lang))
            for i, rec in enumerate(assistant_ui_msg["recommended_analyses"]):
                title_rec, desc_rec, ex_query = rec.get('title'), rec.get('description'), rec.get('example_query')
                with st.container():
                    st.markdown(f"##### {title_rec}")
                    st.markdown(desc_rec)
                    if ex_query:
                        key = f"rec_btn_{i}_{user_query[:10].replace(' ', '_')}_{len(st.session_state.ui_messages)}"
                        btn_text = f"Try query: \"{ex_query}\"" if lang == 'en' else f"尝试查询: \"{ex_query}\""
                        if st.button(btn_text, key=key):
                            st.session_state.selected_suggestion_query = ex_query
                            st.rerun()
                    st.markdown("---")

        if not generated_sql and not assistant_ui_msg["recommended_analyses"] and \
                not assistant_ui_msg["llm_general_explanation"] and not assistant_ui_msg["data_analysis_text"]:
            st.info(get_text('no_action', lang))

        st.session_state.ui_messages.append(assistant_ui_msg)


def process_user_query_orchestrator(user_query, df_data, lang='en'):
    """
    【状态机模式】处理智能报告请求。
    此函数现在作为状态路由器，根据当前 job_status 执行相应阶段。
    """
    # 如果任务不存在，则初始化
    if "current_analysis_job" not in st.session_state:
        print("\n================== [智能报告流程初始化] ==================")
        print(f"用户问题: {user_query}")
        initial_status_message = "智能报告任务已启动..." if lang == 'zh' else "Smart Report task initiated..."
        st.session_state.current_analysis_job = {
            "job_status": "STARTED",  # 初始状态
            "original_query": user_query,
            "stages": {},
            "status_message": initial_status_message,
            "stage_info": "阶段 1/4：准备中..." if lang == 'zh' else "Stage 1/4: Preparing..."
        }
        st.rerun()
        return

    # 获取当前任务和状态
    job = st.session_state.current_analysis_job
    status = job.get("job_status")

    # --- 状态路由 ---

    # 阶段一：从 "STARTED" 状态开始，生成初步SQL
    if status == "STARTED":
        print("\n[Orchestrator] ==> STAGE 1: 生成初步SQL查询...")
        job.update({
            "status_message": "正在生成初步分析的SQL查询...",
            "stage_info": "阶段 1/4：生成初步查询" if lang == 'zh' else "Stage 1/4: Generating Initial Query"
        })
        system_prompt = FULL_SYSTEM_PROMPT_EN if lang == 'en' else FULL_SYSTEM_PROMPT
        llm_response1 = get_llm_response_structured(
            [{"role": "user", "content": job["original_query"]}], system_prompt, lang=lang
        )
        print("[Orchestrator] <== STAGE 1: 完成")

        if not llm_response1 or not llm_response1.get("sql_query"):
            job.update({"job_status": "FAILED", "status_message": "未能生成初步SQL查询。"})
            job.update({"job_status": "FAILED", "status_message": "未能生成初步SQL查询。"})
            if llm_response1:
                explanation = llm_response1.get("explanation")
            recommended_analyses = llm_response1.get("recommended_analyses")
            if explanation:
                print(f"LLM Explanation on failure: {explanation}")
            if recommended_analyses:
                print(f"LLM Recommended Analyses on failure: {recommended_analyses}")
        else:
            baseline_df, error_msg = execute_sql(llm_response1["sql_query"], df_data)
            if baseline_df is None:
                job.update({"job_status": "FAILED", "status_message": "执行初步SQL查询失败。"})
            else:
                job["stages"]["stage1_baseline"] = {"data": baseline_df, "sql": llm_response1["sql_query"]}
                job["job_status"] = "STAGE1_COMPLETE"  # 更新到下一状态
        st.rerun()

    # 阶段二：从 "STAGE1_COMPLETE" 状态开始，规划分析步骤
    elif status == "STAGE1_COMPLETE":
        print("\n[Orchestrator] ==> STAGE 2: 基于初步数据规划深度分析...")
        job.update({
            "status_message": "已发现关键信息，正在规划深度探查方案...",
            "stage_info": "阶段 2/4：规划深度分析" if lang == 'zh' else "Stage 2/4: Planning Deep Dive"
        })
        baseline_df = job["stages"]["stage1_baseline"]["data"]

        system_prompt = FULL_SYSTEM_PROMPT_EN if lang == 'en' else FULL_SYSTEM_PROMPT
        analysis_plan_json = get_analysis_plan(job["original_query"], baseline_df.head(20), system_prompt, lang=lang)
        print("[Orchestrator] <== STAGE 2: 完成")

        if not analysis_plan_json or "plan" not in analysis_plan_json or not analysis_plan_json["plan"]:
            job.update({"job_status": "FAILED", "status_message": "未能生成有效的分析计划。"})
        else:
            job["stages"]["stage2_plan"] = analysis_plan_json["plan"]
            job["stages"]["stage3_evidence"] = {}  # 初始化用于存储证据
            job["job_status"] = "STAGE2_COMPLETE"  # 更新到下一状态
        st.rerun()

    # 阶段三：从 "STAGE2_COMPLETE" 状态开始，执行计划
    elif status == "STAGE2_COMPLETE":
        print("\n[Orchestrator] ==> STAGE 3: 执行分析计划并收集数据...")
        job.update(
            {"stage_info": "阶段 3/4：执行并收集数据" if lang == 'zh' else "Stage 3/4: Executing & Gathering Data"})
        plan = job["stages"]["stage2_plan"]

        # 检查是否所有步骤都已执行
        current_step_index = len(job["stages"]["stage3_evidence"])
        if current_step_index < len(plan):
            step = plan[current_step_index]
            print(f"[Orchestrator]     - STAGE 3.{current_step_index + 1}: {step['purpose']}")
            job["status_message"] = f"正在执行第 {current_step_index + 1}/{len(plan)} 步: {step['purpose']}"
            evidence_df, error_msg = execute_sql(step['sql'], df_data)
            job["stages"]["stage3_evidence"][f"evidence_{current_step_index + 1}"] = {
                "purpose": step["purpose"], "dataframe": evidence_df,
                "data_markdown": evidence_df.to_markdown(index=False) if evidence_df is not None else "查询失败或无数据。"
            }
            # 保持状态不变，以便循环执行下一步
        else:
            print("[Orchestrator] <== STAGE 3: 所有步骤完成")
            job["job_status"] = "STAGE3_COMPLETE"  # 所有步骤完成后，更新到下一状态
        st.rerun()

    # 阶段四：从 "STAGE3_COMPLETE" 状态开始，生成报告
    elif status == "STAGE3_COMPLETE":
        print("\n[Orchestrator] ==> STAGE 4: 综合所有信息生成最终报告...")
        job.update({
            "status_message": "所有数据已收集，正在撰写最终分析报告...",
            "stage_info": "阶段 4/4：综合分析报告" if lang == 'zh' else "Stage 4/4: Synthesizing Report"
        })
        # evidence_for_llm = {k: {"purpose": v["purpose"], "data": v["data_markdown"]} for k, v in
        #                     job["stages"]["stage3_evidence"].items()}
        evidence_for_llm = job["stages"]["stage3_evidence"]
        final_report_json = get_synthesized_report(job["original_query"], evidence_for_llm, lang=lang)
        print("[Orchestrator] <== STAGE 4: 完成")
        print("\n================== [智能报告流程结束] ==================")

        if not final_report_json:
            job.update({"job_status": "FAILED", "status_message": "未能生成最终报告。"})
        else:
            job["stages"]["stage4_report"] = final_report_json
            job["job_status"] = "DONE"  # 任务最终完成
        st.rerun()