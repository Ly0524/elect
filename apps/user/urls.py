
from django.urls import path,re_path
from django.contrib.auth.decorators import login_required
from apps.user.views import RegisterView,ActiveView,LoginView,UserInfoView,UserOrderView,AddressView,LogoutView

urlpatterns = [
    # path('register/',views.register,name='register'),# 注册
    # path('register_handle/',views.register_handle,name="register_handle"),# 注册处理

    path('register/',RegisterView.as_view(),name='register'),# 注册
    re_path('active/(?P<token>.*)',ActiveView.as_view(),name='active'),# 用户激活
    path('login/',LoginView.as_view(),name='login'),# 登录
    path('logout/',LogoutView.as_view(),name='logout'),# 退出登录

    # path('',login_required(UserInfoView.as_view()),name='user'),# 用户中心信息页
    # path('order/',login_required(UserOrderView.as_view()),name='order'),# 用户中心订单页
    # path('address/',login_required(AddressView.as_view()),name='address'),# 用户中心地址页

    path('',UserInfoView.as_view(),name='user'),# 用户中心信息页
    re_path('order/(?P<page>\d+)',UserOrderView.as_view(),name='order'),# 用户中心订单页
    path('address/',AddressView.as_view(),name='address'),# 用户中心地址页

]