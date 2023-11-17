import time
import requests
import re
import json
from collections import defaultdict
from web3 import Web3

ETH_RPC = "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
LARK = "https://open.larksuite.com/open-apis/bot/v2/hook/90a379b9-85d0-49af-89b6-e66172d1dfee"

REG = r'data:,\{.+?\}'

BLOCK_GAP = 10

ANALYSIS_BLOCK_NUM = 10


def connect(infura_url):
    # 初始化 Web3 连接（使用 Infura）
    web3 = Web3(Web3.HTTPProvider(infura_url))
    block_datas = list()

    # 检查连接是否成功
    if not web3.is_connected():
        print("Failed to connect to Ethereum network!")
        exit()

    while True:
        # 获取当前的区块号
        current_block_number = web3.eth.block_number
        print(current_block_number)
        # 获取区块中的所有交易
        block = web3.eth.get_block(current_block_number, full_transactions=True)

        for tx in block.transactions:
            # 检查是否是发往自己地址的交易
            if tx['to'] == tx['from']:
                # 解析 payload 数据
                if tx['input'] != '0x':
                    payload = tx['input']
                    decode_payload = payload.decode("utf-8")
                    res = re.match(REG, decode_payload)
                    if res:
                        json_data = json.loads(",".join(decode_payload.split(",")[1:]))
                        block_datas.append(json_data)
                        print("TxhHash: %s | Payload: %s" % (tx['hash'].hex(), json_data))
        time.sleep(BLOCK_GAP)
        if current_block_number % ANALYSIS_BLOCK_NUM == 0:
            process_block_data(current_block_number, block_datas)
            block_datas = list()


# 处理每10个区块的数据
def process_block_data(current_block_number, data):
    block_data = defaultdict(int)

    for item in data:
        # 组合 tick 和 p 来确保唯一性
        key = "p: %s, tick: %s" % (item['p'], item['tick'])
        block_data[key] += 1

    # 输出统计结果
    tick_list = list()
    for key in sorted(block_data, key=block_data.get, reverse=True):
        content = f"区块 {current_block_number - ANALYSIS_BLOCK_NUM + 1} 到 {current_block_number} 中出现的: {key} 出现次数: {block_data[key]}"
        print(content)
        tick_list.append(content)

    # 发送lark
    if len(tick_list):
        post_lark_msg(tick_list)


def post_lark_msg(tick_info):
    content = list()
    for data in tick_info:
        content.append(
            [{
                "tag": "text",
                "text": "%s \n" % data
            }]
        )
    msg = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "ETH铭文铸造统计",
                    "content": content
                }
            }
        }
    }
    requests.post(LARK, json=msg)


if __name__ == "__main__":
    connect(ETH_RPC)