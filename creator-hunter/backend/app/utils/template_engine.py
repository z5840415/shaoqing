"""
模板引擎 - 用于话术变量替换
"""
import re
from datetime import datetime
from typing import Dict, Any


class TemplateEngine:
    """话术模板引擎"""

    @staticmethod
    def render(template: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板，替换变量

        Args:
            template: 模板字符串，包含 {变量名} 格式的占位符
            variables: 变量字典

        Returns:
            渲染后的字符串
        """
        result = template

        # 替换所有变量
        for key, value in variables.items():
            pattern = f"{{{key}}}"
            result = result.replace(pattern, str(value))

        return result

    @staticmethod
    def extract_variables(template: str) -> list:
        """
        提取模板中的所有变量

        Args:
            template: 模板字符串

        Returns:
            变量名列表
        """
        pattern = r'\{([^}]+)\}'
        return re.findall(pattern, template)

    @staticmethod
    def build_variables(target_data: Dict, account_data: Dict = None) -> Dict[str, Any]:
        """
        根据目标和账号数据构建变量字典

        Args:
            target_data: 目标创作者数据
            account_data: 账号数据

        Returns:
            变量字典
        """
        variables = {}

        # 目标创作者变量
        if target_data:
            variables['昵称'] = target_data.get('nickname', '')
            variables['粉丝数'] = TemplateEngine._format_number(target_data.get('followers_count', 0))
            variables['内容标签'] = target_data.get('tags', '')

        # 账号变量
        if account_data:
            variables['微信号'] = account_data.get('wechat_id', '')
            variables['运营姓名'] = account_data.get('operator_name', '运营')

        # 时间变量
        now = datetime.now()
        variables['今天'] = now.strftime('%Y年%m月%d日')
        variables['本月'] = now.strftime('%m月')
        variables['星期'] = TemplateEngine._get_weekday(now.weekday())

        # 系统变量
        variables['公司名称'] = '网易'
        variables['项目名称'] = '永劫无间'
        variables['激励政策'] = '每月发布4-10条永劫无间相关内容最多可获得最多1.5万激励'

        return variables

    @staticmethod
    def _format_number(num: int) -> str:
        """格式化数字（万、千）"""
        if num >= 10000:
            return f"{num / 10000:.1f}万"
        elif num >= 1000:
            return f"{num / 1000:.1f}千"
        else:
            return str(num)

    @staticmethod
    def _get_weekday(weekday: int) -> str:
        """获取星期几的中文"""
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        return f"星期{weekdays[weekday]}"

    @staticmethod
    def preview(template: str, target_data: Dict, account_data: Dict = None) -> Dict:
        """
        预览模板渲染效果

        Returns:
            包含原始模板、变量和渲染结果的字典
        """
        variables = TemplateEngine.build_variables(target_data, account_data)
        rendered = TemplateEngine.render(template, variables)

        return {
            'original': template,
            'variables': variables,
            'rendered': rendered,
            'missing_variables': [
                var for var in TemplateEngine.extract_variables(template)
                if var not in variables
            ]
        }
