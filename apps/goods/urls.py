from apps.goods.views import ListView,IndexView,DetailView
from django.urls import path,re_path
from django.conf.urls.static import static
from django.conf import settings

app_name='apps.goods'


urlpatterns = [
    path('',IndexView.as_view(),name='index'),# 首页
    re_path('goods/(?P<goods_id>\d+)',DetailView.as_view(),name='detail'),# 详情页
    re_path('list/(?P<type_id>\d+)/(?P<page>\d+)',ListView.as_view(),name='list'),# 列表页

]


