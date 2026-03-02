from enum import Enum


class Currency(str, Enum):
    BGN = "BGN"
    CHF = "CHF"
    EUR = "EUR"
    HUF = "HUF"
    PLN = "PLN"
    RON = "RON"

    def __str__(self) -> str:
        return str(self.value)
