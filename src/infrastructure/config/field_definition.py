from typing import Any

class FieldDef:
    
    def __init__(self, alias: str, default: Any):
        self._alias: str = alias
        self._default: Any = default
    
    
    @property
    def alias(self) -> str:
        return self._alias
    
    
    @property
    def default(self) -> Any:
        if callable(self._default):
            return self._default()
        return self._default