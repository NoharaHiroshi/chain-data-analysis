import logging
from dash import dash_table
from dash import dcc
import plotly.express as px
import requests
import pandas as pd


def get_chains_tvl():
    logging.info("加载当前各链tvl")
    url = "https://api.llama.fi/v2/chains"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data = sorted(data, key=lambda d: d["tvl"], reverse=True)[:50]
        return data
    else:
        return None


# Dash 布局
def gen_chains_tvl_layout(data):
    df = pd.DataFrame(data)
    # 过滤和排序数据（可选）
    df = df[['name', 'tvl']]  # 仅保留需要的列
    df.sort_values(by='tvl', ascending=False).head(50)  # 根据 TVL 降序排序
    # 绘制饼图
    fig = px.pie(df, values='tvl', names='name', title='各链 TVL 分布')
    fig.update_traces(textposition='inside', textinfo='label+percent', showlegend=False)  # 文字信息在里面
    fig.update_layout(
        autosize=False,
        width=800,  # 设置图表宽度
        height=600,  # 设置图表高度
    )
    return dcc.Graph(
        id='tvl-pie-chart',
        figure=fig,
        style={'display': 'inline-block', 'text-align': 'center'}  # 设置图表的 CSS 样式
    )

# TVL数值转换
def format_tvl(value):
    if value >= 1e9:  # 大于或等于 1 billion
        return str(round(value / 1e9, 2)) + 'B'
    elif value >= 1e6:  # 大于或等于 1 million
        return str(round(value / 1e6, 2)) + 'M'
    else:
        return str(value)


# 表格
def gen_chains_tvl_table(data):
    # 创建数据框并按 TVL 降序排序
    df = pd.DataFrame(data)
    df = df[['name', 'tvl']]  # 仅保留需要的列
    df = df.sort_values(by='tvl', ascending=False).head(50)
    df['tvl'] = df['tvl'].apply(format_tvl)
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",  # 启用排序功能
        page_size=20,  # 分页，每页显示15行
        style_table={'width': '600px', 'overflowY': 'auto', 'text-align': 'center', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-bottom': '10px'}
    )