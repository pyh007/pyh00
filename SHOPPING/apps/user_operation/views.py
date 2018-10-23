from rest_framework import viewsets
from rest_framework import mixins

from .models import UserFav, UserLeavingMessage, UserAddress
from .serializers import UserFavSerializers, UserFavDetailSerializers, LeavingMessageSerializers, AddressSerializers
from rest_framework.permissions import IsAuthenticated      #验证是否登录
from utils.permissions import IsOwnerOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import BasicAuthentication, SessionAuthentication,TokenAuthentication


class UserFavViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):                 #收藏可以理解为添加一条记录所以有mixins.CreateModelMixin，取消就是删除所以 mixins.DestroyModelMixin，
                                                                                           #mixins.ListModelMixin是为了获取收藏的列表（比如一个用户会收藏很多),RetrieveModelMixin生成一个usl根据主键id获取单条数据

    """
    list:
        获取用户收藏列表
    retrieve：
        判断某个商品是否已经收藏
     create:
        收藏商品
    """
    # queryset = UserFav.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)    #IsAuthenticated验证用户是否登录，未登录访问抛401错误，IsOwnerOrReadOnly当前用户只能删除自己收藏的
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # 验证方式
    lookup_field = 'goods_id'  #RetrieveModelMixin中有个get_object函数的参数lookup_field会查找主键id（）默认，现在改为查找商品id为了方便前端。
     # 查找goods_id这个操作只会在return UserFav.objects.filter(user=self.request.user)里面操作，所以不会查找出其他用户的id


    def get_queryset(self):                  #只能获取当前用户的UserFav
        return UserFav.objects.filter(user=self.request.user)

    # def perform_create(self, serializer): #添加收藏+1功能 (也可以用信号量)
    #     instance = serializer.save()
    #     goods = instance.goods
    #     goods.fav_num += 1
    #     goods.save()


    def get_serializer_class(self):      #
        if self.action == "list":
            return UserFavDetailSerializers
        elif self.action == "create":
            return UserFavSerializers

        return UserFavSerializers

class LeavingMessageViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """
     List:
         获取留言
     Create:
         创建留言
      Delete
         删除留言
    """

    permission_classes = (
    IsAuthenticated, IsOwnerOrReadOnly)  # IsAuthenticated验证用户是否登录，未登录访问抛401错误，IsOwnerOrReadOnly当前用户只能删除自己收藏的
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # 验证方式
    serializer_class = LeavingMessageSerializers
    def get_queryset(self):                  #只能获取当前用户的UserFav
        return UserLeavingMessage.objects.filter(user=self.request.user)


class AddressViewset(viewsets.ModelViewSet):
    """"
    收货地址管理
    List:
        获取地址
    Create:
        创建地址
    Update：
        更新收货地址
    Deleta:
        删除地址
    """


    permission_classes = (
    IsAuthenticated, IsOwnerOrReadOnly)  # IsAuthenticated验证用户是否登录，未登录访问抛401错误，IsOwnerOrReadOnly当前用户只能删除自己收藏的
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # 验证方式
    serializer_class = AddressSerializers
    def get_queryset(self):                  #只能获取当前用户的UserFav
        return UserAddress.objects.filter(user=self.request.user)






