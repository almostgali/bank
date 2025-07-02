import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_project.settings')
django.setup()

# 导入模型
from bank_app.models import Deposit

def add_default_deposit():
    # 创建默认存款类型
    default_deposit, created = Deposit.objects.get_or_create(
        pk=1,
        defaults={
            'savingName': '标准账户',
            'descrip': '标准银行账户'
        }
    )
    
    if created:
        print('成功创建默认存款类型: 标准账户')
    else:
        print('默认存款类型已存在: 标准账户')

if __name__ == '__main__':
    print('开始创建默认存款类型...')
    add_default_deposit()
    print('默认存款类型创建完成！')