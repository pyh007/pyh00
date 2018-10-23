from django.shortcuts import render
from rest_framework import serializers
from .models import Goods
import time
from rest_framework.authentication import SessionAuthentication
from utils.permissions import IsOwnerOrReadOnly
from rest_framework import viewsets
from rest_framework import mixins
from .serializers import ShopCartSerializers, ShopCarDetailSerializer, OrderSerializers, OrderDetailSerializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated      #验证是否登录
from .models import ShoppingCart, OrderInfo, OrderGoods
from utils.alipay import AliPay
from MxShop.settings import ali_pub_key_path, private_key_path
from datetime import datetime
from rest_framework.response import Response
from django.shortcuts import redirect
from django.http import HttpResponse


class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    List：
        获取购物车详情
    create：
        加入购物车
    delete：
        删除购物记录
    """
    permission_classes = (
    IsAuthenticated, IsOwnerOrReadOnly)  # IsAuthenticated验证用户是否登录，未登录访问抛401错误，IsOwnerOrReadOnly当前用户只能删除自己收藏的
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # 验证方式
    # serializer_class = ShopCartSerializers
    lookup_field = 'goods_id'  # RetrieveModelMixin中有个get_object函数的参数lookup_field会查找主键id（）默认，现在改为查找商品id为了方便前端。


    def perform_create(self, serializer):  #修改商品库存
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_record.nums
        saved_record = serializer.save()
        nums = saved_record.nums - existed_nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()
    def get_serializer_class(self):
        if self.action == "list":
            return ShopCarDetailSerializer
        else:
            return ShopCartSerializers


    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)  #list只返回当前用户的goods



class OrderViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理
    List：
        获取订单
    delete：
        删除订单
    create：
        新增订单
    """
    permission_classes = (
    IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # 验证方式
    serializer_class = OrderSerializers
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializers


    def perform_create(self, serializer):
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)  #获取当前用户购物车商品
        for shop_cart in shop_carts:  #循环
            order_goods = OrderGoods() #实例化订单的商品详情，生成订单的商品详情这张表
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()

            shop_cart.delete()  #提交订单后，把东西从购物车中删除掉
        return order


from  rest_framework.views import APIView
class Alipayview(APIView):
    def get(self, request):
        """
        处理支付宝的return_url返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            appid="2016091700534479",
            app_notify_url="http://118.24.29.15:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://118.24.29.15:8000/alipay/return/"
        )

        verify_re = alipay.verify(processed_dict, sign)

        if verify_re:
            # order_sn = processed_dict.get('out_trade_no', None)
            # trade_no = processed_dict.get('trade_no', None)
            # trade_status = processed_dict.get('trade_status', None)
            #
            # existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            # for existed_order in existed_orders:
            #     existed_order.pay_status = trade_status
            #     existed_order.trade_no = trade_no
            #     existed_order.pay_time = datetime.now()
            #     existed_order.save()

            response = redirect("index")
            response.set_cookie("nextPath", "pay", max_age=3) #配合前端的逻辑
            return response
        else:
            response = redirect("index")
            return response
    def post(self, request): #异步请求
        """
        处理支付宝的notify_url
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value

        sign = processed_dict.pop('sign', None)

        alipay = AliPay(
            appid="2016091700534479",
            app_notify_url="http://118.24.29.15:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://118.24.29.15:8000/alipay/return/"
        )

        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return HttpResponse("success")





