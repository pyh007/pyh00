# -*- coding: utf-8 -*-
__author__ = 'pyh'
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
#django对model的操作会对全局发个信号，  我们可以捕捉这个信号，在添加自己的逻辑
User = get_user_model()
#django信号量，截取post_save这个信号，在进行操作
@receiver(post_save, sender=User) #sender就是接受那个model传递过来的
def create_user(sender, instance=None, created=False, **kwargs):
    if created:                  #判断是不是新创建的
        password = instance.password
        instance.set_password(password) #instance就是user所以可以调用set_password方法
        instance.save()

