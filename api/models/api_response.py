from typing import Any, Self, TypeVar

import requests
from pydantic import TypeAdapter, ValidationError

T = TypeVar("T")
E = TypeVar("E")


class ApiResponse[T]:
    def __init__(self, response: requests.Response, model_class: type[T] | None = None):
        self.response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self._model_class = model_class

    def value(self) -> T:
        self.response.raise_for_status()
        if not self._model_class:
            raise RuntimeError("Pydantic model class not defined")
        try:
            return TypeAdapter(self._model_class).validate_python(self.response.json())
        except ValidationError as exc:
            raise AssertionError(f"Validation failed for: {exc}") from exc

    def assert_status(self, expected: int) -> Self:
        assert self.status_code == expected, f"Expected {expected}, got {self.status_code}: {self._json()}"
        return self

    def parse(self, model: type[E]) -> E:
        try:
            return TypeAdapter(model).validate_python(self._json())
        except ValidationError as exc:
            raise AssertionError(f"Validation failed: {exc}") from exc

    def validate(self, status: int, model: type[E]) -> E:
        return self.assert_status(status).parse(model)

    @property
    def raw(self) -> requests.Response:
        return self.response

    def _json(self) -> dict[str, Any]:
        if self.status_code == requests.codes.no_content or not self.response.content:
            return {}
        return self.response.json()
