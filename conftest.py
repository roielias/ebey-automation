"""
Pytest configuration and fixtures
"""
import pytest
import allure
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config.config import Config
from utils.logger import Logger
from utils.screenshot_helper import ScreenshotHelper

logger = Logger.get_logger(__name__)

# Ensure directories exist
Config.ensure_directories()


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Browser launch arguments"""
    return {
        "headless": Config.HEADLESS,
        "args": ["--start-maximized"] if not Config.HEADLESS else []
    }


@pytest.fixture(scope="session")
def browser_context_args():
    """Browser context arguments"""
    return {
        "viewport": None if not Config.HEADLESS else {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def playwright_instance():
    """Create a Playwright instance for the entire test session"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, browser_type_launch_args):
    """Create a browser instance for the entire test session"""
    logger.info(f"Launching {Config.BROWSER} browser")
    
    if Config.BROWSER == "chromium":
        browser = playwright_instance.chromium.launch(**browser_type_launch_args)
    elif Config.BROWSER == "firefox":
        browser = playwright_instance.firefox.launch(**browser_type_launch_args)
    elif Config.BROWSER == "webkit":
        browser = playwright_instance.webkit.launch(**browser_type_launch_args)
    else:
        raise ValueError(f"Unsupported browser: {Config.BROWSER}")
    
    yield browser
    
    logger.info("Closing browser")
    browser.close()


@pytest.fixture(scope="function")
def context(browser, browser_context_args):
    """Create a new browser context for each test"""
    context = browser.new_context(**browser_context_args)
    context.set_default_timeout(Config.DEFAULT_TIMEOUT)
    context.set_default_navigation_timeout(Config.NAVIGATION_TIMEOUT)
    
    yield context
    
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Create a new page for each test"""
    page = context.new_page()
    
    yield page
    
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture screenshots on test failure
    """
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        if Config.SCREENSHOT_ON_FAILURE:
            try:
                # Get the page fixture if it exists
                if "page" in item.funcargs:
                    page = item.funcargs["page"]
                    screenshot_path = ScreenshotHelper.take_screenshot(
                        page,
                        f"failure_{item.name}"
                    )
                    
                    # Attach to Allure report
                    if screenshot_path:
                        with open(screenshot_path, "rb") as image_file:
                            allure.attach(
                                image_file.read(),
                                name=f"failure_{item.name}",
                                attachment_type=allure.attachment_type.PNG
                            )
            except Exception as e:
                logger.error(f"Failed to capture failure screenshot: {e}")


def pytest_configure(config):
    """Configure pytest"""
    logger.info("=" * 80)
    logger.info("Starting Test Execution")
    logger.info("=" * 80)
    logger.info(f"Base URL: {Config.BASE_URL}")
    logger.info(f"Browser: {Config.BROWSER}")
    logger.info(f"Headless: {Config.HEADLESS}")


def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes"""
    logger.info("=" * 80)
    logger.info("Test Execution Completed")
    logger.info(f"Exit Status: {exitstatus}")
    logger.info("=" * 80)
