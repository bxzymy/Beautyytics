# ======================
# Beauty Industry Sales Analysis Prompt Library
# Usage Instructions:
#   1. Import the required template functions
#   2. Call the functions with parameters
#   3. Combine the returned prompt with user questions and send to LLM
# ======================

class BeautyAnalyticsPromptsEn:
    @staticmethod
    def descriptive_analysis(
            time_period: str = "Q1-Q2 2024",
            product_categories: list = ["Skincare", "Makeup", "Perfume"],
            channels: list = ["Tmall", "Douyin", "Offline Counters"]
    ) -> str:
        """
        Descriptive Analysis Template: Basic Sales Data Statistics
        Applicable scenarios: Performance overview, monthly/quarterly reports
        """
        return f"""
As a senior analyst in the beauty industry, please conduct a comprehensive scan and analysis of sales performance based on the following dimensions:
1. Product dimension (statistics by categories: {', '.join(product_categories)}):
   - Absolute sales and market share
   - Month-over-month growth rate (compared to previous period)
   - Top 3 products by return rate analysis
2. Channel dimension (performance on platforms: {', '.join(channels)}):
   - GMV share and average order value comparison across channels
   - Channel growth efficiency index (traffic cost vs. conversion rate)
3. Customer dimension:
   - Contribution ratio of new vs. returning customers (validate the 80/20 rule)
   - Geographic distribution heatmap (tier-1 cities vs. lower-tier markets)
4. Visualization requirements:
   - Combined trend chart: dual Y-axis curve of sales and gross profit
   - Table: Top 10 best-selling products list, including SKU, unit price, repurchase rate
   - Core conclusions: summarize key findings in 3 sentences, including anomaly warnings
Special notes:
- If data is missing, please clearly mark 【Data Required】 and explain the impact of missing data on analysis.
"""

    @staticmethod
    def diagnostic_analysis(
            problem: str = "20% YoY sales decline",
            focus_area: str = "Essence category",
            time_comparison: str = "same period in 2023"
    ) -> str:
        """
        Diagnostic Analysis Template: Root Cause Identification
        Applicable scenarios: Performance anomaly diagnosis, sudden drop analysis
        """
        return f"""
Please diagnose the issue of 【{problem}】 observed in the beauty brand's 【{focus_area}】 during 【{time_comparison}】. Specific requirements:
1. Multi-dimensional attribution analysis:
   a) Price band penetration test: Focus on market share trend changes in the main price segment (200-500 RMB)  
   b) Competitor comparison matrix: Select 3 main competitors to compare promotion intensity and new product launch pace  
   c) Channel health scan: Monitor GPM (gross profit margin) fluctuations in Douyin self-broadcast rooms
2. Deep dive into user behavior:
   - Profile of churned customers: analyze consumption level, age distribution, and city tier distribution  
   - Customer complaint keyword cloud: use NLP to extract and rank top 5 quality issue keywords
3. Supply chain traceability:
   - Inventory turnover anomaly detection  
   - Core ingredient (e.g., Bosexin) supply stability assessment
4. Output requirements:
   - Attribution conclusions at three levels: primary cause (weight ≥ 50%), secondary cause (30%), incidental factors (20%)  
   - Accompanying validation plan: suggest 2 A/B tests to verify core hypotheses
"""

    @staticmethod
    def predictive_analysis(
            product_line: str = "Anti-aging Skincare Series",
            forecast_period: str = "Q3 2024",
            key_drivers: list = ["Number of holidays", "Social media advertising budget", "Competitor new product launch pace"]
    ) -> str:
        """
        Predictive Analysis Template: Future Performance Simulation
        Applicable scenarios: Sales forecasting, budget planning
        """
        return f"""
Please forecast the sales trend of 【{product_line}】 for 【{forecast_period}】 based on historical data, with specific requirements:
1. Modeling framework:
   - Basic model: Time series decomposition (seasonal + trend + residual components)
   - Enhanced factors: include regression coefficient analysis of {', '.join(key_drivers)}
2. Beauty industry-specific parameters:
   - Promotion leverage (e.g., 618, Double 11 amplification effect on GMV)
   - KOL advertising decay curve (lifecycle of viral content)
   - Weather sensitivity parameters (e.g., UV index impact on sunscreen category)
3. Deliverables:
   a) Sales forecast in three scenarios: optimistic, neutral, pessimistic numeric predictions  
   b) Sensitivity analysis table, example format:
        | Variable Change    | GMV Impact | Profit Impact |
        | ------------------ | ---------- | ------------- |
        | Marketing spend +10%| ?%         | ?%            |
        | Raw material cost +5%| ?%        | ?%            |
   c) Warning of inflection points: identify key months that may breach inventory alert thresholds
"""

    @staticmethod
    def swot_analysis(
            brand_position: str = "Domestic mid-tier skincare",
            core_competency: str = "Plant extraction technology"
    ) -> str:
        """
        SWOT Analysis Template: Competitiveness Assessment
        Applicable scenarios: Strategic planning, competitor analysis
        """
        return f"""
Please build a dynamic SWOT matrix for the 【{brand_position}】 beauty brand, with specific content as follows:
Strengths (S):
- Technical barriers: Patent coverage of {core_competency} (please provide specific data)
- Supply chain: Flexible production capability (including minimum order quantity / MOQ data)
Weaknesses (W):
- Channel shortcomings: Offline BA training pass rate (with regional comparisons)
- Repurchase defects: Member 6-month retention rate vs. industry benchmark
Opportunities (O):
- Policy dividends: Progress in entering Hainan duty-free channels
- Ingredient trends: Growth rate of clean beauty demand
Threats (T):
- International brands: Price reduction monitoring of major competitors like Estée Lauder
- Regulatory risks: Declining approval rate for new raw material filings
Output requirements:
- Provide at least two quantitative evidences per dimension (e.g., "Tmall flagship store search share dropped from 12% in Q1 to 9% in Q2")
- Generate a strategic four-quadrant chart, emphasizing priority implementation plans for SO strategies (Strengths + Opportunities)
"""

    @staticmethod
    def funnel_analysis(
            campaign_name: str = "Summer Sunscreen Campaign",
            funnel_steps: list = ["Ad Impressions", "Detail Page Visits", "Add to Cart", "Successful Payment"]
    ) -> str:
        """
        Funnel Analysis Template: Conversion Path Optimization
        Applicable scenarios: Marketing campaign evaluation, user path optimization
        """
        return f"""
Please analyze the user conversion funnel for the campaign 【{campaign_name}】 with the following requirements:
1. Funnel modeling:
   - Step definitions: {' → '.join(funnel_steps)}
   - Conversion benchmarks: compare industry averages and the product's historical best
2. Bottleneck diagnosis:
   - Conduct deep attribution analysis for stages with churn rate over 40%
   - Page heatmap analysis, including mouse trajectory and dwell time
3. Scenario-based optimization suggestions:
   - Golden 3-second rule: optimize above-the-fold information density
   - Trust building: increase exposure of trust elements such as test reports
   - Churn recovery: formulate outreach strategies for abandoned cart users
4. Predicted benefits:
   - If the conversion rate of 【{funnel_steps[1]}】 increases by 5 percentage points, expected GMV increase is __ million RMB
   - Optimizing detail page load speed to 1.5 seconds could reduce bounce rate by __%
"""

    @staticmethod
    def logic_tree(
            core_question: str = "How to improve high-end product profit margin",
            mcee_layers: int = 3
    ) -> str:
        """
        Logic Tree Template: Complex Problem Breakdown
        Applicable scenarios: Strategic issue decomposition, systematic problem analysis
        """
        return f"""
Please decompose the strategic proposition 【{core_question}】 based on the MECE principle, with the following specifics:
First layer: Core dimensions  
- Increase revenue (including new customer acquisition and existing customer value enhancement)  
- Cost saving (including supply chain optimization and operational efficiency)  
Second layer: Beauty industry specifics  
├─ New customer acquisition: High-end customer penetration strategies (e.g., luxury SPA partnerships)  
├─ Existing customer value enhancement: Customized services (e.g., AI skin analysis and formula customization)  
├─ Supply chain: Packaging cost breakdown (e.g., glass bottles account for __% of total cost)  
└─ Operations: BA productivity improvement (e.g., intelligent script assistance)  
Third layer: Executable items  
- Cross-industry collaboration: Co-branding premium solutions with luxury brands  
- Cost control: Alternative packaging supplier price comparison table  
Output requirements:  
- Ensure all dimension layers are mutually exclusive and collectively exhaustive (MECE)  
- Mark implementation priority for terminal nodes (High H, Medium M, Low L)  
- Quantify expected benefit, e.g., contribution to profit margin percentage points per measure
"""

    @staticmethod
    def data_requirements_check() -> str:
        """
        Data readiness check module
        Note: It is recommended to prepend this module to all prompts
        """
        return """
**Data Readiness Check**:  
[ ] Time period   [ ] Product segmentation   [ ] Channel data  
[ ] Cost structure   [ ] Customer profiling   [ ] Competitor data  
Adjust analysis depth automatically based on missing data (L1 basic → L3 deep)
"""
