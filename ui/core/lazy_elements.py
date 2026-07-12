from collections.abc import Iterable, Iterator
from typing import override

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ui.core.lazy_element import LazyElement
from ui.core.timeouts import DEFAULT_TIMEOUT
from ui.core.types import Locator


class LazyElements[T](Iterable[T]):
    def __init__(self, instance, locator: Locator, item_class: type[T] | None = None) -> None:
        self._instance = instance
        self.locator = locator
        self.item_class = item_class

    def _resolve(self) -> list[T]:
        root = self._search_root()
        if isinstance(root, WebElement):
            WebDriverWait(root, DEFAULT_TIMEOUT).until(lambda el: len(el.find_elements(*self.locator)) > 0)
            elements = root.find_elements(*self.locator)
        else:
            WebDriverWait(root, DEFAULT_TIMEOUT).until(EC.presence_of_all_elements_located(self.locator))
            elements = root.find_elements(*self.locator)

        if self.item_class is None:
            return [LazyElement.from_node(self._instance.driver, el) for el in elements]  # type: ignore[return-value]
        return [self.item_class(el) for el in elements]

    def _search_root(self):
        instance = self._instance
        if getattr(instance, "root", None) is not None:
            return instance.scoped_root
        return instance.driver

    @property
    def first(self) -> T:
        return self[0]

    @override
    def __iter__(self) -> Iterator[T]:
        return iter(self._resolve())

    def __len__(self) -> int:
        return len(self._resolve())

    def __getitem__(self, index: int) -> T:
        return self._resolve()[index]
