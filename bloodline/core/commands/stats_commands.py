from .base_command import BaseInterceptCommand

class StatsCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
    def info(self) -> None:
        self._console.print_output("This is a list of all stat commands:", "normal")
        self._console.print_output(
            "'stats list bosses [-a] [-s deaths|time -o desc|asc]': Lists bosses by the selected filters. By default all bosses will be listed in the order they were added\n"
            +"'stats list games [-s deaths|time -o desc|asc]': Lists all games by the selected filters. By default the games will be listed in the order they were added\n"
            +"'stats save': Saves the tracking values to the selected boss in the save file\n"
            +"'stats export': Exports all bosses with their corresponding values from the selected game to a .csv file", "list"
        )
    
    
    def list_bosses_by() -> bool:
        pass
    
    
    def list_all_bosses_by() -> None:
        pass
    
    
    def list_games_by() -> None:
        pass
    
    
    def save() -> bool:
        pass
    
    
    def export_by() -> bool:
        pass