"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.contrib import admin
import  xadmin
from .settings import MEDIA_ROOT #配置img地址
from django.views.static import serve #配置img地址
from goods.views import GoodsListViewSet,CategoryViewSet, BannerViewSet, IndexCategoryViewSet
from rest_framework.documentation import include_docs_urls   #drf文档功能引入
from rest_framework.routers import DefaultRouter  #dfr接口注册引入
from rest_framework.authtoken import views #用户认证模式配置url(token)用户的username，passwd都会post到这个url，返回一个token值
from rest_framework_jwt.views import obtain_jwt_token #JWT认证模式
from users.views import SmsCodeViewset #手机注册URL
from users.views import UserViewset
from user_operation.views import UserFavViewset, LeavingMessageViewset, AddressViewset
from trade.views import ShoppingCartViewset, OrderViewset, Alipayview
from django.views.generic import TemplateView
from goods.views_base import GoodsListView

router = DefaultRouter()
#配置goods的url
router.register(r'goods', GoodsListViewSet, base_name='goods')  
router.register(r'categorys', CategoryViewSet, base_name='categorys')
router.register(r'codes', SmsCodeViewset, base_name='codes')   #用户发送code的接口
router.register(r'users', UserViewset, base_name='users')      #用户注册接口
# 收藏URL
router.register(r'userfavs', UserFavViewset, base_name='userfavs')
router.register(r'messages', LeavingMessageViewset, base_name='messages') #留言接口
router.register(r'address', AddressViewset, base_name='address') #收货地址
router.register(r'shopcarts', ShoppingCartViewset, base_name='shopcarts') #购物车URl
router.register(r'orders', OrderViewset, base_name='orders') #订单相关url
router.register(r'banners', BannerViewSet, base_name='banners') #轮播图url
router.register(r'indexgoods', IndexCategoryViewSet, base_name='indexgoods') #首页商品系列数据url





from django.views.decorators.cache import cache_page
urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # url(r'^goods/$',goods_list, name='goods_list'),
    url(r'^', include(router.urls)), 
    url(r'^docs/', include_docs_urls(title='慕学生鲜')),
    url(r'^index/', TemplateView.as_view(template_name="index.html"), name="index"),
    # 富文本相关url
    url(r'^ueditor/', include('DjangoUeditor.urls')),
    #drf自带的token认证模式
    url(r'^api-token-auth/', views.obtain_auth_token), 
    #jwt的认证接口
    url(r'^login/', obtain_jwt_token),

    url(r'^alipay/return/', Alipayview.as_view(),name='alipay'),
    url(r'^do/',  cache_page(5)(GoodsListView.as_view()), ),
]
