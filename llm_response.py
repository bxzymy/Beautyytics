from asyncio import base_events
import json
import os
import pandas as pd
import streamlit as st
from openai import OpenAI, OpenAIError

from prompt.prompt import DATABASE_SCHEMA_DESCRIPTION, FULL_SYSTEM_PROMPT
from prompt.prompt_en import DATABASE_SCHEMA_DESCRIPTION_EN

global_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
global_model_name = "qwen3-30b-a3b"

api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key and hasattr(st, 'secrets') and "DASHSCOPE_API_KEY" in st.secrets:
    api_key = st.secrets["DASHSCOPE_API_KEY"]

if not api_key:
    raise ValueError("No DASHSCOPE_API_KEY found. Please configure it in environment variables or Streamlit secrets.")

client = OpenAI(
    api_key=api_key,
    base_url=global_base_url,
)


def get_llm_response_structured(conversation_history_for_llm: list,
                                system_prompt_content: str,
                                model_name: str = global_model_name,
                                active_analysis_framework_prompt: str = None,
                                lang: str = 'zh'):
    """
    Get structured response from LLM with language support
    Args:
        lang: 'zh' for Chinese, 'en' for English
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key and hasattr(st, 'secrets') and "DASHSCOPE_API_KEY" in st.secrets:
        api_key = st.secrets["DASHSCOPE_API_KEY"]

    if not api_key:
        print(
            "Error: [LLM Call 1] DASHSCOPE_API_KEY not found. Please configure it in environment variables or Streamlit secrets.")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url=global_base_url,
    )

    messages_for_api = [
        {"role": "system", "content": system_prompt_content}
    ]

    if active_analysis_framework_prompt:
        if lang == 'zh':
            framework_instruction = (
                "用户希望在一个更广泛的分析框架下进行探索。这是他们选择的框架，请将其作为理解用户意图的背景参考：\n"
                "<analysis_framework_context>\n"
                f"{active_analysis_framework_prompt}\n"
                "</analysis_framework_context>\n"
                "请注意：这个框架描述了用户可能希望达成的整体分析目标。\n"
                "然而，在当前这一步，你的核心任务是：\n"
                "1. 严格专注于用户接下来提出的【具体问题】。\n"
                "2. 根据这个【具体问题】，生成一个相关的、可执行的SQL查询，以获取支撑上述分析框架的数据。\n"
                "3. 严格遵循系统先前定义的指示，以JSON格式返回结果（主要期望 'sql_query'，同时可包含初步的 'chart_type', 'title', 'explanation', 'recommended_analyses' 等关键字段）。\n"
                "你的整个回复必须且只能是一个JSON对象字符串，不应包含任何JSON对象之外的文字、解释或标记。\n"
                "请不要试图在这一步完成分析框架中的所有内容或输出框架本身要求的复杂报告，此阶段重点是为后续分析步骤准备数据查询。"
            )
        else:
            framework_instruction = (
                "The user wants to explore within a broader analytical framework. Here is the framework they selected. Please use this as background context for understanding their intent:\n"
                "<analysis_framework_context>\n"
                f"{active_analysis_framework_prompt}\n"
                "</analysis_framework_context>\n"
                "Note: This framework describes the overall analytical objectives the user may want to achieve.\n"
                "However, at this stage, your core tasks are:\n"
                "1. Strictly focus on the specific question the user asks next.\n"
                "2. Based on this specific question, generate a relevant, executable SQL query to obtain data supporting the above framework.\n"
                "3. Strictly follow the system's previously defined instructions to return results in JSON format (primarily expecting 'sql_query', while optionally including preliminary 'chart_type', 'title', 'explanation', 'recommended_analyses' and other key fields).\n"
                "Your entire response must be and can only be a JSON object string, and should not contain any text, explanation, or markup outside the JSON object.\n"
                "Please do not attempt to complete all content in the analysis framework or output complex reports required by the framework itself at this stage. The focus at this stage is to prepare data queries for subsequent analysis steps."
            )
        messages_for_api.append({"role": "user", "content": framework_instruction})

    messages_for_api.extend(conversation_history_for_llm)

    try:
        print(f"Sending request to LLM ({model_name}) (LLM Call 1 - expecting SQL and preliminary suggestions)...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages_for_api,
            temperature=0.0,
            extra_body={"enable_thinking": False},
        )

        raw_response_content = completion.choices[0].message.content.strip()
        print(f"[LLM Call 1] LLM raw response: {raw_response_content}")

        cleaned_response_content = raw_response_content
        if cleaned_response_content.startswith("```json"):
            cleaned_response_content = cleaned_response_content[len("```json"):].strip()
        if cleaned_response_content.endswith("```"):
            cleaned_response_content = cleaned_response_content[:-len("```")].strip()

        llm_output = None
        try:
            llm_output = json.loads(cleaned_response_content)
        except json.JSONDecodeError as e:
            if "Extra data" in str(e) and e.pos > 0:
                json_part = cleaned_response_content[:e.pos].strip()
                print(
                    f"[LLM Call 1] Detected 'Extra data' error, attempting to reparse truncated JSON (position: {e.pos}). Truncated content: '{json_part[:200]}...'")
                try:
                    llm_output = json.loads(json_part)
                    print("[LLM Call 1] Successfully reparsed truncated JSON.")
                except json.JSONDecodeError as e2:
                    print(f"[LLM Call 1] Failed to reparse truncated JSON: {e2}")
                    print(f"[LLM Call 1] Problematic raw response content (cleaned): {cleaned_response_content}")
                    return None
            else:
                print(f"[LLM Call 1] LLM returned non-standard JSON format, parsing error: {e}")
                print(f"[LLM Call 1] Problematic raw response content (cleaned): {cleaned_response_content}")
                return None

        if llm_output is None:
            print(f"[LLM Call 1] Failed to parse JSON response.")
            return None

        if not ("sql_query" in llm_output or "recommended_analyses" in llm_output):
            print("[LLM Call 1] LLM response JSON missing key fields sql_query and recommended_analyses.")
            return None

        if "sql_query" in llm_output and isinstance(llm_output["sql_query"], str):
            sql_query = llm_output["sql_query"].strip()

            if sql_query.startswith("```sql"):
                sql_query = sql_query[len("```sql"):].strip()
            if sql_query.endswith("```"):
                sql_query = sql_query[:-len("```")].strip()
            llm_output["sql_query"] = sql_query

        return llm_output

    except Exception as e:
        print(
            f"Unknown error occurred when calling LLM API or processing response (get_llm_response_structured - Call 1): {e}")
        import traceback
        traceback.print_exc()
        return None


def get_final_analysis_and_chart_details(
        data_df: pd.DataFrame,
        user_query_for_analysis: str,
        active_analysis_framework_prompt: str = None,
        base_data_analysis_prompt_template: str = None,
        data_caveats_instructions: str = None,
        model_name: str = global_model_name,
        max_tokens_data_representation: int = 4000,
        lang: str = 'zh'
):
    print(f"\nLanguage for analysis: {lang}\n")

    """
    Perform second LLM call with language support
    Args:
        lang: 'zh' for Chinese, 'en' for English
    """

    try:
        analysis_prefix = ""
        # if data_df.shape[0] > 50:
        #     df_for_analysis = data_df.head(50)
        #     analysis_prefix = f"Note: The original data result contains {data_df.shape[0]} rows. For analysis efficiency, only the first 50 rows are used here.\n\n" if lang == 'en' else f"注意：原始数据结果包含 {data_df.shape[0]} 行，为提高分析效率，此处仅基于前50行数据进行分析。\n\n"
        # else:
        #     df_for_analysis = data_df
        df_for_analysis = data_df

        data_string = df_for_analysis.to_markdown(index=False)
        current_length = len(data_string)
        if current_length > max_tokens_data_representation:
            cutoff_point = data_string.rfind('\n', 0, max_tokens_data_representation)
            data_string = data_string[:cutoff_point if cutoff_point != -1 else max_tokens_data_representation]
            data_string += "\n... (data truncated due to length limit)" if lang == 'en' else "\n... (数据因长度限制被截断)"
            print(f"Warning: [LLM Call 2] Data for LLM analysis was truncated. Original length: {current_length}")
    except Exception as e:
        print(f"Error: [LLM Call 2] Error converting DataFrame to markdown: {e}")
        data_string = str(
            data_df.head()) if 'data_df' in locals() else "Data conversion failed" if lang == 'en' else "数据转换失败"

    if lang == 'zh':
        system_message_for_call2 = (
            """
            你是一位专业的数据分析师和可视化专家。  
            你的任务是基于用户提供的原始问题、分析框架（若有）、实际查询到的数据及数据检查要点，  
            进行深入的文本分析，并给出具体且最终的图表化建议。  

            请严格以JSON格式回复，所有与图表相关的字段（如 "chart_type"、"x_axis"、"title"、"explanation" 等）  
            必须作为顶层键直接返回，禁止嵌套在任何子对象（如 "chart_suggestion"）内。

            """
        )
    else:
        system_message_for_call2 = (
            """
            You are a professional data analyst and visualization expert.
            Your task is to perform in-depth textual analysis based on the user's original question, analysis framework (if any), the actual queried data, and data checklist points,
            and provide concrete and final recommendations for visualization.

            Please respond strictly in JSON format. All chart-related fields (such as "chart\_type", "x\_axis", "title", "explanation", etc.)
            must be returned as top-level keys directly, and must NOT be nested inside any sub-objects (such as inside a "chart\_suggestion").

            You must answer in English. Do not use Chinese in any part of your response.
