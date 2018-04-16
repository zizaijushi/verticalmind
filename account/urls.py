from django.urls import path,re_path
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # re_path(r"^login/$", views.user_login, name = 'user_login'),
    re_path(r"^login/$", auth_views.login, {"template_name":"account/login.html"}, name = 'user_login'),
    re_path(r"^logout/$", auth_views.logout, {"template_name":"account/logout.html"}, name = 'user_logout'),
    re_path(r"^register/$", views.register, name = 'register'),
    url(r"^password_change/$", auth_views.password_change,
        {"post_change_redirect":"account/password_change_down"},name = 'password_change'),
    url(r"^password_change_down/$",auth_views.password_change_done, name = 'password_change_down'),
]