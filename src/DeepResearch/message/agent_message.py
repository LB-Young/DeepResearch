from .base_message import BaseMessage
import re

class AgentMessage(BaseMessage):
    def __init__(self, role: str, content: str, message_type: str, message_from: str, message_to: str):
        super().__init__(role, content, message_type, message_from, message_to)
    
    def execute_compress(self) -> str:
        """
        执行Agent消息的压缩逻辑
        主要压缩重复的空白字符、移除多余的换行符，保留关键信息
        
        Returns:
            str: 压缩后的内容
        """
        if not self.content:
            self.compressed_content = ""
            return self.compressed_content
        
        # 移除多余的空白字符和换行符
        compressed = re.sub(r'\s+', ' ', self.content.strip())
        
        # 保留重要的标点符号前后的空格
        compressed = re.sub(r'\s*([.!?;:])\s*', r'\1 ', compressed)
        
        # 移除行首行尾多余空格
        compressed = compressed.strip()
        
        # 如果压缩后长度超过原长度的80%，则进一步压缩
        if len(compressed) > len(self.content) * 0.8:
            # 移除常见的填充词
            filler_words = ['um', 'uh', 'well', 'you know', 'like', 'actually', 'basically']
            for word in filler_words:
                compressed = re.sub(rf'\b{word}\b\s*', '', compressed, flags=re.IGNORECASE)
        
        self.compressed_content = compressed
        return self.compressed_content
