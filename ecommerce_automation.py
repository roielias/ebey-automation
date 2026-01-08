"""
E-commerce Automation Service
Main service class implementing core automation functions
"""
from typing import List, Optional
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from config.config import Config
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class EcommerceAutomation:
    """
    Main automation service implementing core e2e functions
    Following Single Responsibility Principle and OOP best practices
    """
    
    def __init__(self, page: Page, auto_authenticate: bool = True):
        """
        Initialize automation service
        
        Args:
            page: Playwright page instance
            auto_authenticate: Whether to automatically authenticate as guest
        """
        self.page = page
        self.login_page = LoginPage(page)
        self.search_page = SearchPage(page)
        self.product_page = ProductPage(page)
        self.cart_page = CartPage(page)
        
        # Navigate to base URL
        logger.info(f"Initializing E-commerce Automation for {Config.BASE_URL}")
        self.page.goto(Config.BASE_URL)
        self.page.wait_for_load_state("networkidle")
        
        # Authenticate if requested
        if auto_authenticate:
            self.authenticate()
    
    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Authenticate user (login or guest mode)
        
        Core Function 0: Authentication
        
        Args:
            username: Optional username for login. If None, uses guest mode
            password: Optional password for login
            
        Returns:
            True if authentication successful
            
        Example:
            # Guest mode (default)
            automation.authenticate()
            
            # Login with credentials
            automation.authenticate("user@example.com", "password123")
        """
        logger.info("="*80)
        logger.info("CORE FUNCTION 0: authenticate")
        logger.info("="*80)
        
        if username and password:
            # Login with credentials
            success = self.login_page.login(username, password)
            if success:
                logger.info("✓ Authentication successful (logged in)")
            else:
                logger.warning("✗ Authentication failed - continuing as guest")
                success = self.login_page.login_as_guest()
        else:
            # Guest mode
            success = self.login_page.login_as_guest()
        
        logger.info("="*80)
        return success
    
    def search_items_by_name_under_price(
        self, 
        query: str, 
        max_price: float, 
        limit: int = 5
    ) -> List[str]:
        """
        Search for items by name and return URLs of items under max price.
        Handles pagination if needed.
        
        Core Function 1: Search with price filtering
        
        Args:
            query: Search query string
            max_price: Maximum price threshold
            limit: Maximum number of items to return (default: 5)
            
        Returns:
            List of item URLs (up to limit) that meet the price criteria
            
        Example:
            urls = automation.search_items_by_name_under_price("shoes", 220, 5)
        """
        logger.info("="*80)
        logger.info(f"CORE FUNCTION 1: search_items_by_name_under_price")
        logger.info(f"Query: '{query}', Max Price: ${max_price}, Limit: {limit}")
        logger.info("="*80)
        
        urls = self.search_page.search_items_by_name_under_price(query, max_price, limit)
        
        logger.info(f"Search completed: Found {len(urls)} items")
        for i, url in enumerate(urls, 1):
            logger.info(f"  {i}. {url}")
        
        return urls
    
    def add_items_to_cart(self, urls: List[str]) -> None:
        """
        Add items to cart from a list of URLs.
        Handles variant selection (size, color, etc.) randomly.
        Takes screenshots and logs for each item.
        
        Core Function 2: Add items to cart
        
        Args:
            urls: List of product URLs to add to cart
            
        Example:
            automation.add_items_to_cart(urls)
        """
        logger.info("="*80)
        logger.info(f"CORE FUNCTION 2: add_items_to_cart")
        logger.info(f"Adding {len(urls)} items to cart")
        logger.info("="*80)
        
        successful_additions = 0
        failed_additions = 0
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"\n--- Processing item {i}/{len(urls)} ---")
                logger.info(f"URL: {url}")
                
                # Open product page
                if self.product_page.open_product_page(url):
                    # Get product info
                    product_title = self.product_page.get_product_title()
                    product_price = self.product_page.get_product_price()
                    
                    logger.info(f"Product: {product_title}")
                    logger.info(f"Price: {product_price}")
                    
                    # Add to cart
                    if self.product_page.add_to_cart():
                        successful_additions += 1
                        logger.info(f"✓ Successfully added item {i} to cart")
                    else:
                        failed_additions += 1
                        logger.warning(f"✗ Failed to add item {i} to cart")
                else:
                    failed_additions += 1
                    logger.warning(f"✗ Failed to open product page for item {i}")
                
            except Exception as e:
                failed_additions += 1
                logger.error(f"Error processing item {i}: {e}")
                self.product_page.take_screenshot(f"error_item_{i}")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Add to cart completed:")
        logger.info(f"  Successful: {successful_additions}")
        logger.info(f"  Failed: {failed_additions}")
        logger.info(f"{'='*80}")
    
    def assert_cart_total_not_exceeds(
        self, 
        budget_per_item: float, 
        items_count: int
    ) -> None:
        """
        Validate that cart total does not exceed budget.
        Opens cart, reads total, compares with threshold.
        Takes screenshots for evidence.
        
        Core Function 3: Validate cart total
        
        Args:
            budget_per_item: Budget allocated per item
            items_count: Number of items expected in cart
            
        Raises:
            AssertionError: If cart total exceeds budget
            
        Example:
            automation.assert_cart_total_not_exceeds(220, 5)
        """
        logger.info("="*80)
        logger.info(f"CORE FUNCTION 3: assert_cart_total_not_exceeds")
        logger.info(f"Budget per item: ${budget_per_item}, Items count: {items_count}")
        logger.info("="*80)
        
        self.cart_page.assert_cart_total_not_exceeds(budget_per_item, items_count)
        
        logger.info("="*80)
        logger.info("Cart validation PASSED")
        logger.info("="*80)
    
    def run_full_e2e_scenario(
        self,
        search_query: str,
        max_price: float,
        items_limit: int = 5
    ) -> None:
        """
        Run complete e2e scenario:
        1. Search for items under price
        2. Add items to cart
        3. Validate cart total
        
        Args:
            search_query: Product search query
            max_price: Maximum price per item
            items_limit: Number of items to purchase
        """
        logger.info("\n" + "="*80)
        logger.info("STARTING FULL E2E SCENARIO")
        logger.info("="*80)
        
        # Step 1: Search
        urls = self.search_items_by_name_under_price(
            search_query, 
            max_price, 
            items_limit
        )
        
        if not urls:
            logger.warning("No items found matching criteria")
            return
        
        # Step 2: Add to cart
        self.add_items_to_cart(urls)
        
        # Step 3: Validate cart
        self.assert_cart_total_not_exceeds(max_price, len(urls))
        
        logger.info("\n" + "="*80)
        logger.info("E2E SCENARIO COMPLETED SUCCESSFULLY")
        logger.info("="*80 + "\n")
