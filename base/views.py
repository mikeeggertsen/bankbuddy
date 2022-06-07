from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from authsystem.forms import SignUpForm
from base.constants import MANAGER
from base.forms import AccountForm, EmployeeForm, LoanForm, LoanStatusForm, ProfileForm, RankForm, TransactionForm
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from base.models import Account, Employee, Ledger, Loan, Customer, Bank, ScheduledLedger
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractYear
from django.db.models import Count
from django.core.paginator import Paginator


@login_required
def index(request):
    return redirect(reverse('base:dashboard'))

# DASHBOARD


@login_required
def dashboard(request):
    context = {}
    if request.user.is_staff:
        pending = Loan.objects.filter(status=1).count()
        approved = Loan.objects.filter(status=2).count()
        rejected = Loan.objects.filter(status=3).count()
        context["loans"] = [pending, approved, rejected]
        context["total_funds"] = Bank().total_funds
        context["total_customers"] = Customer.objects.all().count()
        context["total_accounts"] = Account.objects.all().count()

        filter = request.GET.get('q', '')
        data_set = None
        if filter == "monthly":
            data_set = Ledger.objects.annotate(label=ExtractMonth(
                "created_at")).values('label').annotate(count=Count('id'))
        elif filter == "yearly":
            data_set = Ledger.objects.annotate(label=ExtractYear(
                "created_at")).values('label').annotate(count=Count('id'))
        else:
            data_set = Ledger.objects.annotate(label=ExtractWeek(
                "created_at")).values('label').annotate(count=Count('id'))

        transactions = []
        labels = []
        ordered_data = data_set.all().order_by('label')
        for record in ordered_data:
            transactions.append(record['count'])
            labels.append(record['label'])
            context["transactions"] = transactions
            context["labels"] = labels
        return render(request, 'base/admin/dashboard.html', context)
    else:
        account = None
        try:
            account = Account.objects.filter(
                customer__id=request.user.id).order_by("created_at")[:1].get()
        except Exception:
            pass
        transaction_filter = request.GET.get('q', '')
        if account:
            context["transactions"] = account.transactions
            if transaction_filter == "credit":
                context["transactions"] = account.transactions.filter(type=1)
            elif transaction_filter == "debit":
                context["transactions"] = account.transactions.filter(type=2)
            context['account'] = account
        return render(request, 'base/dashboard.html', context)

# CUSTOMERS


@staff_member_required
def customers(request):
    context = {}
    customers = Customer.objects.all().order_by("-created_at")
    paginator = Paginator(customers, 4)
    page_number = request.GET.get('page')
    context["customers"] = paginator.get_page(page_number)
    return render(request, "base/admin/customer_list.html", context)


@staff_member_required
def customer_details(request, id):
    context = {}
    customer = get_object_or_404(Customer, pk=id)
    if request.method == "POST":
        form = RankForm(request.POST)
        if form.is_valid():
            rank = form.cleaned_data["rank"]
            customer.rank = rank
            customer.save()
    form = RankForm()
    form.fields["rank"].initial = customer.rank
    context["form"] = form
    context["customer"] = customer
    context["accounts"] = Account.objects.filter(customer__id=id)
    return render(request, "base/admin/customer_details.html", context)


@staff_member_required
def create_customer(request):
    context = {}
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            Customer.objects.create_user(**form.cleaned_data)
        return redirect(reverse('base:customers'))
    context["form"] = SignUpForm()
    return render(request, "base/admin/customer_create.html", context)


# ACCOUNTS
@login_required
def accounts(request):
    context = {}

    accounts = Account.objects.filter(
        customer__id=request.user.id).order_by("-created_at")

    if request.user.is_staff:
        accounts = Account.objects.all().order_by("-created_at")

    paginator = Paginator(accounts, 3)
    page_number = request.GET.get('page')
    context["accounts"] = paginator.get_page(page_number)
    return render(request, 'base/account_list.html', context)


@login_required
def account_details(request, account_no):
    context = {}
    try:
        if request.user.is_staff:
            context["account"] = get_object_or_404(
                Account, account_no=account_no)
        else:
            context["account"] = get_object_or_404(
                Account, customer__id=request.user.id, account_no=account_no)
    except Http404:
        return redirect(reverse('base:accounts'))
    return render(request, 'base/account_details.html', context)


