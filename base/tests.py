from django.test import RequestFactory, TestCase
from base.constants import BASIC, CHECKING, GOLD, MANAGER, PENDING, SAVINGS, SUPPORT

from base.models import Account, Bank, Customer, Employee, Loan, User
from base.views import account_details, accounts, apply_loan, create_account, create_customer, create_employee, create_transaction, customer_details, customers, dashboard, employee_details, employees, loan_details, loan_payment, loans, profile

class ViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.bank = Bank.objects.create(
            id="id_test_bank",
            name="Test Bank",
            external=False
        )
        self.user = Customer.objects.create(
            email="jane@doe.dk",
            first_name="Jane",
            last_name="Doe",
            phone="12345678",
            password="imjanedoe",
            bank=self.bank,
            rank=GOLD
        )
        self.account = Account.objects.create(
            customer=self.user,
            name="Test account",
            type=CHECKING
        )
        self.admin = User.objects.create(
            email="admin@bankbuddy.dk",
            password="supersecurepassword",
            is_superuser=True,
            is_staff=True
        )
        self.employee = Employee.objects.create(
            email="employee@bankbuddy.dk",
            password="lesssecurepassword",
            phone="1337",
            role=MANAGER,
        )
        self.loan = Loan.objects.create(
            customer=self.user,
            name="Car loan",
            credit_account=self.account,
            amount=50000,
            status=PENDING,
        )
        Loan.approve_loan(self.loan)

    def test_dashboard(self):
        request = self.factory.get("/dashboard")
        request.user = self.user
        response = dashboard(request)
        self.assertEqual(response.status_code, 200)

    #ACCOUNT TESTS
    def test_account_list(self):
        request = self.factory.get("/accounts")
        request.user = self.user
        response = accounts(request)
        self.assertEqual(response.status_code, 200)

    def test_account_details(self):
        request = self.factory.get("accounts/<int:account_no>")
        request.user = self.user
        response = account_details(request, self.account.account_no)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.account.balance, 50000)
        self.assertEqual(self.account.name, "Test account")

    def test_create_account_get(self):
        request = self.factory.get(f"/accounts/new")
        request.user = self.user
        response = create_account(request)
        self.assertEqual(response.status_code, 200)

    def test_create_account_post(self):
        acc_name = "Another test account"
        data = {
            "name": acc_name,
            "type": SAVINGS
        }
        request = self.factory.post("/accounts/new", data)
        request.user = self.user
        response = create_account(request)
        created_account = Account.objects.get(name=acc_name)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(created_account.name, acc_name)
        self.assertEqual(created_account.balance, 0)

    #LOAN TESTS
    def test_loan_list(self):
        request = self.factory.get("/loans")
        request.user = self.user
        response = loans(request)
        self.assertEqual(response.status_code, 200)

    def test_loan_details(self):
        request = self.factory.get("/loans")
        request.user = self.user
        response = loan_details(request, self.loan.account_no)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.loan.total_debt, 50000)
        self.assertEqual(self.loan.name, "Car loan")

    def test_apply_loan_get(self):
        request = self.factory.get("/loans/apply")
        request.user = self.user
        response = apply_loan(request)
        self.assertEqual(response.status_code, 200)
    
    def test_apply_loan_post(self):
        data = {
            "accounts": self.account.id,
            "name": "House loan",
            "amount": 1000000,
        }
        request = self.factory.post("/loans/apply", data)
        request.user = self.user
        response = apply_loan(request)
        loan = Loan.objects.get(name=data["name"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(loan.name, data["name"])
        self.assertEqual(loan.total_paid, 0)
        self.assertEqual(loan.credit_account, self.account)
        self.assertEqual(loan.total_debt, 1000000)

    def test_loan_payment_get(self):
        request = self.factory.get("loans/<int:account_no>/payment")
        request.user = self.user
        response = loan_payment(request, self.loan.account_no)
        self.assertEqual(response.status_code, 200)
    
    def test_loan_payment_post(self):
        data = {
            "account": self.account.id,
            "to_account": self.loan.account_no,
            "amount": 1000,
        }
        request = self.factory.post("loans/<int:account_no>/payment", data)
        request.user = self.user
        response = loan_payment(request, self.loan.account_no)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.loan.total_debt, 49000)
        self.assertEqual(self.account.balance, 49000)

    #TRANSACTION TEST
    def test_transaction_get(self):
        request = self.factory.get("transfer")
        request.user = self.user
        response = create_transaction(request)
        self.assertEqual(response.status_code, 200)

    def test_transaction_post(self):
        to_account = Account.objects.create(
            customer=self.user,
            name="Offshore account",
            type=SAVINGS
        )
        data = {
            "account": self.account.id,
            "to_account": to_account.account_no,
            "amount": 100,
            "message": "Savings",
            "own_message": "Savings",
        }
        request = self.factory.post("transfer", data)
        request.user = self.user
        response = create_transaction(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.account.balance, 49900)
        self.assertEqual(to_account.balance, 100)

    #PROFILE
    def test_profile_get(self):
        request = self.factory.get("profile")
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 200)
    
    def test_profile_post(self):
        data = {
            "first_name": "Joe",
            "last_name": "Dane",
            "email": "joe@dane.com",
            "phone": "87654321",
        }
        request = self.factory.post("profile", data)
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.first_name, data["first_name"])
        self.assertEqual(self.user.last_name, data["last_name"])
        self.assertEqual(self.user.email, data["email"])
        self.assertEqual(self.user.phone, data["phone"])

    #CUSTOMERS
    def test_customers(self):
        request = self.factory.get("customers")
        request.user = self.admin
        response = customers(request)
        self.assertEqual(response.status_code, 200)
    
    def test_customer_details(self):
        request = self.factory.get("customers/<int:id>")
        request.user = self.admin
        response = customer_details(request, self.user.id)
        self.assertEqual(response.status_code, 200)
    
    def test_create_customer(self):
        data = {
            "email": "dark@knight.dk",
            "first_name": "Bruce",
            "last_name": "Wayne",
            "phone": "1111111",
            "password": "bestofdc",
            "bank": self.bank.id,
        }
        request = self.factory.post("customers/new", data)
        request.user = self.admin
        response = create_customer(request)
        customer = Customer.objects.get(email=data["email"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(customer.email, data["email"])
        self.assertEqual(customer.first_name, data["first_name"])
        self.assertEqual(customer.last_name, data["last_name"])
        self.assertEqual(customer.bank.id, data["bank"])
        self.assertEqual(customer.rank, BASIC)

    #EMPLOYEES
    def test_employees(self):
        request = self.factory.get("employees")
        request.user = self.admin
        response = employees(request)
        self.assertEqual(response.status_code, 200)

    def test_employee_details(self):
        request = self.factory.get("employees/<int:id>")
        request.user = self.admin
        response = employee_details(request, self.employee.id)
        self.assertEqual(response.status_code, 200)

    def test_create_employee_get(self):
        request = self.factory.get("employees")
        request.user = self.admin
        response = create_employee(request)
        self.assertEqual(response.status_code, 200)
    
    def test_create_employee_post(self):
        data = {
            "email": "mclovin@bankbuddy.dk",
            "password": "superbad",
            "phone": "69696969",
            "role": SUPPORT,
        }
        request = self.factory.post("employees", data)
        request.user = self.admin
        response = create_employee(request)
        employee = Employee.objects.get(email=data["email"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(employee.email, data["email"])
        self.assertEqual(employee.phone, data["phone"])
        self.assertEqual(employee.role, data["role"])
