def get_prompts_zh() -> dict:
    """返回所有中文版的指令(Prompts)"""
    return {
        # --- 核心系统指令 ---
        "data_analysis": """
你是一位数据分析专家。接下来会提供一个通过用户查询得到的数据集（格式为 {data_format}）。
你的任务是针对这份数据，提供一段文本分析和解读。请侧重于关键洞察、趋势或对业务用户有价值的发现。
请不要仅仅复述数据表格的内容，而是要解释数据背后可能意味着什么或暗示着什么。
请确保你的分析结果使用中文。

这是数据内容:
{data_string}

请提供你的分析:
""",
        "data_caveats": """
请仔细检查以下提供的数据：
- 原始数据中部分省份名称错误，为城市名，如果遇到这种错误，将数据合并到正确的省份中。
- 留意数据中可能存在的缺失值、异常值或不寻常的数据分布。
""",
        "db_schema": """
您正在使用一个名为 "df_data" 的数据库表。
请确保所有生成的SQL查询都与DuckDB兼容。
在SQL查询中，所有列名都应使用双引号括起来 (例如: "column_name")。

"df_data" 表的结构如下:
- "order_no" (TEXT): 订单编号 (UUID格式，唯一标识订单)
- "order_time" (TIMESTAMP): 订单时间 (精确到秒, 格式<y_bin_46>-MM-DD HH:MM:SS)
- "order_date" (DATE): 订单日期 (格式<y_bin_46>-MM-DD)
- "brand_code" (TEXT): 品牌代码
- "program_code" (TEXT): 项目代码
- "order_type" (TEXT): 订单类型 (例如 '1' 代表正单, '0' 代表退单)
- "sales" (DECIMAL): 销售额 (数值类型，保留两位小数)
- "item_qty" (INTEGER): 商品数量 (整数)
- "item_price" (DECIMAL): 单价 (数值类型)
- "channel" (TEXT): 渠道代码
- "subchannel" (TEXT): 子渠道代码
- "sub_subchannel" (TEXT): 三级子渠道代码
- "material_code" (TEXT): 产品SKU代码
- "material_name_cn" (TEXT): 产品中文名称
- "material_type" (TEXT): 产品类型代码
- "merged_c_code" (TEXT): 统一客户编号
- "tier_code" (TEXT): 会员等级 (空值表示非会员或未绑定等级)
- "first_order_date" (DATE): 客户首单日期 (空值表示新客户或数据未捕获)
- "is_mtd_active_member_flag" (TEXT): 本月活跃标记 ('0' 为非活跃, '1' 为活跃)
- "ytd_active_arr" (TEXT): 年度活跃标记 (数组的字符串表示, 例如 "[0,0,1,...]")
- "r12_active_arr" (TEXT): 近12月活跃标记 (数组的字符串表示)
- "manager_counter_code" (TEXT): 管理门店代码
- "ba_code" (TEXT): BA（导购员）编号
- "province_name" (TEXT): 省份名称 (例如 "安徽省", "新疆维吾尔自治区", "北京市")。请注意：此列数据可能包含与标准行政区划不完全一致的条目。
- "line_city_name" (TEXT): 城市名称 (例如 "合肥市", "阿坝藏族羌族自治州")。请注意：此列数据可能包含与标准行政区划层级不一致的情况。
- "line_city_level" (TEXT): 城市等级
- "store_no" (TEXT): 门店/柜台编号
- "terminal_name" (TEXT): 终端名称 (例如 天猫店铺名称)
- "terminal_code" (TEXT): 终端代码
- "terminal_region" (TEXT): 终端区域
- "default_flag" (TEXT): 特殊订单标记 ('0' 表示正常订单, '1' 可能为异常订单)

指导原则:
- 请将接下来的自然语言问题转换为一个针对上述 "df_data" 表的SQL查询。
- 对于像“上个月”、“本周”这样的相对日期表述，请尝试根据一个假设的当前日期（例如 SQL 函数中的 NOW() 或 CURRENT_DATE，如果 DuckDB 支持且适用）来生成日期范围。
- 请密切关注列名和它们的数据类型。
""",
        "multi_turn_system": """
你是一个 SQL 生成助手。基于用户当前的自然语言问题以及之前的对话历史，生成一个针对 "df_data" 表的 DuckDB 兼容的 SQL 查询。
仔细分析对话历史以理解上下文。

【重要指令】除了生成SQL，请根据用户的问题和预期的数据结果，推荐一个合适的图表类型，并指定用于绘图的关键列。
请以JSON格式返回结果，包含以下键：
- "sql_query": (string) 生成的SQL查询语句。可以为 null 或空字符串，特别是当提供 "recommended_analyses" 时。
- "chart_type": (string) 推荐的图表类型，可选值："line", "bar", "pie", "scatter", "table"。
- "x_axis": (string, 可选) 如果是折线图、柱状图、散点图，推荐作为X轴的列名。
- "y_axis": (string or list of strings, 可选) 如果是折线图、柱状图、散点图，推荐作为Y轴的列名。
- "category_column": (string, 可选) 如果是饼图，推荐作为分类的列名。
- "value_column": (string, 可选) 如果是饼图，推荐作为数值的列名。
- "title": (string, 可选) 推荐的图表标题。
- "explanation": (string) 解释为何推荐此图表类型和参数。如果因查询模糊而提供推荐分析，则解释查询笼统且提供了建议。
- "recommended_analyses": (list of objects, 可选) 如果用户查询宽泛或不明确，提供2-3个潜在分析方向。每个对象应包含:
    - "title": (string) 推荐分析的简短描述性标题。
    - "description": (string) 对此分析内容或可能洞见的简要说明。
    - "example_query": (string) 用户可用于发起此特定分析的示例自然语言查询。

【SQL生成规则】
- **请只在 "sql_query" 字段中输出SQL查询本身**。
- 如果用户要求修改之前的SQL，请基于之前的SQL和用户的指令生成新的SQL。
- 确保所有生成的SQL查询都与DuckDB兼容。
- 在SQL查询中，所有列名都应使用双引号括起来 (例如: "column_name")。
- 表名始终是 "df_data"。

【处理模糊查询】
如果用户的查询过于模糊，无法生成具体有意义的SQL查询 (例如："告诉我关于我的数据")，你应该优先提供 "recommended_analyses"。在这种情况下，"sql_query" 可以为 null 或空字符串，"chart_type" 应为 "table"，并且 "explanation" 字段应明确说明用户查询过于笼统，因此提供了这些建议。
""",
        "llm_response_system_prompt_call2": """
你是一位专业的数据分析师和可视化专家。
你的任务是基于用户提供的原始问题、分析框架（如果提供）、实际查询到的数据以及数据检查注意事项，进行深入的文本分析，并提供具体、最终的图表化建议。
你的整个回复必须严格遵循JSON格式，所有图表相关的键（如 'chart_type', 'x_axis', 'title', 'explanation' 等）必须直接作为返回JSON对象的顶层键，不要将它们嵌套在任何子对象（如 'chart_suggestion'）中。
""",

        # --- 美妆分析框架指令 ---
        "descriptive_analysis": """
作为资深美妆行业分析师，请基于以下维度进行销售全景扫描：
1. **产品维度**：按护肤, 彩妆, 香水类目统计
   - 销售额绝对值与市场份额
   - 环比增长率（对比上个周期）
   - 退货率TOP3单品分析
2. **渠道维度**：天猫, 抖音, 线下专柜平台表现
   - 各渠道GMV占比与客单价对比
   - 渠道增长效率指数（流量成本 vs 转化率）
3. **用户维度**：
   - 新老客贡献占比（二八法则验证）
   - 地域分布热力图（一线vs下沉市场）
4. **可视化输出**：
   - 组合趋势图：销售额/毛利双Y轴曲线
   - 表格：Top10爆品清单（含SKU、单价、复购率）
   - 核心结论：用3句话概括关键发现（含异常点预警）
注意：若数据存在缺失项，请明确标注【需补充数据】并说明影响
""",
        "diagnostic_analysis": """
诊断美妆品牌【精华类目】在【2023年同期】出现的【销售额同比下滑20%】问题：
1. **多维归因分析**：
   a) 价格带穿透测试：检查主力价格段（200-500元）市占率变化
   b) 竞品对比矩阵：选取3个直接竞品对比促销力度/新品节奏
   c) 渠道健康度扫描：重点检测抖音自播间GPM波动
2. **用户行为深挖**：
   - 流失客群画像：消费层级/年龄/城市等级分布
   - 客诉词云分析：NLP提取TOP5质量问题关键词
3. **供应链追溯**：
   - 库存周转率异常检测
   - 核心成分（如玻色因）供货稳定性评估
4. **输出要求**：
   - 归因结论分三级：主因（权重≥50%）、次因（30%）、偶然因素（20%）
   - 附带验证方案：建议2个AB测试验证核心假设
""",
        "predictive_analysis": """
基于历史数据预测【抗衰护肤系列】在【2024年Q3】的销售趋势：
1. **建模框架**：
   - 基础模型：时间序列分解（季节项+趋势项+残差项）
   - 增强因子：节庆日数量, 社媒投放预算, 竞品上新节奏的回归系数
2. **美妆行业特参**：
   - 大促杠杆率（618/双11对GMV的放大效应）
   - KOL投放衰减曲线（爆款内容生命周期）
   - 天气敏感性参数（UV指数对防晒品类影响）
3. **输出交付物**：
   a) 预测三区间：乐观/中性/悲观场景数值
   b) 敏感性分析表：展示变量变动对GMV和利润的影响
   c) 拐点预警：识别可能突破库存警戒线的月份
""",
        "swot_analysis": """
为【国产中端护肤】美妆品牌构建动态SWOT矩阵：
**优势(S)**：
- 技术壁垒：植物萃取技术专利覆盖率（需具体数据）
- 供应链：柔性生产能力（最小起订量/MOQ数据）
**劣势(W)**：
- 渠道短板：线下BA培训通过率（附区域对比）
- 复购缺陷：会员半年留存率 vs 行业标杆
**机会(O)**：
- 政策红利：海南免税渠道准入进度
- 成分趋势：纯净美妆(Clean Beauty)需求增长率
**威胁(T)**：
- 国际品牌：雅诗兰黛等降价幅度监测
- 法规风险：新原料备案通过率下降
**输出要求**：
- 每个维度提供2个量化证据（如："天猫旗舰店搜索份额从Q1的12%→Q2的9%"）
- 生成战略四象限图：SO战略（优势+机会）优先落地
""",
        "funnel_analysis": """
分析【夏日防晒企划】活动的用户转化漏斗：
1. **漏斗建模**：
   - 步骤定义：广告曝光 → 详情页访问 → 加购 → 支付成功
   - 转化基准：行业均值 vs 本品历史最佳值
2. **卡点诊断**：
   - 流失率>40%的环节深度归因
   - 页面热力图分析（鼠标轨迹/停留时长）
3. **场景化优化**：
   - 黄金3秒原则：首屏信息密度优化方案
   - 信任体系建设：增加检测报告露出位
   - 流失挽回：购物车放弃用户的触达策略
4. **预测收益**：
   "若将【详情页访问】转化率提升5pp，GMV预期增加__万元"
   "详情页加载速度优化至1.5s可减少__%跳出"
""",
        "logic_tree": """
用MECE原则拆解战略命题：【如何提升高端线利润率】
**第一层：核心维度**
- 开源（新客获取+老客增值）
- 节流（供应链优化+运营提效）
**第二层：美妆行业特性**
  ├─ 新客获取 → 贵妇圈层渗透策略（高端SPA合作）
  ├─ 老客增值 → 定制化服务（AI肤质测评+配方定制）
  ├─ 供应链 → 包材成本拆解（玻璃瓶占成本__%）
  └─ 运营 → BA人效提升（智能话术辅助）
**第三层：可执行项**
  - 跨界合作：与奢侈品牌联名溢价方案
  - 成本管控：替代包材供应商比价表
**输出要求**：
- 确保各层完全穷尽互斥（MECE）
- 末端节点标注实施优先级（H/M/L）
- 量化预期收益（如：每项措施对利润率贡献百分点）
""",

        # --- 第一次LLM调用的框架指令 ---
        "llm_call1_framework_instruction": "用户希望在一个更广泛的分析框架下进行探索。这是他们选择的框架，请将其作为理解用户意图的背景参考：\n<analysis_framework_context>\n{active_analysis_framework_prompt}\n</analysis_framework_context>\n请注意：这个框架描述了用户可能希望达成的整体分析目标。\n然而，在当前这一步，你的核心任务是：\n1. 严格专注于用户接下来提出的【具体问题】。\n2. 根据这个【具体问题】，生成一个相关的、可执行的SQL查询，以获取支撑上述分析框架的数据。\n3. 严格遵循系统先前定义的指示，以JSON格式返回结果（主要期望 'sql_query'，同时可包含初步的 'chart_type', 'title', 'explanation', 'recommended_analyses' 等关键字段）。\n你的整个回复必须且只能是一个JSON对象字符串，不应包含任何JSON对象之外的文字、解释或标记。\n请不要试图在这一步完成分析框架中的所有内容或输出框架本身要求的复杂报告，此阶段重点是为后续分析步骤准备数据查询。",

        # --- 第二次LLM调用的指令片段 ---
        "llm_call2_user_query_prefix": "用户的原始查询或分析主题是：'{user_query_for_analysis}'",
        "llm_call2_framework_header": "【分析框架参考】\n用户先前选择了以下分析框架，请在解读数据和构建图表时参考此框架的目标和要求：",
        "llm_call2_framework_guidance": "请严格按照上述分析框架的要求，结合下面的实际数据进行分析并撰写报告部分。",
        "llm_call2_general_guidance_header": "【通用分析指引】",
        "llm_call2_general_guidance_body": "请针对下方提供的实际数据，提供你的中文分析结果。",
        "llm_call2_data_header": "【实际查询数据】\n以下是根据用户先前请求查询得到的数据（Markdown格式）:",
        "llm_call2_caveats_header": "【数据检查与注意事项】",
        "llm_call2_caveats_body": "请仔细检查数据，留意潜在问题如地理名称不一致、缺失值或异常。",
        "llm_call2_task_header": "【任务要求与输出格式】",
        "llm_call2_task_body": """
1. **文本分析 (`analysis_text`)**: 根据上述指引和数据，提供详细的中文文本分析。
2. **最终图表建议**: 根据实际数据和分析，推荐最合适的图表类型，并提供以下参数作为JSON对象的顶层键：
   - `chart_type`: (string) 推荐的图表类型（可选值：\"line\", \"bar\", \"pie\", \"scatter\", \"table\"）。
   - `x_axis`: (string, 可选) X轴的列名。
   - `y_axis`: (string or list of strings, 可选) Y轴的列名。
   - `category_column`: (string, 可选) 饼图的分类列名。
   - `value_column`: (string, 可选) 饼图的数值列名。
   - `title`: (string) 基于数据内容和分析的图表标题。
   - `explanation`: (string) 对图表所展示内容的解释，以及关键洞察，可结合数据注意事项。
请将所有结果严格封装在一个JSON对象中返回，确保所有上述图表参数键都在JSON的顶层。
""",
    }

