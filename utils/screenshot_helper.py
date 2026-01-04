"""
Screenshot utility for capturing page states
"""
import os
from datetime import datetime
from playwright.sync_api import Page
from config.config import Config
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class ScreenshotHelper:
    """Helper class for taking and managing screenshots"""
    
    @staticmethod
    def take_screenshot(page: Page, name: str, full_page: bool = True) -> str:
        """
        Take a screenshot of the current page
        
        Args:
            page: Playwright page object
            name: Name for the screenshot file
            full_page: Whether to capture full page or just viewport
            
        Returns:
            Path to the saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        
        try:
            page.screenshot(path=filepath, full_page=full_page)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise
    
    @staticmethod
    def take_element_screenshot(page: Page, selector: str, name: str) -> str:
        """
        Take a screenshot of a specific element
        
        Args:
            page: Playwright page object
            selector: CSS selector or XPath of the element
            name: Name for the screenshot file
            
        Returns:
            Path to the saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_element_{timestamp}.png"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        
        try:
            element = page.locator(selector)
            element.screenshot(path=filepath)
            logger.info(f"Element screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take element screenshot: {e}")
            raise
