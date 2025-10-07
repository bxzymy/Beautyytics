import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 中英文文本映射
CHART_TEXTS = {
    'zh': {
        'untitled': '未命名图表',
        'line_missing': '折线图列缺失. X:{x_col}, Y:{y_col}. 显示表格.',
        'bar_missing': '柱状图列缺失. X:{x_col}, Y:{y_col}. 显示表格.',
        'pie_missing': '饼图列缺失. Names:{cat_col}, Values:{val_col}. 显示表格.',
        'scatter_missing': '散点图列缺失. X:{x_col}, Y:{y_col}. 显示表格.',
        'unknown_type': "未知图表类型: '{chart_type}'. 显示表格.",
        'chart_explanation': "图表说明: {explanation}",
        'chart_error': "生成图表 '{title}' ({chart_type}) 出错: {e}"
    },
    'en': {
        'untitled': 'Untitled Chart',
        'line_missing': 'Missing columns for line chart. X:{x_col}, Y:{y_col}. Showing table instead.',
        'bar_missing': 'Missing columns for bar chart. X:{x_col}, Y:{y_col}. Showing table instead.',
        'pie_missing': 'Missing columns for pie chart. Names:{cat_col}, Values:{val_col}. Showing table instead.',
        'scatter_missing': 'Missing columns for scatter plot. X:{x_col}, Y:{y_col}. Showing table instead.',
        'unknown_type': "Unknown chart type: '{chart_type}'. Showing table instead.",
        'chart_explanation': "Chart explanation: {explanation}",
        'chart_error': "Error generating chart '{title}' ({chart_type}): {e}"
    }
}


def get_chart_text(key, lang='zh', **kwargs):
    """获取本地化的图表文本"""
    return CHART_TEXTS[lang][key].format(**kwargs)


def generate_streamlit_chart(chart_type: str, df: pd.DataFrame, chart_params: dict,
                             chart_key: str = None, lang: str = 'zh'):
    """
    生成Streamlit图表
    Args:
        chart_type: 图表类型 (line/bar/pie/scatter/table)
        df: 数据DataFrame
        chart_params: 图表参数字典
        chart_key: 图表唯一键
        lang: 语言 ('zh' 或 'en')
    """
    if df is None or df.empty:
        return

    title = chart_params.get('title', get_chart_text('untitled', lang))
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
                st.warning(get_chart_text('line_missing', lang, x_col=x_col, y_col=y_col))
                st.dataframe(df)

        elif chart_type == "bar":
            x_col, y_col = chart_params.get("x_axis"), chart_params.get("y_axis")
            if x_col and y_col and x_col in df.columns and any(
                    c in df.columns for c in (y_col if isinstance(y_col, list) else [y_col])):
                fig = px.bar(df, x=x_col,
                             y=[c for c in (y_col if isinstance(y_col, list) else [y_col]) if c in df.columns],
                             title=title)
            else:
                st.warning(get_chart_text('bar_missing', lang, x_col=x_col, y_col=y_col))
                st.dataframe(df)

        elif chart_type == "pie":
            cat_col, val_col = chart_params.get("category_column"), chart_params.get("value_column")
            if cat_col and val_col and cat_col in df.columns and val_col in df.columns:
                fig = px.pie(df, names=cat_col, values=val_col, title=title)
            else:
                st.warning(get_chart_text('pie_missing', lang, cat_col=cat_col, val_col=val_col))
                st.dataframe(df)

        elif chart_type == "scatter":
            x_col, y_col = chart_params.get("x_axis"), chart_params.get("y_axis")
            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                fig = px.scatter(df, x=x_col, y=y_col, title=title)
            else:
                st.warning(get_chart_text('scatter_missing', lang, x_col=x_col, y_col=y_col))
                st.dataframe(df)

        elif chart_type == "table":
            st.dataframe(df)

        else:
            st.info(get_chart_text('unknown_type', lang, chart_type=chart_type))
            st.dataframe(df)

        if fig:
            st.plotly_chart(fig, use_container_width=True, key=chart_key)

        if explanation and (fig or chart_type == "table"):
            st.caption(get_chart_text('chart_explanation', lang, explanation=explanation))

    except Exception as e:
        st.error(get_chart_text('chart_error', lang, title=title, chart_type=chart_type, e=e))
        st.dataframe(df)