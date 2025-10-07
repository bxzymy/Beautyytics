## 第一步：重构核心控制器

​	当前的核心控制器是 sql.py 中的 process_user_query 函数。我将把它从一个简单的执行函数，升级为一个管理整个四阶段分析流程的总调度器。 

**思路安排：** 

​	定义分析状态：在 st.session_state 中创建一个新的、更复杂的对象，例如 current_analysis_job。它将用于追踪单个用户请求的整个生命周期，包含： 

1.  job_status: (e.g., 'PLANNING', 'EXECUTING_QUERIES', 'SYNTHESIZING', 'DONE') 
2.  original_query: 用户的原始问题。 
3.  baseline_result: 阶段一的初步查询结果 (DataFrame)。 
4.  analysis_plan: 阶段二生成的包含多个SQL查询的计划。 
5.  evidence_data: 阶段三收集到的所有数据证据 (一个包含多个DataFrame的列表或字典)。 
6.  final_report: 阶段四生成的最终报告。 

​	流程调度：修改 process_user_query 的内部逻辑，使其按顺序调用新的或改造后的函数，来执行框架的四个阶段。它将负责在每个阶段完成后，更新 current_analysis_job 的状态，并将上一个阶段的输出作为下一个阶段的输入。 

​	UI反馈：在 analysis_page.py 中，根据 current_analysis_job.job_status 的变化，向用户显示不同的状态提示，例如：“正在进行初步分析...”、“已发现关键差异，正在规划深度探查方案...”、“正在执行第2/4步的验证查询...”，提升长时间等待的交互体验。 

##  第二步：引入新的AI能力 - “分析规划器” 

 	这是整个框架的核心增量，需要创建一个全新的AI交互功能，用于实现第二阶段（智能假设与维度分解）。 

 **思路安排**： 

1. 创建新函数：在 llm_response.py 中，新增一个函数，例如 get_analysis_plan(original_query, baseline_data_df)。 
2. 设计专属Prompt：为这个函数设计一个全新的系统提示（System Prompt）。这个Prompt将指示LLM扮演“资深数据分析总监”的角色。它的任务是： 

​	输入：用户的原始问题和第一阶段查询出的数据。 

​	指令：请分析这份初步数据，找出其中的关键信息、异常或值得深挖的点。然后，请提出3-5个核心的分析假设，并将每个假设转化为一个具体的、可执行的DuckDB SQL查询。 

​	输出格式要求：返回一个结构化的JSON对象，其中包含一个查询计划列表，例如：{"plan": [{"purpose": "按产品品类进行销售构成分析", "sql": "SELECT ..."}, {"purpose": "按用户等级进行客户价值分析", "sql": "SELECT ..."}, ...]}。 

​	集成到总调度器：process_user_query 在完成第一阶段后，会调用 get_analysis_plan，并将返回的查询计划存储到 current_analysis_job.analysis_plan 中。 

##  第三步：改造数据执行与AI分析能力 (The Executor & Synthesizer) 

​	 需要改造现有代码，以支持第三阶段（多轮查询）和第四阶段（综合分析）。 

**思路安排**： 

1. 循环执行查询：在 process_user_query 中，增加一个循环逻辑。它会遍历 analysis_plan 中的所有查询任务，调用 execute_sql 函数逐一执行，并将返回的多个DataFrame结果存入 current_analysis_job.evidence_data。 
2. 升级“综合分析器”：改造 llm_response.py 中的 get_final_analysis_and_chart_details 函数。 
3. 修改函数签名：使其能够接收多个数据输入，例如 get_synthesized_report(original_query, evidence_data_map)，其中evidence_data_map是一个将查询目的（purpose）映射到其数据结果（DataFrame）的字典。 

 重写Prompt：重新设计其系统提示，指示LLM扮演“最终报告撰写人”的角色。它的任务是： 

 输入：用户的原始问题和所有收集到的数据证据（包括每个数据的查询目的）。 

 指令：你已经拥有了关于[总览]、[产品构成]、[客户价值]等多个维度的数据。请将这些零散的信息整合起来，撰写一份逻辑连贯、有深度、包含数据支撑和商业建议的综合分析报告。 

 输出：一个包含完整分析文本、结论和多个图表建议的复杂JSON对象。 

##  第四步：UI最终呈现 

 最后，analysis_page.py 需要能将第四阶段产出的复杂报告，以清晰、结构化的方式呈现给用户。 

 思路安排： 

 报告不再是单一的文本框+一张图。 

 可以设计成一个带有章节的报告形式，例如： 

 一、核心结论 (Summary) 

 二、整体销售概览 (包含第一阶段的图表) 

 三、深度洞察：产品维度 (包含针对产品分析的图表和解读) 

 四、深度洞察：用户维度 (包含针对用户分析的图表和解读) 

 五、综合建议 (Actionable Recommendations) 

 这将需要UI代码根据final_report的JSON结构，动态生成不同的Streamlit组件（如st.expander, st.columns, st.markdown, 以及多个图表）。