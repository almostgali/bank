from django.db import migrations
import os

def load_sql_from_file(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(current_dir, filename)
    with open(sql_file, 'r', encoding='utf-8') as f:
        return f.read()

class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            load_sql_from_file('generate_card_id_trigger.sql'),
            # 回滚操作
            "DROP TRIGGER IF EXISTS trigger_auto_generate_card_id ON bank_app_cardinfo;"
            "DROP FUNCTION IF EXISTS auto_generate_card_id();"
            "DROP FUNCTION IF EXISTS generate_random_card_id();"
        ),
    ]