from __future__ import annotations

from typing import Callable

class MessageHub:
    
    _instance: MessageHub | None = None
    _callback_method: Callable[[str, str], None] | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    @classmethod
    def link_callback(cls, callback_method: Callable[[str, str], None]) -> None:
        cls._callback_method = callback_method
    
    
    @classmethod
    def invoke(cls, text: str, text_type: str) -> None:
        cls._callback_method(text, text_type)