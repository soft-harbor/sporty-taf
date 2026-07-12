from dataclasses import dataclass
from pathlib import Path

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "browser.yaml"


@dataclass(frozen=True)
class BrowserContextConfig:
    browser: str
    headless: bool
    window_size: tuple[int, int]
    arguments: tuple[str, ...]


def _load_raw_config() -> dict:
    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_browser_context(name: str | None = None) -> BrowserContextConfig:
    raw = _load_raw_config()
    context_name = name or raw["default_context"]
    ctx = raw["contexts"][context_name]
    size = ctx["window_size"]
    return BrowserContextConfig(
        browser=ctx["browser"],
        headless=ctx["headless"],
        window_size=(size[0], size[1]),
        arguments=tuple(ctx.get("arguments", [])),
    )


def create_webdriver(config: BrowserContextConfig) -> WebDriver:
    width, height = config.window_size

    if config.browser == "chrome":
        options = ChromeOptions()
        if config.headless:
            options.add_argument("--headless=new")
        for arg in config.arguments:
            options.add_argument(arg)
        options.add_argument(f"--window-size={width},{height}")
        return webdriver.Chrome(options=options)

    raise ValueError(f"Unsupported browser: {config.browser!r}; only chrome is configured")
