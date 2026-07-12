from functools import cached_property

from ui.pages.betting_page import BettingPage


class App:
    """Entry point for UI tests. WebDriver is provided via driver_context (see tests/ui/conftest.py)."""

    @cached_property
    def betting_page(self) -> BettingPage:
        return BettingPage()
