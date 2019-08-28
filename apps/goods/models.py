from django.db import models
from db.base_model import BaseModel

# Create your models here.
class GoodsType(BaseModel):
    """商品类型模型类"""
    name = models.CharField(max_length=20, verbose_name='种类名称')
    image = models.ImageField(upload_to='type', verbose_name='商品类型图片')
    desc=models.CharField(max_length=256,verbose_name='商品类型描述')

    class Meta:
        db_table = 'df_goods_type'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Goods(BaseModel):
    """商品模型类"""
    status_choices = (
        (0, '下线'),
        (1, '上线')
    )
    type = models.ForeignKey('GoodsType', on_delete=models.CASCADE, verbose_name='商品种类')
    name = models.CharField(max_length=20, verbose_name='商品名称')
    desc = models.CharField(max_length=256, verbose_name='商品简介')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='原价')
    new_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='促销价')
    image = models.ImageField(upload_to='goods/', verbose_name='商品图片')
    sales = models.IntegerField(default=0, verbose_name='商品销量')


    class Meta:
        db_table = 'df_goods'
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
