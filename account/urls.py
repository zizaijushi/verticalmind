from django.urls import path,re_path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    # log in and out urls
    # re_path(r"^login/$", views.user_login, name = 'user_login'),
    re_path(r"^login/$", auth_views.login, {"template_name":"account/login.html"}, name = 'user_login'),
    re_path(r"^logout/$", auth_views.logout, {"template_name":"account/logout.html"}, name = 'user_logout'),
    re_path(r"^register/$", views.register, name = 'register'),
    re_path(r"^register_done/$",views.register_done,name = 'register_done'),

    # password change urls
    re_path(r"^password_change/$", auth_views.password_change,{
        "post_change_redirect":"account/password_change_down"
    },name = 'password_change'),
    re_path(r"^password_change_down/$",auth_views.password_change_done, name = 'password_change_down'),

    # password reset urls
    re_path(r"^password_reset/$",auth_views.password_reset,{
        "template_name":"account/password_reset_form.html",
        "email_template_name":"account/password_reset_email.html",
        "post_reset_redirect":"/account/password_reset_done",
        "subject_template_name":"account/password_reset_subject.txt",
    }, name = 'password_reset'),
    re_path(r"^password_reset_done/$", auth_views.password_change_done, {
        "template_name": "account/password_reset_done.html",
    }, name='password_reset_done'),

    re_path(r"^password_reset_confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/",auth_views.password_reset_confirm,{
        "template_name":"account/password_reset_confirm.html",
        "post_reset_redirect":"/account/password_reset_complete"
    },name = 'password_reset_confirm'),

    re_path(r"^password_reset_complete/$",auth_views.password_reset_complete,{
        "template_name":"account/password_reset_complete.html",
    },name = 'password_reset_complete'),

    re_path(r"^user_page/$",views.user_profile, name = 'user_page'),
]