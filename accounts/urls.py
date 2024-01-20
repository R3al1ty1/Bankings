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
from accounts import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


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
    #админ
    path('api/admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    #счета
    path(r'api/accounts/', views.get_accounts, name='accounts-list'),
    path(r'api/accounts/search', views.get_accounts_search, name='accounts-list-search'),
    path(r'api/accounts/mod', views.get_accounts_mod, name='accounts-list-mod'),
    path(r'api/accounts/<int:id>/', views.get_account, name='accounts-detail'),
    path(r'api/accounts/<int:id>/put/', views.put_detail, name='accounts-put'),
    path(r'api/accounts/<int:id>/delete/', views.delete_detail, name='accounts-delete'),

    #договоры
    path(r'api/agreements/', views.get_agreements, name='agreements-list-all'),
    path(r'api/agreements/add', views.add_agreement, name='add-agreement'),
    path(r'api/agreements/<int:id>/', views.get_agreement, name='agreement-detail'),
    path(r'api/agreements/mod', views.get_agreements_mod, name='agreements-list-mod'),
    path(r'api/agreements/<int:id>/put/', views.put_agreement, name='agreement-put'),
    path(r'api/agreements/post/', views.create_agreement, name='agreement-post'),
    path(r'api/agreements/<int:id>/delete/', views.delete_agreement, name='agreement-delete'),

    #заявки
    path(r'api/applications/', views.get_applications, name='applications-list'),
    path(r'api/applications/mod', views.get_applications_mod, name='applications-list-mod'),
    path(r'api/applications/<int:pk>/', views.get_application, name='applications-detail'),
    path(r'api/applications/<int:pk>/put/', views.put_application, name='applications-put'),
    path(r'api/applications/<int:id>/delete/', views.delete_application, name='applications-delete'),
    path(r'api/app_create_status/<int:id>/put/', views.put_create_status, name='app-create-put'),
    path(r'api/app_mod_status/<int:id>/put/', views.put_mod_status, name='app-mod-put'),

    #м-м
    path(r'api/apps_accs/<int:acc_id>/<int:app_id>/delete/', views.delete_app_acc, name='app-acc-delete'),
    path(r'api/apps_accs/<int:acc_id>/<int:app_id>/put/', views.put_app_acc, name='app-acc-put'),

    #пользователь и токены
    path("api/register/", views.register, name="register"),
    path("api/login/", views.login, name="login"),
    path("api/check/", views.check, name="check_access_token"),
    path('api/refresh/', views.refresh, name='refresh-token'),
    path("api/logout/", views.logout, name="logout"),

    #разное
    path(r'api/number/<int:acc_id>/<int:app_id>/put/', views.put_number, name='put-number'),
    path(r'api/icon/<str:type>/', views.getIcon, name='get-icons'),
    path('api/test/', views.updateNumber, name='test'),
    path(r'api/accounts/async/<int:id>/put/', views.put_detail_async, name='accounts-put-async'),
]