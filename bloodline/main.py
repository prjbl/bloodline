from gui import Application
from infrastructure import LoggingManager
from infrastructure.config import Directory
from infrastructure.migration import MigrationPipeline

if __name__ == "__main__":
    LoggingManager.setup_logger()
    Directory.setup_all_dirs()
    MigrationPipeline.setup_meta_files()
    MigrationPipeline.handle_migration_process()
    
    app: Application = Application()
    app.run()