import json
import os
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from base.forms import AccountCreationForm, LoanForm, ProfileForm, TransactionCreationForm
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from base.models import Account, Loan, Customer, Ledger
from django.contrib.admin.views.decorators import staff_member_required

# DASHBOARD


@login_required
def dashboard(request):
    transaction_filter = request.GET.get('q', '')
    context = {}
    account = get_object_or_404(Account, customer__id=request.user.id)
    context["transactions"] = account.transactions
    if transaction_filter == "credit":
        context["transactions"] = account.transactions.filter(type=1)
    elif transaction_filter == "debit":
        context["transactions"] = account.transactions.filter(type=2)
    context['account'] = account
    return render(request, 'base/dashboard.html', context)

# ACCOUNTS


@login_required
def accounts(request):
    context = {}
    context['accounts'] = Account.objects.filter(customer__id=request.user.id)
    return render(request, 'base/account_list.html', context)


@login_required
def account_details(request, account_no):
    context = {}
    context["account"] = get_object_or_404(
        Account, customer__id=request.user.id, account_no=account_no)
    return render(request, 'base/account_details.html', context)


@login_required
def create_account(request):
    context = {}
    form = AccountCreationForm()
    context["form"] = form
    if request.method == "POST":
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            customer = get_object_or_404(Customer, pk=request.user.id)
            account.customer = customer
            account.save()
            return redirect(reverse('base:accounts'))

    return render(request, "base/account_create.html", context)

# TRANSACTIONS


@login_required
def create_transaction(request):
    context = {}
    is_loan = False
    if request.method == "POST":
        form = TransactionCreationForm(is_loan, request.POST)
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
                return HttpResponseRedirect(reverse('base:transfer'))

            if bank is not None:
                Ledger.make_external_transfer(
                    credit_account=account_no,
                    debit_account=account,
                    amount=amount,
                    own_message=f"{bank.id}#{account_no}: '{own_message}'",
                    message=message,
                    external_bank_id=bank.id
                )

                return HttpResponseRedirect(reverse('base:transfer'))

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

    form = TransactionCreationForm(is_loan)
    form.fields["account"].queryset = Account.objects.filter(
        customer__id=request.user.id)
    context["form"] = form
    return render(request, "base/transaction_create.html", context)

# LOANS


@login_required
def loans(request):
    context = {}
    context["loans"] = Loan.objects.filter(customer__id=request.user.id)
    context["customer"] = get_object_or_404(Customer, pk=request.user.id)
    return render(request, "base/loan_list.html", context)


@login_required
@user_passes_test(lambda u: get_object_or_404(Customer, pk=u.id).rank > 1)
def loan_details(request, account_no):
    context = {}
    context["loan"] = get_object_or_404(Loan, account_no=account_no)
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
    form = TransactionCreationForm(is_loan)
    if request.method == "POST":
        loan = get_object_or_404(Loan, account_no=account_no)
        data = request.POST.copy()
        msg = f"{loan.name} loan payment"
        data.update({"message": msg, "own_message": msg})
        form = TransactionCreationForm(is_loan, data=data)
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


@staff_member_required
def loan_status(request):
    context = {}
    if request.method == "POST":
        pass

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
