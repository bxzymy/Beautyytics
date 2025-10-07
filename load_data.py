import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Dict, Union


@st.cache_data
def load_data():
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
        st.error("错误: CSV数据文件 'random_order_data.csv' 未找到。请确保文件路径正确。")
        return None
    except Exception as e:
        st.error(f"加载数据时发生未知错误: {e}")
        return None


