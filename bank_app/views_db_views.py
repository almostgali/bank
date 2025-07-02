from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from decimal import Decimal
from datetime import datetime
import json

# 自定义JSON编码器处理Decimal和datetime类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# 数据库视图查询函数
def get_customer_accounts(customer_id=None):
    """查询客户账户视图"""
    with connection.cursor() as cursor:
        if customer_id:
            cursor.execute("SELECT * FROM customer_account_view WHERE \"customerID\" = %s", [customer_id])
        else:
            cursor.execute("SELECT * FROM customer_account_view")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_transaction_details(card_id=None, customer_id=None, limit=None):
    """查询交易明细视图"""
    with connection.cursor() as cursor:
        query = "SELECT * FROM transaction_detail_view"
        params = []
        
        if card_id:
            query += " WHERE \"cardID\" = %s"
            params.append(card_id)
        elif customer_id:
            query += " WHERE \"customerID\" = %s"
            params.append(customer_id)
            
        query += " ORDER BY \"tradeDate\" DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
            
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_customer_balance_summary(customer_id=None):
    """查询账户余额统计视图"""
    with connection.cursor() as cursor:
        if customer_id:
            cursor.execute("SELECT * FROM customer_balance_summary_view WHERE \"customerID\" = %s", [customer_id])
        else:
            cursor.execute("SELECT * FROM customer_balance_summary_view")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_transaction_type_summary():
    """查询交易类型统计视图"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM transaction_type_summary_view")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

# 视图函数
@login_required(login_url='login')
def customer_accounts_view(request, customer_id=None):
    """客户账户视图页面"""
    if request.user.role != 'admin' and not customer_id:
        raise PermissionDenied('您没有权限查看所有客户账户信息。')
    
    accounts = get_customer_accounts(customer_id)
    
    return render(request, 'bank_app/customer_accounts.html', {
        'accounts': accounts,
        'customer_id': customer_id
    })

@login_required(login_url='login')
def transaction_details_view(request, card_id=None, customer_id=None):
    """交易明细视图页面"""
    if request.user.role != 'admin' and not (card_id or customer_id):
        raise PermissionDenied('您没有权限查看所有交易明细。')
    
    # 从URL参数获取过滤条件
    if not card_id and 'card_id' in request.GET:
        card_id = request.GET.get('card_id')
    
    if not customer_id and 'customer_id' in request.GET:
        customer_id = request.GET.get('customer_id')
    
    transactions = get_transaction_details(card_id, customer_id)
    
    # 确定过滤类型和值，用于模板显示
    filter_type = None
    filter_value = None
    
    if card_id:
        filter_type = 'card'
        filter_value = card_id
    elif customer_id:
        filter_type = 'customer'
        filter_value = customer_id
    
    return render(request, 'bank_app/transaction_details.html', {
        'transactions': transactions,
        'filter_type': filter_type,
        'filter_value': filter_value
    })

@login_required(login_url='login')
def customer_balance_summary_view(request):
    """客户余额统计视图页面"""
    if request.user.role != 'admin':
        raise PermissionDenied('您没有权限查看客户余额统计信息。')
    
    summaries = get_customer_balance_summary()
    
    return render(request, 'bank_app/balance_summary.html', {
        'summaries': summaries
    })

@login_required(login_url='login')
def transaction_type_summary_view(request):
    """交易类型统计视图页面"""
    if request.user.role != 'admin':
        raise PermissionDenied('您没有权限查看交易类型统计信息。')
    
    summaries = get_transaction_type_summary()
    
    return render(request, 'bank_app/transaction_summary.html', {
        'summaries': summaries
    })

@login_required(login_url='login')
def dashboard_view(request):
    """数据库视图仪表盘页面，展示各种统计信息"""
    if request.user.role != 'admin':
        raise PermissionDenied('您没有权限访问数据库视图仪表盘。')
    
    # 获取各种统计数据
    balance_summary = get_customer_balance_summary()
    transaction_summary = get_transaction_type_summary()
    accounts = get_customer_accounts()
    
    # 计算总余额
    total_balance = sum(item['totalBalance'] for item in balance_summary) if balance_summary else 0
    max_balance = max([item['maxBalance'] for item in balance_summary]) if balance_summary else 0
    avg_balance = sum(item['totalBalance'] for item in balance_summary) / sum(item['cardCount'] for item in balance_summary) if balance_summary and sum(item['cardCount'] for item in balance_summary) > 0 else 0
    
    # 计算交易统计
    transaction_count = sum(item['transactionCount'] for item in transaction_summary) if transaction_summary else 0
    total_transaction_amount = sum(item['totalAmount'] for item in transaction_summary) if transaction_summary else 0
    avg_transaction_amount = total_transaction_amount / transaction_count if transaction_count > 0 else 0
    
    # 计算交易类型统计
    deposit_count = next((item['transactionCount'] for item in transaction_summary if item['tradeType'] == '存款'), 0)
    withdraw_count = next((item['transactionCount'] for item in transaction_summary if item['tradeType'] == '取款'), 0)
    transfer_count = next((item['transactionCount'] for item in transaction_summary if item['tradeType'] == '转账'), 0)
    
    # 计算客户和卡片统计
    customer_count = len(balance_summary) if balance_summary else 0
    card_count = sum(item['cardCount'] for item in balance_summary) if balance_summary else 0
    lost_card_count = sum(1 for account in accounts if account['IsReportLoss'] == '是') if accounts else 0
    
    return render(request, 'bank_app/db_views_dashboard.html', {
        'customer_count': customer_count,
        'card_count': card_count,
        'lost_card_count': lost_card_count,
        'transaction_count': transaction_count,
        'total_transaction_amount': total_transaction_amount,
        'avg_transaction_amount': avg_transaction_amount,
        'total_balance': total_balance,
        'max_balance': max_balance,
        'avg_balance': avg_balance,
        'deposit_count': deposit_count,
        'withdraw_count': withdraw_count,
        'transfer_count': transfer_count
    })