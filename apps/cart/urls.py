from apps.cart.views import *
from django.urls import path

urlpatterns = [
    path('add/',CartAddView.as_view(),name='add'),# 购物车记录添加
    path('',CartInfoView.as_view(),name='cart'),# 显示购物车页
    path('update/',CartUpdateView.as_view(),name='update'),# 购物车数据更新
    path('delete',CartDeleteView.as_view(),name='delete'),# 删除购物车的商品记录


]