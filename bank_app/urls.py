from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.index, name='index'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<str:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<str:customer_id>/add_card/', views.add_card, name='add_card'),
    path('customers/<str:customer_id>/edit/', views.edit_customer_info, name='edit_customer_info'),
    path('transaction/create/', views.transaction_create, name='transaction_create'),
    path('transaction/success/', views.transaction_success, name='transaction_success'),
    path('inquiry/balance/', views.balance_inquiry, name='balance_inquiry'),
    path('inquiry/history/', views.transaction_history, name='transaction_history'),
    path('system/dashboard/', views.system_dashboard, name='system_dashboard'),
    path('cards/<str:card_id>/toggle_loss_status/', views.toggle_card_loss_status, name='toggle_card_loss_status'),
    path('cards/<str:card_id>/cancel/', views.cancel_card, name='cancel_card'),
]