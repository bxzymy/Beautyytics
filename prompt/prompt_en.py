def get_prompts_en() -> dict:
    """Returns all English prompts."""
    return {
        # --- Core System Prompts ---
        "data_analysis": """
You are a professional data analyst. A dataset obtained from a user query will be provided next (in {data_format} format).
Your task is to provide a text analysis and interpretation of this data. Please focus on key insights, trends, or findings that are valuable to business users.
Do not just repeat the contents of the data table; explain what the data might mean or imply.
Please ensure your analysis is in English.

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
- For relative dates like "last month" or "this week", try to generate a date range based on a hypothetical current date (e.g., NOW() or CURRENT_DATE in SQL functions if supported by DuckDB).
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

        # --- Beauty Analytics Framework Prompts ---
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
""",

        # --- Prompt Fragments for LLM Call 2 ---
        "llm_call2_user_query_prefix": "The user's original query or analysis topic is: '{user_query_for_analysis}'",
        "llm_call2_framework_header": "【Analysis Framework Reference】\nThe user previously selected the following analysis framework. Please refer to its goals and requirements when interpreting the data and building the chart:",
        "llm_call2_general_guidance_header": "【General Analysis Guidance】",
        "llm_call2_general_guidance_body": "Please provide your English analysis for the actual data provided below.",
        "llm_call2_data_header": "【Actual Queried Data】\nBelow is the data queried based on the user's previous request (in Markdown format):",
        "llm_call2_caveats_header": "【Data Check & Caveats】",
        "llm_call2_caveats_body": "Please carefully check the data for potential issues such as inconsistent geographical names, missing values, or anomalies.",
        "llm_call2_task_header": "【Task Requirements & Output Format】",
        "llm_call2_task_body": """
1. **Text Analysis (`analysis_text`)**: Based on the guidance and data above, provide a detailed text analysis in English.
2. **Final Chart Suggestion**: Based on the actual data and analysis, recommend the most suitable chart type and provide the following parameters as top-level keys in the JSON object:
   - `chart_type`: (string) Recommended chart type ("line", "bar", "pie", "scatter", "table").
   - `x_axis`: (string, optional) X-axis column name.
   - `y_axis`: (string or list of strings, optional) Y-axis column name(s).
   - `category_column`: (string, optional) Category column for pie charts.
   - `value_column`: (string, optional) Value column for pie charts.
   - `title`: (string) Chart title based on the data content and analysis.
   - `explanation`: (string) An explanation of what the chart shows, including key insights and potential data caveats.
Please strictly encapsulate all results in a single JSON object, ensuring all the above chart parameter keys are at the top level of the JSON.
""",
    }

def get_ui_texts_en() -> dict:
    """Returns all English UI texts."""
    return {
        # --- Page & Sidebar ---
        "page_title": "Beautyytics",
        "sidebar_header": "Analysis Options",
        "sidebar_framework_select_label": "Analysis Framework Selection",
        "sidebar_framework_select_box": "Select Analysis Framework:",
        "clear_history_button": "Clear Chat History",
        "language_selector_label": "语言 / Language",

        # --- Main Page Welcome ---
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

        # --- In-process Messages & Errors ---
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

        # --- Analysis Framework Names (for UI) ---
        "framework_general": "General Analysis (Default)",
        "framework_descriptive": "Descriptive Analysis (Sales Overview)",
        "framework_diagnostic": "Diagnostic Analysis (Root Cause)",
        "framework_predictive": "Predictive Analysis (Future Performance)",
        "framework_swot": "SWOT Analysis (Competitive Assessment)",
        "framework_funnel": "Funnel Analysis (Conversion Path)",
        "framework_logic_tree": "Logic Tree Analysis (Problem Decomposition)",
    }
