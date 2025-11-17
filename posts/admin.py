from django.contrib import admin

from .models import (
    Comment, Author, Category, Post, Team,
    Experience, Education, Skill, Profile
)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


# SIMPLE REGISTRATIONS
admin.site.register(Profile)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Team)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)