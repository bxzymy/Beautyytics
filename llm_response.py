import json
import os
import pandas as pd
import streamlit as st
from openai import OpenAI, OpenAIError


# DATA_ANALYSIS_PROMPT_TEMPLATE 和其他基础Prompt组件将由调用方 (app.py) 传入或在app.py中构建

def get_llm_response_structured(conversation_history_for_llm: list,
                                system_prompt_content: str,  # 通常是 FULL_SYSTEM_PROMPT (包含DB Schema和SQL生成规则)
                                model_name: str = "qwen-plus",
                                active_analysis_framework_prompt: str = None):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key and hasattr(st, 'secrets') and "DASHSCOPE_API_KEY" in st.secrets:
        api_key = st.secrets["DASHSCOPE_API_KEY"]

    if not api_key:
        print("错误：[LLM Call 1] 未找到 DASHSCOPE_API_KEY。请在环境变量或 Streamlit secrets 中配置。")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    messages_for_api = [
        {"role": "system", "content": system_prompt_content}
    ]

    if active_analysis_framework_prompt:
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
            "你的整个回复必须且只能是一个JSON对象字符串，不应包含任何JSON对象之外的文字、解释或标记。\n"  # 强化指令
            "请不要试图在这一步完成分析框架中的所有内容或输出框架本身要求的复杂报告，此阶段重点是为后续分析步骤准备数据查询。"
        )
        messages_for_api.append({"role": "user", "content": framework_instruction})

    messages_for_api.extend(conversation_history_for_llm)

    try:
        print(f"正在向 LLM ({model_name}) 发送请求 (LLM Call 1 - 期望SQL和初步建议)...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages_for_api,
            temperature=0.0,
        )

        raw_response_content = completion.choices[0].message.content.strip()
        print(f"[LLM Call 1] LLM 原始响应: {raw_response_content}")

        # 清理可能的Markdown代码块标记
        cleaned_response_content = raw_response_content
        if cleaned_response_content.startswith("```json"):
            cleaned_response_content = cleaned_response_content[len("```json"):].strip()
        if cleaned_response_content.endswith("```"):
            cleaned_response_content = cleaned_response_content[:-len("```")].strip()

        llm_output = None
        try:
            llm_output = json.loads(cleaned_response_content)
        except json.JSONDecodeError as e:
            if "Extra data" in str(e) and e.pos > 0:  # 检查是否有 e.pos 属性并且大于0
                # 尝试只解析到错误发生位置之前的部分
                json_part = cleaned_response_content[:e.pos].strip()
                print(
                    f"[LLM Call 1] 检测到 'Extra data' 错误，尝试重新解析截断的JSON (位置: {e.pos})。截断内容: '{json_part[:200]}...'")
                try:
                    llm_output = json.loads(json_part)
                    print("[LLM Call 1] 截断JSON后重新解析成功。")
                except json.JSONDecodeError as e2:
                    print(f"[LLM Call 1] 截断JSON后重新解析失败: {e2}")
                    print(f"[LLM Call 1] 有问题的原始响应内容 (清理后): {cleaned_response_content}")
                    return None
            else:
                # 其他类型的JSON解析错误
                print(f"[LLM Call 1] LLM 返回内容非标准JSON格式，解析错误: {e}")
                print(f"[LLM Call 1] 有问题的原始响应内容 (清理后): {cleaned_response_content}")
                return None

        if llm_output is None:  # 如果在try-except后llm_output仍为None
            print(f"[LLM Call 1] 未能成功解析JSON响应。")
            return None

        if not ("sql_query" in llm_output or "recommended_analyses" in llm_output):
            print("[LLM Call 1] LLM响应JSON中缺少sql_query和recommended_analyses关键字段。")
            return None  # 或者根据实际需求返回一个错误标识

        if "sql_query" in llm_output and isinstance(llm_output["sql_query"], str):
            sql_query = llm_output["sql_query"].strip()
            # 移除SQL查询语句可能存在的Markdown标记 (虽然通常不应该有)
            if sql_query.startswith("```sql"):
                sql_query = sql_query[len("```sql"):].strip()
            if sql_query.endswith("```"):
                sql_query = sql_query[:-len("```")].strip()
            llm_output["sql_query"] = sql_query

        return llm_output

    except Exception as e:  # 更广泛的异常捕获
        print(f"调用 LLM API 或处理响应时发生未知错误 (get_llm_response_structured - Call 1): {e}")
        import traceback
        traceback.print_exc()
        return None


