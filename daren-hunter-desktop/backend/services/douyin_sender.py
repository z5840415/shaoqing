from playwright.async_api import async_playwright, Browser, Page
import asyncio
import random
import json
from pathlib import Path
import os


class DouyinSender:
    """抖音私信发送器"""

    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context = None
        self.page: Page = None
        self.cookie_data = None

    async def init(self):
        """初始化Playwright和浏览器"""
        self.playwright = await async_playwright().start()

        # 启动浏览器（无头模式）
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )

        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 加载Cookie
        await self.load_cookie()

        # 创建页面
        self.page = await self.context.new_page()

        # 设置反检测
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def load_cookie(self):
        """加载Cookie到浏览器上下文"""
        # 从数据库或文件加载Cookie
        # 这里简化处理，实际应从数据库读取
        from database import SessionLocal, Setting

        db = SessionLocal()
        try:
            setting = db.query(Setting).filter(Setting.key == "douyin_cookie").first()
            if setting:
                cookie_data = json.loads(setting.value)
                cookie = cookie_data.get("cookie")

                if cookie:
                    # 解析Cookie字符串并添加到上下文
                    cookies = []
                    for item in cookie.split('; '):
                        if '=' in item:
                            name, value = item.split('=', 1)
                            cookies.append({
                                'name': name,
                                'value': value,
                                'domain': '.douyin.com',
                                'path': '/'
                            })

                    await self.context.add_cookies(cookies)
                    self.cookie_data = cookie_data
        finally:
            db.close()

    async def test_cookie(self) -> bool:
        """测试Cookie是否有效"""
        try:
            await self.page.goto('https://www.douyin.com/', wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)

            # 检查是否需要登录
            # 如果页面有登录相关元素，说明Cookie失效
            is_logged_in = await self.page.evaluate("""
                () => {
                    // 检查是否有用户头像或用户名等登录标识
                    const userElements = document.querySelectorAll('[class*="user"], [class*="avatar"]');
                    return userElements.length > 0;
                }
            """)

            return is_logged_in
        except Exception as e:
            print(f"Cookie测试失败: {e}")
            return False

    async def send_message(self, homepage_url: str, message: str) -> dict:
        """
        发送私信
        :param homepage_url: 达人主页链接
        :param message: 消息内容
        :return: {'success': bool, 'error': str}
        """
        try:
            # 访问主页
            await self.page.goto(homepage_url, wait_until='networkidle', timeout=30000)

            # 随机停留2-5秒（模拟人类行为）
            await asyncio.sleep(random.uniform(2, 5))

            # 查找私信按钮（这里需要根据实际页面结构调整选择器）
            # 抖音的私信按钮通常在用户资料页
            try:
                # 尝试多种可能的私信按钮选择器
                message_button_selectors = [
                    'text="私信"',
                    'button:has-text("私信")',
                    '[data-e2e="user-info-message"]',
                    'button[class*="message"]'
                ]

                message_button = None
                for selector in message_button_selectors:
                    try:
                        message_button = await self.page.wait_for_selector(selector, timeout=5000)
                        if message_button:
                            break
                    except:
                        continue

                if not message_button:
                    return {'success': False, 'error': '找不到私信按钮'}

                # 点击私信按钮
                await message_button.click()
                await asyncio.sleep(2)

                # 等待消息输入框出现
                input_selectors = [
                    'textarea[placeholder*="消息"]',
                    'textarea[data-e2e="message-input"]',
                    'div[contenteditable="true"]'
                ]

                input_box = None
                for selector in input_selectors:
                    try:
                        input_box = await self.page.wait_for_selector(selector, timeout=5000)
                        if input_box:
                            break
                    except:
                        continue

                if not input_box:
                    return {'success': False, 'error': '找不到消息输入框'}

                # 模拟打字（逐字输入，模拟人类）
                for char in message:
                    await input_box.type(char)
                    await asyncio.sleep(random.uniform(0.05, 0.15))

                await asyncio.sleep(1)

                # 查找并点击发送按钮
                send_button_selectors = [
                    'button:has-text("发送")',
                    'button[data-e2e="message-send"]',
                    'button[class*="send"]'
                ]

                send_button = None
                for selector in send_button_selectors:
                    try:
                        send_button = await self.page.wait_for_selector(selector, timeout=5000)
                        if send_button:
                            break
                    except:
                        continue

                if not send_button:
                    return {'success': False, 'error': '找不到发送按钮'}

                # 点击发送
                await send_button.click()
                await asyncio.sleep(2)

                return {'success': True, 'error': None}

            except Exception as e:
                return {'success': False, 'error': f'发送过程出错: {str(e)}'}

        except Exception as e:
            return {'success': False, 'error': f'访问主页失败: {str(e)}'}

    async def visit_homepage(self, homepage_url: str, duration: int = 3):
        """
        访问主页并停留指定时间
        :param homepage_url: 主页链接
        :param duration: 停留时间（秒）
        """
        try:
            await self.page.goto(homepage_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(duration)

            # 模拟滚动
            await self.page.evaluate("""
                () => {
                    window.scrollBy(0, Math.random() * 500);
                }
            """)

            await asyncio.sleep(1)
        except Exception as e:
            print(f"访问主页失败: {e}")

    async def close(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# 测试代码
async def test_sender():
    """测试发送器"""
    sender = DouyinSender()
    await sender.init()

    # 测试Cookie
    is_valid = await sender.test_cookie()
    print(f"Cookie有效性: {is_valid}")

    # 测试发送
    # result = await sender.send_message(
    #     "https://www.douyin.com/user/xxx",
    #     "测试消息"
    # )
    # print(f"发送结果: {result}")

    await sender.close()


if __name__ == "__main__":
    asyncio.run(test_sender())
