"""
URL configuration for bmstu_lab project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bmstu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'accounts/', views.get_accounts, name='accounts-list'),
    path(r'cards/post/', views.post_card, name='cards-post'),
    path(r'credits/post/', views.post_credit, name='credits-post'),
    path(r'deposits/post/', views.post_deposit, name='deposits-post'),
    path(r'saves/post/', views.post_save, name='saves-post'),
    path(r'accounts/<int:account_number>/', views.get_account, name='accounts-detail'),
    path(r'accounts/<int:account_number>/put/', views.put_detail, name='accounts-put'),
    path(r'account_application/<int:id>/post/', views.add_account_to_application, name='acc-app-post'),
    path(r'accounts/<int:account_number>/delete/', views.delete_detail, name='accounts-delete'),
    path(r'applications/', views.get_applications, name='applications-list'),
    path(r'accounts/post/', views.add_account_to_application, name='account-post'),
    path(r'applications/<int:pk>/', views.get_application, name='applications-detail'),
    path(r'applications/<int:pk>/put/', views.put_application, name='applications-put'),
    path(r'applications/<int:pk>/delete/', views.delete_application, name='applications-delete'),
    path(r'apps_accs/<int:acc_id>/<int:app_id>/delete/', views.delete_app_acc, name='app-acc-delete'),
    path(r'apps_accs/<int:acc_id>/<int:app_id>/put/', views.put_app_acc, name='app-acc-put'),
    path(r'app_create_status/<int:id>/put/', views.put_create_status, name='app-create-put'),
    path(r'app_mod_status/<int:id>/put/', views.put_mod_status, name='app-mod-put'),
    #path('accounts/', views.GetAccounts),
    #path('account/<str:name>/', views.GetAccount, name='account_url'),
    #path('get_account_icon/<int:account_id>/', views.getAccountIcon, name='get_account_icon'),
    #path('freeze_account/<str:account_name>/', views.freezeAccount, name='freeze_account'),
]