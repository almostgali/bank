from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import UserInfo, CardInfo, TradeInfo, Deposit, Bankuser
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '登录成功！')
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误！')
    return render(request, 'bank_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '已成功退出！')
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if Bankuser.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在！')
            return render(request, 'bank_app/register.html')

        if password1 != password2:
            messages.error(request, '两次输入的密码不一致！')
            return render(request, 'bank_app/register.html')

        try:
            validate_password(password1)
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
            return render(request, 'bank_app/register.html')

        user = Bankuser.objects.create_user(
            username=username,
            password=password1,
            role=role,
            first_name=first_name,  # 使用用户输入的姓
            last_name=last_name,    # 使用用户输入的名
            email=email,            # 使用用户输入的电子邮箱
            is_staff=True,  # 所有用户都是工作人员
            is_superuser=True if role == 'admin' else False  # 只有管理员是超级用户
        )

        messages.success(request, '注册成功！请登录。')
        return redirect('login')

    return render(request, 'bank_app/register.html')

# 首页视图
@login_required(login_url='login')
def index(request):
    # 获取当前用户的客户信息
    try:
        # 尝试通过用户名查找客户信息
        customer = UserInfo.objects.filter(customerName__contains=request.user.first_name).first()
        
        if customer:
            # 获取该客户的所有银行卡
            cards = CardInfo.objects.filter(customerID=customer)
            return render(request, 'bank_app/index.html', {
                'customer': customer,
                'cards': cards
            })
    except Exception as e:
        # 如果发生错误，记录错误但不中断
        print(f"Error fetching customer data: {e}")
    
    # 如果没有找到客户信息或发生错误，返回空数据
    return render(request, 'bank_app/index.html')

# 客户管理视图
@login_required(login_url='login')
def customer_list(request):
    # 检查用户是否为管理员
    if request.user.role != 'admin':
        raise PermissionDenied('您没有权限访问客户管理页面。')
    if request.method == 'POST':
        # 获取表单数据
        customer_id = request.POST.get('customerID')
        customer_name = request.POST.get('customerName')
        id_card = request.POST.get('idCard')
        telephone = request.POST.get('telephone')
        address = request.POST.get('address')
        
        try:
            # 创建新客户
            UserInfo.objects.create(
                customerID=customer_id,
                customerName=customer_name,
                idCard=id_card,
                telephone=telephone,
                address=address
            )
            messages.success(request, '客户添加成功！')
            return redirect('customer_list')
        except Exception as e:
            messages.error(request, f'添加失败：{str(e)}')
            return redirect('customer_list')
    
    # GET请求显示客户列表
    customers = UserInfo.objects.all()
    return render(request, 'bank_app/customer_list.html', {'customers': customers})

@login_required(login_url='login')
def customer_detail(request, customer_id):
    customer = get_object_or_404(UserInfo, pk=customer_id)
    cards = CardInfo.objects.filter(customerID=customer)
    
    # 确保至少有一个默认存款类型
    default_deposit, created = Deposit.objects.get_or_create(
        pk=1,
        defaults={
            'savingName': '标准账户',
            'descrip': '标准银行账户'
        }
    )
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 处理AJAX请求添加银行卡
        try:
            initial_balance = request.POST.get('initialBalance')
            passwd = request.POST.get('passwd')
            
            # 使用默认存款类型
            deposit = default_deposit
            
            # 创建银行卡 (cardID字段将由触发器自动生成)
            card = CardInfo.objects.create(
                savingID=deposit,  # 使用默认存款类型
                balance=initial_balance,
                passwd=passwd,
                IsReportLoss="否",
                customerID=customer
            )
            
            # 如果有初始余额，创建一条存款交易记录
            if float(initial_balance) > 0:
                TradeInfo.objects.create(
                    cardID=card,
                    tradeType="存入",
                    tradeMoney=initial_balance,
                    remark="开户初始存款"
                )
            
            return JsonResponse({
                'status': 'success',
                'message': '银行卡添加成功',
                'card': {
                    'cardID': card.cardID,
                    'openDate': card.openDate.strftime('%Y-%m-%d'),
                    'balance': float(card.balance),
                    'isReportLoss': card.IsReportLoss
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'添加失败：{str(e)}'
            }, status=400)
    
    return render(request, 'bank_app/customer_detail.html', {
        'customer': customer,
        'cards': cards
    })

# 交易处理视图
# 添加银行卡的AJAX处理函数
@login_required(login_url='login')
def add_card(request, customer_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            customer = get_object_or_404(UserInfo, pk=customer_id)
            initial_balance = request.POST.get('initialBalance')
            passwd = request.POST.get('passwd')
            
            # 使用默认存款类型
            default_deposit, created = Deposit.objects.get_or_create(
                pk=1,
                defaults={
                    'savingName': '标准账户',
                    'descrip': '标准银行账户'
                }
            )
            
            # 创建银行卡 (cardID字段将由触发器自动生成)
            card = CardInfo.objects.create(
                savingID=default_deposit,
                balance=initial_balance,
                passwd=passwd,
                IsReportLoss="否",
                customerID=customer
            )
            
            # 如果有初始余额，创建一条存款交易记录
            if float(initial_balance) > 0:
                TradeInfo.objects.create(
                    cardID=card,
                    tradeType="存入",
                    tradeMoney=initial_balance,
                    remark="开户初始存款"
                )
            
            return JsonResponse({
                'status': 'success',
                'message': '银行卡添加成功',
                'card': {
                    'cardID': card.cardID,
                    'openDate': card.openDate.strftime('%Y-%m-%d'),
                    'balance': float(card.balance),
                    'isReportLoss': card.IsReportLoss
                }
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'添加失败：{str(e)}'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': '无效的请求方法'
    }, status=405)

@login_required(login_url='login')
def transaction_create(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        trade_type = request.POST.get('trade_type')
        amount = request.POST.get('amount')
        from decimal import Decimal
        amount = Decimal(amount)
        remark = request.POST.get('remark', '')

        try:
            card = CardInfo.objects.get(pk=card_id)
            # 验证密码
            if card.passwd != request.POST.get('password'):
                messages.error(request, '密码错误')
                return redirect('transaction_create')
                
            # 检查银行卡是否已挂失
            if card.IsReportLoss == '是':
                messages.error(request, '该银行卡已挂失，无法进行交易操作')
                return redirect('transaction_create')

            # 处理交易
            if trade_type == '存入':
                # 获取存款类型
                deposit_type_id = request.POST.get('deposit_type')
                if not deposit_type_id:
                    messages.error(request, '请选择存款类型')
                    return redirect('transaction_create')
                
                try:
                    deposit_type = Deposit.objects.get(pk=deposit_type_id)
                    # 如果是不同的存款类型，更新银行卡的存款类型
                    if str(card.savingID.savingID) != deposit_type_id:
                        card.savingID = deposit_type
                        remark = f"{remark} (存款类型变更为: {deposit_type.savingName})" if remark else f"存款类型变更为: {deposit_type.savingName}"
                except Deposit.DoesNotExist:
                    messages.error(request, '所选存款类型不存在')
                    return redirect('transaction_create')
                
                card.balance += amount
                messages.success(request, f'成功存入 {amount} 元')
            elif trade_type == '支取':
                if card.balance >= amount:
                    card.balance -= amount
                    messages.success(request, f'成功支取 {amount} 元')
                else:
                    messages.error(request, '余额不足')
                    return redirect('transaction_create')
            elif trade_type == '转账':
                target_card_id = request.POST.get('target_card_id')
                target_card = get_object_or_404(CardInfo, pk=target_card_id)
                
                # 检查目标银行卡是否已挂失
                if target_card.IsReportLoss == '是':
                    messages.error(request, '目标银行卡已挂失，无法转账')
                    return redirect('transaction_create')
                    
                if card.balance >= amount:
                    card.balance -= amount
                    target_card.balance += amount
                    target_card.save()
                    messages.success(request, f'成功转账 {amount} 元至 {target_card_id}')
                else:
                    messages.error(request, '余额不足')
                    return redirect('transaction_create')

            # 保存卡片信息和交易记录
            card.save()
            trade_info = TradeInfo.objects.create(
                cardID=card,
                tradeType=trade_type,
                tradeMoney=amount,
                remark=remark
            )
            request.session['transaction_id'] = trade_info.id
            return redirect('transaction_success')
        except CardInfo.DoesNotExist:
            messages.error(request, '银行卡不存在')
            return redirect('transaction_create')

    deposits = Deposit.objects.all()
    return render(request, 'bank_app/transaction_form.html', {'deposits': deposits})

@login_required(login_url='login')
def transaction_success(request):
    transaction_id = request.session.get('transaction_id')
    if transaction_id:
        try:
            transaction = TradeInfo.objects.get(pk=transaction_id)
            return render(request, 'bank_app/transaction_success.html', {'transaction': transaction})
        except TradeInfo.DoesNotExist:
            messages.error(request, '交易记录不存在')
            return redirect('transaction_create')
    else:
        messages.error(request, '无法获取交易信息')
        return redirect('transaction_create')

# 信息查询视图
@login_required(login_url='login')
def balance_inquiry(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        password = request.POST.get('password')
        try:
            card = CardInfo.objects.get(pk=card_id)
            if card.passwd == password:
                return render(request, 'bank_app/balance_result.html', {
                    'card': card,
                    'balance': card.balance
                })
            else:
                messages.error(request, '密码错误')
        except CardInfo.DoesNotExist:
            messages.error(request, '银行卡不存在')
    return render(request, 'bank_app/balance_inquiry.html')

@login_required(login_url='login')
def transaction_history(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        password = request.POST.get('password')
        try:
            card = CardInfo.objects.get(pk=card_id)
            if card.passwd == password:
                transactions = TradeInfo.objects.filter(cardID=card).order_by('-tradeDate')[:10]
                return render(request, 'bank_app/transaction_history.html', {
                    'card': card,
                    'transactions': transactions
                })
            else:
                messages.error(request, '密码错误')
        except CardInfo.DoesNotExist:
            messages.error(request, '银行卡不存在')
    return render(request, 'bank_app/transaction_history_form.html')

# 系统管理视图
from django.core.exceptions import PermissionDenied

def handler403(request, exception):
    return render(request, 'bank_app/403.html', {'exception': exception}, status=403)

@login_required(login_url='login')
def edit_customer_info(request, customer_id):
    customer = get_object_or_404(UserInfo, pk=customer_id)
    
    # 检查权限：只有管理员或者客户本人可以编辑信息
    if request.user.role != 'admin' and request.user.userID != customer:
        messages.error(request, '您没有权限编辑此客户信息')
        return redirect('index')
    
    if request.method == 'POST':
        # 获取表单数据
        name = request.POST.get('name')
        id_card = request.POST.get('id_card')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # 验证数据
        if not all([name, id_card, phone]):
            messages.error(request, '姓名、身份证号和电话不能为空')
            return redirect('edit_customer_info', customer_id=customer_id)
        
        # 检查身份证号格式（简单验证）
        if len(id_card) != 18:
            messages.error(request, '身份证号必须为18位')
            return redirect('edit_customer_info', customer_id=customer_id)
        
        # 检查电话号码格式（简单验证）
        if not phone.isdigit() or len(phone) != 11:
            messages.error(request, '电话号码必须为11位数字')
            return redirect('edit_customer_info', customer_id=customer_id)
        
        # 检查身份证号是否已被其他用户使用
        if UserInfo.objects.filter(IDCard=id_card).exclude(pk=customer_id).exists():
            messages.error(request, '该身份证号已被其他用户使用')
            return redirect('edit_customer_info', customer_id=customer_id)
        
        # 更新客户信息
        customer.name = name
        customer.IDCard = id_card
        customer.phone = phone
        customer.address = address
        customer.save()
        
        messages.success(request, '客户信息更新成功')
        return redirect('customer_detail', customer_id=customer_id)
    
    context = {
        'customer': customer
    }
    return render(request, 'edit_customer_info.html', context)

@login_required(login_url='login')
def system_dashboard(request):
    if request.user.role != 'admin':
        raise PermissionDenied('您没有权限访问此页面。')
    total_customers = UserInfo.objects.count()
    total_accounts = CardInfo.objects.count()
    total_balance = CardInfo.objects.aggregate(total=Sum('balance'))['total'] or 0
    recent_transactions = TradeInfo.objects.order_by('-tradeDate')[:5]

    return render(request, 'bank_app/system_dashboard.html', {
        'total_customers': total_customers,
        'total_accounts': total_accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions
    })

# 银行卡挂失/解除挂失功能
@login_required(login_url='login')
def toggle_card_loss_status(request, card_id):
    try:
        card = CardInfo.objects.get(pk=card_id)
        
        # 验证密码
        if request.method == 'POST':
            password = request.POST.get('password')
            if card.passwd != password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': '密码错误'}, status=400)
                messages.error(request, '密码错误')
                return redirect('customer_detail', customer_id=card.customerID.customerID)
            
            # 切换挂失状态
            if card.IsReportLoss == '是':
                card.IsReportLoss = '否'
                status_text = '正常'
                message = f'银行卡 {card_id} 已成功解除挂失'
                badge_class = 'bg-success'
                icon_class = 'bi-check-circle'
                button_class = 'btn-outline-danger'
                button_text = '挂失'
            else:
                card.IsReportLoss = '是'
                status_text = '已挂失'
                message = f'银行卡 {card_id} 已成功挂失'
                badge_class = 'bg-danger'
                icon_class = 'bi-x-circle'
                button_class = 'btn-outline-success'
                button_text = '解除挂失'
            
            card.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success', 
                    'message': message,
                    'is_report_loss': card.IsReportLoss,
                    'status_text': status_text,
                    'badge_class': badge_class,
                    'icon_class': icon_class,
                    'button_class': button_class,
                    'button_text': button_text
                })
            
            messages.success(request, message)
            return redirect('customer_detail', customer_id=card.customerID.customerID)
        
        # GET请求重定向到客户详情页
        return redirect('customer_detail', customer_id=card.customerID.customerID)
        
    except CardInfo.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': '银行卡不存在'}, status=404)
        messages.error(request, '银行卡不存在')
        return redirect('index')

@login_required(login_url='login')
def cancel_card(request, card_id):
    try:
        card = CardInfo.objects.get(pk=card_id)
        customer_id = card.customerID.customerID
        
        # 验证权限：只有管理员可以注销银行卡
        if request.user.role != 'admin':
            messages.error(request, '您没有权限执行此操作')
            return redirect('customer_detail', customer_id=customer_id)
        
        if request.method == 'POST':
            password = request.POST.get('password')
            
            # 验证密码
            if card.passwd != password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': '密码错误'}, status=400)
                messages.error(request, '密码错误')
                return redirect('customer_detail', customer_id=customer_id)
            
            # 检查余额
            if card.balance > 0:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'银行卡余额不为零（当前余额：{card.balance}元），无法注销'
                    }, status=400)
                messages.error(request, f'银行卡余额不为零（当前余额：{card.balance}元），无法注销')
                return redirect('customer_detail', customer_id=customer_id)
            
            # 创建注销交易记录
            TradeInfo.objects.create(
                cardID=card,
                tradeType='注销',
                tradeMoney=0,
                remark='银行卡注销'
            )
            
            # 删除银行卡
            card_id_display = card.cardID  # 保存卡号用于显示消息
            card.delete()
            
            message = f'银行卡 {card_id_display} 已成功注销'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success', 
                    'message': message
                })
            
            messages.success(request, message)
            return redirect('customer_detail', customer_id=customer_id)
        
        # GET请求重定向到客户详情页
        return redirect('customer_detail', customer_id=customer_id)
        
    except CardInfo.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': '银行卡不存在'}, status=404)
        messages.error(request, '银行卡不存在')
        return redirect('customer_list')