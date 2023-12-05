from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_signup, name='user-signup'),
    path('login/', views.user_login, name='user-login'),
    path('contracts/<int:pk>/', views.contract_detail, name='contract-detail'),
    path('contracts/', views.list_contracts, name='contract-list'),
    path('profile/', views.get_profile, name='profile-detail'),
    path('jobs/', views.get_jobs, name='user-jobs'),
    path('jobs/unpaid/', views.get_unpaid_jobs, name='user-unpaid-jobs'),
    path('jobs/<int:job_id>/pay/', views.pay_job, name='pay-job'),
    path('balances/deposit/<int:user_id>/', views.deposite_money, name='deposite-money'),
    path('jobs/best-profession/', views.best_profession, name='best-profession'),
    path('jobs/best-clients/', views.best_clients, name='best-clients'),
    path('profiles/', views.list_profiles, name='list-profiles'),
    
]