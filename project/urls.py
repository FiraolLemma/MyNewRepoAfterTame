# project/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from users.views import user_login

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('users/', include('users.urls')),
    path('login/', user_login, name='login'),
    path('poultrys/', include('poultrys.urls', namespace='poultrys')),
    path(
        'items/poultry/',
        RedirectView.as_view(
            pattern_name='poultrys:index',
            permanent=True,
            query_string=True,
        ),
    ),
    path(
        'items/egg-sellers/',
        RedirectView.as_view(
            pattern_name='poultrys:egg_sellers',
            permanent=True,
            query_string=True,
        ),
    ),
    path(
        'items/chicken-sellers/',
        RedirectView.as_view(
            pattern_name='poultrys:chicken_sellers_list',
            permanent=True,
            query_string=True,
        ),
    ),
    path(
        'items/<int:pk>/',
        RedirectView.as_view(
            pattern_name='poultrys:item_detail',
            permanent=True,
            query_string=True,
        ),
    ),
    path(
        'items/',
        RedirectView.as_view(
            pattern_name='poultrys:item_list',
            permanent=True,
            query_string=True,
        ),
    ),
    path('items/', include('poultrys.legacy_urls', namespace='poultryitems')),
    path('conversation/', include('conversation.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('contact/', include('contact.urls' , namespace='contact')),
    path('companies/', include('companies.urls')),
    path('dairys/', include('dairys.urls')),
    path(
        'clothings/',
        RedirectView.as_view(
            pattern_name='clothings:clothing_list',
            permanent=True,
            query_string=True,
        ),
    ),
    path('cart/', include('cart.urls', namespace='cart')),
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin-app/", include("admin_app.urls", namespace="admin_app")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
