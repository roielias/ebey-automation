"""
Configuration settings for the test automation framework
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    
    # Application URLs
    BASE_URL = os.getenv('BASE_URL', 'https://www.ebay.com')
    
    # Browser settings
    BROWSER = os.getenv('BROWSER', 'chromium')  # chromium, firefox, webkit
    HEADLESS = os.getenv('HEADLESS', 'False').lower() == 'true'
    
    # Timeouts (in milliseconds)
    DEFAULT_TIMEOUT = int(os.getenv('TIMEOUT', '30000'))
    NAVIGATION_TIMEOUT = 60000
    
    # Screenshot settings
    SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'True').lower() == 'true'
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'screenshots')
    
    # Reports
    REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    ALLURE_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'allure-results')
    
    # Test data
    TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    @staticmethod
    def ensure_directories():
        """Ensure all required directories exist"""
        directories = [
            Config.SCREENSHOT_DIR,
            Config.REPORT_DIR,
            Config.ALLURE_RESULTS_DIR,
            Config.TEST_DATA_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
