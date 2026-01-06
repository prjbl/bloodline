from __future__ import annotations

from queue import Queue
from typing import Callable

class MessageHub:
    
    _instance: MessageHub | None = None
    _callback_method: Callable[[str, str], None] | None = None
    _buffer: Queue = Queue()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    @classmethod
    def link_callback(cls, callback_method: Callable[[str, str], None]) -> None:
        cls._callback_method = callback_method
        
        while not cls._buffer.empty():
            text, text_type = cls._buffer.get_nowait()
            cls._callback_method(text, text_type)
    
    
    @classmethod
    def invoke(cls, text: str, text_type: str) -> None:
        if cls._callback_method is None:
            cls._buffer.put_nowait((text, text_type))
            return
        
        cls._callback_method(text, text_type)