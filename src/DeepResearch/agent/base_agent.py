from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Iterator, Union


class BaseAgent(ABC):
    @abstractmethod
    async def step(self, inputs: Dict[str, Any], properties: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        pass