from django import forms

from .models import Business, BusinessLocation, QuoteRequest


class BusinessRegistrationForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            "category",
            "name",
            "tagline",
            "description",
            "cover_image",
            "contact_email",
            "contact_phone",
            "website_url",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class BusinessLocationForm(forms.ModelForm):
    class Meta:
        model = BusinessLocation
        fields = [
            "label",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "pincode",
            "country",
            "google_maps_url",
        ]


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["full_name", "email", "phone", "additional_details"]
        widgets = {
            "additional_details": forms.Textarea(attrs={"rows": 4}),
        }
