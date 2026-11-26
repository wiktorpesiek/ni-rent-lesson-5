import pytest

from src.manager import Manager
from src.models import Bill, Parameters


@pytest.fixture
def manager():
    return Manager(Parameters())


def test_costs_for_missing_apartment_is_none(manager):
    assert manager.get_apartment_costs('apart-nie-istnieje', 2025, 1) is None


def test_costs_without_bills_in_month_is_zero(manager):
    costs = manager.get_apartment_costs('apart-polanka', 2025, 6)
    assert costs == 0.0
    assert isinstance(costs, float)


def test_costs_sum_bills_in_month(manager):
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0


def test_costs_year_matches_but_month_does_not(manager):
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0.0


def test_costs_ignore_bills_of_other_apartment(manager):
    manager.bills.append(Bill(
        apartment='apart-inne',
        date_due='2025-02-10',
        settlement_year=2025,
        settlement_month=1,
        amount_pln=500.0,
        type='gas'
    ))
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0


# --- Test prowadzącego (gałąź extra-integration-test) ---

def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0

    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0
