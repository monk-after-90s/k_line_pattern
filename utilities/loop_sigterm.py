import signal
from asyncio import AbstractEventLoop


def handle_sigterm(loop: AbstractEventLoop):
    """使事件循环可以处理sigterm信号，触发其暂停动作"""

    def sigterm_handler(sig, frame):
        # 暂停事件循环
        loop.stop()

    signal.signal(signal.SIGTERM, sigterm_handler)
