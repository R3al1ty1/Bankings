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
from django.urls import path, include
from bmstu import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Bankings API",
      default_version='v1.1',
      description="API for better user experience developed specifically for INK Bank",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="ikworkmail@yandex.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login',  views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path(r'api/accounts/search', views.get_accounts_search, name='accounts-list-search'),
    path(r'api/cards/post/', views.post_card, name='cards-post'),
    path(r'api/credits/post/', views.post_credit, name='credits-post'),
    path(r'api/deposits/post/', views.post_deposit, name='deposits-post'),
    path(r'api/saves/post/', views.post_save, name='saves-post'),
    path(r'api/accounts/<int:id>/', views.get_account, name='accounts-detail'),
    path(r'api/accounts/<int:id>/put/', views.put_detail, name='accounts-put'),
    path(r'api/account_application/<int:id>/post/', views.add_account_to_application, name='acc-app-post'),
    path(r'api/accounts/<int:id>/delete/', views.delete_detail, name='accounts-delete'),
    path(r'api/applications/', views.get_applications, name='applications-list'),
    path(r'api/accounts/post/', views.add_account_to_application, name='account-post'),
    path(r'api/applications/<int:pk>/', views.get_application, name='applications-detail'),
    path(r'api/applications/<int:pk>/put/', views.put_application, name='applications-put'),
    path(r'api/applications/<int:pk>/delete/', views.delete_application, name='applications-delete'),
    path(r'api/apps_accs/<int:acc_id>/<int:app_id>/delete/', views.delete_app_acc, name='app-acc-delete'),
    path(r'api/apps_accs/<int:acc_id>/<int:app_id>/put/', views.put_app_acc, name='app-acc-put'),
    path(r'api/app_create_status/<int:id>/put/', views.put_create_status, name='app-create-put'),
    path(r'api/app_mod_status/<int:id>/put/', views.put_mod_status, name='app-mod-put'),
    #path('accounts/', views.GetAccounts),
    #path('account/<str:name>/', views.GetAccount, name='account_url'),
    #path('get_account_icon/<int:account_id>/', views.getAccountIcon, name='get_account_icon'),
    #path('freeze_account/<str:account_name>/', views.freezeAccount, name='freeze_account'),
]