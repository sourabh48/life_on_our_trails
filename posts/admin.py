from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Comment, Category, Post, Team,
    Experience, Education, Skill, Profile
)


# ----------------------------
# Comment Admin
# ----------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


# ----------------------------
# Profile Admin (Unified Profile)
# ----------------------------

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("avatar_preview",)

    fieldsets = (
        ("User Information", {
            "fields": (
                "user",
                "avatar",
                "avatar_preview",
                "full_name",
                "profile_picture",  # added here so it saves
            )
        }),
        ("Professional Details", {
            "fields": (
                "designation",
                "bio",
                "about_author",
            )
        }),
        ("Social Links", {
            "fields": (
                "linkedin_url",
                "git_url",
                "insta_url",
            )
        }),
    )

    list_display = ("user", "full_name", "designation", "avatar_preview_small")

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;" />',
                obj.avatar.url
            )
        return "No Avatar"

    def avatar_preview_small(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" style="border-radius:4px;" />',
                obj.avatar.url
            )
        return "—"


# ----------------------------
# Simple Registrations
# ----------------------------

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Team)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
