from src.models import Apartment, Bill, Parameters, Tenant, Transfer


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