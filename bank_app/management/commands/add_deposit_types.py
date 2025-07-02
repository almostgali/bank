from django.core.management.base import BaseCommand
from bank_app.models import Deposit

class Command(BaseCommand):
    help = '添加默认的存款类型数据'

    def handle(self, *args, **options):
        deposit_types = [
            {'savingName': '活期存款', 'descrip': '随时存取，利率较低，适合日常使用'},
            {'savingName': '定期一年', 'descrip': '存期一年，利率适中，到期可自动转存'},
            {'savingName': '定期三年', 'descrip': '存期三年，利率较高，提前支取有利息损失'},
            {'savingName': '定期五年', 'descrip': '存期五年，利率最高，长期稳定收益'},
            {'savingName': '零存整取', 'descrip': '按月存入固定金额，到期一次性支取本息'},
            {'savingName': '教育储蓄', 'descrip': '专为子女教育设计，享受国家贴息优惠'},
        ]

        count = 0
        for deposit_type in deposit_types:
            _, created = Deposit.objects.get_or_create(
                savingName=deposit_type['savingName'],
                defaults={'descrip': deposit_type['descrip']}
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'成功添加存款类型: {deposit_type["savingName"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'存款类型已存在: {deposit_type["savingName"]}'))

        self.stdout.write(self.style.SUCCESS(f'成功添加 {count} 个存款类型'))