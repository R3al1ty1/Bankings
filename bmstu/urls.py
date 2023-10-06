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
    path(r'accounts/<int:account_number>/delete/', views.delete_detail, name='accounts-delete'),
    #path('accounts/', views.GetAccounts),
    #path('account/<str:name>/', views.GetAccount, name='account_url'),
    #path('get_account_icon/<int:account_id>/', views.getAccountIcon, name='get_account_icon'),
    #path('freeze_account/<str:account_name>/', views.freezeAccount, name='freeze_account'),
]