from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403
from bank_app.views import handler403 as custom_handler403

handler403 = custom_handler403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bank_app.urls')),
    path('', include('bank_app.urls_db_views')),  # 添加数据库视图相关URL
]