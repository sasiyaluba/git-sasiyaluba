# -*- coding:utf-8 -*-

import sys
import json

sys.path.append("/home/kaka/EM_team")
from common.config import load_config_file
from common.evm_network import build_rpc_node
from detector.reentrancy_detector import ReentrancyDetector
from detector.getTransactionHash import getTxHash, load_tx_hash

# import eventlet
from web3 import Web3
import time

provider_rpc = {
    "development": "http://localhost:9944",
    "quicknode": "https://yolo-wider-surf.quiknode.pro/8157ec3efdf4df16c1dfc03b68c504a28857d5ab/",
}
web3 = Web3(Web3.HTTPProvider(provider_rpc["quicknode"]))
# web3 = rpc_node.web3
# response = web3.provider.make_request(
#     RPCEndpoint("debug_traceTransaction"), ["0x04934c059af702046c594090d477c0a21d61100776eba15ea8723e5060660be7"]
# )
# print(response)
# tx_hash = "0x21e9d20b57f6ae60dac23466c8395d47f42dc24628e5a31f224567a2b4effa88"

# tx_hash = "0xa9a1b8ea288eb9ad315088f17f7c7386b9989c95b4d13c81b69d5ddad7ffe61e" # 没有结果
# tx_hash = "0x32c83905db61047834f29385ff8ce8cb6f3d24f97e24e6101d8301619efee96e"
# tx_hash = "0x8b74995d1d61d3d7547575649136b8765acb22882960f0636941c44ec7bbe146"
# a, b = detector.get_tx_info(tx_hash)

# 记录程序开始运行的时间
# start = time.perf_counter()
# result = detector.detect(
#     "0x32c83905db61047834f29385ff8ce8cb6f3d24f97e24e6101d8301619efee96e"
# )
# print(result)
# print(result)
network = "eth"
config = load_config_file()
network_config = config.networks.get(network)
rpc_node = build_rpc_node(network_config)
detector = ReentrancyDetector(rpc_node=rpc_node)
problem_tx = []


def analyze_tx(tx_hash) -> dict:
    try:
        # eventlet.monkey_patch()
        # with eventlet.Timeout(60, False):
        result = detector.detect(tx_hash)
        return result
    except:
        problem_tx.append(tx_hash)


def execute_analyze(blockNum) -> int:
    result = {}
    start = time.perf_counter()
    # 获取该块的交易数
    txNum = web3.eth.get_block_transaction_count(blockNum)
    with open(f"detector/txHash/{blockNum}.txt", "w") as f:
        for i in range(txNum):
            # 获取该块每个交易
            txHash = web3.eth.get_transaction_by_block(blockNum, i).hash.hex()
            to = web3.eth.get_transaction(txHash)["to"]
            # 交易的to地址不为空，且该交易to地址为合约
            if to != None and web3.eth.get_code(to) != b"":
                f.write(txHash + "\n")
    end = time.perf_counter()
    print(f"get {blockNum} Transaction ok, time {end-start}")
    # 加载交易hash
    txHashes = load_tx_hash(blockNum)
    start = time.perf_counter()
    with open(f"detector/analysis_result/{blockNum}.json", "w") as f:
        print(f"---------------analyze {blockNum} tx ----------------")
        f.write("[")
        for tx_hash in txHashes:
            try:
                # 定时，60s以内
                # eventlet.monkey_patch()
                # with eventlet.Timeout(60, False):
                # 执行检测
                result = detector.detect(tx_hash)
            except:
                problem_tx.append(tx_hash)
            # 结果不为空，且不为None
            if result != {} and result != None:
                # 添加hash标记
                result["tx_hash"] = tx_hash
                json.dump(result, f)
                f.write(",")
        f.write("]")
        end = time.perf_counter()
        print(f"--------{blockNum} analyze ok , time {end-start}--------")
    return 0


def execute(start, end) -> int:
    tx_count = 0
    if start > end or start < 0 or end < 0:
        print(f"error params")
        return
    for i in range(start, end + 1):
        tx_num = execute_analyze(i)
        tx_count += tx_num
    return tx_count


start = time.perf_counter()
print("--------- start detect -----------")
tx_count = execute(15000019, 19000000)

end = time.perf_counter()
print(f"time {end-start},start block {15000000},end block {19000000}")
print(f"tx count {tx_count}")
