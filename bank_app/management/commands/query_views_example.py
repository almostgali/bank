from django.core.management.base import BaseCommand
from django.db import connection
import json
from decimal import Decimal
from datetime import datetime

# 自定义JSON编码器处理Decimal和datetime类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

class Command(BaseCommand):
    help = '展示如何查询和使用数据库视图的示例'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始查询数据库视图示例'))
        
        # 查询客户账户视图
        customer_accounts = self.get_customer_accounts()
        self.stdout.write(self.style.SUCCESS(f'客户账户视图数据 (前5条)：'))
        self.print_json(customer_accounts[:5])
        
        # 查询交易明细视图
        transaction_details = self.get_transaction_details()
        self.stdout.write(self.style.SUCCESS(f'交易明细视图数据 (前5条)：'))
        self.print_json(transaction_details[:5])
        
        # 查询账户余额统计视图
        balance_summary = self.get_customer_balance_summary()
        self.stdout.write(self.style.SUCCESS(f'账户余额统计视图数据：'))
        self.print_json(balance_summary)
        
        # 查询交易类型统计视图
        transaction_summary = self.get_transaction_type_summary()
        self.stdout.write(self.style.SUCCESS(f'交易类型统计视图数据：'))
        self.print_json(transaction_summary)
        
        self.stdout.write(self.style.SUCCESS('数据库视图查询示例完成'))
    
    def get_customer_accounts(self):
        """查询客户账户视图"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer_account_view")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_transaction_details(self):
        """查询交易明细视图"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM transaction_detail_view ORDER BY tradeDate DESC")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_customer_balance_summary(self):
        """查询账户余额统计视图"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer_balance_summary_view")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_transaction_type_summary(self):
        """查询交易类型统计视图"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM transaction_type_summary_view")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def print_json(self, data):
        """格式化输出JSON数据"""
        json_str = json.dumps(data, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
        self.stdout.write(json_str)