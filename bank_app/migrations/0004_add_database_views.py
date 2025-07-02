from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0003_alter_cardinfo_savingid_alter_bankuser_table'),
    ]

    operations = [
        migrations.RunSQL(
            # 创建客户账户视图
            """
            CREATE OR REPLACE VIEW customer_account_view AS
            SELECT 
                u."customerID",
                u."customerName",
                u."idCard",
                u."telephone",
                u."address",
                c."cardID",
                c."openDate",
                c."balance",
                c."IsReportLoss",
                d."savingID",
                d."savingName",
                d."descrip" as "savingDescription"
            FROM 
                bank_app_userinfo u
            JOIN 
                bank_app_cardinfo c ON u."customerID" = c."customerID_id"
            JOIN 
                bank_app_deposit d ON c."savingID_id" = d."savingID";
            """,
            "DROP VIEW IF EXISTS customer_account_view;"
        ),
        migrations.RunSQL(
            # 创建交易明细视图
            """
            CREATE OR REPLACE VIEW transaction_detail_view AS
            SELECT 
                t.id as "tradeID",
                t."tradeDate",
                t."tradeType",
                t."tradeMoney",
                t."remark",
                c."cardID",
                c."balance",
                t."balance" as "balanceAfterTrade",
                u."customerID",
                u."customerName"
            FROM 
                bank_app_tradeinfo t
            JOIN 
                bank_app_cardinfo c ON t."cardID_id" = c."cardID"
            JOIN 
                bank_app_userinfo u ON c."customerID_id" = u."customerID";
            """,
            "DROP VIEW IF EXISTS transaction_detail_view;"
        ),
        migrations.RunSQL(
            # 创建账户余额统计视图
            """
            CREATE OR REPLACE VIEW customer_balance_summary_view AS
            SELECT 
                u."customerID",
                u."customerName",
                COUNT(c."cardID") as "cardCount",
                SUM(c."balance") as "totalBalance",
                MAX(c."balance") as "maxBalance",
                MIN(c."balance") as "minBalance",
                AVG(c."balance") as "avgBalance"
            FROM 
                bank_app_userinfo u
            JOIN 
                bank_app_cardinfo c ON u."customerID" = c."customerID_id"
            GROUP BY 
                u."customerID", u."customerName";
            """,
            "DROP VIEW IF EXISTS customer_balance_summary_view;"
        ),
        migrations.RunSQL(
            # 创建交易类型统计视图
            """
            CREATE OR REPLACE VIEW transaction_type_summary_view AS
            SELECT 
                t."tradeType",
                COUNT(*) as "transactionCount",
                SUM(t."tradeMoney") as "totalAmount",
                AVG(t."tradeMoney") as "avgAmount",
                MAX(t."tradeMoney") as "maxAmount",
                MIN(t."tradeMoney") as "minAmount"
            FROM 
                bank_app_tradeinfo t
            GROUP BY 
                t."tradeType";
            """,
            "DROP VIEW IF EXISTS transaction_type_summary_view;"
        ),
    ]