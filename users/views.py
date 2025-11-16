from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = False  # mark as customer
        user.save()

        messages.success(request, "Account created. Please log in.")
        return redirect("login")

    return render(request, "auth.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("index")  # your homepage
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "auth.html")


def logout_view(request):
    logout(request)
    return redirect("login")
