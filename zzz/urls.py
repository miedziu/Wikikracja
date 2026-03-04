from home import views as hv
from obywatele import views as ov
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from filebrowser.sites import site
from django.views.generic import RedirectView

from typing import List
from django.urls import URLPattern, URLResolver

urlpatterns: List[URLPattern | URLResolver] = [
    path('', include('home.urls')),
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/login/'}, name='logout'),
    path('login/', hv.RememberLoginView.as_view(), name='login'),
    path('haslo/', hv.haslo, name='haslo'),
    path('change_email/', ov.change_email, name='change_email'),
    path('accounts/confirm-email/', RedirectView.as_view(url='/obywatele/onboarding/', permanent=False)),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('admin/filebrowser/', site.urls),
    # path('grappelli/', include('grappelli.urls')), # only needed for django-filebrowser but it is actually breaking admin panel
    path('tinymce/', include('tinymce.urls')),
    path('favicon.ico',RedirectView.as_view(url='/static/home/images/favicon.ico')),  # TODO: robots.txt this way?
    path('captcha/', include('captcha.urls')),

    path('glosowania/',     include('glosowania.urls', namespace='glosowania')),
    path('obywatele/',      include('obywatele.urls', namespace='obywatele')),
    path('elibrary/',       include('elibrary.urls', namespace='elibrary')),
    path('chat/',           include('chat.urls', namespace='chat')),
    path('bookkeeping/',    include('bookkeeping.urls', namespace='bookkeeping')),
    path('board/',          include('board.urls', namespace='board')),
    path('events/',         include('events.urls', namespace='events')),
    path('tasks/',          include('tasks.urls', namespace='tasks')),
    path("__reload__/",     include("django_browser_reload.urls")),
]

# Serve static files only in DEBUG mode (WhiteNoise handles this in production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Media files (user uploads) - must be served in all environments
# In production, Django will serve these (inefficient but works)
# TODO: Consider adding nginx sidecar for better performance
from django.views.static import serve
from django.urls import re_path
from django.http import HttpResponse, Http404
import os
import logging

logger = logging.getLogger(__name__)

def debug_serve_media(request, path):
    """Serve media files with debug logging."""
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    logger.info(f"[MEDIA DEBUG] Request path: {request.path}")
    logger.info(f"[MEDIA DEBUG] MEDIA_ROOT: {settings.MEDIA_ROOT}")
    logger.info(f"[MEDIA DEBUG] Full path: {full_path}")
    logger.info(f"[MEDIA DEBUG] File exists: {os.path.exists(full_path)}")
    
    if os.path.exists(full_path):
        logger.info(f"[MEDIA DEBUG] File size: {os.path.getsize(full_path)}")
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    else:
        logger.warning(f"[MEDIA DEBUG] File NOT FOUND: {full_path}")
        # List directory contents for debugging
        dir_path = os.path.dirname(full_path)
        if os.path.exists(dir_path):
            logger.info(f"[MEDIA DEBUG] Directory contents: {os.listdir(dir_path)[:10]}")
        raise Http404(f"Media file not found: {path}")

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', debug_serve_media),
]

'''
allauth:
Note that you do not necessarily need the URLs provided by django.contrib.auth.urls.
Instead of the URLs login, logout, and password_change (among others),
you can use the URLs provided by allauth: account_login, account_logout, account_set_password…
'''
