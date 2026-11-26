import pytest

from src.manager import Manager
from src.models import Parameters, TenantSettlement


@pytest.fixture
def manager():
    return Manager(Parameters())


def test_three_tenants_share_bills_equally(manager):
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 3
    assert sorted(s.tenant for s in settlements) == ['tenant-1', 'tenant-2', 'tenant-3']
    assert sum(s.bills_pln for s in settlements) == pytest.approx(910.0)
    for s in settlements:
        assert isinstance(s, TenantSettlement)
        assert s.bills_pln == pytest.approx(910.0 / 3)
        assert s.rent_pln == 0.0
        assert s.total_due_pln == pytest.approx(910.0 / 3)
        assert s.balance_pln == pytest.approx(-910.0 / 3)
        assert s.apartment_settlement == 'apart-polanka'
        assert s.month == 1
        assert s.year == 2025


def test_two_tenants_share_bills_equally(manager):
    del manager.tenants['tenant-3']
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 2
    assert sorted(s.tenant for s in settlements) == ['tenant-1', 'tenant-2']
    for s in settlements:
        assert s.bills_pln == pytest.approx(455.0)
        assert s.balance_pln == pytest.approx(-455.0)


def test_single_tenant_pays_all_bills(manager):
    manager.tenants = {'tenant-1': manager.tenants['tenant-1']}
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 1
    assert settlements[0].tenant == 'tenant-1'
    assert settlements[0].bills_pln == 910.0
    assert settlements[0].total_due_pln == 910.0
    assert settlements[0].balance_pln == -910.0


def test_tenant_from_other_apartment_is_not_included(manager):
    manager.tenants['tenant-3'].apartment = 'apart-inne'
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 2
    assert 'tenant-3' not in [s.tenant for s in settlements]


def test_no_tenants_returns_empty_list(manager):
    manager.tenants = {
        key: tenant for key, tenant in manager.tenants.items()
        if tenant.apartment != 'apart-polanka'
    }
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)

    assert manager.create_tenant_settlements(apartment_settlement) == []


def test_month_without_bills_gives_zero_bills(manager):
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 6)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 3
    for s in settlements:
        assert s.bills_pln == 0.0
        assert s.total_due_pln == 0.0
        assert s.month == 6
