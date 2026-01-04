"""Pages package - Page Object Models"""
from .base_page import BasePage
from .search_page import SearchPage
from .product_page import ProductPage
from .cart_page import CartPage

__all__ = ['BasePage', 'SearchPage', 'ProductPage', 'CartPage']
