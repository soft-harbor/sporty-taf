# sporty-taf

QA automation for the Sporty Group take-home: **Selenium UI E2E** and **API tests** against the betting app.

The assignment asks for **two automated tests** (one UI E2E flow, one API check) plus framework structure - see [Assignment scope](#assignment-scope). Additional API scenarios capture **some exploratory findings** from manual execution; the full defect catalogue is in `docs/defects/`.

## Submission map

| Deliverable | Location |
|---|---|
| Test plan (5–6 scenarios) | [`docs/test-plan/TP-001_single_bet_placement.md`](docs/test-plan/TP-001_single_bet_placement.md) |
| Manual execution (top 3) | [`docs/test-plan/execution_summary.md`](docs/test-plan/execution_summary.md) |
| Bug reports | [`docs/defects/`](docs/defects/) |
| Required UI test (TC-01) | [`tests/ui/bets/test_place_bet.py`](tests/ui/bets/test_place_bet.py) |
| Required API test (TC-01b) | [`tests/api/bets/test_bets.py`](tests/api/bets/test_bets.py) |
| Strategy & recommendations | [`docs/test-plan/strategy_and_recommendations.md`](docs/test-plan/strategy_and_recommendations.md) |

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.12 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Test runner | pytest + pytest-check |
| Reporting | Allure (HTTP logs, failure screenshots) |
| API client | requests + Pydantic |
| UI | Selenium 4 (Selenium Manager) |
| Quality | Ruff, Pyright, pre-commit |

### Tooling choices (beyond required stack)

Assignment requires Python 3, Selenium WebDriver, `requests`, and Chrome. Everything else is optional - why it is here:

| Tool | Why |
|---|---|
| **uv** | Modern package manager with a reproducible lockfile; faster setup than pip/Poetry - `make sync` prepares the project in one step. |
| **Pydantic** | Validates JSON responses and maps them to Python types - fast and keeps API models in one place. |
| **pytest-check** | Collects multiple assertion failures in one test run instead of stopping at the first. |
| **Allure** | Rich HTML reports with steps, attachments, and history - easier to debug failures than plain pytest output. |
| **Schemathesis** | Used manually during exploration to fuzz `api/openapi.json` (optional `contract` dep group); not wired into `make test`. |
| **Ruff + Pyright** | Lint, format, and type-check in `make quality` - keeps the framework consistent without extra CI setup. |
| **pre-commit** | Same checks locally before push; hook installed by `make sync` (`uv run pre-commit run --all-files` to run manually). |

Not used as a gate: **pytest-xdist** - tests share one `SPORTY_TEST_USER_ID` and mutate balance, so parallel workers would race (noted under [Commands](#commands)).

## Quick start

```bash
make bootstrap         # once: install uv + Allure CLI
make sync              # deps + pre-commit git hook
cp .env.example .env   # set SPORTY_TEST_USER_ID and URLs
make test-api          # or: make test-ui / make test
```

| Variable | Description |
|---|---|
| `FRONTEND_BASE_URL` | Web app URL |
| `BACKEND_BASE_URL` | API base URL |
| `SPORTY_TEST_USER_ID` | Sent as `x-user-id` header |

Loaded from `.env` via `base_settings.py`.

## Project layout

```
api/                  # client, endpoints, models, steps; openapi.json
ui/                   # page objects (core/, components/, pages/)
tests/api/            # @pytest.mark.api
tests/ui/             # @pytest.mark.ui
tests/reporting/      # Allure HTTP attachments
config/browser.yaml   # Selenium presets (chrome_headless, chrome_headed)
docs/                 # test plan, specs, defect reports
```

## Commands

```bash
make help              # all targets

# Tests (sequential - shared test user; see below)
make test              # all tests + Allure report (opens even if tests fail)
make test-api
make test-ui
make test-ui BROWSER_CONTEXT=chrome_headed
make allure-report     # reopen report from existing allure-results/

# Quality - fix auto-repairs ruff issues; pyright has no auto-fix
make fix               # ruff check --fix + format
make quality           # lint + format check + pyright (CI gate)
uv run pre-commit run --all-files
```

**Allure details:** API calls and UI failure screenshots attach automatically. Results land in `allure-results/{api,ui}/`; `make allure-report` flattens them into `allure-results/_merged/` before `allure serve`.

**Parallel runs:** [pytest-xdist](https://pypi.org/project/pytest-xdist/) is the usual choice when tests are isolated. Here tests share one `SPORTY_TEST_USER_ID` and mutate balance via `POST /api/reset-balance` / `POST /api/place-bet`, so parallel workers would race.

**Contract fuzz (optional):** [Schemathesis](https://schemathesis.io/) was used ad-hoc against `api/openapi.json` during exploration. Install with `uv sync --group contract`, then e.g. `uv run st run api/openapi.json --url "$BACKEND_BASE_URL" --header "x-user-id: $SPORTY_TEST_USER_ID"`. Use a dedicated user; it issues state-changing calls.

## UI architecture

Thin Selenium layer in `ui/core/` — plain WebDriver, no third-party Page Object wrappers, to stay aligned with the assignment brief. Small helpers to cut boilerplate: declarative locators, lazy element resolution, scoped components, shared waits.

| Concept | Declare with | Role                                        |
|---|---|---------------------------------------------|
| Element | `loc()` / `locs()` | Single field or list; found when first used |
| Component | `comps()` + `BaseComponent` | Reusable widget with extra behaviour        |

```python
class MatchCard(BaseComponent):
    status_badge = loc((By.CSS_SELECTOR, ".badge"))
    team_names = locs((By.CSS_SELECTOR, ".teamName"))
    odds_buttons = comps((By.CSS_SELECTOR, ".oddsButton"), OddsButton)
```

## Assignment scope

Per `docs/specs/HQA_Take_Home_Task.md`, Part B requires **two** high-value automated tests. Everything else in the repo supports the framework and documents exploratory work.

| Required | Test | File |
|---|---|---|
| UI E2E | TC-01 - happy path: odds → bet slip → place → receipt | `tests/ui/bets/test_place_bet.py` |
| API | TC-01b - `POST /api/place-bet` contract + money math | `tests/api/bets/test_bets.py` |

**Beyond scope (exploratory):** extra API cases in the same module - payload validation, HTTP protocol, overdraft/currency (xfail) - plus manual test plan, defect reports, and ad-hoc Schemathesis runs against `api/openapi.json`. These reflect findings from top-3 manual execution and exploration, not a full regression suite.

Manual deliverables: `docs/test-plan/`, `docs/defects/`, `docs/test-plan/strategy_and_recommendations.md`. Execution results: `docs/test-plan/execution_summary.md`.

## Coverage & known defects

**Required automation**

| ID | Layer | What |
|---|---|---|
| TC-01 | UI | Happy path: odds → bet slip → place → receipt |
| TC-01b | API | `POST /api/place-bet` contract + money math |

**Some exploratory API findings** (automated where practical)

| Area | Examples |
|---|---|
| Validation | Missing fields, stake bounds, invalid selection/matchId |
| Protocol | Auth header, unsupported methods (xfail API-004) |
| Business rules | Overdraft (xfail API-005), currency (xfail API-006) |

Known bugs are surfaced with **pytest-check** soft asserts (UI) or **xfail** (API) so one run reports every defect without hiding the required happy-path flow. Full write-ups: `docs/defects/`.

Tests reset balance to €125.50 via `POST /api/reset-balance` before each run (test harness only, not part of the user flow).

## CI

Run locally via `make quality`, `make test-api`, `make test-ui`, or `make test`. CI/CD recommendations (Docker/Grid, quality gates, contract checks): [strategy doc](docs/test-plan/strategy_and_recommendations.md#3-top-recommendations-if-scaling).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401` on API tests | Missing or wrong `SPORTY_TEST_USER_ID` in `.env` |
| UI test **FAILED** with multiple soft-check failures | Expected - known product bugs (UI-001, UI-010, UI-011, UI-012); see `docs/defects/ui/` |
| `make test` exits non-zero but report opens | By design - exit code reflects test failures; report still generated |
| Pyright / IDE broken after `uv` reinstall | Point interpreter to `.venv/bin/python` (see below) |

## IDE

After `uv` recreates `.venv`, point the interpreter to `.venv/bin/python` (preset in `.vscode/settings.json`; PyCharm: **Settings → Python Interpreter → Existing**).
