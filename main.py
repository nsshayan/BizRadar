#!/usr/bin/env python3
"""
BizRadar - Main Application Entry Point

This is the main entry point for the BizRadar business monitoring application.
"""

import os
import sys
import flet as ft
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bizradar.gui.main_app import BizRadarApp
from bizradar.utils.config import Config
from bizradar.utils.database import DatabaseManager

def main(page: ft.Page):
    """Main application entry point for Flet."""
    # Load environment variables
    load_dotenv()
    
    # Initialize configuration
    config = Config()
    
    # Initialize database
    db_manager = DatabaseManager(config.database_path)
    db_manager.initialize_database()
    
    # Create and run the main application
    app = BizRadarApp(page, config, db_manager)
    app.build()

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Run the Flet application
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080)
