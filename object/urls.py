from django.urls import path,include,re_path
from . import views

urlpatterns = [
    re_path(r'^dailyreplay_list/$',views.Dailyreply_list,namespade='dailyreplay_list'),
]
