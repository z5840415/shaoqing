"""
自动化基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import random
import asyncio


class AutomationError(Exception):
    """自动化异常"""
    pass


class BaseAutomation(ABC):
    """自动化基类"""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        初始化自动化引擎

        Args:
            headless: 是否无头模式
            timeout: 超时时间（毫秒）
        """
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.context = None
        self.page = None

    @abstractmethod
    async def login(self, cookies: Optional[str] = None) -> bool:
        """
        登录平台

        Args:
            cookies: Cookie字符串

        Returns:
            是否登录成功
        """
        pass

    @abstractmethod
    async def send_message(self, profile_url: str, message: str) -> bool:
        """
        发送私信

        Args:
            profile_url: 创作者主页链接
            message: 私信内容

        Returns:
            是否发送成功
        """
        pass

    @abstractmethod
    async def check_message_status(self, profile_url: str) -> Dict[str, Any]:
        """
        检查消息状态

        Args:
            profile_url: 创作者主页链接

        Returns:
            消息状态信息
        """
        pass

    async def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        随机延迟（模拟人类操作）

        Args:
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数
        """
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def simulate_typing(self, element, text: str):
        """
        模拟打字（非粘贴）

        Args:
            element: 输入元素
            text: 要输入的文本
        """
        for char in text:
            await element.type(char)
            # 随机延迟，模拟打字速度
            await asyncio.sleep(random.uniform(0.05, 0.15))

    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
