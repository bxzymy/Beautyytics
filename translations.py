# translations.py

def get_prompts(lang: str = "中文"):
    """
    根据语言返回包含所有指令(Prompts)的字典。
    这部分内容原先在 prompt.py 和 prompt_model.py 文件中。
    """
    if lang == "English":
        return {
            # --- Core Prompts (from prompt.py) ---
            "data_analysis": """
You are a professional data analyst. A dataset obtained from a user query will be provided next (in {data_format} format).
Your task is to provide a text analysis and interpretation of this data. Please focus on key insights, trends, or findings that are valuable to business users.
Do not just repeat the contents of the data table; explain what the data might mean or imply.
Please ensure your analysis and answer is in English.

Here is the data content:
{data_string}

Please provide your analysis:
""",
            "data_caveats": """
Please carefully check the provided data:
- Some province names in the raw data are incorrect (e.g., city names); if you encounter such errors, merge the data into the correct province.
- Pay attention to potential missing values, outliers, or unusual data distributions.
""",
            "db_schema": """
You are using a database table named "df_data".
Please ensure all generated SQL queries are compatible with DuckDB.
In SQL queries, all column names should be enclosed in double quotes (e.g., "column_name").

The structure of the "df_data" table is as follows:
- "order_no" (TEXT): Order number (UUID format, uniquely identifies an order)
- "order_time" (TIMESTAMP): Order time (accurate to the second, format YYYY-MM-DD HH:MM:SS)
- "order_date" (DATE): Order date (format YYYY-MM-DD)
- "brand_code" (TEXT): Brand code
- "program_code" (TEXT): Program code
- "order_type" (TEXT): Order type (e.g., '1' for a regular order, '0' for a return)
- "sales" (DECIMAL): Sales amount (numeric type, two decimal places)
- "item_qty" (INTEGER): Item quantity (integer)
- "item_price" (DECIMAL): Unit price (numeric type)
- "channel" (TEXT): Channel code
- "subchannel" (TEXT): Sub-channel code
- "sub_subchannel" (TEXT): Tertiary sub-channel code
- "material_code" (TEXT): Product SKU code
- "material_name_cn" (TEXT): Product name in Chinese
- "material_type" (TEXT): Product type code
- "merged_c_code" (TEXT): Unified customer code
- "tier_code" (TEXT): Member tier (null means non-member or tier not assigned)
- "first_order_date" (DATE): Customer's first order date (null means new customer or data not captured)
- "is_mtd_active_member_flag" (TEXT): Month-to-date active member flag ('0' for inactive, '1' for active)
- "ytd_active_arr" (TEXT): Year-to-date active array (string representation of an array, e.g., "[0,0,1,...]")
- "r12_active_arr" (TEXT): Rolling 12-month active array (string representation)
- "manager_counter_code" (TEXT): Managing counter code
- "ba_code" (TEXT): BA (Beauty Advisor) code
- "province_name" (TEXT): Province name (e.g., "Anhui Province", "Xinjiang Uyghur Autonomous Region", "Beijing City"). Note: This column may contain entries that do not perfectly match standard administrative divisions.
- "line_city_name" (TEXT): City name (e.g., "Hefei City", "Aba Tibetan and Qiang Autonomous Prefecture"). Note: This column may have inconsistencies in administrative levels.
- "line_city_level" (TEXT): City tier
- "store_no" (TEXT): Store/Counter number
- "terminal_name" (TEXT): Terminal name (e.g., Tmall store name)
- "terminal_code" (TEXT): Terminal code
- "terminal_region" (TEXT): Terminal region
- "default_flag" (TEXT): Special order flag ('0' for normal, '1' for potentially abnormal)

Guidelines:
- Convert the following natural language question into a SQL query for the "df_data" table.
- For relative dates like "last month" or "this week", try to generate a date range based on a hypothetical current date (e.g., `NOW()` or `CURRENT_DATE` in SQL functions if supported by DuckDB).
- Pay close attention to column names and their data types.
""",
            "multi_turn_system": """
You are a SQL generation assistant. Based on the user's current natural language question and the previous conversation history, generate a DuckDB-compatible SQL query for the "df_data" table.
Carefully analyze the conversation history to understand the context.

【IMPORTANT INSTRUCTIONS】Besides generating SQL, please recommend a suitable chart type based on the user's question and the expected data result, and specify the key columns for plotting.
Please return the result in JSON format with the following keys:
- "sql_query": (string) The generated SQL query. Can be null or an empty string, especially when providing "recommended_analyses".
- "chart_type": (string) Recommended chart type, options: "line", "bar", "pie", "scatter", "table".
- "x_axis": (string, optional) Recommended column for the X-axis.
- "y_axis": (string or list of strings, optional) Recommended column(s) for the Y-axis.
- "category_column": (string, optional) Recommended column for categories in a pie chart.
- "value_column": (string, optional) Recommended column for values in a pie chart.
- "title": (string, optional) A recommended title for the chart.
- "explanation": (string) Explain why this chart type and its parameters are recommended. If providing recommended analyses due to a vague query, explain that the query was too general.
- "recommended_analyses": (list of objects, optional) If the user query is broad or unclear, provide 2-3 potential analysis directions. Each object should contain:
    - "title": (string) A short, descriptive title for the recommended analysis.
    - "description": (string) A brief explanation of the analysis.
    - "example_query": (string) An example natural language query the user can use.

【SQL GENERATION RULES】
- **Only output the SQL query itself in the "sql_query" field**.
- If the user asks to modify the previous SQL, generate a new SQL based on the previous one and the user's instructions.
- Ensure all generated SQL queries are DuckDB compatible.
- All column names in the SQL query should be enclosed in double quotes (e.g., "column_name").
- The table name is always "df_data".

【HANDLING VAGUE QUERIES】
If the user's query is too vague to generate a specific, meaningful SQL query (e.g., "tell me about my data"), you should prioritize providing "recommended_analyses". In this case, "sql_query" can be null or empty, "chart_type" should be "table", and the "explanation" should state that the query was too general and thus suggestions are provided.
""",

            "llm_response_system_prompt_call2": """
        You are a professional data analyst and visualization expert.
        Your task is to conduct an in-depth text analysis and provide specific, final charting recommendations based on the user's original question, the analysis framework (if provided), the actual queried data, and data caveats.
        Your entire response must strictly adhere to the JSON format. All chart-related keys (e.g., 'chart_type', 'x_axis', 'title', 'explanation', etc.) must be top-level keys in the returned JSON object, do not nest them within any sub-objects (like 'chart_suggestion').
        """,

            # --- Beauty Analytics Prompts (from prompt_model.py) ---
            "descriptive_analysis": """
As a senior beauty industry analyst, please conduct a full-scale sales overview based on the following dimensions:
1. **Product Dimension**: Statistics by categories like Skincare, Makeup, Fragrance.
   - Absolute sales value and market share.
   - Month-over-month growth rate.
   - Analysis of top 3 products with the highest return rates.
2. **Channel Dimension**: Performance on platforms like Tmall, Douyin, Offline Counters.
   - GMV proportion and average transaction value comparison.
   - Channel growth efficiency index (traffic cost vs. conversion rate).
3. **User Dimension**:
   - Contribution ratio of new vs. existing customers.
   - Geographical distribution heat map (tier-1 vs. lower-tier cities).
4. **Visualization Output**:
   - Combined trend chart: Sales/Gross Profit on dual Y-axes.
   - Table: Top 10 bestseller list (including SKU, unit price, repurchase rate).
   - Key Conclusions: Summarize key findings in 3 sentences (including alerts for anomalies).
Note: If data is missing, please clearly mark it as [Data Supplement Needed] and explain the impact.
""",
            "diagnostic_analysis": """
Diagnose the problem: "Sales down 20% year-over-year" for the "Essence Category" compared to the "same period last year":
1. **Multi-dimensional Attribution Analysis**:
   a) Price band penetration test: Check market share changes in the main price range ($30-$80).
   b) Competitive analysis matrix: Compare promotional efforts/new product launch pace with 3 direct competitors.
   c) Channel health scan: Focus on GPM fluctuations in Douyin live-streaming rooms.
2. **Deep Dive into User Behavior**:
   - Churned customer profile: Distribution by consumption level/age/city tier.
   - Customer complaint word cloud analysis: Extract top 5 quality issue keywords using NLP.
3. **Supply Chain Trace-back**:
   - Inventory turnover rate anomaly detection.
   - Supply stability assessment of core ingredients (e.g., Pro-Xylane).
4. **Output Requirements**:
   - Attribute conclusions in three levels: Primary cause (weight >= 50%), Secondary cause (30%), Incidental factors (20%).
   - Include a verification plan: Suggest 2 A/B tests to validate core hypotheses.
""",
            "predictive_analysis": """
Based on historical data, forecast the sales trend for the "Anti-Aging Skincare Series" for "Q3 2024":
1. **Modeling Framework**:
   - Base Model: Time series decomposition (seasonal + trend + residual components).
   - Enhancement Factors: Regression coefficients for key drivers like "number of holidays", "social media ad budget", "competitor new launch pace".
2. **Beauty Industry-Specific Parameters**:
   - Big promotion leverage (magnifying effect of 618/Double 11 on GMV).
   - KOL marketing decay curve (lifecycle of viral content).
   - Weather sensitivity parameter (impact of UV index on sunscreen category).
3. **Output Deliverables**:
   a) Three forecast scenarios: Optimistic/Neutral/Pessimistic values.
   b) Sensitivity analysis table showing the impact of variables on GMV and profit.
   c) Inflection point warning: Identify months likely to breach inventory safety stock levels.
""",
            "swot_analysis": """
Construct a dynamic SWOT matrix for a "Mid-range Domestic Skincare" brand:
**Strengths (S)**:
- Technical barrier: Patent coverage of "plant extraction technology" (requires specific data).
- Supply chain: Flexible manufacturing capability (Minimum Order Quantity/MOQ data).
**Weaknesses (W)**:
- Channel shortcomings: Pass rate of offline BA training (with regional comparison).
- Repurchase deficit: Member semi-annual retention rate vs. industry benchmark.
**Opportunities (O)**:
- Policy bonus: Progress on Hainan duty-free channel access.
- Ingredient trend: Growth rate of demand for Clean Beauty.
**Threats (T)**:
- International brands: Price reduction monitoring of brands like Estée Lauder.
- Regulatory risk: Decreasing approval rate for new raw materials.
**Output Requirements**:
- Provide 2 quantitative pieces of evidence for each dimension (e.g., "Tmall flagship store search share dropped from 12% in Q1 to 9% in Q2").
- Generate a strategic quadrant chart: Prioritize SO strategies (Strengths + Opportunities) for implementation.
""",
            "funnel_analysis": """
Analyze the user conversion funnel for the "Summer Sunscreen Campaign":
1. **Funnel Modeling**:
   - Step definition: Ad Exposure → Product Detail Page Visit → Add to Cart → Successful Payment.
   - Conversion benchmark: Industry average vs. this product's historical best.
2. **Bottleneck Diagnosis**:
   - In-depth attribution for steps with a drop-off rate > 40%.
   - Page heatmap analysis (mouse tracking/dwell time).
3. **Scenario-based Optimization**:
   - Golden 3-second rule: Optimization plan for above-the-fold content density.
   - Trust building: Add placement for testing reports.
   - Churn recovery: Outreach strategy for users who abandoned their carts.
4. **Benefit Forecasting**:
   "If the conversion rate of [Product Detail Page Visit] is increased by 5pp, the expected GMV increase is __ thousand dollars."
   "Optimizing page load speed to 1.5s can reduce bounce rate by __%."
""",
            "logic_tree": """
Deconstruct the strategic proposition "How to improve the profit margin of the high-end line" using the MECE principle:
**Layer 1: Core Dimensions**
- Increase Revenue (New customer acquisition + Existing customer value enhancement)
- Reduce Cost (Supply chain optimization + Operational efficiency improvement)
**Layer 2: Beauty Industry Specifics**
  ├─ New Customer Acquisition → High-net-worth circle penetration strategy (e.g., partnership with luxury SPAs)
  ├─ Existing Customer Value → Customized services (AI skin assessment + personalized formula)
  ├─ Supply Chain → Packaging cost breakdown (e.g., glass bottle accounts for __% of cost)
  └─ Operations → BA efficiency improvement (e.g., smart script assistance)
**Layer 3: Actionable Items**
  - Cross-brand collaboration: Co-branding with luxury brands for premium pricing.
  - Cost control: Price comparison table for alternative packaging suppliers.
**Output Requirements**:
- Ensure all layers are mutually exclusive and collectively exhaustive (MECE).
- Mark the implementation priority (H/M/L) for terminal nodes.
- Quantify expected benefits (e.g., contribution of each measure to profit margin in percentage points).
"""
        }

    # Default to Chinese
    return {
        # --- Core Prompts (from prompt.py) ---
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
- "order_time" (TIMESTAMP): 订单时间 (精确到秒, 格式 YYYY-MM-DD HH:MM:SS)
- "order_date" (DATE): 订单日期 (格式 YYYY-MM-DD)
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
- 对于像“上个月”、“本周”这样的相对日期表述，请尝试根据一个假设的当前日期（例如 SQL 函数中的 `NOW()` 或 `CURRENT_DATE`，如果 DuckDB 支持且适用）来生成日期范围。
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

        # --- Beauty Analytics Prompts (from prompt_model.py) ---
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
"""
    }


def get_ui_texts(lang: str = "中文"):
    """
    根据语言返回包含所有UI文本的字典。
    """
    if lang == "English":
        return {
            "page_title": "Beautyytics",
            "sidebar_header": "Analysis Options",
            "sidebar_framework_select_label": "Analysis Framework Selection",
            "sidebar_framework_select_box": "Select Analysis Framework:",
            "clear_history_button": "Clear Chat History",
            "language_selector_label": "语言 / Language",
            "main_title": "📊 Beautyytics",
            "main_subtitle": "Your Data Insight Partner (with optional analysis frameworks)",
            "welcome_message": "👋 Welcome to Beautyytics, I can help you with data analysis!",
            "welcome_instruction": "**Please select an analysis framework from the sidebar on the left (defaults to General Analysis), then ask a question in natural language.**",
            "try_asking_header": "💡 Try asking me:",
            "example_sales": "**Sales Analysis**\n\"Compare sales across different products\"",
            "example_trend": "**Trend Analysis**\n\"Show the sales trend for October 2024\"",
            "example_geo": "**Geographical Analysis**\n\"Compare order counts for Jiangsu, Zhejiang, and Shanghai in 2024\"",
            "features_header": "### Features",
            "features_list": "- 🚀 Intelligent Natural Language Queries\n- 📈 Multi-dimensional Data Visualization\n- 💬 Interactive Conversational Analysis\n- 🧩 Multi-framework Support",
            "history_title": "📊",
            "chat_input_placeholder": "Please enter your question...",
            "error_loading_data": "Error: CSV data file 'random_order_data.csv' not found. Please ensure the file path is correct.",
            "error_loading_data_unknown": "An unknown error occurred while loading data: {e}",
            "error_no_sql": "SQL query is empty or invalid.",
            "error_no_data_for_sql": "Data could not be loaded, cannot execute SQL query.",
            "error_sql_execution": "SQL query execution error: {e}\nAttempted SQL: {sql_query}",
            "chart_warning_missing_cols": "{chart_type} chart columns missing. X:{x_col}, Y:{y_col}. Displaying table.",
            "chart_warning_missing_cols_pie": "Pie chart columns missing. Names:{cat_col}, Values:{val_col}. Displaying table.",
            "chart_warning_missing_cols_scatter": "Scatter plot columns missing. X:{x_col}, Y:{y_col}. Displaying table.",
            "chart_info_unknown_type": "Unknown chart type: '{chart_type}'. Displaying table.",
            "chart_error_generating": "Error generating chart '{title}' ({chart_type}): {e}",
            "llm_error_sql_generation": "Sorry, the AI failed to generate the SQL. Please try again later or rephrase your question.",
            "spinner_thinking": "AI is thinking...",
            "spinner_thinking_framework": "AI is thinking based on the ({framework_name}) framework...",
            "ai_guidance": "AI Guidance: {explanation}",
            "ai_data_insights_header": "##### 🤖 AI Data Insights",
            "spinner_analyzing": "AI is analyzing the data...",
            "spinner_analyzing_framework": "AI is analyzing data based on the ({framework_name}) framework...",
            "query_results_chart_header": "📋 **Query Results & Chart:**",
            "query_results_chart_header_prelim": "📋 **Query Results & Chart (from preliminary suggestion):**",
            "query_results_chart_header_history": "📋 **Query Results & Chart (History):**",
            "warning_no_analysis_text": "Could not retrieve data analysis text from the AI this time.",
            "warning_analysis_failed_fallback": "AI failed to complete data analysis. Will attempt to use the initial chart suggestion if available.",
            "info_query_success_no_data": "The query executed successfully but returned no data.",
            "info_query_success_no_data_history": "The query executed successfully but returned no data (History).",
            "warning_no_result_no_error": "The query did not return a valid result, and there was no specific error message.",
            "info_no_sql_no_rec_no_exp": "The AI did not generate an SQL query or provide specific guidance.",
            "info_no_op": "The AI returned a response, but with no specific action or recommendation.",
            "recommendations_header": "💡 Perhaps you are interested in the following analysis directions?",
            "recommendations_history_header": "💡 **Historical Analysis Suggestions:**",
            "try_query_button": "Try query: \"{query}\"",
            "ai_insights_history_header": "##### 🤖 AI Data Insights (History):",
            "based_on_framework_caption": "(Based on framework: {framework_name})",
            "api_key_warning": "API Key not configured! LLM functionality may be limited or unavailable.",
            "data_load_fail_app_stop": "Data failed to load. The application cannot continue. Please check the CSV file and loading logic.",
            "framework_general": "General Analysis (Default)",
            "framework_descriptive": "Descriptive Analysis (Sales Overview)",
            "framework_diagnostic": "Diagnostic Analysis (Root Cause)",
            "framework_predictive": "Predictive Analysis (Future Performance)",
            "framework_swot": "SWOT Analysis (Competitive Assessment)",
            "framework_funnel": "Funnel Analysis (Conversion Path)",
            "framework_logic_tree": "Logic Tree Analysis (Problem Decomposition)",
        }

    # Default to Chinese
    return {
        "page_title": "妆策灵思",
        "sidebar_header": "分析选项",
        "sidebar_framework_select_label": "分析框架选择",
        "sidebar_framework_select_box": "选择分析框架:",
        "clear_history_button": "清除对话历史",
        "language_selector_label": "语言 / Language",
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
        "framework_general": "通用分析 (默认)",
        "framework_descriptive": "描述性分析 (销售全景)",
        "framework_diagnostic": "诊断性分析 (问题根因)",
        "framework_predictive": "预测性分析 (未来业绩)",
        "framework_swot": "SWOT分析 (竞争力评估)",
        "framework_funnel": "漏斗分析 (转化路径)",
        "framework_logic_tree": "逻辑树分析 (复杂问题拆解)",
    }