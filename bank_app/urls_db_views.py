from django.urls import path
from . import views_db_views

urlpatterns = [
    # 数据库视图相关路由
    path('db_views/customer_accounts/', views_db_views.customer_accounts_view, name='customer_accounts'),
    path('db_views/customer_accounts/<str:customer_id>/', views_db_views.customer_accounts_view, name='customer_accounts_detail'),
    path('db_views/transaction_details/', views_db_views.transaction_details_view, name='transaction_details'),
    path('db_views/transaction_details/card/<str:card_id>/', views_db_views.transaction_details_view, name='transaction_details_by_card'),
    path('db_views/transaction_details/customer/<str:customer_id>/', views_db_views.transaction_details_view, name='transaction_details_by_customer'),
    path('db_views/balance_summary/', views_db_views.customer_balance_summary_view, name='balance_summary'),
    path('db_views/transaction_summary/', views_db_views.transaction_type_summary_view, name='transaction_summary'),
    path('db_views/dashboard/', views_db_views.dashboard_view, name='db_views_dashboard'),
]