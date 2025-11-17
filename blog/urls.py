from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from posts import views
from posts import views as post_views

urlpatterns = [

# AUTH ROUTES
    path('login/', post_views.custom_login, name='login'),
    path('signup/', post_views.signup, name='signup'),
    path('logout/', post_views.custom_logout, name='logout'),

                  path('profile/<str:username>/', views.profile, name='profile'),
                  path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
                  path('profile/<str:username>/change-password/', views.change_password, name='change_password'),

    # HOME PAGE
    path('', views.index, name='index'),

    # BLOG LIST
    path('allblogs/', views.allblogs, name='allblogs'),

    # SINGLE BLOG
    path('singleblog/<int:id>/', views.singleblog, name='singleblog'),

    # SEARCH
    path('search/', views.search, name='search'),

    # CRUD
    path('post/create/', views.create_post, name='create_post'),
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),

    # STATIC PAGES
    path('videos/', views.videos, name='videos'),
    path('music/', views.music, name='music'),
    path('ourteam/', views.ourteam, name='ourteam'),
    path('resume/<int:id>/', views.resume, name='resume'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
