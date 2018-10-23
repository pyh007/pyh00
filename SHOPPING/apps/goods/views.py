# -*- coding:utf-8 -*-


from django.shortcuts import render

from .serializers import GoodsSerializer, CategorySerializer, BannerSerializer, IndexCategorySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .filters import GoodsFilter
from rest_framework import filters
from .models import Banner
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.authentication import TokenAuthentication


from .models import Goods,GoodsCategory


class GoodsPagination(PageNumberPagination):     #商品列表页自定义分页功能
    page_size = 12   #API接口每页默认显示数据
    page_size_query_param = 'page_size' #加上这个参数可以改变每页显示数据
    page_query_param = 'page'   #页码名字
    max_page_size = 100 #每页 最大显示数据数


class GoodsListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):  #GenericViewSet 继承了ViewSetMixin, generics.GenericAPIView，ViewSetMixin主要重写了as_view方法 试注册方式变了
    """
   商品列表页，搜索，过滤，分页，排序
    """
    queryset = Goods.objects.all()
    throttle_classes = (UserRateThrottle, AnonRateThrottle) #请求限速
    serializer_class = GoodsSerializer #序列化
    pagination_class = GoodsPagination  #分页操作
    # authentication_classes =(TokenAuthentication,)#单独对接口进行token验证
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter) #drf的过滤,排序 ,django_filters实现的单纯过滤, filters.SearchFilter是drf中用来做模糊搜索的，filters.OrderingFilter用来做排序
    filter_class = GoodsFilter                                                            #drf中过滤，搜索，排序都是filter，所以都配置到filter_backends里面
    search_fields = ('name', 'goods_brief', 'goods_desc')  # 和filters.SearchFilter配套使用，配置需要过搜索字段，还有^,=,@,$的用法，=good就是完全匹配，有个好处就是只要在配置字段中，出现关键字都能搜索出来
    ordering_fields = ('sold_num', 'shop_price') #排序功能，和filters.OrderingFilter配套使用，这里配置用来排序的字段。

    def retrieve(self, request, *args, **kwargs): #添加了一个商品的点击数
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)




class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,  viewsets.GenericViewSet):  
    """
    (list:
          商品分类列表数据
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer  # 序列化


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    serializer_class = BannerSerializer
    queryset = Banner.objects.all().order_by('index')


class IndexCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=['生鲜食品', '酒水饮料'])
    serializer_class = IndexCategorySerializer

