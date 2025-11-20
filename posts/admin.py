from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Comment,
    Category,
    Profile,
    ProfileSkill,
    ProfileEducation,
    ProfileExperience
)


# ----------------------------
# PROFILE ADMIN
# ----------------------------

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    readonly_fields = ("avatar_preview",)

    list_display = (
        "user",
        "full_name",
        "designation",
        "team_position",
        "phoneno",
        "main",
        "show_in_team",  # <-- ADD THIS
        "avatar_preview_small",
    )

    list_editable = ("show_in_team", "main",)

    search_fields = (
        "user__username",
        "full_name",
        "designation",
        "team_position",
        "phoneno",
        "github_userid",
    )

    fieldsets = (
        ("User Account", {
            "fields": (
                "user",
                "avatar",
                "avatar_preview",
                "profile_picture",
            )
        }),

        ("Basic Profile", {
            "fields": (
                "full_name",
                "designation",
                "bio",
                "about_author",
            )
        }),

        ("Professional Info", {
            "fields": (
                "team_position",
                "date_of_birth",
                "phoneno",
                "address",
                "about_member",
                "github_userid",
            )
        }),

        ("Main Section (Feature Card)", {
            "fields": (
                "mainwork",
                "mainintro",
                "mainlocation",
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

    # ----------------------------
    # IMAGE PREVIEW HELPERS
    # ----------------------------

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="120" style="border-radius: 8px;" />',
                obj.avatar.url
            )
        return "No Avatar"

    def avatar_preview_small(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" style="border-radius: 4px;" />',
                obj.avatar.url
            )
        return "—"


# ----------------------------
# PROFILE SKILL ADMIN
# ----------------------------

@admin.register(ProfileSkill)
class ProfileSkillAdmin(admin.ModelAdmin):
    list_display = ("profile", "skilltopic", "skillpercentage")
    search_fields = ("skilltopic", "profile__user__username")


# ----------------------------
# PROFILE EDUCATION ADMIN
# ----------------------------

@admin.register(ProfileEducation)
class ProfileEducationAdmin(admin.ModelAdmin):
    list_display = ("profile", "institution", "from_year", "to_year")
    search_fields = ("institution", "profile__user__username")


# ----------------------------
# PROFILE EXPERIENCE ADMIN
# ----------------------------

@admin.register(ProfileExperience)
class ProfileExperienceAdmin(admin.ModelAdmin):
    list_display = ("profile", "institution", "position", "from_year", "to_year")
    search_fields = ("position", "institution", "profile__user__username")


from django.contrib import admin
from django import forms
from .models import Post


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "style": "font-family: monospace;"})
    )

    class Meta:
        model = Post
        fields = "__all__"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "status", "created_at")
    search_fields = ("title", "content")

# ----------------------------
# BASIC MODELS
# ----------------------------

admin.site.register(Category)
admin.site.register(Comment)
