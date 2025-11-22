from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import BusinessRegistrationForm, BusinessLocationForm, QuoteRequestForm
from .models import (
    Business,
    BusinessCategory,
    BusinessLocation,
    BusinessService,
    QuoteRequest,
    QuoteServiceItem,
)


# ------------- internal helpers -----------------

def _cart_key(business_id: int) -> str:
    return f"quote_cart_{business_id}"


def _get_cart(request, business_id: int):
    return request.session.get(_cart_key(business_id), [])


def _save_cart(request, business_id: int, cart):
    request.session[_cart_key(business_id)] = cart
    request.session.modified = True


def _clear_cart(request, business_id: int):
    request.session.pop(_cart_key(business_id), None)
    request.session.modified = True


# ------------- public listing & detail -----------

def business_list(request):
    q = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    category_slug = request.GET.get("category", "").strip()

    queryset = Business.objects.filter(is_active=True, is_approved=True, is_locked=False)

    if q:
        queryset = queryset.filter(
            Q(name__icontains=q)
            | Q(tagline__icontains=q)
            | Q(description__icontains=q)
            | Q(services__name__icontains=q)
        ).distinct()

    if city:
        queryset = queryset.filter(locations__city__icontains=city).distinct()

    active_category = None
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
        active_category = category_slug

    categories = BusinessCategory.objects.filter(is_active=True).order_by("name")

    return render(request, "marketplace/business_list.html", {
        "businesses": queryset,
        "categories": categories,
        "q": q,
        "city": city,
        "active_category": active_category,
    })


def business_detail(request, category_slug, slug):
    business = get_object_or_404(
        Business,
        slug=slug,
        category__slug=category_slug,
    )

    # lock logic: if not visible, only owner/admin sees page
    if not business.is_visible_public():
        if not (
                request.user.is_authenticated
                and (request.user.is_superuser or request.user == business.owner)
        ):
            return render(request, "marketplace/business_locked.html", {
                "business": business,
            })

    services = business.services.filter(is_active=True).order_by("sort_order", "name")
    locations = business.locations.filter(is_active=True)
    photos = business.work_images.all().order_by("-created_at")

    cart = _get_cart(request, business.id)

    return render(request, "marketplace/business_detail.html", {
        "business": business,
        "services": services,
        "locations": locations,
        "photos": photos,
        "cart_items": cart,
    })


# ------------- cart & quote (customer) ----------

@login_required
def add_to_cart(request, business_id, service_id):
    if request.method != "POST":
        biz = get_object_or_404(Business, id=business_id)
        return redirect("marketplace:business_detail",
                        category_slug=biz.category.slug,
                        slug=biz.slug)

    business = get_object_or_404(Business, id=business_id)

    if not business.is_visible_public() and not (
            request.user.is_superuser or request.user == business.owner
    ):
        messages.error(request, "This business is not available.")
        return redirect("marketplace:business_list")

    service = get_object_or_404(BusinessService, id=service_id, business=business)

    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 1
    quantity = max(1, quantity)

    cart = _get_cart(request, business.id)

    for item in cart:
        if item.get("service_id") == service.id:
            item["quantity"] += quantity
            break
    else:
        cart.append({
            "service_id": service.id,
            "name": service.name,
            "quantity": quantity,
        })

    _save_cart(request, business.id, cart)
    messages.success(request, "Added to quote list.")
    return redirect("marketplace:business_detail",
                    category_slug=business.category.slug,
                    slug=business.slug)


@login_required
def remove_from_cart(request, business_id, service_id):
    business = get_object_or_404(Business, id=business_id)
    cart = _get_cart(request, business.id)
    cart = [item for item in cart if item.get("service_id") != service_id]
    _save_cart(request, business.id, cart)

    messages.info(request, "Removed from quote list.")
    return redirect("marketplace:business_detail",
                    category_slug=business.category.slug,
                    slug=business.slug)


