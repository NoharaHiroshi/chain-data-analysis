import time
import requests
import re
import json
from collections import defaultdict
from web3 import Web3
from config.rpc_config import ETH_RPC
from config.lark_message_config import LARK_LISTENING_MINT_MESSAGE as LARK

REG = r'data:,\{.+?\}'

BLOCK_GAP_TIME = 10

ANALYSIS_BLOCK_NUM = 50


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


def main(infura_url):
    # 初始化 Web3 连接（使用 Infura）
    web3 = Web3(Web3.HTTPProvider(infura_url))
    block_datas = list()

    # 检查连接是否成功
    if not web3.isConnected():
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
                    bytes_data = bytes.fromhex(payload[2:])
                    utf8_payload = bytes_data.decode('utf-8')
                    res = re.match(REG, utf8_payload)
                    if res:
                        json_data = json.loads(",".join(utf8_payload.split(",")[1:]))
                        block_datas.append(json_data)
                        print("TxhHash: %s | Payload: %s" % (tx['hash'].hex(), json_data))
        time.sleep(BLOCK_GAP_TIME)
        if current_block_number % ANALYSIS_BLOCK_NUM == 0:
            process_block_data(current_block_number, block_datas)
            block_datas = list()


if __name__ == "__main__":
    main(ETH_RPC)