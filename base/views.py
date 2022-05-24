import json
import os
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from base.forms import AccountCreationForm, ProfileForm, TransactionCreationForm
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from base.models import Account, Customer, Ledger

# DASHBOARD


@login_required
def dashboard(request):
    transaction_filter = request.GET.get('q', '')
    context = {}
    try:
        account = Account.objects.filter(
            customer__id=request.user.id)[:1].get()
        transactions = Ledger.objects.filter(
            to_account__customer__id=request.user.id)
        if transaction_filter == "credit":
            transactions = transactions.filter(type=1)
        elif transaction_filter == "debit":
            transactions = transactions.filter(type=2)
        context['account'] = account
        context['transactions'] = transactions
    except:
        pass

    return render(request, 'base/dashboard.html', context)

# ACCOUNTS


@login_required
def accounts(request):
    context = {}
    customer = get_object_or_404(Customer, pk=request.user.id)
    accounts = Account.objects.filter(customer=customer)
    context['accounts'] = accounts
    return render(request, 'base/account_list.html', context)


@login_required
def account_details(request, account_no):
    context = {}
    account = get_object_or_404(
        Account, customer__id=request.user.id, account_no=account_no)
    transactions = Ledger.objects.filter(to_account=account)
    context["account"] = account
    context["transactions"] = transactions
    return render(request, 'base/account_details.html', context)


@login_required
def create_account(request):
    context = {}
    form = AccountCreationForm()
    context["form"] = form
    if request.method == "POST":
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            customer = get_object_or_404(Customer, pk=request.user.id)
            account = Account(**form.cleaned_data)
            account.customer = customer
            account.save()
            return HttpResponseRedirect(reverse('base:accounts'))

    return render(request, "base/account_create.html", context)

# TRANSACTIONS


@login_required
def create_transaction(request):
    context = {}
    if request.method == "POST":
        form = TransactionCreationForm(request.POST)
        context["form"] = form
        if form.is_valid():
            from_account = form.cleaned_data["from_account"]
            account_no = form.cleaned_data["to_account"]
            amount = form.cleaned_data["amount"]
            own_message = form.cleaned_data["own_message"]
            message = form.cleaned_data["message"]
            bank = form.cleaned_data["bank"]
            to_account = Account.objects.filter(account_no=account_no)

            if bank is not None:
                to_account = to_account.filter(customer__bank=bank)

            to_account = to_account[:1].get()
            ledger = Ledger()
            ledger.make_bank_transaction(
                to_acc=to_account,
                from_acc=from_account,
                transaction_amount=amount,
                own_message=own_message,
                message=message,
                )
            return HttpResponseRedirect(reverse('base:transfer'))
        else:
            return render(request, "base/transaction_create.html", context)


    form = TransactionCreationForm()
    form.fields["from_account"].queryset = Account.objects.filter(
        customer__id=request.user.id)
    context["form"] = form
    return render(request, "base/transaction_create.html", context)


@login_required
def profile(request):
    context = {}
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        context["form"] = form
        if form.is_valid():
            customer = form.save()
            customer.set_password(form.cleaned_data["password"])
            customer.save()
            update_session_auth_hash(request, form.instance)
            return HttpResponseRedirect(reverse('base:profile'))
        else: 
            return render(request, 'base/profile_details.html', context)

    customer = Customer.objects.get(pk=request.user.id)
    context["form"] = ProfileForm(instance=customer)
    return render(request, 'base/profile_details.html', context)


@login_required
def settings(request):
    pass


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

        account_number = data['receiverAccountNumber']
        amount = data['amount']
        message = data['message']

        try:
            account = Account.objects.get(account_no=account_number)
        except:
            response = {
                "message": "Could not find account with that number",
                "status": False
            }
            return JsonResponse(response, status=404)

        response = {
            "message": "Found account - transfer can be made",
            "status": True
        }
        return JsonResponse(response, status=200)
