from apps.order.views import *
from django.urls import path,re_path

urlpatterns = [
    path('place/',OrderPlaceView.as_view(),name='place'),# 提交订单显示
    path('commit/',OrderCommitView.as_view(),name='commit'),# 订单创建
    path('pay/',OrderPayView.as_view(),name='pay'),# 订单支付
    path('check/',CheckPayView.as_view(),name='check'),# 查询支付交易结果
    re_path('comment/(?P<order_id>.+)/',OrderCommentView.as_view(),name='comment'),# 订单评论
]