@login_required
def create_account(request):
    context = {}
    if request.method == "POST":
        form = AccountForm(request.user.is_staff, request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            type = form.cleaned_data["type"]
            account.type = type
            if request.user.is_staff:
                account.customer = form.cleaned_data["customer"]
            else:
                account.customer = get_object_or_404(
                    Customer, pk=request.user.id)
            account.save()
            return redirect(reverse('base:accounts'))
    form = AccountForm(request.user.is_staff)
    context["form"] = form
    return render(request, "base/account_create.html", context)

# TRANSACTIONS


@login_required
def create_transaction(request):
    context = {}
    is_loan = False
    if request.method == "POST":
        form = TransactionForm(is_loan, request.POST)
        context["form"] = form
        if form.is_valid():
            account = form.cleaned_data["account"]
            account_no = form.cleaned_data["to_account"]
            amount = form.cleaned_data["amount"]
            own_message = form.cleaned_data["own_message"]
            message = form.cleaned_data["message"]
            bank = form.cleaned_data["bank"]
            scheduled_date = form.cleaned_data["scheduled_date"]

            if account.customer.id != request.user.id:
                print("Not your account!!")  # TODO show error to user

            if bank is not None:
                Ledger.make_external_transfer(
                    credit_account=account_no,
                    debit_account=account,
                    amount=amount,
                    own_message=f"{bank.id}#{account_no}: '{own_message}'",
                    message=message,
                    external_bank_id=bank.id
                )
                return redirect(reverse('base:transfer'))

            to_account = Account.objects.get(account_no=account_no)

            if scheduled_date:
                ScheduledLedger.make_scheduled_transaction(
                    credit_account=to_account,
                    debit_account=account,
                    amount=amount,
                    own_message=own_message,
                    message=message,
                    scheduled_date=scheduled_date
                )
            else:
                Ledger.make_bank_transaction(
                    credit_account=to_account,
                    debit_account=account,
                    amount=amount,
                    own_message=own_message,
                    message=message,
                )
            return redirect(reverse('base:transfer'))
        else:
            return render(request, "base/transaction_create.html", context)

    form = TransactionForm(is_loan)
    form.fields["account"].queryset = Account.objects.filter(
        customer__id=request.user.id)
    context["form"] = form
    return render(request, "base/transaction_create.html", context)

# LOANS


@login_required
def loans(request):
    context = {}

    loans = Loan.objects.filter(customer__id=request.user.id)

    if request.user.is_staff:
        loans = Loan.objects.all().order_by("-created_at")
    else:
        context["customer"] = get_object_or_404(Customer, pk=request.user.id)

    paginator = Paginator(loans, 3)
    page_number = request.GET.get('page')
    context["loans"] = paginator.get_page(page_number)
    return render(request, "base/loan_list.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff or get_object_or_404(Customer, pk=u.id).rank > 1)
def loan_details(request, account_no):
    context = {}
    employee = None
    if request.user.is_staff:
        employee = Employee.objects.get(email=request.user.email)
        context["employee"] = employee
    loan = get_object_or_404(Loan, account_no=account_no)
    if request.method == "POST":
        if employee.role == MANAGER:
            form = LoanStatusForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data["status"]
                if status == 2:
                    Loan.approve_loan(loan)
                loan.status = status
                loan.save()
    context["loan"] = loan
    if request.user.is_staff:
        form = LoanStatusForm()
        form.fields["status"].initial = loan.status
        context["form"] = form
    return render(request, "base/loan_details.html", context)


@login_required
@user_passes_test(lambda u: get_object_or_404(Customer, pk=u.id).rank > 1)
def apply_loan(request):
    context = {}
    if request.method == "POST":
        form = LoanForm(request.user.id, request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            credit_account = form.cleaned_data["accounts"]
            customer = get_object_or_404(Customer, pk=request.user.id)
            loan.customer = customer
            loan.credit_account = credit_account
            loan.save()
            return redirect(reverse('base:loans'))
    context["form"] = LoanForm(request.user.id)
    return render(request, "base/loan_create.html", context)


@login_required
@user_passes_test(lambda u: get_object_or_404(Customer, pk=u.id).rank > 1)
def loan_payment(request, account_no):
    context = {}
    is_loan = True
    form = TransactionForm(is_loan)
    if request.method == "POST":
        loan = get_object_or_404(Loan, account_no=account_no)
        data = request.POST.copy()
        msg = f"{loan.name} loan payment"
        data.update({"message": msg, "own_message": msg})
        form = TransactionForm(is_loan, data=data)
        if form.is_valid():
            account = form.cleaned_data["account"]
            amount = form.cleaned_data["amount"]
            own_message = form.cleaned_data["own_message"]
            message = form.cleaned_data["message"]

            if loan:
                Loan.make_loan_transaction(
                    credit_account=loan,
                    debit_account=account,
                    amount=amount,
                    own_message=own_message,
                    message=message,
                )
            else:
                context["error"] = "Failed to make payment on loan"
            return redirect(reverse('base:loan', kwargs={"account_no": account_no}))
        form.fields["to_account"].initial = account_no
        context["form"] = form
        return render(request, "base/loan_payment.html", context)

    form.fields["to_account"].initial = account_no
    context["form"] = form
    return render(request, "base/loan_payment.html", context)

# EMPLOYEES


@user_passes_test(lambda u: u.is_superuser)
def employees(request):
    context = {}
    employees = Employee.objects.all().order_by("-created_at")
    paginator = Paginator(employees, 4)
    page_number = request.GET.get('page')
    context["employees"] = paginator.get_page(page_number)
    return render(request, "base/admin/employee_list.html", context)


@user_passes_test(lambda u: u.is_superuser)
def employee_details(request, id):
    context = {}
    context["employee"] = get_object_or_404(Employee, pk=id)
    return render(request, "base/admin/employee_details.html", context)


@user_passes_test(lambda u: u.is_superuser)
def create_employee(request):
    context = {}
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.set_password(employee.password)
            is_manager = form.cleaned_data["role"] == 2
            if is_manager:
                employee.is_superuser = True
            else:
                employee.is_staff = True
            employee.save()
            return redirect(reverse("base:employees"))
        pass
    context["form"] = EmployeeForm()
    return render(request, "base/admin/employee_create.html", context)

# PROFILE


@login_required
def profile(request):
    context = {}
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        context["form"] = form
        print(form.is_valid())
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data["password"]:
                user.set_password(form.cleaned_data["password"])
            user.save()
            update_session_auth_hash(request, form.instance)
            return redirect(reverse('base:profile'))
        else:
            return render(request, 'base/profile_details.html', context)

    user = None
    id = request.user.id
    if request.user.is_staff:
        user = get_object_or_404(Employee, pk=id)
    else:
        user = get_object_or_404(Customer, pk=id)
    context["form"] = ProfileForm(instance=user)
    return render(request, 'base/profile_details.html', context)
