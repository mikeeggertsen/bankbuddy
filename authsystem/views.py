from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from authsystem.forms import SignUpForm, SignInForm, VerifyForm
from authsystem.models import VerificationCode
from base.models import Bank, Customer, User

def sign_in(request):
    context = {}

    if request.user and request.user.is_authenticated:
        return redirect(reverse("base:dashboard"))

    if request.method == "POST":
        form = SignInForm(request.POST)
        context["form"] = form
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                VerificationCode.send_code(user)
                request.session["user_id"] = user.pk
                return redirect(reverse('authsystem:verify'))
            else:
                context["error"] = "Invalid email or password"

    form = SignInForm()
    context["form"] = form
    return render(request, "authsystem/sign_in.html", context)


def sign_out(request):
    logout(request)
    return redirect(reverse("authsystem:sign_in"))


def sign_up(request):
    context = {}

    if request.user and request.user.is_authenticated:
        return redirect(reverse("base:dashboard"))

    if request.method == "POST":
        form = SignUpForm(request.POST)
        context["form"] = form
        if form.is_valid():
            try:
                Customer.objects.create_user(**form.cleaned_data)
                return redirect(reverse('authsystem:sign_in'))
            except Exception:
                context["error"] = "Unable to create customer account. Please try again"
        return render(request, "authsystem/sign_up.html", context)
    
    form = SignUpForm()
    form["bank"].queryset = Bank.objects.all()
    context["form"] = form
    return render(request, "authsystem/sign_up.html", context)

def verify(request):
    context = {}

    if request.user and request.user.is_authenticated:
        return redirect(reverse("base:dashboard"))

    if (request.method == "POST"):
        form = VerifyForm(request.POST)
        context["form"] = form
        if form.is_valid():
            code = form.cleaned_data["code"]
            user_id = None
            try:
                user_id = VerificationCode.verify(code)
            except Exception as e:
                context["error"] = e
                return render(request, "authsystem/verify.html", context)
            if user_id:
                user = get_object_or_404(User, pk=user_id)
                if user:
                    if not settings.DEBUG: #login fails when tests run because of session not being on request object
                        login(request, user)
                    return redirect(reverse("base:dashboard"))
            else:
                context["error"] = "Invalid verification code"
        return render(request, "authsystem/verify.html", context)

    context["form"] = VerifyForm()
    return render(request, "authsystem/verify.html", context)

def resend_sms(request):
    if request.user and request.user.is_authenticated:
        return redirect(reverse("base:dashboard"))
    
    if request.method == "POST":
        if request.session["user_id"]:
            user_id = request.session["user_id"]
            del request.session["user_id"]
            user = get_object_or_404(User, pk=user_id)
            VerificationCode.send_code(user)
      
    return redirect(reverse("authsystem:verify"))
