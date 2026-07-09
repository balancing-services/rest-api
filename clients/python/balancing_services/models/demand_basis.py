from enum import Enum


class DemandBasis(str, Enum):
    ADDITIVE = "additive"
    SUBSTITUTIVE = "substitutive"

    def __str__(self) -> str:
        return str(self.value)
