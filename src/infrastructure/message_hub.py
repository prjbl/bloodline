from __future__ import annotations

from queue import Queue
from typing import Callable

class MessageHub:
    
    _instance: MessageHub | None = None
    _print_output: Callable[[str, str, str | None], None] | None
    _buffer: Queue
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._print_output = None
            cls._instance._buffer = Queue()
        return cls._instance
    
    
    def link_callback(self, callback_method: Callable[[str, str, str | None], None]) -> None:
        self._print_output = callback_method
        
        while not self._buffer.empty():
            text, text_type, optional_arg = self._buffer.get_nowait()
            self._print_output(text, text_type, optional_arg)
    
    
    def invoke(self, text: str, text_type: str, optional_arg: str | None = None) -> None:
        if self._print_output is None:
            self._buffer.put_nowait((text, text_type, optional_arg))
            return
        
        self._print_output(text, text_type, optional_arg)