import re
import asyncio
import threading
import time
from .base_message import BaseMessage
from src.DeepResearch.config.config import CONFIG
from src.DeepResearch.model_client.client import model_client
from src.DeepResearch.utils.constant import COMPRESS_PROMPT_FORMAT


class AgentMessage(BaseMessage):
    def __init__(self, role: str, content: str, message_type: str, message_from: str, message_to: str):
        super().__init__(role, content, message_type, message_from, message_to)
        self.compression_task = None
        self.is_compressing = False
        self.compression_completed = False

        self.agent_message_compress_config = CONFIG.get("compress", {}).get("agent_message", {})

        self.compress_method = self.agent_message_compress_config.get("method", "no_compress")
        if self.compress_method == "model":
            self.model = self.agent_message_compress_config.get("model", None)
            if self.model is None:
                raise ValueError("No model specified for model compression")
        self.compress_length = self.agent_message_compress_config.get("length", 1000)

    def start_compress(self):
        """
        启动后台压缩任务
        """
        if not self.compression_task and not self.compression_completed:
            # 使用线程来实现真正的后台压缩
            self.compression_task = threading.Thread(target=self._compress_in_thread, daemon=True)
            self.compression_task.start()
    
    def _compress_in_thread(self):
        """
        在线程中执行压缩逻辑
        """
        try:
            self.is_compressing = True
            print(f"[后台压缩] 开始压缩，原长度: {len(self.content)}")
            
            # 模拟一些压缩处理时间
            time.sleep(0.1)
            
            if self.compress_method == "hard_clip":
                if not self.content:
                    self.compressed_content = ""
                elif len(self.content) > self.compress_length:
                    head = int(self.compress_length * 0.9)
                    tail = int(-1 * self.compress_length * 0.1)
                    self.compressed_content = self.content[:head] + "……" + self.content[tail:]
                    print(f"[压缩] 完成，{len(self.content)} -> {len(self.compressed_content)}")
                else:
                    self.compressed_content = self.content
                    print("[压缩] 内容较短，无需压缩")
            
            elif self.compress_method == "model":
                if not self.content:
                    self.compressed_content = ""
                elif len(self.content) > self.compress_length:
                    compress_prompt = COMPRESS_PROMPT_FORMAT.format(content=self.content, content_length=self.compress_length)
                    messages = [{"role": "user", "content": compress_prompt}]
                    response = model_client.do_chat(messages, self.model)
                    print("response:", response)
                    self.compressed_content = response
                    print(f"[压缩] 完成，{len(self.content)} -> {len(self.compressed_content)}")
                else:
                    self.compressed_content = self.content
                    print("[压缩] 内容较短，无需压缩")
            elif self.compress_method == "no_compress":
                self.compressed_content = self.content
                print("[压缩] 无需压缩")
            
            self.compression_completed = True
            self.is_compressing = False
            
        except Exception as e:
            print(f"[后台压缩] 失败: {e}")
            self.is_compressing = False
            self.compressed_content = self.content  # 失败时使用原内容

    async def get_compressed_content(self) -> str:
        """
        获取压缩后的内容
        智能返回：如果压缩完成则返回压缩内容，否则返回原内容
        
        Returns:
            str: 压缩后的内容或原内容
        """
        print("self.compressed_content:", self.compressed_content)
        if self.compression_completed and self.compressed_content is not None:
            return self.compressed_content
        else:
            return self.content
    
    def get_compression_status(self) -> dict:
        """
        获取压缩状态
        
        Returns:
            dict: 包含压缩状态信息
        """
        return {
            "is_compressing": self.is_compressing,
            "compression_completed": self.compression_completed,
            "has_compressed_content": self.compressed_content is not None,
            "original_length": len(self.content),
            "compressed_length": len(self.compressed_content) if self.compressed_content else 0
        }