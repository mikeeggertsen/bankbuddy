from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from base.forms import AccountCreationForm
from django.urls import reverse

from base.models import Account, Customer


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
    account = get_object_or_404(Account, customer=customer, account_no=account_no)
    context["account"] = account
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
