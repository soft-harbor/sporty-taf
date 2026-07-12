import pytest

from tests.reporting import register_http_logging
from ui.browser_config import BrowserContextConfig, load_browser_context


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--browser-context",
        action="store",
        default=None,
        help="Browser context preset from config/browser.yaml (e.g. chrome_headless)",
    )


def pytest_configure(config: pytest.Config) -> None:
    register_http_logging()


@pytest.fixture(scope="session")
def browser_config(request: pytest.FixtureRequest) -> BrowserContextConfig:
    context_name = request.config.getoption("--browser-context")
    return load_browser_context(context_name)
