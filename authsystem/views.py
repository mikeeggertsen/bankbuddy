from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from authsystem.forms import CustomerCreationForm, UserSignInForm
from base.models import Bank, Customer

def sign_in(request):
    context = {}

    if request.user.is_authenticated:
        return redirect(reverse("base:dashboard"))

    if request.method == "POST":
        form = UserSignInForm(request.POST)
        context["form"] = form
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            print(email, password)
            user = authenticate(request, email=email, password=password)
            print(user)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse("base:dashboard"))
            else:
                context["error"] = "Email or password is incorrect"
                return render(request, "authsystem/sign_in.html", context)

    form = UserSignInForm()
    context["form"] = form
    return render(request, "authsystem/sign_in.html", context)


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("authsystem:sign_in"))


def sign_up(request):
    context = {}

    if request.user.is_authenticated:
        return redirect(reverse("base:dashboard"))

    if request.method == "POST":
        form = CustomerCreationForm(request.POST)
        context["form"] = form
        if form.is_valid():
            try:
                Customer.objects.create_user(**form.cleaned_data)
                return HttpResponseRedirect(reverse('authsystem:sign_in'))
            except Exception:
                context["error"] = "Unable to create customer account. Please try again"
        return render(request, "authsystem/sign_up.html", context)
    
    form = CustomerCreationForm()
    form["bank"].queryset = Bank.objects.all()
    context["form"] = form
    return render(request, "authsystem/sign_up.html", context)


def password_reset(request):
    pass
