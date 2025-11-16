from django.urls import path
from posts import views

urlpatterns = [

    # HOME PAGE
    path('', views.index, name='index'),

    # BLOG
    path('allblogs/', views.allblogs, name='allblogs'),
    path('singleblog/<int:id>/', views.singleblog, name='singleblog'),

    # SEARCH
    path('search/', views.search, name='search'),

    # CRUD (new)
    path('post/create/', views.create_post, name='create_post'),
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),

    # LEGACY PAGES
    path('videos/', views.videos, name='videos'),
    path('music/', views.music, name='music'),
    path('ourteam/', views.ourteam, name='ourteam'),
    path('resume/<int:id>/', views.resume, name='resume'),
]
