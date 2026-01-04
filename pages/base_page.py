"""
Base Page Object Model
Provides common functionality for all page objects
"""
from typing import Optional
from playwright.sync_api import Page, Locator, expect
from config.config import Config
from utils.logger import Logger
from utils.screenshot_helper import ScreenshotHelper

logger = Logger.get_logger(__name__)


class BasePage:
    """Base class for all Page Object Models"""
    
    def __init__(self, page: Page):
        """
        Initialize base page
        
        Args:
            page: Playwright page object
        """
        self.page = page
        self.screenshot_helper = ScreenshotHelper()
    
    def navigate_to(self, url: str) -> None:
        """
        Navigate to a URL
        
        Args:
            url: URL to navigate to
        """
        logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle", timeout=Config.NAVIGATION_TIMEOUT)
    
    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Click an element
        
        Args:
            selector: Element selector
            timeout: Optional timeout in milliseconds
        """
        logger.info(f"Clicking element: {selector}")
        locator = self.page.locator(selector)
        locator.click(timeout=timeout or Config.DEFAULT_TIMEOUT)
    
    def fill(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """
        Fill an input field
        
        Args:
            selector: Input field selector
            text: Text to fill
            timeout: Optional timeout in milliseconds
        """
        logger.info(f"Filling field {selector} with: {text}")
        locator = self.page.locator(selector)
        locator.fill(text, timeout=timeout or Config.DEFAULT_TIMEOUT)
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        Get text from an element
        
        Args:
            selector: Element selector
            timeout: Optional timeout in milliseconds
            
        Returns:
            Text content of the element
        """
        logger.info(f"Getting text from: {selector}")
        locator = self.page.locator(selector)
        return locator.inner_text(timeout=timeout or Config.DEFAULT_TIMEOUT)
    
    def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Get attribute value from an element
        
        Args:
            selector: Element selector
            attribute: Attribute name
            timeout: Optional timeout in milliseconds
            
        Returns:
            Attribute value or None
        """
        logger.info(f"Getting attribute '{attribute}' from: {selector}")
        locator = self.page.locator(selector)
        return locator.get_attribute(attribute, timeout=timeout or Config.DEFAULT_TIMEOUT)
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> None:
        """
        Wait for an element to be in a specific state
        
        Args:
            selector: Element selector
            state: Element state (visible, hidden, attached, detached)
            timeout: Optional timeout in milliseconds
        """
        logger.info(f"Waiting for element {selector} to be {state}")
        locator = self.page.locator(selector)
        locator.wait_for(state=state, timeout=timeout or Config.DEFAULT_TIMEOUT)
    
    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is visible
        
        Args:
            selector: Element selector
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if visible, False otherwise
        """
        try:
            locator = self.page.locator(selector)
            locator.wait_for(state="visible", timeout=timeout or 5000)
            return True
        except Exception:
            return False
    
    def get_elements(self, selector: str) -> list:
        """
        Get all elements matching selector
        
        Args:
            selector: Element selector
            
        Returns:
            List of Playwright Locator objects
        """
        return self.page.locator(selector).all()
    
    def scroll_to_element(self, selector: str) -> None:
        """
        Scroll to an element
        
        Args:
            selector: Element selector
        """
        logger.info(f"Scrolling to element: {selector}")
        locator = self.page.locator(selector)
        locator.scroll_into_view_if_needed()
    
    def take_screenshot(self, name: str) -> str:
        """
        Take a screenshot of the current page
        
        Args:
            name: Screenshot name
            
        Returns:
            Path to the screenshot
        """
        return self.screenshot_helper.take_screenshot(self.page, name)
    
    def select_dropdown_option(self, selector: str, value: str = None, label: str = None, index: int = None) -> None:
        """
        Select an option from a dropdown
        
        Args:
            selector: Dropdown selector
            value: Option value
            label: Option label
            index: Option index
        """
        logger.info(f"Selecting dropdown option from {selector}")
        locator = self.page.locator(selector)
        
        if value:
            locator.select_option(value=value)
        elif label:
            locator.select_option(label=label)
        elif index is not None:
            locator.select_option(index=index)
        else:
            raise ValueError("Must provide value, label, or index")
    
    def press_key(self, selector: str, key: str) -> None:
        """
        Press a keyboard key on an element
        
        Args:
            selector: Element selector
            key: Key to press (e.g., 'Enter', 'Escape')
        """
        logger.info(f"Pressing key '{key}' on element: {selector}")
        locator = self.page.locator(selector)
        locator.press(key)
    
    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> None:
        """
        Wait for URL to match pattern
        
        Args:
            url_pattern: URL pattern to match
            timeout: Optional timeout in milliseconds
        """
        logger.info(f"Waiting for URL to match: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout or Config.DEFAULT_TIMEOUT)
    
    def get_current_url(self) -> str:
        """
        Get current page URL
        
        Returns:
            Current URL
        """
        return self.page.url
