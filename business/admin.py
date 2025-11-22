from django.contrib import admin

from .models import (
    BusinessCategory,
    Business,
    BusinessLocation,
    BusinessService,
    BusinessWorkImage,
    QuoteRequest,
    QuoteServiceItem,
)


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class BusinessLocationInline(admin.TabularInline):
    model = BusinessLocation
    extra = 0


class BusinessServiceInline(admin.TabularInline):
    model = BusinessService
    extra = 0


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "owner", "is_active", "is_approved", "is_locked")
    list_filter = ("category", "is_active", "is_approved", "is_locked")
    search_fields = ("name", "owner__username", "tagline")
    inlines = [BusinessLocationInline, BusinessServiceInline]


admin.site.register(BusinessWorkImage)


class QuoteServiceItemInline(admin.TabularInline):
    model = QuoteServiceItem
    extra = 0


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "business", "full_name", "status", "created_at")
    list_filter = ("status", "business")
    search_fields = ("full_name", "email", "business__name")
    inlines = [QuoteServiceItemInline]
