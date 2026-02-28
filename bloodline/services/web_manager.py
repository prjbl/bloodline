from webbrowser import open_new_tab

from infrastructure.constants import Metadata

class WebManager:
    
    GITHUB_HEADERS: dict = {"User-Agent": f"{Metadata.APP_NAME} {Metadata.VERSION}"}
    
    
    @staticmethod
    def open_hyperlink(url: str) -> None:
        open_new_tab(url)