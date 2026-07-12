from selenium.webdriver.common.by import By

from ui.core.base_component import BaseComponent
from ui.core.locators import loc


class OddsButton(BaseComponent):
    label_text = loc((By.CSS_SELECTOR, ".oddsButtonLabel"))
    value_text = loc((By.CSS_SELECTOR, ".oddsButtonValue"))

    def label(self) -> str:
        return self.label_text.text()

    def value(self) -> float:
        return float(self.value_text.text())

    def select(self) -> None:
        self.click_root()

    def is_selected(self) -> bool:
        classes = self.root_element.get_attribute("class") or ""
        return "oddsButtonSelected" in classes.split()
