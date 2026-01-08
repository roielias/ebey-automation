"""
Login Page Object Model for eBay
Handles authentication functionality
"""
from typing import Optional
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class LoginPage(BasePage):
    """Page Object for eBay Login/Authentication"""
    
    # Locators
    SIGN_IN_LINK = "a#gh-ug, a:has-text('Sign in')"
    USERNAME_INPUT = "input#userid, input[name='userid']"
    PASSWORD_INPUT = "input#pass, input[name='pass']"
    CONTINUE_BUTTON = "button#signin-continue-btn, button[type='submit']"
    SIGN_IN_BUTTON = "button#sgnBt, button[name='sgnBt']"
    
    # Logged in indicators
    ACCOUNT_MENU = "button#gh-ug, span#gh-ug"
    LOGGED_IN_USERNAME = "span.gh-ug-guest, span.gh-ug"
    
    # Error messages
    ERROR_MESSAGE = "div#errMsg, span.errMsg"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def is_logged_in(self) -> bool:
        """
        Check if user is logged in
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for account menu or username display
            if self.is_visible(self.ACCOUNT_MENU, timeout=3000):
                username_text = self.get_text(self.ACCOUNT_MENU)
                # If it's not "Sign in", user is logged in
                if "sign in" not in username_text.lower():
                    logger.info(f"User is logged in as: {username_text}")
                    return True
            return False
        except Exception as e:
            logger.debug(f"Login check failed: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to eBay account
        
        Core Function: Authentication
        
        Args:
            username: eBay username/email
            password: eBay password
            
        Returns:
            True if login successful, False otherwise
            
        Example:
            login_page.login("user@example.com", "password123")
        """
        logger.info("="*80)
        logger.info("CORE FUNCTION: authenticate/login")
        logger.info(f"Attempting to login with username: {username}")
        logger.info("="*80)
        
        try:
            # Check if already logged in
            if self.is_logged_in():
                logger.info("Already logged in, skipping login")
                return True
            
            # Click Sign In link
            logger.info("Clicking Sign In link")
            self.wait_for_element(self.SIGN_IN_LINK, timeout=5000)
            self.click(self.SIGN_IN_LINK)
            
            # Wait for login page to load
            self.page.wait_for_load_state("networkidle")
            self.take_screenshot("login_page_loaded")
            
            # Enter username
            logger.info("Entering username")
            self.wait_for_element(self.USERNAME_INPUT, timeout=10000)
            self.fill(self.USERNAME_INPUT, username)
            
            # Click Continue (eBay has 2-step login)
            if self.is_visible(self.CONTINUE_BUTTON, timeout=2000):
                logger.info("Clicking Continue button")
                self.click(self.CONTINUE_BUTTON)
                self.page.wait_for_load_state("networkidle")
            
            # Enter password
            logger.info("Entering password")
            self.wait_for_element(self.PASSWORD_INPUT, timeout=10000)
            self.fill(self.PASSWORD_INPUT, password)
            
            # Take screenshot before submitting
            self.take_screenshot("before_login_submit")
            
            # Click Sign In
            logger.info("Clicking Sign In button")
            self.click(self.SIGN_IN_BUTTON)
            
            # Wait for login to complete
            self.page.wait_for_load_state("networkidle")
            
            # Verify login success
            if self.is_logged_in():
                logger.info("✓ Login successful")
                self.take_screenshot("login_success")
                return True
            else:
                # Check for error message
                if self.is_visible(self.ERROR_MESSAGE, timeout=3000):
                    error_text = self.get_text(self.ERROR_MESSAGE)
                    logger.error(f"Login failed: {error_text}")
                else:
                    logger.error("Login failed: Unknown error")
                
                self.take_screenshot("login_failed")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.take_screenshot("login_error")
            return False
    
    def login_as_guest(self) -> bool:
        """
        Continue as guest (no login)
        
        Returns:
            True (always successful for guest mode)
        """
        logger.info("="*80)
        logger.info("CORE FUNCTION: authenticate (Guest Mode)")
        logger.info("Continuing as guest - no authentication required")
        logger.info("="*80)
        
        # For eBay, guest mode means we just don't log in
        # Shopping cart and browsing work without authentication
        logger.info("✓ Guest mode enabled - proceeding without login")
        return True
    
    def logout(self) -> None:
        """
        Logout from eBay account
        """
        try:
            if not self.is_logged_in():
                logger.info("Already logged out")
                return
            
            logger.info("Logging out")
            # Implementation depends on eBay's logout flow
            # Usually involves clicking account menu and selecting logout
            
            # For simplicity, just navigate to logout URL
            logout_url = "https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&logout"
            self.navigate_to(logout_url)
            
            logger.info("Logout completed")
            self.take_screenshot("after_logout")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
