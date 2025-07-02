from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Bankuser(AbstractUser):
    """银行用户表"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('operator', '用户')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='operator', verbose_name='角色')
    
    class Meta:
        verbose_name = '银行用户'
        verbose_name_plural = '银行用户'
        db_table = 'bank_app_bankuser' 
        
    def __str__(self):
        return f"{self.username}({self.get_role_display()})"


class UserInfo(models.Model):
    """客户信息表"""
    customerID = models.CharField(max_length=12, primary_key=True, verbose_name="客户编号")
    customerName = models.CharField(max_length=10, verbose_name="姓名")
    idCard = models.CharField(max_length=18, unique=True, verbose_name="身份证号")
    telephone = models.CharField(max_length=11, verbose_name="联系电话", default="")
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name="地址")

    class Meta:
        verbose_name = "客户信息"
        verbose_name_plural = "客户信息"

    def __str__(self):
        return f"{self.customerName}({self.customerID})"


class Deposit(models.Model):
    """存款类型表"""
    savingID = models.AutoField(primary_key=True, verbose_name="存款编号")
    savingName = models.CharField(max_length=20, verbose_name="存款类型名称")
    descrip = models.CharField(max_length=50, null=True, blank=True, verbose_name="类型描述")

    class Meta:
        verbose_name = "存款类型"
        verbose_name_plural = "存款类型"

    def __str__(self):
        return self.savingName


class CardInfo(models.Model):
    """银行卡信息表"""
    cardID = models.CharField(max_length=19, primary_key=True, verbose_name="银行卡号")
    # 存款类型字段保留但不在界面显示，使用默认值
    savingID = models.ForeignKey(Deposit, on_delete=models.PROTECT, verbose_name="存款类型", default=1)
    openDate = models.DateTimeField(default=timezone.now, verbose_name="开户日期")
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="账户余额")
    passwd = models.CharField(max_length=6, verbose_name="密码")
    IsReportLoss = models.CharField(max_length=3, default="否", choices=[("是", "是"), ("否", "否")], verbose_name="挂失状态")
    customerID = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name="客户编号")

    class Meta:
        verbose_name = "银行卡信息"
        verbose_name_plural = "银行卡信息"

    def __str__(self):
        return self.cardID


class TradeInfo(models.Model):
    """交易信息表"""
    tradeDate = models.DateTimeField(default=timezone.now, verbose_name="交易时间")
    tradeType = models.CharField(max_length=6, choices=[("存入", "存入"), ("支取", "支取"), ("转账", "转账")], verbose_name="交易类型")
    cardID = models.ForeignKey(CardInfo, on_delete=models.CASCADE, verbose_name="银行卡号")
    tradeMoney = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="交易金额")
    remark = models.TextField(null=True, blank=True, verbose_name="交易备注")

    class Meta:
        verbose_name = "交易记录"
        verbose_name_plural = "交易记录"
        ordering = ['-tradeDate']

    def __str__(self):
        return f"{self.tradeType}-{self.tradeMoney}-{self.tradeDate.strftime('%Y-%m-%d %H:%M')}"