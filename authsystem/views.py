from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from authsystem.forms import CustomerCreationForm, UserSignInForm
from base.models import Bank, Customer


def sign_in(request):
    context = {}

    if request.user.is_authenticated:
        return redirect(reverse("base:accounts"))

    context["form"] = UserSignInForm()
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("base:dashboard"))
        else:
            context["error"] = "Bad username or password"
    return render(request, "authsystem/sign_in.html", context)


def sign_out(request):
    logout(request)
    return render(request, "authsystem/sign_in.html")


def sign_up(request):
    context = {}

    if request.user.is_authenticated:
        return redirect(reverse("base:accounts"))

    if request.method == "POST":
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            try:
                Customer.objects.create_user(**form.cleaned_data)
                return HttpResponseRedirect(reverse('authsystem:sign_in'))
            except ValueError:
                context["error"] = "Unable to create customer account. Please try again"
        else:
            context["error"] = "Unable to create customer account. Please try again"
    
    form = CustomerCreationForm()
    form["bank"].queryset = Bank.objects.all()
    context["form"] = form
    return render(request, "authsystem/sign_up.html", context)


def password_reset(request):
    pass
