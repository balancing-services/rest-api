from typing import Literal

DemandBasis = Literal["additive", "substitutive"]

DEMAND_BASIS_VALUES: set[DemandBasis] = {
    "additive",
    "substitutive",
}


def check_demand_basis(value: str) -> DemandBasis:
    if value in DEMAND_BASIS_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {DEMAND_BASIS_VALUES!r}"
    )
