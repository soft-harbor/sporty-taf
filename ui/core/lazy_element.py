from collections.abc import Callable
from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from ui.core.timeouts import DEFAULT_TIMEOUT
from ui.core.types import Locator


class LazyElement:
    def __init__(
        self,
        driver: WebDriver,
        locator: Locator | None = None,
        root: WebElement | None = None,
    ) -> None:
        self.driver = driver
        self.locator = locator
        self.root = root

    @classmethod
    def from_node(cls, driver: WebDriver, element: WebElement) -> Self:
        """Wrap an already-resolved DOM node (e.g. from find_elements)."""
        return cls(driver, root=element)

    @property
    def _target(self) -> WebDriver | WebElement:
        return self.root if self.root is not None else self.driver

    def _resolved_element(self) -> WebElement:
        if self.root is None:
            raise RuntimeError("LazyElement requires a root element when no locator is set")
        return self.root

    def _present_element(self) -> WebElement:
        if self.locator is None:
            return self._resolved_element()
        return self._target.find_element(*self.locator)

    def _visible_element(self, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        self.wait_visible(timeout)
        return self._present_element()

    @property
    def _web_element(self) -> WebElement:
        return self._visible_element()

    def click(self) -> None:
        self._web_element.click()

    def fill(self, text: str) -> None:
        self._web_element.clear()
        self._web_element.send_keys(text)

    def text(self, strip: bool = True) -> str:
        text = self._web_element.text
        return text.strip() if strip else text

    def attribute(self, name: str) -> str | None:
        return self._web_element.get_attribute(name)

    def is_present(self) -> bool:
        try:
            self._present_element()
            return True
        except Exception:
            return False

    def is_visible(self) -> bool:
        try:
            return self._present_element().is_displayed()
        except Exception:
            return False

    def contains_text(self, text: str) -> bool:
        return text in self.text()

    def _state_snapshot(self) -> str:
        if not self.is_present():
            return "not present"
        try:
            element = self._present_element()
            return f"present, displayed={element.is_displayed()}, enabled={element.is_enabled()}, text={element.text!r}"
        except Exception as exc:
            return f"<failed to read state: {exc}>"

    def _wait_until(self, condition: Callable[[], bool], *, description: str, timeout: int) -> None:
        try:
            WebDriverWait(self.driver, timeout).until(lambda _: condition(), message=description)
        except TimeoutException as err:
            raise TimeoutException(f"{description} (locator={self.locator!r}, {self._state_snapshot()})") from err

    def wait_visible(self, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(self.is_visible, description="element to be visible", timeout=timeout)
        return self

    def wait_present(self, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(self.is_present, description="element to be present", timeout=timeout)
        return self

    def wait_hidden(self, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(lambda: not self.is_visible(), description="element to be hidden", timeout=timeout)
        return self

    def wait_clickable(self, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(self._is_clickable, description="element to be clickable", timeout=timeout)
        return self

    def wait_text_equals(self, expected: str, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(
            lambda: self._present_element().text == expected,
            description=f"text to equal {expected!r}",
            timeout=timeout,
        )
        return self

    def wait_text_contains(self, text: str, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(
            lambda: text in self._present_element().text,
            description=f"text to contain {text!r}",
            timeout=timeout,
        )
        return self

    def wait_text_not_contains(self, text: str, timeout: int = DEFAULT_TIMEOUT) -> Self:
        self._wait_until(
            lambda: text not in self._present_element().text,
            description=f"text not to contain {text!r}",
            timeout=timeout,
        )
        return self

    def wait_until_text(
        self,
        predicate: Callable[[str], bool],
        timeout: int = DEFAULT_TIMEOUT,
        *,
        description: str | None = None,
    ) -> Self:
        label = description or f"text condition on {self.locator!r}"
        self._wait_until(lambda: predicate(self._present_element().text), description=label, timeout=timeout)
        return self

    def _is_clickable(self) -> bool:
        try:
            element = self._present_element()
            return element.is_displayed() and element.is_enabled()
        except Exception:
            return False
