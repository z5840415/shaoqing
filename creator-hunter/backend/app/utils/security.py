"""
安全工具类
"""
from cryptography.fernet import Fernet
from typing import Optional
import base64
import os


class SecurityManager:
    """安全管理器 - 用于加密敏感数据"""

    def __init__(self, key: Optional[str] = None):
        """
        初始化安全管理器

        Args:
            key: 加密密钥（base64编码），如果不提供则自动生成
        """
        if key:
            self.key = key.encode()
        else:
            # 从环境变量读取或生成新密钥
            env_key = os.getenv('ENCRYPTION_KEY')
            if env_key:
                self.key = env_key.encode()
            else:
                self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        """
        加密字符串

        Args:
            data: 原始字符串

        Returns:
            加密后的字符串（base64编码）
        """
        if not data:
            return ""
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字符串

        Args:
            encrypted_data: 加密的字符串

        Returns:
            解密后的原始字符串
        """
        if not encrypted_data:
            return ""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()

    @staticmethod
    def generate_key() -> str:
        """生成新的加密密钥"""
        return Fernet.generate_key().decode()


# 全局安全管理器实例
security_manager = SecurityManager()
