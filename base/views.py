from email import message
import json
import os
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pkg_resources import require
from base.forms import AccountCreationForm
from django.urls import reverse

from base.models import Account, Customer, Ledger


@login_required
def dashboard(request):
    context = {}
    context['accounts'] = accounts
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
    customer = get_object_or_404(Customer, pk=request.user.id)
    account = get_object_or_404(
        Account, customer=customer, account_no=account_no)
    transactions = Ledger.objects.filter(to_account=account)
    context["account"] = account
    context["transactions"] = transactions
    return render(request, 'base/account_details.html', context)


def create_account(request):
    context = {}
    form = AccountCreationForm()
    context["form"] = form
    if request.method == "POST":
        form = AccountCreationForm(request.POST)
        if (form.is_valid()):
            customer = get_object_or_404(Customer, pk=request.user.id)
            account = Account(**form.cleaned_data)
            account.customer = customer
            account.save()
            return HttpResponseRedirect(reverse('base:accounts'))

    return render(request, "base/account_create.html", context)


@login_required
def transactions(request):
    return HttpResponse('transactions')


@login_required
def profile(request):
    return HttpResponse('profile')


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

        response = {
            "message": "yo",
            "status": False
        }

        return JsonResponse(response, status=200)
