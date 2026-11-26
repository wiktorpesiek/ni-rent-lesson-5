from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float | None:
        """Zwraca sumę rachunków mieszkania.

        Args:
            apartment_key: klucz mieszkania (np. 'apart-polanka').
            year: rok rozliczeniowy; None oznacza wszystkie lata.
            month: miesiąc rozliczeniowy; None oznacza wszystkie miesiące.

        Returns:
            Suma kwot rachunków jako float (0.0, gdy brak pasujących rachunków)
            albo None, gdy mieszkanie nie istnieje.

        Raises:
            ValueError: gdy month jest spoza zakresu 1..12 albo podano month bez year.
        """
        if month is not None:
            if year is None:
                raise ValueError("Nie można podać miesiąca bez roku")
            if not 1 <= month <= 12:
                raise ValueError(f"Miesiąc musi być z zakresu 1..12, otrzymano {month}")

        if apartment_key not in self.apartments:
            return None

        bills = [bill for bill in self.bills if bill.apartment == apartment_key]
        if year is not None:
            bills = [bill for bill in bills if bill.settlement_year == year]
        if month is not None:
            bills = [bill for bill in bills if bill.settlement_month == month]

        return sum((bill.amount_pln for bill in bills), 0.0)

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        """Tworzy rozliczenie mieszkania za dany miesiąc.

        Returns:
            ApartmentSettlement z sumą rachunków za miesiąc albo None,
            gdy mieszkanie nie istnieje.
        """
        total_bills_pln = self.get_apartment_costs(apartment_key, year, month)
        if total_bills_pln is None:
            return None

        # TODO: uwzględnić przelewy w kolejnych krokach
        total_rent_pln = 0.0

        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=total_rent_pln,
            total_bills_pln=total_bills_pln,
            total_due_pln=total_bills_pln,
        )

    def create_tenant_settlements(self, apartment_settlement: ApartmentSettlement) -> list[TenantSettlement]:
        """Dzieli rozliczenie mieszkania równo między jego najemców.

        Returns:
            Lista TenantSettlement (po jednym na najemcę mieszkania);
            pusta lista, gdy mieszkanie nie ma najemców.
        """
        # Najemców NIE filtrujemy po datach umów: w danych bazowych umowy kończą się
        # w 2024, a rachunki są z 2025, więc taki filtr odrzuciłby wszystkich najemców.
        tenant_keys = [
            key for key, tenant in self.tenants.items()
            if tenant.apartment == apartment_settlement.apartment
        ]
        if not tenant_keys:
            return []

        bills_pln = apartment_settlement.total_bills_pln / len(tenant_keys)
        # TODO: uwzględnić czynsz i przelewy najemców w kolejnych krokach
        rent_pln = 0.0
        total_due_pln = bills_pln

        return [
            TenantSettlement(
                tenant=key,
                apartment_settlement=apartment_settlement.apartment,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=rent_pln,
                bills_pln=bills_pln,
                total_due_pln=total_due_pln,
                balance_pln=0.0 - total_due_pln,
            )
            for key in tenant_keys
        ]
