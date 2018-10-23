
import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime
from datetime import timedelta
from rest_framework.validators import UniqueValidator

from .models import VerifyCode

from MxShop.settings import REGEX_MOBILE

User = get_user_model()


class SmsSerializer(serializers.Serializer):        #为什么不用model.Serializer 因为model里面有个code是必填字段7-8
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):   #单独对电话号码验证，就重载validate_mobile这个函数
        """
        验证手机号码
        :param data:
        :return:
        """

        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():  #count（）统计是否存在，
            raise serializers.ValidationError('手机号码已注册')


        # 验证手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago, mobile=mobile).count():  #取出同时满足2个条件的，只有存在就报错
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return mobile
class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email", "mobile")

class UserRegSerializer(serializers.ModelSerializer):          #error_messages自定义的错误信息。 write_only，因为code被删除了在后面，设置了write_only，就不会序列化cdeo了
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])   #drfUniqueValidatordrf验证器，validators验证唯一性。username在数据库中是否唯一。

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )                          #style参数 在API接口输入密码时候就是密文。write_only：password不能返回给前段，容易被截获，所以也不用序列化

    # def create(self, validated_data):  #重载 create方法   #因为存密码的时候ModelSerializer直接保存，没做处理，需要处理成密文在保存到数据库
    #     user = super(UserRegSerializer, self).create(validated_data=validated_data)  #这个方法取出user相当于model的UserProfile，
    #     user.set_password(validated_data["password"])       #set_password加密password  set_password方法是AbstractUser类里面的方法。AbstractUser是UserProfile继承的一个类
    #     user.save()
    #     return user

    def validate_code(self, code):    #验证code合法性。 1：输入错误的验证码 2：输入不符合长度的验证码，3验证码过期了。
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)         看似简单直接把数据取出来，其实存在问题。如果我发送了多次验证码，验证码可能会相同。就会有几条数据就会抛出异常
        # except Exception as e :
        # pass
        # except VerifyCode.DoesNotExist as e:                                                                 没有这条数据，用get也会抛异常，如果不捕获异常，就不会执行。所以反而更麻烦。
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass                                         #在ModelSerializer中，前端传过来的值都会放在initial_data里面。  username等价于mobile
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")   #首先查询code是否存在，先判断前端传来的mobile是否存在（mobile和code是绑定的）。
        if verify_records:                                                                                       #按时间排序，只要最新的有这个mobile就行了，没必要所有数据库的mobile都验证
            last_record = verify_records[0]  #如果有的话就取最新的一条记录

            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)  #获取到5分钟前的时间。
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")               #5分钟之前的时间 > 添加时间就是过期了

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")                #Post过来的code和数据库中code不一样就是验证码错误

        else:
            raise serializers.ValidationError("验证码错误")        #如果查到数据数据 也报验证码错误

    def validate(self, attrs):              #attrs是serializers序列化后的所有字段
        attrs["mobile"] = attrs["username"]
        del attrs["code"]                #删除code字段，验证完code过后，不需要保存到数据库 所以直接删除。 保留账号密码就行了
        return attrs



    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")