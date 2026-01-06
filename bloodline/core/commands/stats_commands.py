from pathlib import Path
from typing import List, Callable

from .base_command import BaseInterceptCommand
from file_io import CsvFileOperations

class StatsCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
    _AVG_LABEL: str = "AVG"
    _SUM_LABEL: str = "SUM"
    
    
    def info(self) -> None:
        self._msg_provider.invoke("This is a list of all stat commands:", "normal")
        self._msg_provider.invoke(
            "'stats list bosses [-a] [-s deaths|time -o desc|asc]': Lists bosses by the selected filters. By default all bosses will be listed in the order they were added\n"
            +"'stats list games [-s deaths|time -o desc|asc]': Lists all games by the selected filters. By default the games will be listed in the order they were added\n"
            +"'stats save': Saves the tracking values to the selected boss in the save file\n"
            +"'stats export': Exports all bosses with their corresponding values from the selected game to a .csv file", "list"
        )
    
    
    def list_bosses_by(self, sort_filter: str, order_filter: str) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"game title\"> from which you want all bosses selected from <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("single")
        
        if not pattern_result:
            return False
        
        game_title: str = pattern_result[0]
        list_of_bosses: List[tuple] = self._save_file.get_bosses_from_game_by(game_title, sort_filter, order_filter)
        
        if not list_of_bosses:
            return False
        
        max_meta_len: int = self._get_max_len(
            iterable=list_of_bosses,
            lambda_expression=lambda boss: boss[0]
        )
        max_deaths_len: int = self._get_max_len(
            iterable=list_of_bosses,
            lambda_expression=lambda deaths: self._format_deaths(deaths[1])
        )
        
        for boss in list_of_bosses:
            formatted_boss_meta: str = self._get_formatted_meta(boss[0], max_meta_len)
            formatted_boss_stats: str = self._get_formatted_stats(boss[1], boss[2], max_deaths_len)
            self._msg_provider.invoke(f"{formatted_boss_meta}  {formatted_boss_stats}", "list")
        
        game_avg: List[tuple] = self._save_file.get_game_avg(game_title)
        game_sum: List[tuple] = self._save_file.get_game_sum(game_title)
        self._msg_provider.invoke(self._get_total_summary_block(game_avg, game_sum), "list")
        return False
    
    
    def list_all_bosses_by(self, sort_filter: str, order_filter: str) -> None:
        list_of_bosses: List[tuple] = self._save_file.get_all_bosses_by(sort_filter, order_filter)
        
        if not list_of_bosses:
            return
        
        max_meta_len: int = self._get_max_len(
            iterable=list_of_bosses,
            lambda_expression=lambda boss: f"{boss[0]} ({boss[1]})"
        )
        max_deaths_len: int = self._get_max_len(
            iterable=list_of_bosses,
            lambda_expression=lambda deaths: self._format_deaths(deaths[2])
        )
        
        for boss in list_of_bosses:
            formatted_boss_meta: str = self._get_formatted_meta(boss[0], max_meta_len, boss[1])
            formatted_boss_stats: str = self._get_formatted_stats(boss[2], boss[3], max_deaths_len)
            self._msg_provider.invoke(f"{formatted_boss_meta}  {formatted_boss_stats}", "list")
        
        all_bosses_avg: List[tuple] = self._save_file.get_all_bosses_avg()
        all_bosses_sum: List[tuple] = self._save_file.get_all_bosses_sum()
        self._msg_provider.invoke(self._get_total_summary_block(all_bosses_avg, all_bosses_sum), "list")
    
    
    def list_games_by(self, sort_filter: str, order_filter: str) -> None:
        list_of_games: List[tuple] = self._save_file.get_all_games_by(sort_filter, order_filter)
        
        if not list_of_games:
            return
        
        max_meta_len: int = self._get_max_len(
            iterable=list_of_games,
            lambda_expression=lambda game: game[0]
        )
        max_deaths_len: int = self._get_max_len(
            iterable=list_of_games,
            lambda_expression=lambda deaths: self._format_deaths(deaths[1])
        )
        
        for game in list_of_games:
            formatted_game_meta: str = self._get_formatted_meta(game[0], max_meta_len)
            formatted_game_stats: str = self._get_formatted_stats(game[1], game[2], max_deaths_len)
            self._msg_provider.invoke(f"{formatted_game_meta}  {formatted_game_stats}", "list")
        
        all_games_avg: List[tuple] = self._save_file.get_all_games_avg()
        all_games_sum: List[tuple] = self._save_file.get_all_games_sum()
        self._msg_provider.invoke(self._get_total_summary_block(all_games_avg, all_games_sum), "list")
    
    
    def save(self) -> bool:
        if self._counter.get_is_none() and self._timer.get_is_none():
            self._msg_provider.invoke("There are no values to be saved. Make sure to start a tracking session and try saving again afterwards", "invalid")
            return False
        
        active_process: bool | None = self._process_count_value()
        if active_process is None:
            return False
        if active_process:
            return True
        
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"boss name\", \"game title\"> of the boss you want the stats safed to <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("double")
        
        if not pattern_result:
            return False
        
        update_successful: bool = self._save_file.update_boss(
            boss_name=pattern_result[0],
            game_title=pattern_result[1],
            deaths=self._counter.get_count(),
            required_time=self._timer.get_end_time()
        )
        if update_successful:
            self._counter.reset(hard_reset=True)
            self._timer.reset(hard_reset=True)
        return False
    
    
    def export_by(self, sort_filter: str, order_filter: str) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"game title\"> you want the stats exported from <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("single")
        
        if not pattern_result:
            return False
        
        game_title: str = pattern_result[0]
        game_data: List[tuple] = self._save_file.get_bosses_from_game_by(game_title, sort_filter, order_filter)
        
        if not game_data:
            return False
        
        headers: List[str] = [header[0] for header in self._save_file.get_boss_table_description()]
        dst_file_path: Path = Path(f"{game_title.lower().replace(" ", "_")}.csv")
        CsvFileOperations.perform_save(
            dst_file_path=dst_file_path,
            headers=headers,
            data=game_data
        )
        return False
    
    
    # formatting helper methods below
    
    @staticmethod
    def _get_formatted_meta(primary_info: str, max_meta_len: int, secondary_info: str | None = None) -> str:
        if secondary_info is None:
            return primary_info.ljust(max_meta_len)
        return f"{primary_info} ({secondary_info})".ljust(max_meta_len)
    
    
    def _get_formatted_stats(self, deaths: int | None, time: int | None, max_deaths_len: int) -> str:
        # uses unicode non-breaking space so word wrap does not split values in half
        return f"{self._format_deaths(deaths).ljust(max_deaths_len)}  {self._format_time(time)}".replace(" ", "\u00A0")
    
    
    def _get_total_summary_block(self, avg_value: List[tuple], sum_value: List[tuple]) -> str:
        total_summary_stats: List[tuple] = [*avg_value, *sum_value]
        max_deaths_len: int = self._get_max_len(
            iterable=total_summary_stats,
            lambda_expression=lambda deaths: self._format_deaths(deaths[0])
        )
        formatted_avg_stats: str = self._get_formatted_summary_stats(StatsCommands._AVG_LABEL, avg_value, max_deaths_len)
        formatted_sum_stats: str = self._get_formatted_summary_stats(StatsCommands._SUM_LABEL, sum_value, max_deaths_len)
        return f"\n{formatted_avg_stats}\n{formatted_sum_stats}"
    
    
    def _get_formatted_summary_stats(self, label: str, value: List[tuple], max_deaths_len: int) -> str:
        formatted_deaths: str = self._format_deaths(value[0][0])
        formatted_time: str = self._format_time(value[0][1])
        return f"{label}  " + f"{formatted_deaths.ljust(max_deaths_len)}  {formatted_time}".replace(" ", "\u00A0")
    
    
    @staticmethod
    def _get_max_len(iterable: List[tuple], lambda_expression: Callable[..., str] | str) -> int:
        return max(len(lambda_expression(item)) for item in iterable)
    
    
    @staticmethod
    def _format_deaths(deaths: int | float | None) -> str:
        if deaths is None:
            return "D N/A"
        return f"D {deaths:,}"
    
    
    @staticmethod
    def _format_time(time: int | None) -> str:
        if time is None:
            return "N/A"
        
        seconds: int = time % 60
        minutes: int = int(time / 60) % 60
        hours: int = int(time / 3600)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    
    # helper methods below
    
    def _process_count_value(self) -> bool | None:
        if not self._counter.get_is_none() or self._counter.get_question_answered():
            return False
        
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter <y[es]|n[o]> if you tracked deaths <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("yes_no")
        
        if not pattern_result:
            return None
        
        decision: str = pattern_result[0]
        if self._check_yes_confirmation(decision):
            self._counter.convert_none_to_zero()
        
        self._counter.set_question_answered()
        self.reset_step_count()
        return False
    
    
    @staticmethod
    def _check_yes_confirmation(decision: str) -> bool:
        return decision.casefold() == "y" or decision.casefold() == "yes"