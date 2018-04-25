from django.urls import path,include,re_path
from . import views

urlpatterns = [
    re_path(r'^object_manage/$',views.object_manage,name='object_manage'),
    re_path(r'^object_manage_del/$',views.object_manage_del,name='object_manage_del'),
    re_path(r'^report_post/$',views.report_post,name='report_post'),
]