"""
        )

    prompt_sections = []
    prompt_sections.append(
        f"用户的原始查询或分析主题是：'{user_query_for_analysis}'" if lang == 'zh' else f"The user's original query or analysis topic is: '{user_query_for_analysis}'")

    analysis_guidance_section = ""
    if active_analysis_framework_prompt:
        if lang == 'zh':
            prompt_sections.append(
                "【分析框架参考】\n用户先前选择了以下分析框架，请在解读数据和构建图表时参考此框架的目标和要求：\n"
                f"<analysis_framework_context>\n{active_analysis_framework_prompt}\n</analysis_framework_context>"
            )
            analysis_guidance_section = "请严格按照上述分析框架的要求，结合下面的实际数据进行分析并撰写报告部分。"
        else:
            prompt_sections.append(
                "【Analysis Framework Reference】\nThe user previously selected the following analysis framework. Please refer to this framework's objectives and requirements when interpreting data and constructing charts:\n"
                f"<analysis_framework_context>\n{active_analysis_framework_prompt}\n</analysis_framework_context>"
            )
            analysis_guidance_section = "Please strictly follow the requirements of the above analysis framework and analyze the actual data below to prepare the report section."
    elif base_data_analysis_prompt_template:
        analysis_guidance_section = (
                base_data_analysis_prompt_template.replace("{data_format}", "markdown table")
                .replace("{data_string}", "")
                .replace("This is the data content:", "")
                .replace("Please provide your analysis:", "").strip()
                + (
                    "\n请针对下方提供的实际数据，提供你的中文分析结果。" if lang == 'zh' else "\nPlease provide your English analysis results for the actual data provided below.")
        )
        prompt_sections.append(
            f"【通用分析指引】\n{analysis_guidance_section}" if lang == 'zh' else f"【General Analysis Guidance】\n{analysis_guidance_section}")
    else:
        if lang == 'zh':
            prompt_sections.append(
                "【通用分析指引】\n请针对下方提供的实际数据，提供一段简明的中文文本分析和解读，侧重于关键洞察、趋势或对业务用户有价值的发现。")
        else:
            prompt_sections.append(
                "【General Analysis Guidance】\nPlease provide a concise English text analysis and interpretation of the actual data provided below, focusing on key insights, trends, or findings valuable to business users.")

    if lang == 'zh':
        prompt_sections.append(f"【实际查询数据】\n以下是根据用户先前请求查询得到的数据（Markdown格式）:\n{data_string}")
    else:
        prompt_sections.append(
            f"【Actual Queried Data】\nHere is the data obtained from the user's previous request (in Markdown format):\n{data_string}")

    if data_caveats_instructions:
        prompt_sections.append(
            f"【数据检查与注意事项】\n{data_caveats_instructions}" if lang == 'zh' else f"【Data Checks & Caveats】\n{data_caveats_instructions}")
    else:
        if lang == 'zh':
            prompt_sections.append("【数据检查与注意事项】\n请仔细检查数据，留意潜在问题如地理名称不一致、缺失值或异常。")
        else:
            prompt_sections.append(
                "【Data Checks & Caveats】\nPlease carefully examine the data, noting potential issues such as inconsistent geographic names, missing values, or anomalies.")

    if lang == 'zh':
        prompt_sections.append(
            "【任务要求与输出格式】\n"
            "1. **文本分析 (`analysis_text`)**: 根据上述指引和数据，提供详细的中文文本分析。\n"
            "2. **最终图表建议**: 根据实际数据和分析，推荐最合适的图表类型，并提供以下参数作为JSON对象的顶层键：\n"
            "   - `chart_type`: (string) 推荐的图表类型（可选值：\"line\", \"bar\", \"pie\", \"scatter\", \"table\"）。\n"
            "   - `x_axis`: (string, 可选) X轴的列名。\n"
            "   - `y_axis`: (string or list of strings, 可选) Y轴的列名。\n"
            "   - `category_column`: (string, 可选) 饼图的分类列名。\n"
            "   - `value_column`: (string, 可选) 饼图的数值列名。\n"
            "   - `title`: (string) 基于数据内容和分析的图表标题。\n"
            "   - `explanation`: (string) 对图表所展示内容的解释，以及关键洞察，可结合数据注意事项。\n"
            "请将所有结果严格封装在一个JSON对象中返回，确保所有上述图表参数键都在JSON的顶层。"
        )
    else:
        prompt_sections.append(
            "【Task Requirements & Output Format】\n"
            "1. **Text Analysis (`analysis_text`)**: Provide detailed English text analysis based on the above guidance and data.\n"
            "2. **Final Chart Recommendations**: Recommend the most appropriate chart type based on the actual data and analysis, providing the following parameters as top-level keys in the JSON object:\n"
            "   - `chart_type`: (string) Recommended chart type (options: \"line\", \"bar\", \"pie\", \"scatter\", \"table\").\n"
            "   - `x_axis`: (string, optional) Column name for X-axis.\n"
            "   - `y_axis`: (string or list of strings, optional) Column name(s) for Y-axis.\n"
            "   - `category_column`: (string, optional) Category column name for pie charts.\n"
            "   - `value_column`: (string, optional) Value column name for pie charts.\n"
            "   - `title`: (string) Chart title based on data content and analysis.\n"
            "   - `explanation`: (string) Explanation of what the chart shows, along with key insights, potentially incorporating data caveats.\n"
            "Please encapsulate all results strictly in a single JSON object, ensuring all the above chart parameter keys are at the top level of the JSON."
        )

    user_content_for_call2 = "\n\n---\n\n".join(prompt_sections)

    messages_for_api = [
        {"role": "system", "content": system_message_for_call2},
        {"role": "user", "content": user_content_for_call2}
    ]

    try:
        print(f"Sending data to LLM ({model_name}) for analysis and final chart recommendations (LLM Call 2)...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages_for_api,
            temperature=0.3,
            extra_body={"enable_thinking": False},
        )
        raw_response_content = completion.choices[0].message.content.strip()
        print(f"[LLM Call 2] LLM raw response: {raw_response_content}")

        cleaned_response_content = raw_response_content
        if cleaned_response_content.startswith("```json"):
            cleaned_response_content = cleaned_response_content[len("```json"):].strip()
        if cleaned_response_content.endswith("```"):
            cleaned_response_content = cleaned_response_content[:-len("```")].strip()

        llm_output = json.loads(cleaned_response_content)

        if "chart_suggestion" in llm_output and isinstance(llm_output["chart_suggestion"], dict):
            print("[LLM Call 2] Detected 'chart_suggestion' key, attempting to flatten structure.")
            chart_details = llm_output.pop("chart_suggestion")
            for key, value in chart_details.items():
                if key not in llm_output:
                    llm_output[key] = value
        elif "chart_suggestions" in llm_output and isinstance(llm_output["chart_suggestions"], dict):
            print("[LLM Call 2] Detected 'chart_suggestions' key, attempting to flatten structure.")
            chart_details = llm_output.pop("chart_suggestions")
            for key, value in chart_details.items():
                if key not in llm_output:
                    llm_output[key] = value

        required_keys = ["analysis_text", "chart_type", "title", "explanation"]
        missing_keys = [key for key in required_keys if key not in llm_output]
        if missing_keys:
            print(
                f"[LLM Call 2] LLM response JSON missing one or more key fields: {missing_keys}. Current top-level keys: {list(llm_output.keys())}")
            return None

        if "analysis_text" in llm_output and analysis_prefix:
            llm_output["analysis_text"] = analysis_prefix + llm_output["analysis_text"]

        return llm_output

    except json.JSONDecodeError as e:
        print(f"[LLM Call 2] LLM returned non-standard JSON format, parsing error: {e}")
        print(f"[LLM Call 2] Problematic raw response content (cleaned): {cleaned_response_content}")
        return None
    except Exception as e:
        print(
            f"Unknown error occurred when calling LLM API or processing response (get_final_analysis_and_chart_details - Call 2): {e}")
        import traceback
        traceback.print_exc()
        return None


PLANNER_PROMPT_ZH = """
# Overall Context and Database Schema
{full_system_prompt}

