from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    # Dango Admin
    path('admin/', admin.site.urls),

    # User Authentication
    path('accounts/', include('allauth.urls')),

    # User Profiles
    path('users/', include('users.urls')),

    # Local apps
    path('', include('pages.urls')),
    path('books/', include('books.urls')),
    path('ai/', include('ai.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "pages.views.handler500"
handler404 = "pages.views.handler404"
handler400 = "pages.views.handler400"
handler403 = "pages.views.handler403"

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
