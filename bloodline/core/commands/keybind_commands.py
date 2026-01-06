from .base_command import BaseCommand

class KeybindCommands(BaseCommand):
    
    def __init__(self, instances: dict):
        super().__init__(instances)
    
    
    def info(self) -> None:
        self._msg_provider.invoke("This is a list of all keybind commands:", "normal")
        self._msg_provider.invoke(
            "'keybinds list': Lists all hotkeys with their corresponding keybinds\n"
            +"'keybinds config <hotkey>': Changes the keybind of the selected hotkey", "list"
        )
    
    
    def list(self) -> None:
        dict_of_hotkeys: dict = self._hk_manager.get_current_hotkeys()
        
        for hotkey, keybind in dict_of_hotkeys.items():
            self._msg_provider.invoke(f"{hotkey}: {keybind}", "list")
    
    
    def config(self, hotkey: str) -> None:
        self._key_listener.set_new_keybind(hotkey)
        self._key_listener.start_hotkey_config_listener()