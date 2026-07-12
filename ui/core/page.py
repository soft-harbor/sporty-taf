from ui.core.base_object import BaseObject


class BasePage(BaseObject):
    def open(self, url: str) -> None:
        self.driver.get(url)
