from django.urls import path,include,re_path
from django.contrib import admin
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # re_path(r"^login/$", views.user_login, name = 'user_login'),
    re_path(r"^login/$", auth_views.login, {"template_name":"account/login.html"}, name = 'user_login'),
    re_path(r"^password_reset/$", auth_views.password_reset, name = 'password_reset'),
    re_path(r"^logout/$", auth_views.logout, {"template_name":"account/logout.html"}, name = 'user_logout'),
    re_path(r"^register/$", views.register, name = 'register'),
]