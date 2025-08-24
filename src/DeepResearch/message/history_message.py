from .base_message import BaseMessage
import re
from typing import List

class HistoryMessage(BaseMessage):
    def __init__(self, role: str, content: str, message_type: str, message_from: str, message_to: str):
        super().__init__(role, content, message_type, message_from, message_to)
    
    async def execute_compress(self) -> str:
        """
        执行历史消息的压缩逻辑
        保留关键信息，移除冗余内容，适合长期存储
        
        Returns:
            str: 压缩后的内容
        """
        if not self.content:
            self.compressed_content = ""
            return self.compressed_content
        
        # 分割成句子进行处理
        sentences = re.split(r'[.!?]+', self.content)
        important_sentences = []
        
        # 关键词列表，包含这些词的句子会被保留
        key_words = [
            'result', 'conclusion', 'important', 'key', 'main', 'primary',
            'significant', 'critical', 'essential', 'summary', 'final',
            'decision', 'action', 'next', 'todo', 'task', 'goal'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 保留包含关键词的句子
            if any(keyword in sentence.lower() for keyword in key_words):
                important_sentences.append(sentence)
            # 保留较短的句子（可能是重要信息）
            elif len(sentence.split()) <= 10:
                important_sentences.append(sentence)
            # 保留包含数字的句子（可能是数据或结果）
            elif re.search(r'\d+', sentence):
                important_sentences.append(sentence)
        
        # 如果没有找到重要句子，保留前几句
        if not important_sentences:
            important_sentences = sentences[:3]
        
        # 重新组合句子
        compressed = '. '.join(important_sentences)
        
        # 清理多余的空白字符
        compressed = re.sub(r'\s+', ' ', compressed.strip())
        
        # 确保以句号结尾
        if compressed and not compressed.endswith('.'):
            compressed += '.'
        
        self.compressed_content = compressed
        return self.compressed_content
