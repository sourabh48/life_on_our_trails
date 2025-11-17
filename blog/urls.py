from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from posts import views as post_views

urlpatterns = [

    # AUTH
    path('login/', post_views.custom_login, name='login'),
    path('signup/', post_views.signup, name='signup'),
    path('logout/', post_views.custom_logout, name='logout'),

    # PROFILE
    path('profile/<str:username>/', post_views.profile, name='profile'),
    path('profile/<str:username>/edit/', post_views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/change-password/', post_views.change_password, name='change_password'),
    path('dashboard/', post_views.dashboard, name='dashboard'),

    # HOME
    path('', post_views.index, name='index'),

    # BLOG LIST
    path('allblogs/', post_views.allblogs, name='allblogs'),

    # CREATE MUST COME BEFORE DYNAMIC ROUTES
    path('post/create/', post_views.create_post, name='create_post'),

    # CRUD (order matters!)
    path('post/edit/<int:post_id>/', post_views.edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', post_views.delete_post, name='delete_post'),

    # SINGLE BLOG
    path('singleblog/<int:id>/', post_views.singleblog, name='singleblog'),

    # SEARCH
    path('search/', post_views.search, name='search'),

    # STATIC PAGES
    path('videos/', post_views.videos, name='videos'),
    path('music/', post_views.music, name='music'),
    path('ourteam/', post_views.ourteam, name='ourteam'),
    path('resume/<int:id>/', post_views.resume, name='resume'),

    # ADMIN PANEL
    path('admin/', admin.site.urls),
]

# STATIC + MEDIA
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
