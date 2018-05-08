from django.urls import path,include,re_path
from . import views

urlpatterns = [
    re_path(r'^object_manage/$',views.object_manage,name='object_manage'),
    re_path(r'^object_manage_del/$',views.object_manage_del,name='object_manage_del'),
    re_path(r'^report_post/$',views.report_post,name='report_post'),
    re_path(r'^object_list/(?P<object_id>[\d]+)/$',views.object_list,name='object_list'),
    re_path(r'^report/(?P<id>\d+)/(?P<slug>[-\w]+)/$',views.report,name='report'),
    re_path(r'^report_edit/(?P<report_id>\d+)/$',views.report_edit,name='report_edit'),
    re_path(r'^report_like/$',views.report_like,name='report_like'),
]