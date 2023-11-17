import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from chain_tvl_history import gen_chain_historical_tvl_layout
from chain_currenct_tvl import get_chains_tvl, gen_chains_tvl_layout, gen_chains_tvl_table

# 创建 Dash 应用实例
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# 设置应用的路由
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# 首页布局
index_page = html.Div([
    html.H1('Chain Data Analysis'),
    dcc.Link('查询链历史TVL图表', href='/tvl-chart'),
])


# TVL 图表页面布局
def gen_tvl_chart_page():
    tvl_data = get_chains_tvl()
    tvl_chart_page = html.Div([
        gen_chain_historical_tvl_layout(),
        gen_chains_tvl_layout(tvl_data),
        gen_chains_tvl_table(tvl_data),
        dcc.Link('回到主页', href='/'),
    ], style={'textAlign': 'center', 'width': '100%', 'margin': '0 auto'})
    return tvl_chart_page


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/tvl-chart':
        return gen_tvl_chart_page()
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True)