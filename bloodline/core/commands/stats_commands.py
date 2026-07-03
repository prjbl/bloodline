from typing import List, Callable

from .base_command import BaseInterceptCommand
from file_io import CsvFileOperations
from infrastructure.config import Directory
from utils import SharedFormatter

class StatsCommands(BaseInterceptCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
        self._key_listener.link_autosave_callback(lambda: self._console.add_mainloop_task(50, self._autosave))
        
        self._context: dict = {}
    
    
    _AVG_LABEL: str = "AVG"
    _SUM_LABEL: str = "SUM"
    
    
    def info(self) -> None:
        self._msg_provider.invoke("This is a list of all stats commands:", "normal")
        self._msg_provider.invoke(
            "'stats list bosses [-a] [-s deaths|time -o desc|asc]': Lists bosses by the selected filters. By default all bosses will be listed in the order they were added\n"
            "'stats list games [-s deaths|time -o desc|asc]': Lists all games by the selected filters. By default the games will be listed in the order they were added\n"
            "'stats save': Saves the tracking values to the selected boss in the save file\n"
            "'stats merge': Combines the values of two selected bosses into one\n"
            "'stats export': Exports all bosses with their corresponding values from the selected game to a .csv file", "list"
        )
    
    
    def list_bosses_by(self, sort_filter: str, order_filter: str) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"game title\"> from which you want all bosses listed from <...>", "normal")
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
            lambda_expression=lambda deaths: SharedFormatter.format_deaths(deaths[1])
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
            lambda_expression=lambda deaths: SharedFormatter.format_deaths(deaths[2])
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
            lambda_expression=lambda deaths: SharedFormatter.format_deaths(deaths[1])
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
            self._msg_provider.invoke("Please enter the <\"boss name\", \"game title\"> of the boss you want the stats saved to <...>", "normal")
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
    
    
    def _autosave(self) -> None:
        if self._counter.get_is_none() and self._timer.get_is_none():
            self._msg_provider.invoke("There are no values to be saved. Make sure to start tracking and try saving again afterwards", "invalid")
            return False
        
        update_successful: bool = self._save_file.update_boss(
            boss_name=self._shared_context["boss_name"],
            game_title=self._shared_context["game_title"],
            deaths=self._counter.get_count(),
            required_time=self._timer.get_end_time()
        )
        if update_successful:
            self._counter.reset(hard_reset=True)
            self._timer.reset(hard_reset=True)
    
    
    def merge(self) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"boss name 1\", \"game title 1\" + \"boss name 2\", \"game title 2\"> of the bosses you want to merge <...>", "normal")
            return True
        
        if self._current_step == 1:
            pattern_result: List[str] = self._get_input_pattern_result("double_double")
            
            if not pattern_result:
                return False
            
            self._context = {
                "first_boss_name": pattern_result[0],
                "first_game_title": pattern_result[1],
                "second_boss_name": pattern_result[2],
                "second_game_title": pattern_result[3]
            }
            
            self._msg_provider.invoke("Please enter the <\"boss name\", \"game title\"> of the merged boss <...>", "normal")
            return True
        
        pattern_result: List[str] = self._get_input_pattern_result("double")
        
        if not pattern_result:
            return False
        
        self._save_file.merge_bosses(
            bosses_to_merge=[
                (self._context["first_boss_name"], self._context["first_game_title"]),
                (self._context["second_boss_name"], self._context["second_game_title"])
            ],
            new_boss_name=pattern_result[0],
            new_game_title=pattern_result[1]
        )
        return False
    
    
    def export_by(self, sort_filter: str, order_filter: str) -> bool:
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter the <\"game title\"> you want the stats exported from <...>", "normal")
            return True
        
        if self._current_step == 1:
            pattern_result: List[str] = self._get_input_pattern_result("single")
            
            if not pattern_result:
                return False
            
            game_title: str = pattern_result[0]
            game_data: List[tuple] = self._save_file.get_bosses_from_game_by(game_title, sort_filter, order_filter)
            
            if not game_data:
                return False
            
            self._context = {
                "file_name": (file_name := f"{game_title.lower().replace(" ", "_")}.csv"),
                "dst_file_path": str(Directory.EXPORT_PATH / file_name),
                "headers": [header[0] for header in self._save_file.get_boss_table_description()],
                "game_data": self._get_formated_csv_data(game_title, game_data)
            }
        
        active_process: bool | None = self._process_override_protection(self._context, self._current_step)
        if active_process is None:
            self._context.clear()
            return False
        if active_process:
            return True
        
        Directory.create_export_dir()
        try:
            CsvFileOperations.perform_save(
                dst_file_path=self._context["dst_file_path"],
                headers=self._context["headers"],
                data=self._context["game_data"]
            )
            self._msg_provider.invoke(f"The data was successfully written to the file \"{self._context["file_name"]}\"", "success")
        except PermissionError:
            self._msg_provider.invoke(f"The data could not be written because the file \"{self._context["file_name"]}\" is currently open", "invalid")
        
        self._context.clear()
        return False
    
    
    # formatting helper methods below
    
    @staticmethod
    def _get_formatted_meta(primary_info: str, max_meta_len: int, secondary_info: str | None = None) -> str:
        if secondary_info is None:
            return primary_info.ljust(max_meta_len)
        return f"{primary_info} ({secondary_info})".ljust(max_meta_len)
    
    
    def _get_formatted_stats(self, deaths: int | None, time: int | None, max_deaths_len: int) -> str:
        # uses unicode non-breaking space so word wrap does not split values in half
        return f"{SharedFormatter.format_deaths(deaths).ljust(max_deaths_len)}  {SharedFormatter.format_time(time)}".replace(" ", "\u00A0")
    
    
    def _get_total_summary_block(self, avg_value: List[tuple], sum_value: List[tuple]) -> str:
        total_summary_stats: List[tuple] = [*avg_value, *sum_value]
        max_deaths_len: int = self._get_max_len(
            iterable=total_summary_stats,
            lambda_expression=lambda deaths: SharedFormatter.format_deaths(deaths[0])
        )
        formatted_avg_stats: str = self._get_formatted_summary_stats(StatsCommands._AVG_LABEL, avg_value, max_deaths_len)
        formatted_sum_stats: str = self._get_formatted_summary_stats(StatsCommands._SUM_LABEL, sum_value, max_deaths_len)
        return f"\n{formatted_avg_stats}\n{formatted_sum_stats}"
    
    
    def _get_formatted_summary_stats(self, label: str, value: List[tuple], max_deaths_len: int) -> str:
        formatted_deaths: str = SharedFormatter.format_deaths(value[0][0])
        formatted_time: str = SharedFormatter.format_time(value[0][1])
        return f"{label}  " + f"{formatted_deaths.ljust(max_deaths_len)}  {formatted_time}".replace(" ", "\u00A0")
    
    
    def _get_formated_csv_data(self, game_title: str, game_data: List[tuple]) -> None:
        for index, boss in enumerate(game_data):
            name, deaths, time = boss
            game_data[index] = (name, SharedFormatter.format_deaths(deaths, prefix=False), SharedFormatter.format_time(time))
            
        game_avg: tuple = self._save_file.get_game_avg(game_title)[0]
        game_sum: tuple = self._save_file.get_game_sum(game_title)[0]
            
        game_data[0] = game_data[0] + ("", StatsCommands._AVG_LABEL, SharedFormatter.format_deaths(game_avg[0]), SharedFormatter.format_time(game_avg[1]))
        game_data[1] = game_data[1] + ("", StatsCommands._SUM_LABEL, SharedFormatter.format_deaths(game_sum[0]), SharedFormatter.format_time(game_sum[1]))
        return game_data
    
    
    @staticmethod
    def _get_max_len(iterable: List[tuple], lambda_expression: Callable[..., str] | str) -> int:
        return max(len(lambda_expression(item)) for item in iterable)
    
    
    # helper methods below
    
    def _process_count_value(self) -> bool | None:
        if not self._counter.get_is_none() or self._counter.get_question_answered():
            return False
        
        if self._current_step == 0:
            self._msg_provider.invoke("Please enter <y[es]|n[o]> if you tracked the deaths <...>", "normal")
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