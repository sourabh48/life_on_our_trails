# user/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from posts.models import Profile  # Profile is defined in posts app


# -----------------------------
# SIGN UP
# -----------------------------
@never_cache
def signup_view(request):
    """
    Registration endpoint used by the sign-up side of auth.html.
    Creates both User and Profile.
    """
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        bio = (request.POST.get("bio") or "").strip()
        location = (request.POST.get("location") or "").strip()
        linkedin = (request.POST.get("linkedin") or "").strip()
        avatar = request.FILES.get("avatar")

        # ---- validation ----
        if not username or not full_name or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "That username is already taken.")
            return redirect("signup")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("signup")

        # ---- create user ----
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
        )

        # ---- create / populate profile ----
        profile = Profile.objects.create(
            user=user,
            full_name=full_name or username,
            bio=bio,
            mainlocation=location,
            linkedin_url=linkedin,
        )

        if avatar:
            profile.avatar = avatar
            profile.save()

        messages.success(request, "Account created successfully. Please sign in.")
        return redirect("login")

    # GET – render the combined auth template
    return render(request, "auth.html")


# -----------------------------
# LOG IN
# -----------------------------
@never_cache
def custom_login(request):
    """
    Login endpoint used by sign-in side of auth.html.
    """
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("index")  # adjust if your home url name differs
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "auth.html")


# -----------------------------
# LOG OUT
# -----------------------------
@never_cache
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# -----------------------------
# AJAX USERNAME CHECK
# -----------------------------
@require_GET
def check_username(request):
    """
    GET /check-username/?username=foo
    Returns JSON:
    {
        "exists": true/false
    }
    """
    username = (request.GET.get("username") or "").strip()
    exists = False
    if username:
        exists = User.objects.filter(username__iexact=username).exists()

    return JsonResponse({"exists": exists})
