from django.contrib import admin
from django.core.cache import cache
from apps.goods.models import GoodsType, Goods


# Register your models here.

admin.site.register(GoodsType)
admin.site.register(Goods)

