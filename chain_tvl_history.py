import logging

from dash import dcc
import plotly.graph_objs as go
import requests
import pandas as pd

chain_name_list = [
    "tron",
    "bsc",
    "polygon",
    "avalanche",
    "solana",
    "arbitrum",
    "optimism",
    "base",
    "ton"
]


# 获取链的历史 TVL 数据
def get_chain_historical_tvl(chain):
    logging.info("加载%s历史tvl" % chain)
    url = f"https://api.llama.fi/charts/{chain}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Dash 布局
def gen_chain_historical_tvl_layout():
    data_frames = []
    for chain_name in chain_name_list:
        # 数据准备
        data = get_chain_historical_tvl(chain_name)
        if data:
            for d in data:
                d["date"] = int(d["date"])
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'], unit='s')
            df.set_index('date', inplace=True)
            df.rename(columns={'totalLiquidityUSD': chain_name}, inplace=True)
            data_frames.append(df)
    all_data = pd.concat(data_frames, axis=1)
    return dcc.Graph(
        id='multi-chain-tvl',
        figure={
            'data': [
                go.Scatter(x=all_data.index, y=all_data[chain_name], mode='lines', name=chain_name)
                for chain_name in chain_name_list
            ],
            'layout': go.Layout(
                title='多链历史 TVL 对比',
                xaxis={'title': '日期'},
                yaxis={'title': '总锁定价值 (USD)'}
            )
        }
    )