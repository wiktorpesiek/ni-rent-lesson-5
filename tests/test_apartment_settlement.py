import pytest

from src.manager import Manager
from src.models import ApartmentSettlement, Bill, Parameters


@pytest.fixture
def manager():
    return Manager(Parameters())


def test_settlement_for_month_with_bills(manager):
    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 1
    assert settlement.total_bills_pln == 910.0
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == 910.0


def test_settlement_for_month_without_bills(manager):
    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 6)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 6
    assert settlement.total_bills_pln == 0.0
    assert settlement.total_due_pln == 0.0


def test_bill_from_other_month_does_not_change_settlement(manager):
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=300.0,
        type='gas'
    ))
    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)

    assert settlement.total_bills_pln == 910.0
    assert settlement.total_due_pln == 910.0


def test_settlement_for_missing_apartment_is_none(manager):
    assert manager.create_apartment_settlement('apart-nie-istnieje', 2025, 1) is None
