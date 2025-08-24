from typing import Dict, Any, Optional, Iterator, Union
from abc import ABC, abstractmethod

class BaseMessage(ABC):
    def __init__(self, role: str, content: str, message_type: str, message_from: str, message_to: str):
        """
        role:
        content:
        message_type:
        message_from:
        message_to:
        """
        self.role = role
        self.content = content
        self.compressed_content = None
        self.message_type = message_type
        self.message_from = message_from
        self.message_to = message_to

    async def execute_compress(self) -> str:
        """
        执行消息压缩的抽象方法
        子类需要实现具体的压缩逻辑
        
        Returns:
            str: 压缩后的内容
        """
        pass
    
    async def get_compressed_content(self) -> str:
        """
        获取压缩后的内容
        
        Returns:
            str: 压缩后的内容，如果未压缩则返回原内容
        """
        print("self.compressed_content:", self.compressed_content)
        return self.compressed_content if self.compressed_content else self.content

    async def get_role(self):
        return self.role