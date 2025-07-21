from base_memory import BaseMemory


class AgentMemory(BaseMemory):
    def __init__(self) -> None:
        self.memory = []
        self.compressed_memory = []

    def add_memory(self, messages):
        self.memory.extend(messages)
        self.compressed_memory.extend(messages)

    def compress_memory(self):
        self.compressed_memory = self.memory
        
    def get_memory(self):
        return self.compressed_memory
    
    def clear_memory(self):
        self.memory = []
        self.compressed_memory = []
