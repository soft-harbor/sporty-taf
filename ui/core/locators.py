from typing import Self, overload

from ui.core.lazy_element import LazyElement
from ui.core.lazy_elements import LazyElements
from ui.core.types import Locator


class Loc:
    """Descriptor: single lazy element bound to a locator."""

    def __init__(self, locator: Locator) -> None:
        self.locator = locator

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type) -> LazyElement: ...

    def __get__(self, instance, owner: type):
        if instance is None:
            return self
        return instance.element(self.locator)


class Locs:
    """Descriptor: lazy collection of elements (LazyElement)."""

    def __init__(self, locator: Locator) -> None:
        self.locator = locator

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type) -> LazyElements[LazyElement]: ...

    def __get__(self, instance, owner: type):
        if instance is None:
            return self
        return instance.elements(self.locator)


class Comps[T]:
    """Descriptor: lazy collection of UI components (widgets with structure and behavior)."""

    def __init__(self, locator: Locator, component_class: type[T]) -> None:
        self.locator = locator
        self.component_class = component_class

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type) -> LazyElements[T]: ...

    def __get__(self, instance, owner: type):
        if instance is None:
            return self
        return instance.elements(self.locator, self.component_class)


def loc(selector: Locator) -> Loc:
    return Loc(selector)


def locs(selector: Locator) -> Locs:
    return Locs(selector)


def comps[T](selector: Locator, component_class: type[T]) -> Comps[T]:
    return Comps(selector, component_class)
