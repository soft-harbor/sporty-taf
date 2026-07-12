from collections.abc import Generator

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from api.client import SportyAPIClient
from api.steps.account import AccountSteps
from base_settings import settings
from ui.app import App
from ui.browser_config import BrowserContextConfig, create_webdriver
from ui.core.context import driver_context


@pytest.fixture(scope="session")
def driver(browser_config: BrowserContextConfig) -> Generator[WebDriver]:
    web_driver = create_webdriver(browser_config)
    yield web_driver
    web_driver.quit()


@pytest.fixture(autouse=True)
def setup_context(driver: WebDriver) -> Generator[None]:
    token = driver_context.set(driver)
    yield
    driver_context.reset(token)


@pytest.fixture
def api() -> Generator[SportyAPIClient]:
    with SportyAPIClient(user_id=settings.sporty_test_user_id) as client:
        yield client


@pytest.fixture
def account_steps(api: SportyAPIClient) -> AccountSteps:
    return AccountSteps(api)


@pytest.fixture
def app(account_steps: AccountSteps) -> App:
    # Test harness assumption: reset via POST /api/reset-balance for a deterministic
    # starting balance. Not part of the user journey; the app has no other option to set any predefined balance.
    account_steps.reset_balance()
    return App()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator[None]:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            driver.current_url,
            name="page-url",
            attachment_type=allure.attachment_type.TEXT,
        )
    except Exception:
        pass
