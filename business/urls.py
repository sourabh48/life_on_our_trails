from django.urls import path
from . import views

app_name = "marketplace"

urlpatterns = [
    path("", views.business_list, name="business_list"),

    path("signup/", views.business_signup, name="business_signup"),
    path("partner/register/", views.partner_register, name="partner_register"),
    path("owner/dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("owner/quote/<int:quote_id>/", views.owner_quote_detail, name="owner_quote_detail"),

    path("<int:business_id>/service/<int:service_id>/add/", views.add_to_cart, name="add_to_cart"),
    path("<int:business_id>/service/<int:service_id>/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("<int:business_id>/request-quote/", views.request_quote, name="request_quote"),
    path("quote/<int:quote_id>/thank-you/", views.quote_thank_you, name="quote_thank_you"),

    path("<slug:category_slug>/<slug:slug>/", views.business_detail, name="business_detail"),
]