@login_required
def request_quote(request, business_id):
    business = get_object_or_404(Business, id=business_id)

    if not business.is_visible_public() and not (
            request.user.is_superuser or request.user == business.owner
    ):
        messages.error(request, "This business is not available.")
        return redirect("marketplace:business_list")

    cart = _get_cart(request, business.id)
    if not cart:
        messages.error(request, "Please add at least one service to your quote list.")
        return redirect("marketplace:business_detail",
                        category_slug=business.category.slug,
                        slug=business.slug)

    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.business = business
            quote.customer = request.user

            location_id = request.POST.get("location_id")
            if location_id:
                try:
                    quote.location = BusinessLocation.objects.get(
                        id=location_id,
                        business=business,
                    )
                except BusinessLocation.DoesNotExist:
                    pass

            quote.status = QuoteRequest.Status.NEW
            quote.save()

            for item in cart:
                service_id = item.get("service_id")
                quantity = item.get("quantity", 1)

                service = BusinessService.objects.filter(
                    id=service_id,
                    business=business
                ).first()

                QuoteServiceItem.objects.create(
                    quote=quote,
                    service=service,
                    custom_label=item.get("name", ""),
                    quantity=quantity,
                )

            _clear_cart(request, business.id)
            messages.success(request, "Your quote request has been submitted.")
            return redirect("marketplace:quote_thank_you", quote_id=quote.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["full_name"] = request.user.get_full_name() or request.user.username
            initial["email"] = request.user.email
        form = QuoteRequestForm(initial=initial)

    locations = business.locations.filter(is_active=True)

    return render(request, "marketplace/request_quote.html", {
        "business": business,
        "form": form,
        "cart_items": cart,
        "locations": locations,
    })


@login_required
def quote_thank_you(request, quote_id):
    quote = get_object_or_404(QuoteRequest, id=quote_id)

    if not (
            (quote.customer and quote.customer == request.user)
            or quote.business.owner == request.user
            or request.user.is_superuser
    ):
        messages.error(request, "You are not allowed to view this quote.")
        return redirect("marketplace:business_list")

    return render(request, "marketplace/quote_thank_you.html", {
        "quote": quote,
    })


# ------------- business signup & owner flows ----

def business_signup(request):
    """
    Separate signup page for business owners: /business/signup/
    """
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("marketplace:business_signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("marketplace:business_signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("marketplace:business_signup")

        user = User.objects.create_user(username=username, email=email, password=password)
        auth_login(request, user)

        messages.success(request, "Business account created. Please register your business details.")
        return redirect("marketplace:partner_register")

    return render(request, "marketplace/business_signup.html")


@login_required
def partner_register(request):
    """
    First business registration form for a logged-in user.
    """
    if request.method == "POST":
        b_form = BusinessRegistrationForm(request.POST, request.FILES)
        l_form = BusinessLocationForm(request.POST)

        if b_form.is_valid() and l_form.is_valid():
            business = b_form.save(commit=False)
            business.owner = request.user
            business.is_active = True
            business.is_approved = False  # admin approves later
            business.save()

            location = l_form.save(commit=False)
            location.business = business
            location.save()

            messages.success(
                request,
                "Your business has been submitted. Admin will review and approve it."
            )
            return redirect("marketplace:owner_dashboard")
    else:
        b_form = BusinessRegistrationForm()
        l_form = BusinessLocationForm()

    return render(request, "marketplace/partner_register.html", {
        "b_form": b_form,
        "l_form": l_form,
    })


@login_required
def owner_dashboard(request):
    businesses = Business.objects.filter(owner=request.user)
    quotes = QuoteRequest.objects.filter(
        business__owner=request.user
    ).select_related("business").order_by("-created_at")[:50]

    return render(request, "marketplace/owner_dashboard.html", {
        "businesses": businesses,
        "quotes": quotes,
    })


@login_required
def owner_quote_detail(request, quote_id):
    quote = get_object_or_404(
        QuoteRequest,
        id=quote_id,
        business__owner=request.user,
    )

    if request.method == "POST":
        status = request.POST.get("status") or quote.status
        quoted_amount = request.POST.get("quoted_amount", "").strip()
        owner_notes = request.POST.get("owner_notes", "")

        quote.status = status
        quote.owner_notes = owner_notes

        if quoted_amount:
            try:
                quote.quoted_amount = float(quoted_amount)
            except ValueError:
                messages.error(request, "Invalid quoted amount. Please enter a number.")
                return redirect("marketplace:owner_quote_detail", quote_id=quote.id)

        quote.save()
        messages.success(request, "Quote updated successfully.")
        return redirect("marketplace:owner_quote_detail", quote_id=quote.id)

    return render(request, "marketplace/owner_quote_detail.html", {
        "quote": quote,
    })
