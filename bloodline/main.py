#!/bin/bash

from logging import getLogger

from gui import Application
from infrastructure import EventLogger
from infrastructure.config import Directory, Metadata
from infrastructure.migration import MigrationPipeline

if __name__ == "__main__":
    Directory.setup_all_dirs()
    EventLogger.setup_logger()
    
    getLogger(__name__).info(f"{Metadata.APP_NAME} started (v{Metadata.VERSION})")
    
    MigrationPipeline.setup_meta_files()
    MigrationPipeline.handle_migration_process()
    
    app: Application = Application()
    app.run()