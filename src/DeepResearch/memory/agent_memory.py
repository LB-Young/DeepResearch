from typing import Union, List
import threading
from .base_memory import BaseMemory
from src.DeepResearch.message import HistoryMessage
from src.DeepResearch.message import AgentMessage

class AgentMemory(BaseMemory):
    def __init__(self) -> None:
        """
        self.history : save the history info
        self.memory : save the memory of cur agent execute info
        self.finished : flag of wheather the last execute info has finished
        """
        self.history = []
        self.deep_research_memory = []
        self.memory = []
        self.finished = False
        self._compression_lock = threading.Lock()  # 用于保护压缩操作的线程锁

    async def set_history(self, history):
        self.history = history

    async def get_history(self):
        return self.history

    async def set_deep_research_memory(self, memory):
        self.deep_research_memory = memory
    
    async def get_deep_research_memory(self):
        return self.deep_research_memory

    async def get_finished(self):
        return self.finished

    async def add_memory(self, messages: Union[AgentMessage, List[AgentMessage]]):
        if isinstance(messages, list):
            self.memory.extend(messages)
        else:
            self.memory.append(messages)
        
    async def compress_memory(self):
        pass

    async def get_memory(self):
        return self.memory

    async def get_model_messages(self):
        all_history_messages = []
        # history roles: [user, assistant]
        for item in self.history:
            if isinstance(item, dict):
                all_history_messages.append(item)
            elif isinstance(item, HistoryMessage):
                content = await item.get_compressed_content()
                role = await item.get_role()
                all_history_messages.append({"role": role, "content":content})

        all_deep_research_messages = []
        for item in self.deep_research_memory:
            if isinstance(item, dict):
                all_deep_research_messages.append(item)
            elif isinstance(item, AgentMessage):
                content = await item.get_compressed_content()
                role = await item.get_role()
                all_deep_research_messages.append({"role": role, "content":content})
        
        # memory roles: [user, assistant, user_function, xxx_agent]
        all_messages = []
        for item in self.memory:
            if isinstance(item, dict):
                all_messages.append(item)
            elif isinstance(item, AgentMessage):
                content = await item.get_compressed_content()
                role = await item.get_role()
                if role.startswith("user"):
                    role = "user"
                else:
                    role = "assistant"
                all_messages.append({"role": role, "content":content})
        return all_history_messages, all_deep_research_messages, all_messages
    
    async def clear(self):
        self.history = []
        self.deep_research_memory = []
        self.memory = []
        self.finished = False
        self.full_response_content = ""

    async def add_response_content(self, content):
        self.full_response_content = content

    async def get_full_response_content(self):
        return getattr(self, 'full_response_content', "")
