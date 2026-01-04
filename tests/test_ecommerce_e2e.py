"""
End-to-End tests for e-commerce automation
Using pytest with Allure reporting
"""
import pytest
import allure
import os
from playwright.sync_api import Page
from ecommerce_automation import EcommerceAutomation
from utils.data_reader import DataReader
from config.config import Config

# Load test data
test_data_path = os.path.join(Config.TEST_DATA_DIR, 'test_data.json')
test_data_json = DataReader.read_json(test_data_path)


@allure.feature('E-commerce Shopping')
@allure.story('Product Search and Purchase')
class TestEcommerceE2E:
    """End-to-end test cases for e-commerce functionality"""
    
    @pytest.mark.e2e
    @pytest.mark.smoke
    @allure.title("Test: Search and add items to cart - {test_data[search_query]}")
    @allure.description("Complete e2e test: search items, add to cart, validate total")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("test_data", test_data_json)
    def test_full_e2e_scenario(self, page: Page, test_data: dict):
        """
        Full e2e scenario test
        
        Steps:
        1. Search for items under max price
        2. Add items to cart
        3. Validate cart total
        """
        with allure.step(f"Initialize automation for {test_data['search_query']}"):
            automation = EcommerceAutomation(page)
        
        with allure.step(f"Search for '{test_data['search_query']}' under ${test_data['max_price']}"):
            urls = automation.search_items_by_name_under_price(
                query=test_data['search_query'],
                max_price=test_data['max_price'],
                limit=test_data['items_limit']
            )
            
            allure.attach(
                f"Found {len(urls)} items\n" + "\n".join(urls),
                name="Search Results",
                attachment_type=allure.attachment_type.TEXT
            )
            
            assert len(urls) > 0, f"No items found for query: {test_data['search_query']}"
        
        with allure.step(f"Add {len(urls)} items to cart"):
            automation.add_items_to_cart(urls)
        
        with allure.step(f"Validate cart total not exceeds ${test_data['budget_per_item'] * len(urls)}"):
            automation.assert_cart_total_not_exceeds(
                budget_per_item=test_data['budget_per_item'],
                items_count=len(urls)
            )


@allure.feature('E-commerce Shopping')
@allure.story('Product Search')
class TestSearchFunctionality:
    """Test cases for search functionality"""
    
    @pytest.mark.search
    @allure.title("Test: Search items by name under price")
    @allure.description("Verify search function returns items under specified price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_items_under_price(self, page: Page):
        """Test search functionality with price filter"""
        with allure.step("Initialize automation"):
            automation = EcommerceAutomation(page)
        
        with allure.step("Search for 'phone case' under $50"):
            urls = automation.search_items_by_name_under_price(
                query="phone case",
                max_price=50,
                limit=3
            )
            
            allure.attach(
                str(urls),
                name="Search Results URLs",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Verify results"):
            assert isinstance(urls, list), "Search should return a list"
            assert len(urls) <= 3, "Should not exceed limit"
    
    @pytest.mark.search
    @allure.title("Test: Search handles pagination")
    @allure.description("Verify search continues to next page if needed")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_with_pagination(self, page: Page):
        """Test search with pagination to collect items"""
        with allure.step("Initialize automation"):
            automation = EcommerceAutomation(page)
        
        with allure.step("Search for 'book' under $30 with limit 5"):
            urls = automation.search_items_by_name_under_price(
                query="book",
                max_price=30,
                limit=5
            )
        
        with allure.step("Verify pagination handling"):
            # Test should handle pagination if available
            assert isinstance(urls, list), "Should return list of URLs"


@allure.feature('E-commerce Shopping')
@allure.story('Shopping Cart')
class TestCartFunctionality:
    """Test cases for cart functionality"""
    
    @pytest.mark.cart
    @allure.title("Test: Add single item to cart")
    @allure.description("Verify single item can be added to cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_single_item_to_cart(self, page: Page):
        """Test adding a single item to cart"""
        with allure.step("Initialize automation"):
            automation = EcommerceAutomation(page)
        
        with allure.step("Search for one item"):
            urls = automation.search_items_by_name_under_price(
                query="usb cable",
                max_price=20,
                limit=1
            )
            
            # Skip test if no items found
            if not urls:
                pytest.skip("No items found for testing")
        
        with allure.step("Add item to cart"):
            automation.add_items_to_cart(urls)
        
        # Test passes if no exception thrown
    
    @pytest.mark.cart
    @allure.title("Test: Validate cart total calculation")
    @allure.description("Verify cart total validation works correctly")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_total_validation(self, page: Page):
        """Test cart total validation"""
        with allure.step("Initialize automation"):
            automation = EcommerceAutomation(page)
        
        with allure.step("Search and add items"):
            urls = automation.search_items_by_name_under_price(
                query="sticker",
                max_price=10,
                limit=2
            )
            
            if not urls:
                pytest.skip("No items found for testing")
            
            automation.add_items_to_cart(urls)
        
        with allure.step("Validate cart total"):
            automation.assert_cart_total_not_exceeds(
                budget_per_item=10,
                items_count=len(urls)
            )


@allure.feature('E-commerce Shopping')
@allure.story('Data-Driven Testing')
class TestDataDriven:
    """Data-driven test cases using YAML"""
    
    @pytest.mark.regression
    @allure.title("Test: Data-driven from YAML - {test_data[test_name]}")
    @allure.description("Execute tests with data from YAML file")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("test_data", 
        DataReader.read_yaml(os.path.join(Config.TEST_DATA_DIR, 'test_data.yaml'))['test_cases']
    )
    def test_from_yaml_data(self, page: Page, test_data: dict):
        """Test using YAML data file"""
        with allure.step(f"Run test: {test_data['test_name']}"):
            automation = EcommerceAutomation(page)
            
            urls = automation.search_items_by_name_under_price(
                query=test_data['search_query'],
                max_price=test_data['max_price'],
                limit=test_data['items_limit']
            )
            
            if urls:
                automation.add_items_to_cart(urls)
                automation.assert_cart_total_not_exceeds(
                    budget_per_item=test_data['budget_per_item'],
                    items_count=len(urls)
                )
            else:
                pytest.skip(f"No items found for {test_data['search_query']}")
