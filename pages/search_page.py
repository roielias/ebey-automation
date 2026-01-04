"""
Search Page Object Model for eBay
"""
import re
import time
from typing import List, Optional
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class SearchPage(BasePage):
    """Page Object for eBay Search functionality"""
    
    # Locators
    SEARCH_BOX = "input[type='text'][placeholder*='Search'], input#gh-ac"
    SEARCH_BUTTON = "input[type='submit'][value='Search'], button#gh-btn"
    
    # Results
    SEARCH_RESULTS_ITEMS = "//li[contains(@class, 's-item') or contains(@class, 'srp-results')]//div[@class='s-item__info' or @class='s-item__wrapper']"
    ITEM_TITLE = ".//h3[contains(@class, 's-item__title')]"
    ITEM_PRICE = ".//span[contains(@class, 's-item__price')]"
    ITEM_LINK = ".//a[contains(@class, 's-item__link')]"
    
    # Alternative selectors
    ALT_SEARCH_RESULTS = "ul.srp-results li.s-item"
    ALT_ITEM_PRICE = "span.s-item__price"
    ALT_ITEM_LINK = "a.s-item__link"
    
    # Filters
    PRICE_MIN_INPUT = "input[aria-label*='Minimum Value'], input[name*='_udlo']"
    PRICE_MAX_INPUT = "input[aria-label*='Maximum Value'], input[name*='_udhi']"
    PRICE_SUBMIT_BUTTON = "button[aria-label*='Submit price range'], button[type='submit']"
    
    # Pagination
    NEXT_PAGE_BUTTON = "a.pagination__next, a[aria-label='Next']"
    PAGINATION_LINKS = "nav.pagination a"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def search_for_item(self, query: str) -> None:
        """
        Search for an item on eBay
        
        Args:
            query: Search query
        """
        logger.info(f"Searching for: {query}")
        
        # Wait for search box to be visible
        self.wait_for_element(self.SEARCH_BOX)
        
        # Clear and fill search box
        self.page.locator(self.SEARCH_BOX).clear()
        self.fill(self.SEARCH_BOX, query)
        
        # Click search button or press Enter
        try:
            self.click(self.SEARCH_BUTTON)
        except Exception:
            self.press_key(self.SEARCH_BOX, "Enter")
        
        # Wait for results to load
        time.sleep(2)  # Give page time to load
        self.page.wait_for_load_state("networkidle")
    
    def apply_price_filter(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> None:
        """
        Apply price filter if available
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
        """
        try:
            logger.info(f"Applying price filter: min={min_price}, max={max_price}")
            
            # Check if price filter inputs exist
            if self.is_visible(self.PRICE_MAX_INPUT, timeout=3000):
                if min_price:
                    self.fill(self.PRICE_MIN_INPUT, str(min_price))
                
                if max_price:
                    self.fill(self.PRICE_MAX_INPUT, str(max_price))
                
                # Submit filter
                if self.is_visible(self.PRICE_SUBMIT_BUTTON, timeout=2000):
                    self.click(self.PRICE_SUBMIT_BUTTON)
                    time.sleep(2)
                    self.page.wait_for_load_state("networkidle")
                    logger.info("Price filter applied successfully")
            else:
                logger.warning("Price filter not found on page")
        except Exception as e:
            logger.warning(f"Could not apply price filter: {e}")
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price from text
        
        Args:
            price_text: Price text (e.g., "$99.99", "$100 to $200")
            
        Returns:
            Price as float or None if cannot parse
        """
        try:
            # Remove currency symbols and extra text
            price_text = price_text.replace(',', '')
            
            # Handle price ranges - take the first price
            if 'to' in price_text.lower():
                price_text = price_text.split('to')[0].strip()
            
            # Extract numbers with decimal point
            match = re.search(r'\d+\.?\d*', price_text)
            if match:
                return float(match.group())
            return None
        except Exception as e:
            logger.warning(f"Could not parse price '{price_text}': {e}")
            return None
    
    def get_search_results_items_under_price(self, max_price: float, limit: int = 5) -> List[dict]:
        """
        Get search result items under a specific price
        
        Args:
            max_price: Maximum price threshold
            limit: Maximum number of items to return
            
        Returns:
            List of dictionaries containing item information
        """
        items = []
        page_number = 1
        
        while len(items) < limit:
            logger.info(f"Processing page {page_number}, found {len(items)} items so far")
            
            # Wait for results to load
            time.sleep(2)
            
            try:
                # Try to get results using XPath
                result_elements = self.page.locator(self.SEARCH_RESULTS_ITEMS).all()
                
                # If no results with XPath, try alternative selector
                if not result_elements:
                    logger.info("Trying alternative selector for results")
                    result_elements = self.page.locator(self.ALT_SEARCH_RESULTS).all()
                
                logger.info(f"Found {len(result_elements)} result elements on page {page_number}")
                
                for element in result_elements:
                    if len(items) >= limit:
                        break
                    
                    try:
                        # Get item link
                        link_locator = element.locator(self.ITEM_LINK).first
                        if not link_locator.count():
                            link_locator = element.locator(self.ALT_ITEM_LINK).first
                        
                        if not link_locator.count():
                            continue
                        
                        item_url = link_locator.get_attribute("href")
                        
                        # Skip sponsored or invalid items
                        if not item_url or "pulsar" in item_url.lower():
                            continue
                        
                        # Get price
                        price_locator = element.locator(self.ITEM_PRICE).first
                        if not price_locator.count():
                            price_locator = element.locator(self.ALT_ITEM_PRICE).first
                        
                        if not price_locator.count():
                            continue
                        
                        price_text = price_locator.inner_text()
                        price = self.parse_price(price_text)
                        
                        if price is None:
                            logger.debug(f"Could not parse price: {price_text}")
                            continue
                        
                        # Check if price is within budget
                        if price <= max_price:
                            # Get title
                            title_locator = element.locator(self.ITEM_TITLE).first
                            title = title_locator.inner_text() if title_locator.count() else "Unknown"
                            
                            item_info = {
                                "url": item_url,
                                "price": price,
                                "title": title,
                                "price_text": price_text
                            }
                            items.append(item_info)
                            logger.info(f"Added item {len(items)}: {title} - ${price}")
                        else:
                            logger.debug(f"Item price ${price} exceeds max ${max_price}")
                    
                    except Exception as e:
                        logger.debug(f"Error processing item: {e}")
                        continue
                
                # Check if we have enough items or if there's no next page
                if len(items) >= limit:
                    logger.info(f"Collected {len(items)} items, reaching limit")
                    break
                
                # Try to go to next page
                if not self._go_to_next_page():
                    logger.info("No more pages available")
                    break
                
                page_number += 1
            
            except Exception as e:
                logger.error(f"Error getting search results: {e}")
                break
        
        return items[:limit]
    
    def _go_to_next_page(self) -> bool:
        """
        Navigate to the next page of search results
        
        Returns:
            True if successfully navigated, False otherwise
        """
        try:
            # Check if next button exists
            if self.is_visible(self.NEXT_PAGE_BUTTON, timeout=2000):
                current_url = self.get_current_url()
                
                # Click next page
                self.click(self.NEXT_PAGE_BUTTON)
                time.sleep(3)
                self.page.wait_for_load_state("networkidle")
                
                # Verify URL changed
                new_url = self.get_current_url()
                if new_url != current_url:
                    logger.info("Successfully navigated to next page")
                    return True
            
            logger.info("Next page button not found or unavailable")
            return False
        
        except Exception as e:
            logger.warning(f"Could not navigate to next page: {e}")
            return False
    
    def search_items_by_name_under_price(self, query: str, max_price: float, limit: int = 5) -> List[str]:
        """
        Main function: Search items by name and return URLs under max price
        
        Args:
            query: Search query
            max_price: Maximum price threshold
            limit: Maximum number of items to return
            
        Returns:
            List of item URLs
        """
        logger.info(f"=== Starting search: query='{query}', max_price=${max_price}, limit={limit} ===")
        
        # Perform search
        self.search_for_item(query)
        
        # Take screenshot of search results
        self.take_screenshot(f"search_results_{query}")
        
        # Apply price filter if possible
        self.apply_price_filter(max_price=max_price)
        
        # Get items under price
        items = self.get_search_results_items_under_price(max_price, limit)
        
        # Extract URLs
        urls = [item["url"] for item in items]
        
        logger.info(f"=== Search complete: found {len(urls)} items ===")
        return urls