---

# Role: Senior Data Analysis Director

## Profile
- description: You are a seasoned Data Analysis Director with the capability to design analytical plans and write executable SQL queries.

## Skills
- Translate the user's initial question into analytical hypotheses.
- Identify patterns, anomalies, and areas for further investigation from data summaries.
- Write SQL queries that are directly executable on DuckDB, following column quoting conventions.
- Output structured JSON analytical plans.

## Background
The user posed a question based on the database schema: “{original_query}”.
An initial query has been executed, and the following is the returned data summary (in Markdown format):
{data_summary}

## Goals
- Propose 3 to 5 specific and insightful analytical hypotheses.
- For each hypothesis, write a clear, syntactically correct SQL query.
- All analysis should focus on the "df_data" table, and column names must be enclosed in double quotes.
- The output should be a single JSON object with no additional content.

## OutputFormat
{
"plan": [
{
"purpose": "A concise description of the analysis goal of this query.",
"sql": "SELECT ... FROM \"df_data\" WHERE ...;"
},
{
"purpose": "A different analytical objective.",
"sql": "SELECT ... FROM \"df_data\" WHERE ...;"
}
]
}

## Rules
1. All SQL queries must operate on the "df_data" table.
2. All column names must be enclosed in double quotes.
3. Each analysis must include both a purpose and an executable SQL query.
4. Output must contain only a JSON object formatted according to the specified structure.

