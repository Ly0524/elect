from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
import re
from django.core.mail import send_mail

from apps.goods.models import Goods
from apps.user.models import User,Address
from apps.order.models import OrderInfo,OrderGoods

from django.conf import settings
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.contrib.auth import authenticate, login,logout
from utils.mixin import LoginRequiredMixin
from django.core.paginator import Paginator
from django_redis import get_redis_connection




# Create your views here.


# 地址：/user/register
class RegisterView(View):
    """用户注册"""

    def get(self, request):
        # 显示注册页面
        return render(request, 'register.html')


    def post(self, request):
        # 进行注册处理
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            # 邮箱不合法
            return render(request, 'register.html', {'errmsg': '邮箱格式不合法'})

        # 校验用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意用户协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()


        # 发送激活邮件，包含激活链接：http://127.0.0.1:8000/user/active/1
        # 激活链接中需要包含用户身份信息,并且要把身份信息进行加密

        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # 转化的是bytes
        token = token.decode()  # 对bytes进行解码为str类型

        # 发邮件
        subject = '天天生鲜欢迎信息'
        message = '邮件正文'
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = '<h1>%s,欢迎您成为注册会员</h1>' \
                       '请点击下面链接激活你的账户<br/>' \
                       '<a href="http://127.0.0.1:8000/user/active/%s">' \
                       'http://127.0.0.1:8000/user/active/%s' \
                       '</a>' % (username, token, token)

        send_mail(subject, message, sender, receiver, html_message=html_message)

        # 发邮件,celery异步执行任务
        # send_register_active_email.delay(email,username,token)

        # 返回应答,跳转到首页
        return redirect(reverse('goods:index'))



class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        # 进行解密，获取要激活的用户信息,第一个参数是秘钥，3600是可以自定义设置的过期时间
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)

            # 获取待激活用户的ID
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# 地址：/user/login
class LoginView(View):
    """登录"""

    def get(self, request):
        """显示登录页面"""
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """进行登录处理"""
        username = request.POST.get('username')
        password = request.POST.get('pwd')


        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转到next_url
                return redirect(next_url)  # HttpResponseRedirect
                # 判断是否需要记住用户名
                remember = request.POST.get('remember')

                if remember == 'on':
                    #     记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')

                #     返回response
                return response


            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

# 地址：/user/logout
class LogoutView(View):
    """退出登录"""
    def get(self,request):
        """退出登录"""
        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse('goods:index'))


# 地址：/user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心信息页面"""

    def get(self, request):
        """显示"""
        # page=user
        # request.user.is_authenticated()
        # 如果用户未登录->AnonymousUser类的一个实例
        # 如果用户登录->User类的一个实例
        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件，叫做user

        # 获取用户的个人信息
        user=request.user
        address=Address.objects.get_default_address(user)



        #获取用户的历史浏览记录
        # sr=StrictRedis(host='192.168.176.129',port='6379',db=1)

        con=get_redis_connection('default')

        history_key='history_%d'%user.id

        # 获取用户最新浏览5个商品的id
        sku_ids=con.lrange(history_key,0,4)

        # 从数据库查询用户浏览的商品的具体信息
        # goods_li=GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res=[]
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的历史商品信息
        goods_list=[]
        for id in sku_ids:
            goods = Goods.objects.get(id=id)
            goods_list.append(goods)

        context = {'page': 'user',
                   'address': address,
                   'goods_list': goods_list}

        return render(request, 'user_center_info.html', context)


# 地址：/user/order
class UserOrderView(LoginRequiredMixin, View):
    """用户中心订单页面"""

    def get(self, request,page):
        """显示"""
        # page=order
        # 获取用户的订单信息
        user=request.user
        orders=OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus=OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历Order_skus计算商品的小计
            for order_sku in order_skus:
                amount=order_sku.count *order_sku.price
                # 动态给order_sku增加属性amount,保存订单商品小计
                order_sku.amount=amount

            # 动态给order增加属性，保存订单状态标题
            order.status_name=OrderInfo.ORDER_STATUS[order.order_status]
            order.order_skus=order_sku

        # 分页
        paginator=Paginator(orders,2)

        try:
            page=int(page)
        except Exception as e:
            page=1
        if page>paginator.num_pages or page<=0:
            page=1

        # 获取第page页的Page实例对象
        order_page=paginator.page(page)
        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1. 总数不足5页，显示全部
        # 2. 如当前页是前3页，显示1-5页
        # 3. 如当前页是后3页，显示后5页
        # 4. 其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,  # 页面范围控制
                   'page': 'order'}


        return render(request, 'user_center_order.html', context)


# 地址：/user/address
class AddressView(LoginRequiredMixin, View):
    """用户中心地址页面"""

    def get(self, request):
        """显示"""
        # page=address
        # 获取登录用户对应User对象
        user = request.user
        # 获取用户的默认收货地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address=Address.objects.get_default_address(user)

        return render(request, 'user_center_site.html', {'page': 'address','address':address})

    def post(self,request):
        """地址的添加"""
        # 接受数据
        receiver=request.POST.get('receiver')
        addr=request.POST.get('addr')
        zip_code=request.POST.get('zip_code')
        phone=request.POST.get('phone')

        # 校验数据
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'emmsg':'数据不完整'})

        if not re.match(r'^1([3-8][0-9]|5[189]|8[6789])[0-9]{8}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号格式不合法'})


        # 业务处理,地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user=request.user
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address=None
        address=Address.objects.get_default_address(user)
        if address:
            is_default=False
        else:
            is_default=True
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答，刷新地址页面
        return redirect(reverse("user:address"))# get请求方式




