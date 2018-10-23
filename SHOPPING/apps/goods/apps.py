from django.apps import AppConfig


class GoodsConfig(AppConfig):
    name = 'goods'
    verbose_name = '商品'

    def ready(self):  # 配置信号量
        import goods.signals
