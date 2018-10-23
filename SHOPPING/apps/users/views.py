from django.shortcuts import render

# Create your views here.
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from random import choice
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from MxShop.settings import APIKEY
from utils.yunpian import YunPian
from .models import VerifyCode


User = get_user_model()#get_user_model函数会在setting配置中找到重载的 'users.UserProfile',就可以的带User，因为一些第三方开发可能不知道user放在那个model下的




class CustomBackend(ModelBackend):   #自定义用户验证，必须继承ModelBackend，重写authenticate函数，
    """
    自定义用户验证，因为JWT认证默认的是取用户的username和password，无法用mobile登录
    """
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):         #check_password会对前端传来的密码加密，因为django存储的密码是加密的，全都传来的是明文。
                return user
        except Exception as e:
            return None

class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):    #短信发送接口
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  #拿到的serializer就是   serializer_class = SmsSerializer中的SmsSerializer
        serializer.is_valid(raise_exception=True)  # raise_exception=True这个参数的意思还是，如果验证错误直接抛异常，不进入下面了。drf捕捉到就会抛出400异常

        mobile = serializer.validated_data["mobile"]   #取出serializer中的mobile，能到这步已经验证过了，肯定有mobile

        yun_pian = YunPian(APIKEY)         #实例化

        code = self.generate_code()     #调用发送code的函数

        sms_status = yun_pian.send_sms(code=code, mobile=mobile)  #调用发送短信的函数

        if sms_status["code"] != 0:                             #如果返回的code不为0代表失败，报错
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:                                                    #为0，保存code和mobile  返回状态
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()

            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)


                                                                                                                  #CreateModelMixin 注册用户
class UserViewset(CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet): #mixins.RetrieveModelMixin获取某个用户的详情(自动注册url，/userfav/userid/)
    """
    用户，注册，修改  获取
    """
    # serializer_class = UserRegSerializer
    queryset = User.objects.all()
    # permission_classes = (permissions.IsAuthenticated, ) #IsAuthenticated验证用户是否登录
    #注册后如果自动登录，就需要返回一个Token。
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication )          #单独对接口进行token验证

    def get_serializer_class(self):      #因为注册的是序列化的UserRegSerializer只有code ，usernam等，所以根据动作，动态序列化对象
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer
    #
    # # permission_classes = (permissions.IsAuthenticated, )
    def get_permissions(self):  # 继承在APIview中，        因为设置全局用户验证，用户注册的时候不可能登录账号去注册，所以需要动态的验证
        if self.action == "retrieve":  # 返回用户数据，就是retrieve动作，需要验证 （只有使用了GenericViewSet才会有self保存antion，使用APIview是没有的）
            return [permissions.IsAuthenticated()]  # 因为需要验证登录，所以也需要authentication_classes验证
        elif self.action == "create":  # create动作，post注册动作不需要验证，返回空列表就行。其他情况也返回空列表
            return []

        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.perform_create(serializer)   #拿到user
        re_dict = serializer.data
        payload = jwt_payload_handler(user)     #生成payload
        re_dict["token"] = jwt_encode_handler(payload)   #生成token并将token添加到参数里面
        re_dict["name"] = user.name if user.name else user.username   #并将用户返回会去。

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)


    def get_object(self):    #方法继承在GenericAPIView， 重载get_object方法，不管输入什么id，都返回当前登录用户（），只有RetrieveModelMixin和DestroyModelMixin用get_object
        return self.request.user

    def perform_create(self, serializer):    #重载这个函数返回这个对象，  create函数中就可以拿到user
        return serializer.save()





