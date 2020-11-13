from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from posts.views import index, allblogs, singleblog, search, videos, ourteam, resume

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='post-list'),
    path('allblogs/', allblogs, name='post-list'),
    path('singleblog/<id>/', singleblog, name='post-detail'),
    path('search/', search, name='search'),
    path('videos/', videos),
    path('ourteam/', ourteam, name='member-list'),
    path('resume/<id>/', resume, name='member-detail'),
    path('tinymce/', include('tinymce.urls')),
    path(r'hitcount/', include('hitcount.urls', namespace='hitcount')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
