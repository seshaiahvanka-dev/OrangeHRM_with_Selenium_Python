import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from pageObjects.DashBoardPage import DashboardPage
from pageObjects.JobPage import JobPage
from utilities.ReadConfig import ReadConfig
from pageObjects.LoginPage import LoginPage
from utilities.customLogger import LogGen  # Import your logger utility

# Initialize the logger for the conftest level
logger = LogGen.loggen()


# This hook adds the custom --browser argument to the pytest command
def pytest_addoption(parser):
    logger.info("--------- Addoption Hook Running  ---------")
    parser.addoption("--browser", action="store", default="chrome",
                     help="Type in browser: chrome or firefox or edge")


@pytest.fixture(scope="function")
def setup(request):
    browser_name = request.config.getoption("--browser").lower()
    driver = None
    logger.info("--------- Starting WebDriver Setup ---------")
    logger.info(f"--------- Initializing {browser_name} browser ---------")

    try:
        # 1️⃣ Create browser
        if browser_name == "chrome":
            options = ChromeOptions()
            options.page_load_strategy = 'eager'
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)

        elif browser_name == "firefox":
            driver = webdriver.Firefox()

        elif browser_name == "edge":
            driver = webdriver.Edge()

        else:
            logger.warning(f"Browser '{browser_name}' not recognized. Launching Chrome as default.")
            driver = webdriver.Chrome()

        # 2️⃣ Browser configurations
        timeout = int(ReadConfig.get_config_data('common info', 'timeout'))
        driver.implicitly_wait(timeout)
        driver.set_page_load_timeout(30)
        driver.delete_all_cookies()
        logger.info(f"Browser configured with implicit wait: {timeout}s")

        # 3️⃣ Launch application
        base_url = ReadConfig.get_config_data('common info', 'baseURL')
        logger.info(f"Opening Application URL: {base_url}")
        driver.get(base_url)
        driver.maximize_window()
        logger.info("Browser window maximized.")

        # 4️⃣ Pass driver to the test class
        if request.cls is not None:
            request.cls.driver = driver

        yield driver

    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        raise e

    finally:
        if driver is not None:
            logger.info("Quitting WebDriver and closing browser.")
            logger.info(f"--------- {browser_name} Browser Closed ---------")
            driver.quit()
        logger.info("--------- WebDriver Setup Completed ---------")


@pytest.fixture(scope="function")
def init_pages(request, setup):
    """
    Initializes Page Objects and logs the initialization process.
    """
    logger.info(" ********** Initializing Page Objects **********")

    request.cls.lp = LoginPage(setup)
    request.cls.dp = DashboardPage(setup)
    request.cls.jp = JobPage(setup)

    logger.info("Page Objects initialized and attached to the class instance.")


# ================= CUSTOM HTML REPORT CONFIGURATION =================

def pytest_configure(config):
    """Adds custom metadata including active browser to the HTML Report environment section safely"""

    try:
        browser_used = config.getoption("--browser")
    except ValueError:
        browser_used = "chrome"

    browser_name = str(browser_used).capitalize()

    if hasattr(config, "stash"):
        from pytest_metadata.plugin import metadata_key
        config.stash[metadata_key]['Project Name'] = 'OrangeHRM Test Suite'
        config.stash[metadata_key]['Tester'] = 'QA Automation Engineer'
        config.stash[metadata_key]['Browser'] = browser_name

        if 'JAVA_HOME' in config.stash[metadata_key]:
            del config.stash[metadata_key]['JAVA_HOME']
        if 'Packages' in config.stash[metadata_key]:
            del config.stash[metadata_key]['Packages']
    else:
        if hasattr(config, "_metadata"):
            config._metadata['Project Name'] = 'OrangeHRM Test Suite'
            config._metadata['Tester'] = 'QA Automation Engineer'
            config._metadata['Browser'] = browser_name
