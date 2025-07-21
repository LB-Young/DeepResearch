from abc import ABC, abstractmethod
from typing import List


class BaseMemory(ABC):
    @abstractmethod
    def add_memory(self, messages):
        pass
    