## Workflows
1. Read the system context and data summary to understand the analysis background.
2. Analyze the initial data to identify patterns or anomalies worth deeper investigation.
3. Build several specific analytical hypotheses based on these findings.
4. Write DuckDB SQL queries for each hypothesis.
5. Output the complete plan in structured JSON format.

## Init
Your current task is to design a multi-step analytical plan based on the initial data summary. Ensure you fully understand the system context, the user's question, and the data summary before proceeding.
"""

PLANNER_PROMPT_EN = """
# Overall Context and Database Schema
{full_system_prompt}

---

# Your New Task: Analysis Planning

Based on the schema and rules provided above, your new task is to act as a senior data analysis director. Devise a multi-step analysis plan based on the initial data summary below.

# Context
The user has asked a general question: "{original_query}".
An initial query has been run, and here is a summary of the data returned (in markdown format):
{data_summary}

# Goal
Based on this initial data, identify key patterns, anomalies, or areas that warrant deeper investigation.
Formulate 3-5 specific, insightful analytical hypotheses. For each hypothesis, create a concrete, executable DuckDB SQL query to test it.

# Constraints
- The SQL must query the "df_data" table.
- All column names in SQL must be enclosed in double quotes.
- The purpose of each query must be clearly stated.
- Your entire output must be a single, valid JSON object and nothing else.

