# -*- coding:utf-8 -*-

from rest_framework import serializers


from goods.models import Goods, GoodsCategory, GoodsImage, \
    Banner, GoodsCategoryBrand, IndexAd
from django.db.models import Q

# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True, max_length=100)
#     click_num = serializers.IntegerField(default=0)
#
#     def create(self, validated_data): #5-5用处，把前端传过来的数据（如果给前端一个添加商品的接口）保存数据到数据库中
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return Goods.objects.create(**validated_data)


class CategorySerializer3(serializers.ModelSerializer):  #3类
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class CategorySerializer2(serializers.ModelSerializer):  #2类
    sub_cat = CategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    """
    商品类别序列化
    """
    sub_cat= CategorySerializer2(many=True)   #可以在1类下面显示2类，sub_cat参数在设计model时候定义,many参数是表示2类可能有多个是个。必须加上
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image", )


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer() #嵌套一下，可以吧外键category属性在接口中显示出来
    images = GoodsImageSerializer(many=True)     #商品详情页轮播图
    class Meta:
        model = Goods
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fileds = '__all__'


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)   #品牌名
    goods = serializers.SerializerMethodField() #自定义
    sub_cat = CategorySerializer2(many=True)  #二级分类
    ad_goods = serializers.SerializerMethodField()  #广告

    def get_ad_goods(self,obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            good_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context['request']}).data  #在Serializer里面调用Serializer就不会自动加上域名， context={'request': self.context['request']}这个参数是为了加域名

        return goods_json


    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | Q(
            category__parent_category__parent_category_id=obj.id))
        goods_serializer = GoodsSerializer(all_goods, many=True)#在serializer里面传递queryset对象， 在加上.data对象就能得到Json对象
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'