def get_final_analysis_and_chart_details(
        data_df: pd.DataFrame,
        user_query_for_analysis: str,
        active_analysis_framework_prompt: str = None,
        base_data_analysis_prompt_template: str = None,
        data_caveats_instructions: str = None,
        model_name: str = "qwen-plus",
        max_tokens_data_representation: int = 4000
):
    """
    执行第二轮LLM调用：基于实际查询到的数据、分析框架和数据注意事项，生成文本分析和最终的图表参数。
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key and hasattr(st, 'secrets') and "DASHSCOPE_API_KEY" in st.secrets:
        api_key = st.secrets["DASHSCOPE_API_KEY"]

    if not api_key:
        print("错误：[LLM Call 2] 进行数据分析时未找到 DASHSCOPE_API_KEY。")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    try:
        analysis_prefix = ""
        if data_df.shape[0] > 50:
            df_for_analysis = data_df.head(50)
            analysis_prefix = f"注意：原始数据结果包含 {data_df.shape[0]} 行，为提高分析效率，此处仅基于前50行数据进行分析。\n\n"
        else:
            df_for_analysis = data_df

        data_string = df_for_analysis.to_markdown(index=False)
        current_length = len(data_string)
        if current_length > max_tokens_data_representation:
            cutoff_point = data_string.rfind('\n', 0, max_tokens_data_representation)
            data_string = data_string[:cutoff_point if cutoff_point != -1 else max_tokens_data_representation]
            data_string += "\n... (数据因长度限制被截断)"
            print(f"警告：[LLM Call 2] 用于LLM分析的数据被截断。原始代表长度: {current_length}")
    except Exception as e:
        print(f"错误：[LLM Call 2] 将DataFrame转换为markdown时出错: {e}")
        data_string = str(data_df.head()) if 'data_df' in locals() else "数据转换失败"  # Fallback


    prompt_sections = []
    prompt_sections.append(f"用户的原始查询或分析主题是：'{user_query_for_analysis}'")

    analysis_guidance_section = ""
    if active_analysis_framework_prompt:
        prompt_sections.append(
            "【分析框架参考】\n用户先前选择了以下分析框架，请在解读数据和构建图表时参考此框架的目标和要求：\n"
            f"<analysis_framework_context>\n{active_analysis_framework_prompt}\n</analysis_framework_context>"
        )
        analysis_guidance_section = "请严格按照上述分析框架的要求，结合下面的实际数据进行分析并撰写报告部分。"
    elif base_data_analysis_prompt_template:  # 通常是 prompt.DATA_ANALYSIS_PROMPT_TEMPLATE
        # 此处假设 base_data_analysis_prompt_template 包含了核心的通用分析引导文本
        # 并且不包含 {data_string} 或 {data_format} 占位符，因为数据会在下面专门提供
        # 如果它包含占位符，app.py 在传入前应处理掉或传入一个不含占位符的纯指令文本
        # 为简化，这里直接使用一个通用的分析引导文本，或者app.py应传入处理好的文本
        analysis_guidance_section = (
                base_data_analysis_prompt_template.replace("{data_format}", "markdown table")
                .replace("{data_string}", "")  # 移除数据占位符，数据单独提供
                .replace("这是数据内容:", "")  # 清理模板中数据引入的引导语
                .replace("请提供你的分析:", "").strip()  # 清理末尾的引导语
                + "\n请针对下方提供的实际数据，提供你的中文分析结果。"
        )
        prompt_sections.append(f"【通用分析指引】\n{analysis_guidance_section}")
    else:
        prompt_sections.append(
            "【通用分析指引】\n请针对下方提供的实际数据，提供一段简明的中文文本分析和解读，侧重于关键洞察、趋势或对业务用户有价值的发现。")

    prompt_sections.append(f"【实际查询数据】\n以下是根据用户先前请求查询得到的数据（Markdown格式）:\n{data_string}")

    if data_caveats_instructions:
        prompt_sections.append(f"【数据检查与注意事项】\n{data_caveats_instructions}")
    else:
        prompt_sections.append("【数据检查与注意事项】\n请仔细检查数据，留意潜在问题如地理名称不一致、缺失值或异常。")

    prompt_sections.append(
        "【任务要求与输出格式】\n"
        "1. **文本分析 (`analysis_text`)**: 根据上述指引和数据，提供详细的中文文本分析。\n"
        "2. **最终图表建议**: 根据实际数据和分析，推荐最合适的图表类型，并提供以下参数作为JSON对象的顶层键：\n"  # 强调顶层键
        "   - `chart_type`: (string) 推荐的图表类型（可选值：\"line\", \"bar\", \"pie\", \"scatter\", \"table\"）。\n"
        "   - `x_axis`: (string, 可选) X轴的列名。\n"
        "   - `y_axis`: (string or list of strings, 可选) Y轴的列名。\n"
        "   - `category_column`: (string, 可选) 饼图的分类列名。\n"
        "   - `value_column`: (string, 可选) 饼图的数值列名。\n"
        "   - `title`: (string) 基于数据内容和分析的图表标题。\n"
        "   - `explanation`: (string) 对图表所展示内容的解释，以及关键洞察，可结合数据注意事项。\n"
        "请将所有结果严格封装在一个JSON对象中返回，确保所有上述图表参数键都在JSON的顶层。"
    )
    user_content_for_call2 = "\n\n---\n\n".join(prompt_sections)

    messages_for_api = [
        {"role": "system", "content": system_message_for_call2},
        {"role": "user", "content": user_content_for_call2}
    ]

    try:
        print(f"正在向 LLM ({model_name}) 发送数据以进行分析和最终图表建议 (LLM Call 2)...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages_for_api,
            temperature=0.3,
        )
        raw_response_content = completion.choices[0].message.content.strip()
        print(f"[LLM Call 2] LLM 原始响应: {raw_response_content}")

        cleaned_response_content = raw_response_content
        if cleaned_response_content.startswith("```json"):
            cleaned_response_content = cleaned_response_content[len("```json"):].strip()
        if cleaned_response_content.endswith("```"):
            cleaned_response_content = cleaned_response_content[:-len("```")].strip()

        llm_output = json.loads(cleaned_response_content)

        # 检查并处理可能的嵌套图表建议
        if "chart_suggestion" in llm_output and isinstance(llm_output["chart_suggestion"], dict):
            print("[LLM Call 2] 检测到 'chart_suggestion' 键，正在尝试扁平化结构。")
            chart_details = llm_output.pop("chart_suggestion")
            for key, value in chart_details.items():
                if key not in llm_output:  # 避免覆盖顶层已有的同名键 (比如 analysis_text)
                    llm_output[key] = value
        elif "chart_suggestions" in llm_output and isinstance(llm_output["chart_suggestions"], dict):  # 处理复数形式
            print("[LLM Call 2] 检测到 'chart_suggestions' 键，正在尝试扁平化结构。")
            chart_details = llm_output.pop("chart_suggestions")
            for key, value in chart_details.items():
                if key not in llm_output:
                    llm_output[key] = value

        required_keys = ["analysis_text", "chart_type", "title", "explanation"]
        missing_keys = [key for key in required_keys if key not in llm_output]
        if missing_keys:
            print(
                f"[LLM Call 2] LLM响应JSON中缺少一个或多个关键字段: {missing_keys}。当前顶层键: {list(llm_output.keys())}")
            return None

        if "analysis_text" in llm_output and analysis_prefix:
            llm_output["analysis_text"] = analysis_prefix + llm_output["analysis_text"]

        return llm_output

    except json.JSONDecodeError as e:
        print(f"[LLM Call 2] LLM 返回内容非标准JSON格式，解析错误: {e}")
        print(f"[LLM Call 2] 有问题的原始响应内容 (清理后): {cleaned_response_content}")
        return None
    except Exception as e:
        print(f"调用 LLM API 或处理响应时发生未知错误 (get_final_analysis_and_chart_details - Call 2): {e}")
        import traceback
        traceback.print_exc()
        return None