def get_ui_texts_zh() -> dict:
    """返回所有中文版的UI界面文本"""
    return {
        # --- 页面与侧边栏 ---
        "page_title": "妆策灵思",
        "sidebar_header": "分析选项",
        "sidebar_framework_select_label": "分析框架选择",
        "sidebar_framework_select_box": "选择分析框架:",
        "clear_history_button": "清除对话历史",
        "language_selector_label": "语言 / Language",

        # --- 主页面欢迎信息 ---
        "main_title": "📊 数析灵思",
        "main_subtitle": "您的数据洞察伙伴 (可选择特定分析框架)",
        "welcome_message": "👋 欢迎使用 数析灵思 ，我可以帮助你进行数据分析！",
        "welcome_instruction": "**请先在左侧侧边栏选择一个分析框架（默认为通用分析），然后用自然语言提问。**",
        "try_asking_header": "💡 试试这样问我：",
        "example_sales": "**销售额分析**\n\"不同产品销售额对比\"",
        "example_trend": "**时间趋势分析**\n\"2024年10月的销售趋势图\"",
        "example_geo": "**地域分析**\n\"2024年江苏省、浙江省、上海市的订单数量对比\"",
        "features_header": "### 功能特点",
        "features_list": "- 🚀 智能自然语言查询\n- 📈 多维度数据可视化\n- 💬 交互式对话分析\n- 🧩 多分析框架支持",
        "history_title": "📊",
        "chat_input_placeholder": "请输入您的问题...",

        # --- 流程中的消息与错误提示 ---
        "error_loading_data": "错误: CSV数据文件 'random_order_data.csv' 未找到。请确保文件路径正确。",
        "error_loading_data_unknown": "加载数据时发生未知错误: {e}",
        "error_no_sql": "SQL 查询为空或无效。",
        "error_no_data_for_sql": "数据未能加载，无法执行SQL查询。",
        "error_sql_execution": "SQL 查询执行错误: {e}\n尝试执行的 SQL: {sql_query}",
        "chart_warning_missing_cols": "{chart_type}图列缺失. X:{x_col}, Y:{y_col}. 显示表格.",
        "chart_warning_missing_cols_pie": "饼图列缺失. Names:{cat_col}, Values:{val_col}. 显示表格.",
        "chart_warning_missing_cols_scatter": "散点图列缺失. X:{x_col}, Y:{y_col}. 显示表格.",
        "chart_info_unknown_type": "未知图表类型: '{chart_type}'. 显示表格.",
        "chart_error_generating": "生成图表 '{title}' ({chart_type}) 出错: {e}",
        "llm_error_sql_generation": "抱歉，AI未能完成SQL生成。请稍后再试或调整您的问题。",
        "spinner_thinking": "AI 思考中...",
        "spinner_thinking_framework": "AI 根据 ({framework_name}) 框架思考中...",
        "ai_guidance": "AI 指导: {explanation}",
        "ai_data_insights_header": "##### 🤖 AI 数据洞察",
        "spinner_analyzing": "AI 正在分析数据...",
        "spinner_analyzing_framework": "AI 正基于 ({framework_name}) 框架分析数据...",
        "query_results_chart_header": "📋 **查询结果与图表:**",
        "query_results_chart_header_prelim": "📋 **查询结果与图表 (基于初步建议):**",
        "query_results_chart_header_history": "📋 **查询结果与图表 (历史):**",
        "warning_no_analysis_text": "本次未能从AI获取数据分析文本。",
        "warning_analysis_failed_fallback": "AI未能完成数据分析。将尝试使用初步的图表建议（如果可用）。",
        "info_query_success_no_data": "查询已成功执行，但没有返回任何数据。",
        "info_query_success_no_data_history": "查询成功执行，但没有返回数据 (历史)。",
        "warning_no_result_no_error": "查询未返回有效结果，也无明确错误信息。",
        "info_no_sql_no_rec_no_exp": "AI 未能生成 SQL 查询或提供明确指导。",
        "info_no_op": "AI 返回了响应，但没有具体的操作或建议。",
        "recommendations_header": "💡 或许您对以下分析方向感兴趣？",
        "recommendations_history_header": "💡 **历史分析建议:**",
        "try_query_button": "尝试查询: \"{query}\"",
        "ai_insights_history_header": "##### 🤖 AI 数据洞察 (历史):",
        "based_on_framework_caption": "（基于框架：{framework_name}）",
        "api_key_warning": "API Key 未配置! LLM 功能可能受限或无法使用。",
        "data_load_fail_app_stop": "数据未能成功加载，应用无法继续。请检查 CSV 文件和加载逻辑。",

        # --- 分析框架名称 (用于UI显示) ---
        "framework_general": "通用分析 (默认)",
        "framework_descriptive": "描述性分析 (销售全景)",
        "framework_diagnostic": "诊断性分析 (问题根因)",
        "framework_predictive": "预测性分析 (未来业绩)",
        "framework_swot": "SWOT分析 (竞争力评估)",
        "framework_funnel": "漏斗分析 (转化路径)",
        "framework_logic_tree": "逻辑树分析 (复杂问题拆解)",
    }

