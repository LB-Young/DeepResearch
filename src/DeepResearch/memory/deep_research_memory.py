from .base_memory import BaseMemory


class DeepResearchMemory(BaseMemory):
    def __init__(self) -> None:
        """
        self.history : save the history info
        self.memory : save the memory of cur deep research execute info
        self.finished : flag of wheather the deep research last execute info has finished
        """
        self.history = []
        self.memory = []
        self.origin_query = None
        self.finished = False

    def set_origin_query(self, query):
        self.origin_query = query

    def get_origin_query(self):
        return self.origin_query

    def set_history(self, history):
        self.history = history

    def get_history(self):
        return self.history

    def get_finished(self):
        return self.finished

    def add_memory(self, messages):
        if isinstance(messages, list):
            self.memory.extend(messages)
        else:
            self.memory.append(messages)

    def get_query(self):
        if self.memory[-1].role == 'user':
            return [self.memory[-1]]
        else:
            return []

    def compress_memory(self):
        pass
        
    def get_deep_search_memory(self):
        return self.memory
    
    def clear(self):
        self.memory = []
        self.history = []
        self.finished = False
        
