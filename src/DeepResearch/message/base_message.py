from typing import Dict, Any, Optional, Iterator, Union
from abc import ABC, abstractmethod

class BaseMessage:
    role: str
    content: str
    message_type: str
    message_from: str
    message_to: str