# Output Format
{{
  "plan": [
    {{
      "purpose": "A clear, concise description of what this query aims to investigate.",
      "sql": "SELECT ... FROM \\"df_data\\" WHERE ...;"
    }},
    {{
      "purpose": "Another distinct investigative purpose.",
      "sql": "SELECT ... FROM \\"df_data\\" WHERE ...;"
    }}
  ]
}}
"""

SYNTHESIZER_PROMPT_ZH = """
# Role: Data Storytelling Specialist and Business Strategy Advisor

## Profile
- author: LangGPT
- version: 1.0
- language: English
- description: You are an expert in transforming data analysis results into business insights and strategic recommendations, with a strong talent for storytelling with data.

## Skills
- Integrate outputs from multi-step analyses to extract core insights.
- Build logically sound and narratively compelling data report structures.
- Offer actionable strategic recommendations grounded in data evidence.
- Proficient in organizing structured output using Markdown and chart parameters.

## Background
The user initially proposed a business goal: "{original_query}". To achieve this, a series of data analyses were conducted. Below is all the collected data evidence during the analysis process (provided in JSON format, each evidence includes its analytical purpose and data content in Markdown format).

## Data Evidence
{evidence_json}

## Goals
- Integrate all data points into a complete report with storytelling and action orientation.
- The report should not only present data but also reveal relationships, trends, and translate them into executable business recommendations.

