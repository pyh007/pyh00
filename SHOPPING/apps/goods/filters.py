# -*- coding:utf-8 -*-


#自定义过滤

import django_filters
from django.db.models import Q

from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet): #django的filter
    """
    商品的过滤类
    """
    pricemin = django_filters.NumberFilter(name='shop_price', help_text="最低价格", lookup_expr='gte') #gte大于等于，gt大于
    pricemax = django_filters.NumberFilter(name='shop_price', lookup_expr='lte')#lte小于等于
    top_category = django_filters.NumberFilter(method='top_category_filter') #z自定义过滤,为了前端页面，点击1类商品，能够展现1类商品下的2类和3类商品

    # name = django_filters.CharFilter(name='name', lookup_expr='icontains') #模糊查询名字，加上i是忽略大小写,不加lookup_expr，就是必须全部匹配的意思,后面用drf的filter进行模糊搜索，有局限性只能在名字的字段搜索。

    def top_category_filter(self, queryset, name, value):                           #自定义过滤，6-5章，为了展示某一类下面的所有商品
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(
            category__parent_category__parent_category_id=value)) #queryset=goods的queryset



    class Meta:
        model = Goods
        # fields = ['name', 'shop_price', ]
        fields = ['pricemin', 'pricemax', 'is_hot', 'is_new']
