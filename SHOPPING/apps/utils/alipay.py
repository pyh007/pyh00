__author__ = 'pyh'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path  #私钥文件名路径
        self.app_private_key = None #读文件并进行加密
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())
            # print(fp.read())

        self.alipay_public_key_path = alipay_public_key_path #公钥文件名称路径
        with open(self.alipay_public_key_path) as fp:
            # print(fp.read())
            self.alipay_public_key = RSA.import_key(fp.read())  #读写文件并进行加密


        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"  #沙箱的url
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do" #正式的url

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)  #可变参数，因还还可以天其他可选参数，都会放到biz_content这个dict里面
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url) #生成公共参数
        return self.sign_data(data) #签名

    def build_body(self, method, biz_content, return_url=None):   #生成公共参数
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data): #签名
        data.pop("sign", None) #如果有sign这个参数 就删除。 签名不能带这个参数
        # 排序后的字符串
        unsigned_items = self.ordered_data(data) #对参数的排序，支付宝文档要求，在字母排序
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))  #字符串生成进行签名
        # ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):  #对参数的排序，支付宝文档要求，在字母排序
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key #私钥
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")  #移除回城换行符
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):  #验证返回url
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)



if __name__ == "__main__":
    # return_url = 'http://127.0.0.1:8000/alipay/return/?charset=utf-8&out_trade_no=20170202aaa&method=alipay.trade.page.pay.return&total_amount=100.00&sign=Ha%2B5%2F9RKzgC0sLsSV8MIa6fbLanKKuRQkFmT1xrsd5%2BNtU9QXA3jysrnVBJKuB%2FSQ4EeMy1EHXm42rZunKf7qc9m0UiWKkGsFng2OWg8rmCSp36r6yw%2FyUmsYIUGtTSDKhcMAk1dE4dG100kKk3AdCtL3hxZezXsWsresw8wyJBTJWK59Tte5vzVdOTgLaM3LFCB8TGTUa9XKbLB3dP9YcwJfraZDKp2nxIyYBgWTaE0Li%2BkAfcXUkDYVKTSCCsC7xAwg1oH7Kwks9QwtrpyOwMDoZa9NDptcunqrDJD9LRxiS6A8PvDIs7PVoIjxPnauVRoXbstnoPcVYaiNUd7Nw%3D%3D&trade_no=2018082021001004790200547180&auth_app_id=2016091700534479&version=1.0&app_id=2016091700534479&sign_type=RSA2&seller_id=2088102176078444&timestamp=2018-08-20+17%3A57%3A49'
    # o = urlparse(return_url)
    # query = parse_qs(o.query)
    # processed_query = {}
    # ali_sign = query.pop("sign")[0]


    alipay = AliPay(
        appid="2016091700534479",
        app_notify_url="http://118.24.29.15:8000/alipay/return/",
        app_private_key_path="../trade/keys/private_2048.txt",   #个人私钥
        alipay_public_key_path="../trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
        return_url="http://118.24.29.15:8000/alipay/return/"
    )

    # for key, value in query.items():
    #     processed_query[key] = value[0]
    # print (alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
            subject="测试订单2",
            out_trade_no="20170202yhg",
            total_amount=100,
            return_url="http://118.24.29.15:8000/alipay/return/"
        )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

    print(re_url)