## OutputFormat
{
  "title": "An engaging title for the final report",
  "summary": "A 2-3 sentence high-level summary of key findings and recommendations.",
  "chapters": [
    {
      "title": "Chapter title, e.g., 'Overall Sales Overview'",
      "content": "Detailed narrative of this chapter, deriving insights from the data evidence, written in Markdown.",
      "chart_type": "line",
      "chart_params": {
        "data_key": "The key corresponding to a piece of data evidence",
        "x_axis": "Name of the X-axis field",
        "y_axis": ["Name of Y-axis field 1", "Name of Y-axis field 2"]
      }
    }
    // There can be multiple chapters, each following the same structure
  ],
  "recommendations": [
    "First actionable business recommendation",
    "Second actionable business recommendation"
  ]
}

## Rules
1. Each chapter's `chart_params.data_key` must match a valid data evidence key.
2. The report must be analytically deep, logically connecting the data points.
3. All recommendations must directly relate to the findings and be actionable.
4. When specifying `x_axis` and `y_axis`, you must and can only select from the following actual column names: {column_list}. Do not invent or use any column names outside this list. Exact match required, including case and underscores.

## Workflows
1. Interpret the original goal and content of data evidence.
2. Extract insights from each data segment and construct the overall logic framework.
3. Write in-depth, story-driven content for each chapter, including chart parameters.
4. Conduct integrated analysis, produce strategic recommendations, and finalize into valid JSON format.

# Context
1. The user’s original goal is: {original_query}
In this analysis, the field "channel" is a key dimension. Business classifications by field value are as follows:
- Tmall, JD → classified as "Online Channels"
- Other values such as Suning, Walmart, etc. → classified as "Offline Channels"

Please use "Online Channels / Offline Channels" in the report, charts, and recommendations, instead of original values or autogenerated IDs.

2. `data_key` must be selected from the provided list of evidence keys. Creating new names is prohibited.
"chart_params": 
{
    "data_key": "The value must be exactly selected from the given list of evidence keys (e.g., 'evidence_1', 'baseline'). Creating new names is strictly forbidden.",
    ...
}
"""

SYNTHESIZER_PROMPT_EN = """
You are a master data storyteller and business strategist. Your job is to synthesize findings from multiple data analyses into a single, coherent, and actionable report.

# Context
The user's original objective was: "{original_query}".
To answer this, a multi-step analysis was conducted. You have been provided with all the data evidence collected. Each piece of data is keyed and contains its original purpose and the data itself in markdown format.

# Data Evidence
{evidence_json}

# Goal
Weave a compelling narrative from these disparate data points. Your report should not just present data; it must connect the dots, reveal the underlying story, and provide strategic recommendations.

# Output Format
Your entire output must be a single, valid JSON object that represents the final report. The structure should be:
{{
  "title": "A compelling title for the final report.",
  "summary": "A high-level executive summary of the key findings and recommendations, 2-3 sentences.",
  "chapters": [
    {{
      "title": "Title for the first chapter (e.g., 'Overall Sales Landscape').",
      "content": "A detailed narrative for this chapter, explaining the insights derived from the relevant data evidence. Use markdown for formatting.",
      "chart_type": "line",
      "chart_params": {{
        "data_key": "key_of_the_evidence_data_to_use",
        "x_axis": "column_name",
        "y_axis": ["column_name1", "column_name2"]
      }}
    }},
    {{
      "title": "Title for the second chapter (e.g., 'Deep Dive into Product Performance').",
      "content": "Another detailed narrative for this chapter...",
      "chart_type": "bar",
      "chart_params": {{
         "data_key": "key_of_the_evidence_data_to_use",
         "x_axis": "category_column",
         "y_axis": "value_column"
      }}
    }}
  ],
  "recommendations": [
    "First actionable business recommendation.",
    "Second actionable business recommendation."
  ]
}}

