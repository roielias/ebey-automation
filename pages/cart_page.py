"""
Cart Page Object Model for eBay
"""
import re
from typing import Optional
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class CartPage(BasePage):
    """Page Object for eBay Shopping Cart page"""
    
    # Locators
    CART_ICON = "a[href*='/cart'], a#gh-cart, i.gh-eb-Minicart"
    CART_LINK = "//a[contains(@href, '/cart') or contains(@href, 'viewcart')]"
    
    # Cart items
    CART_ITEMS = "div[data-test-id*='cart-item'], div.cart-bucket"
    ITEM_PRICE = "span[data-test-id='ITEM_PRICE'], span.item-price"
    
    # Cart total
    CART_SUBTOTAL = "span[data-test-id='SUB_TOTAL'], div.summary-total span.val"
    CART_TOTAL = "span[data-test-id='TOTAL'], div.total span.val"
    
    # Alternative selectors
    ALT_CART_TOTAL = "//div[contains(@class, 'total')]//span[contains(@class, 'amount')]"
    ALT_SUBTOTAL = "//tr[contains(., 'Subtotal')]//td//span"
    
    # Cart URL
    CART_URL_PATTERN = "**/cart**"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def open_cart(self) -> None:
        """
        Open the shopping cart
        """
        try:
            logger.info("Opening shopping cart")
            
            # Try clicking cart icon
            if self.is_visible(self.CART_ICON, timeout=3000):
                self.click(self.CART_ICON)
            else:
                # Navigate directly to cart URL
                cart_url = f"{self.page.context.base_url or 'https://www.ebay.com'}/cart"
                self.navigate_to(cart_url)
            
            # Wait for cart page to load
            self.page.wait_for_load_state("networkidle")
            
            # Take screenshot
            self.take_screenshot("cart_page")
            
            logger.info("Cart page opened")
        
        except Exception as e:
            logger.error(f"Failed to open cart: {e}")
            raise
    
    def parse_price_from_text(self, price_text: str) -> Optional[float]:
        """
        Parse price from text
        
        Args:
            price_text: Price text (e.g., "US $99.99", "$100.00")
            
        Returns:
            Price as float or None
        """
        try:
            # Remove currency symbols and extra text
            price_text = price_text.replace(',', '').replace('US', '').replace('$', '').strip()
            
            # Extract numbers with decimal point
            match = re.search(r'\d+\.?\d*', price_text)
            if match:
                price = float(match.group())
                logger.debug(f"Parsed price: {price} from text: {price_text}")
                return price
            
            logger.warning(f"Could not parse price from: {price_text}")
            return None
        
        except Exception as e:
            logger.error(f"Error parsing price '{price_text}': {e}")
            return None
    
    def get_cart_subtotal(self) -> Optional[float]:
        """
        Get cart subtotal
        
        Returns:
            Subtotal as float or None
        """
        try:
            logger.info("Getting cart subtotal")
            
            # Try main selector
            if self.is_visible(self.CART_SUBTOTAL, timeout=3000):
                subtotal_text = self.get_text(self.CART_SUBTOTAL)
                return self.parse_price_from_text(subtotal_text)
            
            # Try alternative XPath selector
            if self.is_visible(self.ALT_SUBTOTAL, timeout=2000):
                subtotal_text = self.get_text(self.ALT_SUBTOTAL)
                return self.parse_price_from_text(subtotal_text)
            
            logger.warning("Could not find subtotal element")
            return None
        
        except Exception as e:
            logger.error(f"Error getting cart subtotal: {e}")
            return None
    
    def get_cart_total(self) -> Optional[float]:
        """
        Get cart total (including shipping/taxes if applicable)
        
        Returns:
            Total as float or None
        """
        try:
            logger.info("Getting cart total")
            
            # Try to get total
            if self.is_visible(self.CART_TOTAL, timeout=3000):
                total_text = self.get_text(self.CART_TOTAL)
                return self.parse_price_from_text(total_text)
            
            # Try alternative selector
            if self.is_visible(self.ALT_CART_TOTAL, timeout=2000):
                total_text = self.get_text(self.ALT_CART_TOTAL)
                return self.parse_price_from_text(total_text)
            
            # If no total found, use subtotal
            logger.info("Total not found, using subtotal")
            return self.get_cart_subtotal()
        
        except Exception as e:
            logger.error(f"Error getting cart total: {e}")
            return None
    
    def get_number_of_items(self) -> int:
        """
        Get number of items in cart
        
        Returns:
            Number of items
        """
        try:
            items = self.page.locator(self.CART_ITEMS).all()
            count = len(items)
            logger.info(f"Found {count} items in cart")
            return count
        except Exception as e:
            logger.warning(f"Could not count cart items: {e}")
            return 0
    
    def assert_cart_total_not_exceeds(self, budget_per_item: float, items_count: int) -> None:
        """
        Assert that cart total does not exceed budget
        
        Args:
            budget_per_item: Budget per item
            items_count: Expected number of items
            
        Raises:
            AssertionError: If total exceeds budget
        """
        logger.info(f"=== Validating cart total ===")
        logger.info(f"Budget per item: ${budget_per_item}")
        logger.info(f"Expected items count: {items_count}")
        
        # Open cart
        self.open_cart()
        
        # Get cart total
        cart_total = self.get_cart_total()
        
        if cart_total is None:
            logger.error("Could not retrieve cart total")
            self.take_screenshot("cart_total_error")
            raise AssertionError("Failed to retrieve cart total")
        
        # Calculate threshold
        threshold = budget_per_item * items_count
        
        logger.info(f"Cart total: ${cart_total}")
        logger.info(f"Threshold: ${threshold}")
        
        # Take screenshot for evidence
        self.take_screenshot("cart_validation")
        
        # Assert
        if cart_total > threshold:
            error_msg = f"Cart total ${cart_total} exceeds threshold ${threshold}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        else:
            logger.info(f"✓ Cart total ${cart_total} is within budget ${threshold}")
