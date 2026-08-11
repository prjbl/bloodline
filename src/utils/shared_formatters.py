
class SharedFormatter:
    
    @staticmethod
    def format_deaths(deaths: int | float | None, prefix: bool = True) -> str:
        if deaths is None:
            return "D N/A" if prefix else "N/A"
        return f"D {deaths:,}" if prefix else f"{deaths:,}"
    
    
    @staticmethod
    def format_time(time: int | None) -> str:
        if time is None:
            return "N/A"
        
        seconds: int = time % 60
        minutes: int = int(time / 60) % 60
        hours: int = int(time / 3600)
        return f"{hours:02}:{minutes:02}:{seconds:02}"