from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import *
from utils.mixin import LoginRequiredMixin
from django.shortcuts import render

# 地址：/cart/add
class CartAddView(View):
    """购物车增加模块"""
    def post(self,request):
        """购物车记录添加"""
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res':0,'errmsg':'请先登录'})
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 校验数据
        if not all([sku_id, count]):
            return JsonResponse({'res': 0, 'errmsg': '数据不完整'})

        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 1, 'errmsg': '商品数目出错'})
        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

        # 业务处理：添加购物车记录
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id

        # 先尝试获取sku_id的值 -> hget cart_key 属性: cart_key[sku_id]
        # 如果sku_id在hash中不存在，hget返回None
        cart_count=conn.hget(cart_key,sku_id)
        if cart_count:
            # redis中存在该商品，进行数量累加
            count+=int(cart_count)

        # 校验商品的库存
        # if count>sku.stock:
        #     return JsonResponse({'res':4,'errmsg':'商品库存不足'})

        # 设置hash中sku_id对应的值
        # hset ->如sku_id存在,更新数据,如sku_id不存在，追加数据
        conn.hset(cart_key,sku_id,count)

        # 获取用户购物车中的条目数
        cart_count=conn.hlen(cart_key)

        return JsonResponse({ 'message': '添加成功','res':5,'cart_count':cart_count})


# /cart/
class CartInfoView(LoginRequiredMixin, View):
    """购物车显示"""
    def get(self, request):
        user = request.user
        # 获取用户购物车的商品信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # {'商品id': 商品数量}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        # 保存用户购物车中商品总数目和总价格
        total_count = 0
        total_price = 0
        # 遍历获取商品信息
        for sku_id, count in cart_dict.items():
            # 根据商品id获取商品信息
            sku = Goods.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku对象添加一个属性amount,保存商品小计
            sku.amount = amount
            # 动态给sku对象添加一个属性,保存购物车中对应商品的数量
            sku.count = int(count)

            # 添加
            skus.append(sku)

            # 累加计算商品的总数目和总价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {'total_count': total_count,
                   'total_price': total_price,
                   'skus': skus}

        return render(request, 'cart.html', context)


# 更新购物车记录
# 采用ajax post请求
# 前端需要传递的参数: 商品id(sku_id) 更新商品数量(count)
# /cart/update
class CartUpdateView(View):
    """购物车记录更新"""
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 校验添加的商品数量
        # noinspection PyBroadException
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理: 更新购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id

        # 校验商品的库存
        # if count > sku.stock:
        #     return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # 更新
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车中商品的总件数{'1':5,'2':3}
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '更新成功'})


# 删除购物车记录
# 采用ajax post请求
# 前端需要传递的参数: 商品id(sku_id)
# /cart/delete
class CartDeleteView(View):
    """购物车记录删除"""
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')

        # 数据校验
        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品id'})

        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

        # 业务处理: 删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id

        # 删除 hdel
        conn.hdel(cart_key, sku_id)

        # 计算用户购物车中商品的总件数{'1':5,'2':3}
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        return JsonResponse({'res': 3, 'total_count': total_count, 'message': '删除成功'})




