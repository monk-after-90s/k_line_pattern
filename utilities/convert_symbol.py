import vnpy_crypto

vnpy_crypto.init()
import asyncio
import importlib
import time
from collections import defaultdict
from vnpy.trader.constant import Product
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import ContractData
from vnpy_binance_pro import (
    BinanceSpotGateway,
    BinanceUsdtGateway,
    BinanceInverseGateway
)
from vnpy_crypto import Exchange

# 交易所的vnpy symbol到ContractData的映射
vnpy_symbol_contract_mapping = defaultdict(dict)
# exchange的市场类型的通用symbol到ContractData的映射
united_symbol_contract_mapping = defaultdict(lambda: defaultdict(dict))
# gateway
gateway_classes = (BinanceSpotGateway, BinanceUsdtGateway, BinanceInverseGateway)
# 初始化锁
lock = asyncio.Lock()


def get_symbol_type(contract: ContractData):
    """通过vnpy的市场类型转换为API传入的市场类型"""
    if contract.product == Product.SPOT:
        return 'spot'
    elif contract.product == Product.FUTURES:
        return "futures"


def get_contract_product(symbol_type: str):
    """通用市场类型到vnpy Product枚举的转换"""
    return {"spot": Product.SPOT,
            "futures": Product.FUTURES}[symbol_type]


def init_symbol_mapping():
    """初始化符号映射"""
    main_engine = MainEngine()
    # 连接gateway
    for gateway_classe in gateway_classes:
        main_engine.add_gateway(gateway_classe)
        main_engine.connect(
            setting={'key': "", 'secret': "", "代理地址": "", "代理端口": "", "服务器": "REAL"},
            gateway_name=gateway_classe.default_name)
    time.sleep(5)  # 等待连接完成
    try:
        main_engine.close()
    except:
        pass
    # 获取合约 建立映射
    for gateway_classe in gateway_classes:
        gateway_module = importlib.import_module(gateway_classe.__module__)
        for contract in gateway_module.symbol_contract_map.values():
            contract: ContractData
            for exchange in gateway_classe.exchanges:
                exchange: Exchange
                symbol_type = get_symbol_type(contract)
                vnpy_symbol_contract_mapping[exchange.value][contract.symbol] = contract
                # 币安的特殊处理一下
                if "BINANCE" in exchange.value:
                    if symbol_type == "spot":
                        united_symbol_contract_mapping[exchange.value][symbol_type][contract.name] = contract
                    else:  # 选取永续合约
                        united_symbol_contract_mapping[exchange.value][symbol_type][contract.name] = get_bn_futures(
                            contract.name)
                else:
                    united_symbol_contract_mapping[exchange.value][symbol_type][contract.name] = contract


def get_bn_futures(united_symbol: str):
    """获取币安的永续合约"""
    for gateway_classe in (BinanceUsdtGateway, BinanceInverseGateway):
        gateway_module = importlib.import_module(gateway_classe.__module__)
        for contract in gateway_module.symbol_contract_map.values():
            contract: ContractData
            if contract.name == united_symbol and contract.symbol == united_symbol.replace('/', ''):
                return contract


async def symbol_vnpy2united(exchange: str, vnpy_symbol: str, init=False):
    """
    vnpy的symbol转换为通用市场类型(spot、futures)和通用symbol(BTC/USDT)

    :return: symbol_type(spot、futures)，united_symbol(BTC/USDT)
    """
    if init:
        # 没有其他初始化过程
        if not lock.locked():
            # 初始化
            async with lock:
                await asyncio.get_running_loop().run_in_executor(None, init_symbol_mapping)
        else:  # 有其他初始化过程，等初始化完成
            async with lock:
                ...
            # 直接转换
            return await symbol_vnpy2united(exchange, vnpy_symbol)
    try:
        contract: ContractData = vnpy_symbol_contract_mapping[exchange][vnpy_symbol]
        return get_symbol_type(contract), contract.name
    except KeyError:
        if not init:
            return await symbol_vnpy2united(exchange, vnpy_symbol, True)
        else:
            raise


async def symbol_united2vnpy(exchange: str, symbol_type: str, united_symbol: str, init=False):
    """
    通用symbol到vnpy symbol

    :return: vnpy symbol如btcusdt，表示币安现货的BTC/USDT
    """
    if init:
        # 没有其他初始化过程
        if not lock.locked():
            # 初始化
            async with lock:
                await asyncio.get_running_loop().run_in_executor(None, init_symbol_mapping)
        else:  # 有其他初始化过程，等初始化完成
            async with lock:
                ...
            # 直接转换
            return await symbol_united2vnpy(exchange, symbol_type, united_symbol)

    try:
        contract: ContractData = united_symbol_contract_mapping[exchange][symbol_type][united_symbol]
        return contract.symbol
    except KeyError:
        if not init:
            return await symbol_united2vnpy(exchange, symbol_type, united_symbol, True)
        else:
            raise


if __name__ == '__main__':
    from loguru import logger


    async def test():
        logger.info(await asyncio.gather(symbol_vnpy2united('BINANCE', 'btcusdt'),
                                         symbol_vnpy2united('BINANCE', 'ltcusdt'),
                                         symbol_vnpy2united('BINANCE', 'ethusdt'),
                                         symbol_vnpy2united('BINANCE', 'bnbusdt'),
                                         ))
        logger.info(await symbol_united2vnpy('BINANCE', 'spot', "ETH/USDT"))
        logger.info(await symbol_united2vnpy('BINANCE', 'futures', "LTC/USDT"))

        logger.info(await symbol_united2vnpy('OKEX', 'futures', "LTC/USDT"))


    asyncio.run(test())
