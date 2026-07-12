from functools import cached_property
from typing import Self
from urllib.parse import urlencode

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from base_settings import settings
from ui.components import BetSlip, Header, MatchCard, Receipt
from ui.core.locators import comps
from ui.core.page import BasePage
from ui.core.timeouts import DEFAULT_TIMEOUT


class BettingPage(BasePage):
    match_cards = comps((By.CSS_SELECTOR, ".matchCard"), MatchCard)

    @cached_property
    def header(self) -> Header:
        return Header()

    @cached_property
    def bet_slip(self) -> BetSlip:
        return BetSlip()

    @cached_property
    def receipt(self) -> Receipt:
        return Receipt()

    @property
    def url(self) -> str:
        base = settings.frontend_base_url.rstrip("/")
        query = urlencode({"user-id": settings.sporty_test_user_id})
        return f"{base}/?{query}"

    def wait_open(self, timeout: int = DEFAULT_TIMEOUT) -> Self:
        try:
            self.header.balance_display.wait_visible(timeout)
        except TimeoutException as err:
            raise TimeoutException(f"betting page did not open at {self.url!r}") from err
        return self

    def navigate(self) -> None:
        self.open(self.url)
        self.wait_open()

    def has_selected_odds(self) -> bool:
        return any(card.has_selected_odds() for card in self.match_cards)
