from ui.core.context import driver_context
from ui.core.lazy_element import LazyElement
from ui.core.lazy_elements import LazyElements
from ui.core.types import Locator


class BaseObject:
    @property
    def driver(self):
        return driver_context.get()

    def element(self, locator: Locator) -> LazyElement:
        return LazyElement(self.driver, locator)

    def elements[T](self, locator: Locator, item_class: type[T] | None = None) -> LazyElements[T]:
        return LazyElements(self, locator, item_class)
