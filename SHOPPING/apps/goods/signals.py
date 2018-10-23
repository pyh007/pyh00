from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
#django对model的操作会对全局发个信号，  我们可以捕捉这个信号，在添加自己的逻辑
User = get_user_model()
from user_operation.models import UserFav




#django信号量，截取post_save这个信号，在进行操作
@receiver(post_save, sender=UserFav) #sender就是接受那个model传递过来的
def create_userfav(sender, instance=None, created=False, **kwargs):
    if created:                  #判断是不是新创建的
        # instance = serializer.save()
        goods = instance.goods
        goods.fav_num += 1
        goods.save()

@receiver(pre_delete, sender=UserFav) #sender就是接受那个model传递过来的
def delete_userfav(sender, instance=None, created=False, **kwargs):
        # instance = serializer.save()
        goods = instance.goods
        goods.fav_num -= 1
        goods.save()