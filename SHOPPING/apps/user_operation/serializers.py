from rest_framework import serializers
from .models import UserFav, UserLeavingMessage, UserAddress
from rest_framework.validators import UniqueTogetherValidator
from goods.serializers import GoodsSerializer


class UserFavDetailSerializers(serializers.ModelSerializer):
    goods = GoodsSerializer()
    class Meta:
        model = UserFav
        fields = ( 'goods', 'id')

class UserFavSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )                #这个用处，直接获取当前登录用户
    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏"
            )
        ]   #验证user和goods两个参数是否联合起来唯一性。如果有了，就报错已经收藏（需要在model中Meta信息里设置unique_together = ("user", "goods") 这个参数  ）
        fields = ('user', 'goods', 'id')  #id为数据库自动生成的主见id，  因为为了后期删除方便，就把id也返回

class LeavingMessageSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M') #这个参数只返回不提交, 格式化时间让前段显示更好看
    class Meta:
        model = UserLeavingMessage
        fields = ('user', 'message_type', 'subject', 'message', 'file', 'id', 'add_time') #加id是为了删除


class AddressSerializers(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = UserAddress
        fields = ('user', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'id') #加id是为了删除