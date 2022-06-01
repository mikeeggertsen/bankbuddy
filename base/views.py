import json
import os
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from base.forms import AccountForm, LoanForm, LoanStatusForm, ProfileForm, RankForm, TransactionForm
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from base.models import Account, Ledger, Loan, Customer, Bank
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractYear
from django.db.models import Count
from django.core.paginator import Paginator

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
            data_set = Ledger.objects.annotate(label=ExtractMonth("created_at")).values('label').annotate(count=Count('id'))
        elif filter == "yearly":
            data_set = Ledger.objects.annotate(label=ExtractYear("created_at")).values('label').annotate(count=Count('id'))
        else:
            data_set = Ledger.objects.annotate(label=ExtractWeek("created_at")).values('label').annotate(count=Count('id'))
        
        transactions = []
        labels = []
        for record in data_set:
            transactions.append(record['count'])
            labels.append(record['label'])
            context["transactions"] = transactions
            context["labels"] = labels
        return render(request, 'base/admin/dashboard.html', context)
    else:
        account = Account.objects.filter(customer__id=request.user.id)
        transaction_filter = request.GET.get('q', '')
        if account:
            context["transactions"] = account.transactions
            if transaction_filter == "credit":
                context["transactions"] = account.transactions.filter(type=1)
            elif transaction_filter == "debit":
                context["transactions"] = account.transactions.filter(type=2)
            context['account'] = account
        return render(request, 'base/dashboard.html', context)

#CUSTOMERS
@staff_member_required
def customers(request):
    context = {}
    customers = Customer.objects.all()
    paginator = Paginator(customers, 10)
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

# ACCOUNTS


@login_required
def accounts(request):
    context = {}
    if request.user.is_staff:
        context['accounts'] = Account.objects.all().order_by("-created_at")
    else: 
        context['accounts'] = Account.objects.filter(customer__id=request.user.id).order_by("-created_at")
    return render(request, 'base/account_list.html', context)


@login_required
def account_details(request, account_no):
    context = {}
    try:
        if request.user.is_staff:
            context["account"] = get_object_or_404(Account, account_no=account_no)
        else: 
            context["account"] = get_object_or_404(Account, customer__id=request.user.id, account_no=account_no)
    except Http404:
        return redirect(reverse('base:accounts'))
    return render(request, 'base/account_details.html', context)


@login_required
def create_account(request):
    context = {}
    form = AccountForm(request.user.is_staff)
    context["form"] = form
    if request.method == "POST":
        form = AccountForm(request.user.is_staff, request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            account = form.save(commit=False)
            type = form.cleaned_data["type"]
            account.type = type
            if request.user.is_staff:
                account.customer = form.cleaned_data["customer"]
            else:
                account.customer = get_object_or_404(Customer, pk=request.user.id)
            account.save()
            return redirect(reverse('base:accounts'))

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
            to_account = get_object_or_404(Account, account_no=account_no)

            if account.customer.id != request.user.id:
                print("Not your account!!")  # TODO show error to user
                return redirect(reverse('base:transfer'))

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

            to_account = to_account[:1].get()
            Ledger.make_bank_transaction(
                credit_account=to_account.account_no,
                debit_account=account.account_no,
                amount=amount,
                own_message=own_message,
                message=message,
            )
            return redirect(reverse('base:transfer'))
        else:
            return render(request, "base/transaction_create.html", context)


    form = TransactionForm(is_loan)
    form.fields["account"].queryset = Account.objects.filter(customer__id=request.user.id)
    context["form"] = form
    return render(request, "base/transaction_create.html", context)

# LOANS


@login_required
def loans(request):
    context = {}
    if request.user.is_staff:
        context["loans"] = Loan.objects.all().order_by("-created_at")
    else:
        context["loans"] = Loan.objects.filter(customer__id=request.user.id)
        context["customer"] = get_object_or_404(Customer, pk=request.user.id)
    return render(request, "base/loan_list.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff or get_object_or_404(Customer, pk=u.id).rank > 1)
def loan_details(request, account_no):
    context = {}
    loan = get_object_or_404(Loan, account_no=account_no)
    if request.method == "POST":
        form = LoanStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data["status"]
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
            customer = get_object_or_404(Customer, pk=request.user.id)
            loan.customer = customer
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
                Loan.make_bank_transaction(
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

# PROFILE
@login_required
def profile(request):
    context = {}
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        context["form"] = form
        if form.is_valid():
            customer = form.save(commit=False)
            if form.cleaned_data["password"]:
                customer.set_password(form.cleaned_data["password"])
            customer.save()
            update_session_auth_hash(request, form.instance)
            return redirect(reverse('base:profile'))
        else:
            return render(request, 'base/profile_details.html', context)

    customer = get_object_or_404(Customer, pk=request.user.id)
    context["form"] = ProfileForm(instance=customer)
    return render(request, 'base/profile_details.html', context)


@csrf_exempt
def transfer_request(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)

        if 'Token' not in request.headers:
            response = {
                "message": "Provide bank token",
                "status": False
            }
            return JsonResponse(response, status=404)

        if request.headers['Token'] != os.environ['BANK_CONTROLLER_TOKEN']:
            response = {
                "message": "Not correct token",
                "status": False
            }
            return JsonResponse(response, status=405)

        transaction_id = data['id']
        bank_id = data['senderBankId']
        sender_bank_account = data['senderAccountNumber']
        account_number = data['receiverAccountNumber']
        amount = data['amount']
        message = data['message']

        try:
            credit_account = Account.objects.get(account_no=account_number)
        except:
            response = {
                "message": "Could not find account with that number",
                "status": False
            }
            return JsonResponse(response, status=400)

        try:
            Ledger.receive_external_transfer(
                credit_account=credit_account,
                amount=amount,
                message=f"{bank_id}#{sender_bank_account}: {message}",
                transaction_id=transaction_id
            )
        except:
            response = {
                "message": "Could not receive the transfer",
                "status": False
            }
            return JsonResponse(response, status=400)

        response = {
            "message": "Found account - transfer has been made",
            "status": True
        }
        return JsonResponse(response, status=200)
