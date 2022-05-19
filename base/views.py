from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from base.models import Account


@login_required
def dashboard(request):
    context = {}
    accounts = Account.objects.all()
    context['accounts'] = accounts
    return render(request, 'base/dashboard.html', context)

# ACCOUNTS


@login_required
def accounts(request):
    context = {}
    accounts = Account.objects.all()
    context['accounts'] = accounts
    return render(request, 'base/account_list.html', context)


@login_required
def transactions(request):
    return HttpResponse('transactions')


@login_required
def profile(request):
    return HttpResponse('profile')


@login_required
def settings(request):
    pass
