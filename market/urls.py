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
from django.urls import path,include,re_path
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from . import views

urlpatterns = [
    path("", views.indexView.as_view(), name = 'index'),
    re_path(r"^minifullswitchswitch/$", views.minifullswitchView.as_view(), name = 'minifullswitch'),
    re_path(r"^keywords/$", views.keywordsView.as_view(), name = 'keywords'),
    re_path(r"^fund/$",views.fund.as_view(),name = 'fund'),
    # re_path(r"^fund/(?P<fundcode>[\d]+[.]*[\w]*)",views.fund.as_view(),name = 'fund'),
    # path("glxu",views.glxu, name = 'glxu'),
    # path("bbzhang",views.bbzhang, name = 'bbzhang')
    # path('<str:TRADE_CODE>',views.detail),
]