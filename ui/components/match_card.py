from selenium.webdriver.common.by import By

from api.models.selection import Selection
from ui.components.odds_button import OddsButton
from ui.core.base_component import BaseComponent
from ui.core.locators import comps, loc, locs
from ui.helpers import ui_label_for


class MatchCard(BaseComponent):
    status_badge = loc((By.CSS_SELECTOR, ".matchMeta .badge"))
    team_names = locs((By.CSS_SELECTOR, ".teamName"))
    odds_buttons = comps((By.CSS_SELECTOR, ".oddsButton"), OddsButton)

    def home_team(self) -> str:
        return self.team_names[0].text()

    def away_team(self) -> str:
        return self.team_names[1].text()

    def status_label(self) -> str:
        return self.status_badge.text()

    def is_upcoming(self) -> bool:
        return self.status_label().upper() != "PAST"

    def select_odds(self, selection: Selection) -> None:
        self._odds_button(selection).select()

    def odds_for(self, selection: Selection) -> float:
        return self._odds_button(selection).value()

    def has_selected_odds(self) -> bool:
        return any(button.is_selected() for button in self.odds_buttons)

    def _odds_button(self, selection: Selection) -> OddsButton:
        label = ui_label_for(selection)
        for button in self.odds_buttons:
            if button.label() == label:
                return button
        raise ValueError(f"Selection {selection.value!r} not found")
