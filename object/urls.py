from django.urls import path,include,re_path
from . import views

urlpatterns = [
    re_path(r'^object_manage/$',views.object_manage,name='object_manage'),
]
