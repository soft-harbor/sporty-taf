from typing import override

from selenium.webdriver.remote.webelement import WebElement

from ui.core.base_object import BaseObject
from ui.core.lazy_element import LazyElement
from ui.core.types import Locator


class BaseComponent(BaseObject):
    def __init__(self, root: WebElement | Locator | None = None) -> None:
        self.root = root

    @property
    def scoped_root(self) -> WebElement | None:
        if self.root is None:
            return None
        if isinstance(self.root, WebElement):
            return self.root
        return LazyElement(self.driver, self.root)._web_element  # noqa: SLF001

    @property
    def root_element(self) -> WebElement:
        """DOM node this scoped component represents."""
        root = self.scoped_root
        if root is None:
            raise RuntimeError(f"{type(self).__name__} requires a scoped root element")
        return root

    def click_root(self) -> None:
        self.root_element.click()

    @override
    def element(self, locator: Locator) -> LazyElement:
        root_el = self.scoped_root
        if root_el is not None:
            return LazyElement(self.driver, locator, root=root_el)
        return super().element(locator)
