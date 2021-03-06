"""verticalmind URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^market/',include(('market.urls','market'),namespace='market')),
    path('', RedirectView.as_view(url='/market/',permanent=True)),
    re_path(r'^account/', include(('account.urls','account'),namespace='account')),
    re_path(r'^object/', include(('object.urls','object'),namespace = 'object')),
] + static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
