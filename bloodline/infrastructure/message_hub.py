from __future__ import annotations

from queue import Queue
from typing import Callable

class MessageHub:
    
    _instance: MessageHub | None = None
    _print_output: Callable[[str, str, str | None], None] | None = None
    _buffer: Queue = Queue()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    @classmethod
    def link_callback(cls, callback_method: Callable[[str, str, str | None], None]) -> None:
        cls._print_output = callback_method
        
        while not cls._buffer.empty():
            text, text_type, optional_arg = cls._buffer.get_nowait()
            cls._print_output(text, text_type, optional_arg)
    
    
    @classmethod
    def invoke(cls, text: str, text_type: str, optional_arg: str | None = None) -> None:
        if cls._print_output is None:
            cls._buffer.put_nowait((text, text_type, optional_arg))
            return
        
        cls._print_output(text, text_type, optional_arg)