from re import compile, fullmatch

class ValidationPattern:
    
    @staticmethod
    def validate_hex_pattern(color: str) -> bool:
        valid_hex_pattern: str = compile(r"#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})")
        
        if not fullmatch(valid_hex_pattern, color):
            return False
        return True
    
    @staticmethod
    def validate_geometry_pattern(geometry: str) -> bool:
        valid_geometry_pattern: str = compile(r"(\d+x\d+)|(\d+x\d+)\+(\-)?\d+\+(\-)?\d+")
        
        if not fullmatch(valid_geometry_pattern, geometry):
            return False
        return True
    
    @staticmethod
    def validate_position_pattern(position: str) -> bool:
        valid_position_pattern: str = compile(r"^\+(\-)?\d+\+(\-)?\d+$")
        
        if not fullmatch(valid_position_pattern, position):
            return False
        return True