# Constraints
- For each chapter's chart, `chart_params.data_key` MUST match one of the keys from the provided Data Evidence.
- The analysis must be deep, connecting different pieces of evidence where appropriate.
- Recommendations must be concrete and directly supported by the findings.
"""


def get_analysis_plan(original_query: str, data_summary_df: pd.DataFrame, full_system_prompt: str, lang: str = 'en'):
    print("Requesting analysis plan from LLM (Stage 2)...")

    if lang == 'zh':
        prompt_template = PLANNER_PROMPT_ZH
    else:
        prompt_template = PLANNER_PROMPT_EN

    data_summary_str = data_summary_df.to_markdown(index=False)

    if len(data_summary_str) > 4000:
        data_summary_str = data_summary_str[:4000] + "\n... (data truncated)"

    # print(f"[LLM Planner] Data summary length: {len(data_summary_str)} characters")
    # print(f"full_system_prompt:{full_system_prompt}\n original_query:{original_query}\n data_summary_str:{data_summary_str}")

    system_prompt_content = prompt_template.format(
        full_system_prompt=full_system_prompt,
        original_query=original_query,
        data_summary=data_summary_str
    )
    messages_for_api = [{"role": "system", "content": system_prompt_content}]

    raw_response = ""
    try:
        completion = client.chat.completions.create(
            model=global_model_name,
            messages=messages_for_api,
            temperature=0.1,
            response_format={"type": "json_object"},
            extra_body={"enable_thinking": False},
        )
        raw_response = completion.choices[0].message.content.strip()
        print(f"[LLM Planner] Raw response: {raw_response}")

        cleaned_response = raw_response
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[len("```json"):].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-len("```")].strip()

        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error getting analysis plan from LLM: {e}")
        print(f"Problematic raw response: {raw_response}")
        return None


def get_synthesized_report(original_query: str, evidence_data_map: dict, lang: str = 'en'):
    """
    Calls the LLM to synthesize a final report from multiple pieces of evidence.

    Args:
        original_query (str): The user's initial question.
        evidence_data_map (dict): A dictionary where keys are evidence IDs and values
                                  are dicts containing purpose and markdown data.
    """
    print("Requesting synthesized report from LLM (Stage 4)...")
    if lang == 'zh':
        prompt_template = SYNTHESIZER_PROMPT_ZH
    else:
        prompt_template = SYNTHESIZER_PROMPT_EN

    evidence_for_prompt = {
        key: {"purpose": value["purpose"], "data": value.get("data_markdown", "No data available.")}
        for key, value in evidence_data_map.items()
    }
    evidence_json_str = json.dumps(evidence_for_prompt, indent=2, ensure_ascii=False)

    if len(evidence_json_str) > 8000:
        print(f"Warning: Evidence data is very long ({len(evidence_json_str)} chars) and may be truncated.")
        evidence_json_str = evidence_json_str[:8000] + "\n... (evidence truncated)"

    all_columns = set()
    for evidence in evidence_data_map.values():
        if evidence.get("dataframe") is not None and not evidence["dataframe"].empty:
            all_columns.update(evidence["dataframe"].columns)
    print(f"evidence_data_map keys: {list(evidence_data_map.keys())}")

    system_prompt_content = prompt_template.format(
        original_query=original_query,
        evidence_json=evidence_json_str,
        column_list=str(list(all_columns))
    )
    messages_for_api = [{"role": "system", "content": system_prompt_content}]

    raw_response = ""
    try:
        completion = client.chat.completions.create(
            model=global_model_name,
            messages=messages_for_api,
            temperature=0.3,
            response_format={"type": "json_object"},
            extra_body={"enable_thinking": False},
        )
        raw_response = completion.choices[0].message.content.strip()
        print(f"[LLM Synthesizer] Raw response: {raw_response}")
        return json.loads(raw_response)
    except Exception as e:
        print(f"Error getting synthesized report from LLM: {e}")
        print(f"Problematic raw response: {raw_response}")
        return None