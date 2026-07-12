from selenium.webdriver.common.by import By

from ui.core.base_component import BaseComponent
from ui.core.locators import loc
from ui.helpers import parse_eur_amount


class Header(BaseComponent):
    balance_display = loc((By.ID, "header-balance"))

    def balance(self) -> float | int:
        return parse_eur_amount(self.balance_display.text())

    def wait_balance(self, expected: float | int, timeout: int = 15) -> None:
        self.balance_display.wait_until_text(
            lambda text: parse_eur_amount(text) == expected,
            timeout,
            description=f"header balance to become {expected}",
        )
