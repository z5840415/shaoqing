"""
抖音自动化引擎
"""
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Dict, Any, Optional
import json
import logging
from .base import BaseAutomation, AutomationError

logger = logging.getLogger(__name__)


class DouyinAutomation(BaseAutomation):
    """抖音自动化引擎"""

    DOUYIN_URL = "https://www.douyin.com"

    async def initialize(self):
        """初始化浏览器"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await self.context.new_page()

            # 设置超时
            self.page.set_default_timeout(self.timeout)

            logger.info("浏览器初始化成功")
            return True
        except Exception as e:
            logger.error(f"浏览器初始化失败: {str(e)}")
            raise AutomationError(f"浏览器初始化失败: {str(e)}")

    async def login(self, cookies: Optional[str] = None) -> bool:
        """
        登录抖音

        Args:
            cookies: Cookie JSON字符串

        Returns:
            是否登录成功
        """
        try:
            # 访问抖音首页
            await self.page.goto(self.DOUYIN_URL)
            await self.random_delay(2, 4)

            if cookies:
                # 使用Cookie登录
                cookies_dict = json.loads(cookies) if isinstance(cookies, str) else cookies
                await self.context.add_cookies(cookies_dict)
                await self.page.reload()
                await self.random_delay(2, 3)

                # 验证登录状态
                is_logged_in = await self._check_login_status()
                if is_logged_in:
                    logger.info("Cookie登录成功")
                    return True
                else:
                    logger.warning("Cookie已失效，需要重新登录")
                    return False
            else:
                # 手动扫码登录（返回False，需要人工介入）
                logger.info("请手动扫码登录")
                return False

        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            raise AutomationError(f"登录失败: {str(e)}")

    async def _check_login_status(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查页面中是否存在登录后的元素（如头像、用户名等）
            # 这里需要根据实际抖音页面结构调整选择器
            await self.page.wait_for_selector('[data-e2e="user-info"]', timeout=5000)
            return True
        except PlaywrightTimeout:
            return False

    async def send_message(self, profile_url: str, message: str) -> bool:
        """
        发送私信

        Args:
            profile_url: 创作者主页链接
            message: 私信内容

        Returns:
            是否发送成功
        """
        try:
            logger.info(f"正在访问主页: {profile_url}")

            # 访问创作者主页
            await self.page.goto(profile_url)
            await self.random_delay(2, 4)

            # 查找并点击私信按钮
            # 注意：这些选择器需要根据实际抖音页面结构调整
            try:
                # 尝试多个可能的私信按钮选择器
                message_button_selectors = [
                    'button:has-text("私信")',
                    '[data-e2e="user-message"]',
                    '.user-message-btn',
                    'button[title="私信"]'
                ]

                message_button = None
                for selector in message_button_selectors:
                    try:
                        message_button = await self.page.wait_for_selector(selector, timeout=3000)
                        if message_button:
                            break
                    except PlaywrightTimeout:
                        continue

                if not message_button:
                    raise AutomationError("未找到私信按钮")

                await message_button.click()
                await self.random_delay(1, 2)

            except Exception as e:
                logger.error(f"点击私信按钮失败: {str(e)}")
                raise AutomationError(f"无法打开私信窗口: {str(e)}")

            # 等待私信输入框出现
            try:
                input_selectors = [
                    'textarea[placeholder*="消息"]',
                    'textarea[placeholder*="私信"]',
                    '.message-input',
                    'textarea.im-input'
                ]

                input_element = None
                for selector in input_selectors:
                    try:
                        input_element = await self.page.wait_for_selector(selector, timeout=3000)
                        if input_element:
                            break
                    except PlaywrightTimeout:
                        continue

                if not input_element:
                    raise AutomationError("未找到私信输入框")

                # 模拟打字输入消息
                await self.random_delay(0.5, 1.5)
                await self.simulate_typing(input_element, message)
                await self.random_delay(1, 2)

            except Exception as e:
                logger.error(f"输入消息失败: {str(e)}")
                raise AutomationError(f"无法输入消息: {str(e)}")

            # 查找并点击发送按钮
            try:
                send_button_selectors = [
                    'button:has-text("发送")',
                    '[data-e2e="message-send"]',
                    '.message-send-btn',
                    'button[type="submit"]'
                ]

                send_button = None
                for selector in send_button_selectors:
                    try:
                        send_button = await self.page.wait_for_selector(selector, timeout=2000)
                        if send_button:
                            break
                    except PlaywrightTimeout:
                        continue

                if not send_button:
                    raise AutomationError("未找到发送按钮")

                await send_button.click()
                await self.random_delay(1, 2)

                logger.info("私信发送成功")
                return True

            except Exception as e:
                logger.error(f"点击发送按钮失败: {str(e)}")
                raise AutomationError(f"无法发送消息: {str(e)}")

        except AutomationError:
            raise
        except Exception as e:
            logger.error(f"发送私信失败: {str(e)}")
            raise AutomationError(f"发送私信失败: {str(e)}")

    async def check_message_status(self, profile_url: str) -> Dict[str, Any]:
        """
        检查消息状态

        Args:
            profile_url: 创作者主页链接

        Returns:
            消息状态信息 {viewed: bool, replied: bool, reply_content: str}
        """
        try:
            # 访问私信列表
            await self.page.goto(f"{self.DOUYIN_URL}/messages")
            await self.random_delay(2, 3)

            # 这里需要根据实际页面结构来判断消息状态
            # 示例代码，实际需要调整
            status = {
                "viewed": False,
                "replied": False,
                "reply_content": None
            }

            # TODO: 实现实际的状态检测逻辑

            return status

        except Exception as e:
            logger.error(f"检查消息状态失败: {str(e)}")
            return {"viewed": False, "replied": False, "reply_content": None}

    async def get_cookies(self) -> str:
        """获取当前Cookie"""
        try:
            cookies = await self.context.cookies()
            return json.dumps(cookies)
        except Exception as e:
            logger.error(f"获取Cookie失败: {str(e)}")
            return None

    async def close(self):
        """关闭浏览器"""
        try:
            await super().close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器失败: {str(e)}")
