"""
Product Page Object Model for eBay
"""
import time
import random
from typing import Optional
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class ProductPage(BasePage):
    """Page Object for eBay Product details page"""
    
    # Locators
    ADD_TO_CART_BUTTON = "a[href*='additem'], a:has-text('Add to cart'), button:has-text('Add to cart')"
    BUY_IT_NOW_BUTTON = "a:has-text('Buy It Now'), a[id*='binBtn']"
    
    # Variants/Options
    SIZE_DROPDOWN = "select[aria-label*='Size'], select#msku-sel-1"
    COLOR_DROPDOWN = "select[aria-label*='Color'], select[aria-label*='Colour'], select#msku-sel-2"
    QUANTITY_INPUT = "input[aria-label*='Quantity'], input[id*='qtyTextBox']"
    
    # Generic variant selectors
    VARIANT_SELECTS = "select[class*='msku'], select[class*='variant']"
    
    # Confirmation
    CART_CONFIRMATION = "div[role='dialog'], div[class*='confirmation']"
    GO_TO_CART_LINK = "a:has-text('Go to cart'), a[href*='/cart']"
    CONTINUE_SHOPPING = "a:has-text('Continue shopping'), button:has-text('Continue')"
    
    # Product info
    PRODUCT_TITLE = "h1.x-item-title, h1[class*='title']"
    PRODUCT_PRICE = "span[class*='x-price-primary'], div[class*='x-price-section']"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def get_product_title(self) -> str:
        """
        Get product title
        
        Returns:
            Product title
        """
        try:
            return self.get_text(self.PRODUCT_TITLE)
        except Exception as e:
            logger.warning(f"Could not get product title: {e}")
            return "Unknown Product"
    
    def get_product_price(self) -> Optional[str]:
        """
        Get product price
        
        Returns:
            Product price text or None
        """
        try:
            return self.get_text(self.PRODUCT_PRICE)
        except Exception as e:
            logger.warning(f"Could not get product price: {e}")
            return None
    
    def select_random_variants(self) -> None:
        """
        Select random variants/options if available (size, color, etc.)
        """
        logger.info("Checking for product variants")
        
        try:
            # Find all select dropdowns for variants
            variant_selects = self.page.locator("select").all()
            
            for select_element in variant_selects:
                try:
                    # Check if this is a variant selector
                    select_id = select_element.get_attribute("id") or ""
                    select_class = select_element.get_attribute("class") or ""
                    select_label = select_element.get_attribute("aria-label") or ""
                    
                    # Skip quantity selectors
                    if "quantity" in select_id.lower() or "qty" in select_id.lower():
                        continue
                    
                    # Check if it's a variant selector
                    if any(keyword in (select_id + select_class + select_label).lower() 
                           for keyword in ["size", "color", "colour", "msku", "variant", "style"]):
                        
                        # Get available options
                        options = select_element.locator("option").all()
                        
                        # Filter out placeholder options
                        valid_options = []
                        for i, option in enumerate(options):
                            option_text = option.inner_text().strip().lower()
                            option_value = option.get_attribute("value") or ""
                            
                            # Skip empty or placeholder options
                            if (option_text and option_value and 
                                option_text not in ["select", "choose", "please select", "-"] and
                                option_value not in ["", "-1"]):
                                valid_options.append(i)
                        
                        if valid_options:
                            # Select random valid option
                            random_index = random.choice(valid_options)
                            select_element.select_option(index=random_index)
                            
                            selected_option = options[random_index].inner_text()
                            logger.info(f"Selected variant: {selected_option}")
                            time.sleep(0.5)  # Wait a bit between selections
                
                except Exception as e:
                    logger.debug(f"Error handling select element: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Error selecting variants: {e}")
    
    def set_quantity(self, quantity: int = 1) -> None:
        """
        Set product quantity
        
        Args:
            quantity: Quantity to set
        """
        try:
            if self.is_visible(self.QUANTITY_INPUT, timeout=2000):
                logger.info(f"Setting quantity to {quantity}")
                quantity_field = self.page.locator(self.QUANTITY_INPUT).first
                quantity_field.clear()
                quantity_field.fill(str(quantity))
        except Exception as e:
            logger.debug(f"Could not set quantity: {e}")
    
    def add_to_cart(self) -> bool:
        """
        Add item to cart
        
        Returns:
            True if successfully added, False otherwise
        """
        try:
            logger.info("Attempting to add item to cart")
            
            # Select variants if available
            self.select_random_variants()
            
            # Set quantity to 1
            self.set_quantity(1)
            
            # Take screenshot before adding
            self.take_screenshot("before_add_to_cart")
            
            # Find and click Add to Cart button
            add_to_cart_locator = self.page.locator(self.ADD_TO_CART_BUTTON).first
            
            if add_to_cart_locator.count() == 0:
                logger.error("Add to Cart button not found")
                return False
            
            # Scroll to button if needed
            add_to_cart_locator.scroll_into_view_if_needed()
            time.sleep(0.5)
            
            # Click the button
            add_to_cart_locator.click()
            logger.info("Clicked Add to Cart button")
            
            # Wait for confirmation
            time.sleep(2)
            
            # Take screenshot after adding
            self.take_screenshot("after_add_to_cart")
            
            # Check for confirmation dialog
            if self.is_visible(self.CART_CONFIRMATION, timeout=3000):
                logger.info("Cart confirmation dialog appeared")
                
                # Try to continue shopping or close dialog
                if self.is_visible(self.CONTINUE_SHOPPING, timeout=2000):
                    self.click(self.CONTINUE_SHOPPING)
                    time.sleep(1)
            
            logger.info("Item added to cart successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add item to cart: {e}")
            self.take_screenshot("add_to_cart_error")
            return False
    
    def open_product_page(self, url: str) -> bool:
        """
        Open a product page
        
        Args:
            url: Product URL
            
        Returns:
            True if successfully opened, False otherwise
        """
        try:
            logger.info(f"Opening product page: {url}")
            self.navigate_to(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Verify product page loaded
            if self.is_visible(self.PRODUCT_TITLE, timeout=5000):
                product_title = self.get_product_title()
                logger.info(f"Product page loaded: {product_title}")
                return True
            else:
                logger.warning("Product page may not have loaded correctly")
                return False
        
        except Exception as e:
            logger.error(f"Failed to open product page: {e}")
            return False
