import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_project.settings')
django.setup()

# 导入模型
from bank_app.models import Deposit

def add_deposit_types():
    deposit_types = [
        {'savingName': '活期存款', 'descrip': '随时存取，利率较低'},
        {'savingName': '定期一年', 'descrip': '存期一年，利率适中'},
        {'savingName': '定期三年', 'descrip': '存期三年，利率较高'},
        {'savingName': '定期五年', 'descrip': '存期五年，利率最高'},
        {'savingName': '零存整取', 'descrip': '按月存入固定金额'},
        {'savingName': '教育储蓄', 'descrip': '专为子女教育设计'},
    ]

    count = 0
    for deposit_type in deposit_types:
        _, created = Deposit.objects.get_or_create(
            savingName=deposit_type['savingName'],
            defaults={'descrip': deposit_type['descrip']}
        )
        if created:
            count += 1
            print(f'成功添加存款类型: {deposit_type["savingName"]}')
        else:
            print(f'存款类型已存在: {deposit_type["savingName"]}')

    print(f'成功添加 {count} 个存款类型')

if __name__ == '__main__':
    print('开始添加存款类型数据...')
    add_deposit_types()
    print('存款类型数据添加完成！')