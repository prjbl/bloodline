from webbrowser import open_new_tab

from infrastructure import Directory

class WebManager:
    
    _REPO: str = "prjbl/bloodline"
    _RELEASE_URL: str = f"https://github.com/{_REPO}/releases/latest"
    _API_URL: str = f"https://api.github.com/repos/{_REPO}/releases/latest"
    _HEADERS: dict = {"User-Agent": f"{Directory.get_app_name()} {Directory.get_version()}"}
    
    
    @staticmethod
    def open_hyperlink(url: str) -> None:
        open_new_tab(url)
    
    
    @classmethod
    def get_release_url(cls) -> str:
        return cls._RELEASE_URL
    
    
    @classmethod
    def get_api_url(cls) -> str:
        return cls._API_URL
    
    
    @classmethod
    def get_headers(cls) -> str:
        return cls._HEADERS