from rest_framework import serializers
from goods.models import Goods
from .models import ShoppingCart,OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer
import time
from utils.alipay import AliPay
from MxShop.settings import ali_pub_key_path, private_key_path

class ShopCarDetailSerializer(serializers.ModelSerializer):  #
    goods = GoodsSerializer(many=False) #一个购物车的记录只对应一个goods
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class ShopCartSerializers(serializers.Serializer):  #购物车
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label='数量', min_value=1, error_messages={
        'min_value': '购买数量不能小于一',
        'required': '请选择购买数量'
    })
    goods = serializers.PrimaryKeyRelatedField(required=True, label='商品', queryset=Goods.objects.all())   #外键，因为不是modelsSerializer，所以需要加上queryset


    def create(self, validated_data):
        user = self.context["request"].user  #Serializer里面request存在context里面
        nums = validated_data['nums']
        goods = validated_data['goods']

        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        if existed:
            existed = existed[0]  #如果存在取第一个
            existed.nums += nums  # 原来基础上+nums
            existed.save() #保存

        else:
            existed = ShoppingCart.objects.create(**validated_data) #或者创建一条记录

        return existed
    def update(self, instance, validated_data): #修改商品数量, 因为不是继承的MidekSerializer,要进行更新操作，需要重写方法，
        instance.nums = validated_data['nums'] #instance是ShoppingCart的实例化对象
        instance.save()
        return instance



class OrderGoodsSerialzier(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerialzier(many=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):  # 命名规则是签名加一个get_
        alipay = AliPay(
            appid="2016091700534479",
            app_notify_url="http://118.24.29.15:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://118.24.29.15:8000/alipay/return/"
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url
    class Meta:
        model = OrderInfo
        fields = '__all__'

class OrderSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    pay_status = serializers.CharField(read_only=True) #订单状态
    trade_no = serializers.CharField(read_only=True) #支付宝返回的交易号
    order_sn = serializers.CharField(read_only=True) #后台生成的订单号
    pay_time = serializers.DateTimeField(read_only=True) #支付时间
    alipay_url = serializers.SerializerMethodField(read_only=True) #支付地址

    def get_alipay_url(self, obj):#命名规则是签名加一个get_
        alipay = AliPay(
            appid="2016091700534479",
            app_notify_url="http://118.24.29.15:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://118.24.29.15:8000/alipay/return/"
        )

        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
        )
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url


    def generate_order_sn(self):    #生成订单号
        # 当前时间+userid+随机数
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context['request'].user.id, ranstr=random_ins.randint(10, 99))

        return order_sn

    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs
    class Meta:
        model = OrderInfo
        fields = '__all__'








