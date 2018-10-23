# -*- coding:utf-8 -*-

import requests   #网络请求库
import json


class YunPian(object):             #云片网发送短信验证码逻辑

    def __init__(self, api_key):   #api_key云片网账号申请的一个值
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):   #参数意思：验证码和发送到那个手机
        parmas = {
            "apikey": self.api_key,
            "mobile": mobile,
            "text": "【慕学生鲜】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code) #format格式化函数
        }

        response = requests.post(self.single_send_url, data=parmas)
        re_dict = json.loads(response.text)
        return re_dict



if __name__ == "__main__":         #测试上边代码
    yun_pian = YunPian("7cdba0a2b05910c7ec6bf25856c88739")
    yun_pian.send_sms("2017", "13980188230")